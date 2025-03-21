import numpy as np
import cv2
import math
from scipy.spatial.transform import Slerp, Rotation as R
import os
from pathlib import Path
import tifffile

# Resizes the the input_image to the size of the target_image
def match_image_size(input_image, target_image):
	if input_image.shape[0:2] != target_image.shape[0:2]:
		input_image = cv2.resize(input_image, (target_image.shape[1], target_image.shape[0]))
	return input_image

# Uses OpenCV for reading in most images, but switch to tifffile for TIFs.
# tifffile is more robust in the case of incorrectly specified metadata (e.g., channel contents) in TIF files.
def read_image(filepath):
	if filepath.endswith('.tif'):
		return tifffile.imread(filepath)
	else:
		return cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

# Combines DSM, color, and label images to obtain a point cloud
def dsm_to_pointcloud(dsm_path, color_path=None, annotation_path=None, annotation_binary_threshold=None, only_positive_dsm_values=False):
	dsm = read_image(dsm_path)
	
	# we scale everything to the resolution of the dsm
	if color_path:
		color = match_image_size(read_image(color_path), dsm)
		color = color.reshape(-1, 3)

	if annotation_path:
		annotation = match_image_size(read_image(annotation_path), dsm)
		if annotation_binary_threshold:
			_, annotation = cv2.threshold(annotation, annotation_binary_threshold, 1.0, cv2.THRESH_BINARY)

	x, y = np.meshgrid(np.arange(dsm.shape[1]), np.arange(dsm.shape[0]))
	x = x.flatten()
	y = y.flatten()
	dsm = dsm.flatten()

	mask = abs(dsm) < np.finfo(np.float32).max   # filter out invalid values
	if only_positive_dsm_values:
		mask &= (dsm > 0)

	columns = [x[mask], y[mask], dsm[mask]]
	if color_path:
		columns.extend([color[:, 0][mask], color[:, 1][mask], color[:, 2][mask]])
	if annotation_path:
		columns.append(annotation.flatten()[mask])

	pointcloud = np.stack(columns, axis=-1)
	return pointcloud

# Incrementally reconstructs a point cloud by backprojecting depth/color/label images
class RGBDReconstruction:
	# intrinsics is an array of the form: np.array([[fx, 0, Cu], [0, fy, Cv], [0, 0, 1]])
	def __init__(self, intrinsics, image_resolution, map_color_to_segmentation_id=False, depth_threshold=math.inf):
		self.intrinsics = np.linalg.inv(intrinsics)
		self.depth_threshold = depth_threshold
		self.image_resolution = image_resolution
		self.map_color_to_segmentation_id = map_color_to_segmentation_id
		self.color_to_segmentation_map = {}
		self.result = []

	# Maps the pixel colors of a segmentation image to a running index of segmentation IDs
	def __color_to_segID__(self, color):
		arr = tuple(color)
		if arr not in self.color_to_segmentation_map:
			self.color_to_segmentation_map[arr] = len(self.color_to_segmentation_map)
		return self.color_to_segmentation_map[arr]

	# if direct_result is True, the images are not accumulated, but the pointcloud for an image is directly returned
	# this is useful, if the result should be written to disk incrementally (e.g., when using the TileWriter)
	def add_image(self, depth, color, pose, segmentation=None, direct_result=False):
		x, y = np.meshgrid(np.arange(self.image_resolution[0]), np.arange(self.image_resolution[1]))
		x = x.flatten()
		y = y.flatten()

		# mask invalid depth values
		mask = np.all([depth[y,x] > 0.0, depth[y,x] < self.depth_threshold], axis=0)
		x = x[mask]
		y = y[mask]
		depths_flat = depth[y, x]

		rgb_flat = color[y, x].astype(np.uint8)
		rgb = rgb_flat[:, :3]

		# project depth image and transform to world coordinate system
		img_coords = np.stack([x, y, np.ones(x.shape[0])], axis=0).astype(float)
		local_coords = np.matmul(self.intrinsics, img_coords * depths_flat)
		global_coords = np.vstack([local_coords, np.ones((1, local_coords.shape[1]))])
		global_coords = np.matmul(pose, global_coords)
		xyz = (global_coords[:3] / global_coords[3]).transpose()

		columns = [xyz, rgb]

		if segmentation is not None:
			seg = segmentation[y, x].astype(np.uint32)
			if self.map_color_to_segmentation_id:
				seg = np.apply_along_axis(self.__color_to_segID__, axis=1, arr=seg).reshape(-1, 1)
			columns.append(seg.flatten())

		if direct_result:
			return np.column_stack(columns)
		else:
			self.result.extend(np.column_stack(columns))

	def get_result(self):
		return np.array(self.result)
	
# Interpolates between two poses using the given timestamp
def get_pose_matrix_interpolated(pose1, pose2, t1, t2, timestamp):
	alpha = (timestamp - t1) / (t2 - t1)
	position = (1 - alpha) * pose1[:3] + alpha * pose2[:3]
	slerp = Slerp([0, 1], R.from_quat([pose1[3:], pose2[3:]]))
	rotation = slerp(alpha)
	pose_matrix = np.eye(4)
	pose_matrix[:3, :3] = rotation.as_matrix()
	pose_matrix[:3, 3] = position
	return pose_matrix

# Converts a pose of the form [x, y, z, qx, qy, qz, qw] into a pose matrix
def get_pose_matrix_from_pose(pose):
	pose_matrix = np.eye(4)
	pose_matrix[:3, :3] = R.from_quat(pose[3:]).as_matrix()
	pose_matrix[:3, 3] = pose[:3]
	return pose_matrix

# Retrieves the best pose from a list of poses for the given target_timestamp
def get_pose_matrix(timestamps, poses, target_timestamp, interpolate=True):
	idx = np.searchsorted(timestamps, target_timestamp)
	# At the borders just take the nearest pose
	if idx == 0 or idx == len(timestamps) - 1 or interpolate == False:
		return get_pose_matrix_from_pose(poses[idx])
	else:
		# Retrieve the nearest poses and interpolate between them
		t1, t2 = timestamps[idx - 1], timestamps[idx]
		pose1, pose2 = poses[idx - 1], poses[idx]
		return get_pose_matrix_interpolated(pose1, pose2, t1, t2, target_timestamp)


# Projects the points using the transformation matrix T and the projection matrix proj
# roi = [x, y, w, h] denotes the region of interest. Points outside this are discarded.
# The function returns the projected points, as well as a mask denoting which points are within the ROI.
def project_points_to_image(points, T, proj, roi):
	points_cam = T @ points.T
	points_im = proj @ points_cam
	points_im[:2] /= points_im[2]
	points_im = points_im[0:3].T

	x, y, w, h = roi
	mask = (points_im[:,0] >= x) & (points_im[:,0] < x + w - 1) & (points_im[:,1] >= y) & (points_im[:,1] < y + h - 1) & (points_im[:,2] >= 0)

	return points_im[np.where(mask)], mask


# Gets Path objects for all entries in a folder, considering possible inclusion/exclusion lists
def get_processing_order(input_path, inclusion_list, exclusion_list):
	processing_order = []
	if inclusion_list is not None:
		for entry in inclusion_list:
			filepath = os.path.join(input_path, entry)
			if os.path.exists(filepath):
				processing_order.append(Path(filepath))
	else:
		for entry in os.scandir(input_path):
			if entry.name not in exclusion_list:
				processing_order.append(Path(entry.path))
	return processing_order