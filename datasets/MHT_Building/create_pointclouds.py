import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore

from utils.pointcloud_format import FORMAT_XYZRGB
from utils.io import FileFormat, write_pointcloud
from utils.rosbags import extract_poses
from utils.pointcloud_creation import RGBDReconstruction, get_pose_matrix_from_pose, get_processing_order
from utils.pointcloud_processing import remove_duplicates


parser = argparse.ArgumentParser(prog='MHT Building - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of filenames to exclude for reconstruction, e.g., "3D_22-08-13-00-00_place_0.bag"', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of filenames to include (overwrites exclusion list)', nargs='+', type=str)

typestore = get_typestore(Stores.ROS1_NOETIC)

intrinsics = np.array([[478.913844053, 0., 320.], [0., 478.913844053, 240.], [0., 0., 1.]])   # guessed

def depth_from_message(rawdata, msgtype):
	depth_msg = typestore.deserialize_ros1(rawdata, msgtype)
	return np.frombuffer(depth_msg.data, np.float32).reshape((480, 640))

def color_from_message(rawdata, msgtype):
	color_msg = typestore.deserialize_ros1(rawdata, msgtype)
	color = np.frombuffer(color_msg.data, np.uint8).reshape((480, 640, 3))
	return cv2.cvtColor(color, cv2.COLOR_BGR2RGB)

def extract_pointcloud(input_path, output_path, output_format):
	_, poses = extract_poses(input_path.resolve(), typestore, '/robot_pose')
	
	# Rearrange columns: for the pose, the z-axis points up, but for the point clouds, the y-axis points up
	poses = poses[:, [0, 2, 1, 3, 5, 4, 6]]

	with Reader(input_path.resolve()) as reader:
		depth_reader = reader.messages(connections=[x for x in reader.connections if x.topic == '/head_xtion/depth/image' and x.msgtype == 'sensor_msgs/msg/Image'])
		color_reader = reader.messages(connections=[x for x in reader.connections if x.topic == '/head_xtion/rgb/image_color' and x.msgtype == 'sensor_msgs/msg/Image'])
		d_connection, _, d_rawdata = next(depth_reader, None)
		c_connection, _, c_rawdata = next(color_reader, None)

		rgbd_reconstruction = RGBDReconstruction(intrinsics, image_resolution=[640, 480])
		progress_bar = tqdm(leave=False)
		idx = 0
		while d_connection is not None:
			if d_connection.topic == '/head_xtion/depth/image':      # for some reason there seem to be wrong topics in here sometimes
				depth = depth_from_message(d_rawdata, d_connection.msgtype)
				color = color_from_message(c_rawdata, c_connection.msgtype)
				pose = get_pose_matrix_from_pose(poses[idx])     # the timestamps of the poses do not fit the images. We just use the poses in their stored order
				rgbd_reconstruction.add_image(depth, color, pose)

			d_connection, _, d_rawdata = next(depth_reader, (None, None, None))
			c_connection, _, c_rawdata = next(color_reader, (None, None, None))
			progress_bar.update()
			idx += 1

		result = remove_duplicates(rgbd_reconstruction.get_result())
		write_pointcloud(result, output_path, input_path.stem, output_format, FORMAT_XYZRGB)


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	for scene in ['place_0', 'place_1', 'place_2']:
		os.makedirs(os.path.join(output_folder, scene), exist_ok=True)

	processing_order = []
	for epoch in os.scandir(os.path.join(input_path, 'rosbags')):
		processing_order.extend(get_processing_order(epoch.path, inclusion_list, exclusion_list))

	for entry in tqdm(processing_order):
		if not 'active' in entry.name:
			scene_name = 'place_' + entry.stem.split('_')[-1]
			extract_pointcloud(entry, os.path.join(output_folder, scene_name), output_format)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
					 args.output_folder, 
					 args.output_format, 
					 args.exclusion_list, 
					 args.inclusion_list)


