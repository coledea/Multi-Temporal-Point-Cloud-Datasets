# The MHT Building Dataset

<img src="./../../images/MHT Building.png" width="400"/>

[Original Dataset Website](https://lcas.lincoln.ac.uk/nextcloud/shared/datasets/mht_rgbd.html) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/MHT_Building)

## Notes
  - The released dataset corresponds to the "laboratory dataset" described in the paper
  - The website states that "each rosbag with a 3D prefix contains a depth/color image, camera information, robot position, tf data, laser scan and person detection [...]" and "each rosbag with a 2D prefix contains AMCL position estimates, robot odometry, tf data and laser scans". Actually, the 3D rosbags contain depth and color images, robot poses, and laser scans, while the 2D rosbags contain robot poses and laser scans. No information is provided regarding camera intrinsics.
  - The full download contains more data (two additional days) than the website lists as individual downloadable files. For these additional scans (3D_2013-08-22 and 3D_2013-08-23), four scan locations instead of three are recorded. However, the rosbags only contain color and depth images without poses.
  - Some of the rosbags are corrupted (the ones with a ".active" file extension), probably due to the recording being terminated prematurely.
  - The timestamps of the poses and images do not match, i.e., all timestamps of the images are outside the range of timestamps stored for the poses. However, there are always the same amount of images and poses, so we assume that they can be mapped to each other in their stored order.


## Scripts
* `create_pointclouds.py` extracts the depth/color images from the rosbags and creates pointclouds via backprojection.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs.

The expected folder structure for the data is as follows:

```
MHT_Building
  |-- rosbags
        |-- 3D_2013-08-24
            |-- 3D_24-08-13-00-00_place_0.bag
            |-- 3D_24-08-13-00-00_place_1.bag
            |-- 3D_24-08-13-00-00_place_2.bag
            |-- ...
        |-- 3D_2013-08-25
        |-- 3D_2013-08-26
        |-- ...
  |-- pointclouds           # This gets created by the "create_pointclouds.py" script.
        |-- place_0
            |-- 24-08-13-00-00.laz
            |-- 24-08-13-00-05.laz
            |-- ...
        |-- place_1
        |-- place_2
```