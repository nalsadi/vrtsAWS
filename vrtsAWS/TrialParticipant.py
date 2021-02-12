from Enums import PositionData, OrientationData, OrientationType, Position, ParticipantDirection, VelocityData
from ParticipantMoment import ParticipantMoment
from Enums import CheckingState
import Globals

import scipy.signal
import operator
import math
import time


MEMO_INDEX_BEFORE_LAST_ENTER_ROAD = "MEMO_INDEX_BEFORE_LAST_ENTER_ROAD"
MEMO_INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD = "MEMO_INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD"

ROAD_START_Z = 0.0
ROAD_MIDDLE_Z = Globals.roadWidth / 2.0

# No idea what this value is based on, specifically
FAST_HUMAN_RUN_SPEED = 8.0 
# TODO: clean up these fixes?


class TrialParticipant():
	
	def __init__(self, participant_position_data, participant_orientation_data):
		self._position_data = participant_position_data
		self._orientation_data = participant_orientation_data
		self._participant_dict = {}  # time -> ParticipantMoment
		
		self._objectify() # Make objects from raw data
		
		# Memoized participant data
		self.__memoizedData = {}
		self.__memoizedData[MEMO_INDEX_BEFORE_LAST_ENTER_ROAD] = None
		self.__memoizedData[MEMO_INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD] = None
		
		# Used in velocity calculations
		self._build_participant_velocity_data_dict()  # time -> velocity
		
