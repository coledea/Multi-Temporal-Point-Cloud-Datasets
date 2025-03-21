import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from utils.evaluation import Statistics, print_dataset_statistics


parser = argparse.ArgumentParser(prog='3DCD - Dataset Avg. Change Points Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_change_percentage(image_path):
	im = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
	if im is None:
		return -1
	change_pixels =  cv2.countNonZero(im) / (im.shape[0] * im.shape[1])
	return change_pixels


def compute_avg_change_points(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
		
	processing_order = []
	for split in os.scandir(os.path.join(input_folder, 'raw')):
		if not split.is_dir():
			continue
		for file in os.scandir(os.path.join(split.path, '3D')):
			processing_order.append(file.path)

	change_percentage = []
	for entry in tqdm(processing_order, leave=leave_progress_bar):
		change_percentage.append(compute_change_percentage(entry))

	change_percentage = np.array(change_percentage)
	change_percentage = change_percentage[change_percentage >= 0]
	print_dataset_statistics({Statistics.CHANGE_POINTS : change_percentage}, output_log_path)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_avg_change_points(args.input_path, args.output_log, leave_progress_bar=True)