# The SMARS Dataset

<img src=./../../images/SMARS.png width="400"/>

[Original Dataset Website](https://www2.isprs.org/commissions/comm1/wg8/benchmark_smars) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/SMARS)

## Notes
  - Even though the metadata of the files specifies WGS 84/UTM zone 31 as spatial reference system, the images are actually not georeferenced. 
  - It says on the website that "the python code used to split the data for our experiments are also provided and users can customize the codes to their needs (we will publish the code soon)." However, this did not seem to have happened.
  - The TIF files for SParis/50cm appear to have the content of their channels not specified correctly in the metadata. Some viewers (GIMP, Windows viewer) are not able to open them correctly. Re-saving (e.g., with IrfanView) fixes the issue. Additionally, these images have a different resolution compared to the other images, which is however expected and documented in the paper.
  - The change map files for SParis/30cm have an additional "_gt" suffix in their name, which the other change maps do not have. This has to be taken care of when parsing the dataset automatically.
  - The buildings that were removed in the second epoch are still there, just with a corresponding label.



## Scripts
* `create_pointclouds.py` combines the DSM, RGB, label, and change images to create a 3D point cloud. Please note that the images for SParis/50cm suffer from incorrectly specified metadata. We handle this by using `tifffile`, which is more robust in these cases (compared to `OpenCV`, which we use in all other cases). However, if you want to open these images in an image viewer, you might have to re-save them first.
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs. Also computes the average percentage of points that are labeled as changed across all second epoch point clouds.

The expected folder structure for the data is as follows:

```
SMARS
  |-- SMARS_release
      |-- SParis
          |-- 30cm
              |-- change_map
                  |-- test
                  |-- train
                  |-- val
                  |-- SParis_30cm_change_map_2classes_building_gt.tif
                  |-- SParis_30cm_change_map_3classes_gt.tif
              |-- post
                  |-- original
                      |-- SParis_30cm_post.tif
                      |-- SParis_30cm_post_building_gt.tif
                      |-- SParis_30cm_post_dsm.tif
                      |-- SParis_30cm_post_gt.tif
                  |-- splitting
              |-- pre
          |-- 50cm
      |-- SVenice
  |-- pointclouds            # this gets created by the create_pointclouds.py script
      |-- SParis
          |-- 30cm
              |-- post.laz
              |-- pre.laz
          |-- 50cm
      |-- SVenice
```