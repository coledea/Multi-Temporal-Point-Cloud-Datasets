# The AHK 2 Dataset

<img src="./../../images/AHK 2.png" width="400"/>

[Original Dataset Website](https://doi.org/10.11588/data/TGSVUI) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/AHK_2)

## Notes
  - The area is split into 10 non-overlapping tiles

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
AHK_2
  |-- Hochebenkar_TLS_20190624
        |-- 20190624_region_1a_normals.xyz
        |-- 20190624_region_1b_normals.xyz
        |-- ...
  |-- Hochebenkar_TLS_20190706
        |-- 20190706_region_1a_normals.xyz
        |-- 20190706_region_1b_normals.xyz
        |-- ...
  |-- ...
```