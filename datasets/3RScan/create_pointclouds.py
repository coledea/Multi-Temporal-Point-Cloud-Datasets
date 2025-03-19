import os
import argparse
import cv2
import json
import tempfile
import numpy as np
from tqdm import tqdm
from zipfile import ZipFile

from utils.pointcloud_format import FORMAT_XYZRGB
from utils.io import FileFormat, write_pointcloud
from utils.pointcloud_creation import RGBDReconstruction, get_processing_order, match_image_size


parser = argparse.ArgumentParser(prog='3RScan - Point Cloud Creation by RGBD Backprojection')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of scans to exclude for reconstruction (e.g., 00d42bef-778d-2ac6-848a-008ef6c19ad6)', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of scans to include (overwrites exclusion list)', nargs='+', type=str)
	
def extract_pointcloud(input_path, output_folder, output_filename, output_format, align_to_reference):
	archive_path = os.path.join(input_path, 'sequence.zip')
	if not os.path.exists(archive_path):
		return
	
	with ZipFile(archive_path) as archive_file:
		with tempfile.TemporaryDirectory() as temp_dir:
			archive_file.extractall(temp_dir)

			with open(os.path.join(temp_dir, '_info.txt')) as camera_file:
				lines = [line.split(' = ') for line in camera_file.readlines()]
				depth_resolution = [int(lines[4][1]), int(lines[5][1])]
				intrinsics = np.array(lines[9][1].split(' ')[:-1]).astype(np.float32).reshape((4,4))
				depth_shift = float(lines[6][1])
				num_frames = int(lines[11][1])

			reconstruction = RGBDReconstruction(intrinsics[:3, :3], depth_resolution)

			for idx in tqdm(range(num_frames), total=num_frames, leave=False):
				pose = np.loadtxt(os.path.join(temp_dir, f'frame-{idx:06d}.pose.txt'))
				pose = align_to_reference @ pose

				depth_path = os.path.join(temp_dir, f'frame-{idx:06d}.depth.pgm')
				depth = cv2.imread(depth_path, -1).astype(np.float64)
				depth = (depth / depth_shift).astype(np.float32)

				color_path = os.path.join(temp_dir, f'frame-{idx:06d}.color.jpg')
				color = cv2.cvtColor(cv2.imread(color_path), cv2.COLOR_BGR2RGB)
				color = match_image_size(color, depth)

				reconstruction.add_image(depth, color, pose)

	write_pointcloud(reconstruction.get_result(), output_folder, output_filename, output_format, FORMAT_XYZRGB)


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list):
	if not os.path.exists(input_path):
		return

	# dictionary that records for each scan the [reference (first epoch) name, output name, matrix for alignment to reference scan]
	scenes = {}
	with open(os.path.join(input_path, 'raw', '3RScan.json')) as json_file:
		data = json.load(json_file)
		for scene in data:
			reference_name = scene['reference']
			scenes[reference_name] = [reference_name, 'epoch_0', np.eye(4)]

			epoch_idx = 1
			if scene['type'] != 'test':
				for scan in scene['scans']:
					scan_name = scan['reference']
					if not 'transform' in scan:
						continue
					align_to_reference = np.array(scan['transform']).reshape((4,4)).T
					scenes[scan_name] = [reference_name, 'epoch_' + str(epoch_idx), align_to_reference]
					epoch_idx += 1

	processing_order = get_processing_order(os.path.join(input_path, 'raw'), inclusion_list, exclusion_list)
	processing_order = [entry for entry in processing_order if not entry.name.endswith('.json')]

	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')
	
	for entry in tqdm(processing_order):
		output_path = os.path.join(output_folder, scenes[entry.name][0])
		os.makedirs(output_path, exist_ok=True)
		extract_pointcloud(entry.resolve(), output_path, scenes[entry.name][1], output_format, scenes[entry.name][2])


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format,
				 args.exclusion_list,
				 args.inclusion_list)