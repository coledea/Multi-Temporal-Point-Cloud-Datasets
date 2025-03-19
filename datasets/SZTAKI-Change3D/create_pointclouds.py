import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from utils.pointcloud_format import FORMAT_XYZC
from utils.io import FileFormat, write_pointcloud


parser = argparse.ArgumentParser(prog='SZTAKI-Change3D - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


# adapted in parts from https://learnopencv.com/3d-lidar-visualization/
def depth_image_to_pointcloud(depth_image, label_image=None):
	# The resulting point clouds are slightly bent, probably because of the cropping to 5m height and mapping to the images. 
	# However, it is not specified, how to deal with this during projecting back to a pointcloud.
	# The bending can be removed by changing the vertical angles slightly (e.g., to [6, -20.8]), but it is unclear, why.
	h_angles = np.deg2rad(np.linspace(-180, 180, depth_image.shape[1]))[np.newaxis, :]
	v_angles = np.deg2rad(np.linspace(2, -24.8, depth_image.shape[0]))[:, np.newaxis]

	x = depth_image * np.sin(h_angles) * np.cos(v_angles)
	y = depth_image * np.cos(h_angles) * np.cos(v_angles)
	z = depth_image * np.sin(v_angles)

	# Filter out points beyond the distance range
	mask = depth_image > 0
	return np.column_stack([x[mask], y[mask], z[mask], label_image[mask]])


def extract_pointcloud(input_path, output_folder, output_format):
	image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
	depth_0 = image[0:128] / 1000
	depth_1 = image[128:128*2] / 1000
	label = image[128*2:] / 18000 #  this value is scaled to 60K (probably due to the 16-bit format used for storing the range data)
	label = label.astype(np.int32)    # but the spacing between the labels is uneven. Discard fractional part.

	# split combined label
	label_0 = label & 1
	label_1 = label & 2

	epoch_0 = depth_image_to_pointcloud(depth_0, label_0)
	epoch_1 = depth_image_to_pointcloud(depth_1, label_1)
	write_pointcloud(epoch_0, output_folder, 'epoch_0', output_format, FORMAT_XYZC)
	write_pointcloud(epoch_1, output_folder, 'epoch_1', output_format, FORMAT_XYZC)


def extract_pointclouds(input_path, output_folder, output_format):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	for image in tqdm(list(os.scandir(os.path.join(input_path, 'raw')))):
		output_path = os.path.join(output_folder, image.name.split('.')[0])
		os.makedirs(output_path, exist_ok=True)
		extract_pointcloud(image.path, output_path, output_format)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format)