#		self._repair_velocity_data_by_identifying_abnormal_frame_times()
		self._repair_velocity_data_with_savitzky_golay_filter()
		self._write_velocity_data_to_file()
	
	
	def __str__(self):
		''' Print out this object '''
		p_string = ""
		p_string = "# position points = %s, # orientation points = %s" % (len(self._position_data), len(self._orientation_data))
		return p_string
	
	
	def _objectify(self):
		''' Create a dictionary that allows us to look up participant data by time '''
		
		# Create ParticipantMoment objects for all data points
		print("In TRIAL PARTICP: ",len(self._position_data))
		for i in range(len(self._position_data)):
			t = self._position_data[i][PositionData.TIME]
			ori_t = self._orientation_data[i][OrientationData.TIME]
			
			#sanity check
			if t != ori_t:
				print "ERROR MAKING PARTICIPANT DATA, SOMETHING IS NOT ALIGNED"
			
			pos = self._position_data[i][PositionData.POSITION]
			ori = self._orientation_data[i][OrientationData.ORIENTATION]
			
			
			checking_state = self._get_checking_state(ori)
			moment = ParticipantMoment(t, i, pos, ori, checking_state)
			
			self._participant_dict[t] = moment

				
	def _build_participant_velocity_data_dict(self):
		'''Create a dictionary of the participant's velocity at the given t'''

		#TODO: do we want to calculate velocity as change in z, or change in position?

		self._participant_velocity_data = {}  # time -> velocity
		prev_z = None
		prev_t = None
		
		# Build the velocity data
		for i in range(len(self._position_data)):
			
			t = self._position_data[i][PositionData.TIME]
			current_moment = self._participant_dict[t]
			current_z = current_moment.get_z_position()

			if not prev_z:
				v = 0.0				
			else:
				delta_d = current_z - prev_z
				delta_t = t - prev_t
				v = delta_d / delta_t
				
			prev_z = current_z
			prev_t = t

			self._participant_velocity_data[t] = v
		
		
	def _write_velocity_data_to_file(self):
		''' writes the participant_velocity_data dict to a file, for debugging '''
		with open('C:\\vr\\vr3\\_master_data\\velocity_data.txt', 'w') as file:
			file.write("t;v\n")
			for t in sorted(self._participant_velocity_data.keys()):
				v = self._participant_velocity_data[t]
				file.write("%.8f;%.8f\n" % (t,v))
		file.close()
		
		
	def _repair_velocity_data_with_savitzky_golay_filter(self, window_length=25, polynomial_order=3):
		""" Uses the Savitzky-Golay filter to process the velocities """
		
		# get a list of the velocities, sorted by time, and apply the Savitzky-Golay filter
		sorted_velocities = [x[1] for x in sorted(self._participant_velocity_data.items(), key=operator.itemgetter(0))]
		
		# check that there is enough data to apply the filter
		if len(sorted_velocities) < window_length:
			print "\n*** TrialParticipant._repair_velocity_data_by_signal_smoothing: not enough velocity data to apply S-G filter."
			print "\t--smoothing will not be applied to this trial\n"
			return
		
		# A note on the parameters below (sorted_velocities, m, n):
		# You're using a polynomial order of N to approximate M data points
		# Generally, N is chosen considerably smaller than M to achieve some smoothing
		# (if they're too close, there's very little smoothing going on)
		# The smaller N compared to M, the more smoothing takes place
		# There don't appear to be any practical guidelines, it's more about seeing what works with yr data
		# (but often, an N of 3,4,5 and an M much higher)
		# See: http://dsp.stackexchange.com/questions/15643/savitzky-golay-filter-parameters
		filtered_velocities = scipy.signal.savgol_filter(sorted_velocities, window_length, polynomial_order)
		
		# loop through the times and update the velocity dictionary with the filtered results
		sorted_times = sorted(self._participant_velocity_data.keys())
		for i, val in enumerate(sorted_times):
			self._participant_velocity_data[val] = filtered_velocities[i]
		
		
	def _repair_velocity_data_by_identifying_abnormal_frame_times(self):
		''' 
		identifies any participant velocity updates outside of a given time 
		tolerance window and repairs them 
		'''
		
		prev_t = 0.0		
		# run through the sorted participant velocity data
		for t, v in sorted(self._participant_velocity_data.iteritems()):
			delta_t = t - prev_t
			if self._is_abnormal_frame_time(delta_t):
				print "*** delta_t outside tolerance (%.5f); repairing..." % delta_t
				repaired_v = self._repair_data_point((t,v))
				self._participant_velocity_data[t] = repaired_v
			prev_t = t
		
		
	def _is_abnormal_frame_time(self, delta_t):
		#TODO: if the framerate of the system changes, these will need to be updated
		if not .01577 <= delta_t <= .01757:  # mike determined these cutoffs through stats analysis - email Feb18/15
			return True
		return False
		
		
	def _repair_data_point(self, data_point):
		''' 
		repairs a given data point by setting its velocity to the mean of 
		the velocity of the surrounding points 
		'''

		sorted_velocities = sorted(self._participant_velocity_data.items(), key=operator.itemgetter(0))
		
		num_pts_each_side = 3
		surrounding_points = []
		index = sorted_velocities.index(data_point)
		prev_t, prev_v = sorted_velocities[index-num_pts_each_side-1]
		
		for t, v in sorted_velocities[index-num_pts_each_side:index+num_pts_each_side+1]:
			delta_t = t - prev_t
			prev_t = t
			if self._is_abnormal_frame_time(delta_t) or abs(t - data_point[0]) < 0.00001:
				continue  # make sure it's valid and not the frame we're currently repairing
			surrounding_points.append((t, v))
		
		# get the mean velocity of those surrounding points
		if len(surrounding_points) > 0:
			total_velocity = 0
			for t, v in surrounding_points:
				total_velocity += v
			mean_velocity = total_velocity / len(surrounding_points)
			print "\t-->velocity was %.5f and was reset to %.5f" % (data_point[1], mean_velocity)
			return mean_velocity
			
		print "\tcouldn't repair! (not enough valid surrounding data points)"
		return data_point[1]
		
	
	
	def get_participant_dict(self):
		return self._participant_dict
		
		
	def get_position_data(self):
		return self._position_data
	
	
	def get_orientation_data(self):
		return self._orientation_data
		
		
	def get_yaw(self, t):
		try:
			moment = self._participant_dict[t]
			yaw = moment.get_yaw()
		except KeyError:
			yaw = None
		return yaw
		
		
	def get_pitch(self, t):
		try:
			moment = self._participant_dict[t]
			pitch = moment.get_pitch()
		except KeyError:
			pitch = None
		return pitch
		
		
	def get_x_position(self, t):
		''' Return the participant's x position at time t '''
		try:
			moment = self._participant_dict[t]
			position = moment.get_x_position()
		except KeyError:
			position = None
			
		return position
		
		
	def get_z_position(self, t):
		''' Return the participant's z position at time t '''
		try:
			moment = self._participant_dict[t]
			position = moment.get_z_position()
		except KeyError:
			position = None
			
		return position
	
	
	def get_position(self, t):
		''' Return the participant's position at time t '''
		try:
			moment = self._participant_dict[t]
			position = moment.get_position()
		except KeyError:
			position = None
			
		return position


	def get_velocity(self,t):
		'''Returns the velocity at time t'''
		v = self._participant_velocity_data[t]
		return v


	def get_momentary_velocity(self, t):
		''' Return the momentary velocity at t '''
		
		cur_moment = self._participant_dict[t]
		prev_moment = self.get_prev_moment(t)
		if not prev_moment:
			# This is the first data point
			return None
		
		# calculate the difference in position/time from last moment to this moment
		d_delta_z = cur_moment.get_z_position() - prev_moment.get_z_position()
		t_delta = cur_moment.get_time() - prev_moment.get_time()
		if t_delta == 0:
			return None
		velocity_z = d_delta_z / t_delta
		return velocity_z


	def get_min_velocity(self, enter_time, exit_time):
		''' Return the minimum velocity between enter_time and exit_time '''

		#TODO: should be infinity
		min_vel = 10000000
		enter_index = self._participant_dict[enter_time].get_index()
		exit_index = self._participant_dict[exit_time].get_index()

		# get min velocity in car path
		for i in range(enter_index, exit_index):
			t = self._position_data[i][PositionData.TIME]
			v = self._participant_velocity_data[t]
			
			# Check that this velocity is reasonable
			if v < -FAST_HUMAN_RUN_SPEED:
				print "WARNING: That velocity (", v, ") is ridiculous."
				print "Something probably went wrong; disregarding this velocity"
			else:
				if v < min_vel:
					min_vel = v
		
		return min_vel


	def get_max_velocity(self, enter_time, exit_time):
		''' Return the maximum velocity between enter_time and exit_time '''
		
		max_vel = -1
		enter_index = self._participant_dict[enter_time].get_index()
		exit_index = self._participant_dict[exit_time].get_index()
		
		for i in range(enter_index, exit_index):
			t = self._position_data[i][PositionData.TIME]
			v = self._participant_velocity_data[t]
			
			# Check if the speed is attainable (check required b/c of a glitch in the system)
			if v > FAST_HUMAN_RUN_SPEED:
				print "WARNING: That velocity (", v, ") is ridiculous."
				print "Something probably went wrong; disregarding this velocity"
			else:
				if v > max_vel:
					max_vel = v
		
		return max_vel
		
		
	def get_mean_velocity(self, enter_time, exit_time):
		''' Return the average velocity between enter_time and exit_time '''
		
		total_vel = 0.0
		enter_index = self._participant_dict[enter_time].get_index()
		exit_index = self._participant_dict[exit_time].get_index()
		total_points = exit_index - enter_index + 1
		
		for i in range(enter_index, exit_index):
			t = self._position_data[i][PositionData.TIME]
			v = self._participant_velocity_data[t]
			if math.fabs(v) > FAST_HUMAN_RUN_SPEED:
				print "WARNING: That velocity (", v, ") is ridiculous."
				print "Something probably went wrong; disregarding this velocity"
			else:
				total_vel += v
			
		mean_vel =  float(total_vel) / total_points
		return mean_vel


	def get_moment(self, t):
		''' Return the ParticipantMoment object at time t '''
		return self._participant_dict[t]


	def get_prev_moment(self, t):
		''' Return the moment before the moment at t '''
		time_list = sorted(self._participant_dict.keys())
		cur_index = time_list.index(t)
		if cur_index == 0:
			return None
		prev_time = time_list[cur_index - 1]
		if prev_time in self._participant_dict:
			return self._participant_dict[prev_time]
		
		# Return none if there is no moment before this one (i.e. this is the first data point)
		return None
		
		
	def get_next_moment(self,t):
		'''Return the moment after the moment at t'''
		time_list = sorted(self._participant_dict.keys())
		curr_index = time_list.index(t)
		if (curr_index + 1) < len(time_list):
			next_time = time_list[curr_index + 1]
			if next_time in self._participant_dict:
				return self._participant_dict[next_time]
		
		# Return none if there is no moment after this one (i.e. this is the last data point)
		return


	def get_first_moment(self):
		time_list = sorted(self._participant_dict.keys())
		return self._participant_dict[time_list[0]]
		
		
	def get_last_moment(self):
		time_list = sorted(self._participant_dict.keys())
		return self._participant_dict[time_list[-1]]


	def get_direction(self, t):
		''' 
		Return the direction the participant is moving at time t by examining
		the difference between the previous point and the current point.
		'''
		direction = None
		prev_moment = self.get_prev_moment(t)
		if not prev_moment:
			return None
		
		prev_z_position = prev_moment.get_z_position()
		z_position = self._participant_dict[t].get_z_position()
		
		# If the participant isn't moving in the z-direction, don't change their direction (think of it as "last known direction")
		if z_position > prev_z_position:
			direction = ParticipantDirection.FORWARD
		elif z_position < prev_z_position:
			direction = ParticipantDirection.BACKWARD

		return direction


	def get_moment_last_entered_road(self):
		''' Return the moment the participant last entered the road '''
		if not self.__memoizedData[MEMO_INDEX_BEFORE_LAST_ENTER_ROAD]:
			self.__memoizedData[MEMO_INDEX_BEFORE_LAST_ENTER_ROAD] = self._get_moment_last_crossed_z_value(ROAD_START_Z)
		
