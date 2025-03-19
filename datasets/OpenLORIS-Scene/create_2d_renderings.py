import os
import argparse
import laspy
import numpy as np
import pandas as pd
import datashader as ds
import datashader.transfer_functions as tf
from datashader.utils import export_image
from tqdm import tqdm


parser = argparse.ArgumentParser(prog='OpenLORIS-Scene - Render to Groundplane')
parser.add_argument('input_path', help='The folder with the extracted pointclouds')
parser.add_argument('output_folder', help='Path of a folder where the resulting images should be stored')

# the plot ranges for each scene
ranges = {
	'corridor':[(25,60), (-65,5)],
	'cafe':[(15,35), (15,25)],
	'home':[(-5, 15), (-10, 10)],
	'market':[(-130,-70), (-35,30)],
	'office':[(-7,5),(-5, 5)]
}

def render_to_image(input_folder, output_path, plot_range):
	accumulated_image = None
	for tile in tqdm(list(os.scandir(input_folder)), leave=False):
		pointcloud_las = laspy.read(tile.path)
			
		if len(pointcloud_las.x) < 2:
			continue

		dataframe = pd.DataFrame({'x': np.asarray(pointcloud_las.x), 'y': np.asarray(pointcloud_las.y)})
		canvas = ds.Canvas(plot_width=2000, plot_height=2000, x_range=plot_range[0], y_range=plot_range[1])
		agg = canvas.points(dataframe, 'x', 'y')
		img = tf.shade(agg, cmap='red', how='log')
		accumulated_image = img if accumulated_image is None else tf.stack(accumulated_image, img)

	export_image(accumulated_image, output_path)


def render_to_images(input_folder, output_folder):
	if not os.path.exists(input_folder):
		return
	
	for scene in tqdm(list(os.scandir(input_folder))):
		for scan in tqdm(list(os.scandir(scene.path))):
			output_folder = os.path.join(output_folder, scene.name)
			os.makedirs(output_folder, exist_ok=True)
			render_to_image(scan.path, os.path.join(output_folder, scan.name + '.png'), ranges[scene.name])


if __name__ == '__main__':
	args = parser.parse_args()
	render_to_images(args.input_path, args.output_folder)