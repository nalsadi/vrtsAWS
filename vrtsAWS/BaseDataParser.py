#import vizmat
from Enums import *


class BaseDataParser(object):
    '''	A base class for the Data Parsers used throughout the project '''

    def __init__(self):
        """ Constructor of the base class for all data parser classes """
        pass

    def calculateParticipantMomentaryVelocityZ(self, previousMoment, currentMoment):
        ''' Calculate the velocity between two moments in the Z direction. '''
        # calculate the difference in position/time from last moment to this moment
        d_delta_z = currentMoment[PositionData.POSITION][Position.Z_POS] - \
            previousMoment[PositionData.POSITION][Position.Z_POS]
        t_delta = currentMoment[PositionData.TIME] - \
            previousMoment[PositionData.TIME]
        velocity_z = d_delta_z / t_delta

        return velocity_z

    def calculateParticipantMomentaryVelocity(self, previousMoment, currentMoment):
        ''' Calculate the velocity between two moments in ALL directions. '''
        d_delta = vizmat.Distance(
            previousMoment[PositionData.POSITION], currentMoment[PositionData.POSITION])
        t_delta = currentMoment[PositionData.TIME] - \
            previousMoment[PositionData.TIME]
        v = d_delta / t_delta
        return v
