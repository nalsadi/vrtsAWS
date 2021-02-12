import Globals
import VariableNames
from BaseDataParser import BaseDataParser

from PathDetail import PathDetail # Store infomration about entering and exiting car path or road
from TrialDetail import TrialDetail

import os
import logging
#import pickle
import cPickle as pickle
#import vizmat
import math
import time

from Enums import *

NO_VALUE = '99999' # string used to fill space when no value is calculated
NO_VALUE_NUM = 99999

ROAD_START_Z_VALUE = 0
ROAD_MIDDLE_Z_VALUE = Globals.roadWidth / 2.0
ROAD_END_Z_VALUE = Globals.roadWidth / 2.0 

GAP_SIZE_M = 0
GAP_SIZE_S = 1

NEAR_MISS_TIME = 0
NEAR_MISS_DISTANCE = 1

MEMO_HITS_RIGHT = "RIGHT_HITS"
MEMO_HITS_LEFT = "LEFT_HITS"
MEMO_GAPS_RIGHT = "RIGHT_GAPS"
MEMO_GAPS_LEFT = "LEFT_GAPS"
MEMO_INDEX_BEFORE_LAST_ENTER_ROAD = "INDEX_BEFORE_LAST_ENTER_ROAD"
MEMO_INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD = "INDEX_BEFORE_LAST_CROSS_MIDDLE_OF_ROAD"
MEMO_INDEX_BEFORE_LAST_EXIT_ROAD = "_INDEX_BEFORE_LAST_EXIT_ROAD"
MEMO_INDEX_BEFORE_LAST_ENTER_RIGHT_CAR_PATH = "INDEX_BEFORE_LAST_ENTER_RIGHT_CAR_PATH"
MEMO_INDEX_BEFORE_LAST_EXIT_RIGHT_CAR_PATH = "INDEX_BEFORE_LAST_EXIT_RIGHT_CAR_PATH"
MEMO_INDEX_BEFORE_LAST_ENTER_LEFT_CAR_PATH = "INDEX_BEFORE_LAST_ENTER_LEFT_CAR_PATH"
MEMO_INDEX_BEFORE_LAST_EXIT_LEFT_CAR_PATH = "INDEX_BEFORE_LAST_EXIT_LEFT_CAR_PATH"
MEMO_CAR_PATH_TIMES_LEFT = "CAR_PATH_TIMES_LEFT"
MEMO_CAR_PATH_TIMES_RIGHT = "CAR_PATH_TIMES_RIGHT"


class RawDataParser(BaseDataParser):
	''' Load and parse all the raw data that was pickled during the trials.	'''

	def __init__(self, participant_session, mean_walking_speed_HMDV, mean_walking_speed_RWV, mean_running_speed_RWV):	

		self._participant_session = participant_session
		self.__meanWalkingSpeedHMDV = mean_walking_speed_HMDV
		self.__meanWalkingSpeedRWV = mean_walking_speed_RWV
		self.__meanRunningSpeedRWV = mean_running_speed_RWV

		# Create a logger
		self.__logger = logging.getLogger ("mainlogger.RawDataParser")
		
		# Get the bounding box data for each car model
		self.__carBoundingBoxDict = participant_session.get_bounding_box_data()
		self._participant_data = participant_session.get_participant_data()
		
		# A dictionary that saves all the data for all the trials (key = trialNumber)
		self.__trialsDataDictionary = {}

	# Used to time the functions
	def print_timing(func):
		def wrapper(*arg):
			t1 = time.clock()
			res = func(*arg)
			t2 = time.clock()
			#print '%s took %0.3f s' % (func.func_name, (t2-t1))
			return res
		return wrapper

	def _get_num_road_entrances(self, trial_dict):
		''' return the number of lines required to output this trial to SPSS '''
		if VariableNames.HeadAngleOnEnterRoad not in trial_dict:
			return 0
		if not trial_dict[VariableNames.HeadAngleOnEnterRoad]: # check that there are HeadAngles for the RFC data, if not, no road entrances/practice trials.
			num_spss_lines = 0
		else:
			num_spss_lines = len(trial_dict[VariableNames.HeadAngleOnEnterRoad]) # one line for each road entrance 
		return num_spss_lines

	def _get_road_entrance_lines(self, participant_trial, trial_dict):
		''' Return the SPSS lines for the road entrances of this trial. '''
		# Map the variables for this practice trial to their values
		spss_lines = []
		num_trial_spss_lines = self._get_num_road_entrances(trial_dict)
		
		var_list = VariableNames.get_var_names_list()
		var_map = {
			VariableNames.ParticipantId: self._participant_session.get_participant_id(),
			VariableNames.FileName: participant_trial.get_filename(),
			VariableNames.TrialNumber: participant_trial.get_trial_number(),
			VariableNames.AttemptNumber: participant_trial.get_attempt_number(),
			VariableNames.LastModified: participant_trial.get_last_modified(),
			VariableNames.Phase: Phase.toStr(self._participant_session.get_phase()),
			VariableNames.TrialType: TrialType.toStr(participant_trial.get_trial_type()),
			VariableNames.MeanWalkingSpeedHMDV: self.__meanWalkingSpeedHMDV,
			VariableNames.MeanWalkingSpeedRWV: self.__meanWalkingSpeedRWV,
			VariableNames.MeanRunningSpeedRWV: self.__meanRunningSpeedRWV
		}

		# Fill in the PER ROAD ENTRANCE lines 
		per_road_entrance_lines = VariableNames.get_per_road_entrance_variables()
		for i in range(0, num_trial_spss_lines):
			spss_line = ""
			for var_name in var_list:
				if var_name == VariableNames.RoadEntrance:
					value = i + 1 #save the road entrance
				elif var_name == VariableNames.SimulatedHitHMDV:
					if trial_dict.get(var_name)[0] != None:
						value = trial_dict.get(var_name)[0][i] # SimHit returns a Tuple of lists... hnnng.
					else:
						value = None
				elif var_name == VariableNames.SimulatedHitRWV: # This is exceptionally ugly
					if trial_dict.get(var_name)[0] != None:
						value = trial_dict.get(var_name)[0][i]
					else:
						value = None
				elif var_name in per_road_entrance_lines:
					value = trial_dict.get(var_name)[i]
				else:
					value = var_map.get(var_name, NO_VALUE)
					
				spss_line += str(value) + ';'

			spss_lines.append(spss_line)
			
		return spss_lines
			

	def _get_summary_line(self, participant_trial, trial_dict):
		''' Return the summary for this trial '''

		spss_line = ""
		var_list = VariableNames.get_var_names_list()
		tuple_variables = VariableNames.get_tuple_variables()
		per_road_entrance_variables = VariableNames.get_per_road_entrance_variables()
		
		num_road_entrances = self._get_num_road_entrances(trial_dict)
		trial_dict[VariableNames.RoadEntrance] = "summary"
		
		for var_name in var_list:
			value = trial_dict.get(var_name, NO_VALUE)
			if value is not NO_VALUE:
				if var_name in tuple_variables:
					value = value[0] #TODO: HACK for pilot data use the RFC data

				# Special cases
				if var_name == VariableNames.NearMisses:
					# for near misses, print the length of the dictionary  -- near misses always returns a {}
					value = len(value)
				elif var_name == VariableNames.TrialResult:
					value = TrialResult.toStr(value)

				# Road entrance lines - use the last road entrance value in the summary
				if var_name in per_road_entrance_variables:
					if num_road_entrances == 0 or value == None:
						value = NO_VALUE
					else:
						value = value[-1] # Use the last road entrance value

			spss_line += str(value) + ";"
			
		return spss_line

	def get_spss_output(self):
		''' Return output for the trials formatted for SPSS. '''

		if not self.__trialsDataDictionary:
			print "PARSING TRIALS BEFORE GENERATING SPSS OUTPUT (participant: %s timestamp: %s)" % (self._participant_session.get_participant_id(), self._participant_session.get_timestamp())
			self.parseTrials()
			
		var_list = VariableNames.get_var_names_list()
		spss_lines = []

		for participant_trial in self.__trialsDataDictionary:
			print "\n" + "Trial Information " + "Trial Type: " + participant_trial.get_trial_cond() + " PRE/POST: " + participant_trial.get_trial_prepost() +  "\n" + "\n"
			trial_dict = self.__trialsDataDictionary[participant_trial]
			
			road_entrance_lines = self._get_road_entrance_lines(participant_trial, trial_dict)
			spss_lines.extend(road_entrance_lines)
				
			summary_line = self._get_summary_line(participant_trial, trial_dict)
			spss_lines.append(summary_line)
		
		return spss_lines

	@print_timing
	def parseTrials(self):
		
		# get the non-practice trials
		participant_session = self._participant_session
		trials = participant_session.get_trials()
		
		# Perform calculations on each of the trials
		for participant_trial in trials:
			
			# Store the master data for this trial
			trialDataDictionary = {}

			# Load the trial data
			print "Trial %s (%s)" % (participant_trial.get_trial_and_attempt_number(), participant_trial.get_filename())
			raw_data = participant_trial.get_raw_data()
			trialData = TrialDetail(raw_data, self.__carBoundingBoxDict)
			
			# -------------------------------
			# Participant & Trial Information
			# -------------------------------
			
			#trial_and_attempt_number = super(RawDataParser, self).get_trial_and_attempt_number(filename, self.__timeStamp)
			trialDataDictionary[VariableNames.ParticipantId] = participant_session.get_participant_id()#self.__participantId
			trialDataDictionary[VariableNames.FileName] = participant_trial.get_filename()
			trialDataDictionary[VariableNames.TrialNumber] = participant_trial.get_trial_number()
			trialDataDictionary[VariableNames.AttemptNumber] = participant_trial.get_attempt_number()
			trialDataDictionary[VariableNames.LastModified] = participant_trial.get_last_modified()
			trialDataDictionary[VariableNames.TrialType] = TrialType.toStr(participant_trial.get_trial_type())
			trialDataDictionary[VariableNames.LeftFacingCarSpeed] = participant_trial.get_left_facing_car_speed()
			trialDataDictionary[VariableNames.RightFacingCarSpeed] = participant_trial.get_right_facing_car_speed()
			trialDataDictionary[VariableNames.MeanWalkingSpeedHMDV] = self.__meanWalkingSpeedHMDV
			trialDataDictionary[VariableNames.MeanWalkingSpeedRWV] = self.__meanWalkingSpeedRWV
			trialDataDictionary[VariableNames.MeanRunningSpeedRWV] = self.__meanRunningSpeedRWV
			trialDataDictionary[VariableNames.Phase] = Phase.toStr(self._participant_session.get_phase())
#			
#			# TRIAL RESULT
#			trial_result = self.getTrialResult(trialData)
#			trialDataDictionary[VariableNames.TrialResult] = trial_result
#
#			if trial_result == TrialResult.ENTERED_BEFORE_FIRST_CAR:
#				#print "ENTERED BEFORE FIRST CAR"
#				self.__trialsDataDictionary[participant_trial] = trialDataDictionary
#				continue
#
#			
#			#DURATION
			trialDataDictionary[VariableNames.TrialDuration] = self.calculateTrialDuration(trialData)
			trialDataDictionary[VariableNames.DurationInRoad] = self.calculateDurationInRoad(trialData) #for each road entrance [dur1, dur2, etc]
##			trialDataDictionary[VariableNames.DurationInCarPath] = self.calculateDurationInCarPath(trialData) # for the last car path entrance
#			trialDataDictionary[VariableNames.DurationInMiddleOfRoad] = self.calculateDurationInMiddleOfRoad(trialData) # Duration in Middle of Road in need to find output of this function
#			trialDataDictionary[VariableNames.DurationInMiddleOfRoadList] = self.calculateDurationInMiddleOfRoadList(trialData) # Duration in Middle of Road in need to find output of this function
#			trialDataDictionary[VariableNames.DurationInMiddleOfRoadSum] = self.calculateDurationInMiddleOfRoadSum(trialData) # Duration in Middle of Road in need to find output of this function
##			# NUMBER OF CHECKS (FULL/PARTIAL, IN ROAD/ON SIDEWALK/IN CAR PATH/BETWEEN CURB AND CAR PATH)
##			trialDataDictionary[VariableNames.FullChecksInRoad] = self.calculate_number_of_full_checks_in_road(trialData)
##			trialDataDictionary[VariableNames.FullChecksOnSidewalk] = self.calculate_number_of_full_checks_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.FullChecksInCarPath] = self.calculate_number_of_full_checks_in_car_path(trialData)
##			trialDataDictionary[VariableNames.FullChecksBetweenCurbAndCarPath] = self.calculate_number_of_full_checks_between_curb_and_car_path(trialData)
##			trialDataDictionary[VariableNames.PartialChecksInRoad] = self.calculate_number_of_partial_checks_in_road(trialData)
##			trialDataDictionary[VariableNames.PartialChecksOnSidewalk] = self.calculate_number_of_partial_checks_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.PartialChecksInCarPath] = self.calculate_number_of_partial_checks_in_car_path(trialData)
##			trialDataDictionary[VariableNames.PartialChecksBetweenCurbAndCarPath] = self.calculate_number_of_partial_checks_between_curb_and_car_path(trialData)
##			
##			trialDataDictionary[VariableNames.FullChecksWithClosestCarInViewInRoad] = self.calculate_full_checks_with_car_in_view_in_road(trialData)
##			trialDataDictionary[VariableNames.FullChecksWithClosestCarInViewOnSidewalk] = self.calculate_full_checks_with_car_in_view_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.FullChecksWithClosestCarInViewInCarPath] = self.calculate_full_checks_with_car_in_view_in_car_path(trialData)
##			trialDataDictionary[VariableNames.FullChecksWithClosestCarInViewBetweenCurbAndCarPath] = self.calculate_full_checks_with_car_in_view_between_curb_and_car_path(trialData)
##			trialDataDictionary[VariableNames.PartialChecksWithClosestCarInViewInRoad] = self.calculate_partial_checks_with_car_in_view_in_road(trialData)
##			trialDataDictionary[VariableNames.PartialChecksWithClosestCarInViewOnSidewalk] = self.calculate_partial_checks_with_car_in_view_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.PartialChecksWithClosestCarInViewInCarPath] = self.calculate_partial_checks_with_car_in_view_in_car_path(trialData)
##			trialDataDictionary[VariableNames.PartialChecksWithClosestCarInViewBetweenCurbAndCarPath] = self.calculate_partial_checks_with_car_in_view_between_curb_and_car_path(trialData)
##			
##			# MEAN CHECK TIME (FULL/PARTIAL, IN ROAD/ON SIDEWALK/IN CAR PATH/BETWEEN CURB AND CAR PATH)
##			trialDataDictionary[VariableNames.MeanFullCheckTimeInRoad] = self.calculate_mean_full_check_time_in_road(trialData)
##			trialDataDictionary[VariableNames.MeanFullCheckTimeOnSidewalk] = self.calculate_mean_full_check_time_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.MeanFullCheckTimeInCarPath] = self.calculate_mean_full_check_time_in_car_path(trialData)
##			trialDataDictionary[VariableNames.MeanFullCheckTimeBetweenCurbAndCarPath] = self.calculate_mean_full_check_time_between_curb_and_car_path(trialData)
##			trialDataDictionary[VariableNames.MeanPartialCheckTimeInRoad] = self.calculate_mean_partial_check_time_in_road(trialData)
##			trialDataDictionary[VariableNames.MeanPartialCheckTimeOnSidewalk] = self.calculate_mean_partial_check_time_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.MeanPartialCheckTimeInCarPath] = self.calculate_mean_partial_check_time_in_car_path(trialData)
##			trialDataDictionary[VariableNames.MeanPartialCheckTimeBetweenCurbAndCarPath] = self.calculate_mean_partial_check_time_between_curb_and_car_path(trialData)
##			trialDataDictionary[VariableNames.MeanTimeWithClosestCarInViewInRoad] = self.calculate_mean_car_in_view_check_time_in_road(trialData)
##			trialDataDictionary[VariableNames.MeanTimeWithClosestCarInViewOnSidewalk] = self.calculate_mean_car_in_view_check_time_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.MeanTimeWithClosestCarInViewInCarPath] = self.calculate_mean_car_in_view_check_time_in_car_path(trialData)
##			trialDataDictionary[VariableNames.MeanTimeWithClosestCarInViewBetweenCurbAndCarPath] = self.calculate_mean_car_in_view_check_time_between_curb_and_car_path(trialData)
##			
##			# PERCENT CHECKING (FULL/PARTIAL, IN ROAD/ON SIDEWALK/IN CAR PATH/BETWEEN CURB AND CAR PATH)
##			trialDataDictionary[VariableNames.PercentFullCheckingInRoad] = self.calculate_percent_full_checking_in_road(trialData)
##			trialDataDictionary[VariableNames.PercentFullCheckingOnSidewalk] = self.calculate_percent_full_checking_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.PercentFullCheckingInCarPath] = self.calculate_percent_full_checking_in_car_path(trialData)
##			trialDataDictionary[VariableNames.PercentFullCheckingBetweenCurbAndCarPath] = self.calculate_percent_full_checking_between_curb_and_car_path(trialData)
##			trialDataDictionary[VariableNames.PercentPartialCheckingInRoad] = self.calculate_percent_partial_checking_in_road(trialData)
##			trialDataDictionary[VariableNames.PercentPartialCheckingOnSidewalk] = self.calculate_percent_partial_checking_on_sidewalk(trialData)
##			trialDataDictionary[VariableNames.PercentPartialCheckingInCarPath] = self.calculate_percent_partial_checking_in_car_path(trialData)
##			trialDataDictionary[VariableNames.PercentPartialCheckingBetweenCurbAndCarPath] = self.calculate_percent_partial_checking_between_curb_and_car_path(trialData)
##						
##			#TODO: NEED TESTING
#			trialDataDictionary[VariableNames.LFCInViewOnMiddleOfRoadEntry] = self.calculate_is_looking_at_far_lane_car_on_middle_of_road_entry(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestLFCInViewInNearLane] = self.calculate_percent_closest_LFC_in_view_in_near_lane(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestRFCInViewInNearLane] = self.calculate_percent_closest_RFC_in_view_in_near_lane(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestLFCInViewInFarLane] = self.calculate_percent_time_closest_LFC_in_view_in_far_lane(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestRFCInViewInFarLane] = self.calculate_percent_time_closest_RFC_in_view_in_far_lane(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestLFCInViewBetweenCarPaths] = self.calculate_percent_time_closest_LFC_in_view_between_car_paths(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestRFCInViewBetweenCarPaths] = self.calculate_percent_time_closest_RFC_in_view_between_car_paths(trialData)

			###
			
