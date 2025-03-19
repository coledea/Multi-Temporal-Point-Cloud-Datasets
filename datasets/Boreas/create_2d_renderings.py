import os
import argparse
import laspy
import numpy as np
import datashader as ds
import pandas as pd
import datashader.transfer_functions as tf
from datashader.utils import export_image
from tqdm import tqdm

parser = argparse.ArgumentParser(prog='Boreas - Render to Groundplane')
parser.add_argument('input_path', help='The folder with the extracted pointclouds')
parser.add_argument('output_folder', help='Path of a folder where the resulting images should be stored')


def render_to_image(input_folder, output_path):
    accumulated_image = None
    for tile in tqdm(list(os.scandir(input_folder)), leave=False):
        pointcloud_las = laspy.read(tile.path)

        dataframe = pd.DataFrame({'x': np.asarray(pointcloud_las.x), 'y': np.asarray(pointcloud_las.y)})
        canvas = ds.Canvas(plot_width=3000, plot_height=3000, x_range=(-2000,1000), y_range=(-800,3000))
        agg = canvas.points(dataframe, 'x', 'y')
        img = tf.shade(agg, cmap='red', how='log')
        accumulated_image = img if accumulated_image is None else tf.stack(accumulated_image, img)

    export_image(accumulated_image, output_path)

def render_to_images(input_folder, output_folder):
    if not os.path.exists(input_folder):
        return

    os.makedirs(output_folder, exist_ok=True)
    
    for idx, scan in tqdm(list(enumerate(os.scandir(input_folder)))):
        output_path = os.path.join(output_folder, scan.name + '.png')
        render_to_image(scan.path, output_path)


if __name__ == '__main__':
    args = parser.parse_args()
    render_to_images(args.input_path, args.output_folder)


