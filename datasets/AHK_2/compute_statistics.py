import os
import argparse
from utils.evaluation import Statistics, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='AHK 2 - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return

	regions = { }
	for epoch in os.scandir(input_folder):
		if not epoch.is_dir():
			continue
		for region in os.scandir(epoch.path):
			region_name = region.name.split('_')[2]
			if region_name not in regions:
				regions[region_name] = [[region.path]]
			else:
				regions[region_name].append([region.path])

	compute_dataset_statistics(list(regions.values()), 
							[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE], 
							output_log_path, 
							leave_progress_bar,
							position_offset=[-653000, -5189000, -2600])     # shift to avoid precision errors


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)