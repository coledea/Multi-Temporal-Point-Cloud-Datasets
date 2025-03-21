from dataclasses import dataclass, field
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
import numpy as np
from shapely.geometry import MultiPoint
from shapely import union_all
from .pointcloud_processing import reduce_and_remove_outliers
from tqdm import tqdm
from .io import read_pointcloud_for_evaluation, read_and_merge_pointclouds_for_evaluation
from enum import Enum
import os

class Statistics(Enum):
    NUM_POINTS = 'Number of points'
    AVG_DISTANCE = 'Average neighbor distance'
    PARTIAL_EPOCHS = 'Partial epochs'
    CHANGE_POINTS = 'Change ratio'


# The position_offset can be used to shift a point cloud in order to avoid precision errors due to high coordinate values.
# The rotation_before_projection (a scipy.spatial.transform.Rotation object) can be used if the point clouds are not axis-aligned, i.e., if they have to be rotated before the convex hull in the xy-plane can be computed
@dataclass
class EvaluationConfig:
    statistics_to_compute: list = None
    output_log_path: str = None
    tiled_epochs: bool = False
    leave_progress_bar: bool = False
    position_offset: list = field(default_factory=lambda:[0, 0, 0])
    txt_has_header: bool = False
    txt_delimiter: str = None
    remove_duplicates: bool = False
    rotation_before_projection: Rotation = None



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

def print_dataset_statistics(statistics, file_path=None):
    statistics_string = ''
    for key in statistics:
        if len(statistics[key]) == 0:
            continue
        if key == Statistics.NUM_POINTS:
            statistics_string += statistics_num_points_string(statistics[key])
        elif key == Statistics.AVG_DISTANCE:
            statistics_string += statistics_avg_distance_string(statistics[key])
        elif key == Statistics.PARTIAL_EPOCHS:
            statistics_string += statistics_partial_epochs_string(statistics[key], threshold=0.75)
        elif key == Statistics.CHANGE_POINTS:
            statistics_string += statistics_change_points_string(statistics[key])
    print(statistics_string)

    if file_path:
        write_to_log(file_path, statistics_string)

# Utility class for approximating the overlap of point clouds with a reference point cloud
class OverlapApproximator:
    def __init__(self, rotation_before_projection=None, down_sample_factor=0.1, outlier_removal_neighbors=20, outlier_removal_std_ratio=1.0):
        self.reference_epoch_polygon = None
        self.polygons = []
        self.down_sample_factor = down_sample_factor
        self.outlier_removal_neighbors = outlier_removal_neighbors
        self.outlier_removal_std_ratio = outlier_removal_std_ratio
        self.rotation_before_projection = rotation_before_projection
    
    # add tile to the current epoch
    def add_tile(self, pointcloud):
        pointcloud_reduced = reduce_and_remove_outliers(pointcloud, self.down_sample_factor, self.outlier_removal_neighbors, self.outlier_removal_std_ratio)
        if self.rotation_before_projection is not None:
            self.rotation_before_projection.apply(pointcloud_reduced)
        self.polygons.append(MultiPoint(pointcloud_reduced[:,0:2]).convex_hull)
        
    # compute overlap of the current epoch to the reference epoch and reset
    def compute_overlap(self):
        if self.reference_epoch_polygon is None:
            self.reference_epoch_polygon = union_all([self.polygons])
            self.polygons = []
            return None
        else:
            intersection_area = self.reference_epoch_polygon.intersection(union_all([self.polygons])).area
            self.polygons = []
            return intersection_area / self.reference_epoch_polygon.area

# Computes the specified statistics for the given epoch and appends them to the statistics dictionary
def compute_statistics_for_epoch(tiles, statistics, config, overlap_approximator, merge_tiles=False):
    overall_num_points = 0
    points_per_tile = []
    distance_per_tile = []
    change_ratios = []

    # compute values per tile
    for tile in tqdm(tiles, leave=False):
        if merge_tiles:
            pointcloud = read_and_merge_pointclouds_for_evaluation(tiles, txt_has_header=config.txt_has_header, txt_delimiter=config.txt_delimiter, position_offset=config.position_offset, remove_duplicates=config.remove_duplicates)
        else:
            pointcloud = read_pointcloud_for_evaluation(tile, txt_has_header=config.txt_has_header, txt_delimiter=config.txt_delimiter, position_offset=config.position_offset, remove_duplicates=config.remove_duplicates)

        num_points = len(pointcloud)
        if num_points < 2:
            continue

        overall_num_points += num_points
        points_per_tile.append(num_points)

        if Statistics.AVG_DISTANCE in statistics:
            avg_distance = avg_neighbor_distance(pointcloud)
            distance_per_tile.append(avg_distance)

        if Statistics.PARTIAL_EPOCHS in statistics:
            overlap_approximator.add_tile(pointcloud[:, 0:3])
        
        if Statistics.CHANGE_POINTS in statistics and pointcloud.shape[1] > 3:
            change_ratio = np.count_nonzero(pointcloud[:,3]) / len(pointcloud)
            change_ratios.append(change_ratio)

        if merge_tiles:
            break

    # merge per-tile values into per-epoch values
    if Statistics.AVG_DISTANCE in statistics:
        if len(distance_per_tile) > 1:
            overall_avg_distance = 0
            for tile_idx in range(len(distance_per_tile)):
                overall_avg_distance += distance_per_tile[tile_idx] * (points_per_tile[tile_idx] / overall_num_points)
            statistics[Statistics.AVG_DISTANCE].append(overall_avg_distance)
        else:
            statistics[Statistics.AVG_DISTANCE].append(distance_per_tile[0])

    if Statistics.NUM_POINTS in statistics:
        statistics[Statistics.NUM_POINTS].append(overall_num_points)

    if Statistics.PARTIAL_EPOCHS in statistics:
        overlap = overlap_approximator.compute_overlap()
        if overlap is not None:
            statistics[Statistics.PARTIAL_EPOCHS].append(overlap)

    if Statistics.CHANGE_POINTS:
        if len(change_ratios) > 0:
            statistics[Statistics.CHANGE_POINTS].append(np.average(change_ratios))


# This function has several assumptions:
# - The processing_order is a list of scenes, which is a list of epochs. Each epoch is a list of filepaths to the point cloud parts that make up this epoch (in most cases just one).
# - If an overlap evaluation should be executed, the first epoch in each scene list is assumed to be the reference epoch
# - The computation of the percentage of change points per epoch is only executed for LAS/LAZ files, if they contain an extra dimension named "change" (with values > 0 denoting changes). 
#   For other cases, the change ratio has to be computed separately, as the approaches differ significantly.
# - For textfiles, this function assumes the format as written by io.write_pointcloud
def compute_dataset_statistics(processing_order, config : EvaluationConfig):
    statistics = {}
    for statistic in config.statistics_to_compute:
        statistics[statistic] = []

    for scene in tqdm(processing_order, leave=config.leave_progress_bar):
        overlap_approximator = OverlapApproximator(config.rotation_before_projection)
        for epoch in tqdm(scene, leave=False):
            compute_statistics_for_epoch(epoch, statistics, config, overlap_approximator, merge_tiles=(len(epoch) > 1 and not config.tiled_epochs))

    for key in statistics:
        statistics[key] = np.array(statistics[key])
    print_dataset_statistics(statistics, config.output_log_path)