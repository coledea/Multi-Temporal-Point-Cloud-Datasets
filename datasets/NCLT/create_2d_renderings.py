import os
import argparse
import laspy
import numpy as np
import datashader as ds
import pandas as pd
import datashader.transfer_functions as tf
from datashader.utils import export_image
from scipy.spatial.transform import Rotation as R
from tqdm import tqdm

parser = argparse.ArgumentParser(prog='NCLT - Render to Groundplane')
parser.add_argument('input_path', help='The folder with the extracted pointclouds')
parser.add_argument('output_folder', help='Path of a folder where the resulting images should be stored')


def render_to_image(input_folder, output_path, z_rotation=0):
	accumulated_image = None
	for tile in tqdm(list(os.scandir(input_folder)), leave=False):
		pointcloud_las = laspy.read(tile.path)
			
		if len(pointcloud_las.x) < 2:
			continue
			
		rotation = R.from_euler('z', z_rotation, degrees=True).as_matrix()[:2, :2]
		xy = np.stack([pointcloud_las.x, pointcloud_las.y], axis=0)
		xy = np.matmul(rotation, xy)

		dataframe = pd.DataFrame({'x': xy[0], 'y': xy[1]})
		canvas = ds.Canvas(plot_width=2000, plot_height=2000, x_range=(-300,1050), y_range=(-400,600))
		agg = canvas.points(dataframe, 'x', 'y')
		img = tf.shade(agg, cmap='red', how='log')
		accumulated_image = img if accumulated_image is None else tf.stack(accumulated_image, img)

	export_image(accumulated_image, output_path)

def render_to_images(input_folder, output_folder):
	if not os.path.exists(input_folder):
		return
	
	# The scans are not registered. Empirically derived rotations are applied first to register them coarsely.
	rotations = [0, 5, 15, 15, 15, 15, 0, 15, 15, 60, 110, 15, 20, 95, 115, 15, 20, 20, 25, 10, 18, 20, 15, 15, 10, 25, 30]

	os.makedirs(args.output_folder, exist_ok=True)

	for idx, scan in tqdm(list(enumerate(os.scandir(input_folder)))):
		output_path = os.path.join(output_folder, scan.name + '.png')
		render_to_image(scan.path, output_path, z_rotation=rotations[idx])


if __name__ == '__main__':
	args = parser.parse_args()
	render_to_images(args.input_path, args.output_folder)
