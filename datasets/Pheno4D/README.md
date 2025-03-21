# The Pheno4D Dataset

<img src="./../../images/Pheno4D.png" width="400"/>

[Original Dataset Website](https://www.ipb.uni-bonn.de/data/pheno4d) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Pheno4D)

## Notes
  - Only every second scan has instance labels. For the maize plants, also semantic labels are available.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs


The expected folder structure for the data is as follows:

```
Pheno4D
  |-- Maize01
      |-- M01_0313_a.txt
      |-- M01_0314.txt
      |-- ...
  |-- Maize02
  |-- ...
  |-- Tomato0
  |-- Tomato1
  |-- ...
```