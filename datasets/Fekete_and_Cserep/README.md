# The Fekete and Csérep Dataset

<img src="./../../images/Fekete and Cserép.png" width="400"/>

[Original Dataset Website](https://data.mendeley.com/datasets/9thyzzwd5d/2) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Fekete_and_Cserep)

## Notes

## Scripts
* `create_pointclouds.py` creates point clouds from the DSMs
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Fekete_and_Cserep
  |-- raw
        |-- ahn2_05m_dsm_amsterdam-small.tif
        |-- ahn2_05m_dsm_delft-center.tif
        |-- ahn2_05m_dsm_trees2
        |-- ...
  |-- pointclouds            # this gets created by the create_pointclouds.py script
        |-- ahn2_05m_dsm_amsterdam.laz
        |-- ahn2_05m_dsm_delft.laz
        |-- ahn2_05m_dsm_trees2.laz
        |-- ...
```