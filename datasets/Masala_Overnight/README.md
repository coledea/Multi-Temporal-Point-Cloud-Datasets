# The Masala Overnight Dataset

<img src="./../../images/Masala Overnight.png" width="400"/>

[Original Dataset Website](https://etsin.fairdata.fi/dataset/6e3e85fc-ba9a-49b1-962c-b540a07ea77f) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Masala_Overnight)

## Notes
  - For some timepoints, full scans are provided. While these do not include semantic/instance information, for all timepoints, individual point clouds for segmented objects are provided.  
  - The objects have a known type but there is not a fixed number of classes into which objects are sorted. The number of different classes can be extracted from the list of all objects by grouping similar objects into one class.
  - The point clouds of the third night are not registered to those of the first and second. Additionally, the captured objects and corresponding instance IDs do not necessarily match between these scans. Therefore, we excluded the October data from our computations.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the share of partial epochs.

The expected folder structure for the data is as follows:

```
Masala_Overnight
  |-- 2016_August_LeafOn
        |-- Aug23
            |-- LAZ_Target_01
            |-- LAZ_Target_02
            |-- ...
        |-- Aug24
            |-- LAZ_Target_01
            |-- LAZ_Target_02
        |-- ...
  |-- ...
```