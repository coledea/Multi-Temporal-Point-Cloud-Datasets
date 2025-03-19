import os
import argparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(prog='KTH Longterm - Point Cloud Renaming')
parser.add_argument('input_folder', help='Path of the root dataset folder (containing the folders for each scanning day)')

if __name__ == '__main__':
    args = parser.parse_args()

    for day in os.scandir(args.input_folder):
        if not day.is_dir() or not day.name.startswith('2014'):
            continue
        for run in os.scandir(day.path):
            for room in os.scandir(run.path):
                xml_path = os.path.join(room.path, 'room.xml')
                xml_root = ET.parse(xml_path).getroot()
                waypoint_name = xml_root.find('RoomStringId').text
                os.rename(os.path.join(room.path, 'complete_cloud.pcd'), os.path.join(room.path, waypoint_name + '.pcd'))