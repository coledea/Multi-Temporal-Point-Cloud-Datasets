import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R

from utils.pointcloud_format import FORMAT_XYZRGB
from utils.io import FileFormat, read_pointcloud_xyz
from utils.tile_writer import TileWriter
from utils.pointcloud_processing import remove_duplicates
from utils.pointcloud_creation import project_points_to_image, get_pose_matrix_from_pose, get_processing_order


parser = argparse.ArgumentParser(prog='TorWIC-SLAM - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of epochs to exclude for reconstruction, e.g., "june_15_2022/Aisle_CCW_Run_1"', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of epochs to include (overwrites exclusion list)', nargs='+', type=str)
parser.add_argument('--num_tiles', help='The number of tiles into which the scene should be divided in x and y direction', nargs=2, default=[2,2])

T_lidar_to_leftcam = np.eye(4)
T_lidar_to_leftcam[:3,:3] = R.from_quat([-0.6116725, 0.39292797, -0.3567415, 0.58668551]).as_matrix()
T_lidar_to_leftcam[:3, 3] = np.array([0.12944592, 0.04299934, -0.1137434])
T_lidar_to_leftcam = np.linalg.inv(T_lidar_to_leftcam)

T_lidar_to_rightcam = np.eye(4)
T_lidar_to_rightcam[:3,:3] = R.from_quat([0.41406507, -0.6100328, 0.57049433, -0.3618651]).as_matrix()
T_lidar_to_rightcam[:3, 3] = np.array([0.07686256, -0.15441064, -0.1026438])
T_lidar_to_rightcam = np.linalg.inv(T_lidar_to_rightcam)

intrinsics_left = np.array([[621.397474650905, 0, 649.644481364277], [0, 620.649424677401, 367.908146431575], [0, 0, 1]])
intrinsics_right = np.array([[613.100554293744, 0, 638.086832160361], [0, 613.903691840614, 378.314715743037], [0, 0, 1]])

projection_leftcam = np.eye(4)
projection_leftcam[:3,:3] = intrinsics_left

projection_rightcam = np.eye(4)
projection_rightcam[:3,:3] = intrinsics_right


def extract_pointcloud(input_path, output_folder, output_format, num_tiles):
	poses = np.loadtxt(os.path.join(input_path, 'traj_gt.txt'))

	tile_writer = TileWriter(output_folder,
			  pointcloud_format=FORMAT_XYZRGB,
			  file_format=output_format,
			  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
			  num_tiles=num_tiles)

	file_list = sorted(os.scandir(os.path.join(input_path, 'lidar')), key=lambda e: e.name)
	for idx, file in tqdm(enumerate(file_list)):
		im_left = cv2.imread(os.path.join(input_path, 'image_left', file.name.split('.')[0] + '.png'))
		im_left = cv2.cvtColor(im_left, cv2.COLOR_BGR2RGB)
		im_right = cv2.imread(os.path.join(input_path, 'image_right', file.name.split('.')[0] + '.png'))
		im_right = cv2.cvtColor(im_right, cv2.COLOR_BGR2RGB)

		pose_matrix = get_pose_matrix_from_pose(poses[idx][1:])
		position = read_pointcloud_xyz(file.path)
		position = np.hstack((position, np.ones((position.shape[0], 1))))
		aligned_position = np.dot(position, pose_matrix.T)[:, :3]

		# project to images to retrieve color
		# This approach colors some points wrongly, due to differing occlusion in lidar vs. camera 
		# e.g., points behind a box that are visible in the laser scan and occluded in the rgb image might receive the color of the box
		points_left, mask_left = project_points_to_image(position, 
												   T_lidar_to_leftcam, 
												   projection_leftcam, 
												   [0, 0, im_width=im_left.shape[1], im_height=im_left.shape[0]])
		
		points_right, mask_right = project_points_to_image(position, 
										   T_lidar_to_rightcam, 
										   projection_rightcam,
										   [0, 0, im_width=im_right.shape[1], im_height=im_right.shape[0]])
		
		colors = np.zeros((aligned_position.shape[0], 3))
		colors[np.where(mask_left)] = im_left[np.round(points_left[:,1]).astype(int), np.round(points_left[:,0]).astype(int)]
		colors[np.where(mask_right)] = im_right[np.round(points_right[:,1]).astype(int), np.round(points_right[:,0]).astype(int)]

		mask = mask_left | mask_right
		pointcloud = np.hstack((aligned_position[np.where(mask)], colors[np.where(mask)]))
		tile_writer.add_points(remove_duplicates(pointcloud))

	tile_writer.close()


# returns the inclusion/exclusion list for an epoch by checking for the epoch name and stripping it
def get_epoch_file_list(file_list, epoch_name):
	if file_list is None:
		return None
	else:
		return [entry.split('/')[1] for entry in file_list if epoch_name in entry]

def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list, num_tiles):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	processing_order = []
	for epoch in os.scandir(os.path.join(input_path, 'raw')):
		epoch_exclusion_list = get_epoch_file_list(exclusion_list, epoch.name)
		epoch_inclusion_list = get_epoch_file_list(inclusion_list, epoch.name)
		processing_order.extend(get_processing_order(epoch.path, epoch_inclusion_list, epoch_exclusion_list))

	for entry in tqdm(processing_order):
		# sort the scans into the respective scenes
		run_name_split = entry.name.split('_')
		if 'Hallway' in run_name_split:
			scene_name = '_'.join(run_name_split[:2])
			run_name = '_'.join(run_name_split[2:])
		else:
			scene_name = run_name_split[0]
			run_name = '_'.join(run_name_split[1:])
		output_path = os.path.join(output_folder, scene_name, entry.parent.name + '_' + run_name)
		os.makedirs(output_path, exist_ok=True)
		extract_pointcloud(entry.resolve(), output_path, output_format, np.array(num_tiles))


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
					 args.output_folder, 
					 args.output_format, 
					 args.exclusion_list, 
					 args.inclusion_list,
					 args.num_tiles)


