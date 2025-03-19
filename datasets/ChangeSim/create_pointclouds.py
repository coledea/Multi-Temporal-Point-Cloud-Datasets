import os
import cv2
import argparse
import numpy as np
from tqdm import tqdm
from utils.pointcloud_format import FORMAT_XYZRGBS
from utils.io import FileFormat, write_pointcloud
from utils.pointcloud_creation import RGBDReconstruction, get_pose_matrix_from_pose


parser = argparse.ArgumentParser(prog='ChangeSim - Point Cloud Creation')
parser.add_argument('input_path', help='The root path of ChangeSim')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of filepaths to exclude for reconstruction. Do not prepend the root directory of ChangeSim, i.e., write Query_Seq_Train/Warehouse_6/Seq_0', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of filepaths to include (overwrites exclusion list)', nargs='+', type=str)


def extract_pointcloud(input_path, output_path, output_format):
	poses = np.loadtxt(os.path.join(input_path, 'trajectory.txt'), delimiter=' ', usecols=(0,1,2,3,4,5,6,7))
	intrinsics = np.array([[320, 0, 320], [0, 320, 240], [0, 0, 1]])
	resolution = [640, 480]
	reconstruction = RGBDReconstruction(intrinsics, resolution, map_color_to_segmentation_id=True, depth_threshold=40.0)

	for idx, raw_pose in tqdm(enumerate(poses), total=len(poses), leave=False):
		filename = str(idx)

		depth_im_path = os.path.join(input_path, 'depth', filename + '.png')
		depth_image = (cv2.imread(depth_im_path, -1).astype(np.float32) / 255.0) * 50.0

		color_im_path = os.path.join(input_path, 'rgb', filename + '.png')
		color_image = cv2.cvtColor(cv2.imread(color_im_path), cv2.COLOR_BGR2RGB)

		seg_im_path = os.path.join(input_path, 'semantic_segmentation', filename + '.png')
		seg_image = cv2.cvtColor(cv2.imread(seg_im_path), cv2.COLOR_BGR2RGB)

		pose = get_pose_matrix_from_pose(raw_pose[1:])

		reconstruction.add_image(depth_image, color_image, pose, segmentation=seg_image)

	write_pointcloud(reconstruction.get_result(), output_path, 'rgbd_reconstruction', output_format, PointcloudFormat.XYZRGBL)


def extract_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list):
	if not os.path.exists(input_path):
		return
	
	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds')
	
	if inclusion_list is not None:
		for entry in tqdm(inclusion_list):
			extract_pointcloud(os.path.join(input_path, entry), output_folder, output_format)
	else:
		exclusion_list = [os.path.join(input_path, entry) for entry in exclusion_list]

		processing_order = []

		for split in os.scandir(input_path):
			if not split.is_dir():
				continue
			for scene in os.scandir(split.path):
				for run in os.scandir(scene.path):
					if run.path not in exclusion_list:
						processing_order.append(run.path)

		for entry in tqdm(processing_order):
			extract_pointcloud(entry, output_folder, output_format)


if __name__ == '__main__':
	args = parser.parse_args()
	extract_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format,
				 args.exclusion_list,
				 args.inclusion_list)