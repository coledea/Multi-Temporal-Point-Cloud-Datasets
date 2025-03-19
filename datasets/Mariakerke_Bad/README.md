# The Mariakerke Bad Dataset

<img src="./../../images/Mariakerke Bad.png" width="400"/>

[Original Dataset Website](https://zenodo.org/records/13759858) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Mariakerke_Bad)

## Notes
  - In the full archive download, the archive of July 2018 is corrupted and within the archive of June 2018, there is corrupted LAZ file
  - The file 171227_145945.laz seems to be corrupted

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Mariakerke_Bad
  |-- scans
        |-- 2017_december
            |-- 171201
                |-- 171201_005952_tr.laz
                |-- 171201_015953_tr.laz
                |-- ...
            |-- 171202
            |-- ..
        |-- 2017_november
        |-- 2018_april
        |-- ...
```