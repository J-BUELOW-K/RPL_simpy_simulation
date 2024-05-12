import simpy
import copy
import random

import networkx as nx
import matplotlib.pyplot as plt
import math
from dodag import Rpl_Instance, Dodag, generate_linklocal_ipv6_address
from control_messages import *
from OF0 import of0_compute_rank, of0_compare_parent, DAGRank
import defines
from networkx.drawing.nx_agraph import graphviz_layout

from rich.console import Console
from rich.table import Table
from rich.terminal_theme import MONOKAI

import network 

class Node:

    # MÅSKE ET TUPLE med Dodag object og tilhørende rank. eller skal rank være de del af dodag objetktet?
    
    # Liste med Rpl_Instances (inde i den er listen DODAGS)

    # TODO tilføj contrains liste

    # lav funktion et sted til at broadcast til alle connection (tager senderens node_id som input)
    # HUSK, man skal ikke kun yeild på put(), men også get() (e.g. yield store.put(f'spam {i}'))
    #    hmm... men i Process Communication example yielder de ikke på put. det kommer nok an på om man vil sidde stuck indtil den er sendt, eller bare komme videre idk
    # Problem. hvordan tingår en node andre nodes input queues. er det ikke kun noget netwærk objektet kan?? tænk over det

    def __init__(self, env, nw, node_id, xpos, ypos, alive = True):

        # Physical network values:
        self.network = nw
        self.env = env
        self.node_id = node_id
        self.alive = alive
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

        # DODAG discovery values:
        self.timeout_event = None
        self.timeout_process = None
        self.response_received = (False, None) # (True/False, dodag_reference) - used to determine if a secondary parent should be promoted to preferred parent
        
        # IPv6 address:
        self.ipv6_address = generate_linklocal_ipv6_address(node_id) # link local ipv6 address of the node (excluding \[prefix length])
        self.ipv6_address_prefix_len = defines.IPV6_ADDRESS_PREFIX_LEN # ipv6 address prefix length

    def kill_node(self):
        self.alive = False

    
    def revive_node(self):
        self.alive = True
    
    def determine_if_to_kill_or_revive(self):
        for rpl in self.rpl_instances:
            for dodag in rpl.dodag_list:
                if dodag.rank == defines.ROOT_RANK:
                    return "nothing" # dont kill the root node
        change = False
        if self.alive:
            if random.random() < defines.NODE_KILL_PROBABILITY:
                self.kill_node()
                change = True
        if not change and not self.alive:
            if random.random() < defines.NODE_REVIVE_PROBABILITY:
                self.revive_node()
                change = True
        
        # if change:
        #     for rpl in self.rpl_instances:
        #         for dodag_instance in rpl.dodag_list:
        #             if not self.alive:
                        
        #                     dodag_instance.prefered_parent = None
        #                     dodag_instance.prefered_parent_rank = defines.INFINITE_RANK
        #                     dodag_instance.rank = defines.INFINITE_RANK
                

        return "nothing"
        
        
        
    
    def add_to_neighbors_list(self, neighbor_object, connection_object): # add a single neighbor to the self.neighbors list
        self.neighbors.append((neighbor_object, connection_object, None)) # None is a placeholder for the ipv6 address. This will be updated when a DIO message is recieved
        pass

    def find_ipv6_address(self, node_id):
        for neighbor in self.neighbors:
            if neighbor[0].node_id == node_id:
                return neighbor[2]
        return None

    def increment_metric_object_from_neighbor(self, neighbors_metric_object, neighbors_node_id): # helper function used to increment a metric object recieved from a neighbor - to include path from neighbor to this node
        #print(f"debug: nabo objekt:{neighbors_metric_object}")
        if defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_NONE:
            return None
        elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_HOPCOUNT:
            neighbors_metric_object.cumulative_hop_count += 1
        elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_ETX:
            for neighbor in self.neighbors:
                if neighbor[0].node_id == neighbors_node_id:
                    neighbors_metric_object.cumulative_etx += neighbor[1].etx_value
        return neighbors_metric_object

      
    def unicast_packet(self, destination, packet): # Destination must be the receiving node_id
        # Unicast a message to a neighbor
        for neighbor in self.neighbors:
            if neighbor[0].node_id == destination:
                neighbor[0].input_msg_queue.put(packet)


    def unicast_dio(self, rpl_instance_id, dodag: Dodag, destination):
        icmp_dio = ICMP_DIO(rpl_instance_id, dodag.dodag_version_num, dodag.rank, dodag.dodag_id) # DIO message with icmp header
        if defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_HOPCOUNT:
            icmp_dio.add_HP_metric(dodag.metric_object.cumulative_hop_count) 
            pass
        elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_ETX:
            icmp_dio.add_ETX_metric(dodag.metric_object.cumulative_etx) 
            pass
        packet = Packet(self.node_id, icmp_dio)
        self.unicast_packet(destination, packet)


    def broadcast_packet(self, packet):
        # broadcast packet to all neighbors 
        for neighbor in self.neighbors:

            neighbor[0].input_msg_queue.put(packet)   # some simpy examples yield at put(), some dont 
    
    def broadcast_all_dios(self): # for all the dodags, broadcast dio messages
        for instance in self.rpl_instances:
            for dodag in instance.dodag_list:
                icmp_dio = ICMP_DIO(instance.rpl_instance_id, dodag.dodag_version_num, dodag.rank, 
                                    dodag.dodag_id, prefix=self.ipv6_address, prefix_len=self.ipv6_address_prefix_len) # DIO message with icmp header
                if defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_HOPCOUNT:
                    icmp_dio.add_HP_metric(dodag.metric_object.cumulative_hop_count) 
                    pass
                elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_ETX:
                    icmp_dio.add_ETX_metric(dodag.metric_object.cumulative_etx) 
                    pass
                packet = Packet(self.node_id, icmp_dio)
                self.broadcast_packet(packet)
        
    # def broadcast_packet_to_parents(self, packet, dodag: Dodag): # TODO VI SKAL KUN PREFERD PARENTS IKKE ALL PARENTS
    #     parents_ids = [parent[0] for parent in dodag.parents_list]  # parent[0] = node_id of parent
    #     for neighbor in self.neighbors:
    #         if neighbor.node_id in parents_ids:
    #             neighbor[0].input_msg_queue.put(packet)   

    def send_all_daos(self): # for all the dodags, send a dao message to the preferred parent
        for instance in self.rpl_instances:
            for dodag in instance.dodag_list:
                dodag.dao_sequence += 1  #increment dao_seqence (acording to the standard - see section 9.3 (point 1) in RFC 6550)
                icmp_dao = ICMP_DAO(instance.rpl_instance_id, dodag.dodag_id, dodag.dodag_version_num, dodag.dao_sequence)
                icmp_dao.add_target(self.ipv6_address, self.ipv6_address_prefix_len)   # add the node itself as a target in the DAO message
                for dest_ipv6_address in dodag.downward_routes.keys(): # add all the downward routes as targets in the DAO message
                    icmp_dao.add_target(dest_ipv6_address, defines.IPV6_ADDRESS_PREFIX_LEN)

                packet = Packet(self.node_id, icmp_dao)
                self.unicast_packet(dodag.prefered_parent, packet)


    def broadcast_dis(self):
        # broadcast a DIS message to all neighbors
        # DIS message is used to initiate the DODAG discovery process
        
        
        #first we notice the time of the DIS message
   
        
        
        icmp_dis = ICMP_DIS()
        packet = Packet(self.node_id, icmp_dis)
        self.broadcast_packet(packet)
        #self.start_timeout_timer() # start the timeout timer for the DIO response
        pass
    
    def unicast_dis(self):
        icmp_dis = ICMP_DIS()
        packet = Packet(self.node_id, icmp_dis)
        self.unicast_packet(self.rpl_instances[0].dodag_list[0].prefered_parent, packet)
        
    def start_timeout_timer(self):
        # start a timer for the DIO response
        
        self.timeout_process = self.env.process(self.timeout_handler())
        pass

    def reset_timeout_timer(self):
        if self.timeout_process and self.timeout_process.is_alive:
            self.timeout_process.interrupt('Reset by preferred parent')
        self.start_timeout_timer()
        
    def record_response(self, dodag_reference):
        self.response_received = (True, dodag_reference)
        
    def timeout_handler(self):
        try:
            yield self.env.timeout(defines.DIO_RESPONSE_WAIT_TIME)
        except simpy.Interrupt:
            pass
        else:
            if self.response_received[0]:
                self.promote_secondary_parent(self.response_received[1])
    
    def promote_secondary_parent(self, dodag_reference):
        dodag_reference.prefered_parent_rank = dodag_reference.secondary_rank
        dodag_reference.preferred_parent = dodag_reference.secondary_parent
        dodag_reference.metric_object = copy.deepcopy(dodag_reference.secondary_metric_object)
        
        dodag_reference.secondary_metric_object = None
        if defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_HOPCOUNT:
            dodag_reference.secondary_metric_object = HP_OBJ(0) # init hopcount to 0
        elif defines.METRIC_OBJECT_TYPE == defines.METRIC_OBJECT_ETX:
            dodag_reference.secondary_metric_object = ETX_OBJ(0) # init ETX to 0
        dodag_reference.secondary_parent = None
        dodag_reference.secondary_rank = defines.INFINITE_RANK
        
        dodag_reference.rank = of0_compute_rank(dodag_reference.prefered_parent_rank, dodag_reference.metric_object)
    
 ###################### TESTING FUNCTIONS ######################
    # The dio_handler function is responsible for handling DIO messages. It first finds or creates the DODAG, then updates the DODAG timestamp, prefix info, and preferred parent.
    def dio_handler(self, senders_node_id, dio_message: DIO, senders_metric_object = None, senders_prefix_info: Prefix_info = None):
        # Find or create the DODAG
        print(f"debug: {self.node_id}: recieved DIO from node {senders_node_id}")
        rpl_instance_idx, dodag_list_idx = self.find_or_create_dodag(dio_message)
        instance_reference = self.rpl_instances[rpl_instance_idx]
        dodag_reference = instance_reference.dodag_list[dodag_list_idx]
        if senders_node_id == dodag_reference.prefered_parent:
            print("debug: prefered parent")
            self.reset_timeout_timer()
        elif senders_node_id == dodag_reference.secondary_parent:
            print("debug: secondary parent")
            self.record_response(dodag_reference)
        
        # Update the DODAG timestamp
        self.update_dodag_timestamp(dodag_reference, senders_node_id)
        # Update the prefix info
        self.update_prefix_info(senders_node_id, senders_prefix_info)
        # Update the preferred parent
        self.update_preferred_parent(dodag_reference, senders_node_id, dio_message, senders_metric_object)

    # The find_or_create_dodag function finds the DODAG in the RPL instances or creates a new one if it doesn't exist.
    def find_or_create_dodag(self, dio_message):
        # Find the DODAG
        rpl_instance_idx, dodag_list_idx = network.find_dodag(self.rpl_instances, dio_message.rpl_instance_id, dio_message.dodag_id, dio_message.vers)
        if rpl_instance_idx is None:
            # If the DODAG doesn't exist, create a new RPL instance
            rpl_instance_idx, dodag_list_idx = self.create_rpl_instance(dio_message)
        elif dodag_list_idx is None:
            # If the DODAG doesn't exist, create a new DODAG
            dodag_list_idx = self.create_dodag(rpl_instance_idx, dio_message)
        return rpl_instance_idx, dodag_list_idx

    # The create_rpl_instance function creates a new RPL instance and adds it to the list of RPL instances.
    def create_rpl_instance(self, dio_message):
        # Create a new DODAG object
        dodag_object = Dodag(env=self.env, dodag_id=dio_message.dodag_id, dodag_version_num=dio_message.vers)
        # Create a new RPL instance object
        rpl_instance_obj = Rpl_Instance(dio_message.rpl_instance_id)
        rpl_instance_obj.add_dodag(dodag_object)
        # Add the RPL instance to the list of RPL instances
        self.rpl_instances.append(rpl_instance_obj)
        rpl_instance_idx = len(self.rpl_instances) - 1
        dodag_list_idx = len(rpl_instance_obj.dodag_list) - 1
        return rpl_instance_idx, dodag_list_idx

    # The create_dodag function creates a new DODAG and adds it to the list of DODAGs in the RPL instance.
    def create_dodag(self, rpl_instance_idx, dio_message):
        # Create a new DODAG object
        dodag_object = Dodag(env=self.env, dodag_id=dio_message.dodag_id, dodag_version_num=dio_message.version)
        # Add the DODAG to the list of DODAGs in the RPL instance
        self.rpl_instances[rpl_instance_idx].add_dodag(dodag_object)
        return len(self.rpl_instances[rpl_instance_idx].dodag_list) - 1

    # This function updates the timestamp of a DODAG (Destination Oriented Directed Acyclic Graph)
    def update_dodag_timestamp(self, dodag_reference, senders_node_id):
        # Update the last DIO (DODAG Information Object) timestamp to the current time
        dodag_reference.last_dio = self.env.now
        # Update the timestamp of the surrounding DODAGs
        dodag_reference.surrounding_dodags.update({senders_node_id: self.env.now})

    # This function updates the prefix information of a node
    def update_prefix_info(self, senders_node_id, senders_prefix_info):
        # Check if the sender's prefix info is not None
        if senders_prefix_info is not None:
            # Iterate over the neighbors
            for i, neighbor in enumerate(self.neighbors):
                # If the node ID of the neighbor matches the sender's node ID
                if neighbor[0].node_id == senders_node_id:
                    # Update the neighbor's information with the sender's prefix info
                    self.neighbors[i] = (neighbor[0], neighbor[1], senders_prefix_info.prefix)
                    break

    # This function updates the preferred parent of a node in a DODAG
    def update_preferred_parent(self, dodag_reference, senders_node_id, dio_message, senders_metric_object):
        # Check if the rank of the DODAG is not the root rank
        if dodag_reference.rank != defines.ROOT_RANK:
            # Create a copy of the sender's metric object
            senders_metric_object_copy = copy.deepcopy(senders_metric_object)
            # Calculate the metric object through the neighbor
            metric_object_through_neighbor = self.increment_metric_object_from_neighbor(senders_metric_object_copy, senders_node_id)
            # If the preferred parent of the DODAG is None
            if dodag_reference.prefered_parent is None:
                # Set the sender as the preferred parent
                self.set_preferred_parent(dodag_reference, senders_node_id, dio_message.rank, metric_object_through_neighbor)
            else:
                # Compare and update the parent of the DODAG
                self.compare_and_update_parent(dodag_reference, senders_node_id, dio_message.rank, metric_object_through_neighbor)

    # This function sets the preferred parent of a DODAG
    def set_preferred_parent(self, dodag_reference, parent_node_id, parent_rank, metric_object):
        # Set the preferred parent, its rank, and its metric object
        dodag_reference.prefered_parent = parent_node_id
        dodag_reference.prefered_parent_rank = parent_rank
        dodag_reference.metric_object = metric_object
        # Compute and set the rank of the DODAG
        dodag_reference.rank = of0_compute_rank(dodag_reference.prefered_parent_rank, dodag_reference.metric_object)

    # This function compares and updates the parent of a DODAG
    def compare_and_update_parent(self, dodag_reference, potential_parent_node_id, potential_parent_rank, metric_object):
        print("debug: compare_and_update_parent")
        # Compare the potential parent with the current preferred parent
        result, winner_rank = of0_compare_parent(dodag_reference.prefered_parent_rank, potential_parent_rank, dodag_reference.metric_object, metric_object)
        # If the result is to update the parent
        if result == "update parent":
            # Set the potential parent as the preferred parent
            self.set_secondary_parent(dodag_reference, dodag_reference.prefered_parent, dodag_reference.prefered_parent_rank, dodag_reference.metric_object)
            self.set_preferred_parent(dodag_reference, potential_parent_node_id, potential_parent_rank, metric_object)
        # If the result is nothing and the secondary parent is None
        elif result == "keep parent" and dodag_reference.secondary_parent is None:
            # Set the potential parent as the secondary parent
            self.set_secondary_parent(dodag_reference, potential_parent_node_id, potential_parent_rank, metric_object)
        # If the result is nothing
        elif result == "keep parent" and dodag_reference.secondary_parent is not None:
            # Compare and update the secondary parent
            self.compare_and_update_secondary_parent(dodag_reference, potential_parent_node_id, potential_parent_rank, metric_object)

    # This function sets the secondary parent of a DODAG
    def set_secondary_parent(self, dodag_reference, parent_node_id, parent_rank, metric_object):
        # Set the secondary parent, its rank, and its metric object
        if dodag_reference.prefered_parent != parent_node_id: 
            dodag_reference.secondary_parent = parent_node_id
            dodag_reference.secondary_rank = parent_rank
            dodag_reference.secondary_metric_object = metric_object
            # Compute and set the secondary rank of the DODAG
        dodag_reference.secondary_rank = of0_compute_rank(dodag_reference.secondary_rank, dodag_reference.secondary_metric_object)

    # This function compares and updates the secondary parent of a DODAG
    def compare_and_update_secondary_parent(self, dodag_reference, potential_parent_node_id, potential_parent_rank, metric_object):
        # Compare the potential parent with the current secondary parent
        result, winner_rank = of0_compare_parent(dodag_reference.secondary_rank, potential_parent_rank, dodag_reference.secondary_metric_object, metric_object)
        # If the result is to update the parent
        if result == "update parent":
            # Set the potential parent as the secondary parent
            self.set_secondary_parent(dodag_reference, potential_parent_node_id, potential_parent_rank, metric_object)



