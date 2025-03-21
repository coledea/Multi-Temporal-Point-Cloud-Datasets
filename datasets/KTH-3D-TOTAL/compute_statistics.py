import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='KTH-3D-TOTAL - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	# Used for bringing the scans in the correct chronological order
	scan_order = {'Mor':'0', 'Aft':'1', 'Eve':'2'}
	sorting_function = lambda x: x.name.split('_')[2] + scan_order[x.name.split('_')[3]]

	processing_order = []
	for table in os.scandir(os.path.join(input_folder, 'pcd-annotated')):
		processing_order.append([])
		for scan in sorted(os.scandir(table.path), key=sorting_function):
			processing_order[-1].append([scan.path])

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar)
	
	compute_dataset_statistics(processing_order, config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)