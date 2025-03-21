# The ChangeSim Dataset

<img src=./../../images/ChangeSim.png width="400"/>

[Original Dataset Website](https://sammica.github.io/ChangeSim) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/ChangeSim)

## Notes
  - RGBD data and poses are available for all runs. However, for the Ref_test sequences, the trajectory.txt files contain more or less entries than there are images available. It is unclear, how the poses are to be synced with the image data, as no timestamps are provided.
  - The depth images contain banding artifacts (probably from quantization - the images have only one 8 bit channel) that make an accurate reconstruction difficult.
  - While reconstruction from the depth images seems to be difficult, for the query epochs, point cloud reconstructions are available. For the reference epochs, point clouds can be exported from the RTAB-Map database (using the [RTAB-Map](http://introlab.github.io/rtabmap/) database viewer). For this, we used a 20m depth limit and removed duplicate points. 
  - The dataset can be considered to have 4 epochs per scene - the first and second between which actual changes happen, and the two additional runs for dark and dust, for which only appearance changes happened.
  - While the sequence number generally corresponds to the trajectory followed, Query_Seq_0_dark seems to follow another path than the other runs in Seq_0.


## Scripts
* `create_pointclouds.py` reconstruct pointclouds from the RGBD data and given poses. Please note that this works only for the query sequences and the results are very noisy. We didn't use these for computing the statistics.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. We used the pre-computed point cloud maps and the ones exported from the RTAB-Map database for this.
* `compute_avg_change_points.py` computes the average percentage of points that are labeled as changed across all second epoch point clouds. Please note that we compute this value on the image change masks (as it is also done in the ChangeSim paper), which might overrepresent areas that were scanned more often.

Before computing the statistics, the data has to be prepared. For the reference epochs, point clouds have to be exported from the RTAB-Map database, using the [database viewer](https://github.com/introlab/rtabmap/wiki/Tools).
For the query epochs, the already available point cloud reconstructions can be used. The expected folder structure is depicted below.

```
ChangeSim
  |-- Query_Seq_Test
      |-- Warehouse_6
          |-- Seq_0
              |-- change_segmentation
              |-- depth
              |-- pose
              |-- rgb
              |-- cloud_map.ply
              |-- trajectory.txt
              |-- ...
          |-- Seq_0_dark
          |-- Seq_0_dust
          |-- Seq_1
          |-- ...
      |-- ...
  |-- Ref_Seq_Test
      |-- Warehouse_6
          |-- depth
          |-- rgb
          |-- cloud_map.ply   # This needs to be exported from rtabmap.db
          |-- rtabmap.db
          |-- trajectory.txt
          |-- ...
      |-- ...
  |-- Query_Seq_Train
  |-- Ref_Seq_Train
```