## Trial Data Collection Names ##

def get_var_names_list():
	''' All variables found in the SPSS output are listed here. '''
	return [
		ParticipantId,
		FileName,
		TrialNumber,
		AttemptNumber,
		LastModified,
		Phase,
		TrialType,
		LeftFacingCarSpeed,
		RightFacingCarSpeed,
		MeanWalkingSpeedHMDV,
		MeanWalkingSpeedRWV,
		MeanRunningSpeedRWV,
		TrialResult,
		TrialDuration,

		# Road entrance variables
		RoadEntrance, # Not a real variable, but needed in the headers
		DurationInRoad,
		DurationInMiddleOfRoad,
		DurationInMiddleOfRoadList,
		DurationInMiddleOfRoadSum,
		SimulatedHitHMDV,
		SimulatedHitRWV,
		MeanVelInRoad,
		HeadAngleOnEnterRoad,
		MeanHeadAngleInRoad,
		HeadAngleOnLossOfView,
		FullChecksInRoad,
		FullChecksOnSidewalk,
		FullChecksInCarPath,
		FullChecksBetweenCurbAndCarPath,
		PartialChecksInRoad,
		PartialChecksOnSidewalk,
		PartialChecksInCarPath,
		PartialChecksBetweenCurbAndCarPath,
		FullChecksWithClosestCarInViewInRoad,
		FullChecksWithClosestCarInViewOnSidewalk,
		FullChecksWithClosestCarInViewInCarPath,
		FullChecksWithClosestCarInViewBetweenCurbAndCarPath,
		PartialChecksWithClosestCarInViewInRoad,
		PartialChecksWithClosestCarInViewOnSidewalk,
		PartialChecksWithClosestCarInViewInCarPath,
		PartialChecksWithClosestCarInViewBetweenCurbAndCarPath,
		MeanFullCheckTimeInRoad,
		MeanFullCheckTimeOnSidewalk,
		MeanFullCheckTimeInCarPath,
		MeanFullCheckTimeBetweenCurbAndCarPath,
		MeanPartialCheckTimeInRoad,
		MeanPartialCheckTimeOnSidewalk,
		MeanPartialCheckTimeInCarPath,
		MeanPartialCheckTimeBetweenCurbAndCarPath,
		MeanTimeWithClosestCarInViewInRoad,
		MeanTimeWithClosestCarInViewOnSidewalk,
		MeanTimeWithClosestCarInViewInCarPath,
		MeanTimeWithClosestCarInViewBetweenCurbAndCarPath,
		PercentFullCheckingInRoad,
		PercentFullCheckingOnSidewalk,
		PercentFullCheckingInCarPath,
		PercentFullCheckingBetweenCurbAndCarPath,
		PercentPartialCheckingInRoad,
		PercentPartialCheckingOnSidewalk,
		PercentPartialCheckingInCarPath,
		PercentPartialCheckingBetweenCurbAndCarPath,
		PercentTimeClosestCarInViewInRoad,
		PercentTimeClosestCarInViewOnSidewalk,
		PercentTimeClosestCarInViewInCarPath,
		PercentTimeClosestCarInViewBetweenCurbAndCarPath,	
		PctFullCheckingInRoadCarInView,
		PctFullCheckingOnSidewalkCarInView,
		PctFullCheckingInCarPathCarInView,
		PctFullCheckingBetweenCurbAndCarPathCarInView,
		PctPartialCheckingInRoadCarInView,
		PctPartialCheckingOnSidewalkCarInView,
		PctPartialCheckingInCarPathCarInView,
		PctPartialCheckingBetweenCurbAndCarPathCarInView,
		PercentTimeClosestLFCInViewInNearLane,
		PercentTimeClosestRFCInViewInNearLane,
		PercentTimeClosestLFCInViewInFarLane,
		PercentTimeClosestRFCInViewInFarLane,
		PercentTimeClosestLFCInViewBetweenCarPaths,
		PercentTimeClosestRFCInViewBetweenCarPaths,
		LFCInViewOnMiddleOfRoadEntry,
		
		# Trial summary variables
		DurationInCarPath,
		HeadAngleOnEnterCarPath,
		MeanHeadAngleInCarPath,
		
		NearMissDistance,
		NearMissTime,
		NearMisses, 
		Hits, 
		MissedOpportunities,

		TLSEnterRoad, 
		TLSEnterCarPath, 
		TLSExitCarPath, 
		TLSExitCarPathAvgWalkingSpeedRWV,
		TLSExitCarPathAvgWalkingSpeedHMDV,
		TLSOnLossOfView,

		VelEnterRoad, 
		MeanVelInCarPath,
		VelEnterCarPath, 
		VelExitCarPath, 
		MaxVelInCarPath, 
		MinVelInCarPath, 

		CrossingTime,
		StartDelay,
		GapLength,
		GapInterval,
		MarginOfSafety,
		PercentageOfGapUsed,

		MaxRejectedGapTime,
		AverageRejectedGapTime,
		MinRejectedGapTime,

		TrafficVolume,
		TrafficVolumePerMinute,

		JumpBacks,
	]

