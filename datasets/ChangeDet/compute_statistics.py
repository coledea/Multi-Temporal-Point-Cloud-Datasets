import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='ChangeDet - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
		
	processing_order = []
	
	for scene in os.scandir(input_folder):
		if not scene.is_dir():
			continue
		processing_order.append([])
		for epoch in ['_t0_warped', '_t1']:
			processing_order[-1].append([os.path.join(scene.path, scene.name + epoch + '.pcd')])

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar)

	compute_dataset_statistics(processing_order, config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)


# The share of change points was computed manually by retrieving the number of points from the changes.pcd and setting it in relation to the number of points in t1