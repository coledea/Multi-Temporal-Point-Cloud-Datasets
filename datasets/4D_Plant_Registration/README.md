# The 4D Plant Registration Dataset

<img src="./../../images/4D Plant Registration.png" width="400"/>

[Original Dataset Website](https://www.ipb.uni-bonn.de/data/4d-plant-registration) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/4D_Plant_Registration)

## Notes

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
4D Plant Registration
  |-- maize
        |-- plant1
        |-- plant2
        |-- plant3
  |-- tomato
        |-- plant1
        |-- plant2
        |-- plant3
```