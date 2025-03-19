import os
import argparse
import cv2
import csv
import numpy as np
from tqdm import tqdm

from utils.pointcloud_format import FORMAT_XYZRGBSIC
from utils.io import FileFormat
from utils.pointcloud_creation import RGBDReconstruction
from utils.io import write_pointcloud


parser = argparse.ArgumentParser(prog='Schmid et al. - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def extract_pointcloud(input_folder, epoch, output_folder, output_format, instance_to_change, instance_to_class):
	data_folder = os.path.join(input_folder, epoch)
	if not os.path.exists(data_folder):
		return
	os.makedirs(output_folder, exist_ok=True)

	intrinsics = np.array([[320, 0, 320], [0, 320, 240], [0, 0, 1]])
	resolution = [640, 480]

	depth_images = [entry for entry in os.scandir(data_folder) if entry.name.endswith('.tiff')]

	# threshold depth to discard points outside of windows
	reconstruction = RGBDReconstruction(intrinsics, resolution, depth_threshold=10.0)

	for depth_file in tqdm(depth_images, leave=False):
		filename = depth_file.name.split('_')[0]
		depth = cv2.imread(depth_file.path, -1).astype(np.float32)

		color_path = os.path.join(data_folder, filename + '_color.png')
		color = cv2.cvtColor(cv2.imread(color_path), cv2.COLOR_BGR2RGB)

		segmentation_path = os.path.join(data_folder, filename + '_segmentation.png')
		segmentation = cv2.imread(segmentation_path, -1)

		pose_path = os.path.join(data_folder, filename + '_pose.txt')
		pose = np.loadtxt(pose_path)

		reconstruction.add_image(depth, color, pose, segmentation)

	pointcloud = reconstruction.get_result()
	changes = instance_to_change(pointcloud[:, 6])
	classes = instance_to_class(pointcloud[:, 6])
	write_pointcloud(np.column_stack([pointcloud, classes, changes]), output_folder, epoch, output_format, FORMAT_XYZRGBSIC)


def load_labels(labels_path, changes_path):
	# extract change labels per object from the changes.txt
	# We use three change labels: 1 = moved, 2 = added, 3 = removed
	changes = {}
	current_change_label = 0
	with open(changes_path) as changes_file:
		for line in changes_file.readlines():
			if line.startswith('#'):
				current_change_label += 1
			else:
				changes[line] = current_change_label

	# the label_dict maps instance IDs to classes and change labels for the two runs
	label_dict = {}
	with open(labels_path) as label_file:
		reader = csv.reader(label_file)
		header = next(reader)
		for row in reader:
			label_dict[int(row[0])] = [
				int(row[1]),    # class ID
				changes[row[8]] if (row[8] in changes and changes[row[8]] == 3) else 0, # removed objects are annotated in the first run
				changes[row[8]] if (row[8] in changes and changes[row[8]] < 3) else 0]  # moved and added objects are annotated in the second run
	return label_dict


def extract_pointclouds(input_path, output_folder, output_format):
	if not os.path.exists(input_path):
		return
	
	data_folder = os.path.join(input_path, 'flat_dataset')
	label_dict = load_labels(os.path.join(data_folder, 'groundtruth_labels.csv'), os.path.join(data_folder, 'changes.txt'))
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')
		
	for epoch in tqdm(range(1, 3)):
		instance_to_change = np.vectorize(lambda x: label_dict[x][epoch])
		instance_to_class = np.vectorize(lambda x: label_dict[x][0])
		extract_pointcloud(data_folder, 'run' + str(epoch), output_folder, output_format, instance_to_change, instance_to_class)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format)