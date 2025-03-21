# The Trail Valley Creek Dataset

<img src="./../../images/Trail Valley Creek.png" width="400"/>

[Original Dataset Website](https://doi.pangaea.de/10.1594/PANGAEA.901293) | [Additional Dataset Details](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/details/Trail_Valley_Creek)

## Notes
  - When clicking the download link from PANGAEA, the web browser may attempt to open the large text files of several GB. A better way is to download the files directly using a tool like curl. However, PANGAEA stores some files on tape, so the system needs time to retrieve them. This requires first an initial download request that will fail. After waiting approximately one minute for the files to be fetched, the actual download request can be sent.

## Scripts
* `compute_statistics.py` computes the minimum, median, and maximum of the number of points and average point neighbor distance across all epochs

The expected folder structure for the data is as follows:

```
Trail_Valley_Creek
  |-- PermaSAR_TLS_201506_Site1.txt
  |-- PermaSAR_TLS_201506_Site2.txt
  |-- PermaSAR_TLS_201508_Site1.txt
  |-- ...
```