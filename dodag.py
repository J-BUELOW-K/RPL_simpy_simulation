import math
import hashlib
from ipaddress import ip_address

import control_messages
import defines
from defines import METRIC_OBJECT_TYPE, METRIC_OBJECT_NONE, METRIC_OBJECT_HOPCOUNT, METRIC_OBJECT_ETX

# Note: Global Unicast vs Link Local ipv6 addresses. The nodes in our RPL network does not need to be individually reachable from the internet, so we can use link local ipv6 addresses.
# The root might still be reachable from the global internet, so it should have a global unicast ipv6 address
# as stated in the RPL standard: In Storing mode operation, the IPv6 source and destination, addresses of a DAO message MUST be link-local addresses.
# In short: We will use link local ipv6 addresses for all nodes in the network. This means that the network prefix will be fe80::/10 and the interface part will be the node_id.

def generate_linklocal_ipv6_address(node_id:int) -> str:  
    network = "fe80:0000:0000:0000" # link local network prefix

    interface_hex_len = defines.IPV6_ADDRESS_HEX_LEN - defines.IPV6_ADDRESS_PREFIX_HEX_LEN
    hardware_unique = format(node_id, f'0{interface_hex_len}x') 
    hardware_unique = hardware_unique[:4] + ":" + hardware_unique[4:8] + ":" + hardware_unique[8:12] + ":" + hardware_unique[12:16]

    full_ipv6_address_str = f"{network}:{hardware_unique}"
    ipv6_address_str = str(ip_address(full_ipv6_address_str)) # convert from full ipv6 address to abreviated ipv6 address

    return ipv6_address_str

def print_ipv6_address(ipv6_address:str, ipv6_address_prefix_len:int):
    print(f"IPv6 address: {ipv6_address}/{ipv6_address_prefix_len}")


class Dodag:
    def __init__(self, env:object, dodag_id, dodag_version_num, rank = defines.INFINITE_RANK):  # , MinHopRankIncrease = 256.0):
        self.dodag_id = dodag_id # (string) ipv6 address of the root (as acording to the RPL standard)
        self.env = env
        self.dodag_version_num = dodag_version_num # 0
        self.prefered_parent = None # node_id of prefered parent
        self.prefered_parent_rank = defines.INFINITE_RANK

        self.rank = rank

        self.metric_object = None
        if METRIC_OBJECT_TYPE == METRIC_OBJECT_HOPCOUNT:
            self.metric_object = control_messages.HP_OBJ(0) # init hopcount to 0
        elif METRIC_OBJECT_TYPE == METRIC_OBJECT_ETX:
            self.metric_object = control_messages.ETX_OBJ(0) # init ETX to 0
            
        self.surrounding_dodags = {} # dict of dodag_ids of surrounding dodags and their timestamps

        self.dao_sequence = 0 # init to 0
        self.children_dao_seq_list = [] # list of tuples (child_node_id, seq_num) - used to keep track of the sequence number of the DAO messages sent to the children
        self.downward_routes = {} # ROUTING TABLE - dict of downward routes. format: (destination ipv6 address, next_hop ipv6 address)


class Rpl_Instance:
    def __init__(self, rpl_instance_id):
        self.rpl_instance_id = rpl_instance_id
        self.dodag_list = []

    def add_dodag(self, dodag: Dodag):
        self.dodag_list.append(dodag)
