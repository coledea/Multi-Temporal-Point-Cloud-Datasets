import os
import argparse
import numpy as np
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R

from utils.pointcloud_format import FORMAT_XYZC
from utils.io import FileFormat, write_pointcloud
from utils.pointcloud_creation import get_pose_matrix_from_pose


parser = argparse.ArgumentParser(prog='Underwood et al. - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def extract_pointcloud(epoch_parts, output_folder, output_filename, output_format):
	parts = []
	for scan_path, pose_path in epoch_parts:
		pointcloud = np.loadtxt(scan_path, delimiter=',')
		pose = np.loadtxt(pose_path, delimiter=',')

		rotation = R.from_euler('xyz', angles=pose[3:]).as_quat()
		pose_matrix = get_pose_matrix_from_pose([*pose[0:3], *rotation])
		positions = np.vstack((pointcloud[:, 0:3].T, np.ones(pointcloud.shape[0])))
		positions = (pose_matrix @ positions).T
		parts.append(np.column_stack([positions[:, 0:3], pointcloud[:, 4]]))

	write_pointcloud(np.vstack(parts), output_folder, output_filename, output_format, FORMAT_XYZC)


def extract_pointclouds(input_path, output_folder, output_format):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	scenes = {}
	for folder in os.scandir(os.path.join(input_path, 'raw')):
		if not folder.name in ['carpark', 'sim', 'lab']:
			continue

		# collect all scans of the same epoch
		epochs = {}
		for scan in os.scandir(folder.path):
			if not 'object' in scan.name:
				continue
			epoch_name = scan.name.split('.')[2]
			if epoch_name not in epochs:
				epochs[epoch_name] = []
			pose_path = os.path.join(folder.path, '.'.join(scan.name.split('.')[0:2]) + '.csv')
			epochs[epoch_name].append([scan.path, pose_path])
		scenes[folder.name] = epochs

	for scene in tqdm(scenes):
		output_path = os.path.join(output_folder, scene)
		os.makedirs(output_path, exist_ok=True)
		for idx, epoch in tqdm(list(enumerate(sorted(scenes[scene]))), leave=False):
			extract_pointcloud(scenes[scene][epoch], output_path, 'epoch_' + epoch[-1], output_format)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
					 args.output_folder, 
					 args.output_format)


