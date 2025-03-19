import os
import argparse
import cv2
import numpy as np
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore

from utils.pointcloud_format import FORMAT_XYZI, FORMAT_XYZRGB
from utils.io import FileFormat
from utils.rosbags import pointcloud_from_point_message, extract_poses
from utils.tile_writer import TileWriter
from utils.pointcloud_creation import get_pose_matrix, project_points_to_image, get_processing_order


parser = argparse.ArgumentParser(prog='BLT - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to "[input_path]/pointclouds")')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ supported)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of file names to exclude for reconstruction.', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of file names to include (overwrites the exclusion list)', nargs='+', type=str)
parser.add_argument('--project_images', help='Projects the RGB images onto the point cloud to get per-point colors', action='store_true')
parser.add_argument('--num_tiles', help='The number of tiles into which the scene should be divided in x and y direction', nargs=2, default=[4,4])


# Transform matrices
T_frontcam_to_base = np.eye(4)
T_frontcam_to_base[:3, :3] = R.from_quat([0.0, 0.017, 0.0, 1.0]).as_matrix()
T_frontcam_to_base[:3, 3] = np.array([0.345, 0.06, 0.763])
T_base_to_frontcam = np.linalg.inv(T_frontcam_to_base)

T_sidecam_to_base = np.eye(4)
T_sidecam_to_base[:3, :3] = R.from_quat([0.0, 0.0, 0.707, 0.707]).as_matrix()
T_sidecam_to_base[:3, 3] = np.array([-0.083,0.3,0.934])
T_base_to_sidecam = np.linalg.inv(T_sidecam_to_base)

T_lidar_to_base = np.eye(4)
T_lidar_to_base[:3,3] = np.array([-0.098, 0.000, 1.000])

T_axis_swap = np.array([[0, -1, 0, 0], [0, 0, -1, 0], [1, 0, 0, 0], [0, 0, 0, 1]])

T_lidar_to_frontcam = T_base_to_frontcam @ T_lidar_to_base
T_lidar_to_frontcam = T_axis_swap @ T_lidar_to_frontcam   # swap axes to align with image plane
T_lidar_to_sidecam = T_base_to_sidecam @ T_lidar_to_base
T_lidar_to_sidecam = T_axis_swap @ T_lidar_to_sidecam   # swap axes to align with image plane


im_width = 1920
im_height = 1080

