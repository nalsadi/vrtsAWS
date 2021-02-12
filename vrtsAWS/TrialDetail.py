from Enums import TrialData, Direction, ParticipantDirection, CheckingState, PercentChecking, TrialResult, Intervention
from TrialParticipant import TrialParticipant
import Globals
from TrialCars import TrialCars
from PathDetail import PathDetail
from GapDetail import GapDetail

ROAD_START_Z_VALUE = 0.0
ROAD_MIDDLE_Z_VALUE = Globals.roadWidth / 2.0
ROAD_END_Z_VALUE = Globals.roadWidth
BETWEEN_CAR_PATHS_CLOSE_Z = Globals.closeLaneCenterZ + 1.0 #this is the maximum width of our largest cars. May need to change if cars change.
BETWEEN_CAR_PATHS_FAR_Z = Globals.farLaneCenterZ - 1.0

MEMO_INDEX_BEFORE_LAST_ENTER_ROAD = "MEMO_INDEX_BEFORE_LAST_ENTER_ROAD"


class TrialDetail:
	''' Store information about a trial from the raw data '''
	
	def __str__(self):
		td_string = "\nparticipant: %s\n" % self._participant
		td_string += "lfc_data: %s\n" % self._left_facing_car_data
		td_string += "rfc_data: %s" % self._right_facing_car_data
		return td_string
	
	def __init__(self, trial_data, trial_car_bounding_box_data):
		self._trial_data = trial_data
		self._participant = TrialParticipant(self._trial_data[TrialData.PARTICIPANT_POSITION], self._trial_data[TrialData.PARTICIPANT_ORIENTATION])
		
		#
		self._intervention_cause = self._trial_data[TrialData.INTERVENTION]
		self._right_facing_car_data = TrialCars(self._trial_data[TrialData.RIGHT_FACING_CAR_DATA],trial_car_bounding_box_data, Direction.RIGHT)
		try:
			self._left_facing_car_data  = TrialCars(self._trial_data[TrialData.LEFT_FACING_CAR_DATA], trial_car_bounding_box_data, Direction.LEFT)
		except IndexError:
			# Old trials didn't have LFC data.. dumdeedumdum
			self._left_facing_car_data  = TrialCars([], trial_car_bounding_box_data, Direction.LEFT)
		
		self._closest_car_dict = {} # t -> TrialCar
		self._car_path_details = [] # List of PathDetail objects with enter and exit times
		self._road_details = []     # List of PathDetail objects with enter and exit times
		self._between_car_path_details = []
		self._hits = []				# List of ParticipantMoment objects corresponding to when the participant was hit
		self._gaps = []				# List of gaps, no "gap" before first car
		self._percent_checking = [] # List of [% checking on sidewalk, % checking in road] for each road entrance
		self._entered_before_first_car = False # Hack to allow us to discard trials where the kid is in the road when the first car arrives
		
		self._objectify(Direction.LEFT) # Make objects and dictionaries and whatnot
#the above line was commented out...possibly because it would throw an exception for older data, or data where there are no LFC?
		self._objectify(Direction.RIGHT) # Make objects and dictionaries and whatnot
		
		# Memoized data for fast retrieval
		self.__memoizedData = {}
		self.__memoizedData[MEMO_INDEX_BEFORE_LAST_ENTER_ROAD] = None
		
	
	def get_percent_checking(self):
		return self._percent_checking
	
	def _is_in_car_path(self, t, trial_car):
		participant_z = self._participant.get_z_position(t)
		car_close_z = trial_car.get_close_side_z(t)
		car_far_z = trial_car.get_far_side_z(t)
		
		if (participant_z <= car_far_z and participant_z >= car_close_z):
			return True
		
		return False
		
	def _is_in_road(self, t):
		participant_z = round(self._participant.get_z_position(t),4)
		if (participant_z >= ROAD_START_Z_VALUE and participant_z < ROAD_END_Z_VALUE):
			return True
			
		return False
	
	def _is_in_near_lane(self, t):
		participant_z = round(self._participant.get_z_position(t), 4)
		if (participant_z >= ROAD_START_Z_VALUE and participant_z < ROAD_MIDDLE_Z_VALUE):
			return True
			
	def _is_between_car_paths(self, t):
		participant_z = round(self._participant.get_z_position(t), 4)
		if (participant_z >= BETWEEN_CAR_PATHS_CLOSE_Z and participant_z <= BETWEEN_CAR_PATHS_FAR_Z):
			return True

		return False

	def _objectify(self, direction):
		''' Make lists and dictionaries. '''
		
		trial_cars = self.get_trial_cars(direction)
		pos_data = self._participant.get_position_data()
		
