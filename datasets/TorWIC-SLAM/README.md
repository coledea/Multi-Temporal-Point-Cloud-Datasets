# The TorWIC-SLAM Dataset

<img src="./../../images/TorWIC-SLAM.png" width="400"/>

[Original Dataset Website](https://github.com/Viky397/TorWICDataset) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/TorWIC-SLAM)

## Notes
  - The provided results of image-based semantic segmentation are not very precise.


## Scripts
* `create_pointclouds.py` uses the lidar data and color images together with the given poses to create colored pointclouds.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the number of partial epochs.

The expected folder structure for the data is as follows:

```
TorWIC-SLAM
  |-- raw
      |-- jun_15_2022
          |-- Aisle_CCW_Run_1
              |-- depth_left
                  |-- 000000.png
                  |-- 000001.png
                  |-- ...
              |-- depth_right
                  |-- 000000.png
                  |-- 000001.png
                  |-- ...
              |-- image_left
                  |-- 000000.png
                  |-- 000001.png
                  |-- ...
              |-- image_right
                  |-- 000000.png
                  |-- 000001.png
                  |-- ...
              |-- lidar
                  |-- 000000.pcd
                  |-- 000001.pcd
                  |-- ...
              |-- traj_gt.txt
              |-- ...
          |-- Aisle_CCW_Run_2
          |-- Aisle_CW_Run_1
          |-- ...
      |-- jun_23_2022
      |-- oct_12_2022
      |-- ...
  |-- pointclouds           # This gets created by the "create_pointclouds.py" script.
      |-- Aisle
          |-- jun_15_2022_CCW_Run_1
              |-- tile_0_0.laz
              |-- tile_0_1.laz
              |-- tile_1_0.laz
              |-- tile_1_1.laz
          |-- jun_15_2022_CCW_Run_2
          |-- jun_15_2022_CW_Run_1
          |-- ...
      |-- Hallway_Full
      |-- Hallway_Straight
```