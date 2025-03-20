# The BACCHUS Long-Term (BLT) Dataset

<img src=./../../images/BLT.png width="400"/>

[Original Dataset Website](https://lncn.ac/lcas-blt) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/BLT)


## Notes
  - For the KG scene, ROS bags with synchronized sensor outputs are available alongside the raw data.
  - Poses are provided only for the KG scene, while for the Riseholme scene only odometry and IMU data is available. To reconstruct a unified point cloud from this data, a SLAM solution has to be used (we tested [FasterLIO](https://github.com/gaoxiang12/faster-lio), which worked reasonably well). However, as argued in the paper, we only used the KG scene for our computations.
  - For the KG scene, the paper and website list 11 epochs. However, the website also states that there are only 10 epochs. We found that the synchronized ROS bag for May 18th (`kg_may_18.bag`) is corrupted and reindexing it (using `rosbag reindex`) discards most of its data. Additionally, this is the only date for which raw data is not available. Therefore, there are ultimatively 10 usable epochs.
  - In the downloadable files, `june_22` is missing from the synchronized ROS bag and `kg_september_09.bag` appears to be corrupted. For these dates, we used the raw data for our computations.
  - A person walking behind the robot causes noise in the final point cloud if not removed.
  - Mapping the color images to the laser scans often results in the tip of the vines receiving the color of the sky.


## Scripts
* `create_pointclouds.py` extracts the local point clouds from the synchronized rosbags and uses the given poses to transform them into a global coordinate system. For projection of the color images, we assume that the synchronized rosbags are used.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.

The expected folder structure for the data is as follows. We mainly used the synchronized ROS bags, even though our code also allows to use the raw data (which we did for `june_22`, as the synchronized ROS bag for this date is missing).

```
BLT
  |-- rosbags
        |-- Ktima Gerovassiliou
            |-- kg_april_06.bag
            |-- kg_april_20.bag
            |-- kg_june_08.bag
            |-- ...
        |-- Riseholme
  |-- pointclouds        # This gets created by the create_pointclouds.py script
        |-- Ktima Gerovassiliou
            |-- kg_april_06
                |-- tile_0_0.laz
                |-- tile_0_1.laz
                |-- tile_0_2.laz
                |-- ...
            |-- kg_april_20
            |-- kg_june_08
            |-- ...
```