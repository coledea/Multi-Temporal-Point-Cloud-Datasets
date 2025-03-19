# The AHK 1 Dataset

<img src="./../../images/AHK 1.png" width="400"/>

[Original Dataset Website](https://doi.org/10.1594/PANGAEA.902042) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/AHK_1)


## Notes


## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
AHK_1
  |-- 20150701_TLS_Hochebenkar_UTM32N.txt
  |-- 20170719_TLS_Hochebenkar_UTM32N.txt
  |-- ...
```