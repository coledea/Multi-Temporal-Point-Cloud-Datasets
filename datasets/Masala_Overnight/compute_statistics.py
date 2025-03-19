import os
import argparse
from utils.evaluation import Statistics, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='Masala Overnight - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	scenes = {}
	for day in ["2016_August_LeafOn/Aug23", "2016_August_LeafOn/Aug24"]:
		day_folder_path = os.path.join(input_folder, day)
		if not os.path.exists(day_folder_path):
			continue
		for target in os.scandir(day_folder_path):
			if "Combined" in target.name:
				continue

			if target.name not in scenes:
				scenes[target.name] = []

			for epoch in os.scandir(target.path):
				scenes[target.name].append([epoch.path])

	compute_dataset_statistics(list(scenes.values()), 
							[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS], 
							output_log_path, 
							leave_progress_bar)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)