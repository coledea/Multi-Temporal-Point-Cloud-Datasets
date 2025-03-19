import os
import argparse
import csv
import ssl
import urllib.request
from tqdm import tqdm

parser = argparse.ArgumentParser(prog='KTH Longterm - Dataset Downloader')
parser.add_argument('download_paths', help='Path to the "download_paths.csv", containing the source and target paths of the files to download')
parser.add_argument('output_folder', help='The folder into which the files should be downloaded')

if __name__ == '__main__':
    args = parser.parse_args()

    # The certificate of the website has expired. We ignore it.
    ssl._create_default_https_context = ssl._create_unverified_context

    with open(args.download_paths) as csvfile:
        reader = csv.reader(csvfile)
        for row in tqdm(list(reader)):
            output_path = os.path.join(args.output_folder, row[1])
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            urllib.request.urlretrieve(row[0], output_path)

    