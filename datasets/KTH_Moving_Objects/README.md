# The KTH Moving Objects Dataset

<img src="./../../images/KTH Moving Objects.png" width="400"/>

[Original Dataset Website](https://strands.pdc.kth.se/public/KTH_labelled_moving_objects/readme.html) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/KTH_Moving_Objects)

## Notes
  - This dataset extends the KTH Longterm Label dataset with additional data from more waypoints. This additional data contains fewer labels (10) but only for objects that were consistently located in different positions in multiple rooms.
  - It seems that the waypoint IDs do not match between this and the other KTH datasets.
  - For WayPoint2 and WayPoint29, only one scan exists.
  - The point clouds contain many (~25% at times) NaN points that have to be filtered out first.
  - As only 10 objects are labeled that are consistently located in different places, the labels could be understood as semantic, instance, and change labels at the same time.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the share of partial epochs.
* `compute_avg_change_points.py` computes the average percentage of points that are labeled as changed across all second epoch point clouds. We compute this value using the individual object point clouds provided besides the full scans (`complete_cloud.pcd`), as these objects are consistently located at different places.

The expected folder structure for the data is as follows:

```
KTH_Moving_Objects
  |-- WayPoint2
  |-- WayPoint3
      |-- 20151221
          |-- patrol_run_9
              |-- room_4
                  |-- complete_cloud.pcd
                  |-- rgb_0001_label_0.pcd
                  |-- rgb_0004_label_0.pcd
                  |-- ...
          |-- patrol_run_11
      |-- 20160107
      |-- 20160108
  |-- WayPoint4
  |-- ...
```