# The Waikīkī Beach Dataset

<img src="./../../images/Waikīkī Beach.png" width="400"/>

[Original Dataset Website](https://doi.org/10.6084/m9.figshare.c.6911899.v1) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Waikiki_Beach)

## Notes
  - The last 56 RGB images (from 20200225 on) seem to be corrupted and can't be openend in a way to get valid color values.

## Scripts
* `create_pointclouds.py` combines the DSM and RGB images to create a 3D point cloud
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all (valid) epochs.

The expected folder structure for the data is as follows:

```
Waikiki_Beach
  |-- DTMs
        |-- 20180412_dem.tif
        |-- 20180412_dem.tfw
        |-- 20180418_dem.tif
        |-- 20180418_dem.tfw
        |-- ...
  |-- MOSAIC
        |-- 20180412_mosaic.tif
        |-- 20180418_mosaic.tif
        |-- ...
  |-- pointclouds                 # this gets created by the create_pointclouds.py script
      |-- 20180412.laz
      |-- 20180418.laz
      |-- ...
```