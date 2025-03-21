import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='3RScan - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the point clouds created from 3RScan')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
		
	processing_order = []
	for scene in os.scandir(input_folder):
		processing_order.append([])
		for epoch in list(sorted(os.scandir(scene.path), key=lambda e: int(e.name.split('_')[1].split('.')[0]))):
			processing_order[-1].append([epoch.path])

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar)
	
	compute_dataset_statistics(processing_order, config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)