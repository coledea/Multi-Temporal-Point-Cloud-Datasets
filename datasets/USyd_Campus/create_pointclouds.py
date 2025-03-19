import os
import argparse
import cv2
import glob
import numpy as np
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
import matplotlib.pyplot as plt


from utils.pointcloud_format import FORMAT_XYZI, FORMAT_XYZRGB
from utils.io import FileFormat
from utils.rosbags import pointcloud_from_point_message, extract_poses
from utils.tile_writer import TileWriter
from utils.pointcloud_creation import get_pose_matrix, project_points_to_image, get_processing_order

parser = argparse.ArgumentParser(prog='USyd Campus - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to "[input_path]/pointclouds")')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ supported)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of epoch names to exclude for reconstruction (e.g., Week23_2018-08-15).', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of file names to include (overwrites the exclusion list)', nargs='+', type=str)
parser.add_argument('--project_images', help='Projects the RGB images onto the point cloud to get per-point colors', action='store_true')
parser.add_argument('--tile_size', help='The size of the tiles into which the scene is divided in x and y direction', default=100, type=int)

# As these do not change, we just hardcode them here
T_lidar_to_base = np.eye(4)
T_lidar_to_base[:3,3] = np.array([1.2, 0.0, 1.37])
T_lidar_to_base[:3,:3] = R.from_quat([0.0, 0.06096217687101231, 0.0, 0.9981400768384903]).as_matrix()

t_imu_to_base = np.array([0.517, 0.0, 0.255])

typestore = get_typestore(Stores.ROS1_NOETIC)

class Camera:
	def __init__(self, name):
		self.name = name
		self.T_lidar_to_cam = None
		self.projection = None
		self.undistort_map_x = None
		self.undistort_map_y = None
		self.roi = None
		self.timestamps = None
		self.video = None
		self.current_frame_number = -1
		self.current_frame = None

	def __del__(self):
		self.video.release()
	
	# find best matching image and fetch if necessary
	def __update_current_frame(self, target_timestamp):
		target_frame_number = np.searchsorted(self.timestamps, target_timestamp)
		if target_frame_number != self.current_frame_number:
			# front_video.set(cv2.CAP_PROP_POS_FRAMES, current_frame_number) is unfortunately unreliable. Therefore, we have to read every frame.
			while self.current_frame_number != target_frame_number:
				ret, image = self.video.read()
				self.current_frame_number += 1
			image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			self.current_frame = cv2.remap(image, self.undistort_map_x, self.undistort_map_y, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)  # undistort image

	# retrieves the colors for the given points by projecting them to the best fitting video frame
	# also returns a mask of points for which the colors are valid
	def get_colors_for_points(self, points_timestamp, points):
		self.__update_current_frame(points_timestamp)
		points_im, mask = project_points_to_image(points, self.T_lidar_to_cam, self.projection, self.roi)
		colors = self.current_frame[np.round(points_im[:,1]).astype(int), np.round(points_im[:,0]).astype(int)]
		return [colors, mask]


def matrix_from_transform_message(transform):
	trans = transform.translation
	rot = transform.rotation
	matrix = np.eye(4)
	matrix[:3,3] = np.array([trans.x, trans.y, trans.z])
	matrix[:3,:3] = R.from_quat([rot.x, rot.y, rot.z, rot.w]).as_matrix()
	return matrix


# TODO: A3, B0, B1
link_to_cam = {
	'gmsl_centre_link' : 'A0',
	'gmsl_left_link' : 'A1',
	'gmsl_right_link' : 'A2',
	'TODO' : 'A3',
	'TODO' : 'B0',
	'TODO' : 'B1'
}

# we read the transforms from the bag, as they sometimes change between the bags
def read_camera_data(input_folder, bag_path):
	cameras = {} 
	with Reader(bag_path) as reader:
		# read transforms
		tf_connection = [x for x in reader.connections if x.topic == '/tf_static']
		tf_c, _, tf_d = next(reader.messages(connections=tf_connection))
		tf = typestore.deserialize_ros1(tf_d, tf_c.msgtype)
		for transform in tf.transforms:
			# deserialize?
			if transform.child_frame_id in link_to_cam:
				cam_id = link_to_cam[transform.child_frame_id]
				cameras[cam_id] = Camera(cam_id)
				cameras[cam_id].T_lidar_to_cam = np.linalg.inv(matrix_from_transform_message(transform.transform))
		
		# read projection matrices and compute undistortion maps
		for connection in reader.connections:
			if connection.msgtype == 'sensor_msgs/msg/CameraInfo':
				c, _, d = next(reader.messages(connections=[connection]))
				cam_info = typestore.deserialize_ros1(d, c.msgtype)
				K = np.array(cam_info.K).reshape((3,3))
				distortion = np.array(cam_info.D)

				K_new, roi = cv2.getOptimalNewCameraMatrix(K, distortion, (cam_info.width, cam_info.height), 0.25, (cam_info.width, cam_info.height))
				mapx, mapy = cv2.fisheye.initUndistortRectifyMap(K, distortion, np.eye(3), K_new, (cam_info.width, cam_info.height), cv2.CV_16SC2)
				projection_matrix = np.eye(4)
				projection_matrix[:3,:3] = K_new
				camera_id = connection.topic.split('/')[2]
				cameras[camera_id].projection = projection_matrix
				cameras[camera_id].undistort_map_x = mapx
				cameras[camera_id].undistort_map_y = mapy
				cameras[camera_id].roi = roi

				# open video an extract image timstamps
				video_path = glob.glob(os.path.join(input_folder, '*' + camera_id + '*.h264'))[0]   # for week 1, the video name has an underscore before the extension
				cameras[camera_id].video = cv2.VideoCapture(video_path)

				image_timestamps = []
				for _, timestamp, _ in reader.messages(connections=[connection]):
					image_timestamps.append(timestamp)
				cameras[camera_id].timestamps = np.array(image_timestamps)
	return cameras


