import os
import argparse
import json
import trimesh
import plyfile
import numpy as np
from tqdm import tqdm

from utils.pointcloud_format import FORMAT_XYZRGBSIC
from utils.io import FileFormat, write_pointcloud
from utils.pointcloud_creation import get_processing_order

parser = argparse.ArgumentParser(prog='3RScan - Point Cloud Creation by Mesh Sampling')
parser.add_argument('input_path', help='The root path of the dataset')
parser.add_argument('--output_folder', help='The folder into which the pointclouds should be written (defaults to [input_path]/pointclouds_sampled)')
parser.add_argument('--output_format', help='The format of the output point cloud', type=FileFormat, choices=[format.value for format in FileFormat], default=FileFormat.LAZ)
parser.add_argument('--exclusion_list', help='A list of scans to exclude for reconstruction (e.g., 00d42bef-778d-2ac6-848a-008ef6c19ad6)', nargs='*', type=str, default=[])
parser.add_argument('--inclusion_list', help='A list of scans to include (overwrites exclusion list)', nargs='+', type=str)
parser.add_argument('--sampling_density', help='The density with which the mesh should be sampled (number of points per square meter)', default=30000)


def sample_pointcloud(input_path, output_folder, output_filename, output_format, align_to_reference, change_labels, sampling_density):
	mesh_path = os.path.join(input_path, 'mesh.refined.v2.obj')
	label_mesh_path = os.path.join(input_path, 'labels.instances.annotated.v2.ply')

	if not os.path.exists(mesh_path) or not os.path.exists(label_mesh_path):
		return
	
	mesh = trimesh.load(mesh_path, process=False)
	mesh.apply_transform(align_to_reference)
	points, face_idx, colors = trimesh.sample.sample_surface(mesh, int(mesh.area * sampling_density), sample_color=True)
	vertices_for_sampled_points = mesh.faces[face_idx][:, 0]

	label_mesh = plyfile.PlyData.read(label_mesh_path)
	instances =  label_mesh['vertex']['globalId'][vertices_for_sampled_points]
	local_instances = label_mesh['vertex']['objectId'][vertices_for_sampled_points]
	classes = label_mesh['vertex']['RIO27'][vertices_for_sampled_points]

	changes = np.zeros(len(instances))
	if len(change_labels) > 0:
		change_indices = np.isin(local_instances, list(change_labels.keys()))
		instance_to_change = np.vectorize(change_labels.get)
		changes[change_indices] = instance_to_change(local_instances[change_indices])
	
	pointcloud = np.column_stack([points, colors[:, 0:3], classes, instances, changes])
	write_pointcloud(pointcloud, output_folder, output_filename, output_format, FORMAT_XYZRGBSIC)


def sample_pointclouds(input_path, output_folder, output_format, exclusion_list, inclusion_list, sampling_density):
	if not os.path.exists(input_path):
		return

	# dictionary that records for each scan the [reference (first epoch) name, output name, matrix for alignment to reference scan]
	scenes = {}
	with open(os.path.join(input_path, 'raw', '3RScan.json')) as json_file:
		data = json.load(json_file)
		for scene in data:
			reference_name = scene['reference']
			scenes[reference_name] = [reference_name, 'epoch_0', np.eye(4), {}]

			if scene['type'] == 'test':
				continue

			epoch_idx = 1
			for scan in scene['scans']:
				scan_name = scan['reference']
				if not 'transform' in scan:
					continue
				align_to_reference = np.array(scan['transform']).reshape((4,4)).T

				# extract changes. We use three change labels: 0 = None, 1 = rigid transform, 2 = nonrigid transform
				# removals can't be annotated (as the corresponding objects are not in the scene anymore)
				changes = {}
				for entry in scan['rigid']:
					changes[entry['instance_reference']] = 1
				for entry in scan['nonrigid']:
					changes[entry] = 2

				scenes[scan_name] = [reference_name, 'epoch_' + str(epoch_idx), align_to_reference, changes]
				epoch_idx += 1

	processing_order = get_processing_order(os.path.join(input_path, 'raw'), inclusion_list, exclusion_list)
	processing_order = [entry for entry in processing_order if not entry.name.endswith('.json')]

	if output_folder is None:
		output_folder = os.path.join(input_path, 'pointclouds_sampled')
	
	for entry in tqdm(processing_order):
		output_path = os.path.join(output_folder, scenes[entry.name][0])
		os.makedirs(output_path, exist_ok=True)
		sample_pointcloud(entry.resolve(), output_path, scenes[entry.name][1], output_format, scenes[entry.name][2], scenes[entry.name][3], sampling_density)


if __name__ == '__main__':
	args = parser.parse_args()
	sample_pointclouds(args.input_path, 
				 args.output_folder, 
				 args.output_format,
				 args.exclusion_list,
				 args.inclusion_list,
				 args.sampling_density)