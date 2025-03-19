# The Eschikon Dataset

<img src=./../../images/Eschikon.png width="400"/>

[Original Dataset Website](https://projects.asl.ethz.ch/datasets/doku.php?id=2018plantstressphenotyping) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Eschikon)

## Notes
  - Only every second scan is labeled
  - The paper states that the dataset consists of scans from 31 boxes. However, the available data only contains 30 boxes. 
  - In the Matlab files, the naming convention is not consistent. For the first epoch, the data item is named "Results1". For the subsequent epochs, the data items are named "Results3" (point_cloud_2.mat) to "Results16" (point_cloud_15.mat). For the last epoch (point_cloud_16.mat), the data item is named "point_cloud_16".
  - Similar to the naming issue, the provided data set index ("DataSet") in the Matlab files is wrong. From the second epoch on, the index is one step higher than it should be. The last and the second-to-last epoch both store the same index (16), even though they clearly do not contain the same data.


## Scripts
* `create_pointclouds.py` converts the Matlab files to another format using the Matlab Engine. It seems that there is currently no way around installing Matlab and, for example, using its Python API for performing the conversion. Other libraries, such as mat4py or scipy weren't able to handle these specific files.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Eschikon
  |-- MeasurementPointcloud.m      # important for correct parsing of the data during conversion
  |-- pointclouds
        |-- point_cloud_1.mat
        |-- point_cloud_2.mat
        |-- point_cloud_3.mat
        |-- ...
  |-- converted_pointclouds       # this gets created by the create_pointclouds.py script
        |-- Box_1
            |-- epoch_0.las
            |-- epoch_1.las
            |-- ...
        |-- Box_2
        |-- ...
```