import os
import argparse
import yaml
import subprocess
from tqdm import tqdm

parser = argparse.ArgumentParser(prog='Script for processing multiple datasets')
parser.add_argument('config_path', help='Path to a configuration YAML, specifying how to process which datasets')


def placeholder_replacement(input, dataset_name, dataset_root, has_create_pointcloud_script):
    result = input.replace('${{dataset_name}}', dataset_name)
    result = result.replace('${{dataset_root}}', dataset_root)
    result = result.replace('${{pointclouds}}', 'pointclouds' if has_create_pointcloud_script else '')
    return result

def get_command_for_processing_step(step, dataset_name, dataset_root, has_create_pointcloud_script):
    script_name = step['script']
    script_path_parts = ['datasets', dataset_name, script_name]
    script_path = os.path.join(*script_path_parts) + '.py'
    if not os.path.exists(script_path):
        return None

    command_parts = ['python -m', '.'.join(script_path_parts)]
    for argument in step['arguments']:
        argument_value = step['arguments'][argument]
        if isinstance(argument_value, str):
            argument_value = placeholder_replacement(argument_value, 
                                                    dataset_name, 
                                                    dataset_root, 
                                                    has_create_pointcloud_script)
        else:
            argument_value = str(argument_value)
            
        if argument.startswith('--'):
            command_parts.append(argument)
        command_parts.append(argument_value)
    return ' '.join(command_parts)


if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.config_path, 'r') as config_file:
        config = list(yaml.safe_load_all(config_file))
        default_config = None if len(config) == 1 else config[0]
        datasets = config[0] if len(config) == 1 else config[1]

    processing_order = []
    for dataset_name in datasets:
        dataset = datasets[dataset_name]
        if (dataset != 'default') and ('dataset_root' in dataset):
            dataset_root = dataset['dataset_root']
        else:
            if default_config is None:
                print('Expected default configuration, but none was specified')
                exit()
            dataset_root = default_config['dataset_root']
        
        dataset_root = dataset_root.replace('${{dataset_name}}', dataset_name)
        has_create_pointcloud_script = os.path.exists(os.path.join('datasets', dataset_name, 'create_pointclouds.py'))

        processing_order.append({'name' : dataset_name, 'scripts' : []})
        config = default_config['processing_steps'] if dataset == 'default' else datasets[dataset_name]['processing_steps']
        for step in config:
            command = get_command_for_processing_step(step, dataset_name, dataset_root, has_create_pointcloud_script)
            if command is not None:
                processing_order[-1]['scripts'].append(command)

    for dataset in tqdm(processing_order):
        tqdm.write('Processing ' + dataset['name'])
        for script in dataset['scripts']:
            subprocess.call(script)

        


         