# The 3RScan Dataset

<img src=./../../images/3RScan.png width="400"/>

[Original Dataset Website](https://github.com/WaldJohannaU/3RScan) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/3RScan)

## Notes
  - Some scans have no rescans, alignment data, or labels. Others are very small due to upload or processing issues during acquisition.
  - The scans were labeled using crowdsourcing, which led to some annotations being erroneous or inconsistent (e.g., a backpack being an individual object in one scan and considered as part of the bed it lies next to in another one).
  - The semantic annotations are only available for the training and validation split and only in the form of mesh annotations. If an annotated point clouds should be constructed, either the mesh has to be sampled, or for each RGBD frame, the mesh's instance labels have to be rendered from the given camera pose and subsequently combined with the result of backprojecting the RGBD frame.
  - The scenes are not oriented consistently - sometimes the y-axis points upwards, in other cases the z-axis.


## Scripts
* `create_pointclouds.py` combines the RGBD images with the given poses to construct unified point clouds per epoch. To obtain labeled point clouds from the RGBD images, the rio_renderer from 3RScan's accompanying code could be used to render label images per RGBD frame before backprojecting them to a pointcloud. Alternatively, the resulting point cloud could be projected to the label meshes, provided by the dataset.
* `sample_pointclouds.py` samples point clouds from the meshes, which results in point clouds with class, instance, and change labels. Compared to the point clouds obtained via backprojection of the RGBD images, these pointclouds are cleaner but less representative of typical real-world scans.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also the number of partial epochs is computed.
* `compute_avg_change_points.py` computes the average percentage of points that are labeled as changed (excluding the first epoch per scene). We use the point clouds sampled from the meshes for this.


The expected folder structure for the data is as follows:

```
3RScan
  |-- raw
      |-- 00d42bed-778d-2ac6-86a7-0e0e5f5f5660
          |-- sequence.zip
          |-- ...
      |-- 00d42bef-778d-2ac6-848a-008ef6c19ad6
      |-- 0a4b8ef6-a83a-21f2-8672-dce34dd0d7ca
      |-- ...
      |-- 3RScan.json
      |-- objects.json
      |-- relationships.json
  |-- pointclouds               # this gets created by the create_pointclouds.py script
      |-- 0cac759b-8d6f-2d13-8e3b-2e3bc1ee1158
          |-- epoch_1.laz
          |-- epoch_2.laz
          |-- ...
      |-- 02b33e01-be2b-2d54-93fb-4145a709cec5
      |-- 4fbad31e-465b-2a5d-84b7-c0ddea978db4
      |-- ...
  |-- pointclouds_sampled       # this gets created by the sample_pointclouds.py script
        |-- 0cac759b-8d6f-2d13-8e3b-2e3bc1ee1158
          |-- epoch_1.laz
          |-- epoch_2.laz
          |-- ...
      |-- 02b33e01-be2b-2d54-93fb-4145a709cec5
      |-- 4fbad31e-465b-2a5d-84b7-c0ddea978db4
      |-- ...
```