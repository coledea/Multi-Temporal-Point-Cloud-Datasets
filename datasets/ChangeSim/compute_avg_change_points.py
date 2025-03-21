import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from utils.evaluation import Statistics, print_dataset_statistics


parser = argparse.ArgumentParser(prog='ChangeSim - Dataset Avg. Change Points Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_change_percentage(folder_path):
	for image in tqdm(list(os.scandir(folder_path)), leave=False):
		im = cv2.imread(image.path, 0)
		change_pixels =  cv2.countNonZero(im) / (im.shape[0] * im.shape[1])
		return change_pixels


def compute_avg_change_points(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	processing_order = []
	for split in os.scandir(input_folder):
		if not split.is_dir():
			continue
		for scene in os.scandir(split.path):
			for run in os.scandir(scene.path):
				processing_order.append(os.path.join(run.path, 'change_segmentation'))

	change_percentage = []
	for entry in tqdm(processing_order, leave=leave_progress_bar):
		change_percentage.append(compute_change_percentage(entry))

	print_dataset_statistics({Statistics.CHANGE_POINTS : np.array(change_percentage)}, output_log_path)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_avg_change_points(args.input_path, args.output_log, leave_progress_bar=True)