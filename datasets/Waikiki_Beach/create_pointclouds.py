import os
import argparse
import cv2
import exifread
import numpy as np
from tqdm import tqdm
from utils.pointcloud_format import FORMAT_XYZRGB
from utils.io import write_pointcloud, FileFormat

parser = argparse.ArgumentParser(prog='Waikīkī Beach - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def create_pointclouds(input_path, output_folder, file_format, leave_progress_bar=False):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	os.makedirs(output_folder, exist_ok=True)

	processing_order = [scan for scan in os.scandir(os.path.join(input_path, 'DTMs')) if scan.name.endswith('.tif')]
	for dtm in tqdm(processing_order, leave=leave_progress_bar):
		# We don't use the dsm_to_pointcloud() function from utils.pointcloud_creation, as the process is a bit more involved with coordinate system conversions
		depth_im = cv2.imread(dtm.path, cv2.IMREAD_UNCHANGED)
		depth = depth_im.flatten()
		mask = depth > np.finfo(np.float32).min   # Discard empty values
		depth = depth[mask]

		date_string = dtm.name.split('_')[0]
		# color_valid = int(date_string) < 20200225          # Could be used to test for valid color images
		color_path = os.path.join(input_path, 'MOSAIC', date_string + '_mosaic.tif')
		color_im = cv2.cvtColor(cv2.imread(color_path), cv2.COLOR_BGR2RGB)
		color_shape = color_im.shape
		color_im = color_im.reshape(-1, 3)

		depth_world_origin = np.loadtxt(dtm.path[:-4] + '.tfw')[4:6]
		depth_pixel_scale = (0.5, -0.5)      # direction of the y-axis differs between world and image coordinates

		x, y = np.meshgrid(np.arange(depth_im.shape[1]), np.arange(depth_im.shape[0]))
		x = x.flatten()[mask] * depth_pixel_scale[0]    # we already work with offset coordinates for avoiding precision issues
		y = y.flatten()[mask] * depth_pixel_scale[1]

		with open(color_path, 'rb') as f:
			tags = exifread.process_file(f)
			color_world_origin = (tags['Image Tag 0x8482'].values[3][0], tags['Image Tag 0x8482'].values[4][0])
			color_pixel_scale = (tags['Image Tag 0x830E'].values[0][0], tags['Image Tag 0x830E'].values[1][0])

		# find corresponding color pixel: Transform to world coordinates and then to color image coordinates
		color_pixel_x = (x + depth_world_origin[0] - color_world_origin[0]) / color_pixel_scale[0]
		color_pixel_y = (y + depth_world_origin[1] - color_world_origin[1]) / color_pixel_scale[1]
		color_mask = color_pixel_x.astype(int) + np.round(np.abs(color_pixel_y)).astype(int) * color_shape[1]
		color = color_im[color_mask]

		pointcloud = np.column_stack([x, y, depth, color])
		offsets = np.array([depth_world_origin[0], depth_world_origin[1], 0])
		if file_format != FileFormat.LAS and file_format != FileFormat.LAZ:
			pointcloud[:, 0:3] += offsets
		write_pointcloud(pointcloud, output_folder, dtm.name.split('_')[0], file_format, FORMAT_XYZRGB, las_offsets=offsets)


if __name__ == '__main__':
	args = parser.parse_args()
	create_pointclouds(args.input_path, args.output_folder, args.output_format, leave_progress_bar=True)

