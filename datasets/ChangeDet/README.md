# The ChangeDet Dataset

<img src=./../../images/ChangeDet.png width="400"/>

[Original Dataset Website](https://yewzijian.github.io/ChangeDet) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/ChangeDet)

## Notes
  - The (predicted) change points are stored redundantly in a separate file and could be used to annotate the original point cloud.
  - The point clouds contains no ground points due to the photogrammetric creation from side-facing cameras.


## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
ChangeDet
  |-- BusinessDistrict
        |-- BusinessDistrict_t0_warped.pcd
        |-- BusinessDistrict_t1.pcd
        |-- ...
  |-- ResearhTown
        |-- ResearchTown_t0_warped.pcd
        |-- ResearchTown_t1.pcd
        |-- ...
```