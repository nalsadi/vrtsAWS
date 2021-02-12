import os
from datetime import datetime
import cPickle as pickle
from collections import defaultdict
from ParticipantSession import ParticipantSession
from ParticipantTrial import ParticipantTrial
from Enums import TrialType, Phase, TrialData
#import viz
import logging

PRACTICE_TRIALS = 0
STANDARD_TRIALS = 1
TIME_PRESSURE_TRIALS = 2

class DataHandler():
	''' Handle the saving / loading of the trial data. '''
	
	def __init__(self):
		logging.basicConfig()
		self._logger = logging.getLogger("DataHandlerLogger")
		#self._data_dir = data_dir # The directory we're dealing with.
		
	def _get_trial_and_attempt_number(self, filename, participant_id): #, timestamp):
		''' Parse the trial and attempt numbers from the given trial_number, taken from the filename of a trial (e.g. 4-1). '''
		
		timestamp_start_index = filename.rfind(participant_id) + len(participant_id) + 1 #filename.index(timestamp) + len(timestamp) + 1 #for the _
		timestamp_end_index = filename.find("_", timestamp_start_index) #filename.index("_", start_index)
		trial_end_index = filename.find("_", timestamp_end_index + 1)
		trial_and_attempt_number = filename[timestamp_end_index + 1:trial_end_index]

		dash_index = trial_and_attempt_number.index("-")
		trial_number = trial_and_attempt_number[:dash_index]
		attempt_number = trial_and_attempt_number[dash_index+1:]

		return (trial_number, attempt_number)

	def _get_phase(self, file_list, participant_id, timestamp):
		
		# TODO: this won't work unless the PRACTICE, STANDARD, and TIMEPRESSURE trials are done in separate session, as is the case for the pilot.
		participant_dumped_data_files = filter(lambda x:participant_id in x and timestamp in x and 'dumpedData' in x, file_list)
		
		if participant_dumped_data_files:
			if self._is_practice_trial(participant_dumped_data_files[0]):
				return Phase.PHASE_III
				
			if self._is_speed_test_trial(participant_dumped_data_files[0]):
				return Phase.PHASE_II
				
			if self._is_time_pressure_trial(participant_dumped_data_files[0]):
				return Phase.PHASE_V
		
		#return TrialType.STANDARD
		return Phase.PHASE_IV
		
	def _is_practice_trial(self, filename):
		if '_p_' in filename:
			return True
		return False
		
	def _is_speed_test_trial(self, filename):
		if '_st_' in filename or '_str_' in filename:
			return True
		return False
		
	def _is_time_pressure_trial(self, filename):
		if '_tp_' in filename:
			return True
		return False
		
	def _get_participant_trials(self, file_list, participant_id, timestamp, data_dir, tp_timestamp):
		''' Return a list of ParticipantTrials for this session '''

		session_file_list = filter(lambda x:participant_id in x and timestamp in x and 'dumpedData' in x, file_list)

		trials = []
		for f in session_file_list:
			
			trial_type = None
			right_facing_car_speed = 99999
			left_facing_car_speed = 99999

			# the data from VR2.0 was NOT pickled in binary, so we need to account for that
			full_path_filename = os.path.join(data_dir, f)
			try:
				file_object = open(full_path_filename, 'rb')
				all_trial_data = pickle.load(file_object)
			except ValueError:
				file_object = open(full_path_filename, 'r')	
				all_trial_data = pickle.load(file_object)
			
			# grab all the trial data
			try:
				trial_data = all_trial_data[TrialData.TRIAL_DATA]
				trial_type = trial_data.getTrialType()
				trial_cond = trial_data.getPredefinedConditionId()
				trial_prepost = trial_data.getPrePost()
				right_facing_car_speed = trial_data.getRightFacingCarSpeed()
				left_facing_car_speed = trial_data.getLeftFacingCarSpeed()
			except IndexError:
				print "ERROR: ENCOUNTERED TRIAL DATA THAT DOES NOT CONTAIN a Trial object."
			
			trial_and_attempt_number = self._get_trial_and_attempt_number(f, participant_id)
			trial_number = trial_and_attempt_number[0]
			attempt_number = trial_and_attempt_number[1]
			last_modified = datetime.fromtimestamp(float(os.path.getmtime(full_path_filename)))
	
			participant_trial = ParticipantTrial(trial_number, attempt_number, full_path_filename, last_modified, trial_type, trial_cond, left_facing_car_speed, right_facing_car_speed,trial_prepost)
			trials.append(participant_trial)
		
		return trials
	
	def _get_bounding_box_data(self, file_list, participant_id, timestamp, data_dir):
		bb_data_file = filter(lambda x:participant_id in x and timestamp in x and 'boundingBoxData' in x, file_list)
		try:
			f = open(os.path.join(data_dir, bb_data_file[0]), 'rb')
			bb_data = pickle.load(f)
		except IOError:
			self._logger.error("Could not load bounding box data.")
			return None
		# if we're loading VR2.0 data, it was NOT saved in binary
		except ValueError:
			f = open(os.path.join(data_dir, bb_data_file[0]), 'r')
			bb_data = pickle.load(f)
			
		return bb_data
		
	def _get_participant_data(self, file_list, participant_id, timestamp, data_dir):
		p_data_file = filter(lambda x:participant_id in x and timestamp in x and 'participantData' in x, file_list)
		try:
			f = open(os.path.join(data_dir, p_data_file[0]), 'rb')
			p_data = pickle.load(f)
		except IOError:
			self._logger.error("Could not load participant data.")
			return None
		# if we're loading VR2.0 data, it was NOT saved in binary	
		except ValueError:
			f = open(os.path.join(data_dir, p_data_file[0]), 'r')
			p_data = pickle.load(f)
		
		return p_data
	
	def _get_timestamp(self, participant_data_file):
		''' Get the timestamp of the participant_data_file (ends with "participantData") '''
		timestamp_end_index = participant_data_file.rfind("_")
		timestamp_start_index = participant_data_file.rfind("_", 0, timestamp_end_index)
		timestamp = participant_data_file[timestamp_start_index+1:timestamp_end_index]
		return timestamp
		
	def _get_participant_ids(self, file_list):
		''' Return a list of IDs given a list of filenames ending in "participantData" '''
		participant_ids = set()
		participant_data_files = filter(lambda x:x.endswith("participantData.pkl"), file_list) # Each session has a "participantData" file
		for f in participant_data_files:
			participant_id = self._get_participant_id(f)
			participant_ids.add(participant_id)
			
		return participant_ids

	def _get_participant_id(self, participant_data_file):
		# get the timestamp
		timestamp_end_index = participant_data_file.rfind("_")
		timestamp_start_index = participant_data_file.rfind("_", 0, timestamp_end_index)
		timestamp = participant_data_file[timestamp_start_index+1:timestamp_end_index]
		
		# get the participant ID
		participant_id = participant_data_file[:timestamp_start_index]
		
		return participant_id
		
	
	def get_participant_sessions(self, data_dir):
		''' Get all participant sessions from this directory. '''
		
		file_list = os.listdir(data_dir)
		participant_sessions = defaultdict(list) # {participant_id:[ParticipantSession]}

		# Get all the participant ids from this directory listing
		participant_ids = self._get_participant_ids(file_list)
		
		for participant_id in participant_ids:
			
