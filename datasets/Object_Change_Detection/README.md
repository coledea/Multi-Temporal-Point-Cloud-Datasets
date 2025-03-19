# The Object Change Detection Dataset

<img src="./../../images/Object Change Detection.png" width="400"/>

[Original Dataset Website](https://www.acin.tuwien.ac.at/en/vision-for-robotics/software-tools/object-change-detection-dataset-of-indoor-environments) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Object_Change_Detection)

## Notes
  - During writing the paper, the download link for the dataset stopped working (timeout). It is unclear whether the dataset was removed or is only temporarily unavailable. In any case, another dataset that uses the same raw scans is available [here](https://doi.org/10.48436/y3ggy-hxp10). The point clouds differ very slightly and are split into surfaces. Also the first epoch is not available. However, ROSbags for all scans are provided.



## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs
* `compute_avg_change_points.py` computes the average percentage of points that are labeled as changed across all second epoch point clouds. For this, it uses the files in the `Annotations` folders.

The expected folder structure for the data is as follows:

```
Object_Change_Detection
  |-- big_room
      |-- Annotations
          |-- scene2_GT.anno
          |-- scene3_GT.anno
          |-- ...
      |-- scene1.pcd
      |-- scene2.pcd
      |-- scene3.pcd
      |-- ...
  |-- kitchen_partial
  |-- living_room_partial
  |-- office_partial
  |-- small_room
```