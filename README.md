# A Survey of Publicly Available Multi-Temporal Point Cloud Datasets

![](./images/overview.png "Overview of surveyed datasets")

This repository contains code for processing the datasets we surveyed in our paper (currently under review).
Additionally, for each dataset, possible issues and pecularities are listed in the corresponding README file. For more information on the characteristics of the different datasets, please refer to our paper and the accompanying [website](https://hpicgs.github.io/multi-temporal-point-cloud-datasets-survey/). The website facilitates improved exploration of the available datasets via sorting and filtering functionality.

## Contents of this Repository
```
|-- config           # Configuration files for the pointcloud_processing.py script
|-- datasets         # Scripts + README for each dataset
|-- images           # One thumbnail image for each datasets (used in the README files)
|-- requirements     # Lists of Python dependencies for processing the different datasets
|-- utils            # Common functions used by multiple of the dataset-specific scripts
    |-- evaluation.py             # Computing statistics and printing the results
    |-- io.py                     # Reading and writing point clouds
    |-- pointcloud_creation.py    # Creating unified point clouds from some input data (e.g., RGBD images)
    |-- pointcloud_format.py      # Specification of possible point cloud formats used for writing
    |-- pointcloud_processing.py  # Filtering and transformation of point clouds
    |-- rosbags.py                # Functionalities for extracting data from ROS bagfiles
    |-- tile_writer.py            # A tile-based writer for large point clouds
|-- process_datasets.py           # A master script for processing multiple datasets in row
```

The code in this repository is written in Python and is not optimized for performance (as we had to run it only once). Nevertheless, it might serve as a useful starting point for working with the respective datasets. For each dataset, at least one script is provided to compute various statistics, such as the average number of points, point spacings, or the number of partial epochs. For datasets that have to be transformed into a unified point cloud first, a corresponding script is provided as well. Additionally, some dataset-specific scripts are available.

## Usage Instructions

### Installation
We used **Python 3.10**. You can install the required dependencies by executing

`pip install -r requirements/requirements-all.txt`

If you do not want to install all dependencies (which include some that are only required for a single dataset), you can also install only the base dependencies (`requirements/requirements-base.txt`) plus any optional dependencies for specific datasets.

### Dataset-specific Scripts
Please start each script as a module from the root folder in order for the imports to be resolved correctly.
Example:  `python -m datasets.3DCD.compute_statistics path/to/dataset`

### Master Script
This script facilitate the processing of multiple datasets according to the provided YAML configuration file. 
We provide one configuration file for processing all datasets with (nearly) all available scripts (i.e., point cloud creation and statistics computation):

`python process_datasets.py config/config_all.yaml`

Please be aware that this may take very long.
We also provide an additional example configuration file that you can adapt to your needs.