#		print "  first posn point:", pos_data[0]
#		print "  last posn point:", pos_data[-1]
		
		was_in_car_path = False			# For car path entrance/exit details
		in_car_path = False
		
		was_in_road = False
		in_road = False					# For road entrance/exit details
		
		was_in_near_lane = False
		in_near_lane = False
		
		was_between_car_paths = False
		between_car_paths = False
		
		is_being_hit = False			# For hits
		is_being_hit_car_id = None
		has_been_hit = False # the participant was hit in this trial
		
		participant_direction = None  	# The direction the participant was last moving (Enums.ParticipantDirection)
		
		road_detail = None
		road_detail_saved = True
		car_path_detail = None
		car_path_detail_saved = True
		
		between_car_path_detail = None
		between_car_path_detail_saved = True
		
		was_checking_state = CheckingState.NO_CHECKING
		checking_state = CheckingState.NO_CHECKING
		checking_state_counter = [0,0,0,0,0] # number of moments participant has been on sidewalk / in road, per location state change: [NO_CHECKING, PC_L, FC_L, PC_R, FC_R]
		percent_looking = 0
		checking_moments = 0
		percent_checking_list = [0, 0] #[ON_SIDEWALK, IN_ROAD]
		
		is_first_time_car_passed = True # Must check the first time a car passes
		
		# Create dictionary of closest cars at time, lists of car path entrances/exist, road entrances/exits
		participant_dict = self._participant.get_participant_dict()
		sorted_keys = sorted(participant_dict.iterkeys())
		first_car = self._get_closest_car_to_participant_at_time(sorted_keys[0], direction)
		
		for t in sorted_keys:
			closest_car = self._get_closest_car_to_participant_at_time(t, direction)
			self._closest_car_dict[t] = closest_car
#			print "  closest car at t=%s = %s" % (t, closest_car.get_viz_node_id())
			if closest_car != None:
				print("Closest Car Direction", closest_car.get_direction())		
					
			# Set initially to True (it will be set to False later)
			self._entered_before_first_car = True
			
			# Don't include what happens before the first car arrives in the measures 
			# Note: the data might be used in measures that are calculated independently of the objectify method)
			if closest_car == first_car:
				continue
			else:
				# If the kid is in the road when the first car passes, most of the measure values will be useless
				# only check the very first time that the car passes
				if is_first_time_car_passed:
					#print "FIRST TIME A CAR PASSED"
					if self._participant.get_z_position(t) > ROAD_START_Z_VALUE:
						#print "KID IN THE ROAD"
						self._entered_before_first_car = True
						return None
					else:
						#print "KID NOT IN THE ROAD"
						is_first_time_car_passed = False
				
			
			# PARTICIPANT DIRECTION
			participant_direction = self._participant.get_direction(t)
			
			# IN CAR PATH
			was_in_car_path = in_car_path
			if closest_car:
				in_car_path = self._is_in_car_path(t, closest_car)
			else:
				in_car_path = False

			# IN ROAD
			was_in_road = in_road
			in_road = self._is_in_road(t)
			
			# IN NEAR LANE
			was_in_near_lane = in_near_lane
			in_near_lane = self._is_in_near_lane(t)
			
			#BETWEEN CAR PATHS
			was_between_car_paths = between_car_paths
			between_car_paths = self._is_between_car_paths(t)
			
			# CHECKING DATA 
			was_checking_state = checking_state
			checking_state = participant_dict.get(t).get_checking_state()

			#print "t: %s inRoad: %s inCP: %s checking_state: %s checking_moments: %s" % (t, in_road, in_car_path, CheckingState.toStr(checking_state), checking_moments)
			#print "t: %s, pos: %s, in_road=%s, car_near_z= %s, car_far_z= %s" % (t, self._participant.get_position(t), in_road, closest_car.get_close_side_z(t), closest_car.get_far_side_z(t))

			# HITS
			
			participant_z = round(self._participant.get_z_position(t), 4)
			#print("The current z value is:", participant_z)
			
			if (participant_z >= ROAD_START_Z_VALUE):
				participant_position = self._participant.get_position(t)
				cars = trial_cars.get_cars_at_time(t)
				for trial_car in cars:
					#print("DIRECTION:", trial_car.get_direction())
				
					# if we're being hit, wait until we're not hit again to start calculating hits
					if is_being_hit:
						#print("ISBEINGHIT")
						car_id = trial_car.get_viz_node_id()
						if (is_being_hit_car_id == car_id):
							hit = trial_car.is_in_bounding_box(t, participant_position)
							if not hit:
								is_being_hit = False
					else:
						hit = trial_car.is_in_bounding_box(t, participant_position)
						if hit:
							is_being_hit = True
							is_being_hit_car_id = trial_car.get_viz_node_id()
							has_been_hit = True													
							print "HIT HERE: ", self._participant.get_moment(t)
							self._hits.append(self._participant.get_moment(t))
							break
								
			if not was_in_road and in_road:
