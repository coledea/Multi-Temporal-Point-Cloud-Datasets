# The MulRan Dataset

<img src="./../../images/MulRan.png" width="400"/>

[Original Dataset Website](https://sites.google.com/view/mulran-pr/home) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/MulRan)

## Notes
  - Each sequence has to be requested individually by filling out a Google Form.
  - There is one smaller sample sequence (Parking Lot) for which only one timestamp exists. 

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
MulRan
  |-- DCC01
      |-- sick_pointcloud.las
      |-- ...
  |-- DCC02
  |-- DCC03
  |-- KAIST01
  |-- ...
```