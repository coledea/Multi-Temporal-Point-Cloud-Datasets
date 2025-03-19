import os
import argparse
import laspy
import numpy as np
import datashader as ds
import pandas as pd
import datashader.transfer_functions as tf
from datashader.utils import export_image
from tqdm import tqdm

parser = argparse.ArgumentParser(prog='USyd Campus - Render to Groundplane')
parser.add_argument('input_path', help='The folder with the extracted pointclouds')
parser.add_argument('output_folder', help='Path of a folder where the resulting images should be stored')


def render_to_image(input_folder, output_path, shift=np.array([0,0])):
	accumulated_image = None
	for tile in tqdm(list(os.scandir(input_folder)), leave=False):
		pointcloud_las = laspy.read(tile.path)
			
		if len(pointcloud_las.x) < 2:
			continue

		dataframe = pd.DataFrame({'x': pointcloud_las.x + shift[0], 'y': pointcloud_las.y + shift[0]})
		canvas = ds.Canvas(plot_width=2000, plot_height=2000, x_range=(-300,1200), y_range=(-800,400))
		agg = canvas.points(dataframe, 'x', 'y')
		img = tf.shade(agg, cmap='red', how='log')
		accumulated_image = img if accumulated_image is None else tf.stack(accumulated_image, img)

	export_image(accumulated_image, output_path)

def render_to_images(input_folder, output_folder):
	if not os.path.exists(input_folder):
		return
	
	# Some scans have to be shifted to fit into the image
	shifts = np.zeros((49,2))
	shifts[0] = np.array([0, 300])
	shifts[3] = np.array([600, -400])
	shifts[10] = np.array([300, -300])
	shifts[9] = np.array([200, -200])
	shifts[[21, 23, 31, 35, 40, 44]] = np.array([0, 100])
	shifts[43] = np.array([0, 800])

	os.makedirs(args.output_folder, exist_ok=True)

	for idx, scan in tqdm(enumerate(sorted(list(os.scandir(input_folder)), key=lambda e:e.name))):
		output_path = os.path.join(output_folder, scan.name + '.png')
		render_to_image(scan.path, output_path, shifts[idx])


if __name__ == '__main__':
	args = parser.parse_args()
	render_to_images(args.input_path, args.output_folder)