def get_per_road_entrance_variables():
	per_road_entrance_variables = [
			SimulatedHitHMDV,
			SimulatedHitRWV,
			DurationInRoad,
			HeadAngleOnEnterRoad,
			MeanHeadAngleInRoad,
			MeanVelInRoad,
			FullChecksInRoad,
			FullChecksOnSidewalk,
			FullChecksInCarPath,
			FullChecksBetweenCurbAndCarPath,
			PartialChecksInRoad,
			PartialChecksOnSidewalk,
			PartialChecksInCarPath,
			PartialChecksBetweenCurbAndCarPath,
			FullChecksWithClosestCarInViewInRoad,
			FullChecksWithClosestCarInViewOnSidewalk,
			FullChecksWithClosestCarInViewInCarPath,
			FullChecksWithClosestCarInViewBetweenCurbAndCarPath,
			PartialChecksWithClosestCarInViewInRoad,
			PartialChecksWithClosestCarInViewOnSidewalk,
			PartialChecksWithClosestCarInViewInCarPath,
			PartialChecksWithClosestCarInViewBetweenCurbAndCarPath,
			MeanFullCheckTimeInRoad,
			MeanFullCheckTimeOnSidewalk,
			MeanFullCheckTimeInCarPath,
			MeanFullCheckTimeBetweenCurbAndCarPath,
			MeanPartialCheckTimeInRoad,
			MeanPartialCheckTimeOnSidewalk,
			MeanPartialCheckTimeInCarPath,
			MeanPartialCheckTimeBetweenCurbAndCarPath,
			MeanTimeWithClosestCarInViewInRoad,
			MeanTimeWithClosestCarInViewOnSidewalk,
			MeanTimeWithClosestCarInViewInCarPath,
			MeanTimeWithClosestCarInViewBetweenCurbAndCarPath,
			PercentFullCheckingInRoad,
			PercentFullCheckingOnSidewalk,
			PercentFullCheckingInCarPath,
			PercentFullCheckingBetweenCurbAndCarPath,
			PercentPartialCheckingInRoad,
			PercentPartialCheckingOnSidewalk,
			PercentPartialCheckingInCarPath,
			PercentPartialCheckingBetweenCurbAndCarPath,
			PercentTimeClosestCarInViewInRoad,
			PercentTimeClosestCarInViewOnSidewalk,
			PercentTimeClosestCarInViewInCarPath,
			PercentTimeClosestCarInViewBetweenCurbAndCarPath,
			PctFullCheckingInRoadCarInView,
			PctFullCheckingOnSidewalkCarInView,
			PctFullCheckingInCarPathCarInView,
			PctFullCheckingBetweenCurbAndCarPathCarInView,
			PctPartialCheckingInRoadCarInView,
			PctPartialCheckingOnSidewalkCarInView,
			PctPartialCheckingInCarPathCarInView,
			PctPartialCheckingBetweenCurbAndCarPathCarInView,
		]
		
	return per_road_entrance_variables

def get_tuple_variables():
	''' Return a list of the variables that are currently represented as tuples (RFC, LFC, overall) '''
	tuple_variables = [
		Hits,
		MissedOpportunities,
		SimulatedHitHMDV,
		SimulatedHitRWV,
		NearMisses,
		TLSEnterCarPath,
		TLSEnterRoad,
		TLSExitCarPath,
		VelEnterCarPath,
		VelExitCarPath,
		MaxVelInCarPath,
		MinVelInCarPath,
		StartDelay,
		GapInterval,
		GapLength,
		MarginOfSafety,
		PercentageOfGapUsed,
		MaxRejectedGapTime,
		AverageRejectedGapTime,
		MinRejectedGapTime,
		TrafficVolume,
		TrafficVolumePerMinute
	]
	return tuple_variables

