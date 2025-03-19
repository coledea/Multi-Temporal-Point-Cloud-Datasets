import numpy as np
import laspy
import plyfile
import os
from pypcd4 import PointCloud as PCDPointCloud
from enum import Enum
import utils.pointcloud_format as pf

class FileFormat(str, Enum):
    LAS = 'LAS'
    LAZ = 'LAZ'
    PLY = 'PLY'
    TXT = 'TXT'


def write_ply(pointcloud, path, pointcloud_format):
    new_pointcloud = np.array(list(map(tuple, pointcloud)), dtype=pointcloud_format.ply_output_dtypes)
    el = plyfile.PlyElement.describe(new_pointcloud, 'vertex')
    plyfile.PlyData([el]).write(path)

# ignores offset for avoiding precision errors during later computations
def read_las_in_local_crs(path):
    pointcloud = laspy.read(path)
    scales = pointcloud.header.scales
    pointcloud = np.column_stack((pointcloud.X * scales[0], pointcloud.Y * scales[1], pointcloud.Z * scales[2]))
    return pointcloud

def read_las_with_changes(path):
    pointcloud = laspy.read(path)
    pointcloud = np.column_stack((pointcloud.x, pointcloud.y, pointcloud.z, pointcloud.change))
    return pointcloud


def las_points_from_pointcloud(pointcloud, pointcloud_format, las_header):
    las_points = laspy.LasData(las_header)
    for idx, field in enumerate(pointcloud_format.fields):
        if (field is pf.X) or (field is pf.Y) or (field is pf.Z):
            las_points[field.name] = pointcloud[:, idx].astype(field.dtype) / las_header.scales[0]
        else:
            las_points[field.name] = pointcloud[:, idx].astype(field.dtype)
    return las_points

def get_las_header(pointcloud_format, offsets=np.array([0, 0, 0]), precision=1000000):
    las_header = laspy.LasHeader(version='1.4', point_format=2)
    las_header.offsets = offsets
    las_header.scales = 1.0 / np.array([precision, precision, precision])

    if pf.SEMANTIC in pointcloud_format.fields:
        las_header.add_extra_dim(laspy.ExtraBytesParams(name='semantic', type=np.uint8))
    
    if pf.INSTANCE in pointcloud_format.fields:
        las_header.add_extra_dim(laspy.ExtraBytesParams(name='instance', type=np.uint16))

    if pf.CHANGE in pointcloud_format.fields:
        las_header.add_extra_dim(laspy.ExtraBytesParams(name='change', type=np.uint8))

    return las_header


def write_las(pointcloud, path, pointcloud_format, offsets = np.array([0, 0, 0]), precision=1000000):
    las_header = get_las_header(pointcloud_format, offsets, precision)
    las_points = las_points_from_pointcloud(pointcloud, pointcloud_format, las_header)
    with laspy.open(path, mode='w', header=las_header) as outfile:
        outfile.write_points(las_points.points)

# Reads the point positions. For .txt files assumes the format as written out by write_pointcloud().
# For other formats (e.g., other delimiters, headers, column orders etc.) use np.genfromtxt()
# The position_offset gets applied to all data read from file formats other than LAS/LAZ (where we just ignore the global offset). It can be used to avoid coordinate precision errors.
def read_pointcloud_xyz(filepath, position_offset=np.array([0,0,0]), txt_has_header=False, txt_delimiter=None, remove_duplicates=False):
    if not os.path.isfile(filepath):
        print(filepath, ' does not exist!')
        exit()

    if filepath.endswith('.las') or filepath.endswith('.laz'):
        pointcloud = read_las_in_local_crs(filepath)
    elif filepath.endswith('.ply'):
        pointcloud = plyfile.PlyData.read(filepath)
        pointcloud = np.vstack([pointcloud['vertex']['x'], pointcloud['vertex']['y'], pointcloud['vertex']['z']]).transpose() + position_offset
    elif filepath.endswith('.pcd'):
        pointcloud = PCDPointCloud.from_path(filepath).numpy()[:, 0:3] + position_offset
    elif filepath.endswith('.txt') or filepath.endswith('.xyz'):
        pointcloud = np.loadtxt(filepath, skiprows=(1 if txt_has_header else 0), delimiter=txt_delimiter)[:, 0:3] + position_offset

    pointcloud = pointcloud[~np.isnan(pointcloud).any(axis=1)]  # remove rows with NaN values

    if remove_duplicates:
        pointcloud = np.unique(pointcloud, axis=0)

    return pointcloud


def write_pointcloud(pointcloud, folder, filename, file_format, pointcloud_format, las_offsets=np.array([0, 0, 0]), las_precision=1000000):
    if len(pointcloud) == 0:
        print('Pointcloud', filename, 'is empty')
        return
    
    if file_format == FileFormat.LAS:
        write_las(pointcloud, os.path.join(folder, filename + '.las'), pointcloud_format, offsets=las_offsets, precision=las_precision)
    elif file_format == FileFormat.LAZ:
        write_las(pointcloud, os.path.join(folder, filename + '.laz'), pointcloud_format, offsets=las_offsets, precision=las_precision)
    elif file_format == FileFormat.PLY:
        write_ply(pointcloud, os.path.join(folder, filename + '.ply'), pointcloud_format)
    elif file_format == FileFormat.TXT:
        output_path = os.path.join(folder, filename + '.txt')
        np.savetxt(output_path, 
                   pointcloud, 
                   header=pointcloud_format.txt_output_header, 
                   fmt=pointcloud_format.txt_output_dtypes)