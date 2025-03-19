# The Belvedere Glacier Dataset

<img src="./../../images/Belvedere Glacier.png" width="400"/>

[Original Dataset Website](https://zenodo.org/records/10817029) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Belvedere_Glacier)

## Notes
  - The two oldest epochs have only greyscale values instead of RGB colors
  - The epochs from 2015 on cover a smaller area compared to the previous epochs (probably as these were acquired using a UAV compared to an aircraft) 


## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Belvedere_Glacier
  |-- belvedere_1977_histo
        |-- belv_1977_histo_pcd.laz
  |-- belvedere_1991_histo
        |-- belv_1991_histo_pcd.laz
  |-- ...
  |-- belvedere_2023_uav
        |-- belv_2023_uav_pcd-0.laz
        |-- belv_2023_uav_pcd-1.laz
        |-- ...
  |-- ...
```
