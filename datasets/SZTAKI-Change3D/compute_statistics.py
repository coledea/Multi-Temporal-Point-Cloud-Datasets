import os
import argparse
from utils.evaluation import Statistics, compute_dataset_statistics_las


parser = argparse.ArgumentParser(prog='SZTAKI-Change3D - Dataset Statistics Computation')
parser.add_argument('input_path', help='The folder with the reconstructed point clouds')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	processing_order = []
	for scene in os.scandir(input_folder):
		processing_order.append([])
		for epoch in sorted(os.scandir(scene.path), key=lambda e: e.name):
			processing_order[-1].append([epoch.path])
	
	compute_dataset_statistics_las(processing_order, 
					[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS, Statistics.CHANGE_POINTS], 
					output_log_path, 
					leave_progress_bar,
					changes_in_all_epochs=True)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)