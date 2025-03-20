# The Bad Frankenhausen Dataset

<img src="./../../images/Bad Frankenhausen.png" width="400"/>

[Original Dataset Website](https://zenodo.org/records/6521706) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Bad_Frankenhausen)

## Notes
  - All point clouds are stored in one binary CloudCompare file (together with the M3C2 results).
  - While the point clouds contain an intensity attribute, it seems to be just the color value converted to greyscale. As the point clouds are the result of photogrammetric reconstruction, it can't be an actual intensity value as obtained during laser scanning.
  - For each epoch, one point cloud reconstructed from terrestrial photos and one from aerial photos is available.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

First, the point clouds have to be extracted from the binary file.
For this, open the file with [CloudCompare](https://www.danielgm.net/cc/) and save each of the contained point clouds, for example as LAS files.
The expected folder structure for the data is as follows:

```
Bad Frankenhausen
  |-- pointclouds
        |-- 2017_erdfall_terr_new_august_with_pm.las
        |-- 2017_erdfall_uav_new_optimized_with_pm.las
        |-- ...
```