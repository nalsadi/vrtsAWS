import os
import time
import logging
from collections import defaultdict

import Globals
import VariableNames
#from SpeedTrialDataParser import SpeedTrialDataParser
from RawDataParser import RawDataParser
from DataHandler import DataHandler
from Enums import TrialType, Phase

NO_VALUE_NUM = 99999


class MasterDataGenerator:
    '''	Save the master data from the raw data files for a given participant. '''

    def __init__(self, *args, **kwargs):
        ''' Should be called with **kwargs containing keys: data_dir, participant_sessions '''
        self._data_dir = kwargs.get('data_dir', Globals.dataDirectoryPath)
        # {p_id->ParticipantSession objects} for all participants
        self._participant_sessions = kwargs.get('participant_sessions', {})

        self._mean_walking_speed = {}  # id -> mean_walking_speed
        self._mean_walking_speed_RWV = {}
        self._mean_running_speed_RWV = {}

    def _get_header(self):
        var_names = VariableNames.get_var_names_list()
        header = ';'.join(var_names)
        return header

    def _get_speed_test_sessions(self, participant_sessions):
        """ Return the speed test sessions from the list of participant sessions """
        speed_test_sessions = filter(lambda x: x.get_phase(
        ) == Phase.PHASE_II, participant_sessions)  # Phase II = speed test session
        return speed_test_sessions

    def _get_practice_sessions(self, participant_sessions):
        """ Return the practice sessions from the list of participant sessions """
        practice_sessions = filter(lambda x: x.get_phase(
        ) == Phase.PHASE_III, participant_sessions)  # Phase III = practice session
        return practice_sessions

    def _get_non_practice_sessions(self, participant_sessions):
        ''' Return the non-practice session from the list of participant sessions '''
        non_practice_sessions = filter(
            lambda x: x.get_phase() == Phase.PHASE_IV, participant_sessions)
        non_practice_sessions.extend(
            filter(lambda x: x.get_phase() == Phase.PHASE_V, participant_sessions))
        return non_practice_sessions

    def _get_speed_trials_output(self, participant_sessions):
        """ Parse the speed test and practice trials for the given participant """
        speed_test_sessions = self._get_speed_test_sessions(
            participant_sessions)
        if len(speed_test_sessions) < 1:
            print "WARNING: COULD NOT FIND SPEED TEST SESSION(s)"
            return ""

        stdp = SpeedTrialDataParser()
        # use the LAST speed test session only
        speed_test_session = speed_test_sessions[-1]
        # should be the same for both sessions
        participant_id = speed_test_session.get_participant_id()
        stdp.parse_speed_trials(speed_test_session)
        self._mean_walking_speed_RWV[participant_id] = stdp.get_mean_walking_speed_RWV(
        )
        self._mean_running_speed_RWV[participant_id] = stdp.get_mean_running_speed_RWV(
        )
        trials = speed_test_session.get_trials()

        # if we have practice (HMD) sessions, go ahead and parse those too
        practice_sessions = self._get_practice_sessions(participant_sessions)
        if practice_sessions:
            practice_session = practice_sessions[-1]
            stdp.parse_practice_trials(practice_session)
            self._mean_walking_speed[participant_id] = stdp.get_mean_walking_speed_HMDV(
            )
            trials += practice_session.get_trials()

        spss_output = stdp.get_spss_output(
            trials, participant_id, speed_test_session.get_phase())
        return spss_output

    def _get_non_practice_trials_output(self, participant_sessions):
        spss_output_list = []
        non_practice_sessions = self._get_non_practice_sessions(
            participant_sessions)

        for participant_session in non_practice_sessions:

            participant_id = participant_session.get_participant_id()

            try:
                mws_RWV = self._mean_walking_speed_RWV[participant_id]
            except:
                print "MasterDataGenerator: Warning! Could not find mean walking speed (RWV) under the given participant ID"
                mws_RWV = NO_VALUE_NUM

            try:
                mrs_RWV = self._mean_running_speed_RWV[participant_id]
            except:
                print "MasterDataGenerator: Warning! Could not find mean running speed (RWV) under the given participant ID "
                mrs_RWV = NO_VALUE_NUM

            try:
                mws_HMDV = self._mean_walking_speed[participant_id]
            except:
                print "MasterDataGenerator: Warning! Could not find mean walking speed (HMDV) under the given participant ID"
                mws_HMDV = NO_VALUE_NUM

            rdp = RawDataParser(participant_session,
                                mws_HMDV, mws_RWV, mrs_RWV)
            spss_output_list.extend(rdp.get_spss_output())

        return spss_output_list

    def save_master_data(self):
        """ Save the master data for this participant / timestamp """

        header = self._get_header()
        print("SAVING TO ", os.path.join(
            self._data_dir, "MASTER.txt"))
        master_data_file = open("MASTER.txt", "w")
        master_data_file.write(header)
        master_data_file.write("\n")

        print "***"
        print header

        logger.info("attempting to process master data")

        for p_id in self._participant_sessions:
            try:
                p_sessions = self._participant_sessions[p_id]

                #speed_trials_output = self._get_speed_trials_output(p_sessions)
                non_practice_trials_output = self._get_non_practice_trials_output(
                    p_sessions)

                # print "\n".join(s for s in speed_trials_output)
                print "\n".join(s for s in non_practice_trials_output)

               # master_data_file.write(
                #    "\n".join(s for s in speed_trials_output))
                master_data_file.write("\n")
                master_data_file.write(
                    "\n".join(s for s in non_practice_trials_output))
                master_data_file.write("\n")

            except Exception as e:
                logger.exception(
                    "unable to process participant {0}".format(p_id))


if __name__ == "__main__":

    #	data_dir = "C:\\Users\\user\\Desktop\\Partic Mean GAP SIZE\\Paste DATA here\\"
    #	data_dir = "C:\\Users\\user\\Desktop\\BackpackTestingData\\"
    data_dir = './testdata/'
    print(data_dir)
    dh = DataHandler()
    participant_sessions = dh.get_participant_sessions(
        data_dir)  # {participant_id -> [filenames]}
    print("here now")
    global logger
    logger = logging.getLogger(__name__)
    hdlr = logging.FileHandler(os.path.join(
        data_dir, 'failed_participants.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.info("MASTER DATA GENERATOR START")

    kwargs = {}
    kwargs['data_dir'] = data_dir
    kwargs['participant_sessions'] = participant_sessions
    mdg = MasterDataGenerator(**kwargs)
    mdg.save_master_data()
    print "Save complete. Exiting..."
    logger.info("master data generator finished and exiting")
        #read input file
    fin = open("MASTER.txt", "rt")
    #read file contents to string
    data = fin.read()
    #replace all occurrences of the required string
    data = data.replace(';', ',')
    #close the input file
    fin.close()
    #open the input file in write mode
    fin = open("views/images/MASTER.csv", "wt")
    #overrite the input file with the resulting data
    fin.write(data)
    #close the file
    fin.close()
