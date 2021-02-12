"""Holds global data and functions, this file will be created by the GUI"""
from decimal import Decimal, getcontext
#set the precision of Decimal numbers to 10 (should be at least double the number of digits that we are rounding to)
getcontext().prec = 10
from Enums import Direction, TrialType, CarBehaviour, FlowState, CarActionType, AvatarBehaviour, ParticipantInputType
import time
###
# GLOBAL VARIABLES
###
# ****************************************** '
# Using vizconnect_file:'viz_move_walking_VR.py'
# ****************************************** '
vizconnect_file='viz_move_walking_VR.py'
startingHotspotCenter = -1
startingHotspotDepth = 1
startingPosition = []
trackerurl = "PPT0@192.168.99.1"
headset_fov = 80  # diagonal fov = 60, so horizontal (by Pythagorean theorem) is 46.852 -- (now using oculus in steroscopic - Changed to 80
RADTODEG = 57.2957795
numTypesofCars = 15
randomize_car_spawn_order = False
roadWidth = 5.5
numOfLanes = 1
closeLaneCenterZ = roadWidth * 0.25
farLaneCenterZ = roadWidth * 0.75
timetoCross = 2.0
dataCollectionPeriod  =  0.01
nearMissDistance  =  1
criticalPoint = 1.375
hesitationVelThresh = 0.1
hesitationTimeThresh = 0.3
initialSpawnTime  =  2.0
respawnStart  =  -200
respawnEnd  =  130
dataDirectoryPath  = 'C:\\vr\\vr3\\_testing_data\\'
dataFileExtension   = '.txt'
currentTrial = None
initialFlowState = FlowState.FREERANGE
trial_intervention = 0
avgCarLength = 2.7
participantId  = 'VR2L-45-AdF'
participantVariableNames = ['ParticipantId','ParticipantAge','ParticipantSex','ParticipantHeight']
participantVariableValues = ['VR2L-45-AdF','','','']
initialMainViewPosition = [0,1.82,-2.7]
fullCheckAngle  =  65
partialCheckAngle  =  45
max_check_angle = -113.0  # beyond this angle they can no longer see the road from the starting point
checkMaxAnglePitch  =  20
practiceTrialsMeanVelocity = 0
timeStamp = str(int(time.mktime(time.localtime())))
participantInputType = ParticipantInputType.HMD
trialInits = \
[\
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Near-Post', CarBehaviour.SPAWNONSTARTTRIAL, [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33,38.89,43.75,48.61,53.47,58.33,63.19,68.06,72.92,77.78,82.64,87.5,92.36,97.22,102.08,106.94,111.81,116.67,121.53,126.39,131.25,136.11,140.97,145.83,150.69,155.56,160.42,165.28,170.14,175,179.86,184.72,189.58,194.44], [], 19.44446 , 19.44446, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Near-Post', CarBehaviour.SPAWNONSTARTTRIAL, [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33], [], 8.33334 , 8.33334, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Far-Post', CarBehaviour.SPAWNONSTARTTRIAL, [], [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33], 8.33334 , 8.33334, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Near-Post', CarBehaviour.SPAWNONSTARTTRIAL, [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33,38.89,43.75,48.61,53.47,58.33,63.19,68.06,72.92,77.78,82.64,87.5,92.36,97.22,102.08,106.94,111.81,116.67,121.53,126.39,131.25,136.11,140.97,145.83,150.69,155.56,160.42,165.28,170.14,175,179.86,184.72,189.58,194.44], [], 19.44446 , 19.44446, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Far-Post', CarBehaviour.SPAWNONSTARTTRIAL, [], [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33], 8.33334 , 8.33334, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Far-Post', CarBehaviour.SPAWNONSTARTTRIAL, [], [38.89,43.75,48.61,53.47,58.33,63.19,68.06,72.92,77.78,82.64,87.5,92.36,97.22,102.08,106.94,111.81,116.67,121.53,126.39,131.25,136.11,140.97,145.83,150.69,155.56,160.42,165.28,170.14,175,179.86,184.72,189.58,194.44], 19.44446 , 19.44446, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Near-Post', CarBehaviour.SPAWNONSTARTTRIAL, [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33], [], 8.33334 , 8.33334, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Far-Post', CarBehaviour.SPAWNONSTARTTRIAL, [], [38.89,43.75,48.61,53.47,58.33,63.19,68.06,72.92,77.78,82.64,87.5,92.36,97.22,102.08,106.94,111.81,116.67,121.53,126.39,131.25,136.11,140.97,145.83,150.69,155.56,160.42,165.28,170.14,175,179.86,184.72,189.58,194.44], 19.44446 , 19.44446, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Near-Post', CarBehaviour.SPAWNONSTARTTRIAL, [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33], [], 8.33334 , 8.33334, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Far-Post', CarBehaviour.SPAWNONSTARTTRIAL, [], [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33], 8.33334 , 8.33334, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Far-Post', CarBehaviour.SPAWNONSTARTTRIAL, [], [38.89,43.75,48.61,53.47,58.33,63.19,68.06,72.92,77.78,82.64,87.5,92.36,97.22,102.08,106.94,111.81,116.67,121.53,126.39,131.25,136.11,140.97,145.83,150.69,155.56,160.42,165.28,170.14,175,179.86,184.72,189.58,194.44], 19.44446 , 19.44446, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post'),
(TrialType.STANDARD_ConstantGap_PRE, 'g2_Near-Post', CarBehaviour.SPAWNONSTARTTRIAL, [16.67,18.75,20.83,22.92,25,27.08,29.17,31.25,33.33,35.42,37.5,39.58,41.67,43.75,45.83,47.92,50,52.08,54.17,56.25,58.33,60.42,62.5,64.58,66.67,68.75,70.83,72.92,75,77.08,79.17,81.25,83.33,38.89,43.75,48.61,53.47,58.33,63.19,68.06,72.92,77.78,82.64,87.5,92.36,97.22,102.08,106.94,111.81,116.67,121.53,126.39,131.25,136.11,140.97,145.83,150.69,155.56,160.42,165.28,170.14,175,179.86,184.72,189.58,194.44], [], 19.44446 , 19.44446, 1, 1, True, 0, 0, AvatarBehaviour.NONE, 'post')
]
carsInits = \
[
]
practiceTrialsMeanCrossingTime = 0
practiceTrialsMeanCrossingTimeCount = 0
dumpedDataExtension = "_dumpedData.pkl"
participantDataExtension = "_participantData.pkl"
boundingBoxDataExtension = "_boundingBoxData.pkl"

