#import pickle
import cPickle as pickle
from Enums import TrialType

class ParticipantTrial():

	def __init__(self, trial_number, attempt_number, filename, last_modified, trial_type,trial_cond, left_facing_car_speed, right_facing_car_speed,prepost):
		self._trial_number = trial_number
		self._attempt_number = attempt_number
		self._raw_data = None
		self._filename = filename
		self._last_modified = last_modified
		self._trial_type = trial_type
		self._trial_cond = trial_cond
		self._trial_prepost = prepost
		self._left_facing_car_speed = left_facing_car_speed
		self._right_facing_car_speed = right_facing_car_speed
		
	def __str__(self):
		my_string = "t: %s, a: %s, filename: %s, type: %s" % (self._trial_number, self._attempt_number, self._filename, TrialType.toStr(self._trial_type))
		return my_string
		
	def get_trial_number(self):
		return self._trial_number
		
	def get_trial_cond(self):
		return self._trial_cond
		
	def get_trial_prepost(self):
		return self._trial_prepost
		
	def get_attempt_number(self):
		return self._attempt_number
		
	def get_trial_and_attempt_number(self):
		return self._trial_number + "-" + self._attempt_number
	
	def get_filename(self):
		return self._filename
		
	def get_last_modified(self):
		return self._last_modified
		
	def get_trial_type(self):
		return self._trial_type
		
	def get_left_facing_car_speed(self):
		return self._left_facing_car_speed
		
	def get_right_facing_car_speed(self):
		return self._right_facing_car_speed
		
	def get_raw_data(self):
		# If the data has already been loaded, return it
		if self._raw_data:
			return self._raw_data
			
		f = open(self._filename)
		self._raw_data = pickle.load(f)
		return self._raw_data


		
		

	