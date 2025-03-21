import os
import argparse
import numpy as np
from tqdm import tqdm
from utils.evaluation import Statistics, print_dataset_statistics
from utils.io import read_pointcloud_for_evaluation

parser = argparse.ArgumentParser(prog='KTH Moving Objects - Dataset Avg. Change Points Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_change_percentage(folder_path):
	full_scan_path = os.path.join(folder_path, 'complete_cloud.pcd')
	number_of_points = len(read_pointcloud_for_evaluation(full_scan_path))

	number_of_change_points = 0
	for file in os.scandir(folder_path):
		if '_label' in file.name and file.name.endswith('.pcd'):
			number_of_change_points += len(read_pointcloud_for_evaluation(file.path))

	return number_of_change_points / number_of_points


def compute_avg_change_points(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	processing_order = []
	for waypoint in os.scandir(input_folder):
		# Filter scenes with only one epoch
		if not waypoint.is_dir() or waypoint.name == 'WayPoint2' or waypoint.name == 'WayPoint29':
			continue
		for day in sorted(os.scandir(waypoint.path), key=lambda e: e.name):
			if not day.is_dir():
				continue
			for run in sorted(os.scandir(day.path), key=lambda e: int(e.name.split('_')[-1])):
				for subfolder in os.scandir(run.path):
					processing_order.append(subfolder.path)

	change_percentage = []
	for entry in tqdm(processing_order, leave=leave_progress_bar):
		change_percentage.append(compute_change_percentage(entry))

	print_dataset_statistics({Statistics.CHANGE_POINTS : np.array(change_percentage)}, output_log_path)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_avg_change_points(args.input_path, args.output_log, leave_progress_bar=True)