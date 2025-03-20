# The Boreas Dataset

<img src=./../../images/Boreas.png width="400"/>

[Original Dataset Website](https://www.boreas.utias.utoronto.ca) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Boreas)


## Notes
  - There are two different routes, but one route is only followed once in one of the (test) sequences.
  - The route of the additional Boreas-Objects-V1 dataset does not seem to correspond to the other sequences. 
  - For 10 epochs, the ground thruth trajectory has not been released to facilitate a comparable, public benchmark.
  - The quality of the point clouds strongly depends on the weather during acquisition.
  - The download website depicts the estimated download size and calculates with 100 GB per sequence. Many sequences actually have a lower size (~80 GB).
  - In the pip version of pyboreas (the accompanying Python package for the dataset), the odom_train split erroneously contains `boreas-2021-04-29-15-55`, which however has no odometry data available.


## Scripts
* `create_pointclouds.py` combines the local point cloud batches from the binary LiDAR files with the given poses to obtain a globally aligned point cloud. On Windows, the pyboreas package may not work properly due to how parallelization is implemented. A fix for this has been submitted, but it is not yet part of the package available via pip. So you may want to install the package from source in this case or adjust the source code of the pip package locally.
* `create_2d_renderings.py` renders the point clouds resulting from the `create_pointclouds.py` script to the ground plane. As each tile is rendered separately, the color mapping is only valid within a tile, leading to visible tile borders. However, in our case, we used these renderings only for assessing the area coverage of a point cloud.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.

The expected folder structure for the data is as follows:
```
Boreas
  |-- raw
      |-- boreas-2020-11-26-13-58
          |-- applanix
          |-- calib
          |-- camera
          |-- lidar
          |-- ...
      |-- boreas-2020-12-01-13-26
      |-- boreas-2020-12-18-13-44
      |-- ..
  |-- pointclouds        # This gets created by the create_pointclouds.py script
      |-- boreas-2020-11-26-13-58
          |-- tile_0_1.laz
          |-- tile_0_2.laz
          |-- tile_0_3.laz
          |-- ...
      |-- boreas-2020-12-01-13-26
      |-- boreas-2020-12-18-13-44
      |-- ...
```