# The KTH Longterm Labels Dataset

<img src="./../../images/KTH Longterm Labels.png" width="400"/>

[Original Dataset Website](https://strands.pdc.kth.se/public/KTH_longterm_dataset_labels/readme.html) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/KTH_Longterm_Labels)

## Notes  
  - This is an extension of the KTH Longterm dataset by semantic labels for Waypoint16. However, the point clouds are smaller, because only the RGB-D images for a single height were used.
  - The labels are available in form of image annotations that would have to be combined with the depth and color images to reconstruct a point cloud. 
  - For each object, only one label image is available, even if the object appears in multiple images. Also, not all objects are labeled.
  - Alternatively, for each segmented object, a single point cloud is available. However, the object is also still present in the full point cloud.


## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the share of partial epochs.

The expected folder structure for the data is as follows:

```
KTH_Longterm_Labels
  |-- 20140820
      |-- patrol_run_2
          |-- room_1
              |-- complete_cloud.pcd
              |-- ...
      |-- patrol_run_4
  |-- 20140828
  |-- 20140829
  |-- ...
```