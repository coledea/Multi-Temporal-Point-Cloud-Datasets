import os
import argparse
import csv
import numpy as np
from tqdm import tqdm
from pypcd4 import PointCloud
from scipy.spatial.transform import Rotation as R

from utils.pointcloud_format import FORMAT_XYZC
from utils.io import FileFormat, write_pointcloud

parser = argparse.ArgumentParser(prog='SZTAKI-CityCDLoc - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ allowed)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)

# for some reason, the z-component is not recorded in the csv-file, but harcoded in a matlab script. However, the value is not correct and has to be increased by a bit.
z_shifts = {'Scenario1 (Fïvám)' : 106.5610 + 2.5,
			'Scenario2 (Kálvin)' : 106.5610 + 0.4,
			'Scenario3 (Deák)' : 106.5610 + 1.75}

rotations = {'Scenario1 (Fïvám)' : -60.0,
			'Scenario2 (Kálvin)' : -36.0,
			'Scenario3 (Deák)' : 45.0}

offset = np.array([651026, 238332, 0])

def extract_pointcloud(input_path, output_format):
	scene_name = os.path.basename(input_path)
	gps_file_path = [file.path for file in os.scandir(input_path) if file.name.endswith('.csv')][0]
	with open(gps_file_path) as gps_file:
		reader = csv.reader(gps_file, delimiter=';')
		
		pointcloud_parts = []
		for row in tqdm(reader, leave=False):
			file_name = row[0].split('.')[0]
			file_path = os.path.join(input_path, 'GT change detection', row[0])

			if not os.path.exists(file_path):
				continue

			alignment_path = os.path.join(input_path, 'GT registration', file_name + '.txt')
			alignment_matrix = np.loadtxt(alignment_path)
			transformation_matrix = np.eye(4)
			transformation_matrix[:3, 3] = np.array([float(row[1].replace(',', '.')), float(row[2].replace(',', '.')), z_shifts[scene_name]])
			transformation_matrix[:3, :3] = R.from_euler('z', angles=rotations[scene_name], degrees=True).as_matrix()
			transformation_matrix = transformation_matrix @ alignment_matrix

			pointcloud = PointCloud.from_path(file_path)
			position = pointcloud[('x', 'y', 'z')].numpy()
			position = np.hstack((position, np.ones((position.shape[0], 1))))
			position = np.dot(position, transformation_matrix.T)[:, 0:3] - offset

			# The changes are encoded as colors
			colors = PointCloud.decode_rgb(pointcloud[('rgb')].numpy())
			changes = np.zeros((len(colors)))
			changes[colors[:, 0] > 0] = 1      # red means dynamic change
			changes[colors[:, 1] > 0] = 2      # green means vegetation change

			pointcloud = np.column_stack([position, changes])
			pointcloud_parts.append(pointcloud)

	pointcloud = np.row_stack(pointcloud_parts)
	write_pointcloud(pointcloud, input_path, 'epoch_2', output_format, FORMAT_XYZC, las_offsets=offset)


def extract_pointclouds(input_path, output_format):
	if not os.path.exists(input_path):
		return
	
	progress_bar = tqdm()
	for scene in os.scandir(input_path):
		if not scene.is_dir():
			continue
		extract_pointcloud(scene.path, output_format)
		progress_bar.update()

if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path,
				 args.output_format)