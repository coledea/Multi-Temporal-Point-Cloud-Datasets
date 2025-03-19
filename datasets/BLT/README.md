# The BACCHUS Long-Term (BLT) Dataset

<img src=./../../images/BLT.png width="400"/>

[Original Dataset Website](https://lncn.ac/lcas-blt) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/BLT)


## Notes
  - For the KG scene, in addition to the raw data, also rosbags with synchronized sensor outputs are available.
  - Poses are provided only for the KG scene, while the Riseholme data only contains odometry and IMU data. To reconstruct a unified point cloud from this data, a SLAM solution has to be used (we tested [FasterLIO](https://github.com/gaoxiang12/faster-lio), which worked reasonably well). However, as argued in the paper, we only used the KG scene for our computations.
  - For the KG scene, the paper and the website list 11 epochs. At the same time, the website states that there are only 10 epochs. We found that the synchronized rosbag for May 18th (`kg_may_18.bag`) is corrupted and reindexing (using `rosbag reindex`) discards most of its data. Also, this is the only date, for which raw data is not available. Therefore, in the end there are 10 usable epochs available.
  - In the downloadable files, `june_22` is missing from the synchronized rosbags and `kg_september_09.bag` seems to be corrupted. For these dates, we used the raw data for our computations.
  - A person walking behind the robot causes noise in the final point cloud if not removed
  - Mapping the color images to the laser scans often results in the tip of the vines receiving the color of the sky


## Scripts
* `create_pointclouds.py` extracts the local point clouds from the synchronized rosbags and uses the given poses to transform them into a global coordinate system. For projection of the color images, we assume that the synchronized rosbags are used.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.

The expected folder structure for the data is as follows. We mainly used the synchronized rosbags, even though our code also allows to use the raw data (which we did for `june_22`, as the synchronized rosbag for this date is missing).

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