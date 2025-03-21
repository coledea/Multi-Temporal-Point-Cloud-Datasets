import numpy as np
import open3d as o3d
from scipy.spatial.transform import Rotation as R

# Downsamples a point cloud and removes statistical outliers
def reduce_and_remove_outliers(pointcloud, down_sample_factor=0.1, outlier_removal_neighbors=20, outlier_removal_std_ratio=1.0):
	pointcloud_o3d = o3d.geometry.PointCloud()
	pointcloud_o3d.points = o3d.utility.Vector3dVector(pointcloud)

	pointcloud_o3d = pointcloud_o3d.random_down_sample(down_sample_factor)
	cl,ind = pointcloud_o3d.remove_statistical_outlier(nb_neighbors=20, std_ratio=1.0)
	inlier = pointcloud_o3d.select_by_index(ind)

	return np.asarray(inlier.points)


# Returns a rotation for aligning a vector with the z-axis. 
# Useful for transforming the ground plane of a point cloud that is not axis-aligned into the xy-plane
def rotation_for_alignment_with_z(vector):
	vector /= np.linalg.norm(vector)
	rotation, _ = R.align_vectors([vector], [np.array([0, 0, 1])])
	return rotation

# Removes duplicates from pointclouds w.r.t. coordinates. Note that the order of points might change.
def remove_duplicates(pointcloud):
	_, indices = np.unique(pointcloud[:, 0:3], axis=0, return_index=True)
	return pointcloud[indices]