# Projection matrices - extracted from the rosbag
proj_front = np.array([
    [1.05228064e+03, 0.00000000e+00, 9.52226501e+02, 0.00000000e+00],
    [0.00000000e+00, 1.05228064e+03, 5.53573914e+02, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

proj_side = np.array([
    [1.06669202e+03, 0.00000000e+00, 9.62284729e+02, 0.00000000e+00],
    [0.00000000e+00, 1.06669202e+03, 5.40881287e+02, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00],
    [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])


typestore = get_typestore(Stores.ROS1_NOETIC)

# retrieves the colors for the given points using the given image message
# also returns a mask of points for which the colors are valid
def get_colors_from_img_message(message, points, T_lidar_to_cam, projection):
	connection, _, rawdata = message
	msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
	img = cv2.imdecode(msg.data, 0)
	points_im, mask = project_points_to_image(points, T_lidar_to_cam, projection, [0, 0, im_width, im_height])
	colors = img[np.round(points_im[:,1]).astype(int), np.round(points_im[:,0]).astype(int)]
	return [colors, mask]


def extract_pointcloud_with_intensity(input_path, output_path, output_format, num_tiles=np.array([4,4])):
	timestamps, poses = extract_poses(input_path, typestore, '/robot_pose')
	min_timestamp = np.min(timestamps)
	max_timestamp = np.max(timestamps)

	tile_writer = TileWriter(output_path,
						  pointcloud_format=FORMAT_XYZI,
						  file_format=output_format,
						  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
						  num_tiles=num_tiles)

	with Reader(input_path) as reader:
		points_connections = [x for x in reader.connections if x.topic == '/os_cloud_node/points']
		for connection, timestamp, rawdata in tqdm(reader.messages(connections=points_connections), leave=False):
			if timestamp < min_timestamp or timestamp > max_timestamp:
				continue

			msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
			pointcloud = pointcloud_from_point_message(msg)
			xyzw = np.vstack((pointcloud[:,0:3].T, np.ones((len(pointcloud)))))
			pose_matrix = get_pose_matrix(timestamps, poses, timestamp) @ T_lidar_to_base
			xyzw = pose_matrix @ xyzw
			pointcloud = np.column_stack((xyzw[:3].T, pointcloud[:,3]))  # the 4th column contains the intensity
			
			if len(pointcloud) > 0:
				tile_writer.add_points(pointcloud)

		tile_writer.close()

# assumes the synced rosbags
def extract_pointcloud_with_colors(input_path, output_path, output_format, num_tiles=np.array([4,4])):
	timestamps, poses = extract_poses(input_path, typestore, '/robot_pose')
	min_timestamp = np.min(timestamps)
	max_timestamp = np.max(timestamps)

	tile_writer = TileWriter(output_path,
						  pointcloud_format=FORMAT_XYZRGB,
						  file_format=output_format,
						  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
						  num_tiles=num_tiles)

	with Reader(input_path) as reader:
		points_connections = [x for x in reader.connections if x.topic == '/os_cloud_node/points']
		rgb_front_connections = [x for x in reader.connections if x.topic == '/front/zed_node/rgb/image_rect_color/compressed']
		rgb_side_connections = [x for x in reader.connections if x.topic == '/side/zed_node/rgb/image_rect_color/compressed']
		rgb_front_messages = reader.messages(connections=rgb_front_connections)
		rgb_side_messages = reader.messages(connections=rgb_side_connections)

		for connection, timestamp, rawdata in tqdm(reader.messages(connections=points_connections), leave=False):
			if timestamp < min_timestamp or timestamp > max_timestamp:
				continue

			msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
			pointcloud = pointcloud_from_point_message(msg)
			xyzw = np.column_stack((pointcloud[:,0:3], np.ones((len(pointcloud)))))
 
			colors = np.zeros((len(pointcloud), 3))
			mask = np.zeros((len(pointcloud))).astype(bool)

			# Project to front cam
			im_colors, cam_mask = get_colors_from_img_message(next(rgb_front_messages), xyzw, T_lidar_to_frontcam, proj_front)
			colors[np.where(cam_mask)] = im_colors
			mask = mask | cam_mask

			# Project to side cam
			im_colors, cam_mask = get_colors_from_img_message(next(rgb_side_messages), xyzw, T_lidar_to_sidecam, proj_side)
			colors[np.where(cam_mask)] = im_colors
			mask = mask | cam_mask

			# Transform to world space
			pose_matrix = get_pose_matrix(timestamps, poses, timestamp) @ T_lidar_to_base
			xyzw = pose_matrix @ xyzw.T
			pointcloud = np.hstack((xyzw[:3].T[np.where(mask)], colors[np.where(mask)]))

			if len(pointcloud) > 0:
				tile_writer.add_points(pointcloud)

		tile_writer.close()


def extract_pointclouds(input_path, output_path, output_format, exclusion_list, inclusion_list, project_images, num_tiles):
	if not os.path.exists(input_path):
		return

	# get list of rosbags to process
	processing_order = get_processing_order(os.path.join(input_path, 'rosbags', 'Ktima Gerovassiliou'),
										 inclusion_list,
										 exclusion_list)

	# create output folders and extract point clouds
	for entry in tqdm(processing_order):
		if output_path is None:
			output_folder = os.path.join(input_path, 'pointclouds', entry.stem)
		else:
			output_folder = os.path.join(output_path, entry.stem)
		os.makedirs(output_path, exist_ok=True)

		if project_images:
			extract_pointcloud_with_colors(entry.resolve(), output_folder, output_format, np.array(num_tiles))
		else:
			extract_pointcloud_with_intensity(entry.resolve(), output_folder, output_format, np.array(num_tiles))

if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format,
				 args.exclusion_list,
				 args.inclusion_list,
				 args.project_images,
				 args.num_tiles)