#				print "ENTERED ROAD AT t=%s" %(t)
#				print "\tand the index is...", sorted_keys.index(t)
				#print "checking_moments = %s" % checking_moments

				road_detail = PathDetail(t, participant_direction)
				road_detail.set_enter_index(sorted_keys.index(t))
				road_detail_saved = False
				
			if not in_near_lane and was_in_near_lane:
				print "EXITED NEAR LANE AT t=%s" %(t)
				road_detail.set_exit_near_lane_time(t)
				road_detail.set_exit_near_lane_index(sorted_keys.index(t)) #make sure this is the FIRST time the participant exits the near lane.
				road_detail_saved = False #NOT SURE THIS LINE IS NECESSARY?
			
					#TODO:
					#use enter_time -> exit_near_lane_time for events in near lane
					#use exit_near_lane_time -> exit_time for events in far lane
				
				# Checking data -> calculate % checking on sidewalk (we just entered the road)
				try:
					percent_looking = float((checking_state_counter[CheckingState.FULL_CHECKING_LEFT])) / checking_moments
				except ZeroDivisionError:
					percent_looking = 0
				#print "pct looking sidewalk = %s, (%s / %s)" %(str(percent_looking), str(checking_state_counter[CheckingState.FULL_CHECKING_LEFT]), str(checking_moments))
				percent_checking_list[PercentChecking.ON_SIDEWALK] = percent_looking
				checking_moments = 0
				checking_state_counter = [0,0,0,0,0]
				
			if not in_road and was_in_road:
				#print "EXITED ROAD AT i=%s" %(t)
				road_detail.set_exit_time(t)
				road_detail.set_exit_direction(participant_direction)
				road_detail.set_exit_index(sorted_keys.index(t))
				road_detail.set_duration(road_detail.get_exit_time() - road_detail.get_enter_time())
				self._road_details.append(road_detail)
				road_detail_saved = True
				
				#Checking data -> calculate % checking on the sidewalk (we just exited the road)
				percent_looking = float(checking_state_counter[CheckingState.FULL_CHECKING_LEFT]) / checking_moments
				percent_checking_list[PercentChecking.IN_ROAD] = percent_looking
				self._percent_checking.append(percent_checking_list)
				#print "pct looking road = %s, (%s / %s)" %(str(percent_looking), str(checking_state_counter[CheckingState.FULL_CHECKING_LEFT]), str(checking_moments))
				#print "APPENDED: ", percent_checking_list
				checking_moments = 0
				checking_state_counter = [0,0,0,0,0]
				percent_checking_list = [0,0]
			
			if not was_in_car_path and in_car_path:
				#print "ENTERED CAR PATH AT t=%s, in_car_path=%s" %(t, in_car_path)
				car_path_detail = PathDetail(t, participant_direction)
				car_path_detail.set_enter_index(sorted_keys.index(t))
				car_path_detail_saved = False

			if not in_car_path and was_in_car_path and not has_been_hit:
				#print "LEFT CAR PATH AT t=%s, in_car_path=%s" % (t, in_car_path)
				# exited the car's path
				car_path_detail.set_exit_time(t)
				car_path_detail.set_exit_index(sorted_keys.index(t))
				car_path_detail.set_exit_direction(participant_direction)
				car_path_detail.set_duration(car_path_detail.get_exit_time() - car_path_detail.get_enter_time())
				self._car_path_details.append(car_path_detail)
				car_path_detail_saved = True
				
			if not was_between_car_paths and between_car_paths and not has_been_hit:
				print "ENTERED ZONE BETWEEN CAR PATHS AT t=%s, between_car_path=%s" % (t, between_car_paths)
				between_car_path_detail = PathDetail(t, participant_direction)
				between_car_path_detail.set_enter_time(t)
				between_car_path_detail.set_enter_index(sorted_keys.index(t))
				between_car_path_detail_saved = False
				
			if not between_car_paths and was_between_car_paths and not has_been_hit:
				print "EXITED ZONE BETWEEN CAR PATHS AT t=%s, between_car_path=%s" % (t, between_car_paths)
				between_car_path_detail.set_exit_time(t)
				between_car_path_detail.set_exit_index(sorted_keys.index(t))
				between_car_path_detail.set_exit_direction(participant_direction)
				between_car_path_detail.set_duration(between_car_path_detail.get_exit_time() - between_car_path_detail.get_enter_time())
				self._between_car_path_details.append(between_car_path_detail)
				between_car_path_detail_saved = True
			
			# Increment the checking count for their current state
			#print "at t=%s, checking_moments=%s" %(t, checking_moments)
			checking_moments += 1
			checking_state_counter[checking_state] +=1

		# Save unsaved % checking data
		if checking_moments > 1: 
			percent_looking = float((checking_state_counter[CheckingState.FULL_CHECKING_LEFT])) / checking_moments
			#print "CHECKING_STATE_COUNTERS:", checking_state_counter
			#print "FC: %s, total moments: %s, pct looking: %s" %(str(checking_state_counter[CheckingState.FULL_CHECKING_LEFT]), str(checking_moments), str(percent_looking))
			if in_road:
				percent_checking_list[PercentChecking.IN_ROAD] = percent_looking
			else:
				percent_checking_list[PercentChecking.ON_SIDEWALK] = percent_looking
				percent_checking_list[PercentChecking.IN_ROAD] = 0
				
			self._percent_checking.append(percent_checking_list)
			#print "FINALLY APPENDED: %s, (list size: %s) " % (percent_checking_list, str(len(self._percent_checking)))

		# Save any car_path_detail or road_detail objects that weren't saved (op intervention, hit)
		if not road_detail_saved:
