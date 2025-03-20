# The Kijkduin Dataset

<img src="./../../images/Kijkduin.png" width="400"/>

[Original Dataset Website](https://doi.pangaea.de/10.1594/PANGAEA.934058) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Kijkduin)

## Notes
  - In an earlier paper, a [subset of this dataset](https://data.4tu.nl/articles/_/12692660/1) with denser but only daily point clouds was used and released.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Kijkduin
  |-- scans
        |-- 161111
              |-- 161111_200058.laz
              |-- 161111_210058.laz
              |-- ...
        |-- 161112
        |-- 161113
        |-- ...
```