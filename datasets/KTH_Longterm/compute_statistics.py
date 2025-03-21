import os
import argparse
import numpy as np
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics
from utils.pointcloud_processing import rotation_for_alignment_with_z


parser = argparse.ArgumentParser(prog='KTH Longterm - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	scenes = {}
	for day in sorted(os.scandir(input_folder), key=lambda e: e.name):
		if not day.is_dir() or not day.name.startswith('2014'):
			continue
		for run in sorted(os.scandir(day.path), key=lambda e: e.name):
			for room in os.scandir(run.path):
				for file in os.scandir(room.path):
					if file.name.startswith('WayPoint'):
						if file.name in scenes:
							scenes[file.name].append([file.path])
						else:
							scenes[file.name] = [[file.path]]

	
	# the scans are not axis-aligned. We have to rotate them before computing the ground-plane convex hull
	# the ground plane normal was empirically determined
	rotation = rotation_for_alignment_with_z(np.array([-0.028786, -1.026719, -0.448721]))
	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar,
						   rotation_before_projection=rotation)
	
	compute_dataset_statistics(list(scenes.values()), config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)