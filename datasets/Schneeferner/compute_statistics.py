import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='Schneeferner - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
			return
	
	# We chose 180419_101733 as reference scan, as it covers the full area (in contrast to the first few scans) and does not contain as many outliers as other scans
	epochs = [[os.path.join(input_folder, '180419_101733.laz')]]
	for epoch in os.scandir(input_folder):
		if epoch.name.endswith('.laz') and epoch.name != '180419_101733.laz':
			epochs.append([epoch.path])
	
	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar)
	
	compute_dataset_statistics([epochs], config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)