#			trialDataDictionary[VariableNames.PercentTimeClosestCarInViewInRoad] = self.calculate_percent_closest_car_in_view_in_road(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestCarInViewOnSidewalk] = self.calculate_percent_closest_car_in_view_on_sidewalk(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestCarInViewInCarPath] = self.calculate_percent_closest_car_in_view_in_car_path(trialData)
#			trialDataDictionary[VariableNames.PercentTimeClosestCarInViewBetweenCurbAndCarPath] = self.calculate_percent_closest_car_in_view_between_curb_and_car_path(trialData)
#			
#			# PERCENT TIME CLOSEST CAR WAS IN VIEW DURING FULL/PARTIAL CHECKS
#			trialDataDictionary[VariableNames.PctFullCheckingInRoadCarInView] = self.calculate_pct_full_checking_with_car_in_view_in_road(trialData)
#			trialDataDictionary[VariableNames.PctFullCheckingOnSidewalkCarInView] = self.calculate_pct_full_checking_with_car_in_view_on_sidewalk(trialData)
#			trialDataDictionary[VariableNames.PctFullCheckingInCarPathCarInView] = self.calculate_pct_full_checking_with_car_in_view_in_car_path(trialData)
#			trialDataDictionary[VariableNames.PctFullCheckingBetweenCurbAndCarPathCarInView] = self.calculate_pct_full_checking_with_car_in_view_between_curb_and_car_path(trialData)
#			trialDataDictionary[VariableNames.PctPartialCheckingInRoadCarInView] = self.calculate_pct_partial_checking_with_car_in_view_in_road(trialData)
#			trialDataDictionary[VariableNames.PctPartialCheckingOnSidewalkCarInView] = self.calculate_pct_partial_checking_with_car_in_view_on_sidewalk(trialData)
#			trialDataDictionary[VariableNames.PctPartialCheckingInCarPathCarInView] = self.calculate_pct_partial_checking_with_car_in_view_in_car_path(trialData)
#			trialDataDictionary[VariableNames.PctPartialCheckingBetweenCurbAndCarPathCarInView] = self.calculate_pct_partial_checking_with_car_in_view_between_curb_and_car_path(trialData)
#			
#			# HEAD ANGLE ON ENTER CAR PATH (last forward entrance)
#			trialDataDictionary[VariableNames.HeadAngleOnEnterCarPath] = self.calculateHeadAngleOnEnterCarPath(trialData)
#			
#			# MEAN HEAD ANGLE IN CAR PATH (last forward entrance)
#			trialDataDictionary[VariableNames.MeanHeadAngleInCarPath] = self.calculateMeanHeadAngleInCarPath(trialData)
#
#			# HITS - CURRENTLY RETURNS A LIST OF INDICIES OF THE POSITION DATA WHEN THE PARTICIPANT IS HIT, for left-facing, right, overall
#			trialDataDictionary[VariableNames.Hits] = tuple(map(len, self.calculateHits(trialData)))
#			self.__logger.info("Hits: " + str(trialDataDictionary[VariableNames.Hits]))
#
#			# NEAR MISSES
#			trialDataDictionary[VariableNames.NearMisses] = self.calculateNearMisses(trialData)
#			self.__logger.info("Near misses: " + str(trialDataDictionary[VariableNames.NearMisses]))
#			
#			#TODO: HACK for RFC
#			trialDataDictionary[VariableNames.NearMissDistance] = self.getNearMissDistance(trialDataDictionary[VariableNames.NearMisses][0])
#			self.__logger.info("Near miss distance: " + str(trialDataDictionary[VariableNames.NearMissDistance]))
#			
#			#TODO: HACK for RFC
#			trialDataDictionary[VariableNames.NearMissTime] = self.getNearMissTime(trialDataDictionary[VariableNames.NearMisses][0])
#			self.__logger.info("Near miss time (minimum): " + str(trialDataDictionary[VariableNames.NearMissTime]))
#
#			# JUMP BACKS
#			trialDataDictionary[VariableNames.JumpBacks] = self.calculateJumpBacks(trialData)
#			self.__logger.info("Jump backs: " + str(trialDataDictionary[VariableNames.JumpBacks]))
#			
#			# ----------------------------------------------
#			# Crossing choice functions (TLS / missed opps)
#			# ----------------------------------------------
#			
#			# MISSED OPPORTUNITIES - NEED AVERAGE CROSSING TIME
#			trialDataDictionary[VariableNames.MissedOpportunities] = self.calculateMissedOpportunities(trialData)
#			self.__logger.info("Missed opportunities: " + str(trialDataDictionary[VariableNames.MissedOpportunities]))
#			
#			# TLS ON LOSS OF VIEW
#			trialDataDictionary[VariableNames.TLSOnLossOfView] = self.calculate_time_left_to_spare_on_loss_of_view(trialData)
#			self.__logger.info("Time left to spare on loss of view: " + str(trialDataDictionary[VariableNames.TLSOnLossOfView]))
#
#			# TLS ENTER ROAD
#			trialDataDictionary[VariableNames.TLSEnterRoad] = self.calculateTimeLeftToSpareOnEnterRoad(trialData)
#			self.__logger.info("Time left to spare on entering road: " + str(trialDataDictionary[VariableNames.TLSEnterRoad]))
#			
#			# TLS ENTER CAR PATH
#			trialDataDictionary[VariableNames.TLSEnterCarPath] = self.calculateTimeLeftToSpareOnEnterCarPath(trialData)
#			self.__logger.info("Time left to spare on entering car path: " + str(trialDataDictionary[VariableNames.TLSEnterCarPath]))
#			
#			# TLS EXIT CAR PATH
#			trialDataDictionary[VariableNames.TLSExitCarPath] = self.calculateTimeLeftToSpareOnExitCarPath(trialData)
#			self.__logger.info("Time left to spare on exiting car path: " + str(trialDataDictionary[VariableNames.TLSExitCarPath]))
#			
#			trialDataDictionary[VariableNames.TLSExitCarPathAvgWalkingSpeedRWV] = self.calculate_tls_on_exit_car_path_at_mean_walking_speed_RWV(trialData)
#			self.__logger.info("Time left to spare on exit car path at average walking speed (RWV): " + str(trialDataDictionary[VariableNames.TLSExitCarPathAvgWalkingSpeedRWV]))
#			
#			trialDataDictionary[VariableNames.TLSExitCarPathAvgWalkingSpeedHMDV] = self.calculate_tls_on_exit_car_path_at_mean_walking_speed_HMDV(trialData)
#			self.__logger.info("Time left to spare on exit car path at average walking speed (HMDV): " + str(trialDataDictionary[VariableNames.TLSExitCarPathAvgWalkingSpeedHMDV]))
#			
#			# CROSSING TIME
#			trialDataDictionary[VariableNames.CrossingTime] = self.calculateCrossingTime(trialData)
#			self.__logger.info("Crossing time: " + str(trialDataDictionary[VariableNames.CrossingTime]))
#			
#			# START DELAY
#			trialDataDictionary[VariableNames.StartDelay] = self.calculateStartDelay(trialData)
#			self.__logger.info("Start delay: " + str(trialDataDictionary[VariableNames.StartDelay]))
#			
#			# ------------------
#			# Velocity functions
#			# ------------------
#			
#			# VEL ENTER ROAD
#			trialDataDictionary[VariableNames.VelEnterRoad] = self.calculateVelocityOnEnterRoad(trialData)
#			self.__logger.info("Velocity on entering road: " + str(trialDataDictionary[VariableNames.VelEnterRoad]))
#			
#			# VEL ENTER CAR PATH
#			trialDataDictionary[VariableNames.VelEnterCarPath] = self.calculateVelocityOnEnterCarPath(trialData)
#			self.__logger.info("Velocity on entering car path: " + str(trialDataDictionary[VariableNames.VelEnterCarPath]))
#			
#			# VEL EXIT CAR PATH
#			trialDataDictionary[VariableNames.VelExitCarPath] = self.calculateVelocityOnExitCarPath(trialData)
#			self.__logger.info("Velocity on exiting car path: " + str(trialDataDictionary[VariableNames.VelExitCarPath]))
#			
#			# MAX VEL IN CAR PATH
#			trialDataDictionary[VariableNames.MaxVelInCarPath] = self.calculateMaximumVelocityInCarPath(trialData)
#			self.__logger.info("Maximum velocity in car path: " + str(trialDataDictionary[VariableNames.MaxVelInCarPath]))
#			
#			# MIN VEL IN CAR PATH
#			trialDataDictionary[VariableNames.MinVelInCarPath] = self.calculateMinimumVelocityInCarPath(trialData)
#			self.__logger.info("Minimum velocity in car path: " + str(trialDataDictionary[VariableNames.MinVelInCarPath]))
#			
#			
#			# ---------------------
#			# Gap-related functions
#			# ---------------------
#			
#			# GAP LENGTH - a list of the gaps
#			trialDataDictionary[VariableNames.GapLength] = self.calculateGapLength(trialData)
#			self.__logger.info("Gap length: " + str(trialDataDictionary[VariableNames.GapLength]))
#			
#			# GAP INTERVAL
#			trialDataDictionary[VariableNames.GapInterval] = self.calculateGapInterval(trialData)
#			self.__logger.info("Gap interval: "  + str(trialDataDictionary[VariableNames.GapInterval]))
#			
#			# PERCENTAGE OF GAP USED -- runs through to here
#			trialDataDictionary[VariableNames.PercentageOfGapUsed] = self.calculatePercentageOfGapUsed(trialData)
#			self.__logger.info("Percentage of gap used: " + str(trialDataDictionary[VariableNames.PercentageOfGapUsed]))
#			
#			# MAX REJECTED GAP TIME
#			trialDataDictionary[VariableNames.MaxRejectedGapTime] = self.calculateMaxRejectedGapTime(trialData)
#			self.__logger.info("Maximum rejected gap time: " + str(trialDataDictionary[VariableNames.MaxRejectedGapTime]))
#			
#			# AVERAGE REJECTED GAP TIME
#			trialDataDictionary[VariableNames.AverageRejectedGapTime] = self.calculateAverageRejectedGapTime(trialData)
#			self.__logger.info("Average rejected gap time: " + str(trialDataDictionary[VariableNames.AverageRejectedGapTime]))
#			
#			# MIN REJECTED GAP TIME
#			trialDataDictionary[VariableNames.MinRejectedGapTime] = self.calculateMinRejectedGapTime(trialData)
#			self.__logger.info("Minimum rejected gap time: " + str(trialDataDictionary[VariableNames.MinRejectedGapTime]))
#			
#			# MARGIN OF SAFETY
#			trialDataDictionary[VariableNames.MarginOfSafety] = self.calculateMarginOfSafety(trialData)
#			self.__logger.info("Margin of safety: " + str(trialDataDictionary[VariableNames.MarginOfSafety]))
#			
#			# ---------------
#			# Traffic volume
#			# ---------------
#			
#			# TRAFFIC VOLUME
#			trialDataDictionary[VariableNames.TrafficVolume] = self.calculateTrafficVolume(trialData)
#			self.__logger.info("Traffic volume (number of cars passed by): " + str(trialDataDictionary[VariableNames.TrafficVolume]))
#			
#			# TRAFFIC VOLUME PER MINUTE
#			trialDataDictionary[VariableNames.TrafficVolumePerMinute] = self.calculateTrafficVolumePerMinute(trialData)
#			self.__logger.info("Traffic volume per minute: " + str(trialDataDictionary[VariableNames.TrafficVolumePerMinute]))

			# ------------------------------
			# Store this trial's master data
			# ------------------------------
			
			# Save this trial in the data dictionary containing all the trials' data
			self.__trialsDataDictionary[participant_trial] = trialDataDictionary
			
		return self.__trialsDataDictionary
		
	
	def getTrialResult(self, trialData):
		''' Return the Enums.TrialResult for this trial '''
		return trialData.get_trial_result()
		
	@print_timing
	def calculateJumpBacks(self, trialData):
		'''
		Calculate the number of times a participant 'jumped back'
		during the trial.  This is determined by a change in velocity
		from positive to negative after they have entered the road for
		the first time.
		'''
		
		#Local variables
		jumpBacks = 0
		movingBackward = False
		inRoad = False
		positionData = trialData.get_participant().get_position_data()
		
		# Average walking speeds range from 5.3 - 5.4 in younger people, 4.5 - 4.8 in older people; this is less than 10x the average.
		VELOCITY_THRESHOLD = 0.2
		first_car_arrived_t = trialData.get_time_first_car_arrived(Direction.RIGHT)

		# Parse the trial data, looking for a change in velocity
		for i in range(len(positionData)-1):
			t = positionData[i][PositionData.TIME]
			if t < first_car_arrived_t:
				continue
			
			# z value for each moment
			moment = positionData[i]
			z = moment[PositionData.POSITION][Position.Z_POS]
			
			# participant entered the road
			if (z > 0):
				inRoad = True
			else:
				inRoad = False				

			# while the participant is crossing the road, calculate their z-velocity from
			# moment to moment and check if it becomes negative.
			if (inRoad):
				previousMoment = positionData[i-1]
				velocity_z = super(RawDataParser, self).calculateParticipantMomentaryVelocityZ(previousMoment, moment)
				
				#print "JB: velocity_z = %s, round(vel_z, 2) = %s " % (str(velocity_z), str(round(velocity_z, 1)))

				if (movingBackward == False):
					# if the participant moved backwards, add a jump back
					# and wait for them to move forward again
					if (velocity_z < -VELOCITY_THRESHOLD):
						print "JUMPED BACK"
						jumpBacks += 1
						movingBackward = True
				else:
					# if they were moving backward, and now they're moving forward
					# set that they're moving forward again
					if (velocity_z > 0):
						movingBackward = False
						
				# if get_closest_car fails (which should be rare), fail this calculation gracefully
				if trialData.get_closest_car(t, Direction.RIGHT) == None:
					print "Warning: (calculateJumpBacks) could not find closest car - stopping JumpBack calculation"
					self.__logger.info("Warning: (calculateJumpBacks) could not find closest car - stopping JumpBack calculation")
					return NO_VALUE_NUM
					
				#if the participant leaves the car path on the far side, stop counting
				if (z > trialData.get_closest_car(t, Direction.RIGHT).get_far_side_z(t)):
					break
			
		return jumpBacks

	@print_timing
	def calculateSimulatedHitHMDV(self, trialData):
		rightFacingSimulatedHits = self.__calculate_simulated_hits_HMDV(trialData, Direction.RIGHT) # a list
		leftFacingSimulatedHits = self.__calculate_simulated_hits_HMDV(trialData, Direction.LEFT)
		
		# Return a list of simulated hit calculations for each road entrance
		return (rightFacingSimulatedHits, leftFacingSimulatedHits, None)
		
	def calculateSimulatedHitRWV(self, trialData):
		rightFacingSimulatedHits = self.__calculate_simulated_hits_RWV(trialData, Direction.RIGHT)
		leftFacingSimulatedHits = self.__calculate_simulated_hits_RWV(trialData, Direction.LEFT)
		
		# Return a list of simulated hit calculations for each road entrance
		return (rightFacingSimulatedHits, leftFacingSimulatedHits, None)
		
	def calculateDurationInRoad(self,trialData):
		''' Get a list of the road durations for each road entrance '''
		road_entrances = trialData.get_road_details_forward_entrance()
		re_durations = []
		for re in road_entrances:
			re_durations.append(re.get_duration())
			
		return re_durations
		
	def calculateDurationInMiddleOfRoad(self,trialData):
		#print "Enter calculateDurationInMiddleOfRoad"
		''' Get a list of the road durations for each road entrance '''
		#### --- Duration in Road
		road_entrances = trialData.get_between_car_path_details()
		re_durations = None
		for re in road_entrances:
			re_durations = re.get_duration()
		#print("Duration: ", re_durations)	
		return re_durations
		
	def calculateDurationInMiddleOfRoadList(self,trialData):
		''' Get a list of the road durations '''
		road_entrances = trialData.get_between_car_path_details()
		durationList = []
		print(road_entrances)
		for re in road_entrances:
			durationList.append(re.get_duration())
		return durationList
		
	def calculateDurationInMiddleOfRoadSum(self,trialData):
		''' Get a list of the road durations '''
		road_entrances = trialData.get_between_car_path_details()
		durationList = []
		print(road_entrances)
		for re in road_entrances:
			durationList.append(re.get_duration())
		return sum(durationList)
		
	def calculateHeadAngleOnEnterRoad(self, trialData):
		head_angles = self.__calculate_head_angle_on_enter_road(trialData) # head angle on each enter road
		return head_angles
		
	def calculateMeanHeadAngleInRoad(self, trialData):
		head_angles = self.__calculate_mean_head_angle_in_road(trialData) # mean head angle each time the participant is in the road
		return head_angles
		
	def calculatePercentCheckingInRoad(self, trialData):
