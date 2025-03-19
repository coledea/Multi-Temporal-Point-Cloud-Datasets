# The 3DCD Dataset

<img src=./../../images/3DCD.png width="400"/>

[Original Dataset Website](https://sites.google.com/uniroma1.it/3dchangedetection/home-page) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/3DCD)

## Notes
  - The paper states that the dataset contains 472 pairs of images, but there are only 471 available for download 
  - 88 of the DSMs contain erroneous parts (black stripes)
  - The file train/3D/356-4612_6_6.tif is corrupted and can't be read

## Scripts
* `create_pointclouds.py` combines the DSM, RGB, and change images to create a 3D point cloud
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs
* `compute_avg_change_points.py` computes the average percentage of points that are labeled as changed across all second epoch point clouds. We compute this value on the change masks.

The expected folder structure for the data is as follows:

```
3DCD
  |-- raw
      |-- train
            |-- 3D
            |-- 2010
            |-- 2017
            |-- DSM_2010
            |-- DSM_2017
      |-- test
            |-- ...
      |-- val
            |-- ...
  |-- pointclouds            # this gets created by the create_pointclouds.py script
        |-- 348-4608_4_5
            |-- 348-4608_4_5_2010.las
            |-- 348-4608_4_5_2017.las
        |-- ...
```