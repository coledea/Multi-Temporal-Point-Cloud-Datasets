import os
import argparse
from tqdm import tqdm

from utils.pointcloud_creation import dsm_to_pointcloud
from utils.io import write_pointcloud, FileFormat
from utils.pointcloud_format import FORMAT_XYZRGB, FORMAT_XYZRGBC


parser = argparse.ArgumentParser(prog='3DCD - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of 3DCD')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def create_pointclouds(input_path, output_folder, file_format, leave_progress_bar=False):
	if not os.path.exists(input_path):
		return
		
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	for split in tqdm(os.listdir(os.path.join(input_path, 'raw')), leave=leave_progress_bar):
		for year in tqdm(['2010', '2017'], leave=False):
			split_path = os.path.join(input_path, 'raw', split)
			rgb_folder = os.path.join(split_path, year)
			for file in tqdm(os.listdir(rgb_folder), leave=False):
				file_name = file.split('.')[0]
				rgb_path = os.path.join(split_path, year, file)
				dsm_path = os.path.join(split_path, 'DSM_' + year, file)
				output_path = os.path.join(output_folder, split, file_name)

				os.makedirs(output_path, exist_ok=True)

				# Only add the change label to the second epoch
				if year == '2010':
					pointcloud = dsm_to_pointcloud(dsm_path, rgb_path, None)
					write_pointcloud(pointcloud, output_path, file_name + '_' + year, file_format, FORMAT_XYZRGB)
				else:
					annotation_path = os.path.join(split_path, '3D', file)
					pointcloud = dsm_to_pointcloud(dsm_path, rgb_path, annotation_path, annotation_binary_threshold=0.001)
					write_pointcloud(pointcloud, output_path, file_name + '_' + year, file_format, FORMAT_XYZRGBC)



if __name__ == '__main__':
	args = parser.parse_args()
	create_pointclouds(args.input_path, args.output_folder, args.output_format, leave_progress_bar=True)

