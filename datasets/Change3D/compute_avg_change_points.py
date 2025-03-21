import os
import laspy
import math
import argparse
import csv
import numpy as np
import open3d as o3d
from tqdm import tqdm
from utils.evaluation import Statistics, print_dataset_statistics


parser = argparse.ArgumentParser(prog='Change3D - Dataset Avg. Change Points Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


change_str_to_index = {
	"nochange" : 0,
	"removed" : 1,
	"added" : 2,
	"change" : 3,
	"color_change" : 4
}

# Faster alternative to extracting the object point clouds
# adapted from: https://github.com/SamGalanakis/ChangeDetectionDatasetViewer/blob/main/utils.py
def extract_object_fast(pointcloud, center, radius=3):
	mask = np.linalg.norm(pointcloud[:,:2] - center[:2], axis=1) < radius   # extract cylindrical environment
	pointcloud = pointcloud[mask]
	pointcloud = pointcloud[pointcloud[:,2] > 0.43]    # This threshold is used in the corresponding code for removing the groundplane


# For the paper, we used this method for extracting the objects for the change point computation.
# It uses RANSAC to find the ground plane for removal.
# Therefore, it is more precise than the alternative given in the extract_object_fast() function, but also slower.
def extract_object(original_pointcloud, center, radius=3):
	mask = np.linalg.norm(original_pointcloud[:,:2] - center[:2], axis=1) < radius   # extract cylindrical environment
	pointcloud = original_pointcloud[mask]

	# Remove the upper part of the point cloud to improve RANSAC results
	z_max = np.max(pointcloud[:,2])
	pointcloud_cropped = pointcloud[pointcloud[:,2] < z_max / 4]

	if len(pointcloud_cropped) < 3:
		return np.empty((0,3))

	# Find ground plane
	pointcloud_o3d = o3d.geometry.PointCloud()
	pointcloud_o3d.points = o3d.utility.Vector3dVector(pointcloud_cropped)
	plane, _ = pointcloud_o3d.segment_plane(distance_threshold=0.2, ransac_n=3, num_iterations=300)
	[a,b,c,d] = plane
	denominator = math.sqrt(a*a + b*b + c*c)

	# Discard points of the ground plane
	distances = np.abs(a * pointcloud[:, 0] + b * pointcloud[:, 1] + c * pointcloud[:, 2] + d) / denominator
	mask = distances > 0.2
	return pointcloud[mask]


def compute_change_percentage(first_epoch_path, second_epoch_path, label_path):
	shift = np.array([-86960, -439141, 0])    # shift to reduce coordinate sizes

	# Load change labels
	with open(label_path) as label_file:
		reader = csv.reader(label_file)
		header = next(reader)
		change_labels = [[*line[1:4], change_str_to_index[line[4]]] for line in reader]

	change_labels = np.array(change_labels, dtype=np.float32)
	change_labels[:,0:3] += shift
		
	# Compute percentage of share points
	first_epoch = laspy.read(first_epoch_path)
	first_epoch = np.vstack([first_epoch.x, first_epoch.y, first_epoch.z]).T + shift
	second_epoch = laspy.read(second_epoch_path)
	second_epoch = np.vstack([second_epoch.x, second_epoch.y, second_epoch.z]).T + shift

	overall_points = len(second_epoch)
	change_points = 0
	for change in change_labels:
		# Add removed points to the next epoch
		if change[3] == 1:
			object_cloud = extract_object(first_epoch, change[0:3])
			change_points += len(object_cloud)
			overall_points += len(object_cloud)
		elif change[3] != 0:
			object_cloud = extract_object(second_epoch, change[0:3])
			change_points += len(object_cloud)

	return change_points / overall_points


def compute_avg_change_points(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
		
	# Compute processing order
	scenes = {}
	for epoch in ['2016', '2020']:
		for file in os.scandir(os.path.join(input_folder, epoch)):
			scene_idx = file.name.split('_')[0]
			if scene_idx not in scenes:
				scenes[scene_idx] = [file.path]
			else:
				scenes[scene_idx].append(file.path)

	# Compute share of change points per second epoch
	change_percentage = []
	for entry in tqdm(list(scenes.values())):
		if len(entry) <= 1:
			continue
		label_file_name = os.path.basename(entry[0]).split('.')[0]
		label_file_name += '_' + label_file_name.split('_')[1] + '.csv'
		label_file_path = os.path.join(input_folder, 'labels', 'labeled_point_lists', '2016-2020', label_file_name)
		change_percentage.append(compute_change_percentage(entry[0], entry[1], label_file_path))
	   
	print_dataset_statistics({Statistics.CHANGE_POINTS : np.array(change_percentage)}, output_log_path)

if __name__ == '__main__':
	args = parser.parse_args()
	compute_avg_change_points(args.input_path, args.output_log, leave_progress_bar=True)