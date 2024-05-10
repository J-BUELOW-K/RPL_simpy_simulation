
"""ICMPv6 RPL Control Message Codes"""
CODE_DIS = 0
CODE_DIO = 1
CODE_DAO = 2
CODE_DAO_ACK = 3

"""ICMPv6 type values"""
TYPE_RPL_CONTOL_MSG = 155

"""Network defines"""
SIM_TIME = 500
NUMBER_OF_NODES = 50
RADIUS = 0.2

NODE_TRANSMIT_TIMER = 5 # Periodic transmit timer - in simpy time units
NODE_TRANSMIT_TIMER_JITTER = 2 # Jitter for the periodic transmit timer - in simpy time units  VERY IMPORTANT! WITHOUT JITTER, ALL NODES WILL TRANSMIT AT THE SAME TIME WHICH WILL BREAKS STUFF
NODE_KILL_PROBABILITY = 0.05 # Probability that a node will die (stop transmitting) - this is used to simulate node death
NODE_REVIVE_PROBABILITY = 0.5 # Probability that a node will revive (start transmitting) - this is used to simulate node death


"""dodag defines"""
ROOT_RANK = 0
INFINITE_RANK = 0xffff
INFINITE_CUMULATIVE_ETX = 0xffffffff # has to be big
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

"""Metric Object defines"""
METRIC_OBJECT_NONE = 0
METRIC_OBJECT_HOPCOUNT = 1
METRIC_OBJECT_ETX = 2
METRIC_OBJECT_TYPE = METRIC_OBJECT_ETX # This is the metric object that the simulation will use - choose either of the above

"""imaginary ISP "assigned" network prefix for ipv6 global unicast address (used for the node)"""
IPV6_GLOBAL_UCAST_NETWORK_PREFIX = "2001:db8:0:1" # (subnet is simply set to 1)

"""Link Local IPv6 Address defines"""
IPV6_ADDRESS_PREFIX_LEN = 64
IPV6_ADDRESS_PREFIX_HEX_LEN = 16 # (64 bits = 16 hex characters)
IPV6_ADDRESS_HEX_LEN = 32 # (128 bits = 32 hex characters) 

"""Network and dodag plotting setting"""
DODAG_NODE_SIZE = 150
NETWORK_NODE_SIZE = 80
LABLE_SIZE = 7