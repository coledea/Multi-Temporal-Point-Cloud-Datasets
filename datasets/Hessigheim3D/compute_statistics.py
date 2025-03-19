import os
import argparse
from utils.evaluation import Statistics, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='Hessigheim3D - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	scenes = {}
	for epoch in os.scandir(input_folder):
		if not epoch.is_dir():
			continue
		for scan in os.scandir(os.path.join(epoch.path, 'LiDAR')):
			scene_name = scan.name.split('_')[1].split('.')[0]
			if scan.name.endswith('.laz'):
				if scene_name not in scenes:
					scenes[scene_name] = [[scan.path]]
				else:
					scenes[scene_name].append([scan.path])

	compute_dataset_statistics(list(scenes.values()), 
							[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE], 
							output_log_path, 
							leave_progress_bar)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)