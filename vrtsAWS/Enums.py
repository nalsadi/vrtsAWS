# Stores some enums that are used throughout the program

class Phase:
	PHASE_I = 0
	PHASE_II = 1
	PHASE_III = 2
	PHASE_IV = 3
	PHASE_V = 4

	@staticmethod
	def toStr(num):
		if num == 0:
			return "PHASE_I"
		elif num == 1:
			return "PHASE_II"
		elif num == 2:
			return "PHASE_III"
		elif num == 3:
			return "PHASE_IV"
		elif num == 4:
			return "PHASE_V"
			
			
class TrialResult:
	SAFE_CROSSING = 0
	HIT = 1
	OP_INTERVENED = 2
	ENTERED_BEFORE_FIRST_CAR = 3
	CHILD_INTERVENED = 4
	
	@staticmethod
	def toStr(num):
		if num == 0:
			return "SAFE_CROSSING"
		elif num == 1:
			return "HIT"
		elif num == 2:
			return "OP_INTERVENE"
		elif num == 3:
			return "ENTERED_BEFORE_FIRST_CAR"
		elif num == 4:
			return "CHILD_INTERVENED"
	
			
class Intervention:
	NO_INTERVENTION = 0
	OP_INTERVENED = 1
	CHILD_INTERVENED = 2
	
	@staticmethod
	def toStr(num):
		if num == 0:
			return "NO_INTERVENTION"
		elif num == 1:
			return "OP INTERVENED"
		elif num == 2:
			return "CHILD INTERVENED"
	
			
class PathDetailEnum:
	ENTER = 0
	EXIT = 1


class PercentChecking:
	# % checking in road/on sidewalk
	ON_SIDEWALK = 0
	IN_ROAD = 1


class CheckingState:
	NO_CHECKING = 0
	PARTIAL_CHECKING_LEFT = 1
	FULL_CHECKING_LEFT = 2
	PARTIAL_CHECKING_RIGHT = 3
	FULL_CHECKING_RIGHT = 4
	
	@staticmethod
	def toStr(num):
		if num == 0:
			return "NO_CHECKING"
		elif num == 1:
			return "PARTIAL_CHECKING_LEFT"
		elif num == 2:
			return "FULL_CHECKING_LEFT"
		elif num == 3:
			return "PARTIAL_CHECKING_RIGHT"
		elif num == 4:
			return "FULL_CHECKING_RIGHT"


class ParticipantDirection:
	FORWARD = 0
	BACKWARD = 1
	
	@staticmethod
	def toStr(num):
		if num == 0:
			return "FORWARD"
		elif num == 1:
			return "BACKWARD"
	

class Gap:
	METERS = 0
	SECONDS =  1


class TrialType:
	NONE = 0
	PRACTICE = 1
	PILOT = 2
	EVASIVE = 3
	SpeedTest = 4
	STANDARD_ConstantGap_PRE = 5
	STANDARD_ConstantGap_POST = 6
	STANDARD_Familiarity_PRE = 7
	STANDARD_Familiarity_POST = 8
	STANDARD_VariableGap_PRE = 9
	STANDARD_VariableGap_POST = 10
	STANDARD_IncrementalGap_PRE = 11
	STANDARD_IncrementalGap_POST = 12
	TimePresOn_PRE = 13
	TimePresOff_PRE = 14
	TimePresOn_POST = 15
	TimePresOff_POST = 16
	SpeedTest_Running = 17
	Familiarization_BP = 18
	Familiarization_BP_OFF = 19
	NoCars_BP = 20
	NoCars_BP_OFF = 21
	NoSound_BP = 22
	NoSound_BP_OFF = 23
	Practice_BP = 24
	Practice_BP_OFF = 25
	TimePressON_BP = 26
	TimePressON_BP_OFF = 27
	
	
	@staticmethod
	def toStr(num):
		if num == 0:
			return "NONE"
		elif num == 1:
			return "PRACTICE"
		elif num == 2:
			return "PILOT"
		elif num == 3: 
			return "EVASIVE"
		elif num == 4:
			return "SpeedTest"
		elif num == 5:
			return "STANDARD_ConstantGap_PRE"
		elif num == 6:
			return "STANDARD_ConstantGap_POST"
		elif num == 7:
			return "STANDARD_Familiarity_PRE"
		elif num == 8:
			return "STANDARD_Familiarity_POST"
		elif num == 9:
			return "STANDARD_VariableGap_PRE"
		elif num == 10:
			return "STANDARD_VariableGap_POST"
		elif num == 11:
			return "STANDARD_IncrementalGap_PRE"
		elif num == 12:
			return "STANDARD_IncrementalGap_POST"
		elif num == 13:
			return "TimePresOn_PRE"
		elif num == 14:
			return "TimePressOff_PRE"
		elif num == 15:
			return "TimePresOn_POST"
		elif num == 16:
			return "TimePressOff_POST"
		elif num == 17:
			return "SpeedTest_Running"
		elif num == 18:
			return "Familiarization_BP"
		elif num == 19:
			return "Familiarization_BP_OFF"
		elif num == 20:
			return "NoCars_BP"
		elif num == 21:
			return "NoCars_BP_OFF"
		elif num == 22:
			return "NoSound_BP"
		elif num == 23:
			return "NoSound_BP_OFF"
		elif num == 24:
			return "Practice_BP"
		elif num == 25:
			return "Practice_BP_OFF"
		elif num == 26:
			return "TimePressON_BP"
		elif num == 27:
			return "TimePressON_BP_OFF"

class DataCalculationMode:
	RIGHT_FACING_CARS_ONLY = 0
	LEFT_FACING_CARS_ONLY = 1
	BOTH_DIRECTIONS = 2
	

