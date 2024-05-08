import simpy
import copy
import random

import networkx as nx
import matplotlib.pyplot as plt
import math
from dodag import Rpl_Instance, Dodag, generate_linklocal_ipv6_address
from control_messages import *
from OF0 import of0_compute_rank, of0_compare_parent, DAGRank
from defines import *
from networkx.drawing.nx_agraph import graphviz_layout


SPEED_OF_LIGHT = 299792458
LINK_FREQ = 2.4 * pow(10, 9)  # Hz

MAX_ETX = 0xFFFF
MAX_DISTANCE = 0xFFFF

def estimate_etx(distance: float, model: str) -> float:
    # ETX calc is not specific, however is it usually calculated as: ETX = 1 / (Df*Dr) 
                                        # where Df is the measured probability that a packet is received by the neighbor and Dr is 
                                        # the measured probability that the acknowledgment packet is successfully received.
                                        # https://datatracker.ietf.org/doc/html/rfc6551#page-21)
                                        # In practice, Df and Dr is estimated using beacon messages (hard to do in a sim): https://hal.science/hal-01165655/document
    # HOWEVER, as we just use the ETX to compare against other ETX values, it only needs to be relative to itself.
    # Note: this also means tht we CANT think of our specific ETX value as "expected transmission count"
    # Note: if we acutally wanted to compare the performance of DODAGS created with different metrics (e.g. hop distance vs etx),
    #       then this etx value would have to actually match "expected transmission count" and should be linked to path loss when sending messages between nodes.
    #       However, such performence tests is beyond the scope of this simulation. We want to simulate DODAG contruction.

    if model == "linear":
        return distance # distance is already linear
    elif model == "fspl":
        fspl = pow((4*math.pi*distance*LINK_FREQ) / SPEED_OF_LIGHT, 2)  # https://en.wikipedia.org/wiki/Free-space_path_loss
        return fspl
    
# def increase_metric_value(metric_object, metric_object_type):
#     if metric_object_type == None:
#         return None
#     elif metric_object_type == "HP":
#         metric_object.cumulative_hop_count += 1
    
