import os
import argparse
import laspy
import numpy as np
from tqdm import tqdm
from utils.evaluation import Statistics, avg_neighbor_distance, print_dataset_statistics
from utils.io import read_pointcloud_xyz


parser = argparse.ArgumentParser(prog='SZTAKI-CityCDLoc - Dataset Statistics Computation')
parser.add_argument('input_path', help='The folder with the reconstructed point clouds')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	statistics = {Statistics.NUM_POINTS : [], Statistics.AVG_DISTANCE : [], Statistics.CHANGE_POINTS : []}
	
	# we don't use utils.evaluation.compute_dataset_statistics, as we required custom loading for the change label
	for scene in tqdm(list(os.scandir(input_folder)), leave=leave_progress_bar):
		if not scene.is_dir():
			continue
		
		# epoch 1
		epoch_1_path = [file.path for file in os.scandir(scene.path) if file.name.endswith('.pcd')][0]
		pointcloud = read_pointcloud_xyz(epoch_1_path, position_offset=np.array([651026, 238332, 0]))
		statistics[Statistics.NUM_POINTS].append(len(pointcloud))
		statistics[Statistics.AVG_DISTANCE].append(avg_neighbor_distance(pointcloud[:, 0:3]))

		# epoch 2
		epoch_2_path = [file.path for file in os.scandir(scene.path) if file.name.startswith('epoch_2')][0]
		pointcloud = laspy.read(epoch_2_path)
		scales = pointcloud.header.scales
		pointcloud = np.column_stack((pointcloud.X * scales[0], pointcloud.Y * scales[1], pointcloud.Z * scales[2], pointcloud.user_data))
		statistics[Statistics.NUM_POINTS].append(len(pointcloud))
		statistics[Statistics.AVG_DISTANCE].append(avg_neighbor_distance(pointcloud[:, 0:3]))
		statistics[Statistics.CHANGE_POINTS].append(np.count_nonzero(pointcloud[:,3]) / len(pointcloud))

	print_dataset_statistics([np.array(entry) for entry in statistics.values()], 
						statistics.keys(), 
						output_log_path)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)