import os
import numpy as np
import argparse
import struct
from tqdm import tqdm
import cv2
from scipy.spatial.transform import Rotation as R

from utils.pointcloud_format import FORMAT_XYZI, FORMAT_XYZRGB
from utils.io import FileFormat
from utils.tile_writer import TileWriter
from utils.pointcloud_creation import get_pose_matrix, project_points_to_image, get_processing_order


parser = argparse.ArgumentParser(prog='NCLT - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to "[input_path]/pointclouds")')
parser.add_argument('--output_format', help='The format of the output point cloud (only LAS/LAZ supported)', type=FileFormat, choices=['LAS', 'LAZ'], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of dates to exclude for reconstruction, e.g., "2012-01-15".', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of dates to include, e.g., "2012-01-15" (overwrites the exclusion list)', nargs='+', type=str)
parser.add_argument('--project_images', help='Projects the RGB images onto the point cloud to get per-point colors', action='store_true')
parser.add_argument('--tile_size', help='The size of the tiles into which the scene is divided in x and y direction', default=50, type=int)


# inspired in some parts by https://github.com/Kitware/pyLiDAR-SLAM/blob/master/slam/dataset/nclt_dataset.py
# and the official NCLT code
point_format = 'HHHBB'
point_size_binary = struct.calcsize(point_format)

# Transform matrices
T_body_to_lb3 = np.eye(4)
T_body_to_lb3[:3, :3] = R.from_euler(seq='xyz', angles=[-179.93, -0.23, 0.50], degrees=True).as_matrix()
T_body_to_lb3[:3, 3] = np.array([0.035, 0.002, -1.23])
T_body_to_lb3 = np.linalg.inv(T_body_to_lb3)

T_lidar_to_body = np.eye(4)
T_lidar_to_body[:3,:3] = R.from_euler(seq='xyz', angles=[0.807,0.166,-90.703], degrees=True).as_matrix()
T_lidar_to_body[:3,3] = np.array([0.002,-0.004,-0.957])

im_width = 1616
im_height = 1232

cam_projection = []
T_body_to_cam = []
undistort_maps = []
undistorted_image_names = []

# Adapted from the official NCLT code
class Undistort(object):
	def __init__(self, fin, scale=1.0):
		self.fin = fin
		self.scale = scale
		data = np.loadtxt(fin, skiprows=1, dtype=np.float32)
		self.mapu = data[:, 3].reshape((im_height, im_width))
		self.mapv = data[:, 2].reshape((im_height, im_width))

		# generate a mask
		self.mask = np.ones(self.mapu.shape, dtype=np.uint8)
		self.mask = cv2.remap(self.mask, self.mapu, self.mapv, cv2.INTER_LINEAR)
		kernel = np.ones((30,30),np.uint8)
		self.mask = cv2.erode(self.mask, kernel, iterations=1)

	def undistort(self, img):
		return cv2.resize(cv2.remap(img, self.mapu, self.mapv, cv2.INTER_LINEAR),
						  (self.mask.shape[1], self.mask.shape[0]),
						  interpolation=cv2.INTER_CUBIC)
	

def load_camera_matrices(cam_params_folder):
	for cam_index in range(6):
		proj = np.eye(4)
		proj[:3,:3] = np.loadtxt(os.path.join(cam_params_folder,'K_cam%d.csv' % (cam_index)), delimiter=',')
		cam_projection.append(proj)

		x_lb3_c = np.loadtxt(os.path.join(cam_params_folder, 'x_lb3_c%d.csv' % (cam_index)), delimiter=',')
		T_cam_to_lb3 = np.eye(4)
		T_cam_to_lb3[:3,:3] = R.from_euler(seq='xyz', angles=x_lb3_c[3:], degrees=True).as_matrix()
		T_cam_to_lb3[:3, 3] = x_lb3_c[:3]
		T_body_to_cam.append(np.linalg.inv(T_cam_to_lb3) @ T_body_to_lb3)

		undistort_maps.append(Undistort(os.path.join(cam_params_folder, 'U2D_Cam%d_1616X1232.txt' % (cam_index))))