#			print "PARTICIPANT: ", participant_id
			participant_data_files = filter(lambda x:x.endswith("participantData.pkl") and participant_id in x, file_list)
			
			# TODO: Hack: need to label the last set of participant trials as time pressure.  Time pressure trials are run last (in the pilot trails).
			num_sessions = len(participant_data_files)
			tp_timestamp = self._get_timestamp(max(sorted(participant_data_files, key=self._get_timestamp))) # Still used when the data saved in the OLD format
					
			for participant_data_file in participant_data_files:
				
				# get the timestamp
				timestamp_end_index = participant_data_file.rfind("_")
				timestamp_start_index = participant_data_file.rfind("_", 0, timestamp_end_index)
				timestamp = participant_data_file[timestamp_start_index+1:timestamp_end_index]
				
				# get the participant ID
				participant_id = participant_data_file[:timestamp_start_index]

				# get the session phase (Enums.Phase)
				phase = self._get_phase(file_list, participant_id, timestamp)
				
				# get the ParticipantTrials
				participant_trials = self._get_participant_trials(file_list, participant_id, timestamp, data_dir, tp_timestamp)
				
				# get bounding box data
				bounding_box_data = self._get_bounding_box_data(file_list, participant_id, timestamp, data_dir)
				
				# get participant data
				participant_data = self._get_participant_data(file_list, participant_id, timestamp, data_dir)
				print( participant_id)
				# create a participant session
				participant_session = ParticipantSession(data_dir, participant_id, timestamp, participant_trials, bounding_box_data, participant_data, phase)
				
