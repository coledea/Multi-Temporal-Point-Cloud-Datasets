import laspy
import numpy as np
import os
from utils.io import FileFormat, las_points_from_pointcloud, get_las_header

class SingleTileWriter:
    def __init__(self, output_path, las_header, write_threshold, pointcloud_format):
        self.las_header = las_header
        self.pointcloud_format = pointcloud_format
        self.output_path = output_path
        self.las_writer = laspy.open(output_path, mode='w', header=las_header)
        
        self.write_threshold = write_threshold
        self.data = np.empty((write_threshold, len(pointcloud_format.fields)), dtype=np.float32)
        self.current_index = 0
        self.points_written = 0

    def add_points(self, points):
        num_points = len(points)
        if self.current_index + num_points > self.write_threshold:
            self.flush()
        self.data[self.current_index:self.current_index + num_points] = points
        self.current_index += num_points

    def flush(self):
        if self.current_index == 0:
            return

        las_points = las_points_from_pointcloud(self.data[:self.current_index], 
                                                self.pointcloud_format,
                                                self.las_header)
        self.las_writer.write_points(las_points.points)
        self.points_written += self.current_index
        self.current_index = 0

    def close(self):
        if self.current_index > 0:
            self.flush()
        self.las_writer.close()
        if self.points_written == 0:
            os.remove(self.output_path)


class TileWriter:
    # The tiles can be created from two different specifications: 
    # - bbox + tile_size   -> derive num_tiles
    # - bbox + num_tiles   -> derive tile_size
    # If both are available, the tile_size is used to derive the num_tiles
    # bbox should be a matrix of shape (2,2), with the first row being the minimum, and the second the maximum on the ground plane (xy)
    # The tiles are open to the borders, i.e., points falling outside the borders of a tile are added to the nearest tile
    def __init__(self, 
                 output_folder,
                 pointcloud_format,
                 file_format = FileFormat.LAZ,
                 bbox=np.array([[0,0], [1,1]]), 
                 tile_size=None, 
                 num_tiles=np.array([1,1]), 
                 padding=0, 
                 write_threshold=4000000):
        self.las_header = get_las_header(pointcloud_format)
        self.bbox = bbox

        bbox_extent = bbox[1] - bbox[0]
        if tile_size is not None:
            self.tile_size = tile_size
            self.num_tiles = np.ceil(bbox_extent / tile_size).astype(int)
        else:
            self.num_tiles = num_tiles
            self.tile_size = bbox_extent / num_tiles.astype(float)
        if padding != 0:
            self.num_tiles += padding * 2
            self.bbox[0] -= tile_size * padding
            self.bbox[1] += tile_size * padding

        self.writers = []
        for x in range(self.num_tiles[0]):
            self.writers.append([])
            for y in range(self.num_tiles[1]):
                tile_path = os.path.join(output_folder, 
                                         ''.join(['tile_', str(x), '_',  
                                         str(y), 
                                         '.laz' if file_format == FileFormat.LAZ else '.las']))
                self.writers[x].append(SingleTileWriter(tile_path, 
                                                        self.las_header, 
                                                        write_threshold=write_threshold, 
                                                        pointcloud_format=pointcloud_format))

    
    def add_points(self, points):
        # sort points into tiles
        tile_idx = ((points[:,:2] - self.bbox[0]) / self.tile_size).astype(int)
        tile_idx[:,0] = np.clip(tile_idx[:,0], a_min=0, a_max=self.num_tiles[0]-1)
        tile_idx[:,1] = np.clip(tile_idx[:,1], a_min=0, a_max=self.num_tiles[1]-1)
        u, i, counts = np.unique(tile_idx, return_inverse=True, return_counts=True, axis=0)
        points_sorted = points[np.argsort(i)]
        tiled_points = np.split(points_sorted, np.cumsum(counts)[:-1])

        for idx, tile in enumerate(tiled_points):
            tile = tile[~np.isnan(tile).any(axis=1)]
            tile_x = u[idx][0]
            tile_y = u[idx][1]
            self.writers[tile_x][tile_y].add_points(tile)

    def close(self):
        for x in range(self.num_tiles[0]):
            for y in range(self.num_tiles[1]):
                self.writers[x][y].close()