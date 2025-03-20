# The Fehr et al. Dataset

<img src="./../../images/Fehr et al.png" width="400"/>

[Original Dataset Website](https://github.com/ethz-asl/change_detection_ds) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Fehr_et_al)

## Notes
- The pointclouds in the ROS bags contain some points with their color erroneously being black, i.e., it is clear from the scene that these surface points were not black in the real world. We filtered them out for our computations.

## Scripts
* `create_pointclouds.py` extracts the globally aligned pointcloud frames from the rosbags and combines them into one unified pointcloud per epoch.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.

The expected folder structure for the data is as follows:

```
Fehr_et_al
  |-- raw
      |-- living_room
          |-- complete_mesh
          |-- rosbag
              |-- observation_0.bag
              |-- observation_1.bag
              |-- ...
      |-- lounge
      |-- office
  |-- pointclouds           # This gets created by the "create_pointclouds.py" script.
      |-- living_room
          |-- observation_0.laz
          |-- observation_1.laz
          |-- ...
      |-- lounge
      |-- office
```