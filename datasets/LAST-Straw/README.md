# The LAST-Straw Dataset

<img src="./../../images/LAST-Straw.png" width="400"/>

[Original Dataset Website](https://lcas.github.io/LAST-Straw) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/LAST-Straw)

## Notes

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
LAST-Straw
  |-- variety_A
      |-- A1_20220512.xyz
      |-- A1_20220519.xyz
      |-- ...
  |-- variety_B
  |-- ...
```