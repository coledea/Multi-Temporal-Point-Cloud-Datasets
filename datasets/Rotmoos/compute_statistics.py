import os
import argparse
from utils.evaluation import Statistics, EvaluationConfig, compute_dataset_statistics


parser = argparse.ArgumentParser(prog='Rotmoos - Dataset Statistics Computation')
parser.add_argument('input_path', help='The root folder of the dataset')
parser.add_argument('--output_log', help='Path of a textfile where the results should be written to', default=None)


def compute_statistics(input_folder, output_log_path, leave_progress_bar=False):
	if not os.path.exists(input_folder):
		return
	
	epochs = [os.path.join(input_folder, '2015_river_erosion_photogrammetry', '2015_UAV_fixedwing_pointcloud.txt'), 
			os.path.join(input_folder, '2021_Rotmoostal_colorized_ULS.laz'),
			os.path.join(input_folder, '201906_Rotmoostal_ULS.laz'),
			os.path.join(input_folder, '20150709_Rotmoos_glaciers_TLS_UTM32N.txt'),
			os.path.join(input_folder, '2022_rotmoos_ULS', '2022_Rotmoostal_flight1_colorized_ULS.laz'),
			os.path.join(input_folder, '2022_rotmoos_ULS', '2022_Rotmoostal_flight2_colorized_ULS.laz')]
	
	processing_order = [[[epoch]] for epoch in epochs if os.path.exists(epoch)]
	config = EvaluationConfig(statistics_to_compute=[Statistics.NUM_POINTS, Statistics.AVG_DISTANCE],
						   output_log_path=output_log_path,
						   leave_progress_bar=leave_progress_bar,
						   position_offset=[-654251, -5189692, -2313],
						   txt_has_header=True)
	
	compute_dataset_statistics(processing_order, config)


if __name__ == '__main__':
	args = parser.parse_args()
	compute_statistics(args.input_path, args.output_log, leave_progress_bar=True)