def retrieve_undistorted_image_names(undistorted_images_path):
	for cam_index in range(6):
		undistorted_images_cam_path = os.path.join(undistorted_images_path, 'Cam' + str(cam_index))
		os.makedirs(undistorted_images_cam_path, exist_ok=True)
		undistorted_image_names.append(sorted([x for x in os.listdir(undistorted_images_cam_path)]))

def verify_start_marker(s):
	m = np.array(struct.unpack('<HHHH', s))
	return len(m) >= 4 and np.all(m == 44444)


# extracts all poses and their timestamps from the pose file
def extract_poses(pose_path):
	poses = np.loadtxt(pose_path, delimiter=',', skiprows=1, usecols=(1,2,3,4,5,6))
	timestamps = np.loadtxt(pose_path, delimiter=',', skiprows=1, usecols=(0), dtype='uint64')
	valid_poses = ~np.isnan(poses).any(axis=1)
	poses = poses[valid_poses]
	timestamps = timestamps[valid_poses]

	rotations = R.from_euler(seq='xyz', angles=poses[:,3:])
	return [timestamps, np.column_stack([poses[:,0:3], rotations.as_quat()])]


def get_undistorted_image(image_path, undistorted_image_path, cam_index):
	image_name = os.path.basename(image_path)

	# undistort image and cache if not done already
	if image_name not in undistorted_image_names[cam_index]:
		if not os.path.exists(image_path):
			return None
		img = cv2.imread(image_path)
		img_undistorted = undistort_maps[cam_index].undistort(img)
		cv2.imwrite(undistorted_image_path, img_undistorted)
		img_undistorted = cv2.cvtColor(img_undistorted, cv2.COLOR_BGR2RGB)
		undistorted_image_names[cam_index].append(image_name)
	else:
		img_undistorted = cv2.cvtColor(cv2.imread(undistorted_image_path), cv2.COLOR_BGR2RGB)

	return img_undistorted


def extract_pointcloud_with_intensity(input_path, output_path, output_format, tile_size):
	velodyne_path = os.path.join(input_path, 'velodyne_hits.bin')
	pose_path = os.path.join(input_path, 'groundtruth_' + os.path.basename(input_path) + '.csv')

	timestamps, poses = extract_poses(pose_path)
	min_timestamp = np.min(timestamps)
	max_timestamp = np.max(timestamps)

	tile_writer = TileWriter(output_path,
						  pointcloud_format=FORMAT_XYZI,
						  file_format=output_format,
						  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
						  tile_size=tile_size,
						  padding=2)
	
	f_bin = open(velodyne_path, 'rb')
	progress_bar = tqdm()
	while True:
		start_marker = f_bin.read(8)
		if start_marker == b'' or len(start_marker) < 8: # eof
			break
		
		if not verify_start_marker(start_marker):
			print('Could not verify start marker')

		# read points from binary
		num_hits, timestamp = struct.unpack('<IQxxxx', f_bin.read(16))   # the third entry is just padding
		bytes_to_read = num_hits * point_size_binary
		chunk_format = '<' + point_format * num_hits
		bytes = struct.unpack(chunk_format, f_bin.read(bytes_to_read))
		pointcloud = np.array(bytes).reshape((num_hits,5))

		if timestamp < min_timestamp or timestamp > max_timestamp:    # we ignore all scans for which we have no gt pose
			continue

		# transform points to world space
		pose_matrix = get_pose_matrix(timestamps, poses, timestamp) @ T_lidar_to_body # these scans are still in the lidar frame
		xyz = pointcloud[:, :3] * 0.005 - 100.0
		xyz = pose_matrix @ np.column_stack([xyz, np.ones(num_hits)]).T
		tile_writer.add_points(np.column_stack([xyz[:3].T, pointcloud[:, 3]])) # the 4th column contains the intensity

		progress_bar.update()
	tile_writer.close()

