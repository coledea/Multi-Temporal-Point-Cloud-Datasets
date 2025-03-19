# The Schneeferner Dataset

<img src="./../../images/Schneeferner.png" width="400"/>

[Original Dataset Website](https://doi.pangaea.de/10.1594/PANGAEA.941550) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Schneeferner)

## Notes
  - The scene was scanned from two different locations, as the scanner was moved to a more protected place during night (leading to less spatial coverage)
  - Some scans contain artifacts (noise points), especially near the scanner position

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the percentage of partial epochs.

The expected folder structure for the data is as follows:

```
Schneeferner
  |-- 180417_140322.laz
  |-- 180417_150010.laz
  |-- 180417_160010.laz
  |-- ...
```