############################################################################################################





    def dio_handler1(self, senders_node_id, dio_message: DIO, senders_metric_object = None, senders_prefix_info: Prefix_info = None):

        # see section 8 in RPL standarden (RFC 6550) 

        ####################  Find RPL Instance and Dodag in the nodes self.rpl_instaces list - If no entries, we create them ####################
        print(f"debug: {self.node_id}: recieved DIO from node {senders_node_id}")
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
        
        if senders_node_id == dodag_reference.prefered_parent:
            print("debug: prefered parent")
            self.reset_timeout_timer()
        elif senders_node_id == dodag_reference.secondary_parent:
            print("debug: secondary parent")
            self.record_response(dodag_reference)
        

        ####################  Extract and save IPV6 address from senders_prefix_info #################### 
        if senders_prefix_info is not None:
            for i, neighbor in enumerate(self.neighbors):
                if neighbor[0].node_id == senders_node_id:
                    self.neighbors[i] = (neighbor[0], neighbor[1], senders_prefix_info.prefix) # update prefix info
                    break

        ####################  CHECK IF SENDER IS A BETTER PREFERRED PARENT THAN THE CURRENT PREFERRED PARRENT - UPDATE STUFF IF IT IS ####################
        # TODO Clean this the fuck up
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
                if result == "nothing":
                    if dodag_reference.secondary_parent is None:
                        dodag_reference.secondary_parent = senders_node_id
                        dodag_reference.secondary_parent_rank = dio_message.rank
                        dodag_reference.secondary_metric_object = metric_object_through_neighbor
                        dodag_reference.secondary_rank = of0_compute_rank(dodag_reference.secondary_parent_rank, dodag_reference.secondary_metric_object)
                    else:
                        result, winner_rank = of0_compare_parent(dodag_reference.secondary_parent_rank, dio_message.rank,
                                                        dodag_reference.secondary_metric_object, metric_object_through_neighbor)
                        if result =="update parent":
                            dodag_reference.secondary_parent = senders_node_id
                            dodag_reference.secondary_parent_rank = dio_message.rank
                            dodag_reference.secondary_metric_object = metric_object_through_neighbor
                            dodag_reference.secondary_rank = winner_rank

        # ####################  EVALUATE PARENT SET  ####################

        # # add neighbor to parent list if not already there (if the neighbor is not a parent, it will be removed afterwards):
        # already_in_parents_list = False
        # for parent in dodag_reference.parents_list:
        #     if parent[0] == senders_node_id:
        #         # we already have an entry for this parent in the parent list
        #         parent = (senders_node_id, dio_message.rank) # update rank
        #         already_in_parents_list = True
        #         break
        # if not already_in_parents_list: # if we dont already have an entry for this parent in the parent list
        #     dodag_reference.parents_list.append((senders_node_id, dio_message.rank))

        # # remove alle non-parents from the parent list :
        # dodag_reference.parents_list = [parent for parent in dodag_reference.parents_list if parent[1] < dodag_reference.rank] # parent[1] = parent rank


        # ####################  EVALUATE CHILD SET ####################'

        # already_in_children_list = False
        # for child in dodag_reference.children_list:
        #     if child[0] == senders_node_id:
        #         # we already have an entry for this child in the child list
        #         child = (senders_node_id, dio_message.rank) # update rank
        #         already_in_children_list = True
        #         break
        # if not already_in_children_list: # if we dont already have an entry for this child in the child list
        #     dodag_reference.children_list.append((senders_node_id, dio_message.rank))

        # # remove alle non-children from the child set:
        # dodag_reference.children_list = [child for child in dodag_reference.children_list if child[1] > dodag_reference.rank]





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
        print("Debug: DIS packet received by node ", self.node_id, "from node ", senders_node_id)
        
        for instance in self.rpl_instances:
            print(f"debug: instance: {instance.rpl_instance_id}")
            for dodag in instance.dodag_list:
                print(f"debug: dodag: {dodag.dodag_id}")
                self.unicast_dio(instance.rpl_instance_id, dodag, senders_node_id)


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
                    print(f"debug: {self.node_id}: RPL tricle timer")
                    if self.alive:
                        self.broadcast_all_dios()
                        self.send_all_daos() # send DAOs to preferred parent  

                        
    
    def recieve_process(self, env):
        while(True):
            message  = yield (self.input_msg_queue.get())
            
            #self.determine_if_to_kill_or_revive() # simulate node death/revival
            if self.alive:
                self.packet_handler(message)
                self.silent_mode = False


    def repair_process(self, env):  # Simpy process
        while(True):

                yield(env.timeout(defines.DIS_TRANSMIT_TIMER + random.randint(-defines.DIS_TRANSMIT_TIMER_JITTER, defines.DIS_TRANSMIT_TIMER_JITTER), value = "DIS_timer"))
                if not self.silent_mode:

                    print(f"debug: {self.node_id}: DIS timer")
                    #self.determine_if_to_kill_or_revive()
                    if self.alive:
                        self.broadcast_dis()
                        #self.unicast_dis()