# Practice & Demographic Info
ParticipantId = "ParticipantId"
FileName = "FileName"
TrialNumber = "TrialNumber"
AttemptNumber = "AttemptNumber"
LastModified = "LastModified"
Phase = "Phase"
TrialType = "TrialType"
LeftFacingCarSpeed = "LeftFacingCarSpeed"
RightFacingCarSpeed = "RightFacingCarSpeed"
MeanWalkingSpeedHMDV = "MeanWalkingSpeedHMDV"
MeanWalkingSpeedRWV = "MeanWalkingSpeedRWV"
MeanRunningSpeedRWV = "MeanRunningSpeedRWV"
TrialResult = "TrialResult"
TrialDuration = "TrialDuration"
RoadEntrance = "RoadEntrance"

MeanVelInRoad = "MeanVelInRoad"
MeanVelInCarPath = "MeanVelInCarPath"

DurationInRoad = "DurationInRoad"
HeadAngleOnEnterRoad = "HeadAngleOnEnterRoad"
MeanHeadAngleInRoad = "MeanHeadAngleInRoad"

FullChecksInRoad = 'FullChecksInRoad'
FullChecksOnSidewalk = 'FullChecksOnSidewalk'
FullChecksInCarPath = 'FullChecksInCarPath'
FullChecksBetweenCurbAndCarPath = 'FullChecksBetweenCurbAndCarPath'
PartialChecksInRoad = 'PartialChecksInRoad'
PartialChecksOnSidewalk = 'PartialChecksOnSidewalk'
PartialChecksInCarPath = 'PartialChecksInCarPath'
PartialChecksBetweenCurbAndCarPath = 'PartialChecksBetweenCurbAndCarPath'

FullChecksWithClosestCarInViewInRoad = 'FullChecksWithClosestCarInViewInRoad'
FullChecksWithClosestCarInViewOnSidewalk = 'FullChecksWithClosestCarInViewOnSidewalk'
FullChecksWithClosestCarInViewInCarPath = 'FullChecksWithClosestCarInViewInCarPath'
FullChecksWithClosestCarInViewBetweenCurbAndCarPath = 'FullChecksWithClosestCarInViewBetweenCurbAndCarPath'
PartialChecksWithClosestCarInViewInRoad = 'PartialChecksWithClosestCarInViewInRoad'
PartialChecksWithClosestCarInViewOnSidewalk = 'PartialChecksWithClosestCarInViewOnSidewalk'
PartialChecksWithClosestCarInViewInCarPath = 'PartialChecksWithClosestCarInViewInCarPath'
PartialChecksWithClosestCarInViewBetweenCurbAndCarPath = 'PartialChecksWithClosestCarInViewBetweenCurbAndCarPath'

MeanFullCheckTimeInRoad = 'MeanFullCheckTimeInRoad'
MeanFullCheckTimeOnSidewalk = 'MeanFullCheckTimeOnSidewalk'
MeanFullCheckTimeInCarPath = 'MeanFullCheckTimeInCarPath'
MeanFullCheckTimeBetweenCurbAndCarPath = 'MeanFullCheckTimeBetweenCurbAndCarPath'
MeanPartialCheckTimeInRoad = 'MeanPartialCheckTimeInRoad'
MeanPartialCheckTimeOnSidewalk = 'MeanPartialCheckTimeOnSidewalk'
MeanPartialCheckTimeInCarPath = 'MeanPartialCheckTimeInCarPath'
MeanPartialCheckTimeBetweenCurbAndCarPath = 'MeanPartialCheckTimeBetweenCurbAndCarPath'
MeanTimeWithClosestCarInViewInRoad = 'MeanTimeClosestCarInViewInRoad'
MeanTimeWithClosestCarInViewOnSidewalk = 'MeanTimeClosestCarInViewOnSidewalk'
MeanTimeWithClosestCarInViewInCarPath = 'MeanTimeClosestCarInViewInCarPath'
MeanTimeWithClosestCarInViewBetweenCurbAndCarPath = 'MeanTimeClosestCarInViewBetweenCurbAndCarPath'

PercentFullCheckingInRoad = 'PercentFullCheckingInRoad'
PercentFullCheckingOnSidewalk = 'PercentFullCheckingOnSidewalk'
PercentFullCheckingInCarPath = 'PercentFullCheckingInCarPath'
PercentFullCheckingBetweenCurbAndCarPath = 'PercentFullCheckingBetweenCurbAndCarPath'
PercentPartialCheckingInRoad = 'PercentPartialCheckingInRoad'
PercentPartialCheckingOnSidewalk = 'PercentPartialCheckingOnSidewalk'
PercentPartialCheckingInCarPath = 'PercentPartialCheckingInCarPath'
PercentPartialCheckingBetweenCurbAndCarPath = 'PercentPartialCheckingBetweenCurbAndCarPath'
PercentTimeClosestCarInViewInRoad = 'PercentTimeClosestCarInViewInRoad'
PercentTimeClosestCarInViewOnSidewalk = 'PercentTimeClosestCarInViewOnSidewalk'
PercentTimeClosestCarInViewInCarPath = 'PercentTimeClosestCarInViewInCarPath'
PercentTimeClosestCarInViewBetweenCurbAndCarPath = 'PercentTimeClosestCarInViewBetweenCurbAndCarPath'

