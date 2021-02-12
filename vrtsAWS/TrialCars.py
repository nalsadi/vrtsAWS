from Enums import CarPositionData, BoundingBox, Direction
from TrialCar import TrialCar

class TrialCars:
	''' Cars for a given trial.  Either right or left facing cars. '''
	
	def __init__(self, raw_trial_cars_data, trial_cars_bounding_box_data, direction):
		# trial_cars == list of tuples (car.getMeshFileName(), car.getVizNodeId(), currentTime, car.getPosition(), car.getDirection())
		self._raw_car_data = raw_trial_cars_data
		self._trial_cars_bounding_box_data = trial_cars_bounding_box_data
		self._direction = direction #Enums.Direction
		
		self._cars = [] # list of [TrialCar]
#		self._cars_dict = {} # (mesh,id) -> TrialCar ---- viz_node_ids are not unique
		
		self._objectify() # Make a bunch of objects
	
	def __str__(self):
		tc_string = "# points: %s" % len(self._raw_car_data)
		return tc_string
		
	def _objectify(self):
		# Get list of the cars in the trial
		#unique_car_ids = set([car_tuple[CarPositionData.CARID] for car_tuple in self._raw_car_data])
		unique_id_mesh = set([(car_tuple[CarPositionData.CARMESH], car_tuple[CarPositionData.CARID]) for car_tuple in self._raw_car_data])
		
#		print "TRIAL CARS"
#		for p in unique_id_mesh:
#			print "car: ", p
#		
		# Create a TrialCar for each of the cars
		for unique_car_mesh_id in unique_id_mesh:#unique_car_ids:
			
			this_car_mesh = unique_car_mesh_id[0]
			this_car_id = unique_car_mesh_id[1]
			
			raw_trial_car_data = [
				car_tuple for car_tuple in self._raw_car_data if \
					car_tuple[CarPositionData.CARID] == this_car_id and \
					car_tuple[CarPositionData.CARMESH] == this_car_mesh
				]
			
			# get TrialCar info from the first tuple
			try:
				direction = raw_trial_car_data[0][CarPositionData.CARDIRECTION]
				#print "d:", direction
				# Some old car data didn't use Enums.Direction, it just had "Right"
				if direction == "Right":
					direction = Direction.RIGHT
			except IndexError:
				#print "OLD CAR DATA -- assuming Direction.RIGHT"
				# Old car data didn't have direction -- assume just RFC data
				direction = Direction.RIGHT
				
				
			bb_data = self._get_bounding_box(this_car_mesh, direction)
			tc = TrialCar(this_car_mesh, this_car_id, direction, raw_trial_car_data, bb_data)

			# Save the car data
			self._cars.append(tc)
			#self._cars_dict[unique_car_mesh_id] = tc
		

	def _get_bounding_box(self, car_mesh, car_direction):
		''' 
		Get the bounding box data for the car.  Must switch around the min/max values
		for car01 due to a problem with the car model not being centered in addition to
		the local co-ordinate system not knowing about the 180 degree rotation of the car.
		'''
		bb_data = self._trial_cars_bounding_box_data[car_mesh]
		if car_direction == Direction.RIGHT:
			temp_zmin = bb_data[BoundingBox.ZMIN]
			temp_zmax = bb_data[BoundingBox.ZMAX]
			bb_data = \
					(bb_data[BoundingBox.XMIN], 
					bb_data[BoundingBox.XMAX],
					-temp_zmax,
					-temp_zmin)
			#print "CAR ZMIN/ZMAX = ", bb_data[BoundingBox.ZMIN], bb_data[BoundingBox.ZMAX]
			
		return bb_data		
		

	def get_raw_car_data(self):
		return self._raw_car_data

	def get_cars(self):
		''' Return all the TrialCar objects for all cars in this trial '''
		return self._cars
		
	def get_cars_at_time(self, t):
		''' Return all the TrialCars that have car data at time t '''
		cars = [trial_car for trial_car in self._cars if t in trial_car.get_car_dict()]
		
		return cars
		
	def get_next_to_x_at_t(self, x, t):
		''' Return the next car that will arrive at x, given time t in the trial '''
		direction = self._direction
		cars = self.get_cars_at_time(t)
		closestCar = None
		closestCarDistanceX = -1000000
		if (direction == Direction.LEFT):
			closestCarDistanceX = 10000000
		
		# get the data point that is closest in X direction to the participant that isn't past him/her
		for trial_car in cars:
			carFrontBumperDistance = trial_car.get_front_bumper_distance_from_x(t, x)
			
			#print "   car: %s distance %s" % (trial_car.get_viz_node_id(), carFrontBumperDistance)
			
			if (direction == Direction.RIGHT):
				# if car has passed the participant, move on
				if (carFrontBumperDistance >= 0):
					continue
				
				# if this car is closer than the previously closest car
				if (carFrontBumperDistance > closestCarDistanceX):
					closestCarDistanceX = carFrontBumperDistance
					closestCar = trial_car
					
			elif (direction == Direction.LEFT):
				# if car has passed the participant, move on
				if (carFrontBumperDistance <= 0):
					continue
				
				# if this car is closer than the previously closest car
				if (carFrontBumperDistance < closestCarDistanceX):
					closestCarDistanceX = carFrontBumperDistance
					closestCar = trial_car

		return closestCar
			
		
	def get_previous_car_passed_x_at_t(self, x, t):
		"""	Returns the car that has most recently passed the participant at a particular time """
		
		direction = self._direction
		cars = self.get_cars_at_time(t)
		
		last_car_passed = None
		closestDistance = 100000
		if (direction == Direction.LEFT):
			closestDistance = -100000
		
		#partPos = self.__get_position_at_time(trialData.get_participant_position_data(), currentTime)
#		print "*** GET PREVIOUS CAR PASSED"
#		print "   * time = ", t
		
		for trial_car in cars:
			#distance = self.__get_distance_from_back_bumper_on_x_axis(partPos, carData)
			distance = trial_car.get_rear_bumper_distance_from_x(t, x)
#			print "     * car: %s, rear bumper to x = %s"% (trial_car, distance)
			if (direction == Direction.RIGHT):
				# distance is negative if the car is still coming, positive if the car has passed
				if distance < 0:
					continue
					
				# if the current car is closer than the closest so far, it's the last car passed
				if (distance < closestDistance):
					closestDistance = distance
					last_car_passed = trial_car
			
			elif (direction == Direction.LEFT):
				# distance is positive if the car is still coming, negative if the car has passed
				if distance > 0:
					continue
					
				# if the current car is closer than the closest so far, it's the last car passed
				if (distance > closestDistance):
					closestDistance = distance
					last_car_passed = trial_car

#		print "   * last car passed = ", last_car_passed
		return last_car_passed
		