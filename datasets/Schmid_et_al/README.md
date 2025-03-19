# The Schmid et al. Dataset

<img src="./../../images/Schmid et al.png" width="400"/>

[Original Dataset Website](https://projects.asl.ethz.ch/datasets/doku.php?id=panoptic_mapping) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Schmid_et_al)

## Notes
  - The labels have to be mapped during backprojection by mapping the instance ID to the corresponding class/change.
  - For points outside of windows, the depth images contain pixels with very high depth values that can interfere with the reconstruction.
  - Also provides additional (semantic/instance) annotations in image format for two of the [3RScan](https://github.com/WaldJohannaU/3RScan) scenes.


## Scripts
* `create_pointclouds.py` reconstruct pointclouds from the RGBD data and given poses using backprojection.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the average percentage of points that are labeled as changed in the second epoch.

The expected folder structure for the dataset is as follows:

```
Schmid_et_al
  |-- flat_dataset
      |-- run1
          |-- 000000_color.png
          |-- 000000_depth.tiff
          |-- 000000_labels.json
          |-- 000000_pose.txt
          |-- 000000_predicted.png
          |-- 000000_segmentation.png
          |-- 000001_color.png
          |-- ...
      |-- run2
      |-- changes.txt
      |-- groundtruth_labels.csv
      |-- ...
  |-- pointclouds                 # this gets created by the create_pointclouds.py script
      |-- run1.laz
      |-- run2.laz
```