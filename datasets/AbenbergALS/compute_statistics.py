import os
import argparse
import numpy as np
from tqdm import tqdm
from utils.evaluation import Statistics, avg_neighbor_distance, print_dataset_statistics


parser = argparse.ArgumentParser(prog='AbenbergALS - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
		
	processing_order = [
		os.path.join(input_folder, 'abenberg_data_2008', 'abenberg_data_2008.txt'),
		os.path.join(input_folder, 'abenberg_data_2009', 'abenberg_data_2009.txt')]
	
	statistics = {Statistics.NUM_POINTS : [], Statistics.AVG_DISTANCE : []}
	for epoch in tqdm(processing_order, leave=leave_progress_bar):
		pointcloud = np.genfromtxt(epoch, delimiter=',', autostrip=True)[:, 1:4]   # the first column is the class
		statistics[Statistics.NUM_POINTS].append(len(pointcloud))
		statistics[Statistics.AVG_DISTANCE].append(avg_neighbor_distance(pointcloud))

	statistics[Statistics.NUM_POINTS] = np.array(statistics[Statistics.NUM_POINTS])
	statistics[Statistics.AVG_DISTANCE] = np.array(statistics[Statistics.AVG_DISTANCE])
	print_dataset_statistics(statistics, output_log_path)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)