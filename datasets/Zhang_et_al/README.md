# The Dataset from Zhang et al.

<img src="./../../images/Zhang et al.png" width="400"/>

[Original Dataset Website](https://doi.org/10.17026/dans-xzg-nqdg) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Zhang_et_al)

## Notes
  - One epoch is provided as ALS point cloud, the other one as photogrammetric point cloud
  - The ALS point cloud is split into ground and non-ground points.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs


The expected folder structure for the data is as follows:

```
Zhang_et_al
  |-- ALS-g-raw.las
  |-- ALS-u-raw.las
  |-- RawPC(lasgrid)(39M).las
  |-- ...
```