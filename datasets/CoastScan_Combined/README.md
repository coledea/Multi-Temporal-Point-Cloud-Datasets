# The CoastScan Combined Dataset

<img src="./../../images/CoastScan Combined.png" width="400"/>

[Original Dataset Website](https://data.4tu.nl/datasets/05477395-f4fe-46dc-bed9-89da04c073cd) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/CoastScan_Combined)

## Notes
  - Comprises ALS and PLS/TLS data. The ALS data covers more area than the PLS/TLS data, but within each data type, the covered area remains the same.
  - The ALS data's z-coordinate is always the same as the y-coordinate, i.e., it is erroneous.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
CoastScan_Combined
  |-- ALS-data                    # as this data is erroneous, we don't use it
  |-- PLS_TLS-data
        |-- 190822_110236c.xyz
        |-- 190919_220210c.xyz
        |-- ...
```