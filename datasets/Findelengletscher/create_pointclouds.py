import os
import argparse
from tqdm import tqdm
from utils.pointcloud_format import FORMAT_XYZ
from utils.pointcloud_creation import dsm_to_pointcloud
from utils.io import write_pointcloud, FileFormat


parser = argparse.ArgumentParser(prog='Findelengletscher - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def create_pointclouds(input_path, output_folder, file_format, leave_progress_bar=False):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')
	os.makedirs(output_folder, exist_ok=True)

	epochs = [epoch for epoch in os.scandir(os.path.join(input_path, 'raw'))]
	for epoch in tqdm(epochs, leave=leave_progress_bar):
		epoch_path = os.path.join(epoch.path, epoch.name + '.tif')
		pointcloud = dsm_to_pointcloud(epoch_path, None, None, only_positive_dsm_values=True)
		write_pointcloud(pointcloud, output_folder, epoch.name, file_format, FORMAT_XYZ, las_precision=1000)


if __name__ == '__main__':
	args = parser.parse_args()
	create_pointclouds(args.input_path, args.output_folder, args.output_format, leave_progress_bar=True)

