# The NCLT Dataset

<img src=./../../images/NCLT.png width="400"/>

[Original Dataset Website](https://robots.engin.umich.edu/nclt/index.html) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/NCLT)


## Notes
  - According to Schaefer et al. ("Long-Term Urban Vehicle Localization Using Pole Landmarks Extracted from 3-D Lidar Scans", 2019), the provided ground truth poses are not very accurate. We confirmed that a better alignment can be achieved by employing current SLAM solutions (e.g., [FasterLIO](https://github.com/gaoxiang12/faster-lio)).
  - Mapping the color images to the point cloud often results in the tip of trees receiving the color of the sky.


## Scripts
* `create_pointclouds.py` extracts the local point cloud batches from the `velodyne_hits.bin` file and uses the given poses to transform them into a global coordinate system. If, however, the `--project_images` argument is passed, the local point clouds in the `velodyne_sync` folder are used instead and combined with the color images in the `lb3` folder and given poses to create a unified, colored point cloud.
* `create_2d_renderings.py` renders the point clouds resulting from the `create_pointclouds.py` script to the ground plane. As each tile is rendered separately, the color mapping is only valid within a tile, leading to visible tile borders. However, in our case, we used these renderings only for assessing the area coverage of a pointcloud.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.

The expected folder structure for the data is as follows:
```
NCLT
  |-- raw
      |-- 2012-01-08
          |-- velodyne_sync
              |-- 1338074715117444.bin
              |-- 1338074715317433.bin
              |-- ...
          |-- lb3
              |-- Cam0
                  |-- 1338074715917481.tiff
                  |-- 1338074716117502.tiff
                  |-- ...
              |-- Cam1
              |-- ...
          |-- lb3_undistorted       # This gets created by the create_pointclouds.py script
              |-- Cam0
                  |-- 1338074715917481.tiff
                  |-- 1338074716117502.tiff
                  |-- ...
              |-- Cam1
              |-- ...
          |-- groundtruth_2012-01-08.csv
          |-- velodyne_hits.bin
          |-- ...
      |-- 2012-01-15
      |-- 2012-01-22
      |-- ...
  |-- cam_params
      |-- K_cam0.csv
      |-- K_cam1.csv
      |-- ...
      |-- U2D_Cam0_1616X1232.txt
      |-- U2D_Cam1_1616X1232.txt
      |-- ...
      |-- x_lb3_c0.csv
      |-- x_lb3_c1.csv
      |-- ...
  |-- pointclouds        # This gets created by the create_pointclouds.py script
      |-- 2012-01-08
          |-- tile_0_1.laz
          |-- tile_0_2.laz
          |-- tile_0_3.laz
          |-- ...
      |-- 2012-01-15
      |-- 2012-01-22
      |-- ...
```