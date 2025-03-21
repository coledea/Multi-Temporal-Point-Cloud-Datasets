"""Software License Agreement (BSD License)

Copyright (c) 2008, Willow Garage, Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution.
* Neither the name of Willow Garage, Inc. nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE."""
# Message conversion code adapted from: http://docs.ros.org/en/kinetic/api/ros_numpy/html/point__cloud2_8py_source.html

import numpy as np
from rosbags.rosbag1 import Reader

DUMMY_FIELD_PREFIX = '__'

# mappings between PointField types and numpy types
type_mappings = [(1, np.dtype('int8')), (2, np.dtype('uint8')), (3, np.dtype('int16')),
				  (4, np.dtype('uint16')), (5, np.dtype('int32')), (6, np.dtype('uint32')),
				  (7, np.dtype('float32')), (8, np.dtype('float64'))]
pftype_to_nptype = dict(type_mappings)
 
# sizes (in bytes) of PointField types
pftype_sizes = {1: 1, 2: 1, 3: 2, 4: 2, 5: 4, 6: 4, 7: 4, 8: 8}

def point_message_dtype_list(fields, point_step):
	offset = 0
	np_dtype_list = []
	for f in fields:
		while offset < f.offset:
			# might be extra padding between fields
			np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
			offset += 1
 
		dtype = pftype_to_nptype[f.datatype]
		if f.count != 1:
			dtype = np.dtype((dtype, f.count))
 
		np_dtype_list.append((f.name, dtype))
		offset += pftype_sizes[f.datatype] * f.count
 
	# might be extra padding between points
	while offset < point_step:
		np_dtype_list.append(('%s%d' % (DUMMY_FIELD_PREFIX, offset), np.uint8))
		offset += 1
		
	return np_dtype_list

def split_rgb_field(cloud_arr):
	rgb_arr = cloud_arr['rgb'].copy()
	rgb_arr.dtype = np.uint32
	r = np.asarray((rgb_arr >> 16) & 255, dtype=np.uint8)
	g = np.asarray((rgb_arr >> 8) & 255, dtype=np.uint8)
	b = np.asarray(rgb_arr & 255, dtype=np.uint8)   

	# create a new array, without rgb, but with r, g, and b fields
	new_dtype = []
	for field_name in cloud_arr.dtype.names:
		field_type, _ = cloud_arr.dtype.fields[field_name]
		if not field_name == 'rgb':
			new_dtype.append((field_name, field_type))
	new_dtype.append(('r', np.uint8))
	new_dtype.append(('g', np.uint8))
	new_dtype.append(('b', np.uint8))    
	new_cloud_arr = np.zeros(cloud_arr.shape, new_dtype)
	
	# fill in the new array
	for field_name in new_cloud_arr.dtype.names:
		if field_name == 'r':
			new_cloud_arr[field_name] = r
		elif field_name == 'g':
			new_cloud_arr[field_name] = g
		elif field_name == 'b':
			new_cloud_arr[field_name] = b
		else:
			new_cloud_arr[field_name] = cloud_arr[field_name]
	return new_cloud_arr


def pointcloud_from_point_message(message):
	dtype_list = point_message_dtype_list(message.fields, message.point_step)
	pc_array = np.frombuffer(message.data, dtype_list)
	pc_array = pc_array[[fname for fname, _type in dtype_list if not (fname[:len(DUMMY_FIELD_PREFIX)] == DUMMY_FIELD_PREFIX)]]
	
	if 'rgb' in pc_array.dtype.names:
		pc_array = split_rgb_field(pc_array)

	columns = [pc_array['x'], pc_array['y'], pc_array['z']]
	if 'intensity' in pc_array.dtype.names:
		columns.append(pc_array['intensity'])
	if 'r' in pc_array.dtype.names:
		columns.extend([pc_array['r'].astype(np.float32), pc_array['g'].astype(np.float32), pc_array['b'].astype(np.float32)])

	return np.column_stack(columns)

# Extracts all poses and their timestamps from a rosbag
def extract_poses(rosbag_path, typestore, topic_name):
	timestamps = []
	poses = []
	with Reader(rosbag_path) as reader:
		pose_connections = [x for x in reader.connections if x.topic == topic_name]
		for connection, timestamp, rawdata in reader.messages(connections=pose_connections):
			pose = typestore.deserialize_ros1(rawdata, connection.msgtype)
			if connection.msgtype == 'nav_msgs/msg/Odometry':
				pose = pose.pose.pose
			orientation_raw = pose.orientation
			position_raw = pose.position
			timestamps.append(timestamp)
			poses.append(np.array([position_raw.x, position_raw.y, position_raw.z, orientation_raw.x, orientation_raw.y, orientation_raw.z, orientation_raw.w]))
	return [np.array(timestamps), np.array(poses)]