import os
import argparse
from tqdm import tqdm
from utils.pointcloud_format import FORMAT_XYZ
from utils.pointcloud_creation import dsm_to_pointcloud
from utils.io import write_pointcloud, FileFormat


parser = argparse.ArgumentParser(prog='Fekete and Csérep - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def create_pointclouds(input_path, output_folder, file_format, leave_progress_bar=False):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	os.makedirs(output_folder, exist_ok=True)

	input_folder = os.path.join(input_path, 'raw')
	scans = [scan.name for scan in os.scandir(input_folder) if scan.name.endswith('.tif') and 'dsm' in scan.name]
	for scan in tqdm(scans, leave=leave_progress_bar):
		pointcloud = dsm_to_pointcloud(os.path.join(input_folder, scan), None, None)
		pointcloud[:, 0:2] *= 0.5     # spacing of the DSMs is 0.5m
		write_pointcloud(pointcloud, output_folder, scan[:-4], file_format, FORMAT_XYZ, las_precision=1000)


if __name__ == '__main__':
	args = parser.parse_args()
	create_pointclouds(args.input_path, args.output_folder, args.output_format, leave_progress_bar=True)