# requires the velodyne_sync and lb3 folders, as well as the camera parameter
def extract_pointcloud_with_colors(input_path, output_path, output_format, tile_size):
	velodyne_path = os.path.join(input_path, 'velodyne_sync')
	pose_path = os.path.join(input_path, 'groundtruth_' + os.path.basename(input_path) + '.csv')

	timestamps, poses = extract_poses(pose_path)
	min_timestamp = np.min(timestamps)
	max_timestamp = np.max(timestamps)

	tile_writer = TileWriter(output_path,
						  pointcloud_format=FORMAT_XYZRGB,
						  file_format=output_format,
						  bbox=np.array([np.min(poses[:, :2], axis=0), np.max(poses[:, :2], axis=0)]), 
						  tile_size=tile_size,
						  padding=2)

	# Prepare folders for color images
	images_path = os.path.join(input_path, 'lb3')
	undistorted_images_path = os.path.join(input_path, 'lb3_undistorted')
	retrieve_undistorted_image_names(undistorted_images_path)

	for scan in tqdm(list(os.scandir(velodyne_path))):
		timestamp = int(scan.name.split('.')[0])
		if timestamp < min_timestamp or timestamp > max_timestamp:    # we ignore all scans for which we have no gt pose
			continue

		# read data from binary file
		with open(scan.path, 'rb') as f_bin:
			data = f_bin.read()
		num_hits = int(len(data) / point_size_binary)
		chunk_format = '<' + point_format * num_hits
		bytes = struct.unpack(chunk_format, data)
		pointcloud = np.array(bytes).reshape((num_hits,5))

		# transform points to world space
		pose_matrix = get_pose_matrix(timestamps, poses, timestamp) # these scans are already in the body frame
		xyz = pointcloud[:, :3] * 0.005 - 100.0
		xyz = np.column_stack([xyz, np.ones(num_hits)])
		positions = pose_matrix @ xyz.T

		# load images and project to pointcloud
		colors = np.zeros((xyz.shape[0], 3))
		mask = np.zeros((xyz.shape[0])).astype(bool)
		for cam_index in range(6):
			image_name = str(timestamp) + '.tiff'
			image_path = os.path.join(images_path, 'Cam' + str(cam_index), image_name)
			undistorted_image_path = os.path.join(undistorted_images_path, 'Cam' + str(cam_index), image_name)

			img_undistorted = get_undistorted_image(image_path, undistorted_image_path, cam_index)
			if img_undistorted is None:
				continue

			points_im, cam_mask = project_points_to_image(xyz, T_body_to_cam[cam_index], cam_projection[cam_index], [0, 0, im_width, im_height])
			colors[np.where(cam_mask)] = img_undistorted[np.round(points_im[:,1]).astype(int), np.round(points_im[:,0]).astype(int)]
			mask |= cam_mask

		# construct final, colored point cloud
		mask &= (colors != 0).any(axis=1)  # discard points at black pixels
		colors = colors[np.where(mask)]
		pointcloud = np.hstack((positions[:3].T[np.where(mask)], colors))

		if len(pointcloud) > 0:
			tile_writer.add_points(pointcloud)

	tile_writer.close()


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list, project_images, tile_size):
	if not os.path.exists(input_path):
		return

	# get list of rosbags to process
	processing_order = get_processing_order(os.path.join(input_path, 'raw'), inclusion_list, exclusion_list)

	if project_images:
		load_camera_matrices(os.path.join(input_path, 'cam_params'))

	# create output folders and extract point clouds
	for entry in tqdm(processing_order):
		if output_folder is None:
			output_path = os.path.join(input_path, 'pointclouds', entry.name)
		else:
			output_path = os.path.join(output_folder, entry.name)
		os.makedirs(output_path, exist_ok=True)

		if project_images:
			extract_pointcloud_with_colors(entry, output_path, output_format, tile_size)
		else:
			extract_pointcloud_with_intensity(entry, output_path, output_format, tile_size)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
					 args.output_folder, 
					 args.output_format,
					 args.exclusion_list,
					 args.inclusion_list,
					 args.project_images,
					 args.tile_size)