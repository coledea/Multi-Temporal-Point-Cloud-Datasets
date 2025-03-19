import os
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore

from utils.pointcloud_format import FORMAT_XYZRGB
from utils.io import FileFormat, write_pointcloud
from utils.rosbags import pointcloud_from_point_message


parser = argparse.ArgumentParser(prog='Fehr et al. - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of filepaths to exclude for reconstruction. Do not prepend the raw data directory of Fehr_et_al, i.e., write living_room/rosbag/observation_0.bag', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of filepaths to include (overwrites exclusion list)', nargs='+', type=str)


def extract_pointcloud(input_path, output_folder, output_format):
	output_path = os.path.join(output_folder, input_path.parent.parent.name)
	os.makedirs(output_path, exist_ok=True)

	typestore = get_typestore(Stores.ROS1_NOETIC)
	
	result = []
	with Reader(input_path.resolve()) as reader:
		points_connections = [x for x in reader.connections if x.topic == 'point_cloud_G']
		for connection, _, rawdata in tqdm(reader.messages(connections=points_connections), leave=False):
			message = typestore.deserialize_ros1(rawdata, connection.msgtype)
			pointcloud = pointcloud_from_point_message(message)

			mask = np.any(pointcloud[:,3:] != 0, axis=1)  # Remove erroneous black points
			result.extend(pointcloud[mask])

	write_pointcloud(np.array(result), output_path, input_path.stem, output_format, FORMAT_XYZRGB)


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')
	
	if inclusion_list is not None:
		for entry in tqdm(inclusion_list):
			extract_pointcloud(Path(input_path, 'raw', entry), output_folder, output_format)
	else:
		exclusion_list = [os.path.join(input_path, 'raw', entry) for entry in exclusion_list]

		processing_order = []
		for scene in os.scandir(os.path.join(input_path, 'raw')):
			if not scene.is_dir():
				continue
			for epoch in os.scandir(os.path.join(scene.path, 'rosbag')):
				if epoch.path not in exclusion_list:
					processing_order.append(Path(epoch.path))

		for entry in tqdm(processing_order):
			extract_pointcloud(entry, output_folder, output_format)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
					 args.output_folder, 
					 args.output_format,
					 args.exclusion_list,
					 args.inclusion_list)