#		 percent_looking = [[ON_SIDEWALK, IN_ROAD],...]
		percent_looking = self.__calculate_percent_time_looking(trialData) # % time that a participant is more than the partial check value in a road/sidewalk
		percent_checking_road = [x[PercentChecking.IN_ROAD] for x in percent_looking]
		return percent_checking_road
		
	def calculatePercentCheckingOnSidewalk(self, trialData):
		percent_looking = self.__calculate_percent_time_looking(trialData) # % time that a participant is more than the partial check value in a road/sidewalk
		percent_checking_sidewalk = [x[PercentChecking.ON_SIDEWALK] for x in percent_looking]
		return percent_checking_sidewalk
	
	def calculateHeadAngleOnEnterCarPath(self, trialData):
		''' Return the head angle of the participant when they entered a car's path for the last time '''
		head_angle = self._calculate_head_angle_on_enter_car_path(trialData)
		return head_angle
		
	def calculateMeanHeadAngleInCarPath(self, trialData):
		''' Return the mean head angle of the participant during their final car path entrance '''
		mean_head_angle = self._calculate_mean_head_angle_in_car_path(trialData)
		return mean_head_angle
	
	def calculatePercentCheckingInCarPath(self, trialData):
		''' Return the % of time that the participant was FULL checking while in the car's path for the last time '''
		percent_checking = self._calculate_percent_checking_in_car_path(trialData)
		return percent_checking
		
	def calculateDurationInCarPath(self, trialData):
		''' Return the duration spent in the car path, for the final car path entrance. '''
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not car_path_detail:
			#return None
			return NO_VALUE_NUM
			
		return car_path_detail.get_duration()

	
	def __calculate_head_angle_on_enter_road(self, trialData):
		''' Calculate the head angle of the participant on each road entrance '''
		head_angles = []
		road_details = trialData.get_road_details_forward_entrance()
		for road_detail in road_details:
			yaw = trialData.get_participant().get_moment(road_detail.get_enter_time()).get_yaw()
			head_angles.append(yaw)
			
		return head_angles
		
	def _calculate_head_angle_on_enter_car_path(self, trialData):
		''' Calculate the head angle of the participant on each car path entrance '''
		head_angles = []
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not car_path_detail:
			return NO_VALUE_NUM
		
		yaw = trialData.get_participant().get_moment(car_path_detail.get_enter_time()).get_yaw()
		return yaw
			
	def __calculate_mean_head_angle_in_road(self, trialData):
		''' Calculate the mean head angle of the participant while they are in the road for each entrance '''
		head_angles = []
		road_details = trialData.get_road_details_forward_entrance()
		participant = trialData.get_participant()
		for road_detail in road_details:
			total_yaw = 0
			total_time = 0
			enter_time = road_detail.get_enter_time()
			exit_time = road_detail.get_exit_time()
			if not exit_time:
				# Operator intervened or hit
				exit_time = participant.get_last_moment().get_time()
			
			#total_time = exit_time - enter_time
			in_road_times = [t for t in sorted(participant.get_participant_dict()) if t >= enter_time and t < exit_time]
			num_keys = len(in_road_times)
			#print "IN ROAD KEYS: ", in_road_times
			
			for t in in_road_times:
				yaw = participant.get_moment(t).get_yaw()
				total_yaw += yaw
			
			mean_angle = total_yaw / num_keys
			
			head_angles.append(mean_angle)
			
		return head_angles
		
	def _calculate_mean_head_angle_in_car_path(self, trialData):
		''' Calculate the mean head angle of the participant while they are in the road for each entrance '''
		mean_head_angle = None
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not car_path_detail:
			#return None
			return NO_VALUE_NUM

		participant = trialData.get_participant()
		total_yaw = 0
		total_time = 0
		
		enter_time = car_path_detail.get_enter_time()
		exit_time = car_path_detail.get_exit_time()
		if not exit_time:
			# Operator intervened or hit
			exit_time = participant.get_last_moment().get_time()
		in_car_path_times = [t for t in sorted(participant.get_participant_dict()) if t >= enter_time and t < exit_time]
		num_keys = len(in_car_path_times)
		# fail gracefully if there are no keys (shouldn't happen under normal operation)
		if num_keys < 1:
			print "Warning: (mean_head_angle_in_car_path) no time in car path - cannot calculate"
			self.__logger.info("Warning: (mean_head_angle_in_car_path) no time in car path - cannot calculate")
			return NO_VALUE_NUM
		
		for t in in_car_path_times:
			yaw = participant.get_moment(t).get_yaw()
			total_yaw += yaw
		
		mean_head_angle = total_yaw / num_keys
		return mean_head_angle
		
	def __calculate_percent_time_looking(self, trialData):
		''' 
		Calculate the % time the participant was looking at least at the partial check angle, bot
		on the sidewalk and when they are in the road, for each time they're in the road.
		This is not exact but it gives a good indication whether or not the kids head was turned.
		'''
		# percent_looking = [[PercentChecking.ON_SIDEWALK, PercentChecking.IN_ROAD]] for each road entrance
		percent_looking = trialData.get_percent_checking()
		return percent_looking
		
	def _calculate_percent_checking_in_car_path(self, trialData):

		percent_full_checking = None
		checking_state_counter = [0,0,0,0,0]
		participant = trialData.get_participant()

		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not car_path_detail:
			#return None
			return NO_VALUE_NUM
			
		enter_time = car_path_detail.get_enter_time()
		exit_time = car_path_detail.get_exit_time()
		if not exit_time:
			exit_time = trialData.get_last_time()

		in_car_path_times = [t for t in sorted(participant.get_participant_dict().iterkeys()) if t >= enter_time and t < exit_time]
		num_keys = len(in_car_path_times)
		if num_keys < 1:
			print "Warning: (percent_checking_in_car_path) no time in car path - cannot calculate"
			self.__logger.info("Warning: (percent_checking_in_car_path) no time in car path - cannot calculate")
			return NO_VALUE_NUM
			
		for t in in_car_path_times:
			checking_state_counter[participant.get_moment(t).get_checking_state()] += 1
			#print "IN CAR PATH: t: %s, state %s" % (t, CheckingState.toStr(participant.get_moment(t).get_checking_state()))
		
		percent_full_checking = float(checking_state_counter[CheckingState.FULL_CHECKING_LEFT]) / num_keys
		
		#print "PERCENT FULL CHECKING IN CAR PATH: %s (%s / %s)" % (percent_full_checking, checking_state_counter[CheckingState.FULL_CHECKING_LEFT], num_keys)
		
		return percent_full_checking 

		
	def __calculate_simulated_hits_HMDV(self, trialData, direction):
		'''
		Calculate if the participant would have been hit if they continued walking
		at the practice trials mean walking speed from the time they entered the road.
		Calculate whether or not there is a simulated hit each time the participant enters the road moving forward.
		'''
		
		# If there's no mean walking velocity, can't calculate simulated hit
		meanVel = self.__meanWalkingSpeedHMDV
		if meanVel > (NO_VALUE_NUM-1):
			self.__logger.info("No practice trials mean walking speed: can't calculate SimulatedHit.")
			return None

		sim_hits = []
		
		# Get all the forward-moving road enterances and check for a simulated hit in each
		road_details = trialData.get_road_details_forward_entrance()
		for road_detail in road_details:
			moment = trialData.get_participant().get_moment(road_detail.get_enter_time())
			sim_hits.append(self._get_sim_hit(trialData, direction, meanVel, moment))
			
		return sim_hits
	
	def __calculate_simulated_hits_RWV(self, trialData, direction):
		'''
		lol
		'''
		
		meanVel = self.__meanWalkingSpeedRWV
		if meanVel > (NO_VALUE_NUM-1):
			self.__logger.info("No speed trials mean walking speed: can't calculate SimulatedHit.")
			return None
			
		sim_hits = []
		
		road_details = trialData.get_road_details_forward_entrance()
		for road_detail in road_details:
			moment = trialData.get_participant().get_moment(road_detail.get_enter_time())
			sim_hits.append(self._get_sim_hit(trialData, direction, meanVel, moment))
			
		return sim_hits
		
	
	def _get_sim_hit(self, trialData, direction, meanVel, moment):
		''' Calculate if there's a simulated hit given this road_detail '''
		t = moment.get_time()
		z = moment.get_z_position()
		x = moment.get_x_position()

		# Get a list of TrialCar that exist when person entered road
		cars = trialData.get_cars_at_time(t, direction)
		
		for trial_car in cars:
			
			carZmin = trial_car.get_close_side_z(t)
			carZmax = trial_car.get_far_side_z(t)

			# calculate distance & time until the person has entered/exited the car's path
			distanceToEnterCarPath = abs(carZmin - z)
			timeToEnterCarPath = distanceToEnterCarPath / meanVel
			
			distanceToExitCarPath = abs(carZmax - z)
			timeToExitCarPath = distanceToExitCarPath / meanVel
			
			# calculate the distance & time until the car has entered/exited the person's path
			front_bumper_distance_x = trial_car.get_front_bumper_distance_from_x(t, x)
			rear_bumper_distance_x = trial_car.get_rear_bumper_distance_from_x(t, x)
			
			# if car has passed the participant, move on
			#TODO: TEST THIS
			if (front_bumper_distance_x > 0):
				continue
			
			carCloseXDistance = front_bumper_distance_x
			carFarXDistance = rear_bumper_distance_x
			
			#carXVelocity = self.__get_car_velocity_on_x_axis(carData, trialData)
			carXVelocity = trial_car.get_velocity_x(t)
			
			timeUntilCarEnterPersonPath = abs(carCloseXDistance) / carXVelocity
			timeUntilCarExitPersonPath = abs(carFarXDistance) / carXVelocity
			if (timeUntilCarEnterPersonPath < timeToExitCarPath and
				timeToEnterCarPath < timeUntilCarExitPersonPath):
				return True
				
			
		return False
		
		
	def calculateTrialDuration(self, trialData):
		''' Get the trial duration -- used for filtering trials. '''
		start_time = trialData.get_start_time()
		end_time = trialData.get_last_time()
		trial_duration = end_time - start_time
		return trial_duration
		
		
	@print_timing
	def calculateVelocityOnEnterRoad(self, trialData):
		'''
		Calculate the velocity when the participant enters the road 
		the LAST time they enter the road. A participant may 'enter 
		the road' a number of times, but we're only interested in the
		last time they enter the road.
		'''
		
		path_detail = trialData.get_last_enter_road_detail(ParticipantDirection.FORWARD)
		if path_detail is None:
			# No car path entrances
			return NO_VALUE_NUM
		
		vel = trialData.get_participant().get_velocity(path_detail.get_enter_time())		
		return vel 
	
	
	def calculateMeanVelocityInCarPath(self, trialData):
		''' Calculate the participant's mean velocity while in the car path, the final time they're in the car's path. '''
		path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not path_detail:
			self.__logger.info("MeanVelocityInCarPath: Can't calculate, never entered a car's path.")
			#print "MeanVelocityInCarPath: Can't calculate, never entered a car's path."
			#return None
			return NO_VALUE_NUM
			
		enter_time = path_detail.get_enter_time()
		exit_time = path_detail.get_exit_time()
		if exit_time is None:
			exit_time = trialData.get_last_time()
		
		mean_vel = trialData.get_participant().get_mean_velocity(enter_time, exit_time)
		#print "MEAN VEL: ", mean_vel
		
		return mean_vel
		
	def calculateMeanVelocityInRoad(self, trialData):
		''' Calculate the participant's mean velocity while in the road, each time they're in the road. '''
		path_details = trialData.get_road_details_forward_entrance()
		mean_velocities = []
		
		for path_detail in path_details:
			enter_time = path_detail.get_enter_time()
			exit_time = path_detail.get_exit_time()
			if exit_time is None:
				exit_time = trialData.get_last_time()
			mean_velocity = trialData.get_participant().get_mean_velocity(enter_time, exit_time)
			mean_velocities.append(mean_velocity)
			
		return mean_velocities


	
	@print_timing
	def calculateVelocityOnEnterCarPath(self, trialData):
		'''
		Calculate the velocity when the participant enters the 
		car's path the LAST time they enter the car's path.
		'''
		velOnEnterRightCarPath = self.__calculate_velocity_on_enter_car_path(trialData, Direction.RIGHT)
		velOnEnterLeftCarPath = self.__calculate_velocity_on_enter_car_path(trialData, Direction.LEFT)
		return (velOnEnterRightCarPath, velOnEnterLeftCarPath, None)
	
	def __calculate_velocity_on_enter_car_path(self, trialData, direction):

		path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if path_detail == None:
			# No car path entrances
			#return None
			return NO_VALUE_NUM
		
		vel = trialData.get_participant().get_velocity(path_detail.get_enter_time())
		return vel 
		
	@print_timing
	def calculateVelocityOnExitCarPath(self, trialData):
		'''
		Calculate the velocity when the participant exits the car's path 
		the LAST time they exit the car's path. A participant  may 'exit 
		the car's path' a number of times, but we're only interested in the
		last time they exit the car's path.
		'''
		
		velOnExitRightCarPath = self.__calculate_velocity_on_exit_car_path(trialData, Direction.RIGHT)
		velOnExitLeftCarPath = self.__calculate_velocity_on_exit_car_path(trialData, Direction.LEFT)
		return (velOnExitRightCarPath, velOnExitLeftCarPath, None)
	
	def __calculate_velocity_on_exit_car_path(self, trialData, direction):
		
		car_path_details = trialData.get_car_path_details()
		path_detail = trialData.get_first_exit_car_path_detail(ParticipantDirection.FORWARD)

		if path_detail == None:
			# No car path entrances
			#return None
			return NO_VALUE_NUM
		
		vel = trialData.get_participant().get_velocity(path_detail.get_exit_time())
		return vel 

	
	@print_timing
	def calculateMaximumVelocityInCarPath(self, trialData):
		'''
		Calculate the maximum velocity when the participant is in the 
		car's path the LAST time they are in car's path.  A participant
		may be in the car's path a number of times, but we're only
		interested in the last time they're in the car's path.
		'''
		maxVelocityInRightCarPath = self.__calculate_maximum_velocity_in_car_path(trialData, Direction.RIGHT)
		maxVelocityInLeftCarPath = self.__calculate_maximum_velocity_in_car_path(trialData, Direction.LEFT)
		return (maxVelocityInRightCarPath, maxVelocityInLeftCarPath, None)
		
	
	def __calculate_maximum_velocity_in_car_path(self, trialData, direction):
		''' Get the maximum velocity between when the participant last entered a car's path, and their first exit of a car path'''
		
		last_enter_car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not last_enter_car_path_detail:
			# No car path entrances
			#return None
			return NO_VALUE_NUM

		enter_time = last_enter_car_path_detail.get_enter_time()
		exit_time = last_enter_car_path_detail.get_exit_time()
		if not exit_time:
			# Operator intervened or hit
			exit_time = trialData.get_participant().get_last_moment().get_time()
		
		max_vel = trialData.get_participant().get_max_velocity(enter_time, exit_time)
		return max_vel
		
	@print_timing
	def calculateMinimumVelocityInCarPath(self, trialData):
		'''
		Calculate the minimum velocity when the participant is in the 
		car's path the LAST time they are in car's path.  A participant
		may be in the car's path a number of times, but we're only
		interested in the last time they're in the car's path.
		'''
		minVelocityInRightCarPath = self.__calculate_minimum_velocity_in_car_path(trialData, Direction.RIGHT)
		minVelocityInLeftCarPath = self.__calculate_minimum_velocity_in_car_path(trialData, Direction.LEFT)
		return (minVelocityInRightCarPath, minVelocityInLeftCarPath, None)

	def __calculate_minimum_velocity_in_car_path(self, trialData, direction):
		last_enter_car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if not last_enter_car_path_detail:
			# No car path entrances
			#return None
			return NO_VALUE_NUM

		enter_time = last_enter_car_path_detail.get_enter_time()
		exit_time = last_enter_car_path_detail.get_exit_time()
		if not exit_time:
			# Operator intervened or hit
			exit_time = trialData.get_participant().get_last_moment().get_time()
		
		min_vel = trialData.get_participant().get_min_velocity(enter_time, exit_time)
		return min_vel
	
	
	def calculate_percent_partial_checking_on_sidewalk(self, trial_data):
		checks = self._get_partial_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_on_sidewalk(trial_data, checks)
	
	def calculate_percent_full_checking_on_sidewalk(self, trial_data):
		checks = self._get_full_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_on_sidewalk(trial_data, checks)
		
	def calculate_percent_closest_car_in_view_on_sidewalk(self, trial_data):
		checks = self._get_car_in_view_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_on_sidewalk(trial_data, checks)
		
	def _calculate_percent_checking_on_sidewalk(self, trial_data, checks_on_sidewalk):
		
		result = []
		start_time = 0  # first sidewalk time is always 0
		
		road_entries = trial_data.get_road_details_forward_entrance()
		if not road_entries:
			return [NO_VALUE_NUM]#None
		
		for entry_number, road_entry in enumerate(road_entries):
			end_time = road_entry.get_enter_time()
			if not end_time:
				return [NO_VALUE_NUM]#None
				
			total_time = end_time - start_time
			time_checking = 0
			percent_checking = 0

			checks_this_entry = checks_on_sidewalk[entry_number]
			for check_start_time, check_end_time in checks_this_entry:
				time_checking += check_end_time - check_start_time
			percent_checking = time_checking / total_time
			result.append(percent_checking)
			start_time = road_entry.get_exit_time()
				
		return result
		
	def calculate_percent_partial_checking_in_road(self, trial_data):
		checks = self._get_partial_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_road(trial_data, checks)
	
	def calculate_percent_full_checking_in_road(self, trial_data):
		checks = self._get_full_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_road(trial_data, checks)
		
	def calculate_percent_closest_car_in_view_in_road(self, trial_data):
		checks = self._get_car_in_view_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_road(trial_data, checks)
	
	#### TODO: ALL OF THESE NEED METHODS AND SUB-METHODS NEED TESTING.
	def calculate_percent_closest_LFC_in_view_in_near_lane(self, trial_data):
		#Users check right for left-facing cars.
		right_checks = self._get_car_in_view_checks_in_near_lane(trial_data, Direction.LEFT) #Direction refers to the direction cars are facing.
		if right_checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_near_lane(trial_data, right_checks)
		
	def calculate_percent_closest_RFC_in_view_in_near_lane(self, trial_data):
		#Users check left for right-facing cars.
		left_checks = self._get_car_in_view_checks_in_near_lane(trial_data, Direction.RIGHT)
		if left_checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_near_lane(trial_data, left_checks)
		
	def calculate_percent_time_closest_LFC_in_view_in_far_lane(self, trial_data):
		#Users check right for left facing cars.
		right_checks = self._get_car_in_view_checks_in_far_lane(trial_data, Direction.LEFT)
		if right_checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_far_lane(trial_data, right_checks)
		
	def calculate_percent_time_closest_RFC_in_view_in_far_lane(self, trial_data):
		left_checks = self._get_car_in_view_checks_in_far_lane(trial_data, Direction.RIGHT)
		if left_checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_far_lane(trial_data, left_checks)
		
	def calculate_percent_time_closest_LFC_in_view_between_car_paths(self, trial_data):
		right_checks = self._get_car_in_view_checks_between_car_paths(trial_data, Direction.LEFT)
		if right_checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_between_car_paths(trial_data, right_checks)
		
	def calculate_percent_time_closest_RFC_in_view_between_car_paths(self, trial_data):
		left_checks = self._get_car_in_view_checks_between_car_paths(trial_data, Direction.RIGHT)
		if left_checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_between_car_paths(trial_data, left_checks)
		
	def calculate_is_looking_at_far_lane_car_on_middle_of_road_entry(self, trial_data):
		right_checks = self._get_car_in_view_checks_in_near_lane(trial_data, Direction.LEFT)
		if not all(right_checks):
			return [NO_VALUE_NUM]
		last_entry_between_car_path_detail = trial_data.get_last_enter_between_car_path_detail(ParticipantDirection.FORWARD)
		print "last_entry_between_car_path_detail", last_entry_between_car_path_detail
		if last_entry_between_car_path_detail is None:
			print "NEVER ENTERED BETWEEN CAR PATHS"
			return [NO_VALUE_NUM]
		last_entry_time = last_entry_between_car_path_detail.get_enter_time()
		print "RIGHT CHECKS", right_checks

		checking_on_entry = False
		for right_check in right_checks:
			print "RIGHT CHECK", right_check
			check_start_time = right_check[-1][0]
			check_end_time = right_check[-1][1]
			if check_start_time <= last_entry_time <= check_end_time:
				checking_on_entry = True
		
		print "Checking on entry: ", checking_on_entry
		return checking_on_entry
