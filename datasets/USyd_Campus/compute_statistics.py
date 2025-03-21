import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics

parser = argparse.ArgumentParser(prog='USyd Campus - Dataset Statistics Computation')
parser.add_argument('input_path', help='The folder with the extracted point clouds')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
		
	epochs = []
	for epoch in os.scandir(input_folder):
		epochs.append([])
		for tile in os.scandir(epoch.path):
			epochs[-1].append(tile.path)

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar,
						   remove_duplicates=True,
						   tiled_epochs=True)
	
	compute_dataset_statistics([epochs], config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)