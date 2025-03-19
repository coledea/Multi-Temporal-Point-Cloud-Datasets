import os
import argparse
from utils.evaluation import Statistics, compute_dataset_statistics

parser = argparse.ArgumentParser(prog='TorWIC-SLAM - Dataset Statistics Computation')
parser.add_argument('input_path', help='The folder with the extracted point clouds')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	epochs = []
	for scene in os.scandir(input_folder):
		for epoch in os.scandir(scene.path):
			epochs.append([])
			for tile in os.scandir(epoch.path):
				epochs[-1].append(tile.path)

	compute_dataset_statistics([epochs],
							[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS], 
							output_log_path, 
							leave_progress_bar,
							tiled_epochs=True)



if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)