import os
import argparse
import plyfile
import numpy as np
from tqdm import tqdm
from utils.evaluation import Statistics, avg_neighbor_distance, print_dataset_statistics

parser = argparse.ArgumentParser(prog='Urb3DCD-v2 - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	processing_order = []
	for folder in os.scandir(input_folder):
		if not os.path.isdir(folder.path):
			continue
		for split in os.scandir(folder.path):
			if not os.path.isdir(split.path):
				continue
			for scene in os.scandir(split.path):
				if not os.path.isdir(scene.path):
					continue
				for epoch in ['pointCloud0.ply', 'pointCloud1.ply']:
					processing_order.append(os.path.join(scene.path, epoch))

	# As custom parsing is required for the PLY files, we don't use utils.evaluation.compute_dataset_statistics here
	statistics = {Statistics.NUM_POINTS:[], Statistics.AVG_DISTANCE:[], Statistics.CHANGE_POINTS:[]}
	for scan in tqdm(processing_order, leave=leave_progress_bar):
		pointcloud_raw = plyfile.PlyData.read(scan)
		pointcloud = np.vstack([pointcloud_raw['params']['x'], pointcloud_raw['params']['y'], pointcloud_raw['params']['z']]).transpose()
		statistics[Statistics.NUM_POINTS].append(len(pointcloud))
		statistics[Statistics.AVG_DISTANCE].append(avg_neighbor_distance(pointcloud))

		if scan.endswith('pointCloud1.ply'):
			changes = pointcloud_raw['params']['label_ch']
			num_changes = np.count_nonzero(changes > 0)
			change_ratio = num_changes / len(pointcloud)
			statistics[Statistics.CHANGE_POINTS].append(change_ratio)

	statistics = [np.array(entry) for entry in statistics.values()]
	print_dataset_statistics(statistics, [Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.CHANGE_POINTS], output_log_path)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)