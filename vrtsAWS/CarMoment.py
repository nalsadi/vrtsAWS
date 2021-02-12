from Enums import Position

class CarMoment:
	
	def __init__(self, t, position, raw_data_point):
		self._time = t
		self._position = position
		self._raw_data_point = raw_data_point
		
	def get_time(self):
		return self._time
		
	def get_position(self):
		return self._position
		
	def get_raw_data_point(self):
		return self._raw_data_point
		
	def get_x_position(self):
		return self._position[Position.X_POS]
		
	def get_y_position(self):
		return self._position[Position.Y_POS]
		
	def get_z_position(self):
		return self._position[Position.Z_POS]