from Enums import Position, OrientationType

class ParticipantMoment:
	''' Represent participant data moments using this object '''
	
	def __init__(self, t, index, position, orientation, checking_state):
		self._time = t
		self._index = index
		self._position = position
		self._orientation = orientation
		self._checking_state = checking_state
		
	def get_time(self):
		return self._time
		
	def get_index(self):
		return self._index
		
	def get_position(self):
		return self._position
		
	def get_x_position(self):
		return self._position[Position.X_POS]
		
	def get_z_position(self):
		return self._position[Position.Z_POS]
		
	def get_y_position(self):
		return self._position[Position.Y_POS]
		
	def get_orientation(self):
		return self._orientation
	
	def get_yaw(self):
		return self._orientation[OrientationType.YAW]
	
	def get_pitch(self):
		return self._orientation[OrientationType.PITCH]
		
	def get_checking_state(self):
		return self._checking_state
	
	def __str__(self):
		return "t: %s, pos: %s, ori: %s" % (self._time, self._position, self._orientation)
	