def find_dodag(rpl_instances: list, rpl_instance_id, dodag_id, dodag_version): # return index of dodag and/or rpl instance in list of rpl instances

    rpl_instance_idx = None
    dodag_list_idx = None

    # Find associated RPL Instance:
    for i in range(len(rpl_instances)):
        if rpl_instances[i].rpl_instance_id == rpl_instance_id:
            #print("debug: matching RPL Instance entry found!")
            rpl_instance_idx = i
            break

    if rpl_instance_idx is not None: # If there exists an entry for the recieved RPL instance in self.rpl_instances!
        # Find associated Dodag:
        for i in range(len(rpl_instances[rpl_instance_idx].dodag_list)):
            temp_dodag = rpl_instances[rpl_instance_idx].dodag_list[i]
            if temp_dodag.dodag_id == dodag_id and temp_dodag.dodag_version_num == dodag_version: # Both ID and Version has to match!
                #print("debug: matching dodag entry found!")
                dodag_list_idx = i
                break

    return rpl_instance_idx, dodag_list_idx


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
            if random.random() < NODE_KILL_PROBABILITY:
                self.kill_node()
                change = True
        if not change and not self.alive:
            if random.random() < NODE_REVIVE_PROBABILITY:
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
        if METRIC_OBJECT_TYPE == METRIC_OBJECT_NONE:
            return None
        elif METRIC_OBJECT_TYPE == METRIC_OBJECT_HOPCOUNT:
            neighbors_metric_object.cumulative_hop_count += 1
        elif METRIC_OBJECT_TYPE == METRIC_OBJECT_ETX:
            for neighbor in self.neighbors:
                if neighbor[0].node_id == neighbors_node_id:
                    neighbors_metric_object.cumulative_etx += neighbor[1].etx_value
        return neighbors_metric_object
                    
    def unicast_packet(self, destination, packet): # Destination must be the receiving node_id
        # Unicast a message to a neighbor
        for neighbor in self.neighbors:
            if neighbor[0].node_id == destination:
                neighbor[0].input_msg_queue.put(packet)

    def broadcast_packet(self, packet):
        # broadcast packet to all neighbors 
        for neighbor in self.neighbors:
            neighbor[0].input_msg_queue.put(packet)   # some simpy examples yield at put(), some dont 
    
    def broadcast_all_dios(self): # for all the dodags, broadcast dio messages
        for instance in self.rpl_instances:
            for dodag in instance.dodag_list:
                icmp_dio = ICMP_DIO(instance.rpl_instance_id, dodag.dodag_version_num, dodag.rank, 
                                    dodag.dodag_id, prefix=self.ipv6_address, prefix_len=self.ipv6_address_prefix_len) # DIO message with icmp header
                if METRIC_OBJECT_TYPE == METRIC_OBJECT_HOPCOUNT:
                    icmp_dio.add_HP_metric(dodag.metric_object.cumulative_hop_count) 
                    pass
                elif METRIC_OBJECT_TYPE == METRIC_OBJECT_ETX:
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

    
    def dio_handler(self, senders_node_id, dio_message: DIO, senders_metric_object = None, senders_prefix_info: Prefix_info = None):
        # see section 8 in RPL standarden (RFC 6550) 

        ####################  Find RPL Instance and Dodag in the nodes self.rpl_instaces list - If no entries, we create them ####################
        rpl_instance_idx, dodag_list_idx = find_dodag(self.rpl_instances, dio_message.rpl_instance_id, \
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

        rpl_instance_idx, dodag_list_idx = find_dodag(self.rpl_instances, dao_message.rpl_instance_id, dao_message.dodag_id, dao_message.dodag_version)

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


     

    def packet_handler(self, packet: Packet):
        # Read ICMP Header:
        #print(f"yesdu: {packet}")
        icmp_header = packet.payload.icmp
        if icmp_header.type != TYPE_RPL_CONTOL_MSG:
            # invalid packet - ignore it
            return
        if icmp_header.code == defines.CODE_DIO:
            self.dio_handler(packet.src_node_id, packet.payload.dio, packet.payload.metric_option, packet.payload.prefix_option)
            pass # TODO
        elif icmp_header.code == defines.CODE_DAO:
            self.dao_handler(packet.src_node_id, packet.payload.dao, packet.payload.targets)
            pass 
        elif icmp_header.code == defines.CODE_DIS:
            pass # TODO


    def run(self, env):  # Simpy process
        while(True):
            #print(f"hehe: {self.node_id}")
            if self.silent_mode == True:
                message = yield self.input_msg_queue.get()
                self.silent_mode = False
                self.packet_handler(message)
            else: # if silent_mode = False
                event = yield self.input_msg_queue.get() | env.timeout(NODE_TRANSMIT_TIMER + random.randint(-NODE_TRANSMIT_TIMER_JITTER, NODE_TRANSMIT_TIMER_JITTER), value = "timeooout")  # Periodic timer is replacement for tricle timer
                if (next(iter(event.values())) == "timeooout"): # event was a timeout event. (https://stackoverflow.com/questions/21930498/how-to-get-the-first-value-in-a-python-dictionary)
                    # note: acording to the standard, a node sends a DAO if i recieves a DAO (after DAO_DELAY) or if it has updates to its downward routes. 
                    #       however, for simplicity, we simpy send a DAO using a periodic timer (just like we do for DIOs)
                    self.determine_if_to_kill_or_revive() # simulate node death/revival
                    if self.alive:
                        self.broadcast_all_dios()
                        self.send_all_daos() # send DAOs to preferred parent  
                    pass
                else: # event was a "message in input_msg_queue" event
                    # TODO HVIS DET DER IF ELSE HALLØJ MED event.values() GIVER FEJL, SÅ PRØV TRY EXECPT
                    # print("debug: Node:: packet recieved!") TODO fjerne udkommenteringen
                    self.determine_if_to_kill_or_revive() # simulate node death/revival
                    if self.alive:
                        self.packet_handler(next(iter(event.values())))
                    pass
            

class Connection:
    def __init__(self, from_node, to_node, etx_value = MAX_ETX, distance = MAX_DISTANCE):
        self.from_node = from_node
        self.to_node = to_node
        self.etx_value = etx_value
        self.distance = distance

class Network:
    # https://networkx.org/documentation/stable/auto_examples/drawing/plot_random_geometric_graph.html 

    def __init__(self, env):
        self.env = env
        self.nodes = []
        self.connections = [] # this line is not strickly needed (is here for completeness)
        pass

    def generate_nodes_and_edges(self, number_of_nodes: int, radius: float, seed = None):

        # Generate geometric network (nodes are places at random, edges are drawn if within radius):
        while(True):
            self.networkx_graph = nx.random_geometric_graph(number_of_nodes, radius, seed=seed)  # TODO: DET KAN VÆRE VI SKAL LAVE VORES EGEN AF DEN HER. FRA OPGAVEBESKRIVELSEN: Implement and simulate a neighbor discovery mechanism that ensures that each nodeestablish connectivity with its nearest neighbors. MEN VI BESTEMMER SELV! VI LADER DEN BARE STÅ
            if nx.is_connected(self.networkx_graph): 
                break #if graph is not connected, try again...

        # tranlate networkx nodes/edges to our own nodes/connections setup (to make them easier to work with):
        self.connections = [Connection(x[0],x[1]) for x in self.networkx_graph.edges()]
        # self.nodes = [Node(node_id = x) for x in self.networkx_graph.nodes()] # does not include position
        for node in self.networkx_graph.nodes(data="pos"):
            self.nodes.append(Node(self.env, self, node_id = node[0], xpos = node[1][0], ypos = node[1][1]))  # node format from networkx: (id, [xpos, ypos])
                                                                                              # note: node_id matches index in self.nodes array!
            #print(f"xpos: {node[1][0]}, ypos: {node[1][1]}")

        # Estimate relative ETX values for each connection:
        for connection in self.connections:
            a = self.nodes[connection.from_node].xpos  # assumption: index in self.nodes array matches node_id
            b = self.nodes[connection.to_node].ypos    # assumption: index in self.nodes array matches node_id
            connection.distance = math.sqrt(a**2 + b**2) # pythagoras
            connection.etx_value = estimate_etx(connection.distance, "fspl")
            #print(f"distance:{connection.distance}  etx:{connection.etx_value}")

        # Make all nodes aware of their neighbors:
        for connection in self.connections:
            # note: At network cration, connection/edges are NOT generated in both directions between nodes. Therefore, we inform both nodes in a connection about the neighboring node
            self.nodes[connection.from_node].add_to_neighbors_list(self.nodes[connection.to_node], connection)  # assumption: index in self.nodes array matches node_id
            self.nodes[connection.to_node].add_to_neighbors_list(self.nodes[connection.from_node], connection)  # assumption: index in self.nodes array matches node_id

        # return max node_id:
        return number_of_nodes - 1
    
    def construct_new_dodag(self, rpl_instance_id, dodag_id, dodag_version, desired_root_node_id = None):

        # Pick Root Node:
        if desired_root_node_id == None:
            # pick root "by random" (we arbitrarily choose index 0, the indexes themselves are "randomly given" to nodes):
            root_node = self.nodes[0]
            pass
        else:
            # use the specified node as root
            root_node = self.nodes[desired_root_node_id] # assumption: index in self.nodes array matches node_id
        
        # Check if specified RPL instance/dodag already exists in root node:
        rpl_instance_idx, dodag_list_idx = find_dodag(root_node.rpl_instances, rpl_instance_id, dodag_id, dodag_version)
        if rpl_instance_idx != None:
            # RPL instance entry found in root node
            if dodag_list_idx != dodag_list_idx:
                print("ERROR: Identical DODAG entry already exists...")
                raise ValueError 
            else:
                # Create DODAG in root node, within the already existing RPL Instance
                new_dodag = Dodag(env = self.env, dodag_id= dodag_id, dodag_version_num= dodag_version, rank=ROOT_RANK) # setting rank to 0 makes the node the root!
                root_node.rpl_instances[rpl_instance_idx].add_dodag(new_dodag)
        else:
            # No matching RPL entry exists in root node - create one! (including dodag):
            new_rpl_instance = Rpl_Instance(rpl_instance_id)
            new_dodag = Dodag(env=self.env, dodag_id=dodag_id, dodag_version_num=dodag_version, rank = ROOT_RANK) # setting rank to 0 makes the node the root!
            new_rpl_instance.add_dodag(new_dodag)
            root_node.rpl_instances.append(new_rpl_instance)

        # initialize dodag formation:
        root_node.broadcast_all_dios()

        return root_node.node_id

 





        # for node in self.nodes:
        #     node.debug_print_neighbors()

        # for connection in self.connections:
        #     print(f"connection from:{connection.from_node} to:{connection.to_node}")

    def register_node_processes(self, env):
        for node in self.nodes:
            env.process(node.run(env))
    
    def plot(self):
        poss = nx.get_node_attributes(self.networkx_graph, "pos") # pos is a dict
        color_map = ['tab:olive' if i == 0 else 'tab:blue' for i in range(len(self.networkx_graph.nodes()))]

        nx.draw_networkx_edges(self.networkx_graph, poss, node_size=NETWORK_NODE_SIZE)
        nx.draw_networkx_nodes(self.networkx_graph, poss, node_size=NETWORK_NODE_SIZE, node_color=color_map)
        plt.legend([ "Connection","Root"])
        nx.draw_networkx_labels(self.networkx_graph, poss, font_size=LABLE_SIZE)

        # Draw ETX edge labels:
        # etx_labels = {}
        # for connection in self.connections:
        #     etx_labels[(connection.from_node, connection.to_node)] =  round(connection.etx_value) #FORKERT!!!  VÆRDIERENE ER KORREKT SAT I PLOTTET
        # nx.draw_networkx_edge_labels(self.networkx_graph, pos, edge_labels=etx_labels, font_size = 6)#verticalalignment="baseline")
        plt.title("Network")
        plt.show()


    # TODO nævn i raport at hver node ikke vil have information om hvordan alle node i en dodag er forbundet da dette ville 
    # kræve en del lagerplads.

    def plot_resulting_dodag(self, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version, nr = "", show = True, save = False): # input: rpl instance, dodag id og dodag version  

        # for node in self.nodes:
        #     print(f"Node {node.node_id}, parent: {node.rpl_instances[0].dodag_list[0].prefered_parent}, DAGRank: {DAGRank(node.rpl_instances[0].dodag_list[0].rank)}, rank: {node.rpl_instances[0].dodag_list[0].rank}, CUMU_ETX: {node.rpl_instances[0].dodag_list[0].metric_object.cumulative_etx} ")

        # for node in self.nodes:
        #     print(f"Node {node.node_id}, parent: {node.rpl_instances[0].dodag_list[0].prefered_parent}, parents_list: {node.rpl_instances[0].dodag_list[0].parents_list}, children_list: {node.rpl_instances[0].dodag_list[0].children_list}, ")
        # TODO HUSK AT NÅR VI UDSKIFTER ROUTING TABELLERNE PÆNT, FÅ OGSÅ LIGE "/[prefix length]" MED I IPV6 ADRESSEN

        for node in self.nodes:
            try:
                print(f"Node {node.node_id}, parent: {node.rpl_instances[0].dodag_list[0].prefered_parent}, downward_routes: {node.rpl_instances[0].dodag_list[0].downward_routes} ")
            except IndexError:
                print(f"Node {node.node_id}, has no dodag")


        if len(self.nodes) == 0:
            raise ValueError("No nodes in network")
        
        # TODO det her virker lidt som en forkert måde at gøre det her på, men det er den eneste måde jeg lige kunne komme på.
        # problemet: Jeg finder og bruger indexer for rpl og dodag listerne baserede på 1 node som er hard coded og brugt til alle.
        rpl_instances = self.nodes[0].rpl_instances
        rpl_instance_idx, dodag_list_idx = find_dodag(rpl_instances, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version) # return index of dodag and/or rpl instance in list of rpl instances
        if (rpl_instance_idx == None) or (dodag_list_idx == None):
            raise ValueError("No Dodag to print with the provided IDs and version.")

        # set up a list containing all edges.
        edges = []
        for node in self.nodes[1:]:
            child = node.node_id
            try:
                parent = node.rpl_instances[rpl_instance_idx].dodag_list[dodag_list_idx].prefered_parent
                edges.append((child, parent))
            except IndexError:
                pass
       
        # plot the DODAG using networkx and graphviz
        G = nx.DiGraph(edges)
        poss = graphviz_layout(G, prog="dot") 
        flipped_poss = {node: (x,-y) for (node, (x,y)) in poss.items()}
        print(flipped_poss)

        color_map = []
        for nodex in G.nodes():
            for node in self.nodes:
                try:
                    rank = node.rpl_instances[rpl_instance_idx].dodag_list[dodag_list_idx].rank
                    if node.node_id == nodex:
                        if node.alive:
                            color_map.append('tab:olive' if rank == ROOT_RANK else 'tab:blue')
                        else:
                            color_map.append('tab:red')
                except IndexError:
                    pass

        nx.draw_networkx_edges(G, flipped_poss, node_size=DODAG_NODE_SIZE)
        nx.draw_networkx_nodes(G, flipped_poss, node_size=DODAG_NODE_SIZE, node_color=color_map)
        nx.draw_networkx_labels(G, flipped_poss, font_size=LABLE_SIZE)


        # nx.draw(G, flipped_poss, with_labels = True, node_size=250, node_color=color_map, font_size=6, width=.7, arrowsize=7)
        
        plt.title("Dodag")
        if save is True:
            plt.savefig(f"Graph{nr}.jpg", format="JPG", dpi=200)
    
        if show is True:
            plt.show()
        else:
            plt.close()
        


    def at_interval_plot(self, rpl_instance_id, dodag_id, dodag_version, interval):
        idx = 0
        while True:
            yield self.env.timeout(interval)
            self.plot_resulting_dodag(rpl_instance_id,dodag_id,dodag_version, idx)
            idx += 1