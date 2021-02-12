from Enums import TrialType, Phase

class ParticipantSession():
	
	def __init__(self, data_dir, participant_id, timestamp, participant_trials, bounding_box_data, participant_data, phase):
		self._participant_id = participant_id
		self._timestamp = timestamp

		self._bounding_box_data = bounding_box_data
		self._participant_data = participant_data
		
		self._data_dir = data_dir
		self._participant_trials = participant_trials #get_trials --> these are ParticipantTrial objects, but they're retrieved using ParticipantSession.get_trials(), just makes sense
		
		self._phase = phase # Enums.Phase --> Which GUI phase this session is for.
	
	def get_participant_id(self):
		return self._participant_id
	
	def get_timestamp(self):
		return self._timestamp
		
	def get_bounding_box_data(self):
		return self._bounding_box_data
		
	def get_participant_data(self):
		return self._participant_data
	
	def get_trials(self):
		return self._participant_trials
		
	def get_phase(self):
		return self._phase
	
	def __str__(self):
		my_string = "participant id: %s, timestamp: %s, phase: %s\n" % (str(self._participant_id), str(self._timestamp), Phase.toStr(self._phase))
		my_string += "trials:\n"
		for pt in self._participant_trials:
			my_string += "  " + str(pt) + "\n"
		return my_string