#				print "SESSION:", participant_session
				
				participant_sessions[participant_id].append(participant_session)

		return participant_sessions

		
	def save_trial_data(self, data_dir, participant_id, timestamp, trial, intervention, \
		participant_position_data, participant_orientation_data, right_facing_car_position_data, left_facing_car_position_data, visual_obstruction_data=[]):
		''' Save the raw data for the trial.  Warning: Changing this to make more sense could break backwards compatibility for parsing old files. '''

		# save the trial number AND the attempt number to not lose data when switching between trials
		trial_and_attempt_number = trial.getTrialAndAttemptNumber() #trial.getTrialNumber()
		trial_type = trial.getTrialType()
		
		trial_data = (participant_position_data, participant_orientation_data, right_facing_car_position_data, left_facing_car_position_data, visual_obstruction_data, trial, intervention)
		
#		print '  HD: got trial data'
		
		filename_root = "%s%s_%s" % (data_dir, participant_id, timestamp)
		filename = "%s_%s" % (filename_root, trial_and_attempt_number)
		
		# if the trial is a practice trial, indicate this with a "_p" appended to the name
		if (trial_type == TrialType.PRACTICE):
			filename = filename + "_p"
			
		# if the trial is a speed test, indicate this with a "_st" appended to the name
		if (trial_type == TrialType.SpeedTest):
			filename = filename + "_st"
			
		if trial_type == TrialType.SpeedTest_Running:
			filename += "_str"
		
		# if the trial is a time pressure trial, indicate this with a "_tp" appended to the name
		if trial_type == TrialType.TimePresOn_PRE or trial_type == TrialType.TimePresOff_PRE or \
			trial_type == TrialType.TimePresOn_POST or trial_type == TrialType.TimePresOff_POST:
			filename = filename + "_tp"
		
		filename += "_dumpedData.pkl"
#		print 'about to open..'
		with open(filename, "wb") as file:
#			print 'opened; about to dump'
			pickle.dump(trial_data, file)
#		print 'dumped.'
		return trial_data 
		
		
	def save_participant_data(self, data_dir, participant_id, timestamp, participant_variables, participant_values):
		pdata = (participant_variables, participant_values)
		filename_root = "%s%s_%s" % (data_dir, participant_id, timestamp)
		filename = filename_root + "_participantData.pkl"
		with open(filename, "wb") as file:
			pickle.dump(pdata, file)
		
		
	def save_car_bounding_box_data(self, data_dir, participant_id, timestamp, all_car_models):
		# save car bounding box data to disk
		carBoundingBoxDict = {}
		for car in all_car_models:
			carBoundingBoxDict[car.getMeshFileName()] = \
				(car.getBoundingBox(viz.ABS_LOCAL).xmin, 
				car.getBoundingBox(viz.ABS_LOCAL).xmax,
				car.getBoundingBox(viz.ABS_LOCAL).zmin,
				car.getBoundingBox(viz.ABS_LOCAL).zmax)
		
		filename_root = "%s%s_%s" % (data_dir, participant_id, timestamp)
		filename = filename_root + "_boundingBoxData.pkl"
		with open(filename, "wb") as file:
			pickle.dump(carBoundingBoxDict, file)
		return carBoundingBoxDict