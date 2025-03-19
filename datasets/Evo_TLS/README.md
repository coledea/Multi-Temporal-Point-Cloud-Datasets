# The Evo TLS Dataset

<img src="./../../images/Evo TLS.png" width="400"/>

[Original Dataset Website](https://www.scanforest.fi/data/) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Evo_TLS)

## Notes
  - This dataset is an artificial combination of two individual datasets that cover the same area
  - The 2019 epochs all cover a slightly larger area than the corresponding 2014 epochs (rectangular in 2014 vs. circular in 2019)
  - In addition to the two epochs referenced in the paper, additional epochs for a different number of plots are available as separate datasets


## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Evo_TLS
  |-- Evo_TLS_2014_laz
      |-- 1002_hnorm.laz
      |-- 1005_hnorm.laz
      |-- 1007_hnorm.laz
      |-- ...
  |-- Evo_TLS_2019_laz
      |-- 1002_hnorm.laz
      |-- 1005_hnorm.laz
      |-- 1007_hnorm.laz
      |-- ...
```