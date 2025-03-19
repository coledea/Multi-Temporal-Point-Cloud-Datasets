# The AbenbergALS Dataset

<img src="./../../images/AbenbergALS.png" width="400"/>

[Original Dataset Website](https://www.iosb.fraunhofer.de/en/competences/image-exploitation/object-recognition/3d-data/datasets/abenberg-als.html) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/AbenbergALS)

## Notes

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
AbenbergALS
  |-- abenberg_data_2008
        |-- abenberg_data_2008.txt
        |-- ...
  |-- abenberg_data_2009
        |-- abenberg_data_2009.txt
        |-- ...
```