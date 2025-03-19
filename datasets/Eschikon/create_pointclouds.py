import os
import argparse
import matlab.engine
import numpy as np
from tqdm import tqdm
from utils.pointcloud_format import FORMAT_XYZRGBS
from utils.io import write_pointcloud, FileFormat

parser = argparse.ArgumentParser(prog='Eschikon - Point Cloud Conversion')
parser.add_argument('input_path', help='The root path of the Eschikon dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/converted_pointclouds)', type=str)
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)


def create_pointclouds(input_path, output_folder, file_format, leave_progress_bar=False):
	if not os.path.exists(input_path):
		return
	
	eng = matlab.engine.start_matlab()

	# add path to the MeasurementPointcloud definition
	eng.addpath(input_path)

	# create output directories for the 30 cultivation boxes
	if output_folder is None:
		output_folder = os.path.join(input_path, 'converted_pointclouds')

	for i in range(30):
		folder_path = os.path.join(output_folder, 'Box_' + str(i+1))
		os.makedirs(folder_path, exist_ok=True)

	pointcloud_files = os.listdir(os.path.join(input_path, 'pointclouds'))
	pointcloud_files = sorted(pointcloud_files, key=lambda x: int(x.split('_')[2].split('.')[0]))   # sort according to epoch number

	for idx, pointcloud_path in tqdm(enumerate(pointcloud_files), leave=leave_progress_bar, total=len(pointcloud_files)):
		data = eng.load(os.path.join(input_path, 'pointclouds', pointcloud_path))
		for entry in list(data.values())[0]:
			box = int(eng.getfield(entry, "BoxNumber")) 
			xyz = np.asarray(eng.getfield(entry, "Location"))
			rgb = (np.asarray(eng.getfield(entry, "Color")) * 255).astype(int)
			label  = np.asarray(eng.getfield(entry, "Label"))

			pointcloud = np.hstack([xyz, rgb, label])
			output_path = os.path.join(output_folder, f'Box_{box}')
			write_pointcloud(pointcloud, output_path, f'epoch_{idx}', file_format, FORMAT_XYZRGBS)

			# would also be available:
			# infrared = np.asarray(eng.getfield(entry, "IRIntensity"))
			# ndvi = np.asarray(eng.getfield(entry, "NDVI"))

			# this index is not correct in all cases:
			# index = int(eng.getfield(entry, "DataSet"))   
			

if __name__ == '__main__':
	args = parser.parse_args()
	create_pointclouds(args.input_path, args.output_folder, args.output_format, leave_progress_bar=True)