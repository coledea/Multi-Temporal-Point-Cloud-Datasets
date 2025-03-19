import os
import numpy as np
import argparse
import cv2

from utils.tile_writer import TileWriter
from utils.pointcloud_format import FORMAT_XYZRGB
from utils.io import FileFormat
from utils.pointcloud_processing import remove_duplicates
from utils.pointcloud_creation import RGBDReconstruction, get_pose_matrix, get_processing_order
from tqdm import tqdm


parser = argparse.ArgumentParser(prog='OpenLORIS-Scene - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ supported)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of epochs to exclude for reconstruction, e.g., "cafe1-1"', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of epochs to include (overwrites exclusion list)', nargs='+', type=str)
parser.add_argument('--num_tiles', help='The number of tiles into which the scene should be divided in x and y direction', nargs=2, default=[7,7])


def extract_pointcloud(input_path, output_path, output_format, num_tiles):
	timestamps = np.loadtxt(os.path.join(input_path, 'groundtruth.txt'), usecols=(0), skiprows=1, dtype=np.float64)
	poses = np.loadtxt(os.path.join(input_path, 'groundtruth.txt'), usecols=(1,2,3,4,5,6,7), skiprows=1)
	depth_paths = np.loadtxt(os.path.join(input_path, 'aligned_depth.txt'), dtype=str)
	color_paths = np.loadtxt(os.path.join(input_path, 'color.txt'), dtype=str)

	min_timestamp = np.min(timestamps)
	max_timestamp = np.max(timestamps)

	tile_writer = TileWriter(output_path,
				  pointcloud_format=FORMAT_XYZRGB,
				  file_format=output_format,
				  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
				  num_tiles=num_tiles)
	
	intrinsics_file = cv2.FileStorage(os.path.join(input_path, 'sensors.yaml'), cv2.FILE_STORAGE_READ)
	intrinsics_values = intrinsics_file.getNode('d400_color_optical_frame').getNode('intrinsics').mat()[0]
	intrinsics_file.release()
	intrinsics = np.array([[intrinsics_values[0], 0.0, intrinsics_values[1]], [0.0, intrinsics_values[2], intrinsics_values[3]], [0.0, 0.0, 1.0]])

	extrinsics_file = cv2.FileStorage(os.path.join(input_path, 'trans_matrix.yaml'), cv2.FILE_STORAGE_READ)
	tf_base_to_camera = extrinsics_file.getNode('trans_matrix').at(0).getNode('matrix').mat()
	extrinsics_file.release()

	# The depth maps are quite noisy, especially at larger distances. We used a threshold of 3m.
	rgbd_reconstruction = RGBDReconstruction(intrinsics, image_resolution=[848, 480], depth_threshold=3)

	for idx, depth_path in tqdm(enumerate(depth_paths), total=len(depth_paths), leave=False):
		timestamp = color_paths[idx][0].astype(np.float64)
		if timestamp < min_timestamp or timestamp > max_timestamp:
			continue

		# Note: the timestamps are aligned with msec precision
		pose = get_pose_matrix(timestamps, poses, timestamp) @ tf_base_to_camera
		depth = cv2.imread(os.path.join(input_path, depth_path[1]), cv2.IMREAD_UNCHANGED).astype(np.float32) * 0.001
		color = cv2.cvtColor(cv2.imread(os.path.join(input_path, color_paths[idx][1])), cv2.COLOR_BGR2RGB)
		result = rgbd_reconstruction.add_image(depth, color, pose, direct_result=True)
		tile_writer.add_points(remove_duplicates(result))

	tile_writer.close()


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list, num_tiles):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	processing_order = []
	for scene in os.scandir(os.path.join(input_path, 'raw')):
		processing_order.extend(get_processing_order(scene.path, inclusion_list, exclusion_list))

	for entry in tqdm(processing_order):
		scene_name = entry.name[:-3]
		output_path = os.path.join(output_folder, scene_name, entry.name)
		os.makedirs(output_path, exist_ok=True)
		extract_pointcloud(entry.resolve(), output_path, output_format, np.array(num_tiles))


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
					 args.output_folder, 
					 args.output_format, 
					 args.exclusion_list, 
					 args.inclusion_list,
					 args.num_tiles)


