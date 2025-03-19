import os
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
from utils.evaluation import write_to_log
from utils.io import read_pointcloud_xyz

parser = argparse.ArgumentParser(prog='Object Change Detection - Dataset Avg. Change Points Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_avg_change_points(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	processing_order = []
	for scene in os.scandir(input_folder):
		if not scene.is_dir():
			continue
		for epoch in os.scandir(scene.path):
			if epoch.name.endswith('.pcd') and not epoch.name.endswith('1.pcd'):
				processing_order.append(Path(epoch.path))
	
	change_percentage = []
	for scan in tqdm(processing_order, leave=leave_progress_bar):
		pointcloud = read_pointcloud_xyz(str(scan.resolve()))

		# count change points in annotation file
		scan_idx = scan.stem[-1]
		annotation_path = os.path.join(input_folder, scan.parent.name, 'Annotations', 'scene' + str(scan_idx) + '_GT.anno')
		num_changes = 0
		with open(annotation_path) as annotation_file:
			for line in annotation_file.readlines():
				num_changes += len(line.split(' ')[1:])

		change_percentage.append(num_changes / len(pointcloud))

	change_percentage = np.array(change_percentage)
	message = 'Average share of labeled change points per epoch: ' + str(np.average(change_percentage))
	tqdm.write(message)
	if output_log_path:
		write_to_log(output_log_path, message)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_avg_change_points(args.input_path, args.output_log, leave_progress_bar=True)