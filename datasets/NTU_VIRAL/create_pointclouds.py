import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore

from utils.pointcloud_format import FORMAT_XYZI
from utils.io import FileFormat
from utils.tile_writer import TileWriter
from utils.rosbags import pointcloud_from_point_message
from utils.pointcloud_creation import get_pose_matrix, project_points_to_image, get_processing_order


parser = argparse.ArgumentParser(prog='NTU VIRAL - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to "[input_path]/pointclouds")')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ possible)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of epoch names to exclude for reconstruction (e.g., eee_01).', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of epoch names to include (overwrites the exclusion list)', nargs='+', type=str)
parser.add_argument('--project_images', help='Projects the monochromatic images onto the point cloud to get per-point greyscale values', action='store_true')
parser.add_argument('--num_tiles', help='The number of tiles into which the scene should be divided in x and y direction', nargs=2, default=[2,2])

typestore = get_typestore(Stores.ROS1_NOETIC)

# Transform matrices
T_lidar_horz_to_base = np.eye(4)
T_lidar_horz_to_base[:3,3] = np.array([-0.05, 0.000, 0.055])

T_lidar_vert_to_base = np.linalg.inv(np.array([[-1.0, 0.0, 0.0, -0.550],
												[0.0, 0.0, 1.0, 0.030],
												[0.0, 1.0, 0.0, 0.050],
												[0.0, 0.0, 0.0, 1.000]]))

T_leftcam_to_base = np.array([[0.02183084, -0.01312053,  0.99967558,  0.00552943],
							[0.99975965,  0.00230088, -0.02180248, -0.12431302],
							[-0.00201407,  0.99991127,  0.01316761,  0.01614686], 
							[0.00000000,  0.00000000,  0.00000000,  1.00000000]])
T_lidar_vert_to_leftcam = np.linalg.inv(T_leftcam_to_base) @ T_lidar_vert_to_base
T_lidar_horz_to_leftcam = np.linalg.inv(T_leftcam_to_base) @ T_lidar_horz_to_base

T_rightcam_to_base = np.array([[-0.01916508, -0.01496218,  0.99970437,  0.00519443],
								[0.99974371,  0.01176483,  0.01934191,  0.1347802],
								[-0.01205075,  0.99981884,  0.01473287,  0.01465067],
								[0.00000000,  0.00000000,  0.00000000,  1.00000000]])
T_lidar_vert_to_rightcam = np.linalg.inv(T_rightcam_to_base) @ T_lidar_vert_to_base
T_lidar_horz_to_rightcam = np.linalg.inv(T_rightcam_to_base) @ T_lidar_horz_to_base

# Camera parameters
im_width = 752
im_height = 480

