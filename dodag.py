import math
import hashlib
from ipaddress import ip_address

import control_messages
import defines
from defines import METRIC_OBJECT_TYPE, METRIC_OBJECT_NONE, METRIC_OBJECT_HOPCOUNT, METRIC_OBJECT_ETX



  
# # generate ipv6 address for a node. subnet is dodag specific and generated from rpl_instance_id, dodag_id and dodag_version_num. interface part is simply the node_id
# IPV6_ADDRESS_NETWORK = "2001:0db8:0000" # just a random network prefix (given by the ISP) (48 bits)
# IPV6_ADDRESS_PREFIX_LEN = 64 # (64 bits for the network part (48 for network, 16 for subnet) and 64 bits for the interface part)
# IPV6_ADDRESS_PREFIX_HEX_LEN = 16 # (64 bits = 16 hex characters)
# IVP6_SUBNET_HEX_LEN = 4 # (16 bits = 4 hex characters)
# IPV6_ADDRESS_HEX_LEN = 32 # (128 bits = 32 hex characters)
def generate_unicast_global_ipv6_address(node_id:int, rpl_instance_id:int, dodag_id:int, dodag_version_num:int) -> str:  
    network = defines.IPV6_ADDRESS_NETWORK
    subnet = hashlib.sha256(str.encode(bin(rpl_instance_id+dodag_id+dodag_version_num))).hexdigest()[:defines.IVP6_SUBNET_HEX_LEN]  #generate 16bit subnet for dodag from rpl_instance_id, dodag_id and dodag_version_num

    interface_hex_len = defines.IPV6_ADDRESS_HEX_LEN - defines.IPV6_ADDRESS_PREFIX_HEX_LEN
    hardware_unique = format(node_id, f'0{interface_hex_len}x') 
    hardware_unique = hardware_unique[:4] + ":" + hardware_unique[4:8] + ":" + hardware_unique[8:12] + ":" + hardware_unique[12:16]

    ipv6_address_str = f"{network}:{subnet}:{hardware_unique}"
    #ipv6_address_prefix_len = defines.IPV6_ADDRESS_PREFIX_LEN
    return ipv6_address_str   KLJAÆSDJKLÆASJDLKÆJASDLKÆJASDLKÆASJ TROR IKKE DEN SKAL VÆRE AFHÆNING AF DE HER TING:::: FOR ROOT NODEN ER DEN ENESTE MED EN GLOBAL UNIQUUE ADDRESSE ANYWAY. SÅ "SUBNETS"OSV GIVER IKKE MENING
                              HUSK AT ASSIGN EN GLOBAL UNUIQUE ADDRESSE TIL ROOTEN

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
        self.dodag_id = dodag_id # 0
        self.env = env
        self.dodag_version_num = dodag_version_num # 0
        #self.MinHopRankIncrease = MinHopRankIncrease # 256.0
        self.last_dio = self.env.now # TODO skal være en timestamp. DET SKAL NOK VÆRE EN SIMPY TIME! IKKE "time" TIME env.now er en ting
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
        self.parents_list = []  # Parent set! (aka a list of parents(neighbors with rank greater than the nodes)) - elements will have the format (neighbor_node_id, neighbor_rank)  
        self.children_list = [] # Child set! (aka a list of children(neighbors with rank less than the nodes)) - elements will have the format (neighbor_node_id, neighbor_rank)
        self.downward_routes = {} # dict of downward routes. format: (destination, next_hop)

        # TODO der skal måske være noget herinde til at holde alt dodag info fra de andre nodes (info man får i DIO beskederne)(en liste)


    # def set_rank(self, rank):
    #     self.rank = rank
        
        
    # def set_prefered_parent(self, parent):
    #     ...
        
    # def DAGRank(self, rank):
    #     return math.floor(float(rank)/ self.MinHopRankIncrease) # Returns Interger part of rank. see sec 3.5.1 in RPL standard for more info

    # er ikker sikker på om vi skal bruge float rank eller DAGRank() (interger part) her







class Rpl_Instance:

    def __init__(self, rpl_instance_id):
        self.rpl_instance_id = rpl_instance_id
        self.dodag_list = []

    def add_dodag(self, dodag: Dodag):
        self.dodag_list.append(dodag)
