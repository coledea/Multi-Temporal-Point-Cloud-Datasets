from scipy.spatial import cKDTree
import numpy as np
from shapely.geometry import MultiPoint
from shapely import union_all
from .pointcloud_processing import reduce_and_remove_outliers
from tqdm import tqdm
from .io import read_pointcloud_xyz, read_las_with_changes, read_las_in_local_crs
from enum import Enum
import os

class Statistics(Enum):
    NUM_POINTS = 'Number of points'
    AVG_DISTANCE = 'Average neighbor distance'
    PARTIAL_EPOCHS = 'Partial epochs'
    CHANGE_POINTS = 'Change ratio'


def avg_neighbor_distance(pointcloud):
    kdtree = cKDTree(pointcloud)
    distances, _ = kdtree.query(pointcloud, k=[2], workers=-1)
    return np.mean(distances)

def write_to_log(filepath, message):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as logfile:
        logfile.write(message)

def statistics_num_points_string(data):
    string = Statistics.NUM_POINTS.value + ':\n'
    string += 'Min: ' + str(np.min(data)) + '\n'
    string += 'Median: ' + str(np.median(data)) + '\n'
    string += 'Max: ' + str(np.max(data)) + '\n'
    string += '============================\n'
    return string

def statistics_avg_distance_string(data):
    string = Statistics.AVG_DISTANCE.value + ':\n'
    string += 'Min: ' + str(np.min(data)) + '\n'
    string += 'Median: ' + str(np.median(data)) + '\n'
    string += 'Max: ' + str(np.max(data)) + '\n'
    string += '============================\n'
    return string

def statistics_partial_epochs_string(overlap_data, threshold):
    num_partial_epochs = len(overlap_data[overlap_data < threshold])
    string = Statistics.PARTIAL_EPOCHS.value + ':\n'
    string += 'Number of partial epochs: ' + str(num_partial_epochs) + '\n'
    if len(overlap_data) > 0:
        string += 'Share of partial epochs: ' + str(num_partial_epochs / len(overlap_data)) + '\n'
    else:
        string += 'Share of partial epochs: 0\n'
    string += '============================\n'
    return string

def statistics_change_points_string(change_data):
    string = Statistics.CHANGE_POINTS.value + ':\n'
    string += 'Share of change points: ' + str(np.average(change_data)) + '\n'
    string += '============================\n'
    return string

def print_dataset_statistics(statistics_data, statistics_specifiers, file_path=None):
    statistics_string = ''
    for idx, statistic in enumerate(statistics_specifiers):
        if len(statistics_data[idx]) == 0:
            continue
        if statistic == Statistics.NUM_POINTS:
            statistics_string += statistics_num_points_string(statistics_data[idx])
        elif statistic == Statistics.AVG_DISTANCE:
            statistics_string += statistics_avg_distance_string(statistics_data[idx])
        elif statistic == Statistics.PARTIAL_EPOCHS:
            statistics_string += statistics_partial_epochs_string(statistics_data[idx], threshold=0.75)
        elif statistic == Statistics.CHANGE_POINTS:
            statistics_string += statistics_change_points_string(statistics_data[idx])
    print(statistics_string)

    if file_path:
        write_to_log(file_path, statistics_string)

# Computes the statistics per tile and merges the results for the whole pointcloud
# we assume LAS/LAZ files for tiled point clouds
def compute_epoch_statistics_tiled(tiles, statistics_to_compute, remove_duplicates=False, first_epoch_polygon=None):
    statistics = {}
    overall_num_points = 0
    points_per_tile = []
    distance_per_tile = []
    polygons = []
    for tile in tqdm(tiles, leave=False):
        pointcloud = read_pointcloud_xyz(tile, remove_duplicates=remove_duplicates)

        num_points = len(pointcloud)
        if num_points < 2:
            continue

        overall_num_points += num_points
        points_per_tile.append(num_points)

        if Statistics.AVG_DISTANCE in statistics_to_compute:
            avg_distance = avg_neighbor_distance(pointcloud)
            distance_per_tile.append(avg_distance)

        if Statistics.PARTIAL_EPOCHS in statistics_to_compute:
            pointcloud_reduced = reduce_and_remove_outliers(pointcloud, down_sample_factor=0.1, outlier_removal_neighbors=20, outlier_removal_std_ratio=1.0)
            polygons.append(MultiPoint(pointcloud_reduced[:,0:2]).convex_hull)

    if Statistics.AVG_DISTANCE in statistics_to_compute:
        overall_avg_distance = 0
        for tile_idx in range(len(distance_per_tile)):
            overall_avg_distance += distance_per_tile[tile_idx] * (points_per_tile[tile_idx] / overall_num_points)
        statistics[Statistics.AVG_DISTANCE] = overall_avg_distance

    if Statistics.NUM_POINTS in statistics_to_compute:
        statistics[Statistics.NUM_POINTS] = overall_num_points

    if Statistics.PARTIAL_EPOCHS in statistics_to_compute:
        if first_epoch_polygon is None:
            first_epoch_polygon = union_all([polygons])
        else:
            second_epoch_polygon = union_all([polygons])
            intersection_area = first_epoch_polygon.intersection(second_epoch_polygon).area
            statistics[Statistics.PARTIAL_EPOCHS].append(intersection_area / first_epoch_polygon.area)

    return statistics, first_epoch_polygon

