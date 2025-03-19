# The KTH Longterm Dataset

<img src="./../../images/KTH Longterm.png" width="400"/>

[Original Dataset Website](https://strands.pdc.kth.se/public/KTH_longterm_dataset_registered/readme.html) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/KTH_Longterm)

## Notes  
  - The paper speaks of (semantic) labels for one of the rooms, but they are not present in the downloadable dataset
  - The website and paper speak of 8 waypoints while there are actually 9
  - In 20140827/patrol_run_14, there is a scan named WayPoint21. However, this waypoint does not exist. It seems to be WayPoint22 actually.
  - There is a WayPoint23 with only one scan, which actually corresponds to WayPoint12, but is not registered to the other scans of this waypoint
  - For WayPoint1, 50 of 79 scans are not registered correctly to the other 29 of which one is the very first scan. Therefore, the 50 other scans fail the overlap test. Among themselves, however, the two groups are coarsely registered.



## Scripts
* `download_complete_pointclouds.py` downloads only the `complete_cloud.pcd` files from the dataset (i.e., the actual final point clouds) and renames them according to the corresponding waypoint. As the first argument, the provided `download_paths.csv` has to be passed.
* `rename_pointclouds.py` renames the `complete_cloud.pcd` files according to the corresponding waypoint if the full dataset was downloaded from the website (instead of using the `download_complete_pointclouds.py` script).
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the share of partial epochs.

The expected folder structure for the data is as follows. The `.pcd` files have to be named according to the scanned waypoint. This is done automatically by either the `download_complete_pointclouds.py` or the `rename_pointclouds.py` script:

```
KTH_Longterm
  |-- 20140820
      |-- patrol_run_1
          |-- room_0
              |-- WayPoint19.pcd
          |-- room_2
              |-- WayPoint1.pcd
          |-- room_3
              |-- WayPoint5.pcd
          |-- ...
      |-- patrol_run_2
      |-- patrol_run_3
      |-- patrol_run_4
  |-- 20140822
  |-- 20140826
  |-- ...
```