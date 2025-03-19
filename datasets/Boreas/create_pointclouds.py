import os
import argparse
import math
import numpy as np
from tqdm import tqdm
from pyboreas import BoreasDataset
from pyboreas.data.splits import odom_train
from pyboreas.utils.utils import get_inverse_tf

from utils.pointcloud_format import FORMAT_XYZRGB, FORMAT_XYZI
from utils.io import FileFormat
from utils.tile_writer import TileWriter


parser = argparse.ArgumentParser(prog='Boreas - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to "[input_path]/pointclouds")')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ supported)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of dates to exclude for reconstruction, e.g., "boreas-2020-11-26-13-58".', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of dates to include, e.g., "boreas-2020-11-26-13-58" (overwrites the exclusion list)', nargs='+', type=str)
parser.add_argument('--project_images', help='Projects the RGB images onto the point cloud to get per-point colors', action='store_true')
parser.add_argument('--tile_size', help='The size of the tiles into which the scene is divided in x and y direction', default=100)


def get_bbox(sequence):
	bbox_min = np.array([math.inf, math.inf])
	bbox_max = np.array([-math.inf, -math.inf])
	for lidar_frame in sequence.lidar:
		bbox_min = np.minimum(lidar_frame.pose[:2,3], bbox_min)
		bbox_max = np.maximum(lidar_frame.pose[:2,3], bbox_max)
		lidar_frame.unload_data()    # could be removed if there is enough memory to hold all frames
	return np.array([bbox_min, bbox_max])


def get_colors(camera_frame, lidar_frame, projection):
	T_camera_lidar = np.matmul(get_inverse_tf(camera_frame.pose), lidar_frame.pose)
	lidar_frame.transform(T_camera_lidar)
	uv, _, mask = lidar_frame.project_onto_image(projection)
	mask = np.asarray(mask).flatten()
	behind_camera = (lidar_frame.points[:, 2] >= 0)[mask]
	mask = mask[behind_camera]     # Exclude points behind the camera
	uv = uv[behind_camera]
	colors = np.zeros((mask.shape[0], 3))
	colors = camera_frame.img[uv.astype(int)[:,1], uv.astype(int)[:,0]]
	camera_frame.unload_data()
	return [mask, colors]

def extract_pointcloud(sequence, output_path, output_format, tile_size, project_images):
	tile_writer = TileWriter(output_path,
						  pointcloud_format=FORMAT_XYZRGB if project_images else FORMAT_XYZI,
						  file_format=output_format,
						  bbox=get_bbox(sequence), 
						  tile_size=tile_size,
						  padding=1)
	
	if project_images:
		sequence.synchronize_frames(ref='lidar')
		camera_iter = sequence.get_camera_iter()
	
	for lidar_frame in tqdm(sequence.lidar, leave=False):
		lidar_frame.remove_motion(lidar_frame.body_rate)
		positions = np.column_stack([lidar_frame.points[:, :3], np.ones(lidar_frame.points.shape[0])]).T
		positions = np.matmul(lidar_frame.pose.astype(np.float64), positions.astype(np.float64))
		positions = positions[:3] / positions[3]

		if project_images:
			mask, colors = get_colors(next(camera_iter), lidar_frame, sequence.calib.P0)
			pointcloud = np.column_stack((positions.T[mask], colors))       # only store colored points
		else:
			pointcloud = np.column_stack([positions.T, lidar_frame.points[:, 3]])

		if len(pointcloud) > 0:
			tile_writer.add_points(pointcloud)
		lidar_frame.unload_data()

	tile_writer.close()
	


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list, project_images, tile_size):
	if not os.path.exists(input_path):
		return

	data_folder = os.path.join(input_path, 'raw')

 	# in the current pip version of pyboreas (1.0.5), this is erroneously in the odom_train split
	exclusion_list.append('boreas-2021-04-29-15-55')

	if inclusion_list is not None:
		split_list = [inclusion_list]
	else:
		split_list = [x for x in odom_train[0] if x not in exclusion_list]
	split_list = [x for x in split_list if os.path.exists(os.path.join(data_folder, x))]
		
	boreas = BoreasDataset(data_folder, split=split_list)

	for seq in tqdm(boreas.sequences):
		if output_folder is None:
			output_path = os.path.join(input_path, 'pointclouds', seq.ID)
		else:
			output_path = os.path.join(output_folder, seq.ID)
		os.makedirs(output_path, exist_ok=True)

		extract_pointcloud(seq, output_path, output_format, tile_size, project_images)



if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
					 args.output_folder, 
					 args.output_format,
					 args.exclusion_list,
					 args.inclusion_list,
					 args.project_images,
					 args.tile_size)