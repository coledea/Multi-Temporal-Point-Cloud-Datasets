import os
import argparse
import numpy as np
from utils.pointcloud_processing import rotation_for_alignment_with_z
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='KTH Moving Objects - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	processing_order = []
	for waypoint in os.scandir(input_folder):
		# Filter scenes with only one epoch
		if not waypoint.is_dir() or waypoint.name == 'WayPoint2' or waypoint.name == 'WayPoint29':
			continue
		processing_order.append([])
		for day in sorted(os.scandir(waypoint.path), key=lambda e: e.name):
			if not day.is_dir():
				continue
			for run in sorted(os.scandir(day.path), key=lambda e: int(e.name.split('_')[-1])):
				for subfolder in os.scandir(run.path):
					processing_order[-1].append([os.path.join(subfolder.path, 'complete_cloud.pcd')])
	

	# the scans are not axis-aligned. We have to rotate them before computing the ground-plane convex hull
	# the ground plane normal was empirically determined
	rotation = rotation_for_alignment_with_z(np.array([-0.028786, -1.026719, -0.448721]))
	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar,
						   rotation_before_projection=rotation)
	
	compute_dataset_statistics(processing_order, config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)