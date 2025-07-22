import os
import argparse
import json
import numpy as np
from tqdm import tqdm

from utils.pointcloud_format import FORMAT_XYZ
from utils.io import FileFormat, write_pointcloud, read_pointcloud_for_evaluation

parser = argparse.ArgumentParser(prog='NSS 2025 - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to "[input_path]/pointclouds")')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of epoch names to exclude for reconstruction (e.g., Bldg1_Stage1).', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of epoch names to include (overwrites the exclusion list)', nargs='+', type=str)


def extract_pointcloud(input_folder, poses, output_folder, output_format):
	pointcloud = []
	for pose_name in poses:
		xyz = read_pointcloud_for_evaluation(os.path.join(input_folder, pose_name))
		xyzw = np.hstack((xyz, np.ones((xyz.shape[0], 1))))
		xyz = np.dot(xyzw, poses[pose_name].T)[:, :3]
		pointcloud.extend(xyz)
	
	if len(pointcloud) > 0:
		write_pointcloud(np.array(pointcloud), output_folder, pose_name.split('_')[1], output_format, FORMAT_XYZ)


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list):
	if not os.path.exists(input_path):
		return
	
	# Bldg4 and Bldg5 are the test scenes that have no groundtruth poses per fragment
	processing_order = {'Bldg1' : {'Stage1' : {}, 'Stage2' : {}, 'Stage3' : {}},
					 	'Bldg2' : {'Stage1' : {}, 'Stage2' : {}, 'Stage3' : {}, 'Stage4' : {}, 'Stage5' : {}, 'Stage6' : {}},
						'Bldg3' : {'Stage1' : {}, 'Stage2' : {}, 'Stage3' : {}, 'Stage4' : {}, 'Stage5' : {}},
						'Bldg6' : {'Stage1' : {}, 'Stage2' : {}, 'Stage3' : {}, 'Stage4' : {}, 'Stage5' : {}, 'Stage6' : {}}}
	
	# load poses per PLY file from pose graphs
	poses_folder = os.path.join(input_path, 'raw', 'pose_graph')
	for split in os.scandir(poses_folder):
		if split.name != 'test':
			for file in os.scandir(split.path):
				with open(file.path, 'r') as f:
					poses = json.load(f)
					for node in poses['nodes']:
						scene, epoch = node['name'].split('_')[0:2]
						if np.any(np.array(node['global_transform']) != 0):
							processing_order[scene][epoch][node['name']] = np.array(node['global_transform'])

	# create output folders and extract point clouds
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	if inclusion_list is not None:
		for entry in inclusion_list:
			scene, epoch = entry.split('_')[0:2]
			output_path = os.path.join(output_folder, scene)
			os.makedirs(output_path, exist_ok=True)
			extract_pointcloud(os.path.join(input_path, 'raw', 'point_cloud'), processing_order[scene][epoch], output_path, output_format)
	else:
		for scene in tqdm(processing_order):
			for epoch in tqdm(processing_order[scene], leave=False):
				if (scene + '_' + epoch) not in exclusion_list:
					output_path = os.path.join(output_folder, scene)
					os.makedirs(output_path, exist_ok=True)
					extract_pointcloud(os.path.join(input_path, 'raw', 'point_cloud'), processing_order[scene][epoch], output_path, output_format)

if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format,
				 args.exclusion_list,
				 args.inclusion_list)