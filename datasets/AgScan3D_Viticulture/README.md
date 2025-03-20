# The AgScan3D Viticulture Dataset

<img src="./../../images/AgScan3D Viticulture.png" width="400"/>

[Original Dataset Website](https://data.csiro.au/collection/csiro:51813) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/AgScan3D_Viticulture)

## Notes
  - The data is represented as ray clouds, storing the origin of the laser in addition to the surface point. To convert the ray cloud into a point cloud, all points with alpha=0 (rays that did not hit anything) have to be discarded.
  - Only a small subset of the originally acquired dataset is released. Within this subset only some rows were scanned multiple times.
  - For Rymill_b13_r27_to_r33, two PLY files for the same raw data exist. One contains the ray cloud, the other one a derived point cloud with the ray direction stored as normal values.

## Scripts
* `create_pointclouds.py` converts the ray clouds for all scenes with multiple epochs to point clouds
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
AgScan3D_Viticulture
  |-- raw
        |-- Mclarenvale_Dec2019
            |-- McLaren_b07_r97_6cam_02.ply
            |-- McLaren_b07_r100_to_r94_01.ply
            |-- ...
        |-- Mclarenvale_Nov2019
        |-- Mclarenvale_Oct2019
        |-- Rymill_Dec2019
        |-- Rymill_Nov2019
        |-- Rymill_Oct2019
  |-- pointclouds            # this gets created by the create_pointclouds.py script
        |-- b07_r100_to_r94
            |-- Dec2019.laz
            |-- Oct2019.laz
        |-- b12_r27_to_r33
        |-- b13_r30_6cam
        |-- b90_r131_to_r125
```