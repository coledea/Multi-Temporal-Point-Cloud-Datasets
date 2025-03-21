import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='M3C2-EP - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	scenes = {}
	for epoch in ['2017', '2018a', '2018b']:
		epoch_path = os.path.join(input_folder, epoch)
		if not os.path.exists(epoch_path):
			continue

		for scan in os.scandir(epoch_path):
			name_split = scan.name.split('_')
			scene_name = name_split[1] + '_' + name_split[2]
			if scene_name in scenes:
				scenes[scene_name].append([scan.path])
			else:
				scenes[scene_name] = [[scan.path]]

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar)

	compute_dataset_statistics(list(scenes.values()), config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)