####
	

	def _calculate_percent_checking_in_road(self, trial_data, checks_in_road):		
		
		result = []
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		if not road_entries:
			return [NO_VALUE_NUM]#None
			
		# go through each time they entered the road
		for entry_number, road_entry in enumerate(road_entries):
			
			enter_time = road_entry.get_enter_time()
			end_time = road_entry.get_exit_time()

			if not enter_time:
				result.append(NO_VALUE_NUM)
				continue
			
			# if they didn't exit, check if they got hit
			if not end_time:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					result.append(NO_VALUE_NUM)
					continue
				end_time = moment_got_hit.get_time()
				
			total_time = end_time - enter_time
			time_checking = 0	
				
			# add the time of each check together
			checks_this_entry = checks_in_road[entry_number]
			for check_start_time, check_end_time in checks_this_entry:
				if enter_time <= check_start_time <= end_time:
					time_checking += check_end_time - check_start_time
					
			percent_checking = time_checking / total_time
			result.append(percent_checking)
				
		return result
		
	def _calculate_percent_checking_in_near_lane(self, trial_data, checks_in_near_lane):
		
		result = []
		
		road_entries = trial_data.get_road_details_forward_entrance()
		if not road_entries:
			return [NO_VALUE_NUM]
		
		for entry_number, road_entry in enumerate(road_entries):
			
			enter_time = road_entry.get_enter_time()
			end_time = road_entry.get_exit_near_lane_time()
			
			if not enter_time:
				result.append(NO_VALUE_NUM)
				continue
			
			# if they didn't exit, check if they got hit
			if not end_time:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					result.append(NO_VALUE_NUM)
					continue
				end_time = moment_got_hit.get_time()
				
			total_time = end_time - enter_time
			time_checking = 0	
			# add the time of each check together
			checks_this_entry = checks_in_near_lane[entry_number]
			
			for check_start_time, check_end_time in checks_this_entry:
				if enter_time <= check_start_time <= end_time:
					time_checking += check_end_time - check_start_time
					
			percent_checking = time_checking / total_time
			result.append(percent_checking)
				
		return result
		
	def _calculate_percent_checking_in_far_lane(self, trial_data, checks_in_far_lane):
		
		result = []
		
		road_entries = trial_data.get_road_details_forward_entrance()
		if not road_entries:
			return [NO_VALUE_NUM]
		
		for entry_number, road_entry in enumerate(road_entries):
			
			enter_time = road_entry.get_exit_near_lane_time()
			end_time = road_entry.get_exit_time()
			
			if not enter_time:
				result.append(NO_VALUE_NUM)
				continue
			
			# if they didn't exit, check if they got hit
			if not end_time:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					result.append(NO_VALUE_NUM)
					continue
				end_time = moment_got_hit.get_time()
				
			total_time = end_time - enter_time
			time_checking = 0	
			# add the time of each check together
			checks_this_entry = checks_in_far_lane[entry_number]
			
			for check_start_time, check_end_time in checks_this_entry:
				if enter_time <= check_start_time <= end_time:
					time_checking += check_end_time - check_start_time
					
			percent_checking = time_checking / total_time
			result.append(percent_checking)
				
		return result				
		
	def _calculate_percent_checking_between_car_paths(self, trial_data, checks_between_car_paths):
		
		result = []
		
		road_entries = trial_data.get_road_details_forward_entrance()
		between_car_path_entries = trial_data.get_between_car_path_details()
		if not road_entries:
			return [NO_VALUE_NUM]
			
		if not between_car_path_entries:
			for entry in road_entries:
				result.append(None)
			return result
		
		for entry_number, road_entry in enumerate(road_entries):
			
			enter_road_time = road_entry.get_enter_time()
			exit_road_time = road_entry.get_exit_time()
			
			if not enter_road_time:
				result.append(NO_VALUE_NUM)
				continue
			
			# if they didn't exit, check if they got hit
			if not exit_road_time:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					result.append(NO_VALUE_NUM)
					continue
				exit_road_time = moment_got_hit.get_time()
			
			# find the total time between car paths
			total_time = 0
			for between_car_path_entry in between_car_path_entries:
				between_path_entry_time = between_car_path_entry.get_enter_time()
				if enter_road_time <= between_path_entry_time <= exit_road_time:					
					between_path_exit_time = between_car_path_entry.get_exit_time()
					if not between_path_exit_time:
						between_path_exit_time = exit_road_time
					total_time += between_path_exit_time - between_path_entry_time
					
			if total_time == 0:
				result.append(NO_VALUE_NUM)
				continue
			
			# add the time of each valid check together
			time_checking = 0		
			checks_this_entry = checks_between_car_paths[entry_number]
			for check_start_time, check_end_time in checks_this_entry:
				if enter_road_time <= check_start_time <= exit_road_time:
					time_checking += check_end_time - check_start_time
			
			percent_checking = time_checking / total_time
			result.append(percent_checking)
				
		return result							
			
	def calculate_percent_partial_checking_in_car_path(self, trial_data):
		checks = self._get_partial_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_car_path(trial_data, checks)
		
	def calculate_percent_full_checking_in_car_path(self, trial_data):
		checks = self._get_full_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_car_path(trial_data, checks)
		
	def calculate_percent_closest_car_in_view_in_car_path(self, trial_data):
		checks = self._get_car_in_view_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_in_car_path(trial_data, checks)
		
	def _calculate_percent_checking_in_car_path(self, trial_data, checks_in_car_path):
		
		result = []

		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		car_path_entries = trial_data.get_car_path_details()
		if not road_entries:# or not car_path_entries:
			return [NO_VALUE_NUM]
		if not car_path_entries:
			for entry in road_entries:
				result.append(None)
			return result
			
		# go through each time they entered the road
		for entry_number, road_entry in enumerate(road_entries):
			
			enter_road_time = road_entry.get_enter_time()
			exit_road_time = road_entry.get_exit_time()
			if not enter_road_time:
				result.append(NO_VALUE_NUM)
				continue		
				
			# if they didn't exit the road, check if they got hit
			if not exit_road_time:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					result.append(NO_VALUE_NUM)
					continue
				exit_road_time = trial_data.get_participant().get_last_moment().get_time()
			
			# find the total time in a car path on this entry
			total_time = 0
			for car_path_entry in car_path_entries:
				path_entry_time = car_path_entry.get_enter_time()
				if enter_road_time <= path_entry_time <= exit_road_time:					
					path_exit_time = car_path_entry.get_exit_time()
					if not path_exit_time:
						path_exit_time = exit_road_time
					total_time += path_exit_time - path_entry_time
					
			if total_time == 0:
				result.append(NO_VALUE_NUM)
				continue
			
			# add the time of each valid check together
			time_checking = 0		
			checks_this_entry = checks_in_car_path[entry_number]
			for check_start_time, check_end_time in checks_this_entry:
				if enter_road_time <= check_start_time <= exit_road_time:
					time_checking += check_end_time - check_start_time
			
			percent_checking = time_checking / total_time
			result.append(percent_checking)
				
		return result			
	
	
	def calculate_percent_partial_checking_between_curb_and_car_path(self, trial_data):
		checks = self._get_partial_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_between_curb_and_car_path(trial_data, checks)
		
	def calculate_percent_full_checking_between_curb_and_car_path(self, trial_data):
		checks = self._get_full_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_between_curb_and_car_path(trial_data, checks)
	
	def calculate_percent_closest_car_in_view_between_curb_and_car_path(self, trial_data):
		checks = self._get_car_in_view_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_percent_checking_between_curb_and_car_path(trial_data, checks)
	
	def _calculate_percent_checking_between_curb_and_car_path(self, trial_data, checks):
		
		result = []
		
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		if not road_entries:
			return [NO_VALUE_NUM]
		car_path_entries = trial_data.get_car_path_details()
		
		# go through each time they entered the road
		for entry_number, road_entry in enumerate(road_entries):
			
			enter_road_time = road_entry.get_enter_time()
			exit_road_time = road_entry.get_exit_time()
			if not enter_road_time:
				result.append(NO_VALUE_NUM)
				continue
				
			# if they didn't exit the road, check if they got hit
			moment_got_hit = None
			if not exit_road_time:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					result.append(NO_VALUE_NUM)
					continue
				exit_road_time = moment_got_hit.get_time()
			
			# find the total time they were between curb and car path
			start_time = enter_road_time
			end_time = None
			total_time = 0
			
			if car_path_entries is not None:
				for car_path_entry in car_path_entries:
					car_path_enter_time = car_path_entry.get_enter_time()
					
					# check that the car path entry happened during this road entry
					if enter_road_time <= car_path_enter_time <= exit_road_time:
						end_time = car_path_enter_time
						total_time += end_time - start_time
					
						# if they went back to the sidewalk, that's our next start time
						if car_path_entry.get_exit_direction() == ParticipantDirection.BACKWARD:
							start_time = car_path_entry.get_exit_time()
							end_time = None
		
			# if we don't have an end time, but they stepped back to the sidewalk, use that
			if not end_time:
				if road_entry.get_exit_direction() == ParticipantDirection.BACKWARD:
					total_time += exit_road_time - start_time
				else:
					result.append(NO_VALUE_NUM)
					continue
			
			if total_time == 0:
				result.append(NO_VALUE_NUM)
				continue
			
			# add the time of each valid check together
			time_checking = 0		
			checks_this_entry = checks[entry_number]
			for check_start_time, check_end_time in checks_this_entry:
				if enter_road_time <= check_start_time <= exit_road_time:
					time_checking += check_end_time - check_start_time
					
			# do the calculation
			percent_checking = time_checking / total_time
			result.append(percent_checking)

		return result
	

	def calculate_pct_full_checking_with_car_in_view_on_sidewalk(self, trial_data):
		checks = self._get_full_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def calculate_pct_full_checking_with_car_in_view_in_road(self, trial_data):
		checks = self._get_full_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def calculate_pct_full_checking_with_car_in_view_in_car_path(self, trial_data):
		checks = self._get_full_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def calculate_pct_full_checking_with_car_in_view_between_curb_and_car_path(self, trial_data):
		checks = self._get_full_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def calculate_pct_partial_checking_with_car_in_view_on_sidewalk(self, trial_data):
		checks = self._get_partial_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def calculate_pct_partial_checking_with_car_in_view_in_road(self, trial_data):
		checks = self._get_partial_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def calculate_pct_partial_checking_with_car_in_view_in_car_path(self, trial_data):
		checks = self._get_partial_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def calculate_pct_partial_checking_with_car_in_view_between_curb_and_car_path(self, trial_data):
		checks = self._get_partial_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_pct_of_checks_with_car_in_view(trial_data, checks)
		
	def _calculate_pct_of_checks_with_car_in_view(self, trial_data, checks):
		"""
		Calculates the percentage of time during the given checks that the closest car was in the 
		participant's view, for each time the participant was in the road.
		
		Parameters:
		trial_data -- a TrialDetail object
		checks -- a list of checks, of the form (start_time, end_time)
		"""
		result = []
		participant = trial_data.get_participant()
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		if not road_entries:
			return [NO_VALUE_NUM]
		
		# we're breaking down the calculation by road entry
		for entry_number, road_entry in enumerate(road_entries):
			# get the checks for this entry
			checks_this_entry = checks[entry_number]
			if not checks_this_entry:
				result.append(NO_VALUE_NUM) # they never checked (or never entered car path)
				continue			
			total_check_time = 0
			total_time_in_view = 0

			for check_start, check_end in checks_this_entry:
				car_was_visible = False
				start_time = None
				total_check_time += (check_end - check_start)
				
				t = check_start				
				while t <= check_end:
					closest_car = trial_data.get_closest_car(t, Direction.RIGHT)
					car_in_view = self._is_car_visible(closest_car, participant, t)
					
					if car_in_view and not car_was_visible:
						start_time = t
						car_was_visible = True
						
					if not car_in_view and car_was_visible:
						total_time_in_view += (t - start_time)
						car_was_visible = False
						start_time = None
					
					t = participant.get_next_moment(t).get_time()
				
				if start_time is not None:
					t = participant.get_prev_moment(t).get_time()
					total_time_in_view += (t - start_time)

			try:
				pct = total_time_in_view / total_check_time
			except ZeroDivisionError:
				pct = NO_VALUE_NUM # they never checked
			result.append(pct)

		return result
				
	
	def calculate_mean_partial_check_time_on_sidewalk(self, trial_data):
		checks = self._get_partial_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_full_check_time_on_sidewalk(self, trial_data):
		checks = self._get_full_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_car_in_view_check_time_on_sidewalk(self, trial_data):
		checks = self._get_car_in_view_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_partial_check_time_in_road(self, trial_data):
		checks = self._get_partial_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_full_check_time_in_road(self, trial_data):
		checks = self._get_full_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_car_in_view_check_time_in_road(self, trial_data):
		checks = self._get_car_in_view_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_partial_check_time_in_car_path(self, trial_data):
		checks = self._get_partial_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_full_check_time_in_car_path(self, trial_data):
		checks = self._get_full_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_car_in_view_check_time_in_car_path(self, trial_data):
		checks = self._get_car_in_view_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_partial_check_time_between_curb_and_car_path(self, trial_data):
		checks = self._get_partial_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_full_check_time_between_curb_and_car_path(self, trial_data):
		checks = self._get_full_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def calculate_mean_car_in_view_check_time_between_curb_and_car_path(self, trial_data):
		checks = self._get_car_in_view_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_mean_check_time(trial_data, checks)
		
	def _calculate_mean_check_time(self, trial_data, checks):
		"""
		Calculates and returns the mean check time for the given list of checks. Return value
		is a list with a mean check time for each road entry in the trial.
		
		Parameters:
		trial_data -- a TrialDetail object
		checks -- a list of checks (e.g. full/partial on sidewalk)
		"""
		
		result = []
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		if not road_entries:
			return [NO_VALUE_NUM]
			
		# loop through the road entries and calculate mean time of those checks
		for entry_number, road_entry in enumerate(road_entries):
			
			checks_this_entry = checks[entry_number]
			
			# operator intervened or some other problem
			if checks_this_entry is None:
				result.append(NO_VALUE_NUM)
				continue
						
			# if they didn't check, just append 0
			if len(checks_this_entry) == 0:
				result.append(0.0)
				continue
				
			total_check_time = 0
			for start_time, end_time in checks_this_entry:
				total_check_time += end_time - start_time
				
			mean_check_time = total_check_time / len(checks_this_entry)
			result.append(mean_check_time)

		return result
	
	
	def calculate_full_checks_with_car_in_view_on_sidewalk(self, trial_data):
		checks = self._get_full_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
	
	def calculate_partial_checks_with_car_in_view_on_sidewalk(self, trial_data):
		checks = self._get_partial_checks_on_sidewalk(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
		
	def calculate_full_checks_with_car_in_view_in_road(self, trial_data):
		checks = self._get_full_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
		
	def calculate_partial_checks_with_car_in_view_in_road(self, trial_data):
		checks = self._get_partial_checks_in_road(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
		
	def calculate_full_checks_with_car_in_view_in_car_path(self, trial_data):
		checks = self._get_full_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
		
	def calculate_partial_checks_with_car_in_view_in_car_path(self, trial_data):
		checks = self._get_partial_checks_in_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
		
	def calculate_full_checks_with_car_in_view_between_curb_and_car_path(self, trial_data):
		checks = self._get_full_checks_between_curb_and_car_path(trial_data)	
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
	
	def calculate_partial_checks_with_car_in_view_between_curb_and_car_path(self, trial_data):
		checks = self._get_partial_checks_between_curb_and_car_path(trial_data)
		if checks is None:
			return [NO_VALUE_NUM]
		return self._calculate_checks_with_car_in_view(trial_data, checks)
	
	def _calculate_checks_with_car_in_view(self, trial_data, checks_by_entry):
		"""
		Given a list of checks (broken down by road entry), returns the number of those checks,
		for each road entry, where the closest (oncoming) car was in the participant's field of
		view at least once. In effect, the number of the given checks in which the participant 
		actually saw the danger car.
		
		Parameters:
		trial_data -- a TrialDetail object
		checks_by_entry -- a list of lists, checks broken down by road entry
		"""
		result = []
		participant = trial_data.get_participant()
		
		# checks are divided by road entries, so go through each entry
		for checks in checks_by_entry:
			num_checks = 0
			if checks is None:
				result.append(NO_VALUE_NUM)
				continue
			
			# for each check in this entry
			for start_time, end_time in checks:
				t = start_time
				# determine if the closest car was ever visible during the check
				while t <= end_time:
					closest_car = trial_data.get_closest_car(t, Direction.RIGHT)
					if self._is_car_visible(closest_car, participant, t):
						num_checks += 1
						break
					next_moment = participant.get_next_moment(t)
					if not next_moment:
						break
					t = next_moment.get_time()
			result.append(num_checks)
			
		return result
	
	
	def calculate_number_of_partial_checks_on_sidewalk(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='partial_checks_on_sidewalk')
		
	def calculate_number_of_full_checks_on_sidewalk(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='full_checks_on_sidewalk')
		
	def calculate_number_of_partial_checks_in_road(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='partial_checks_in_road')
		
	def calculate_number_of_full_checks_in_road(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='full_checks_in_road')	
		
	def calculate_number_of_partial_checks_in_car_path(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='partial_checks_in_car_path')
		
	def calculate_number_of_full_checks_in_car_path(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='full_checks_in_car_path')
		
	def calculate_number_of_partial_checks_between_curb_and_car_path(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='partial_checks_between_curb_and_car_path')
		
	def calculate_number_of_full_checks_between_curb_and_car_path(self, trial_data):
		return self._calculate_number_of_checks(trial_data, check_type='full_checks_between_curb_and_car_path')
		
	def _calculate_number_of_checks(self, trial_data, check_type):
		"""
		Calculates and returns a list of checks of the given check_type. The checks that are returned are a list of lists,
		containing checks for each time the participant was in the desired area (specified by check_type), such as in the 
		road, or on the sidewalk.
		
		Parameters:
		trial_data -- the TrialDetail object of the trial in question
		check_type -- see the _get_checks_method_map dictionary in __init__ for valid types/keys
		"""
		
		# a mapping of methods for getting different types of checks
		checks_method_map = {
			'full_checks_on_sidewalk': self._get_full_checks_on_sidewalk,
			'full_checks_in_road': self._get_full_checks_in_road,
			'full_checks_in_car_path': self._get_full_checks_in_car_path,
			'full_checks_between_curb_and_car_path': self._get_full_checks_between_curb_and_car_path,
			'partial_checks_on_sidewalk': self._get_partial_checks_on_sidewalk,
			'partial_checks_in_road': self._get_partial_checks_in_road,
			'partial_checks_in_car_path': self._get_partial_checks_in_car_path,
			'partial_checks_between_curb_and_car_path': self._get_partial_checks_between_curb_and_car_path,
		}			
		
		get_checks_method = checks_method_map[check_type]
		checks_per_entry = get_checks_method(trial_data)
		if checks_per_entry is None:
			return [NO_VALUE_NUM]
		
		check_counts = []
		for checks in checks_per_entry:
			if checks is None:
				check_counts.append(NO_VALUE_NUM)
			else:
				check_counts.append(len(checks))
		return check_counts
		
		
	def _get_partial_checks_on_sidewalk(self, trial_data):
		check_angle = -Globals.partialCheckAngle
		max_check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_on_sidewalk(
			trial_data, 
			check_angle=check_angle, 
			max_check_angle=max_check_angle
			)
		return checks
		
	def _get_full_checks_on_sidewalk(self, trial_data):	
		check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_on_sidewalk(
			trial_data, 
			check_angle=check_angle
			)
		return checks
		
	def _get_car_in_view_checks_on_sidewalk(self, trial_data):
		checks = self._get_checks_on_sidewalk(trial_data, car_in_view=True)
		return checks
	
	def _get_checks_on_sidewalk(self, trial_data, car_in_view=False, check_angle=None, max_check_angle=None):
		""" 
		Calculates and returns a list of checks on the sidewalk, for each time the participant was on the sidewalk. 
		Checks are represented as tuples with (start_time, end_time). 
		
		If car_in_view is True, returns the list of "checks" where the closest (oncoming) car was in the participant's
		field of view. If car_in_view is False, and both check_angle and max_check_angle are provided, returns the 
		checks between check_angle and max_check_angle, otherwise returns checks at check_angle.
		
		Note: Works only for checks to the LEFT.
		"""
		
		start_index = 0  # trials always start on the sidewalk and always start at 0
		checks_per_entry = []  # a list of checks for each time the participant was on the sidewalk
		
		road_entries = trial_data.get_road_details_forward_entrance()
		if not road_entries:
			return None
		
		for road_entry in road_entries:
			end_index = road_entry.get_enter_index()
			if not end_index:
				checks_per_entry.append(None)
				continue
			
			# if we're looking for car_in_view checks, do that
			if car_in_view is True:
				checks = self._get_times_with_closest_car_in_view(trial_data, start_index, end_index, Direction.LEFT)
			# otherwise, we're using check_angle (and possibly max_check_angle) to find checks
			else:
				checks = self._get_checks_at_angle(trial_data, start_index, end_index, check_angle, max_check_angle)
			checks_per_entry.append(checks)
			if road_entry.get_exit_direction() == ParticipantDirection.BACKWARD:
				start_index = road_entry.get_exit_index()
			
		return checks_per_entry
		
		
	def _get_partial_checks_in_road(self, trial_data):
		check_angle = -Globals.partialCheckAngle
		max_check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_in_road(
			trial_data, 
			check_angle=check_angle, 
			max_check_angle=max_check_angle
			)
		return checks

	def _get_full_checks_in_road(self, trial_data):
		check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_in_road(
			trial_data, 
			check_angle=check_angle
			)
		return checks
		
	def _get_car_in_view_checks_in_road(self, trial_data):
		checks = self._get_checks_in_road(trial_data, car_in_view=True)
		return checks
	
	def _get_car_in_view_left_checks_in_road(self, trial_data):
		left_checks = self._get_checks_in_road(trial_data, Direction.RIGHT, car_in_view=True) #Direction refers to the direction cars are facing, not the direction of the check.
		
		return left_checks
		
	def _get_car_in_view_right_checks_in_road(self, trial_data):
		right_checks = self._get_checks_in_road(trial_data, Direction.LEFT, car_in_view=True) #Direction refers to the direction cars are facing, not the direction of the check.
		
		return right_checks
		
		
	def _get_car_in_view_checks_in_near_lane(self, trial_data, direction):
		if direction == Direction.RIGHT:	#Direction refers to the direction a car is facing, NOT the direction of a check.
			checks = self._get_checks_in_near_lane(trial_data, Direction.RIGHT, car_in_view=True)
		elif direction == Direction.LEFT:
			checks = self._get_checks_in_near_lane(trial_data, Direction.LEFT, car_in_view=True)
		else:
			checks = [NO_VALUE_NUM]
		
		return checks
		
	def _get_car_in_view_checks_in_far_lane(self, trial_data, direction):
		if direction == Direction.RIGHT:	#Direction refers to the direction a car is facing, NOT the direction of a check.
			checks = self._get_checks_in_far_lane(trial_data, Direction.RIGHT, car_in_view=True)
		elif direction == Direction.LEFT:
			checks = self._get_checks_in_far_lane(trial_data, Direction.LEFT, car_in_view=True)
		else:
			checks = [NO_VALUE_NUM]
		
		return checks
	
	def _get_car_in_view_checks_between_car_paths(self, trial_data, direction):
		if direction == Direction.RIGHT:
			checks = self._get_checks_between_car_paths(trial_data, Direction.RIGHT, car_in_view=True)
		elif direction == Direction.LEFT:
			checks = self._get_checks_between_car_paths(trial_data, Direction.LEFT, car_in_view=True)
		else:
			checks = [NO_VALUE_NUM]
		
		return checks
		
	def _get_checks_in_road(self, trial_data, direction, car_in_view=False, check_angle=None, max_check_angle=None):
		""" 
		Calculates and returns a list of checks in the road, for each time the participant was in the road. Checks 
		are represented as tuples with (start_time, end_time). 
		
		If car_in_view is True, returns the list of "checks" where the closest (oncoming) car was in the participant's
		field of view. If car_in_view is False, and both check_angle and max_check_angle are provided, returns the 
		checks between check_angle and max_check_angle, otherwise returns checks at check_angle.
		
		Note: Works only for checks to the LEFT.
		"""
		checks_per_entry = []
		
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		if not road_entries:
			return None
			
		for road_entry in road_entries:
			start_index = road_entry.get_enter_index()
			end_index = road_entry.get_exit_index()
			
			if not start_index:
				checks_per_entry.append(None)
				continue
			if not end_index:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					checks_per_entry.append(None)
					continue
				end_index = moment_got_hit.get_index()
			# if we're looking for car_in_view checks, do that
			if car_in_view is True:
				checks = self._get_times_with_closest_car_in_view(trial_data, start_index, end_index, direction)
			# otherwise, we're using check_angle (and possibly max_check_angle) to find checks
			else:
				checks = self._get_checks_at_angle(trial_data, start_index, end_index, check_angle, max_check_angle)
			checks_per_entry.append(checks)
			
		return checks_per_entry

	def _get_checks_in_near_lane(self, trial_data, direction, car_in_view=False):
		"""
		Calculates and returns a list of checks made with an on-coming car in view in the near lane. Checks
		are represented as tuples with start_time and end_time.
		"""
		
		checks_per_entry = []
		
		road_entries = trial_data.get_road_details_forward_entrance()
		if not road_entries:
			return None
		
		for road_entry in road_entries:
			start_index = road_entry.get_enter_index()
			end_index = road_entry.get_exit_near_lane_index()
			
			if not start_index:
				checks_per_entry.append(None)
				continue
			if not end_index:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					checks_per_entry.append(None)
					continue
				end_index = moment_got_hit.get_index()
			if car_in_view is True:
				if direction == Direction.LEFT:
					checks = self._get_times_with_closest_left_facing_car_in_view(trial_data, start_index, end_index, direction)
				elif direction == Direction.RIGHT: 
					checks = self._get_times_with_closest_right_facing_car_in_view(trial_data, start_index, end_index, direction)
					#print "Has gone " , self._get_times_with_closest_car_in_view_middle_road(trial_data, start_index, end_index, direction)
					# otherwise, return 9999
				else:
					checks = NO_VALUE_NUM
			checks_per_entry.append(checks)	
				
		return checks_per_entry
		
	def _get_checks_in_far_lane(self, trial_data, direction, car_in_view=False):
		checks_per_entry = []
		
		road_entries = trial_data.get_road_details_forward_entrance()
		if not road_entries:
			return None
		
		for road_entry in road_entries:
			start_index = road_entry.get_exit_near_lane_index()
			end_index = road_entry.get_exit_index()
			
			if not start_index:
				checks_per_entry.append(None)
				continue
			if not end_index:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					checks_per_entry.append(None)
					continue
				end_index = moment_got_hit.get_index()
			if car_in_view is True:
				checks = self._get_times_with_closest_car_in_view(trial_data, start_index, end_index, direction)
			else:
				checks = NO_VALUE_NUM #Don't care about checks without on-coming traffic. This is only used with 'car_in_view' logic.
			checks_per_entry.append(checks)	
				
		return checks_per_entry

	def _get_partial_checks_in_car_path(self, trial_data):
		check_angle = -Globals.partialCheckAngle
		max_check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_in_car_path(
			trial_data, 
			check_angle=check_angle, 
			max_check_angle=max_check_angle
			)
		return checks
		
	def _get_full_checks_in_car_path(self, trial_data):
		check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_in_car_path(
			trial_data, 
			check_angle=check_angle
			)
		return checks
		
	def _get_car_in_view_checks_in_car_path(self, trial_data):
		checks = self._get_checks_in_car_path(trial_data, car_in_view=True)
		return checks
		
	def _get_checks_in_car_path(self, trial_data, car_in_view=False, check_angle=0.0, max_check_angle=None):
		""" 
		Calculates and returns a list of checks in the car path, for each time the participant was in the ROAD 
		(not each time they were in a car path). Checks are represented as tuples with (start_time, end_time). 
		
		If car_in_view is True, returns the list of "checks" where the closest (oncoming) car was in the participant's
		field of view. If car_in_view is False, and both check_angle and max_check_angle are provided, returns the 
		checks between check_angle and max_check_angle, otherwise returns checks at check_angle.
		
		Note: Works only for checks to the LEFT.
		"""
		checks_per_entry = []
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		car_path_entries = trial_data.get_car_path_details()
		if not road_entries:# or not car_path_entries:
			return None
		if not car_path_entries:
			for entry in road_entries:
				checks_per_entry.append(None)
			return checks_per_entry
			
		# we have to calculate per road entry (because that's how data is output in MasterDataGenerator)
		for road_entry in road_entries:
			road_entry_index = road_entry.get_enter_index()
			road_exit_index = road_entry.get_exit_index()
			checks_this_entry = []
			
			if not road_entry_index:
				checks_per_entry.append(None)
				continue

			# if they didn't exit, check if they got hit
			if not road_exit_index:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					checks_per_entry.append(None)
					continue
				road_exit_index = trial_data.get_participant().get_last_moment().get_index()
			
			entered_a_car_path = False
			for car_path_entry in car_path_entries:
				start_index = car_path_entry.get_enter_index()
				if not start_index:
					continue
				
				# if the car path entry happened during this road entry...
				if road_entry_index <= start_index <= road_exit_index:
					entered_a_car_path = True
					end_index = car_path_entry.get_exit_index()
					if not end_index:
						moment_got_hit = trial_data.get_first_hit()
						if not moment_got_hit:
							continue
						end_index = moment_got_hit.get_index()
					# if we're looking for car_in_view checks, do that
					if car_in_view is True:
						checks = self._get_times_with_closest_car_in_view(trial_data, start_index, end_index, Direction.LEFT)
					# otherwise, we're using check_angle (and possibly max_check_angle) to determine checks
					else:
						checks = self._get_checks_at_angle(trial_data, start_index, end_index, check_angle, max_check_angle)
					checks_this_entry.extend(checks)
					
			if entered_a_car_path:
				checks_per_entry.append(checks_this_entry)
			else:
				checks_per_entry.append(None)
		return checks_per_entry

		
	def _get_partial_checks_between_curb_and_car_path(self, trial_data):	
		check_angle = -Globals.partialCheckAngle
		max_check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_between_curb_and_car_path(
			trial_data, 
			check_angle=check_angle, 
			max_check_angle=max_check_angle
			)
		return checks
		
	def _get_full_checks_between_curb_and_car_path(self, trial_data):	
		check_angle = -Globals.fullCheckAngle
		checks = self._get_checks_between_curb_and_car_path(
			trial_data, 
			check_angle=check_angle
			)
		return checks
		
	def _get_car_in_view_checks_between_curb_and_car_path(self, trial_data):
		checks = self._get_checks_between_curb_and_car_path(trial_data, car_in_view=True)
		return checks
		
	def _get_checks_between_curb_and_car_path(self, trial_data, car_in_view=False, check_angle=None, max_check_angle=None):
		""" 
		Calculates and returns a list of checks between the near curb and the car path,	for each time the participant
		was in the ROAD (not each time they were between the curb and a car path). Checks are represented as tuples 
		with (start_time, end_time). 
		
		If car_in_view is True, returns the list of "checks" where the closest (oncoming) car was in the participant's
		field of view. If car_in_view is False, and both check_angle and max_check_angle are provided, returns the 
		checks between check_angle and max_check_angle, otherwise returns checks at check_angle.
		
		Note: Works only for checks to the LEFT.
		"""
		checks_per_entry = []
				
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		if not road_entries:
			return None
		car_path_entries = trial_data.get_car_path_details()	
			
		# we have to calculate per road entry (because that's how data is output in MasterDataGenerator)
		for road_entry in road_entries:
			checks_this_entry = []
			road_entry_index = road_entry.get_enter_index()
			if not road_entry_index:
				checks_per_entry.append(None)
				continue
			
			# if they didn't exit, check if they got hit
			road_exit_index = road_entry.get_exit_index()
			if not road_exit_index:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					checks_per_entry.append(None)
					continue
				road_exit_index = moment_got_hit.get_index()
			
			start_index = road_entry_index
			end_index = None
						
			for car_path_entry in car_path_entries:
				
				car_path_entry_index = car_path_entry.get_enter_index()
				
				# check that the car path entry happened during this road entry...
				if road_entry_index <= car_path_entry_index <= road_exit_index:
					
					if car_path_entry.get_enter_direction() == ParticipantDirection.FORWARD:
						end_index = car_path_entry_index
							
						# if we're looking for car_in_view checks, do that
						if car_in_view is True:
							checks = self._get_times_with_closest_car_in_view(trial_data, start_index, end_index, Direction.LEFT)
						# otherwise, we're using check_angle (and possibly max_check_angle) to find checks
						else:
							checks = self._get_checks_at_angle(trial_data, start_index, end_index, check_angle, max_check_angle)							
							
						checks_this_entry.extend(checks)
						start_index = None  # reset these guys
						end_index = None  # reset these guys
			
					if car_path_entry.get_exit_direction() == ParticipantDirection.BACKWARD:
						start_index = car_path_entry.get_exit_index()

			# if you've gone through all of the CPs and there's no exit, use the exit of road			
			if not end_index and start_index is not None:
				end_index = road_exit_index
				# if we're looking for car_in_view checks, do that
				if car_in_view is True:
					checks = self._get_times_with_closest_car_in_view(trial_data, start_index, end_index, Direction.LEFT)
				# otherwise, we're using check_angle (and possibly max_check_angle) to find checks
				else:
					checks = self._get_checks_at_angle(trial_data, start_index, end_index, check_angle, max_check_angle)
				checks_this_entry.extend(checks)
			checks_per_entry.append(checks_this_entry)			
		
		return checks_per_entry


	def _get_checks_at_angle(self, trial_data, start_index, end_index, check_angle, max_check_angle):
		"""
		Calculates and returns a list of checks in the given time frame at the given check_angle.
		Checks are represented as tuples with (start_time, end_time). If max_check_angle is provided (is 
		not None), returns the checks between check_angle and max_check_angle, otherwise returns the number 
		of checks at check_angle.
		Note: Works only for checks to the LEFT.		
		
		Parameters:
		trial_data -- the trial data (a TrialDetail object)
		start_index -- the first time index to inspect
		end_index -- the last time index to inspect
		check_angle -- the head angle (yaw) at which a "check" occurs
		max_check_angle -- the maximum head angle (yaw), or upper limit, at which a "check" occurs (if None, this is ignored)
		"""
		
		checks = []
		checking = False
		full_checking = False
		start_time = None
		end_time = None
		
		# get the orientation data we want to evaluate
		participant = trial_data.get_participant()
		orientation_data = participant.get_orientation_data()[start_index:end_index]
		
		# count the number of checks at the given angle
		for data_point in orientation_data:
			orientation = data_point[OrientationData.ORIENTATION][OrientationType.YAW]

			# do full check/partial check stuff if necessary
			if max_check_angle is not None:
				
				# if we have a "partial" check and didn't just come from a "full check", count it
				if orientation <= check_angle and orientation > max_check_angle:
					if not full_checking and not checking:
						checking = True
						start_time = data_point[OrientationData.TIME]
				# if it's a "full check" and we recorded a "partial" check, remove it
				elif orientation <= max_check_angle:
					full_checking = True
					if checking:
						checking = False
						start_time = None
				# otherwise, no check (of any type) is happening, so reset everything if necessary
				else:
					if checking:
						checking = False
						checks.append((start_time, data_point[OrientationData.TIME]))
						start_time = None
					if full_checking:
						full_checking = False
			
			# if there's no "full check" criteria, just count the number of checks at the given angle
			else:
				if orientation <= check_angle and orientation > Globals.max_check_angle:
					if not checking:
						checking = True
						start_time = data_point[OrientationData.TIME]
				else:
					if checking:
						checking = False
						checks.append((start_time, data_point[OrientationData.TIME]))
						start_time = None

		# if a check started but didn't end, append it with end_time as the last data we have
		if start_time is not None:
			end_time = orientation_data[-1][OrientationData.TIME]
			checks.append((start_time, end_time))

		return checks


	def _get_times_with_closest_car_in_view(self, trial_data, start_index, end_index, direction):
		"""
		Returns the list of distinct "checks" in which the participant had the closest (oncoming) car in 
		their field of vision, in the given time frame (between start_index and end_index). Checks are 
		represented as tuples with (start_time, end_time).
		
		Parameters:
		trial_data -- the trial data (a TrialDetail object)
		start_index -- the first time index to inspect
		end_index -- the last time index to inspect
		"""
		#TODO: CHECK IF THIS IS BROKEN FOR RIGHT CHECKS
		checks = []
		checking = False
		start_time = None
		end_time = None
		
		# get the orientation data we want to evaluate
		participant = trial_data.get_participant()
		orientation_data = participant.get_orientation_data()[start_index:end_index]
		
		for data_point in orientation_data:
			
			t = data_point[OrientationData.TIME]
			closest_car = trial_data.get_closest_car(t, direction)
			car_visible = self._is_car_visible(closest_car, participant, t)
			

			if car_visible:
				if not checking:
					checking = True
					start_time = data_point[OrientationData.TIME]
					
			else:
				if checking:
					checking = False
					checks.append((start_time, data_point[OrientationData.TIME]))
					start_time = None
					
		# if a check started but didn't end, append it with end_time as the last data we have
		if start_time is not None:
			end_time = orientation_data[-1][OrientationData.TIME]
			checks.append((start_time, end_time))
		return checks
		
	def _get_times_with_closest_right_facing_car_in_view(self, trial_data, start_index, end_index, direction):
		"""
		Returns the list of distinct "checks" in which the participant had the closest (oncoming) car in 
		their field of vision, in the given time frame (between start_index and end_index). Checks are 
		represented as tuples with (start_time, end_time).
		
		Parameters:
		trial_data -- the trial data (a TrialDetail object)
		start_index -- the first time index to inspect
		end_index -- the last time index to inspect
		"""
		#TODO: CHECK IF THIS IS BROKEN FOR RIGHT CHECKS
		checks = []
		checking = False
		start_time = None
		end_time = None
		
		# get the orientation data we want to evaluate
		participant = trial_data.get_participant()
		orientation_data = participant.get_orientation_data()[start_index:end_index]
		
		for data_point in orientation_data:
			
			t = data_point[OrientationData.TIME]
			closest_car = trial_data.get_closest_car(t, direction)
			car_visible = self._is_right_facing_car_visible(closest_car, participant, t)
			

			if car_visible:
				if not checking:
					checking = True
					start_time = data_point[OrientationData.TIME]
					
			else:
				if checking:
					checking = False
					checks.append((start_time, data_point[OrientationData.TIME]))
					start_time = None
					
		# if a check started but didn't end, append it with end_time as the last data we have
		if start_time is not None:
			end_time = orientation_data[-1][OrientationData.TIME]
			checks.append((start_time, end_time))
		return checks
		
	def _get_times_with_closest_left_facing_car_in_view(self, trial_data, start_index, end_index, direction):
		"""
		Returns the list of distinct "checks" in which the participant had the closest (oncoming) car in 
		their field of vision, in the given time frame (between start_index and end_index). Checks are 
		represented as tuples with (start_time, end_time).
		
		Parameters:
		trial_data -- the trial data (a TrialDetail object)
		start_index -- the first time index to inspect
		end_index -- the last time index to inspect
		"""
		
		checks = []
		checking = False
		start_time = None
		end_time = None
		
		# get the orientation data we want to evaluate
		participant = trial_data.get_participant()
		orientation_data = participant.get_orientation_data()[start_index:end_index]
		
		for data_point in orientation_data:
			
			t = data_point[OrientationData.TIME]
			closest_car = trial_data.get_closest_car_to_participant_at_time(t, direction)
			if closest_car == None:
				car_visible = False
			else:
				car_visible = self._is_left_facing_car_visible(closest_car, participant, t)
			
			if car_visible:
				if not checking:
					checking = True
					start_time = data_point[OrientationData.TIME]
					
			else:
				if checking:
					checking = False
					checks.append((start_time, data_point[OrientationData.TIME]))
					start_time = None
					
					
		# if a check started but didn't end, append it with end_time as the last data we have
		if start_time is not None:
			end_time = orientation_data[-1][OrientationData.TIME]
			checks.append((start_time, end_time))	
		return checks		

	@print_timing
	def calculateHits(self, trialData):
		''' Number of times the participant was hit by a car '''
		rightFacingHits = self.__get_participant_hits(trialData, Direction.RIGHT)
		leftFacingHits = self.__get_participant_hits(trialData, Direction.LEFT)
		overallHits = rightFacingHits + leftFacingHits
		return (rightFacingHits, leftFacingHits, overallHits)

	
	def __calculate_near_misses(self, trialData, direction):
		''' Calculate near misses first in time then in distance '''
		
		near_misses = {}
		
		# Get final moment
		participant_final_moment = trialData.get_first_hit()
		if participant_final_moment is None:
			participant_final_moment = trialData.get_participant().get_last_moment()
		
		# Get exit car path moments (in either direction) up until a hit/op intervene/exit going forward
		car_path_exits = trialData.get_exit_car_path_details()
		
		# Calculate near misses in time
		for car_path_detail in car_path_exits:
			exit_car_path_time = car_path_detail.get_exit_time()
			trial_car = trialData.get_closest_car(exit_car_path_time, direction)
			if trial_car is None:
				continue

			participant_x = trialData.get_participant().get_x_position(exit_car_path_time)
			next_car_arrival_time = trial_car.get_time_from_x(exit_car_path_time, participant_x)
			if next_car_arrival_time < 1:
				#print "NEAR MISS at t=%s" % next_car_arrival_time
				near_misses[trial_car.get_viz_node_id()] = (next_car_arrival_time, None) #near_misses = {car_id: (Time, Distance)}
		
		# Calculate near misses in distance
		is_near_missing = False
		
		participant = trialData.get_participant()
		participant_dict = participant.get_participant_dict()
		
		for t in sorted(participant_dict.iterkeys()):
			closest_car = trialData.get_closest_car(t, direction)
			if (closest_car is None):
				#print "Warning: (_calculate_near_misses) could not find closest car - discontinuing"
				#self.__logger.info("Warning: (_calculate_near_misses) could not find closest car - discontinuing")
				#return {}
				continue
				
			car_id = closest_car.get_viz_node_id()
			participant_z = participant.get_z_position(t)
			front_bumper_x = closest_car.get_front_bumper_x(t)
			car_center_z = closest_car.get_car_moment(t).get_z_position()

			if participant_z <= car_center_z:
				car_z = closest_car.get_close_side_z(t)
			else:
				car_z = closest_car.get_far_side_z(t)
				
			part_position = (participant.get_x_position(t), 0, participant.get_z_position(t))
			car_position =  (front_bumper_x, 0, car_z)
			distance_to_car = vizmat.Distance(part_position, car_position)
			
			if (distance_to_car < 1 and is_near_missing == False):
				# Starting of near miss
				is_near_missing = True
				near_missing_car_id = car_id
				closest_distance = distance_to_car
			elif (distance_to_car < 1 and is_near_missing == True):
				# Check if this is as close as they got to the car
				if (distance_to_car < closest_distance):
					closest_distance = distance_to_car
			elif (distance_to_car >= 1 and is_near_missing == True):
				# Not near missing anymore, so append the near miss closest distance --> only one near miss per car
#				print "NEAR MISS DISTANCE = %s" % closest_distance
				if near_missing_car_id not in near_misses.keys():
					near_misses[near_missing_car_id] = (None, closest_distance)
				else:
#					print "ALREADY ADDED A NEAR MISS FOR car_id = %s " % (car_id)
					existing = near_misses[near_missing_car_id]
					near_misses[near_missing_car_id] = (existing[0], closest_distance)
				is_near_missing = False
				closest_distance = 1
		
#		print "NEAR MISSES"
#		for k in near_misses:
#			print "car=", k, near_misses[k]
			
		return near_misses

	@print_timing
	def calculateNearMisses(self, trialData):
		'''
		Near misses are in both time and distance.  
		A near miss occurs when:
		   1) the participant is within 1m of a car at any point
		   2) the participant is within 1s of being hit when leaving the car path on either side
		'''
		right_facing_cars_near_misses = self.__calculate_near_misses(trialData, Direction.RIGHT)
		left_facing_cars_near_misses = self.__calculate_near_misses(trialData, Direction.LEFT)
		overall_near_misses = dict(right_facing_cars_near_misses.items() + left_facing_cars_near_misses.items()) #right_facing_cars_near_misses + left_facing_cars_near_misses}
		return (right_facing_cars_near_misses, left_facing_cars_near_misses, overall_near_misses)
		
		
	def calculateStartDelay(self, trialData):
		""" Time from when a car passes to when the participant enters the road	"""
		rightFacingCarsStartDelay = self.__calculate_start_delay(trialData, Direction.RIGHT)
		leftFacingCarsStartDelay = self.__calculate_start_delay(trialData, Direction.LEFT)
		return (rightFacingCarsStartDelay, leftFacingCarsStartDelay, None)

		
	def __calculate_start_delay(self, trialData, direction):
		
		start_delay = None
		t = None
		
		#TODO: Should we pass in direction to all the get_last_*** functions?
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if car_path_detail is None:
			print "S1"
			self.__logger.info("StartDelay: Can't calculate start delay, participant never entered a car's path.")
			#return None
			return NO_VALUE_NUM
			
		enter_car_path_time = car_path_detail.get_enter_time()
		
		previous_car = trialData.get_previous_car_at_time(enter_car_path_time, direction)
		if previous_car is None:
			print "S2"
			self.__logger.info("StartDelay: Can't calculate start delay, no car had passed when the child crossed.")
			#return None
			return NO_VALUE_NUM

		participant_x = trialData.get_participant().get_x_position(enter_car_path_time)
		start_delay = previous_car.get_time_from_x(enter_car_path_time, participant_x)
		
		return start_delay

	
	@print_timing
	def calculateTimeLeftToSpareOnEnterRoad(self, trialData):
		'''
		Time left to spare when the participant enters the road	
		'''
		rightFacing = self.__calculate_time_left_to_spare_on_enter_road(trialData, Direction.RIGHT)
		leftFacing = self.__calculate_time_left_to_spare_on_enter_road(trialData, Direction.LEFT)
		return (rightFacing, leftFacing, None)
		
	def __calculate_time_left_to_spare_on_enter_road(self, trialData, direction):
		road_detail = trialData.get_last_enter_road_detail(ParticipantDirection.FORWARD)
		
		if road_detail is None:
			self.__logger.info("TLS Enter Road: Can't calculate time left to spare on enter road, participant never entered the road.")
			#return None
			return NO_VALUE_NUM
		
		t = road_detail.get_enter_time()
		x = trialData.get_participant().get_x_position(t)
		trial_car = trialData.get_closest_car(t, direction)
		if trial_car is None:
			self.__logger.info("No closest car.  Can't calculate TLS on enter road.")
			#return None
			return NO_VALUE_NUM
		tls = trial_car.get_time_from_x(t, x)

#		print "TLS ENTER ROAD"
#		print "  enter:", road_detail.get_enter_time()
#		print "  exit:", road_detail.get_exit_time()
#		print "  Closest car = %s" % trial_car.get_viz_node_id()
#		print "  TLS = %s" % tls

		return tls
	
	@print_timing
	def calculateTimeLeftToSpareOnEnterCarPath(self, trialData):
		''' Time left to spare when the participant enters the path of the cars	'''
		rightFacing = self.__calculate_time_left_to_spare_on_enter_car_path(trialData, Direction.RIGHT)
		leftFacing = self.__calculate_time_left_to_spare_on_enter_car_path(trialData, Direction.LEFT)
		return (rightFacing, leftFacing, None)
	
	
	def __calculate_time_left_to_spare_on_enter_car_path(self, trialData, direction):
		
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if car_path_detail is None:
			#self.__logger.info("Participant never entered the road.")
			self.__logger.info("TLS Enter Car Path: Can't calculate, participant never entered a car's path")
			#return None
			return NO_VALUE_NUM
		
		t = car_path_detail.get_enter_time()
		x = trialData.get_participant().get_x_position(t)
		trial_car = trialData.get_closest_car(t, direction)
		if trial_car is None:
			self.__logger.info("TLS Enter Car Path:, Can't calculate, no closest car.")
			#return None
			return NO_VALUE_NUM


		tls = trial_car.get_time_from_x(t, x)

#		print "TLS ENTER CAR PATH"
#		print "  enter:", car_path_detail.get_enter_time()
#		print "  exit:", car_path_detail.get_exit_time()
#		print "  Closest car = %s" % trial_car.get_viz_node_id()
#		print "  TLS = %s" % tls

		return tls

	
	@print_timing
	def calculateTimeLeftToSpareOnExitCarPath(self, trialData):
		''' Time left to spare when the participant exit the path of the cars '''
		rightFacing = self.__calculate_time_left_to_spare_on_exit_car_path(trialData, Direction.RIGHT)
		leftFacing = self.__calculate_time_left_to_spare_on_exit_car_path(trialData, Direction.LEFT)
		return (rightFacing, leftFacing, None)
		
	
	def __calculate_time_left_to_spare_on_exit_car_path(self, trialData, direction):
		car_path_detail = trialData.get_first_exit_car_path_detail(ParticipantDirection.FORWARD)
		if car_path_detail is None:
			self.__logger.info("TLS Enter Car Path: Could not calculate, participant never exited the car path going forward.")
			#return None
			return NO_VALUE_NUM
#		else:
#			print "Exit CP at t=%s" % car_path_detail.get_exit_time()
		
		t = car_path_detail.get_exit_time()
		x = trialData.get_participant().get_x_position(t)
		trial_car = trialData.get_closest_car(t, direction)
		if trial_car is None:
			#self.__logger.info("No closest car.  Can't calculate TLS on enter road.")
			#return None
			return NO_VALUE_NUM

		tls = trial_car.get_time_from_x(t, x)
		return tls


	def calculate_tls_on_exit_car_path_at_mean_walking_speed_RWV(self, trial_detail):
		return self._calculate_tls_on_exit_car_path_at_mean_walking_speed(trial_detail, self.__meanWalkingSpeedRWV)
		
	def calculate_tls_on_exit_car_path_at_mean_walking_speed_HMDV(self, trial_detail):
		return self._calculate_tls_on_exit_car_path_at_mean_walking_speed(trial_detail, self.__meanWalkingSpeedHMDV)

	def _calculate_tls_on_exit_car_path_at_mean_walking_speed(self, trial_detail, mean_walking_speed):
		"""
		Calculates the amount of time (in seconds) between when the participant 
		would have exited the path of the oncoming car and when the car would have 
		reached the participant, had the participant crossed the street at their 
		average walking speed.
		"""
		# can't do the calculation without these values, so bail out
		if mean_walking_speed == NO_VALUE_NUM:
			print "TLS@AVGSPEED: have no mean walking speed for this participant, unable to calculate"
			return NO_VALUE_NUM
		last_entered_road = trial_detail.get_moment_last_entered_road()
		if not last_entered_road:
			print "TLS@AVGSPEED: participant never entered the road, returning NO_VALUE_NUM"
			return NO_VALUE_NUM
			
		# we need the last time they exited a car path going forward
		car_path_details = trial_detail.get_car_path_details()
		forward_cp_exits = [cp for cp in car_path_details if cp.get_exit_direction() == ParticipantDirection.FORWARD]
		if not forward_cp_exits:
			print "TLS@AVGSPEED: participant never exited a car path, returning NO_VALUE_NUM"
			return NO_VALUE_NUM
		last_exit_path = max(forward_cp_exits, key=lambda cp: cp.get_exit_time())
		
		# this could happen with multiple road entries in which they didn't exit a cp on last
		if last_exit_path.get_exit_time() < last_entered_road.get_time():
			print "TLS@AVGSPEED: last car path exit {0} came before last road entry {1}, returning NO_VALUE_NUM".format(
				last_exit_path.get_exit_time(), last_entered_road.get_time())
			return NO_VALUE_NUM
		# this could happen if they loop back before finishing crossing
		last_enter_path = trial_detail.get_moment_last_entered_car_path()
		if last_exit_path.get_exit_time() < last_enter_path.get_time():
			print "TLS@AVGSPEED: last car path exit {0} came before last path entry {1}, returning NO_VALUE_NUM".format(
				last_exit_path.get_exit_time(), last_enter_path.get_time())
			return NO_VALUE_NUM
		
		# find the closest car when they entered the car path
		time_entered_car_path = last_enter_path.get_time()
		closest_car = trial_detail.get_closest_car(time_entered_car_path, Direction.RIGHT)
		if not closest_car:
			print "TLS@AVGSPEED: no closest car found, returning NO_VALUE_NUM"
			return NO_VALUE_NUM
		
		# find what time the participant would have exited the car path given avg speed and when they entered
		position_entered_car_path = last_enter_path.get_position()
		position_exited_car_path = trial_detail.get_participant().get_position(last_exit_path.get_exit_time())
		distance_covered_in_car_path = vizmat.Distance(position_entered_car_path, position_exited_car_path)
		time_to_cross_at_average = distance_covered_in_car_path / mean_walking_speed
		estimated_exit_cp_t = time_entered_car_path + time_to_cross_at_average
	
		# get a sorted list of times in this trial
		trial_times = sorted(trial_detail.get_participant().get_participant_dict().iterkeys())

		# if their average walking speed was much slower than their actual walking speed, there may not exist an 
		# actual trial time, in which case we need to estimate the car movement and tls
		if estimated_exit_cp_t >= trial_times[-1]:
			car_speed = closest_car.get_velocity_x(time_entered_car_path)
			car_dist_on_enter = -closest_car.get_front_bumper_distance_from_x(time_entered_car_path, position_exited_car_path[Position.X_POS])
			car_dist_on_exit_at_avg = car_dist_on_enter - (car_speed * time_to_cross_at_average)
			tls = car_dist_on_exit_at_avg / car_speed
		# otherwise we get a matching trial timestamp, find where the car was at that time, and find tls that way
		else:	
			t_index = min(range(len(trial_times)), key=lambda i: abs(trial_times[i] - estimated_exit_cp_t))
			t = trial_times[t_index]
			car_speed = closest_car.get_velocity_x(t)
			car_dist = -closest_car.get_front_bumper_distance_from_x(t, position_exited_car_path[Position.X_POS])
			tls = car_dist / car_speed
		return tls


	def calculate_time_left_to_spare_on_loss_of_view(self, trial_detail):
		""" 
		Calculates the amount of time until the car reaches the participant at the point the participant 
		can no longer see the car, the last time the participant entered the road. 
		"""
		
		# Get the time the participant last entered the road, and the closest car at that time
		last_entered_road = trial_detail.get_moment_last_entered_road()
		if not last_entered_road:
			return NO_VALUE_NUM
		
		t_last_entered_road = last_entered_road.get_time()
		next_car_to_participant = trial_detail.get_closest_car(t_last_entered_road, Direction.RIGHT)	
		participant = trial_detail.get_participant()
		
		# loop backwards until the next_car becomes visible
		t = t_last_entered_road
		while not self._is_car_visible(next_car_to_participant, participant, t):
			
			prev_moment = participant.get_prev_moment(t)
			if not prev_moment:
				return NO_VALUE_NUM 
			t = prev_moment.get_time()
			
			closest_car = trial_detail.get_closest_car(t, Direction.RIGHT)
			if closest_car is not next_car_to_participant:
				return -NO_VALUE_NUM  # negative "infinite" because they never saw the car
				
		# was the car ever out of view?
		if self._approx_equal(t_last_entered_road, t, delta=0.001):
			return NO_VALUE_NUM  # positive "infinite" because they saw the car as they entered
		
		# when would the car arrive at the participant?
		tls_on_loss_of_view = next_car_to_participant.get_time_from_x(t, last_entered_road.get_x_position())
		return tls_on_loss_of_view 


	def calculate_head_angle_on_loss_of_view(self, trial_data):
		"""
		Returns the participant's head angle at which the closest (oncoming) car was last in their
		view, the last time they entered the road.
		"""
		
		# Get the time the participant last entered the road, and the closest car at that time
		last_entered_road = trial_data.get_moment_last_entered_road()
		if not last_entered_road:
			return NO_VALUE_NUM
		t_last_entered_road = last_entered_road.get_time()
		next_car_to_participant = trial_data.get_closest_car(t_last_entered_road, Direction.RIGHT)	
		
		participant = trial_data.get_participant()
		
		# loop backwards until the next_car becomes visible (if it ever does)
		t = t_last_entered_road
		while not self._is_car_visible(next_car_to_participant, participant, t):
			prev_moment = participant.get_prev_moment(t)
			if not prev_moment:
				return NO_VALUE_NUM 
			t = prev_moment.get_time()
			closest_car = trial_data.get_closest_car(t, Direction.RIGHT)
			if closest_car is not next_car_to_participant:
				return NO_VALUE_NUM  # "infinite" because they never saw the car

		# was the car ever out of view?
		if self._approx_equal(t_last_entered_road, t, delta=0.001):
			return -NO_VALUE_NUM  # negative "infinite" because they saw the car as they entered
		
		# what was the participant's head angle at this time?
		head_angle = participant.get_orientation_data()[prev_moment.get_index()][OrientationData.ORIENTATION][OrientationType.YAW]
		return head_angle
			

	def _is_car_visible(self, closest_car, participant, t):
		''' Determines if the given car was visible to the participant at the given t '''
		
		participant_yaw = participant.get_yaw(t)
		participant_fov = Globals.headset_fov  # TODO: this will need to be updated if a different headset is used
		participant_position = participant.get_position(t)
		
		# get a triangle ABC representing the participant's vision in the x-z plane
		point_a = (participant_position[Position.X_POS], participant_position[Position.Z_POS])
		point_b, point_c = self._solve_vision_triangle(participant_yaw, participant_fov, participant_position)
		
		# get the corners of the car
		car_corner_points = [(closest_car.get_front_bumper_x(t), closest_car.get_far_side_z(t)),  # front far side
							(closest_car.get_front_bumper_x(t), closest_car.get_close_side_z(t)),  # front close side
							(closest_car.get_rear_bumper_x(t), closest_car.get_close_side_z(t)),  # rear close side
							(closest_car.get_rear_bumper_x(t), closest_car.get_far_side_z(t))]  # rear far side
		
		# check if any of the points are currently visible
		for pt in car_corner_points:
			if self._is_point_visible(pt, point_a, point_b, point_c):
				return True
		return False
		
	def _is_left_facing_car_visible(self, closest_car, participant, t):
		''' Determines if the given car was visible to the participant at the given t '''
		
		participant_yaw = participant.get_yaw(t)
		participant_fov = Globals.headset_fov  # TODO: this will need to be updated if a different headset is used
		participant_position = participant.get_position(t)
		
		# get a triangle ABC representing the participant's vision in the x-z plane
		point_a = (participant_position[Position.X_POS], participant_position[Position.Z_POS])
		point_b, point_c = self._solve_vision_triangle(participant_yaw, participant_fov, participant_position)
		# get the corners of the car
		car_corner_points = [(closest_car.get_front_bumper_x(t), closest_car.get_far_side_z(t)),  # front far side
							(closest_car.get_front_bumper_x(t), closest_car.get_close_side_z(t)),  # front close side
							(closest_car.get_rear_bumper_x(t), closest_car.get_close_side_z(t)),  # rear close side
							(closest_car.get_rear_bumper_x(t), closest_car.get_far_side_z(t))]  # rear far side
		# check if any of the points are currently visible
		for pt in car_corner_points:
			if self._is_point_visible(pt, point_a, point_b, point_c):
				if closest_car.get_direction() == Direction.LEFT:
					return True
		return False
		
	def _is_right_facing_car_visible(self, closest_car, participant, t):
		''' Determines if the given right facingcar was visible to the participant at the given t '''
		
		participant_yaw = participant.get_yaw(t)
		participant_fov = Globals.headset_fov  # TODO: this will need to be updated if a different headset is used
		participant_position = participant.get_position(t)
		
		# get a triangle ABC representing the participant's vision in the x-z plane
		point_a = (participant_position[Position.X_POS], participant_position[Position.Z_POS])
		point_b, point_c = self._solve_vision_triangle(participant_yaw, participant_fov, participant_position)
		
		# get the corners of the car
		car_corner_points = [(closest_car.get_front_bumper_x(t), closest_car.get_far_side_z(t)),  # front far side
							(closest_car.get_front_bumper_x(t), closest_car.get_close_side_z(t)),  # front close side
							(closest_car.get_rear_bumper_x(t), closest_car.get_close_side_z(t)),  # rear close side
							(closest_car.get_rear_bumper_x(t), closest_car.get_far_side_z(t))]  # rear far side
		
		# check if any of the points are currently visible
		for pt in car_corner_points:
			if self._is_point_visible(pt, point_a, point_b, point_c):
				if closest_car.get_direction() == Direction.RIGHT:
					return True
		return False
	
	def _solve_vision_triangle(self, participant_yaw, participant_fov, participant_position):
		""" 
		Given Cartesian coords of A (participant) and yaw of head, solves for coords of B and C 
		to give triangle ABC representing participant's vision in x-z plane
		"""
		
		# WHAT IS THIS TRIANGLE?
		#
		# C------B  ---
		# \     /    |
		#  \   /     h
		#   \ /      |
		#    A      ---
		# isosceles triangle ABC where AB=AC, height h = view distance, A = fov
		# triangle represents participant's vision in x/z plane
		
		view_distance = 350.0 # max distance (m) they can see (easier to solve as triangle than infinite 2D cone)
		participant_fov = math.radians(participant_fov)
		participant_yaw = -math.radians(participant_yaw)  # trust me on this one
		x = participant_position[Position.X_POS]
		z = participant_position[Position.Z_POS]
		r = view_distance / math.cos(participant_fov / 2.0)
		
		point_b = (x - (r * math.sin(participant_yaw - (participant_fov / 2.0))), z + (r * math.cos(participant_yaw - (participant_fov / 2.0))))
		point_c = (x - (r * math.sin(participant_yaw + (participant_fov / 2.0))), z + (r * math.cos(participant_yaw + (participant_fov / 2.0))))
		return point_b, point_c
	
	
	def _calculate_area_of_triangle(self, point_a, point_b, point_c):
		''' Given the Cartesian coords of the vertices of a triangle, returns its area '''
		area = abs(point_a[0] * (point_b[1] - point_c[1]) + 
				point_b[0] * (point_c[1] - point_a[1]) + 
				point_c[0] * (point_a[1] - point_b[1])) / 2.0
		return area

	
	def _is_point_visible(self, point_p, point_a, point_b, point_c):
		''' Determines if a given point P is within the triangle defined by ABC (representing participant vision in x-z plane) '''
		area_abc = self._calculate_area_of_triangle(point_a, point_b, point_c)
		area_pab = self._calculate_area_of_triangle(point_p, point_a, point_b)
		area_pbc = self._calculate_area_of_triangle(point_p, point_b, point_c)
		area_pac = self._calculate_area_of_triangle(point_p, point_a, point_c)
		return self._approx_equal(area_abc, (area_pab + area_pbc + area_pac), delta=0.001)


	def _approx_equal(self, a, b, delta):
		return abs(a - b) < delta

	
	@print_timing
	def calculateGapLength(self, trialData):
		""" The space between the cars during the trial (in meters)	"""

		# Gaps that the participant had to cross - starts after the first 
		# car passes, so gaps[0] is between the FIRST and SECOND cars. The
		# LAST gap is the gap they crossed in/they got hit in.
		
		trialData.get_gaps(Direction.RIGHT)
		
		rightGapLength = self.__calculate_gap_length(trialData, Direction.RIGHT)
		leftGapLength = self.__calculate_gap_length(trialData, Direction.LEFT)
		#overallGapLength = too complicated for right now
		return (rightGapLength, leftGapLength, None)
	
	def __calculate_gap_length(self, trialData, direction):
#		print "*** CALC GAP LENGTH ***"
		gap_length = None
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if car_path_detail is None:
			self.__logger.info("Gap Length: can't calculate, participant never enter a car's path.")
			#return None
			return NO_VALUE_NUM

		enter_time = car_path_detail.get_enter_time()
		participant = trialData.get_participant()
		participant_x = participant.get_x_position(enter_time)
		
		trial_cars = trialData.get_trial_cars(direction)
		previous_car = trial_cars.get_previous_car_passed_x_at_t(participant_x, enter_time)
		next_car = trial_cars.get_next_to_x_at_t(participant_x, enter_time)
		
		if previous_car is None or next_car is None:
			self.__logger.info("Gap Length: Can't calculate, no cars passed or there's no next car.")
			if direction == Direction.RIGHT:
				print "Warning: Cannot calculate gap length, no cars passed or there's no next car."
			#return None
			return NO_VALUE_NUM
		
		prev_car_rear_bumper_x = previous_car.get_rear_bumper_x(enter_time)
		next_car_front_bumper_x = next_car.get_front_bumper_x(enter_time)
		gap_length = abs(prev_car_rear_bumper_x - next_car_front_bumper_x)
		return gap_length

	
	@print_timing
	def calculateGapInterval(self, trialData):
		""" The time between cars (in seconds)	"""
		rightGapInterval = self.__calculate_gap_interval(trialData, Direction.RIGHT)
		leftGapInterval = self.__calculate_gap_interval(trialData, Direction.LEFT)
		return (rightGapInterval, leftGapInterval, None)
	
	def __calculate_gap_interval(self, trialData, direction):
#		print "*** CALC GAP INTERVAL "
		
		gap_length = None
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if car_path_detail is None:
			self.__logger.info("GapInterval: Can't calculate gap interval, participant never entered into a car's path.")
			#print "NEVER ENTERED ROAD, can't calc gap length."
			#return None
			return NO_VALUE_NUM

		enter_time = car_path_detail.get_enter_time()
		participant = trialData.get_participant()
		participant_x = participant.get_x_position(enter_time)
		
		trial_cars = trialData.get_trial_cars(direction)
		next_car = trial_cars.get_next_to_x_at_t(participant_x, enter_time)
		
#		print "NEXT CAR = %s" % next_car
#		print "ENTER TIME = %s" % enter_time
		
		if next_car is None:
			self.__logger.info("Gap Interval: Cannot calculate gap interval, no next car.")
			return None
		
		next_car_vel = next_car.get_velocity_x(enter_time)
		
		gap_length = self.__calculate_gap_length(trialData, direction)
		if gap_length is None or gap_length is NO_VALUE_NUM:
			self.__logger.info("Gap Interval: Cannot calculate gap interval, no cars passed.")
			if direction == Direction.RIGHT:
				print "Warning: Cannot calculate GapInterval (no value for GapLength)"
			return NO_VALUE_NUM
		
		gap_interval = abs(gap_length / next_car_vel)
		return gap_interval
		
	@print_timing
	def calculatePercentageOfGapUsed(self, trialData):
		'''
		The % of the gap that was used by the participant while crossing. 
		‘Using’ a gap starts when the participant enters the car path	
		'''
		
		rightPercentage = self.__calculate_percentage_of_gap_used(trialData, Direction.RIGHT)
		leftPercentage = self.__calculate_percentage_of_gap_used(trialData, Direction.LEFT)
		
		if (rightPercentage == None or leftPercentage == None):
			overallPercentage = None
		else:
			overallPercentage = leftPercentage + rightPercentage
		
		return (rightPercentage, leftPercentage, overallPercentage)
	
	@print_timing
	def calculatePercentageOfGapRemainingOnEnterCarPath(self, trialData):
		''' The % gap remaining on entrance of the car path '''
		rightPercentage = self.__calculate_percentage_of_gap_remaining_on_enter_car_path(trialData, Direction.RIGHT)
		leftPercentage = self.__calculate_percentage_of_gap_remaining_on_enter_car_path(trialData, Direction.LEFT)
		overallPercentage = None
		return (rightPercentage, leftPercentage, overallPercentage)

	@print_timing
	def calculatePercentageOfGapRemainingOnExitCarPath(self, trialData):
		''' The % gap remaining on exit of car path '''
		rightPercentage = self.__calculate_percentage_of_gap_remaining_on_exit_car_path(trialData, Direction.RIGHT)
		leftPercentage = self.__calculate_percentage_of_gap_remaining_on_exit_car_path(trialData, Direction.LEFT)
		overallPercentage = None
		return (rightPercentage, leftPercentage, overallPercentage)
		
	@print_timing
	def calculateMarginOfSafety(self, trialData):
		'''
		A percentage representing the relative safety of a child’s road crossing.
		Margin Of Safety = ([TLSEnterCarPath / (TLSEnterCarPath - TLSExitCarPath)] - 1) * 100%
		'''
		rightPercentage = self.__calculate_margin_of_safety(trialData, Direction.RIGHT)
		leftPercentage = NO_VALUE_NUM #None #self.__calculate_margin_of_safety(trialData, Direction.LEFT)
		overallPercentage = NO_VALUE_NUM #None
		return (rightPercentage, leftPercentage, overallPercentage)
		
	
	def __calculate_margin_of_safety(self, trialData, direction):
		margin_of_safety = None
		tls_enter_car_path = self.__calculate_time_left_to_spare_on_enter_car_path(trialData, direction)
		tls_exit_car_path = self.__calculate_time_left_to_spare_on_exit_car_path(trialData, direction)
		if tls_enter_car_path is None or tls_exit_car_path is None:
#			print "tls_enter_car_path = %s" % tls_enter_car_path
#			print "tls_exit_car_path = %s" % tls_exit_car_path
#			print "Could not calculate margin of safety; tls_enter_cp or tls_exit_cp not available."
			self.__logger.info("Margin of Safety: Could not calculate, participant didn't ever exit a car's path.")
			#return None
			return NO_VALUE_NUM

#		print "tls_enter_car_path = %s" % tls_enter_car_path
#		print "tls_exit_car_path = %s" % tls_exit_car_path
		
		if tls_enter_car_path == NO_VALUE_NUM or tls_exit_car_path == NO_VALUE_NUM:
			self.__logger.info("Margin of Safety: Could not calculate, participant didn't ever exit a car's path.")
			return NO_VALUE_NUM
		
		margin_of_safety = ((tls_enter_car_path / (tls_enter_car_path - tls_exit_car_path)) - 1) * 100
		return margin_of_safety
	
	def __calculate_percentage_of_gap_used(self, trialData, direction):
		pct_gap_used = None
		car_path_detail = trialData.get_last_enter_car_path_detail(ParticipantDirection.FORWARD)
		if car_path_detail is None:
			#print "NEVER ENTERED car path, can't calculate % gap used."
			self.__logger.info("% Gap Used: Could not calculate, participant didn't ever enter a car's gap.")
			#return None
			return NO_VALUE_NUM

		enter_time = car_path_detail.get_enter_time()
		exit_time = car_path_detail.get_exit_time()
		#print "car path detail = %s" % car_path_detail
		
		if exit_time is None:
			#TODO: need to worry about operator intervention?
			participant = trialData.get_participant()
			exit_time = participant.get_last_moment().get_time()
			
		time_in_car_path = exit_time - enter_time
		gap_interval = self.__calculate_gap_interval(trialData, direction)
		
#		print "time in car path = %s" % time_in_car_path
#		print "gap interval = %s" % gap_interval
		
		if gap_interval is None:
			#print "Can't calculate % gap used; gap interval is none."
			#return None
			return NO_VALUE_NUM

		pct_gap_used = time_in_car_path / gap_interval * 100
		return pct_gap_used
	
	
	def __calculate_percentage_of_gap_remaining_on_enter_car_path(self, trialData, direction):
		pct_gap_remaining = None
		tls_enter_car_path = self.__calculate_time_left_to_spare_on_enter_car_path(trialData, direction)
		gap_interval = self.__calculate_gap_interval(trialData, direction)
		
		if tls_enter_car_path is NO_VALUE_NUM or gap_interval is None:
			print "Can't calculate % gap remaining on enter car path."
			return NO_VALUE_NUM
		
		pct_gap_remaining = (tls_enter_car_path / gap_interval) * 100
		return pct_gap_remaining
	
	def __calculate_percentage_of_gap_remaining_on_exit_car_path(self, trialData, direction):
		pct_gap_remaining = None
		tls_exit_car_path = self.__calculate_time_left_to_spare_on_exit_car_path(trialData, direction)
		gap_interval = self.__calculate_gap_interval(trialData, direction)
		
		if tls_exit_car_path is NO_VALUE_NUM or gap_interval is None:
			print "tls_exit_car_path = %s" % tls_exit_car_path
			print "gap_interval = %s" % gap_interval
			print "Can't calculate % gap remaining on exit car path."
			return NO_VALUE_NUM
		
		pct_gap_remaining = (tls_exit_car_path / gap_interval) * 100
		return pct_gap_remaining

	
	@print_timing
	def calculateCrossingTime(self, trialData):
		''' Time it took to cross the first lane of traffic (in seconds) '''
		
		road_detail = trialData.get_last_exit_road_detail(ParticipantDirection.FORWARD)
		if road_detail is None:
			self.__logger.info("Crossing Time: can't calculate, participant never crossed the road.")
			#return None
			return NO_VALUE_NUM
			
		enter_time = road_detail.get_enter_time()
		exit_time = road_detail.get_exit_time()
		crossing_time = exit_time - enter_time
		
		return crossing_time

		
	@print_timing
	def calculateAverageRejectedGapTime(self, trialData):
		''' The average gap interval that was rejected by the participant '''
		rightFacingAverageRejectedGapTime = self.__calculate_average_rejected_gap_time(trialData, Direction.RIGHT)
		leftFacingAverageRejectedGapTime = self.__calculate_average_rejected_gap_time(trialData, Direction.LEFT)
		return (rightFacingAverageRejectedGapTime, leftFacingAverageRejectedGapTime, None)
	
	def __calculate_average_rejected_gap_time(self, trialData, direction):
		avg_rejected_gap_time = 0
		gaps = trialData.get_gaps(direction)
		if len(gaps) <= 1:
#			print "No rejected gaps. Could not calculate average rejected gap time."
			self.__logger.info("Average Rejected Gap Time: no rejected gaps.")
			#return None
			return NO_VALUE_NUM
		
#		print "gaps = %s" % [str(x) for x in gaps]
		
		# the last gap is the gap you crossed in
		avg_rejected_gap_time = sum(gap.get_gap_time() for gap in gaps[:-1]) / (len(gaps) -1)
		
		return avg_rejected_gap_time
	
	@print_timing
	def calculateMaxRejectedGapTime(self, trialData):
		''' The largest gap interval that was rejected by the participant '''
		rightFacingMaxRejectedGapTime = self.__calculate_max_rejected_gap_time(trialData, Direction.RIGHT)
		leftFacingMaxRejectedGapTime = self.__calculate_max_rejected_gap_time(trialData, Direction.LEFT)
		return (rightFacingMaxRejectedGapTime, leftFacingMaxRejectedGapTime, None)
	
	def __calculate_max_rejected_gap_time(self, trialData, direction):
		max_gap_length = 0
		gaps = trialData.get_gaps(direction)
		if len(gaps) <= 1:
			#print "No rejected gaps. Could not calculate max rejected gap time."
			self.__logger.info("Maximum Rejected Gap Time: Could not calculate max rejected gap time.")
			#return None
			return NO_VALUE_NUM
		
		max_gap_length = max(gap.get_gap_time() for gap in gaps[:-1])
		return max_gap_length
		
	@print_timing
	def calculateMinRejectedGapTime(self, trialData):
		''' The minimum gap interval that was rejected by the participant '''
		rightFacingMinRejectedGapTime = self.__calculate_min_rejected_gap_time(trialData, Direction.RIGHT)
		leftFacingMinRejectedGapTime = self.__calculate_min_rejected_gap_time(trialData, Direction.LEFT)
		return (rightFacingMinRejectedGapTime, leftFacingMinRejectedGapTime, None)

	def __calculate_min_rejected_gap_time(self, trialData, direction):
		min_gap_length = 0
		gaps = trialData.get_gaps(direction)
		if len(gaps) <= 1:
			self.__logger.info("Minimum Rejected Gap Time: Could not calculate min rejected gap time.")
			return NO_VALUE_NUM
		
		min_gap_length = min(gap.get_gap_time() for gap in gaps[:-1])
		return min_gap_length

	@print_timing
	def calculateMissedOpportunities(self, trialData):
		''' The number of times that the participant rejected a gap that was twice the length of the average crossing time '''
		rightFacingMissedOpportunities = self.__calculate_missed_opportunities(trialData, Direction.RIGHT)
		leftFacingMissedOpportunities = self.__calculate_missed_opportunities(trialData, Direction.LEFT)
		return (rightFacingMissedOpportunities, leftFacingMissedOpportunities, None)

	def __calculate_missed_opportunities(self, trialData, direction):
		gaps = trialData.get_gaps(direction)
		if len(gaps) <= 0: 
			# No gaps occurred in the trial
			self.__logger.info("Missed Opportunities: can't calculate, there were no gaps in the trial")
			#return None
			return NO_VALUE_NUM
		
		road_detail = trialData.get_last_enter_road_detail(ParticipantDirection.FORWARD)
		if road_detail is None:
			self.__logger.info("Missed Opportunities: can't calculate, participant did not cross the road safely.")
			#return None
			return NO_VALUE_NUM
			
		enter_road_time = road_detail.get_enter_time()
		exit_road_time = road_detail.get_exit_time()
		if exit_road_time is None:
			self.__logger.info("Missed Opportunities: can't calculate, participant did not cross the road safely.")
			#return None
			return NO_VALUE_NUM
		
		crossing_time = exit_road_time - enter_road_time
		missed_opportunities = filter(lambda gap_time: gap_time > (1.5 * crossing_time), [gap.get_gap_time() for gap in gaps[:-1]]) # last gap is the crossing/hit gap
		return len(missed_opportunities)

	def getNearMissDistance(self, near_miss_dict):
		''' Return the min near miss distance '''
		min_near_miss_dist = NO_VALUE_NUM
		it = [k for k in near_miss_dict.keys() if near_miss_dict.get(k)[NEAR_MISS_DISTANCE] is not None]
		if it:
			k = min(it, key=lambda x:near_miss_dict.get(x)[NEAR_MISS_DISTANCE])
			min_near_miss_dist = near_miss_dict[k][NEAR_MISS_DISTANCE]
			
		return min_near_miss_dist
		
	def getNearMissTime(self, near_miss_dict):
		''' Return the min near miss time '''
		min_near_miss_time = NO_VALUE_NUM
		it = [k for k in near_miss_dict.keys() if near_miss_dict.get(k)[NEAR_MISS_TIME] is not None]
		if it:
			k = min([k for k in near_miss_dict if near_miss_dict[k][NEAR_MISS_TIME] is not None], key=lambda x:near_miss_dict.get(x)[NEAR_MISS_TIME])
			min_near_miss_time = near_miss_dict[k][NEAR_MISS_TIME]
		return min_near_miss_time
		
	@print_timing
	def calculateTrafficVolume(self, trialData):
		""" Return the total number of cars that pass by the participant	"""

		# can't use the rejected gap time list because if 0 cars pass, list=[], if first car passes, list=[]
		rightFacingTrafficVolume = self.__calculate_traffic_volume(trialData, Direction.RIGHT)
		leftFacingTrafficVolume = self.__calculate_traffic_volume(trialData, Direction.LEFT)
		overallTrafficVolume = rightFacingTrafficVolume + leftFacingTrafficVolume
		return (rightFacingTrafficVolume, leftFacingTrafficVolume, overallTrafficVolume)
	
	def __calculate_traffic_volume(self, trialData, direction):
		gaps = trialData.get_gaps(direction)
		hits = trialData.get_hits()
		traffic_volume = len(gaps) + len(hits)
		return traffic_volume
	
	@print_timing
	def calculateTrafficVolumePerMinute(self, trialData):
		"""	# of cars that pass by the participant each minute	"""
		rightFacingTrafficVolumePerMinute = self.__calculate_traffic_volume_per_minute(trialData, Direction.RIGHT)
		leftFacingTrafficVolumePerMinute = self.__calculate_traffic_volume_per_minute(trialData, Direction.LEFT)
		overallTrafficVolumePerMinute = rightFacingTrafficVolumePerMinute + leftFacingTrafficVolumePerMinute
		return (rightFacingTrafficVolumePerMinute, leftFacingTrafficVolumePerMinute, overallTrafficVolumePerMinute)
	
	def __calculate_traffic_volume_per_minute(self, trialData, direction):
		total_trial_time = None
		first_car_time = trialData.get_time_first_car_arrived(Direction.RIGHT)
		if(first_car_time == None):
			return NO_VALUE_NUM
		last_time = trialData.get_last_time()
		if(last_time == None):
			return NO_VALUE_NUM
		elif (last_time == first_car_time):
			self.__logger.error("ERROR: in calculate_traffic_volume_per_minute, first_car_time and last_time are the same. Setting to 99999")
			return NO_VALUE_NUM
		cars_passed = self.__calculate_traffic_volume(trialData, direction)
		traffic_vol_per_minute = cars_passed / ((last_time - first_car_time) / 60)
		#traffic_vol_per_minute = cars_passed / (last_time / 60)
		return traffic_vol_per_minute

	def __get_participant_hits(self, trialData, direction):
		''' 
		Return a list of indices in the participant's position data
		that correspond to when they got hit by a car (first contact
		of the car and participant)
		'''
		return trialData.get_hits()
		
	def _get_checks_between_car_paths(self, trial_data, direction, car_in_view=False):
		"""  
		Calculates and returns a list of checks between car paths, for each time the participant was in the ROAD 
		(not each time they were between the car paths). Checks are represented as tuples with (start_time, end_time). 
		
		If car_in_view is True, returns the list of "checks" where the closest (oncoming) car was in the participant's
		field of view.
		
		"""
		checks_per_entry = []
		road_entries = trial_data.get_road_details_forward_entrance()  # not sure that this distinction matters
		between_car_path_entries = trial_data.get_between_car_path_details()
		if not road_entries:
			return None
		if not between_car_path_entries:
			for entry in road_entries:
				print "NO BETWEEN CAR PATH ENTRIES"
				checks_per_entry.append(None)
			return checks_per_entry
		
		# we have to calculate per road entry (because that's how data is output in MasterDataGenerator)
		for road_entry in road_entries:
			road_entry_index = road_entry.get_enter_index()
			road_exit_index = road_entry.get_exit_index()
			checks_this_entry = []
			
			if not road_entry_index:
				print "NO ROAD ENTRY INDEX"
				checks_per_entry.append(None)
				continue

			# if they didn't exit, check if they got hit
			if not road_exit_index:
				moment_got_hit = trial_data.get_first_hit()
				if not moment_got_hit:
					print "DID NOT EXIT THE ROAD"
					checks_per_entry.append(None)
					continue
				road_exit_index = trial_data.get_participant().get_last_moment().get_index()
			
			entered_between_paths = False
			for between_car_path_entry in between_car_path_entries:
				start_index = between_car_path_entry.get_enter_index()
				if not start_index:
					continue
				
				# if the middle of road entry happened during this road entry...
				if road_entry_index <= start_index <= road_exit_index:
					entered_between_paths = True
					end_index = between_car_path_entry.get_exit_index()
					if not end_index:
						moment_got_hit = trial_data.get_first_hit()
						if not moment_got_hit:
							continue
						end_index = moment_got_hit.get_index()
					# if we're looking for car_in_view checks, do that
					if car_in_view is True:
						if direction == Direction.LEFT:
							checks = self._get_times_with_closest_left_facing_car_in_view(trial_data, start_index, end_index, direction)
						elif direction == Direction.RIGHT: #
							checks = self._get_times_with_closest_right_facing_car_in_view(trial_data, start_index, end_index, direction)
						# otherwise, return 9999
						else:
							print "CAR NOT IN VIEW"
							checks = [NO_VALUE_NUM]
					checks_this_entry.extend(checks)
					
			if entered_between_paths:
				checks_per_entry.append(checks_this_entry)
			else:
				checks_per_entry.append(None)
			
		return checks_per_entry	
				
	def init_logger(self):
		#TODO: NOT used, just here for example
		# ---------- Initialize a logger -------------
		logging.basicConfig(
			level=logging.DEBUG,
			format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
			datefmt='%a, %d %b %Y %H:%M:%S',
			filename='stdout',
			filemode='w'
			)

		#declaration of the global logger object
		__import__(__name__).mainLogger = logging.getLogger('mainlogger')
		
		# define a Handler which writes messages to the sys.stderr
		Globals.console = logging.StreamHandler()
		
		# set a format which is simpler for console use
		formatter = logging.Formatter('%(name)-12s: %(message)s')
		
		# tell the handler to use this format
		Globals.console.setFormatter(formatter)
		
		# add the handler to the root logger
		__import__(__name__).mainLogger.addHandler(Globals.console)	