from Enums import TrialType, ParticipantInputType
import Globals

class Trial:
	"""Stores given, trial-specific data such as trialType, trialNumber, etc.
	"""
	
	number = 0
			
	
	def __init__(self, 
	pTrialType,
	#pPrePost,
	pPredefinedConditionId, 
	pCarBehaviour, 
	pRightFacingCarSpacingList, 
	pLeftFacingCarSpacingList, 
	pRightFacingCarSpeed=0, 
	pLeftFacingCarSpeed=0, 
	pForwardAccelThresh =0, 
	pBackwardAccelThresh =0, 
	pIsContinuous=False, 
	pTimePressure =0, 
	pAttemptNumber=0,
	pAvatarBehaviour=None,
	pPrePost = "NONE",):
		
		if (pTrialType != TrialType.NONE): 
			self.__trialNumber = Trial.number
			Trial.number += 1
			####print "yes"
		else:
			self.__trialNumber = -1
			####print "no"
			
		self.__attemptNumber = pAttemptNumber # the number of times this trial has been attempted
		self.__trialType = pTrialType
		self.__PrePost = pPrePost
		self.__predefinedConditionId = pPredefinedConditionId
		self.__carBehaviour = pCarBehaviour
		self.__rightFacingCarGaps = pRightFacingCarSpacingList
		self.__leftFacingCarGaps = pLeftFacingCarSpacingList
		self.__rightFacingCarSpeed = pRightFacingCarSpeed
		self.__leftFacingCarSpeed = pLeftFacingCarSpeed

			
		self.__forwardAccelThresh = pForwardAccelThresh
		self.__backwardAccelThresh = pBackwardAccelThresh
		self.__isContinuous = pIsContinuous
		self.__isTimePressure = pTimePressure
		self.__avatarBehaviour = pAvatarBehaviour
		
	def getTrialNumber(self):
		return self.__trialNumber
		
	def getAttemptNumber(self):
		return self.__attemptNumber
		
	def incrementAttemptNumber(self):
		self.__attemptNumber += 1
		
	def getTrialAndAttemptNumber(self):
		""" Human readable trial and attempt number """
		return str(self.__trialNumber + 1) + "-" + str(self.__attemptNumber)
	
	def getTrialType(self):
		return self.__trialType
	
	def getPredefinedConditionId(self):
		return self.__predefinedConditionId
		
	def getPrePost(self):
		return self.__PrePost
	
	def getCarBehaviour(self):
		return self.__carBehaviour
	
	def getRightFacingCarSpeed(self):
		return self.__rightFacingCarSpeed
	
	def getLeftFacingCarSpeed(self):
		return self.__leftFacingCarSpeed
		
	def getRightFacingCarGaps(self):
		return self.__rightFacingCarGaps
	
	def getLeftFacingCarGaps(self):
		return self.__leftFacingCarGaps
	
	def getForwardAccelThresh (self):
		return self.__forwardAccelThresh
		
	def getBackwardAccelThresh (self):
		return self.__backwardAccelThresh
	
	def getIsContinuous(self):
		return self.__isContinuous
	
	def getIsTimePressure(self):
		return self.__isTimePressure
	
	def getAvatarBehaviour(self):
		return self.__avatarBehaviour
	