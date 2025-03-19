# The Hessigheim3D Dataset

<img src="./../../images/Hessigheim3D.png" width="400"/>

[Original Dataset Website](https://ifpwww.ifp.uni-stuttgart.de/benchmark/hessigheim/default.aspx) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Hessigheim3D)

## Notes
  - Provides data both as TXT and LAZ
  - The first epoch was obtained via aircraft, the subsequent ones via UAV
  - The first epoch has intensity values, the subsequent ones reflectance

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Hessigheim3D
  |-- Epoch_March2016
        |-- LiDAR
              |-- Mar16_test.laz
              |-- Mar16_train.laz
              |-- ...
        |-- ...
  |-- Epoch_March2018
        |-- LiDAR
              |-- Mar18_test.laz
              |-- Mar18_train.laz
              |-- ...
        |-- ...
  |-- ...
            
```