#			print "SAVING UNFINISHED ROAD ENTRANCE"
			last_time = sorted(participant_dict.iterkeys())[-1]
			road_detail.set_duration(last_time - road_detail.get_enter_time())
			self._road_details.append(road_detail)
			
		if not car_path_detail_saved:
#			print "SAVING UNFINISHED CAR PATH DETAIL"
			last_time = sorted(participant_dict.iterkeys())[-1]
			car_path_detail.set_duration(last_time - car_path_detail.get_enter_time())
			self._car_path_details.append(car_path_detail)
			
		if not between_car_path_detail_saved:
			print "SAVING UNFINISHED BETWEEN CAR PATHS DETAIL"
			last_time = sorted(participant_dict.iterkeys())[-1]
			between_car_path_detail.set_duration(last_time - car_path_detail.get_enter_time())
			self._between_car_path_detail.append(between_car_path_detail)
		
#		print "CAR PATH DETAILS = %s" % [str(x) for x in self._car_path_details]
#		print "ROAD DETAILS = %s" % [str(x) for x in self._road_details]
#		print "HITS = %s" % [str(x) for x in self._hits]

	def get_trial_result(self):
		''' Return Enums.TrialResult depending on the result of the trial '''
		tr = None
		
		if self.get_hits():
			tr = TrialResult.HIT
		elif self.get_last_exit_road_detail(ParticipantDirection.FORWARD):
			tr = TrialResult.SAFE_CROSSING
		elif self._entered_before_first_car and self._intervention_cause == Intervention.NO_INTERVENTION:
			tr = TrialResult.ENTERED_BEFORE_FIRST_CAR
		elif self._intervention_cause == Intervention.CHILD_INTERVENED:
			tr = TrialResult.CHILD_INTERVENED
		elif self._intervention_cause == Intervention.OP_INTERVENED:
			tr = TrialResult.OP_INTERVENED
		
		return tr
	
	def get_end_z(self):
		''' Return the ending z value for this trial '''
		
		#TODO: UPDATE THIS when we distinguish RIGHT from LEFT facing cars
		return Globals.roadWidth / 2.0
	
	def get_mean_walking_speed(self):
		''' Return the mean walking speed for this trial '''
		
		mean_velocity = 0
		
		end_z = self.get_end_z()
		last_enter_road_detail = self.get_last_enter_road_detail(ParticipantDirection.FORWARD)
		if last_enter_road_detail is None:
			return None
		
		enter_road_time = last_enter_road_detail.get_enter_time()
		last_time = self.get_last_time()
		
		participant = self.get_participant()
		participant_dict = participant.get_participant_dict()

		total_velocity = 0
		in_road_times = [key for key in sorted(participant_dict.iterkeys()) if key >= enter_road_time and key <= last_time]
		for t in in_road_times:
			total_velocity += participant.get_velocity(t)
		
		mean_velocity = total_velocity / len(in_road_times)
		#print "MEAN WALKING SPEED = %s" % mean_velocity
		return mean_velocity

	
	def get_start_time(self):
		''' Return the time of the first moment in the trial. '''
		return self._participant.get_first_moment().get_time()
	
	def get_last_time(self):
		''' Return the time of the last moment in the trial: either the hit time, time of final crossing, or op intervention time. '''
		return self._participant.get_last_moment().get_time()
	
	def get_gaps(self, direction):
		"""
		Save a list of the gaps (in metres and seconds) so we don't have to calculate this every time		
		The LAST gap is the gap the participant crossed in or got hit in.
		The gap before the first car is IGNORED.
		"""
		
		if self._gaps: return self._gaps
		
		trial_cars = self.get_trial_cars(direction)
		participant = self.get_participant()
		
		previous_car = None
		next_car = None
		participant_dict = participant.get_participant_dict()
		
		# get last index we're interested in for gap
		path_detail = self.get_first_exit_car_path_detail(ParticipantDirection.FORWARD)
		if path_detail is None:
			last_time = participant.get_last_moment().get_time()
		else:
			last_time = path_detail.get_exit_time()
		
		for t in sorted(participant_dict.iterkeys()):
			if t >= last_time:
				break
			
			closest_car = self.get_closest_car(t, direction)
			if closest_car is None:
				continue
			
			if previous_car is None:
				previous_car = closest_car
			
			if closest_car.get_viz_node_id() != previous_car.get_viz_node_id():
				gap = self._get_gap(closest_car, previous_car, t)

				#print "FOUND GAP = %s" % gap.get_length()
				#print "  t=%s" % t
				#print "  PREV car = %s" % previous_car.get_viz_node_id()
				#print "  NEXT car = %s" % closest_car.get_viz_node_id()
				
				if gap is not None:
					self._gaps.append(gap)

			previous_car = closest_car
			
		return self._gaps

		
	def _get_gap(self, next_car, previous_car, t):
				
		try:
			''' Return a GapDetail for the gap between these two cars '''
			prev_car_rear_bumper_x = previous_car.get_rear_bumper_x(t)
			next_car_front_bumper_x = next_car.get_front_bumper_x(t)
			gap_length = abs(prev_car_rear_bumper_x - next_car_front_bumper_x)
		except:
			print "Warning: gap times do not match - ignoring this gap ( t =",t,")"
			return None
		
		#distance = vizmat.Distance(next_car.get_position(t), previous_car.get_position(t))
		vel_x = next_car.get_velocity_x(t)
		gap_time = abs(gap_length / vel_x)
		gap = GapDetail(gap_length, gap_time)
		return gap
		
		
	def get_road_details(self):
		return self._road_details
		
	def get_road_details_forward_entrance(self):
		''' Return the path details corresponding to when the participant entered the road moving forward. '''
		forward_moving_road_details = []
		for road_detail in self._road_details:
			#print "  road deet:", road_detail
			if road_detail.get_enter_direction() == ParticipantDirection.FORWARD:
				forward_moving_road_details.append(road_detail)
				
		return forward_moving_road_details
		
	def get_car_path_details(self):
		return self._car_path_details
	
	def get_between_car_path_details(self):
		return self._between_car_path_details
		
	def get_trial_data(self):
		return self._trial_data
		
	def get_participant(self):
		return self._participant
		
	def get_trial_cars(self, direction):
		''' Get the car data for the cars facing the given direction. '''
		car_position_data = None
		
		if direction == Direction.RIGHT:
			car_position_data = self.get_right_facing_car_data()
		elif direction == Direction.LEFT:
			car_position_data = self.get_left_facing_car_data()

		return car_position_data
		
	def get_left_facing_car_data(self):
		return self._left_facing_car_data
	
	def get_right_facing_car_data(self):
		return self._right_facing_car_data
	
	
	
	def get_time_first_car_arrived(self, direction):
		''' Return the moment the first car arrived '''
		
		participant_dict = self.get_participant().get_participant_dict()
		sorted_keys = sorted(participant_dict.iterkeys())
		if not sorted_keys:
			return None
		
		first_car = self._get_closest_car_to_participant_at_time(sorted_keys[0], direction)
		for t in sorted_keys:
			closest_car = self._get_closest_car_to_participant_at_time(t, direction)
			if closest_car != first_car:
				return t
		
		return None

	
	def get_moment_last_entered_road(self):
		''' Return the moment the participant last entered the road '''
		moment = self._participant.get_moment_last_entered_road()
		return moment
		
		
	def get_moment_last_entered_car_path(self):
		""" Return the moment the participant last entered the car path """
		car_path_detail = self.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not car_path_detail:
			return None
		time_entered_car_path = car_path_detail.get_enter_time()
		moment = self._participant.get_moment(time_entered_car_path)
		return moment
		
		
	def get_moment_first_exit_car_path(self):
		""" Return the moment the participant first exited the car path """
		car_path_detail = self.get_first_exit_car_path_detail(ParticipantDirection.FORWARD)
		if not car_path_detail:
			return None
		time_exited_car_path = car_path_detail.get_exit_time()
		moment = self._participant.get_moment(time_exited_car_path)
		return moment
		
		
	def get_moment_crossed_road(self):
		""" Return the moment the participant crossed the road """
		crossed_road_z = (Globals.roadWidth / 2.0) - 0.001  # make sure floating point errors don't get us!
		moment = self._participant._get_moment_last_crossed_z_value(crossed_road_z)  # a bit hacky
		return moment
		
	
	def get_cars_at_time(self, t, direction):
		'''	Return a list of the cars at time t. '''
		trial_cars = self.get_trial_cars(direction)
		cars = trial_cars.get_cars_at_time(t)
		return cars	
		
	def get_closest_car(self, t, direction):
		''' Return the closest car at time t '''
		try:
			closest_car = self._closest_car_dict[t]
		except:
			return None
		return self._closest_car_dict[t]
		
	def get_closest_car_to_participant_at_time(self , t, direction):
		return self._get_closest_car_to_participant_at_time(t, direction)
	
	def _get_closest_car_to_participant_at_time(self, t, direction):
		''' Return the closest car to the participant at time t: used when objectifying raw data. '''
		participant_x = self._participant.get_x_position(t)
		trial_cars = self.get_trial_cars(direction)
		#print "t=%s" % (t)
		trial_car = trial_cars.get_next_to_x_at_t(participant_x, t)
		#print "  CLOSEST CAR AT t=%s is %s" % (t, trial_car)
		return trial_car
		
	def get_previous_car_at_time(self, t, direction):
		''' Return the car that last went by the participant at time t '''
		participant_x = self._participant.get_x_position(t)
		trial_cars = self.get_trial_cars(direction)
		trial_car = trial_cars.get_previous_car_passed_x_at_t(participant_x, t)
		return trial_car

	def get_hits(self):
		''' Return a list of ParticipantMoment objects corresponding to when a participant was hit '''
		return self._hits
		
	def get_first_hit(self):
		''' Return the ParticipantMoment of the first hit '''
		if self._hits:
			return self._hits[0]
		
		return None
		
	
	def get_last_enter_road_detail(self, participant_direction):
		''' Return the path_detail corresponding to when the participant last entered the road '''
		for i in range(len(self._road_details)-1, -1, -1):
			if self._road_details[i].get_enter_direction() == participant_direction:
				return self._road_details[i]
				
		return None
		
	def get_last_exit_road_detail(self, participant_direction):
		''' Return the path detail corresponding to when the participant last exited the road '''
		for i in range(len(self._road_details)-1, -1, -1):
			if self._road_details[i].get_exit_direction() == participant_direction:
				return self._road_details[i]
				
		return None
		
	
	def get_last_enter_car_path_detail(self, participant_direction):
		#TODO: Change this for two-lane?
		''' Return the path_detail corresponding to when the participant last entered the car path '''
		for i in range(len(self._car_path_details)-1, -1, -1):
			enter_direction = self._car_path_details[i].get_enter_direction()
			enter_time = self._car_path_details[i].get_enter_time()
			enter_z = self.get_participant().get_moment(enter_time).get_z_position()
			# return the car path detail if the participant was moving forward, and they entered before the half-way
			# point in the road.  This is a hack to ensure that we don't return the last car path detail if the participant
			# "enters" the next closest car's path after crossing safely but VERY CLOSE to the car they passed in front of.
			if  enter_direction == participant_direction and enter_z <= (ROAD_END_Z_VALUE / 2):
				return self._car_path_details[i]
		
		return None
	