class EvasiveActionType:
	NONE = 0
	RUNFORWARD = 1
	JUMPBACK = 2


class HotspotId:
	STARTING = 1
	NEARSIDEWALK = 2
	NEARROAD = 3
	FARROAD = 4
	FARSIDEWALK = 5


class MarkerViewType:
	CYLINDER = 1
	BOX = 2


class MarkerState:
	INVISIBLE = 1
	ENTER = 2
	DONOTENTER = 3


class FlowInput:
	GETREADY = 1
	SETREADY = 2
	START = 3
	END = 4	
	SETBUSY = 5
	TOGGLEFREERANGE = 6
	MOVEPREVIOUSTRIAL = 7
	MOVENEXTTRIAL = 8
	SELECTTRIAL = 9
	RESETMAINVIEW = 10
	CONTINUE_TO_FREERANGE = 11
	CONTINUE_TO_GETTINGREADY = 12
	CONTINUE_TO_SELECTINGTRIAL = 13
	FIRST_CAR_PASSED_PARTICIPANT = 14
	#RESET_FIRST_CAR_TEST = 15
	
	@staticmethod
	def toStr(num):
		if num == 1:
			return "GETREADY"
		elif num == 2:
			return "SETREADY"
		elif num == 3:
			return "START"
		elif num == 4:
			return "END"
		elif num == 5:
			return "SETBUSY"
		elif num == 6:
			return "TOGGLEFREERANGE"
		elif num == 7:
			return "MOVEPREVIOUSTRIAL"
		elif num == 8:
			return "MOVENEXTTRIAL"
		elif num == 9:
			return "SELECTTRIAL"
		elif num == 10:
			return "RESETMAINVIEW"
		elif num == 11: 
			return "CONTINUE_TO_FREERANGE"
		elif num == 12:
			return "CONTINUE_TO_GETTINGREADY"
		elif num == 13:
			return "CONTINUE_TO_SELECTINGTRIAL"
		elif num == 14:
			return "FIRST_CAR_PASSED_PARTICIPANT"


class FlowState:
	""" See Master Document for description of FlowStates """
	GETTINGREADY = 1
	READY = 2
	START = 3
	END = 4
	BUSY = 5
	FREERANGE = 6
	SELECTINGTRIAL = 7
	TRIALSCOMPLETED = 8
	
	@staticmethod
	def toStr(num):
		""" Print the state words, not numbers """
		if num == 1:
			return "GETTINGREADY"
		elif num == 2:
			return "READY"
		elif num == 3:
			return "START"
		elif num == 4:
			return "END"
		elif num == 5:
			return "BUSY"
		elif num == 6:
			return "FREERANGE"
		elif num == 7:
			return "SELECTINGTRIAL"
		elif num == 8:
			return "TRIALSCOMPLETED"


class KeyboardState:
	DISABLED = 0
	ENABLED = 1
	
	@staticmethod
	def toStr(num):
		if num == 0:
			return "DISABLED"
		elif num == 1:
			return "ENABLED"


class DataCollectionState:
	READY = 1
	STOPPED = 2
	STARTED = 3
	ENDING = 4
	QUITTING = 5
	BETWEEN_TRIALS = 6
	SELECTINGTRIAL = 7
	
	@staticmethod
	def toStr(num):
		if num == 1:
			return "READY"
		elif num == 2:
			return "STOPPED"
		elif num == 3:
			return "STARTED"
		elif num == 4:
			return "ENDING"
		elif num == 5:
			return "QUITTING"
		elif num == 6:
			return "BETWEEN_TRIALS"
		elif num == 7:
			return "SELECTINGTRIAL"


class CarBehaviour:
	NoCars = 1
	SPAWNONROADENTER = 2
	SPAWNONSTARTTRIAL = 3


class CarActionType:
	MOVE = 1
	ACCELERATE = 2
	DECELERATE = 3
	TOGGLEHORN = 4
	HITCOURSE = 5


class Direction:
	RIGHT = 1
	LEFT = 2


####
# DATA PARSER variables
###

class TrialData:
	PARTICIPANT_POSITION = 0
	PARTICIPANT_ORIENTATION = 1
	RIGHT_FACING_CAR_DATA = 2
	LEFT_FACING_CAR_DATA = 3
	VISUAL_OBSTRUCTION_DATA = 4
	TRIAL_DATA = 5
	INTERVENTION = 6


class CheckingData:
	# Used in return value from calculateXXXChecks functions
	PARTIAL_CHECKS = 0
	FULL_CHECKS = 1
	
	@staticmethod
	def toStr(num):
		if num == PARTIAL_CHECKS:
			return "PARTIAL CHECKS"
		elif num == FULL_CHECKS:
			return "FULL CHECKS"
		

class PositionData:
	#positionData
	TIME = 0
	POSITION = 1
	
	
class VelocityData:
	#velocityData
	TIME = 0
	VELOCITY = 1
	
	
class Position:
	X_POS = 0
	Y_POS = 1
	Z_POS = 2


class OrientationData:
	#orientationData
	TIME = 0
	ORIENTATION = 1

	
class OrientationType:
	YAW = 0
	PITCH = 1


#carPositionData
class CarPositionData:
	CARMESH = 0
	CARID = 1
	CARTIME = 2
	CARPOSITION = 3
	CARDIRECTION = 4
	

#boundingBox
class BoundingBox:
	XMIN = 0
	XMAX = 1
	ZMIN = 2
	ZMAX = 3

	
class AvatarBehaviour:
	NONE = 0
	SAFE_CROSSING = 1
	RISKY_CROSSING = 2

	
class ParticipantInputType:
	MOUSE_AND_KEYBOARD = 0
	HMD = 1
	XBOX_CONTROLLER = 2