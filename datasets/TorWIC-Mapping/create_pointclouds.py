import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R

from utils.tile_writer import TileWriter
from utils.pointcloud_format import FORMAT_XYZRGB
from utils.io import FileFormat
from utils.pointcloud_processing import remove_duplicates
from utils.pointcloud_creation import RGBDReconstruction, get_pose_matrix_from_pose, get_processing_order


parser = argparse.ArgumentParser(prog='TorWIC-Mapping - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ supported)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of epochs to exclude for reconstruction, e.g., "Scenario_1-1"', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of epochs to include (overwrites exclusion list)', nargs='+', type=str)
parser.add_argument('--num_tiles', help='The number of tiles into which the scene should be divided in x and y direction', nargs=2, default=[2,2])

T_base_to_camera = np.eye(4)
T_base_to_camera[:3, :3] = R.from_quat([-0.431, 0.429, -0.562, 0.561]).as_matrix()
T_base_to_camera[:3, 3] = np.array([0.520, 0.032, 0.011])

T_lidar_to_base = np.eye(4)
T_lidar_to_base[:3, 3] = np.array([-0.456, 0.0, -0.172])

# the intrinsics are taken from utils/calibration.py from the TorWIC repository
intrinsics = np.array([[461.0956115722656, 0.0, 325.4782409667969], [0.0, 460.9181823730469, 177.57662963867188], [0.0, 0.0, 1.0]])

def extract_pointcloud(input_path, output_path, output_format, num_tiles):
	poses = np.loadtxt(os.path.join(input_path, 'poses.txt'))
	
	# The depth maps are quite noisy, especially at larger distances. According to the specs of the camera, the error is < 2% for up to 2m.
	rgbd_reconstruction = RGBDReconstruction(intrinsics, image_resolution=[640, 360], depth_threshold=2)
	
	tile_writer = TileWriter(output_path,
			  pointcloud_format=FORMAT_XYZRGB,
			  file_format=output_format,
			  bbox=np.array([np.min(poses[:, 3:5], axis=0), np.max(poses[:, 3:5], axis=0)]), 
			  num_tiles=num_tiles)
	
	for pose in tqdm(poses, leave=False):
		pose_matrix = get_pose_matrix_from_pose(pose[3:])
		pose_matrix = (pose_matrix @ T_lidar_to_base) @ T_base_to_camera

		file_idx = int(pose[0])

		depth_path = os.path.join(input_path, 'Depth', '{:04d}.png'.format(file_idx))
		depth = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED).astype(np.float32) * 0.001

		color_path = os.path.join(input_path, 'RGB', '{:04d}.png'.format(file_idx))
		color = cv2.cvtColor(cv2.imread(color_path), cv2.COLOR_BGR2RGB)

		#seg_path = os.path.join(input_path, 'Segmentation', '{:04d}.png'.format(file_idx))
		#segmentation = cv2.imread(seg_path, cv2.IMREAD_UNCHANGED).astype(np.uint8)
		segmentation = None   # segmentation is not very good

		result = rgbd_reconstruction.add_image(depth, color, pose_matrix, segmentation, direct_result=True)
		tile_writer.add_points(remove_duplicates(result))

	tile_writer.close()


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list, num_tiles):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	processing_order = []
	for folder in os.scandir(os.path.join(input_path, 'raw')):
		processing_order.extend(get_processing_order(folder.path, inclusion_list, exclusion_list))

	for entry in tqdm(processing_order):
		output_path = os.path.join(output_folder, entry.parent.name, entry.name)
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