#		print "MOMENT LAST ENTERED ROAD = ", self.__memoizedData[MEMO_INDEX_BEFORE_LAST_ENTER_ROAD]
		return self.__memoizedData[MEMO_INDEX_BEFORE_LAST_ENTER_ROAD]


	def get_moment_last_crossed_middle_of_road(self):
		''' Return the moment the participant last entered the middle of the road '''
		if not self.__memoizedData[MEMO_INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD]:
			self.__memoizedData[MEMO_INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD] = self._get_moment_last_crossed_z_value(ROAD_MIDDLE_Z)
		
		return self.__memoizedData[MEMO_INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD]


	def _get_moment_last_crossed_z_value(self, z_value):
		''' Get the moment the participant last crossed the z value, moving forward. '''

		# Loop backwards and find the last time they crossed z
		for i in range((len(self._position_data)-1),-1,-1):
			current_z =  self._position_data[i][PositionData.POSITION][Position.Z_POS]

			# To make sure the participant crossed the z-value, we have to check 
			# that the previous point is 
			if i-1 < 0:
				return None
				
			prev_z = self._position_data[i-1][PositionData.POSITION][Position.Z_POS]
			if (current_z > z_value) and (prev_z <= z_value):
				moment = self._participant_dict[self._position_data[i][PositionData.TIME]]
				return moment
		
		# There was no time the participant entered the road
		return None


	def _get_checking_state(self, ori):
		''' get whether or not the participant is checking at the given moment '''
		
		current_yaw = ori[OrientationType.YAW] #moment.get_yaw()
		current_pitch = ori[OrientationType.PITCH] #moment.get_pitch()
		checking_state = None
		
		PARTIAL_CHECK_ANGLE_RIGHT = Globals.partialCheckAngle
		FULL_CHECK_ANGLE_RIGHT = Globals.fullCheckAngle
		PARTIAL_CHECK_ANGLE_LEFT = -Globals.partialCheckAngle
		FULL_CHECK_ANGLE_LEFT = -Globals.fullCheckAngle
		MAX_FULL_CHECK_ANGLE_LEFT = -180 + FULL_CHECK_ANGLE_LEFT
		MAX_PARTIAL_CHECK_ANGLE_LEFT = -180 + PARTIAL_CHECK_ANGLE_LEFT
		MAX_FULL_CHECK_ANGLE_RIGHT = 180 - FULL_CHECK_ANGLE_RIGHT
		MAX_PARTIAL_CHECK_ANGLE_RIGHT = 180 - PARTIAL_CHECK_ANGLE_RIGHT
		
		#print "PC_R: %s, FC_R: %s" % (PARTIAL_CHECK_ANGLE_RIGHT, FULL_CHECK_ANGLE_RIGHT)
		
		if abs(current_pitch) >= Globals.checkMaxAnglePitch:
			checking_state = CheckingState.NO_CHECKING		
		elif (0 >= current_yaw > PARTIAL_CHECK_ANGLE_LEFT) and (0 <= current_yaw < PARTIAL_CHECK_ANGLE_RIGHT):
			checking_state = CheckingState.NO_CHECKING
		elif (PARTIAL_CHECK_ANGLE_LEFT >= current_yaw > FULL_CHECK_ANGLE_LEFT):
			checking_state = CheckingState.PARTIAL_CHECKING_LEFT
		elif (PARTIAL_CHECK_ANGLE_RIGHT <= current_yaw < FULL_CHECK_ANGLE_RIGHT):
			checking_state = CheckingState.PARTIAL_CHECKING_RIGHT
		elif (FULL_CHECK_ANGLE_LEFT >= current_yaw > MAX_FULL_CHECK_ANGLE_LEFT):
			checking_state = CheckingState.FULL_CHECKING_LEFT
		elif (FULL_CHECK_ANGLE_RIGHT <= current_yaw < MAX_FULL_CHECK_ANGLE_RIGHT):
			checking_state = CheckingState.FULL_CHECKING_RIGHT
		elif (MAX_FULL_CHECK_ANGLE_LEFT >= current_yaw > MAX_PARTIAL_CHECK_ANGLE_LEFT):
			checking_state = CheckingState.PARTIAL_CHECKING_LEFT
		elif (MAX_FULL_CHECK_ANGLE_RIGHT <= current_yaw < MAX_PARTIAL_CHECK_ANGLE_RIGHT):
			checking_state = CheckingState.PARTIAL_CHECKING_RIGHT
		else:
			checking_state = CheckingState.NO_CHECKING
			
		#print "yaw: %s state: %s" %(current_yaw, CheckingState.toStr(checking_state))

		return checking_state