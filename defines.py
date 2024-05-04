
"""ICMPv6 RPL Control Message Codes"""
CODE_DIS = 0
CODE_DIO = 1
CODE_DAO = 2
CODE_DAO_ACK = 3

"""ICMPv6 type values"""
TYPE_RPL_CONTOL_MSG = 155

"""Network defines"""
SIM_TIME = 500
NUMBER_OF_NODES = 70
RADIUS = 0.2

NODE_TRANSMIT_TIMER = 5 # Periodic transmit timer - in simpy time units

"""dodag defines"""
ROOT_RANK = 0
INFINITE_RANK = 0xffff
INFINITE_CUMULATIVE_ETX = 0xffff
INFINITE_HOP_COUNT = 0xffff

"""OF0 defines"""
# Constants (as defined in Section 6.3 in rfc6552):
DEFAULT_STEP_OF_RANK = 3
MINIMUM_STEP_OF_RANK = 1
MAXIMUM_STEP_OF_RANK = 9
DEFAULT_RANK_STRETCH = 0
MAXIMUM_RANK_STRETCH = 5
DEFAULT_RANK_FACTOR  = 1
MINIMUM_RANK_FACTOR  = 1
MAXIMUM_RANK_FACTOR  = 4
DEFAULT_MIN_HOP_RANK_INCREASE = 256 # (defined in sec 18.2.8 in rfc6550)

#
METRIC_OBJECT_NONE = 0
METRIC_OBJECT_HOPCOUNT = 1
METRIC_OBJECT_ETX = 2
METRIC_OBJECT_TYPE = METRIC_OBJECT_NONE # This is the metric object that the simulation will use - choose either of the above

