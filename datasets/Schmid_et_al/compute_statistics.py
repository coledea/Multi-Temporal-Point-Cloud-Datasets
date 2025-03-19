import os
import argparse
import laspy
import numpy as np
from tqdm import tqdm
from utils.evaluation import Statistics, avg_neighbor_distance, print_dataset_statistics


parser = argparse.ArgumentParser(prog='Schmid et al. - Dataset Statistics Computation')
parser.add_argument('input_path', help='The folder with the reconstructed point clouds')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	statistics = {Statistics.NUM_POINTS : [], Statistics.AVG_DISTANCE : [], Statistics.CHANGE_POINTS : []}
	
	# we don't use utils.evaluation.compute_dataset_statistics, as we required custom loading for the change label
	change_points_epoch_1 = 0
	for run in tqdm(sorted(os.scandir(input_folder), key=lambda e: e.name), total=2, leave=leave_progress_bar):
		pointcloud = laspy.read(run.path)
		pointcloud = np.column_stack((pointcloud.x, pointcloud.y, pointcloud.z, pointcloud.user_data))
		statistics[Statistics.NUM_POINTS].append(len(pointcloud))
		statistics[Statistics.AVG_DISTANCE].append(avg_neighbor_distance(pointcloud[:, 0:3]))

		# removed points are counted as change points for the second epoch
		if run.name.startswith('run1'):
			change_points_epoch_1 = np.count_nonzero(pointcloud[:,3] == 3)
		else:
			change_points = change_points_epoch_1 + np.count_nonzero(pointcloud[:,3] == 1) + np.count_nonzero(pointcloud[:,3] == 2)
			statistics[Statistics.CHANGE_POINTS].append(change_points / (len(pointcloud) + change_points_epoch_1))
	
	print_dataset_statistics([np.array(entry) for entry in statistics.values()], 
						  statistics.keys(), 
						  output_log_path)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)