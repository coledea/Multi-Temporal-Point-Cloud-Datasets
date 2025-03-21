import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='Change3D - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return

	scenes = {}
	for epoch in ['2016', '2020']:
		for file in os.scandir(os.path.join(input_folder, epoch)):
			scene_idx = file.name.split('_')[0]
			if scene_idx not in scenes:
				scenes[scene_idx] = [[file.path]]
			else:
				scenes[scene_idx].append([file.path])

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar)
	
	compute_dataset_statistics(list(scenes.values()), config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)