import os
import argparse
import numpy as np
import xml.etree.ElementTree as ET
from tqdm import tqdm
from utils.evaluation import write_to_log
from utils.io import read_pointcloud_xyz


parser = argparse.ArgumentParser(prog='KTH-3D-TOTAL - Dataset Avg. Change Points Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def pose_from_xml(pose_element):
	return [float(pose_element[0].text), float(pose_element[1].text), float(pose_element[2].text), 
			float(pose_element[3].text), float(pose_element[4].text), float(pose_element[5].text)]


def poses_differ(pose1, pose2):
	positions_differ = abs(pose1[0] - pose2[0]) > 0.01 or abs(pose1[1] - pose2[1]) > 0.01 or abs(pose1[2] - pose2[2]) > 0.01
	orientations_differ = abs(pose1[3] - pose2[3]) > 0.1 or abs(pose1[4] - pose2[4]) > 0.1 or abs(pose1[5] - pose2[5]) > 0.1
	return positions_differ and orientations_differ


def get_annotations(label_path):
	annotations = {}
	raw_label_data = ET.parse(label_path).getroot().find('allObjects').findall('object')
	for object in raw_label_data:
		indices = object.find('indices').text
		if indices is not None:
			num_points = len(indices.split(' '))
			annotations[object.find('name').text] = [pose_from_xml(object.find('pose')), num_points]
	return annotations


def compute_avg_change_points(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	# Used for bringing the scans in the correct chronological order
	scan_order = {'Mor':'0', 'Aft':'1', 'Eve':'2'}
	sorting_function = lambda x: x.name.split('_')[2] + scan_order[x.name.split('_')[3]]

	change_percentage = []
	for table in tqdm(list(os.scandir(os.path.join(input_folder, 'pcd-annotated'))), leave=leave_progress_bar):
		last_epoch_annotations = {}
		for idx, scan in tqdm(list(enumerate(sorted(os.scandir(table.path), key=sorting_function))), leave=False):
			overall_points = len(read_pointcloud_xyz(scan.path))
			label_path = os.path.join(input_folder, 'xml-annotated', table.name, scan.name.split('.')[0] + '.xml')

			if idx == 0:
				last_epoch_annotations = get_annotations(label_path)
			else:
				change_points = 0
				current_epoch_annotations = get_annotations(label_path)

				for object_name in current_epoch_annotations:
					# Handle moved objects
					if object_name in last_epoch_annotations:
						if poses_differ(last_epoch_annotations[object_name][0], current_epoch_annotations[object_name][0]):
							change_points += current_epoch_annotations[object_name][1]
					# Handle appeared objects
					else:
						change_points += current_epoch_annotations[object_name][1]

				# Handle removed objects. They are counted as change points for the epoch, in which they do not appear anymore.
				for object_name in last_epoch_annotations:
					if object_name not in current_epoch_annotations:
						change_points += last_epoch_annotations[object_name][1]
						overall_points += last_epoch_annotations[object_name][1]
						
				last_epoch_annotations = current_epoch_annotations
				change_percentage.append(change_points / overall_points)

	change_percentage = np.array(change_percentage)
	change_percentage = change_percentage[change_percentage >= 0]
	message = 'Average share of labeled change points per epoch: ' + str(np.average(change_percentage))
	tqdm.write(message)
	if output_log_path:
		write_to_log(output_log_path, message)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_avg_change_points(args.input_path, args.output_log, leave_progress_bar=True)