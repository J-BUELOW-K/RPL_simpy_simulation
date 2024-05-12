import copy
import random

import simpy
from rich.terminal_theme import MONOKAI

import defines
from control_messages import *
from dodag import Dodag, Rpl_Instance, generate_linklocal_ipv6_address
import network
from OF0 import of0_compare_parent, of0_compute_rank


class Node:
    """
    A node in the network. 
    The node has a list of neighbors, a list of RPLInstances, and an input message queue.
    The node can send and recieve messages to/from its neighbors.
    The node can also send and recieve RPL control messages (DIO, DAO, DIS) to/from its neighbors.
    """
    
    def __init__(self, env, nw, node_id, xpos, ypos, alive = True):
        """ Constructor for the Node class 

        Args:
            env (object): simpy environment object
            nw (object): network object
            node_id (int): unique id of the node
            xpos (float): x position of the node in the network
            ypos (float):  y position of the node in the network
            alive (bool, optional): If the node is alive or not. Defaults to True.
        """

        # Physical network values:
        self.network = nw # network object
        self.env = env # simpy environment object
        self.node_id = node_id # unique id of the node
        self.alive = alive # if the node is alive or not
        self.xpos = xpos  # used to estimate ETX
        self.ypos = ypos  # used to estimate ETX
        self.neighbors = [] # Each element is a tuple: (node object, connection object, link local ipv6 address).   
                            # List of all neighboring nodes and associated connection objects (aka other nodes which this node has a connection/edge to) 
                            # This list has nothing to do with any RPLInstance or DODAG, its simply information about the physical network.
                            # Note on the ipv6 address: Yes, this information can be extracted directly from the node object within the neighbors array... 
                            #                           HOWEVER, this would not be the case in the real world, and we therefore instead keep the ipv6 address as a separate 
                            #                           element in the tuple and extract the address information through the "prefix info" object in the DIO message, for the sake of "realism".

        # RPL values:
        self.rpl_instances = [] # list of RPLIncances that the node is a part of (contains all dodags)
        self.input_msg_queue = simpy.Store(self.env, capacity=simpy.core.Infinity)
        self.silent_mode = True  # node will stay silent untill it has recieved a DIO message from a neighbor (see section 18.2.1.1 in RPL standard)

        # IPv6 address:
        self.ipv6_address = generate_linklocal_ipv6_address(node_id) # link local ipv6 address of the node (excluding \[prefix length])
        self.ipv6_address_prefix_len = defines.IPV6_ADDRESS_PREFIX_LEN # ipv6 address prefix length

    def add_to_neighbors_list(self, neighbor_object, connection_object): # add a single neighbor to the self.neighbors list
        self.neighbors.append((neighbor_object, connection_object, None)) # None is a placeholder for the ipv6 address. This will be updated when a DIO message is recieved
        

    def find_ipv6_address(self, node_id): # find the ipv6 address of a neighbor node
        for neighbor in self.neighbors: # go through all neighbors
            if neighbor[0].node_id == node_id: # if the node_id of the neighbor matches the input node_id
                return neighbor[2] # return the ipv6 address of the neighbor
        return None

    def increment_metric_object_from_neighbor(self, neighbors_metric_object, neighbors_node_id): # helper function used to increment a metric object recieved from a neighbor - to include path from neighbor to this node
        if defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_NONE: # if no metric object type is set
            return None # return None
        elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_HOPCOUNT: # if the metric object type is hopcount
            neighbors_metric_object.cumulative_hop_count += 1 # increment hop count
        elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_ETX: # if the metric object type is ETX
            for neighbor in self.neighbors: # go through all neighbors
                if neighbor[0].node_id == neighbors_node_id: # if the node_id of the neighbor matches the input node_id
                    neighbors_metric_object.cumulative_etx += neighbor[1].etx_value # increment ETX
        return neighbors_metric_object # return the updated metric object

      
    def unicast_packet(self, destination, packet): # Destination must be the receiving node_id
        # Unicast a message to a neighbor
        for neighbor in self.neighbors: # go through all neighbors
            if neighbor[0].node_id == destination: # if the node_id of the neighbor matches the input node_id
                neighbor[0].input_msg_queue.put(packet) # put the packet in the neighbors input message queue


    def unicast_dio(self, rpl_instance_id, dodag: Dodag, destination): # unicast a DIO message to a neighbor
        icmp_dio = ICMP_DIO(rpl_instance_id, dodag.dodag_version_num, dodag.rank, dodag.dodag_id) # DIO message with icmp header
        if defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_HOPCOUNT: # add metric object to the DIO message
            icmp_dio.add_HP_metric(dodag.metric_object.cumulative_hop_count)  # add hop count metric
            
        elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_ETX: # add metric object to the DIO message
            icmp_dio.add_ETX_metric(dodag.metric_object.cumulative_etx)  # add ETX metric
            
        packet = Packet(self.node_id, icmp_dio) # create packet
        self.unicast_packet(destination, packet) # unicast packet to destination


    def broadcast_packet(self, packet): 
        # broadcast packet to all neighbors 
        for neighbor in self.neighbors:
            neighbor[0].input_msg_queue.put(packet)   # some simpy examples yield at put(), some dont 
    
    def broadcast_all_dios(self): # for all the dodags, broadcast dio messages
        for instance in self.rpl_instances: # go through all RPL instances
            for dodag in instance.dodag_list: # go through all dodags in the RPL instance
                icmp_dio = ICMP_DIO(instance.rpl_instance_id, dodag.dodag_version_num, dodag.rank,  # create DIO message
                                    dodag.dodag_id, prefix=self.ipv6_address, prefix_len=self.ipv6_address_prefix_len) # DIO message with icmp header
                if defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_HOPCOUNT: # add metric object to the DIO message
                    icmp_dio.add_HP_metric(dodag.metric_object.cumulative_hop_count)  # add hop count metric
                    
                elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_ETX: # add metric object to the DIO message
                    icmp_dio.add_ETX_metric(dodag.metric_object.cumulative_etx)  # add ETX metric
                    
                packet = Packet(self.node_id, icmp_dio) # create packet
                self.broadcast_packet(packet) # broadcast packet
        

    def send_all_daos(self): # for all the dodags, send a dao message to the preferred parent
        for instance in self.rpl_instances: # go through all RPL instances
            for dodag in instance.dodag_list: # go through all dodags in the RPL instance
                dodag.dao_sequence += 1  #increment dao_seqence (acording to the standard - see section 9.3 (point 1) in RFC 6550)
                icmp_dao = ICMP_DAO(instance.rpl_instance_id, dodag.dodag_id, dodag.dodag_version_num, dodag.dao_sequence) # create DAO message
                icmp_dao.add_target(self.ipv6_address, self.ipv6_address_prefix_len)   # add the node itself as a target in the DAO message
                for dest_ipv6_address in dodag.downward_routes.keys(): # add all the downward routes as targets in the DAO message
                    icmp_dao.add_target(dest_ipv6_address, defines.IPV6_ADDRESS_PREFIX_LEN) # add target

                packet = Packet(self.node_id, icmp_dao) # create packet
                self.unicast_packet(dodag.prefered_parent, packet) # unicast packet to the prefered parent


    def broadcast_dis(self): # broadcast a DIS message
        icmp_dis = ICMP_DIS() # create DIS message
        packet = Packet(self.node_id, icmp_dis) # create packet
        self.broadcast_packet(packet) # broadcast packet
        
    

    def dio_handler(self, senders_node_id, dio_message: DIO, senders_metric_object = None, senders_prefix_info: Prefix_info = None):
        # see section 8 in RPL standarden (RFC 6550) 

        ####################  Find RPL Instance and Dodag in the nodes self.rpl_instaces list - If no entries, we create them ####################
        rpl_instance_idx, dodag_list_idx = network.find_dodag(self.rpl_instances, dio_message.rpl_instance_id, \
                                                      dio_message.dodag_id, dio_message.vers)
        if rpl_instance_idx is None:
            # No entry in self.rpl_instaces for recieved RPL instance! Create one!
            dodag_object = Dodag(env=self.env, dodag_id=dio_message.dodag_id, dodag_version_num=dio_message.vers)
            rpl_instance_obj = Rpl_Instance(dio_message.rpl_instance_id)
            rpl_instance_obj.add_dodag(dodag_object)
            self.rpl_instances.append(rpl_instance_obj)
            rpl_instance_idx = len(self.rpl_instances) - 1 # there might already be entries for other instances in the self.rpl_instaces list
            dodag_list_idx = len(rpl_instance_obj.dodag_list) - 1  # value is always just 0
        else:
            # There exists an entry for the recieved RPL instance in self.rpl_instances!
            if dodag_list_idx is None:
                # No existing DODAG entry in the RPL Instance! Create one!
                dodag_object = Dodag(env=self.env, dodag_id=dio_message.dodag_id, dodag_version_num=dio_message.version)
                self.rpl_instances[rpl_instance_idx].add_dodag(dodag_object)
                dodag_list_idx = len(self.rpl_instances[rpl_instance_idx].dodag_list) - 1 # value is always just 0

        intance_reference = self.rpl_instances[rpl_instance_idx]
        dodag_reference = intance_reference.dodag_list[dodag_list_idx]
        

        ####################  Update timestamp for the recieved dodag  ####################  
        dodag_reference.last_dio = self.env.now # update timestamp for the recieved dodag (used in OF0)
        dodag_reference.surrounding_dodags.update({senders_node_id: self.env.now}) # update timestamp for the recieved dodag
        

        ####################  Extract and save IPV6 address from senders_prefix_info #################### 
        if senders_prefix_info is not None:
            for i, neighbor in enumerate(self.neighbors):
                if neighbor[0].node_id == senders_node_id:
                    self.neighbors[i] = (neighbor[0], neighbor[1], senders_prefix_info.prefix) # update prefix info
                    break

        ####################  CHECK IF SENDER IS A BETTER PREFERRED PARENT THAN THE CURRENT PREFERRED PARRENT - UPDATE STUFF IF IT IS ####################

        if dodag_reference.rank != defines.ROOT_RANK: # (only non-root nodes needs a parent)
            senders_metric_object_copy = copy.deepcopy(senders_metric_object) # create copy to not alter the original.
            metric_object_through_neighbor = self.increment_metric_object_from_neighbor(senders_metric_object_copy, senders_node_id) 

            if dodag_reference.prefered_parent is None: # Our node does not have a prefered parent - we simply accept the DIO sender as prefered parent
                dodag_reference.prefered_parent = senders_node_id
                dodag_reference.prefered_parent_rank = dio_message.rank
                dodag_reference.metric_object = metric_object_through_neighbor # update metric object
                dodag_reference.rank = of0_compute_rank(dodag_reference.prefered_parent_rank, dodag_reference.metric_object)  # update rank
            else:
                # test if sender is a better prefered parrent than current prefered parrent:
                #if of0_compare_parent(asdasd) == 1: # if sender is better parent
                result, winner_rank = of0_compare_parent(dodag_reference.prefered_parent_rank, dio_message.rank,
                                                        dodag_reference.metric_object, metric_object_through_neighbor)
                if result =="update parent":
                    # we found a better preferred parent!
                    dodag_reference.prefered_parent = senders_node_id
                    dodag_reference.prefered_parent_rank = dio_message.rank
                    dodag_reference.metric_object = metric_object_through_neighbor # update metric object
                    dodag_reference.rank = winner_rank # we can just use the rank computed from of0_compare_parent - we dont have to compute it again
            

        # 8.1.  DIO Base Rules

        #    1.  For the following DIO Base fields, a node that is not a DODAG
        #        root MUST advertise the same values as its preferred DODAG parent
        #        (defined in Section 8.2.1).  In this way, these values will
        #        propagate Down the DODAG unchanged and advertised by every node
        #        that has a route to that DODAG root.  These fields are as
        #        follows:
        #        1.  Grounded (G)
        #        2.  Mode of Operation (MOP)
        #        3.  DAGPreference (Prf)
        #        4.  Version
        #        5.  RPLInstanceID
        #        6.  DODAGID

        #    2.  A node MAY update the following fields at each hop:
        #        1.  Rank - DEN HER SKAL UPDATES TROR JEG
        #        2.  DTSN -  BRUGT TIL DOWN ROUTES (dao stuff)

        #    3.  The DODAGID field each root sets MUST be unique within the RPL
        #        Instance and MUST be a routable IPv6 address belonging to the
        #        root.

        #  AKA DODAG ID SKAL VÆRE EN IPv5 ADRESSESE (belonging to the root)

        #     RPL's Upward route discovery algorithms and processing are in terms
        #    of three logical sets of link-local nodes.  First, the candidate
        #    neighbor set is a subset of the nodes that can be reached via link-
        #    local multicast.  The selection of this set is implementation and OF
        #    dependent.  Second, the parent set is a restricted subset of the
        #    candidate neighbor set.  Finally, the preferred parent is a member of
        #    the parent set that is the preferred next hop in Upward routes.
        #    Conceptually, the preferred parent is a single parent; although, it
        #    may be a set of multiple parents if those parents are equally
        #    preferred and have identical Rank.

    def dao_handler(self, senders_node_id, dao_message: DAO, senders_targets: list[RPL_target]):
        # A dao was received from a child node.
        # Aka, this node is the preferred parent of the sender of the dao message (we only send dao messages to preferred parents)
        # Therefore, add the sender to the downward routes of the dodag (if not already there)

        # note: According to the standard, a node SHOULD send DAOs to ALL its parents. It not only includes RPL Target objects but also "Transit Information,"
        #       which, in its "path control," allows for multiple downward routes to a node. HOWEVER, to simplify implementation, we do not implement 
        #       "Transit Information," and we only send to the Preferred parent, resulting in only one route down to a node
        #       (meaning only downward data flows through the edges we see in the Dodag plot).


        ####################  MAKE SURE DAO IS ASSOCIATED WITH A VALID DODAG  ####################

        rpl_instance_idx, dodag_list_idx = network.find_dodag(self.rpl_instances, dao_message.rpl_instance_id, dao_message.dodag_id, dao_message.dodag_version)

        if rpl_instance_idx is None or dodag_list_idx is None:
            return # invalid DAO message - ignore it
        dodag_reference = self.rpl_instances[rpl_instance_idx].dodag_list[dodag_list_idx]

        ####################  MAKE SURE DAO IS NOT OUTDATED  - IF THERE ARE NO CURRENT ENTRY FOR ITS PREVOIUS SEQ NUMBER, CREATE ONE ####################

        child_already_in_dao_seq_list = False
        for child in dodag_reference.children_dao_seq_list:
            if child[0] == senders_node_id:
                # we already have an entry for this child in the children_dao_seq_list
                if dao_message.dao_sequence <= child[1]:
                    return # message is outdated - ignore it
                child = (senders_node_id, dao_message.dao_sequence) # update seq number
                child_already_in_dao_seq_list = True
                break
        if not child_already_in_dao_seq_list: # if we dont already have an entry for this child in the children_dao_seq_list
            dodag_reference.children_dao_seq_list.append((senders_node_id, dao_message.dao_sequence))

        #################### GET IPV6 ADDRESS OF SENDER ####################

        senders_ipv6_address = self.find_ipv6_address(senders_node_id)
        if senders_ipv6_address is None:
            return # invalid DAO message (we have not yet received its ivp6 address from a DIO message) - ignore it

        #################### UPDATE DOWNWARD ROUTES  ####################

        
        for target in senders_targets: # go through all the targets in the DAO message
            dodag_reference.downward_routes[target.target_prefix] = senders_ipv6_address  # this will update the route if it already exists, or create a new one if it does not


     

    def dis_handler(self, senders_node_id):
        # print("Debug: DIS packet received by node ", self.node_id, "from node ", senders_node_id)
        for instance in self.rpl_instances:
            for dodag in instance.dodag_list:
                self.unicast_dio(self, self.rpl_instances.rpl_instance_id, dodag, senders_node_id)


    def packet_handler(self, packet: Packet):
        # Read ICMP Header:
        #print(f"yesdu: {packet}")
        icmp_header = packet.payload.icmp
        if icmp_header.type != defines.TYPE_RPL_CONTOL_MSG:
            # invalid packet - ignore it
            return
        if icmp_header.code == defines.CODE_DIO:
            self.dio_handler(packet.src_node_id, packet.payload.dio, packet.payload.metric_option, packet.payload.prefix_option)
        elif icmp_header.code == defines.CODE_DAO:
            self.dao_handler(packet.src_node_id, packet.payload.dao, packet.payload.targets)
        elif icmp_header.code == defines.CODE_DIS:
            self.dis_handler(packet.src_node_id)
        else:
            # Unknown ICMP code - ignore it
            return


    def rpl_process(self, env):  # Simpy process
        while(True):
            #print(f"hehe: {self.node_id}")
                yield (env.timeout(defines.NODE_TRANSMIT_TIMER + random.randint(-defines.NODE_TRANSMIT_TIMER_JITTER, defines.NODE_TRANSMIT_TIMER_JITTER), value = "RPL_tricle_timer") )
                if not self.silent_mode: # if silent_mode = False
                                    
                        # event was a timeout event. (https://stackoverflow.com/questions/21930498/how-to-get-the-first-value-in-a-python-dictionary)
                        # note: acording to the standard, a node sends a DAO if i recieves a DAO (after DAO_DELAY) or if it has updates to its downward routes. 
                        #       however, for simplicity, we simply send a DAO using a periodic timer (just like we do for DIOs)
                    #self.determine_if_to_kill_or_revive() # simulate node death/revival
                    #print(f"debug: {self.node_id}: RPL tricle timer")
                    if self.alive:
                        self.broadcast_all_dios()
                        self.send_all_daos() # send DAOs to preferred parent  

                        
    
    def recieve_process(self, env):  # Simpy process
        while(True):
            message  = yield (self.input_msg_queue.get())
            #self.determine_if_to_kill_or_revive() # simulate node death/revival
            if self.alive:
                self.packet_handler(message)
                self.silent_mode = False