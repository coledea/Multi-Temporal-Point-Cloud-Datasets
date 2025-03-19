# The NTU VIRAL Dataset

<img src="./../../images/NTU VIRAL.png" width="400"/>

[Original Dataset Website](https://ntu-aris.github.io/ntu_viral_dataset) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/NTU_VIRAL)


## Notes
- The NTU Data Repository, where the data is hosted, states as license `CC BY-NC 4.0`, while the dataset's webpage states `CC BY-NC-SA 4.0`
- The ground truth contains only positions, however, the authors provide SLAM results for the full pose here: https://github.com/ntu-aris/fastlio2_sample. Care has to be taken if the ground truth positions should be combined with the estimated orientations or the IMU data, as the coordinate systems differ and the temporal alignment has also be taken care of.
- The zip archive for epoch nya_01 contains again a zip archive with the same name, which can lead to problems when trying to extract the archive into the the same directory
- The UAV itself may cause noise points in the LiDAR scans. They can be removed by discarding points all in a small box around UAV.
- Using the given poses, some point clouds contain a lot of noise points that may have to be filtered first, depending on the application

## Scripts
* `create_pointclouds.py` extracts the local point clouds from the rosbags and uses the given poses to transform them into a global coordinate system. As the ground truth contains only positions, we use the estimated poses provided by the authors.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.


```
NTU_VIRAL
  |-- rosbags
      |-- eee_01
          |-- camera_left.yaml
          |-- camera_right.yaml
          |-- eee_01.bag
          |-- lidar_horz.yaml
          |-- lidar_vert.yaml
          |-- odometry.csv       # SLAM result provided by dataset authors
          |-- ...
      |-- eee_02
      |-- eee_03
      |-- nya_01
      |-- ...
  |-- pointclouds        # This gets created by the create_pointclouds.py script
      |-- eee
          |-- epoch_1
              |-- tile_0_0.laz
              |-- tile_0_1.laz
              |-- ...
          |-- epoch_2
          |-- epoch_3
      |-- nya
      |-- ...
```