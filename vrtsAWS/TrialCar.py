from CarMoment import CarMoment
from Enums import CarPositionData, Position, BoundingBox, Direction


class TrialCar:
	
	def __init__(self,  mesh_filename, viz_node_id, direction, raw_car_data, bounding_box_data):
		self._mesh_filename = mesh_filename			# Mesh
		self._viz_node_id = viz_node_id				# viz node ID
		self._direction = direction					# Enums.Direction
		self._raw_car_data = raw_car_data			# Raw data points (mesh, id, t, position, direction)
		self._bounding_box_data = bounding_box_data	# Bounding box data 
		
		self._car_moments = [] #[CarMoment]
		self._car_dict = {} # time -> CarMoment
		
		self._objectify()
	
	
	def __str__(self):
		return "id: %s, mesh: %s, direction: %s" % (self._viz_node_id, self._mesh_filename, self._direction)
	
	
	def _objectify(self):
		''' Store the raw data as CarMoment objects '''
		
		for data_tuple in self._raw_car_data:
			# car data == (car.getMeshFileName(), car.getVizNodeId(), currentTime, car.getPosition(), car.getDirection())
			#Cars from both directions are being appended, print("The Direction of The Car Added:",data_tuple[CarPositionData.CARDIRECTION])
			t = data_tuple[CarPositionData.CARTIME]
			pos = data_tuple[CarPositionData.CARPOSITION]
			car_moment = CarMoment(t, pos, data_tuple)
			
			self._car_moments.append(car_moment)
			self._car_dict[t] = car_moment
		
		
	def get_mesh_filename(self):
		return self._mesh_filename
		
		
	def get_viz_node_id(self):
		return self._viz_node_id


	def get_direction(self):
		return self._direction
		
		
	def get_raw_car_data(self):
		return self._raw_car_data
		
		
	def get_car_moments(self):
		return self._car_moments
		
		
	def get_car_dict(self):
		return self._car_dict
	
		
	def get_car_moment(self, t):		
		if t in self._car_dict: 
			return self._car_dict[t]
		return None
	
	
	def get_close_side_z(self, t):
		''' Return the z position of side of the car closest to the participant's starting position'''
		
		# carBoundingBox is based around the center of the car (i.e. the center is at (0,0))
		# so carBoundingBox[BoundingBox.ZMIN] will be negative
		car_moment = self.get_car_moment(t)
		z_min = car_moment.get_z_position() + self._bounding_box_data[BoundingBox.ZMIN]
		return z_min


	def get_far_side_z(self, t):
		''' Return the z position of side of the car farthest from the participant's starting position'''
		car_moment = self.get_car_moment(t)
		z_max = car_moment.get_z_position() + self._bounding_box_data[BoundingBox.ZMAX]
		return z_max


	def get_front_bumper_x(self, t):
		''' Return the front bumper x position at time t '''
		car_moment = self.get_car_moment(t)
		if (self._direction == Direction.RIGHT):
			front_bumper_x = car_moment.get_x_position() + self._bounding_box_data[BoundingBox.XMAX]
		elif (self._direction == Direction.LEFT):
			front_bumper_x = car_moment.get_x_position() + self._bounding_box_data[BoundingBox.XMIN]
			
		return front_bumper_x
	
	
	def get_rear_bumper_x(self, t):
		''' Return the rear bumper x position at time t'''
		car_moment = self.get_car_moment(t)
		if (self._direction == Direction.RIGHT):
			rear_bumper_x = car_moment.get_x_position() + self._bounding_box_data[BoundingBox.XMIN]
		elif (self._direction == Direction.LEFT):
			rear_bumper_x = car_moment.get_x_position() + self._bounding_box_data[BoundingBox.XMAX]
			
		return rear_bumper_x
		
		
	def get_front_bumper_distance_from_x(self, t, x):
		''' 
		Return the distance this car's front bumper is at time t from position x.
		Negative distance means the car is before the x.  Positive means it's passed x.
		'''
		front_bumper_x = self.get_front_bumper_x(t)			
		front_bumper_from_x = front_bumper_x - x
		return front_bumper_from_x 
		
		
	def get_time_from_x(self, t, x):
		''' Return how long from t until this car reaches x, or how long since it was at x '''
		
		d = None
		if (self._direction == Direction.RIGHT):
			# If moving toward the x, use front bumper
			if (x > self.get_car_moment(t).get_x_position()):
				d = self.get_front_bumper_distance_from_x(t, x)
			else:
				d = self.get_rear_bumper_distance_from_x(t, x)
		if (self._direction == Direction.LEFT):
			if (x < self.get_car_moment(t).get_x_position()):
				d = self.get_front_bumper_distance_from_x(t, x)
			else:
				d = self.get_rear_bumper_distance_from_x(t, x)

		v = self.get_velocity_x(t)
		t = abs(d / v)
		return t
		
		
	def get_time_front_bumper_crosses_x(self, x):
		''' Returns the time that the front bumper crosses x (if any) '''
		times = sorted(self.get_car_dict().keys())
		for t in times:
			front_bumper_x = self.get_front_bumper_x(t)
			if front_bumper_x >= x: 
				return t
		return None
		
		
	def get_time_rear_bumper_crosses_x(self, x):
		''' Returns the time that the rear bumper crosses x (if any) '''
		times = sorted(self.get_car_dict().keys())
		for t in times:
			rear_bumper_x = self.get_rear_bumper_x(t)
			if rear_bumper_x >= x:
				return t
		return None
		

	def get_rear_bumper_distance_from_x(self, t, x):
		''' 
		Return the distance this car's rear bumper is at time t from position x.
		Negative distance means the car is before the x.  Positive means it's passed x.
		'''
		rear_bumper_x = self.get_rear_bumper_x(t)
		rear_bumper_from_x = rear_bumper_x - x
		return rear_bumper_from_x


	def is_in_bounding_box(self, t, point):
		''' Return if the point is in the bounding box at time t '''

		in_box = False

		car_front_bumper = self.get_front_bumper_x(t)
		car_rear_bumper = self.get_rear_bumper_x(t)
		car_z_max = self.get_far_side_z(t)
		car_z_min = self.get_close_side_z(t)
		direction = self.get_direction()
		# determine if the point is inside the car
		x = point[Position.X_POS]
		z = point[Position.Z_POS]
		if(direction == Direction.RIGHT):
			if ((car_rear_bumper <= x <= car_front_bumper) and 
				(car_z_min <= z <= car_z_max)):
					in_box = True
		else:
			if ((car_rear_bumper >= x >= car_front_bumper) and 
				(car_z_min <= z <= car_z_max)):
					in_box = True
			
		
		##### GET DIRECTION and use IF to add RB>=x>-FB
		return in_box	
		
		
	def get_velocity_x(self, t):
		''' Return the car's momentary velocity on the x-axis. '''
		
		# Need to average out the velocity (over 50 points, arbitrarily) due to some strange spikes in the recorded car data.
		car_data = self.get_raw_car_data()

		if (len(car_data) < 2):
			#self.__logger.error("Can't calculate car velocity. There's less than 2 data points for this car.")
			return None
		
		# get the index of this particular data point in the list of the car's data points for this trial
		# God, this is dumb.  Reconstructing the tuple just to find it in the raw data.		
		raw_data_point = self.get_car_moment(t).get_raw_data_point()
		carIndex = car_data.index(raw_data_point)
		
		d_delta = 0
		t_delta = 0
		
		total_dp = len(car_data)
		total_velocity = 0
		
		start_val = 0
		end_val = 0
		
		if (len(car_data) < 50):
			start_val = 0
			end_val = len(car_data)
			
		elif (carIndex < 25):
			start_val = 0
			end_val = 50
			
		elif (carIndex + 25 > len(car_data)):
			start_val = len(car_data) - 50
			end_val = len(car_data)
			
		else:
			start_val = carIndex - 25
			end_val = carIndex + 25
		
		iterations = end_val - start_val - 1
		for i in range(start_val, end_val - 1):
			j = i+1
			firstPoint = car_data[i]
			secondPoint = car_data[j]
			d_delta = firstPoint[CarPositionData.CARPOSITION][Position.X_POS] - secondPoint[CarPositionData.CARPOSITION][Position.X_POS]
			t_delta = firstPoint[CarPositionData.CARTIME] - secondPoint[CarPositionData.CARTIME]
			
			total_velocity += (d_delta/t_delta)
		
		average_velocity = total_velocity / iterations
		return average_velocity