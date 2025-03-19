# The KTH Meta-rooms Dataset

<img src="./../../images/KTH Meta-rooms.png" width="400"/>

[Original Dataset Website](https://strands.pdc.kth.se/public/metric_sweeps_201312/readme.html) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/KTH_Meta-rooms)

## Notes

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the share of partial epochs.

The expected folder structure for the data is as follows:

```
KTH_Meta-rooms
  |-- patrol_run_1
      |-- room_0
          |-- complete_cloud.pcd
          |-- ...
      |-- room_1
      |-- room_2
  |-- patrol_run_2
  |-- patrol_run_3
  |-- ...
```