import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='ChangeSim - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	scenes = {}
	for split in os.scandir(input_folder):
		if not split.is_dir():
			continue
		for scene in os.scandir(split.path):
			if scene.name not in scenes:
				scenes[scene.name] = []
			for run in os.scandir(scene.path):
				filepath = os.path.join(run.path, 'cloud_map.ply')
				if os.path.exists(filepath):
					scenes[scene.name].append([filepath])

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar,
						   remove_duplicates=True)

	compute_dataset_statistics(list(scenes.values()), config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)