proj_left = np.array([
    [4.250258563372763e+02, 0.00000000e+00, 3.860151866550880e+02, 0.00000000e+00],
    [0.00000000e+00, 4.267976260903337e+02, 2.419130336743440e+02, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
left_dist = np.array([-0.288105327549552, 0.074578284234601, 7.784489598138802e-04, -2.277853975035461e-04, 0.0])

proj_left_undistort, roi_left = cv2.getOptimalNewCameraMatrix(proj_left[:3,:3], left_dist, (im_width, im_height), 1, (im_width, im_height))
left_mapx, left_mapy = cv2.initUndistortRectifyMap(proj_left[:3, :3], left_dist, None, proj_left_undistort, (im_width, im_height), cv2.CV_32FC1)
proj_left[:3,:3] = proj_left_undistort

proj_right = np.array([
    [4.313364265799752e+02, 0.00000000e+00, 3.548956286992647e+02, 0.00000000e+00],
    [0.00000000e+00, 4.327527965378035e+02, 2.325508916495161e+02, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
right_dist = np.array([-0.300267420221178, 0.090544063693053, 3.330220891093334e-05, 8.989607188457415e-05, 0.0])

proj_right_undistort, roi_right = cv2.getOptimalNewCameraMatrix(proj_right[:3, :3], right_dist, (im_width, im_height), 1, (im_width, im_height))
right_mapx, right_mapy = cv2.initUndistortRectifyMap(proj_right[:3, :3], right_dist, None, proj_right_undistort, (im_width, im_height), cv2.CV_32FC1)
proj_right[:3,:3] = proj_right_undistort


# retrieves the colors for the given points using the given image message
# also returns a mask of points for which the colors are valid
def get_colors_from_img_message(message, points, T_lidar_to_cam, projection, mapX, mapY, roi):
	connection, _, rawdata = message
	msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
	img = msg.data.reshape((im_height, im_width))
	# undistort images using precomputed maps
	img = cv2.remap(img, mapX, mapY, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
	points_im, mask = project_points_to_image(points, T_lidar_to_cam, projection, roi)
	colors = img[np.round(points_im[:,1]).astype(int), np.round(points_im[:,0]).astype(int)]
	return [colors, mask]


def extract_pointcloud_with_intensity(input_path, output_path, output_format, num_tiles):
	poses_raw = np.loadtxt(os.path.join(input_path, 'odometry.csv'), delimiter=',', skiprows=1)
	poses = poses_raw[:, 3:10]
	timestamps = poses_raw[:, 0]

	tile_writer = TileWriter(output_path,
					  pointcloud_format=FORMAT_XYZI,
					  file_format=output_format,
					  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
					  num_tiles=num_tiles)

	with Reader(os.path.join(input_path, os.path.basename(input_path) + '.bag')) as reader:
		points_connections = [x for x in reader.connections if (x.topic == '/os1_cloud_node1/points') or (x.topic == '/os1_cloud_node2/points')]
		for connection, timestamp, rawdata in tqdm(reader.messages(connections=points_connections), leave=False):
			if timestamp < timestamps[0] or timestamp > timestamps[-1]:
				continue

			# deserialize point cloud
			msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
			pointcloud = pointcloud_from_point_message(msg)
			xyzw = np.vstack((pointcloud[:,0:3].T, np.ones((len(pointcloud)))))

			# transform to world coordinate system
			T_lidar_to_base = T_lidar_horz_to_base if connection.topic == '/os1_cloud_node1/points' else T_lidar_vert_to_base
			pose_matrix = get_pose_matrix(timestamps, poses, timestamp) @ T_lidar_to_base
			xyzw = pose_matrix @ xyzw
			mask = np.where(np.any(pointcloud[:,0:3] > 0.6, axis=1))  # discard points originating from the UAV itself
			pointcloud = np.column_stack((xyzw[:3].T[mask], pointcloud[:,3][mask]))  # the 4th column contains the intensity

			if len(pointcloud) > 0:
				tile_writer.add_points(pointcloud)

		tile_writer.close()


def extract_pointcloud_with_colors(input_path, output_path, output_format, num_tiles):
	poses_raw = np.loadtxt(os.path.join(input_path, 'odometry.csv'), delimiter=',', skiprows=1)
	poses = poses_raw[:, 3:10]
	timestamps = poses_raw[:, 0]

	tile_writer = TileWriter(output_path,
				  pointcloud_format=FORMAT_XYZI,
				  file_format=output_format,
				  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
				  num_tiles=num_tiles)
	
	with Reader(os.path.join(input_path, os.path.basename(input_path) + '.bag')) as reader:
		rgb_left_connections = [x for x in reader.connections if x.topic == '/left/image_raw']
		rgb_right_connections = [x for x in reader.connections if x.topic == '/right/image_raw']

		# extract image timestamps
		left_images_timestamps = []
		right_images_timestamps = []
		for connection, timestamp, _ in reader.messages(connections=rgb_left_connections):
			left_images_timestamps.append(timestamp)
		for connection, timestamp, _ in reader.messages(connections=rgb_right_connections):
			right_images_timestamps.append(timestamp)

		min_valid_timestamp = min(timestamps[0], left_images_timestamps[0], right_images_timestamps[0])
		max_valid_timestamp = max(timestamps[-1], left_images_timestamps[-1], right_images_timestamps[-1])

		points_connections = [x for x in reader.connections if (x.topic == '/os1_cloud_node1/points') or (x.topic == '/os1_cloud_node2/points')]
		points_messages = reader.messages(connections=points_connections)
		_, timestamp, rawdata = next(points_messages)

		# as the images are sampled with lower frequency than the point clouds, we have to re-use an image multiple times
		# we store the current image and only fetch the next one, if its timestamp fits the current point cloud frame better
		rgb_left_messages = reader.messages(connections=rgb_left_connections)
		rgb_right_messages = reader.messages(connections=rgb_right_connections)
		left_image = next(rgb_left_messages)
		right_image = next(rgb_right_messages)

		for connection, timestamp, rawdata in tqdm(reader.messages(connections=points_connections), leave=False):
			if timestamp < min_valid_timestamp or timestamp > max_valid_timestamp:
				continue

			# find best matching image and fetch if necessary
			target_timestamp_left = left_images_timestamps[np.searchsorted(left_images_timestamps, timestamp)]
			while left_image[1] != target_timestamp_left:
				left_image = next(rgb_left_messages)
			
			target_timestamp_right = right_images_timestamps[np.searchsorted(right_images_timestamps, timestamp)]
			while right_image[1] != target_timestamp_right:
				right_image = next(rgb_right_messages)

			# deserialize point cloud
			msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
			pointcloud = pointcloud_from_point_message(msg)
			xyzw = np.column_stack((pointcloud[:,0:3], np.ones((len(pointcloud)))))
 
			colors = np.zeros((len(pointcloud)))
			mask = np.zeros((len(pointcloud))).astype(bool)

			# Project to left cam
			T_lidar_to_leftcam = T_lidar_horz_to_leftcam if connection.topic == '/os1_cloud_node1/points' else T_lidar_vert_to_leftcam
			im_colors, cam_mask = get_colors_from_img_message(left_image, xyzw, T_lidar_to_leftcam, proj_left, left_mapx, left_mapy, roi_left)
			colors[np.where(cam_mask)] = im_colors
			mask = mask | cam_mask

			# Project to right cam
			T_lidar_to_rightcam = T_lidar_horz_to_rightcam if connection.topic == '/os1_cloud_node1/points' else T_lidar_vert_to_rightcam
			im_colors, cam_mask = get_colors_from_img_message(right_image, xyzw, T_lidar_to_rightcam, proj_right, right_mapx, right_mapy, roi_right)
			colors[np.where(cam_mask)] = im_colors
			mask = mask | cam_mask

			# Transform to world space
			T_lidar_to_base = T_lidar_horz_to_base if connection.topic == '/os1_cloud_node1/points' else T_lidar_vert_to_base
			pose_matrix = get_pose_matrix(timestamps, poses, timestamp) @ T_lidar_to_base
			xyzw = pose_matrix @ xyzw.T
			mask &= np.where(np.any(pointcloud[:,0:3] > 0.6, axis=1))  # discard points originating from the UAV itself
			pointcloud = np.column_stack((xyzw[:3].T[np.where(mask)], colors[np.where(mask)]))

			if len(pointcloud) > 0:
				tile_writer.add_points(pointcloud)

	tile_writer.close()



def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list, project_images, num_tiles):
	if not os.path.exists(input_path):
		return

	# get list of epochs to process
	processing_order = get_processing_order(os.path.join(input_path, 'rosbags'),
										 inclusion_list,
										 exclusion_list)

	# create output folders and extract point clouds
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')

	for entry in tqdm(processing_order):
		scan_name_split = entry.stem.split('_')
		output_path = os.path.join(output_folder, scan_name_split[0], 'epoch_' + scan_name_split[1])
		os.makedirs(output_path, exist_ok=True)

		if project_images:
			extract_pointcloud_with_colors(entry.resolve(), output_path, output_format, np.array(num_tiles))
		else:
			extract_pointcloud_with_intensity(entry.resolve(), output_path, output_format, np.array(num_tiles))

if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format,
				 args.exclusion_list,
				 args.inclusion_list,
				 args.project_images,
				 args.num_tiles)