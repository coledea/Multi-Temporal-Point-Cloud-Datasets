import os
import argparse
from utils.evaluation import Statistics, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='3DCD - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the point clouds created from 3DCD')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	processing_order = []
	
	for split in os.scandir(input_folder):
		if not split.is_dir():
			continue
		for scene in os.scandir(split.path):
			if not scene.is_dir():
				continue
			processing_order.append([])
			for epoch in os.scandir(scene.path):
				processing_order[-1].append([epoch.path])

	compute_dataset_statistics(processing_order, 
							[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE], 
							output_log_path, 
							leave_progress_bar)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)