PctFullCheckingInRoadCarInView = 'PctFullCheckingInRoadCarInView'
PctFullCheckingOnSidewalkCarInView = 'PctFullCheckingOnSidewalkCarInView'
PctFullCheckingInCarPathCarInView = 'PctFullCheckingInCarPathCarInView'
PctFullCheckingBetweenCurbAndCarPathCarInView = 'PctFullCheckingBetweenCurbAndCarPathCarInView'
PctPartialCheckingInRoadCarInView = 'PctPartialCheckingInRoadCarInView'
PctPartialCheckingOnSidewalkCarInView = 'PctPartialCheckingOnSidewalkCarInView'
PctPartialCheckingInCarPathCarInView = 'PctPartialCheckingInCarPathCarInView'
PctPartialCheckingBetweenCurbAndCarPathCarInView = 'PctPartialCheckingBetweenCurbAndCarPathCarInView'

PercentTimeClosestLFCInViewInNearLane = 'PercentTimeClosestLFCInViewInNearLane'
PercentTimeClosestRFCInViewInNearLane = 'PercentTimeClosestRFCInViewInNearLane'
PercentTimeClosestLFCInViewInFarLane = 'PercentTimeClosestLFCInViewInFarLane'
PercentTimeClosestRFCInViewInFarLane = 'PercentTimeClosestRFCInViewInFarLane'
PercentTimeClosestLFCInViewBetweenCarPaths = 'PercentTimeClosestLFCInViewBetweenCarPaths'
PercentTimeClosestRFCInViewBetweenCarPaths = 'PercentTimeClosestRFCInViewBetweenCarPaths'
LFCInViewOnMiddleOfRoadEntry = 'LFCInViewOnMiddleOfRoadEntry'

HeadAngleOnLossOfView = 'HeadAngleOnLossOfView'

DurationInCarPath = "DurationInCarPath"
HeadAngleOnEnterCarPath = "HeadAngleOnEnterCarPath"
MeanHeadAngleInCarPath = "MeanHeadAngleInCarPath"
DurationInMiddleOfRoad = "DurationInMiddleOfRoad"
DurationInMiddleOfRoadList = "DurationInMiddleOfRoadList"
DurationInMiddleOfRoadSum = "DurationInMiddleOfRoadSum"

NearMissTime = "NearMissTime"
NearMissDistance = "NearMissDistance"
NearMisses = "NearMisses"
Hits = "Hits"
MissedOpportunities = "MissedOpportunities"

TLSEnterRoad = "TLSEnterRoad"
TLSEnterCarPath = "TLSEnterCarPath"
TLSExitCarPath = "TLSExitCarPath"
TLSExitCarPathAvgWalkingSpeedRWV = "TLSExitCarPathAvgWalkingSpeedRWV"
TLSExitCarPathAvgWalkingSpeedHMDV = "TLSExitCarPathAvgWalkingSpeedHMDV"
TLSOnLossOfView = "TLSOnLossOfView"

VelEnterRoad = "VelEnterRoad"
VelEnterCarPath = "VelEnterCarPath"
VelExitCarPath = "VelExitCarPath"
MaxVelInCarPath = "MaxVelInCarPath"
MinVelInCarPath = "MinVelInCarPath"

CrossingTime = "CrossingTime"
StartDelay = "StartDelay"
GapLength = "GapLength"
GapInterval = "GapInterval"
MarginOfSafety = "MarginOfSafety"
PercentageOfGapUsed = "PercentageOfGapUsed"

MaxRejectedGapTime = "MaxRejectedGapTime"
AverageRejectedGapTime = "AverageRejectedGapTime"
MinRejectedGapTime = "MinRejectedGapTime"

TrafficVolume = "TrafficVolume"
TrafficVolumePerMinute = "TrafficVolumePerMinute"

# Trial data - Goal #1
JumpBacks = "JumpBacks"
SimulatedHitHMDV = "SimulatedHitHMDV"
SimulatedHitRWV = "SimulatedHitRWV"

## Data Parser Dictionary Names ##
PracticeTrialsData = "PracticeTrialsData"
PracticeTrialMeanWalkingSpeed = "PracticeTrialMeanWalkingSpeed"
SpeedTrialMeanWalkingSpeed = "SpeedTrialMeanWalkingSpeed"