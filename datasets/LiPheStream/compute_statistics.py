import os
import argparse
import tempfile
import shutil
from zipfile import ZipFile
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='LiPheStream - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def extract_archive(archive_path, target_folder):
	try:
		with ZipFile(archive_path) as file:
			with tempfile.TemporaryDirectory() as temp_dir:
				file.extractall(temp_dir)

				os.makedirs(target_folder, exist_ok=True)
				for root, _, files in os.walk(temp_dir):
					for file in files:
						shutil.copy(os.path.join(root, file), os.path.join(target_folder, file))

		os.remove(archive_path)
		return True
	except:
		return False
	

def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	scenes = {}
	for folder in ['LiPheStream', 'LiPheStream_Winter']:
		folder_path = os.path.join(input_folder, folder)
		if not os.path.exists(folder_path):
			continue

		for species in os.scandir(folder_path):
			for quality in os.scandir(species.path):
				for tree in os.scandir(quality.path):
					# If still an archive: extract first
					if tree.name.endswith('.zip'):
						target_folder = os.path.join(quality.path, tree.name.split('.')[0])
						if extract_archive(tree.path, target_folder) == False:
							continue
						scene_name = tree.name.split('.')[0].split('_')[0]
					else:
						target_folder = tree.path
						scene_name = tree.name.split('_')[0]

					if scene_name not in scenes:
						scenes[scene_name] = []
					for scan in sorted(os.scandir(target_folder), key=lambda e: e.name):
						scenes[scene_name].append([scan.path])

	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE, Statistics.PARTIAL_EPOCHS],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar,
						   remove_duplicates=True)
	
	compute_dataset_statistics(list(scenes.values()),config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)