#	# TODO: Almost never care about last exit car path (because of loop back), use first_exit
#	def get_last_exit_car_path_detail(self, participant_direction):
#		''' Return the path detail object corresponding to the last exit of the car path '''
#		for i in range(len(self._car_path_details)-1, -1, -1):
#			if self._car_path_details[i].get_exit_direction() == participant_direction:
#				return self._car_path_details[i]
#				
#		return None
	
	def get_first_exit_car_path_detail(self, participant_direction):
		''' Return the time that the participant first exited the car path '''
		
		for i in range (0, len(self._car_path_details)):
			if self._car_path_details[i].get_exit_direction() == participant_direction:
				return self._car_path_details[i]
				
		return None
		
	def get_exit_car_path_details(self):
		''' Return all times the participant exited the car path up to the first time they exit the far side of a car's path '''
		cp_details = []
		for i in range(0, len(self._car_path_details)):
			# if the kid entered going forward and exited the car path, include it
			if self._car_path_details[i].get_enter_direction() == ParticipantDirection.FORWARD and \
				self._car_path_details[i].get_exit_direction() is not None:
					cp_details.append(self._car_path_details[i])
					
		return cp_details
		
	def get_last_enter_between_car_path_detail(self, participant_direction):
		'''Return the between car path detail corresponding to the last time the participant entered between the car paths'''
		for i in range(len(self._between_car_path_details)-1,-1,-1):
			if self._between_car_path_details[i].get_enter_direction() == participant_direction:
				return self._between_car_path_details[i]
				
		return None
																