# The Change3D Dataset

<img src=./../../images/Change3D.png width="400"/>

[Original Dataset Website](https://kutao207.github.io) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Change3D)

## Notes
  - The corresponding paper has been retracted due to errors in the evaluation. A later paper from 2023 again describes the dataset, enriched by synthetic data. However, this second version of the dataset can not be found anywhere. 
  - The paper speaks of "over 78 [...] point cloud pairs", but the dataset actually contains exactly 78 and for 2020 one additional scan with prefix "15_" that is missing in 2016.
  - The acquisition is unclear. The paper states that "The 3D data from CycloMedia are generated from depth maps instead of original LiDAR scans", but the website and the second paper speak of "vehicle mounted LiDAR sensors".
  - For computing the label distribution, we extracted cylindrical environments around the POIs and removed the groundplane, as described in the paper. Wang et al. (2023) already provide the data with annotated change labels (which they refer to as the new dataset [SLPCCD]{https://github.com/wangle53/3DCDNet}).



## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs
* `compute_avg_change_points.py` computes the average percentage of points that are labeled as changed across all second epoch point clouds. Points labeled as "removed" in the first epoch are counted towards the percentage of change points for the second epoch. As the labels are only stored for a representative point of an object, the corresponding object has first to be extracted using a cylindrical crop volume and subsequent ground plane removal.

The expected folder structure for the data is as follows:

```
Change3D
  |-- 2016
        |-- 0_5D4KVPBP.laz
        |-- 2_5D4KVPDO.laz
        |-- ...
  |-- 2020
        |-- 0_WE1NZ71I.laz
        |-- 2_WE1NZ8KQ.laz
        |-- ...
  |-- labels
      |-- labeled_point_lists
          |-- 2016-2020
              |-- 0_5D4KVBP_5D4KVBP.csv
              |-- ...
      |-- ...
```