# The USyd Campus Dataset

<img src="./../../images/USyd Campus.png" width="400"/>

[Original Dataset Website](https://ieee-dataport.org/open-access/usyd-campus-dataset) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/USyd_Campus)


## Notes
- Originally, a web page was available for the dataset, describing its use in more detail. However, the website is not available anymore. Parts of it can be accessed through the Internet Archive.
- A code release is available for the dataset at https://gitlab.acfr.usyd.edu.au/its/dataset_metapackage. The code is a bit hard to find, as the original dataset web page where the code was linked no longer exists.
- The archives for the weeks 30, 33, and 34 appear to be corrupted. The ROS bag files can not be extracted properly.
- While a number of semantically labeled images are available, they are not matched to acquisition times and corresponding lidar scans. Therefore, these images can not be used for projecting semantic labels to the point cloud
- Although poses are provided for the LiDAR scans, the resulting point cloud is quite noisy (also due to many moving objects) and exihibts significant drift. In the initial part of the route, to which the vehicle returns at the end, height discrepancies of 100-200 meters can occur between the start and end position. More accurate results could be achieved by employing a SLAM approach to compute more precise poses and achieve proper loop closure.

## Scripts
* `create_pointclouds.py` extracts the local point clouds from the rosbags and uses the given poses to transform them into a global coordinate system.
* `create_2d_renderings.py` renders the point clouds resulting from the `create_pointclouds.py` script to the ground plane. As each tile is rendered separately, the color mapping is only valid within a tile, leading to visible tile borders. However, in our case, we used these renderings only for assessing the area coverage of a pointcloud.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.


```
USyd_Campus
  |-- rosbags
      |-- Week1_2018-03-08
      |-- Week2_2018-03-16
          |-- 2018-03-16-10-33-39_Dataset_year.bag
          |-- 2018-03-16-10-33-39_Dataset_year-A0.h264
          |-- 2018-03-16-10-33-39_Dataset_year-A1.h264
          |-- ...
      |-- Week3_2018-03-22	
      |-- ...
  |-- pointclouds        # This gets created by the create_pointclouds.py script
      |-- Week1_2018-03-08
          |-- tile_0_0.laz
          |-- tile_0_1.laz
          |-- ...
      |-- Week2_2018-03-16
      |-- Week3_2018-03-22	
      |--

```