# The Underwood et al. Dataset

<img src="./../../images/Underwood et al.png" width="400"/>

[Original Dataset Website](https://www.acfr.usyd.edu.au/papers/icra13-underwood-changedetection.shtml) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Underwood_et_al)

## Notes
  - Each epoch is split into multiple scans obtained from different positions that can be fused into one point cloud.
  - In contrast to the other scenes, for the "sim" scene the y-axis faces upwards which gets corrected when applying the given pose.



## Scripts
* `create_pointclouds.py` combines the scans for each epoch into a unified point cloud using the given poses.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the number of partial epochs.

The expected folder structure for the data is as follows:

```
Underwood_et_al
  |-- raw
      |-- carpark
          |-- carpark1.pose1.csv
          |-- carpark1.pose1.object1.label.csv
          |-- carpark1.pose1.object2.label.csv
          |-- ...
      |-- lab
      |-- sim
  |-- pointclouds           # This gets created by the "create_pointclouds.py" script.
      |-- carpark
          |-- epoch_1.laz
          |-- epoch_2.laz
      |-- lab
      |-- sim
```