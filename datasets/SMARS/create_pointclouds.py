import os
import argparse
import numpy as np
from tqdm import tqdm
from utils.pointcloud_format import FORMAT_XYZRGBS, FORMAT_XYZRGBSC
from utils.io import write_pointcloud, FileFormat
from utils.pointcloud_creation import dsm_to_pointcloud, read_image

parser = argparse.ArgumentParser(prog='SMARS - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def create_pointclouds(input_path, output_folder, file_format, leave_progress_bar=False):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	for scene in tqdm(list(os.scandir(os.path.join(input_path, 'SMARS_Release'))), leave=leave_progress_bar):
		for sampling_distance in tqdm(list(os.scandir(scene.path)), leave=False):
			if not sampling_distance.is_dir():
				continue
			for epoch in tqdm(['pre', 'post'], leave=False):
				epoch_path = os.path.join(sampling_distance.path, epoch, 'original')
				if not os.path.exists(epoch_path):
					continue

				dsm_path = os.path.join(epoch_path, '_'.join([scene.name, sampling_distance.name, epoch, 'dsm.tif']))
				color_path = os.path.join(epoch_path, '_'.join([scene.name, sampling_distance.name, epoch + '.tif']))
				annotation_path = os.path.join(epoch_path, '_'.join([scene.name, sampling_distance.name, epoch, 'gt.tif']))
				pointcloud = dsm_to_pointcloud(dsm_path, color_path, annotation_path)

				# add change annotations for second epoch
				if epoch == 'post':
					# handle inconsistent naming
					if scene.name == 'SParis' and  sampling_distance.name == '30cm':
						change_map_name = '_'.join([scene.name, sampling_distance.name, 'change_map_3classes_gt.tif'])
					else:
						change_map_name = '_'.join([scene.name, sampling_distance.name, 'change_map_3classes.tif'])
					change_path = os.path.join(sampling_distance.path, 'change_map', change_map_name)
					change_image = read_image(change_path)
					pointcloud = np.column_stack([pointcloud, change_image.flatten()])

				# take ground sampling distance into account
				point_spacing = 0.1 * float(sampling_distance.name[0])
				pointcloud[:, 0:2] *= point_spacing

				output_path = os.path.join(output_folder, scene.name, sampling_distance.name)
				os.makedirs(output_path, exist_ok=True)
				write_pointcloud(pointcloud, 
					 output_path, 
					 epoch, 
					 file_format, 
					 FORMAT_XYZRGBS if epoch == 'pre' else FORMAT_XYZRGBSC,
					 las_precision=10000)


if __name__ == '__main__':
	args = parser.parse_args()
	create_pointclouds(args.input_path, args.output_folder, args.output_format, leave_progress_bar=True)