def extract_pointcloud_with_intensity(input_path, output_path, output_format, tile_size):
	bag_path = glob.glob(os.path.join(input_path, '*.bag'))[0]
	
	timestamps, poses = extract_poses(bag_path, typestore, '/vn100/odometry')
	poses[:,0:3] += t_imu_to_base
	min_timestamp = np.min(timestamps)
	max_timestamp = np.max(timestamps)

	tile_writer = TileWriter(output_path,
						  pointcloud_format=FORMAT_XYZI,
						  file_format=output_format,
						  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
						  tile_size=tile_size)
	
	with Reader(bag_path) as reader:
		points_connections = [x for x in reader.connections if x.topic == '/velodyne/front/points']
		for connection, timestamp, rawdata in tqdm(reader.messages(connections=points_connections), leave=False):
			if timestamp < min_timestamp or timestamp > max_timestamp:
				continue

			msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
			pointcloud = pointcloud_from_point_message(msg)
			xyzw = np.vstack((pointcloud[:,0:3].T, np.ones((len(pointcloud)))))
			pose_matrix = get_pose_matrix(timestamps, poses, timestamp) @ T_lidar_to_base
			xyzw = pose_matrix @ xyzw
			mask = np.where(np.any(pointcloud[:,0:2] > 0.5, axis=1))  # discard points originating from the vehicle itself
			pointcloud = np.column_stack((xyzw[:3].T[mask], pointcloud[:,3][mask]))  # the 4th column contains the intensity
			
			if len(pointcloud) > 0:
				tile_writer.add_points(pointcloud)
				
	tile_writer.close()


def extract_pointcloud_with_colors(input_path, output_path, output_format, tile_size):
	bag_path = glob.glob(os.path.join(input_path, '*.bag'))[0]

	timestamps, poses = extract_poses(bag_path, typestore, '/vn100/odometry')
	poses[:,0:3] += t_imu_to_base

	tile_writer = TileWriter(output_path,
						  pointcloud_format=FORMAT_XYZRGB,
						  file_format=output_format,
						  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
						  tile_size=tile_size)
	
	with Reader(bag_path) as reader:
		# register additional message types (tf2_msgs/msg/TFMessage and gmsl_frame_msg/msg/FrameInfo are not defined yet)
		types = {}
		for connection in reader.connections:
			types.update(get_types_from_msg(connection.msgdef, connection.msgtype))
		typestore.register(types)

		cameras = read_camera_data(input_path, bag_path)

		# compute valid point cloud timestamps (those for which images exist) and open videos
		min_valid_timestamp = timestamps[0]
		max_valid_timestamp = timestamps[-1]
		for camera in cameras.values():
			min_valid_timestamp = max(min_valid_timestamp, camera.timestamps[0])
			max_valid_timestamp = min(max_valid_timestamp, camera.timestamps[-1])

		points_connections = [x for x in reader.connections if x.topic == '/velodyne/front/points']

		for connection, timestamp, rawdata in tqdm(reader.messages(connections=points_connections), leave=False):
			if timestamp < min_valid_timestamp or timestamp > max_valid_timestamp:
				continue

			msg = typestore.deserialize_ros1(rawdata, connection.msgtype)
			pointcloud = pointcloud_from_point_message(msg)
			xyzw = np.column_stack((pointcloud[:,0:3], np.ones((len(pointcloud)))))

			colors = np.zeros((len(pointcloud), 3))
			mask = np.zeros((len(pointcloud))).astype(bool)

			# Project to images
			for camera in cameras.values():
				im_colors, cam_mask = camera.get_colors_for_points(timestamp, xyzw)
				colors[np.where(cam_mask)] = im_colors
				mask = mask | cam_mask

			# Transform to world space
			pose_matrix = get_pose_matrix(timestamps, poses, timestamp) @ T_lidar_to_base
			xyzw = pose_matrix @ xyzw.T
			mask &= np.any(pointcloud[:,0:3] > 0.5, axis=1)  # discard points originating from the vehicle itself
			pointcloud = np.column_stack((xyzw[:3].T[np.where(mask)], colors[np.where(mask)]))

			if len(pointcloud) > 0:
				tile_writer.add_points(pointcloud)

		tile_writer.close()


def extract_pointclouds(input_path, output_path, output_format, exclusion_list, inclusion_list, project_images, tile_size):
	if not os.path.exists(input_path):
		return

	# get list of rosbags to process
	processing_order = get_processing_order(os.path.join(input_path, 'rosbags'),
										 inclusion_list,
										 exclusion_list)

	# create output folders and extract point clouds
	for entry in tqdm(processing_order):
		if output_path is None:
			output_folder = os.path.join(input_path, 'pointclouds', entry.stem)
		else:
			output_folder = os.path.join(output_path, entry.stem)
		os.makedirs(output_folder, exist_ok=True)

		if project_images:
			extract_pointcloud_with_colors(entry.resolve(), output_folder, output_format, tile_size)
		else:
			extract_pointcloud_with_intensity(entry.resolve(), output_folder, output_format, tile_size)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format,
				 args.exclusion_list,
				 args.inclusion_list,
				 args.project_images,
				 args.tile_size)

