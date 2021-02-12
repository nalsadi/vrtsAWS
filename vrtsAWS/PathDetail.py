from Enums import ParticipantDirection

class PathDetail():
	''' Store information about path entrances and exits for a trial. '''
	
	def __init__(self, enter_time, enter_direction):
		self._enter_time = enter_time
		self._enter_direction = enter_direction # Enums.ParticipantDirection.FORWARD / BAKCWARD
		self._exit_time  = None
		self._exit_direction = None
		self._enter_index = None
		self._exit_index = None
		self._participant_moment = None
		self._duration = None
		self._near_lane_exit_time = None
		self._near_lane_exit_index = None
		
	def get_participant_moment(self):
		return self._participant_moment
		
	def set_participant_moment(self, participant_moment):
		self._participant_moment = participant_moment
	
	def set_enter_time(self, enter_time):
		self._enter_time = enter_time
		
	def set_enter_direction(self, enter_direction):
		self._enter_direction = enter_direction
		
	def set_exit_time(self, exit_time):
		self._exit_time = exit_time
		
	def set_enter_index(self, index):
		self._enter_index = index
		
	def set_exit_index(self, index):
		self._exit_index = index
		
	def set_exit_direction(self, exit_direction):
		self._exit_direction = exit_direction
		
	def set_exit_near_lane_time(self, near_lane_exit_time):
		self._near_lane_exit_time = near_lane_exit_time
		
	def set_exit_near_lane_index(self, near_lane_exit_index):
		self._near_lane_exit_index = near_lane_exit_index
		
	def get_enter_time(self):
		return self._enter_time
		
	def get_enter_direction(self):
		return self._enter_direction
		
	def get_exit_time(self):
		return self._exit_time
		
	def get_enter_index(self):
		return self._enter_index
		
	def get_exit_index(self):
		return self._exit_index
		
	def get_exit_direction(self):
		return self._exit_direction
		
	def get_duration(self):
		return self._duration
		
	def get_exit_near_lane_index(self):
		return self._near_lane_exit_index
		
	def get_exit_near_lane_time(self):
		return self._near_lane_exit_time
		
	def set_duration(self, duration):
		self._duration = duration
		
	
	def __str__(self):
		return "enter: %s, %s, exit: %s, %s, duration: %s" % (
			self._enter_time,
			ParticipantDirection.toStr(self._enter_direction), 
			self._exit_time, 
			ParticipantDirection.toStr(self._exit_direction),
			self._duration
		)