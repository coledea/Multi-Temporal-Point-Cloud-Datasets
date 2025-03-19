import os
import argparse
import json
import laspy
import numpy as np
from tqdm import tqdm
from utils.evaluation import write_to_log
from utils.io import read_las_with_changes

parser = argparse.ArgumentParser(prog='3RScan - Dataset Avg. Change Points Computation')
parser.add_argument('input_path', help='The folder with the sampled point clouds')
parser.add_argument('json_path_3rscan', help='The 3RScan.json file containing the change annotations')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_avg_change_points(input_folder, json_path, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return

	# load list of removed instances per scene
	removals = {}
	with open(json_path) as json_file:
		data = json.load(json_file)
		for scene in data:
			removals[scene['reference']] = []
			if scene['type'] != 'test':
				for scan in scene['scans']:
					removals[scene['reference']].append(scan['removed'])

	# compute change points
	change_percentage = []
	for scene in tqdm(os.scandir(input_folder), leave=leave_progress_bar):
		first_epoch_instances = None
		epoch_paths = sorted(os.scandir(scene.path), key=lambda e: int(e.name.split('_')[1].split('.')[0]))
		for idx, epoch in tqdm(enumerate(epoch_paths), leave=False):
			if idx == 0:
				pointcloud = laspy.read(epoch.path)
				first_epoch_instances = pointcloud.instance
			else:
				change_points = 0
				pointcloud = read_las_with_changes(epoch.path)

				# removed objects are extracted from the first epoch and counted towards the change points
				for removed_object in removals[scene.name][idx-1]:
					change_points += len(first_epoch_instances[first_epoch_instances == removed_object])

				overall_points = change_points + len(pointcloud)
				change_points += np.count_nonzero(pointcloud[:, 3] > 0)
				change_percentage.append(change_points / overall_points)

	change_percentage = np.array(change_percentage)
	message = 'Average share of labeled change points per epoch: ' + str(np.average(change_percentage))
	tqdm.write(message)
	if output_log_path:
		write_to_log(output_log_path, message)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_avg_change_points(args.input_path, args.json_path_3rscan, args.output_log, leave_progress_bar=True)