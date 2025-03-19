import os
import argparse
import plyfile
import numpy as np
from tqdm import tqdm
import utils.pointcloud_format as pf
from utils.io import write_pointcloud, FileFormat


parser = argparse.ArgumentParser(prog='AgScan3D Viticulture - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)

scenes = ['b07_r100_to_r94', 'b90_r131_to_r125', 'b12_r33_to_r27', 'b13_r27_to_r33', 'b13_r30_6cam']

POINTCLOUD_FORMAT = pf.PointcloudFormat([pf.X, pf.Y, pf.Z, pf.R, pf.G, pf.B])

def convert_raw_data(input_path, output_folder, filename, file_format):
    pointcloud = plyfile.PlyData.read(input_path)
    alpha = pointcloud['vertex']['alpha']
    pointcloud = np.column_stack([pointcloud['vertex']['x'], pointcloud['vertex']['y'], pointcloud['vertex']['z'], pointcloud['vertex']['red'], pointcloud['vertex']['green'], pointcloud['vertex']['blue']])
    pointcloud = pointcloud[alpha > 0]    # discard rays that did not hit anything
    write_pointcloud(pointcloud, output_folder, filename, file_format, POINTCLOUD_FORMAT)


def create_pointclouds(input_path, output_folder, file_format, leave_progress_bar=False):
	if not os.path.exists(input_path):
		return
		
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	# Compute processing order
	scenes = {'b07_r100_to_r94_01' : [], 
		   'b90_r131_to_r125' : [],
		   'b12_r33_to_r27' : [], 
		   'b13_r27_to_r33_01' : [], 
		   'b13_r30_6cam' : []}
	
	for folder in os.scandir(os.path.join(input_path, 'raw')):
		if not folder.is_dir():
			continue
		for scan in os.scandir(folder.path):
			if not scan.name.endswith('.ply'):
				continue
			for scene in scenes.keys():
				if scene in scan.name:
					scenes[scene].append(scan.path)

	# Convert the ray clouds to point clouds
	for scene in tqdm(scenes, leave=leave_progress_bar):
		if len(scenes[scene]) > 0:
			scene_path = os.path.join(output_folder, scene)
			os.makedirs(scene_path, exist_ok=True)
			for scan in tqdm(scenes[scene], leave=False):
				output_name = os.path.dirname(scan).split('_')[-1]
				convert_raw_data(scan, scene_path, output_name, file_format)


if __name__ == '__main__':
	args = parser.parse_args()
	create_pointclouds(args.input_path, args.output_folder, args.output_format, leave_progress_bar=True)

