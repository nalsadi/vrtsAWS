class GapDetail:
	''' DTO for gaps '''
	
	def __init__(self, length, time, start_time=None, end_time=None):
		
		self._start_time = start_time
		self._end_time = end_time
		self._length = length
		self._time = time
		
	def __str__(self):
		return "length: %s, time: %s" % (self._length, self._time)
		
	def get_start_time(self):
		return self._start_time
	
	def get_end_time(self):
		return self._end_time
		
	def get_gap_time(self):
		return self._time
		
	def set_gap_time(self, time):
		self._time = time
		
	def get_length(self):
		return self._length
		
	def set_length(self, length):
		self._length = length