# The processing_order is a list of scenes, which is a list of epochs. Each epoch is a list of filepaths to the point cloud parts that make up this epoch (in most cases just one).
# If an overlap evaluation should be executed, the first epoch in each scene list should be the reference epoch
# The computation of the percentage of change points per epoch is not executed by this function, as the approaches differ significantly between the datasets.
# For textfiles, this function assumes the format as written by io.write_pointcloud
# The position_offset can be used to shift a point cloud in order to avoid precision errors due to high coordinate values.
# The rotation_before_projection (a scipy.spatial.transform.Rotation object) can be used if the point clouds are not axis-aligned, i.e., if they have to be rotated before the convex hull in the xy-plane can be computed
# TODO: configuration object?
def compute_dataset_statistics(processing_order, statistics_to_compute, output_log_path=None, leave_progress_bar=False, position_offset=[0, 0, 0], txt_has_header=False, txt_delimiter=None, remove_duplicates=False, rotation_before_projection=None, tiled_epochs=False):
    statistics = {}
    for statistic in statistics_to_compute:
        statistics[statistic] = []

    for scene in tqdm(processing_order, leave=leave_progress_bar):
        first_epoch_polygon = None

        for epoch in tqdm(scene, leave=False):
            if len(epoch) == 1:
                pointcloud = read_pointcloud_xyz(epoch[0], txt_has_header=txt_has_header, txt_delimiter=txt_delimiter, position_offset=np.asarray(position_offset), remove_duplicates=remove_duplicates)
            elif tiled_epochs:           # epoch consists of multiple non-overlapping tiles that are too large to merge
                result, polygon = compute_epoch_statistics_tiled(epoch, statistics_to_compute, remove_duplicates=remove_duplicates, first_epoch_polygon=first_epoch_polygon)
                first_epoch_polygon = polygon
                for key in result:
                    statistics[key].append(result[key])
                continue
            else:                       # epoch consists of multiple parts that can be merged
                pointcloud_parts = []
                for epoch_part in epoch:
                    pointcloud = read_pointcloud_xyz(epoch_part, txt_has_header=txt_has_header, txt_delimiter=txt_delimiter, position_offset=np.asarray(position_offset))
                    pointcloud_parts.append(pointcloud)
                pointcloud = np.concatenate(pointcloud_parts)

            if len(pointcloud) < 2:
                continue

            if Statistics.NUM_POINTS in statistics_to_compute:
                statistics[Statistics.NUM_POINTS].append(len(pointcloud))

            if Statistics.AVG_DISTANCE in statistics_to_compute:
                statistics[Statistics.AVG_DISTANCE].append(avg_neighbor_distance(pointcloud))

            if Statistics.PARTIAL_EPOCHS in statistics_to_compute:
                pointcloud_reduced = reduce_and_remove_outliers(pointcloud, down_sample_factor=0.1, outlier_removal_neighbors=20, outlier_removal_std_ratio=1.0)
                if rotation_before_projection is not None:
                    rotation_before_projection.apply(pointcloud_reduced)
                if first_epoch_polygon is None:
                    first_epoch_polygon = MultiPoint(pointcloud_reduced[:,0:2]).convex_hull
                else:
                    second_epoch_polygon = MultiPoint(pointcloud_reduced[:,0:2]).convex_hull
                    intersection_area = first_epoch_polygon.intersection(second_epoch_polygon).area
                    statistics[Statistics.PARTIAL_EPOCHS].append(intersection_area / first_epoch_polygon.area)

    statistics = [np.array(entry) for entry in statistics.values()]
    print_dataset_statistics(statistics, statistics_to_compute, output_log_path)


# This is basically the same as compute_dataset_statistics, with the difference, that un-tiled LAS/LAZ files
# are assumed as input. It is further assumed that a potential change label (with values > 0 denoting changes) is stored in the user_data
# if changes_in_all_epochs is False, the first epoch is ignored for computing change points (this is the default)
def compute_dataset_statistics_las(processing_order, statistics_to_compute, output_log_path=None, leave_progress_bar=False, changes_in_all_epochs=False):
    statistics = {}
    for statistic in statistics_to_compute:
        statistics[statistic] = []

    for scene in tqdm(processing_order, leave=leave_progress_bar):
        first_epoch_polygon = None

        for idx, epoch in tqdm(list(enumerate(scene)), leave=False):
            if (idx == 0) and (not changes_in_all_epochs):
                pointcloud = read_las_in_local_crs(epoch[0])
            else:
                pointcloud = read_las_with_changes(epoch[0])

            if len(pointcloud) < 2:
                continue

            if Statistics.NUM_POINTS in statistics_to_compute:
                statistics[Statistics.NUM_POINTS].append(len(pointcloud))

            if Statistics.AVG_DISTANCE in statistics_to_compute:
                statistics[Statistics.AVG_DISTANCE].append(avg_neighbor_distance(pointcloud[:,0:3]))

            if Statistics.PARTIAL_EPOCHS in statistics_to_compute:
                pointcloud_reduced = reduce_and_remove_outliers(pointcloud[:,0:3], down_sample_factor=0.1, outlier_removal_neighbors=20, outlier_removal_std_ratio=1.0)
                if first_epoch_polygon is None:
                    first_epoch_polygon = MultiPoint(pointcloud_reduced[:,0:2]).convex_hull
                else:
                    second_epoch_polygon = MultiPoint(pointcloud_reduced[:,0:2]).convex_hull
                    intersection_area = first_epoch_polygon.intersection(second_epoch_polygon).area
                    statistics[Statistics.PARTIAL_EPOCHS].append(intersection_area / first_epoch_polygon.area)

            if Statistics.CHANGE_POINTS in statistics_to_compute and (idx > 0 or changes_in_all_epochs):
                change_ratio = np.count_nonzero(pointcloud[:,3]) / len(pointcloud)
                statistics[Statistics.CHANGE_POINTS].append(change_ratio)
    
    statistics = [np.array(entry) for entry in statistics.values()]
    print_dataset_statistics(statistics, statistics_to_compute, output_log_path)