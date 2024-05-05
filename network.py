import simpy
import copy

import networkx as nx
import matplotlib.pyplot as plt
import math
from dodag import Rpl_Instance, Dodag
from control_messages import *
from OF0 import of0_compute_rank, of0_compare_parent, DAGRank
import defines
from defines import METRIC_OBJECT_TYPE, METRIC_OBJECT_NONE, METRIC_OBJECT_HOPCOUNT, METRIC_OBJECT_ETX, NODE_TRANSMIT_TIMER

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

    if rpl_instance_idx != None: # If there exists an entry for the recieved RPL instance in self.rpl_instances!
        # Find associated Dodag:
        for i in range(len(rpl_instances[rpl_instance_idx].dodag_list)):
            temp_dodag = rpl_instances[rpl_instance_idx].dodag_list[i]
            if temp_dodag.dodag_id == dodag_id and temp_dodag.dodag_version_num == dodag_version: # Both ID and Version has to match!
                #print("debug: matching dodag entry found!")
                dodag_list_idx = i

    return rpl_instance_idx, dodag_list_idx


class Node:

    # MÅSKE ET TUPLE med Dodag object og tilhørende rank. eller skal rank være de del af dodag objetktet?
    
    # Liste med Rpl_Instances (inde i den er listen DODAGS)

    # TODO tilføj contrains liste

    # lav funktion et sted til at broadcast til alle connection (tager senderens node_id som input)
    # HUSK, man skal ikke kun yeild på put(), men også get() (e.g. yield store.put(f'spam {i}'))
    #    hmm... men i Process Communication example yielder de ikke på put. det kommer nok an på om man vil sidde stuck indtil den er sendt, eller bare komme videre idk
    # Problem. hvordan tingår en node andre nodes input queues. er det ikke kun noget netwærk objektet kan?? tænk over det

    def __init__(self, env, node_id, xpos, ypos):

        # Physical network values:
        self.env = env
        self.node_id = node_id
        self.xpos = xpos  # used to estimate ETX
        self.ypos = ypos  # used to estimate ETX
        self.neighbors = [] # Each element is a tuple: (node object, connection object). 
                            # List of all neighboring nodes and associated connection objects (aka other nodes which this node has a connection/edge to) 
                            # This list has nothing to do with any RPLInstance or DODAG, its simply information about the physical network.

        # RPL values:
        self.rpl_instances = [] # list of RPLIncances that the node is a part of (contains all dodags)
        self.input_msg_queue = simpy.Store(self.env, capacity=simpy.core.Infinity)
        self.silent_mode = True  # node will stay silent untill (see section 18.2.1.1 in RPL standard)

    def add_to_neighbors_list(self, neighbor_object, connection_object): # add a single neighbor to the self.neighbors list
        self.neighbors.append((neighbor_object, connection_object))
        pass

    def increment_metric_object_from_neighbor(self, neighbors_metric_object, neighbors_node_id): # helper function used to increment a metric object recieved from a neighbor - to include path from neighbor to this node
        print(f"debug: nabo objekt:{neighbors_metric_object}")
        if METRIC_OBJECT_TYPE == METRIC_OBJECT_NONE:
            return None
        elif METRIC_OBJECT_TYPE == METRIC_OBJECT_HOPCOUNT:
            neighbors_metric_object.cumulative_hop_count += 1
        elif METRIC_OBJECT_TYPE == METRIC_OBJECT_ETX:
            for neighbor in self.neighbors:
                if neighbor[0].node_id == neighbors_node_id:
                    neighbors_metric_object.cumulative_hop_count += neighbor[1].etx_value
        return neighbors_metric_object
                    

    def broadcast_packet(self, packet):
        # broadcast message to all neighbors 
        for neighbor in self.neighbors:
            neighbor[0].input_msg_queue.put(packet)   # some simpy examples yield at put(), some dont

    # def debug_print_neighbors(self):
    #     for nabo in self.neighbors:
    #         print(f"neighbor node: {nabo[0].node_id}, conection to:{nabo[1].from_node}, connection to: {nabo[1].to_node}, etx: {nabo[1].etx_value}")

    def broadcast_dio(self, rpl_instance_id, dodag: Dodag):
         # NOTE: DEN SKAL VEL BARE BROADACAST DIS TIL ALLE NODESENS GEMLE DDOAGS. MEN DET MÅ SKAL ET LAG LÆNGERE OPPE

        icmp_dio = ICMP_DIO(rpl_instance_id, dodag.dodag_version_num, dodag.rank, dodag.dodag_id) # DIO message with icmp header
        if METRIC_OBJECT_TYPE == METRIC_OBJECT_HOPCOUNT:
            icmp_dio.add_HP_metric(dodag.metric_object.cumulative_hop_count) 
            pass
        elif METRIC_OBJECT_TYPE == METRIC_OBJECT_ETX:
            icmp_dio.add_ETX_metric(dodag.metric_object.cumulative_etx) 
            pass
        packet = Packet(self.node_id, icmp_dio)
        self.broadcast_packet(packet)
    
    def broadcast_all_dios(self):
        for instance in self.rpl_instances:
            for dodag in instance.dodag_list:
               self. broadcast_dio(instance.rpl_instance_id, dodag)

    
    def dio_handler(self, senders_node_id, dio_message: ICMP_DIO, senders_metric_object = None):
        # see section 8 in RPL standarden (RFC 6550) 
        # Ehhh:
        #  DODAGID: The DODAGID is a Global or Unique Local IPv6 address of the
        #          root.  A node that joins a DODAG SHOULD provision a host route
        #          via a DODAG parent to the address used by the root as the
        #          DODAGID.
        # AKA DODAG ID ER IPV6 ADDRESSEN?!?!?!?

        

        ####################  Find RPL Instance and Dodag in the nodes self.rpl_instaces list - If no entries, we create them ####################

        # V2:
        rpl_instance_idx, dodag_list_idx = find_dodag(self.rpl_instances, dio_message.rpl_instance_id, \
                                                      dio_message.dodag_id, dio_message.vers)
        if rpl_instance_idx == None:
            # No entry in self.rpl_instaces for recieved RPL instance! Create one!
            dodag_object = Dodag(dio_message.dodag_id, dio_message.vers)
            rpl_instance_obj = Rpl_Instance(dio_message.rpl_instance_id)
            rpl_instance_obj.add_dodag(dodag_object)
            self.rpl_instances.append(rpl_instance_obj)
            rpl_instance_idx = len(self.rpl_instances) - 1 # there might already be entries for other instances in the self.rpl_instaces list
            dodag_list_idx = len(rpl_instance_obj.dodag_list) - 1  # value is always just 0
        else:
            # There exists an entry for the recieved RPL instance in self.rpl_instances!
            if dodag_list_idx == None:
                # No existing DODAG entry in the RPL Instance! Create one!
                dodag_object = Dodag(dio_message.dodag_id, dio_message.version)
                self.rpl_instances[rpl_instance_idx].add_dodag(dodag_object)
                dodag_list_idx = len(self.rpl_instances[rpl_instance_idx].dodag_list) - 1 # value is always just 0

        intance_reference = self.rpl_instances[rpl_instance_idx]
        dodag_reference = intance_reference.dodag_list[dodag_list_idx]


        ####################  asdasdasd ####################  
        if dodag_reference.rank == defines.ROOT_RANK:
            return


        ####################  CHECK IF SENDER IS A BETTER PREFERRED PARENT THAN THE CURRENT PREFERRED PARRENT - UPDATE STUFF IF IT IS ####################

        senders_metric_object_copy = copy.deepcopy(senders_metric_object) # create copy to not alter the original.
        metric_object_through_neighbor = self.increment_metric_object_from_neighbor(senders_metric_object_copy, senders_node_id) 

        if dodag_reference.prefered_parent == None: # Our node does not have a prefered parent - we simply accept the DIO sender as prefered parent
            dodag_reference.prefered_parent = senders_node_id
            dodag_reference.prefered_parent_rank = dio_message.rank
            dodag_reference.metric_object = metric_object_through_neighbor # update metric object
            dodag_reference.rank = of0_compute_rank(dodag_reference.prefered_parent_rank, dodag_reference.metric_object)  # update rank
        else:
            # test if sender is a better prefered parrent than current prefered parrent:
            #if of0_compare_parent(asdasd) == 1: # if sender is better parent
            result, winner_rank = of0_compare_parent(dodag_reference.prefered_parent_rank, dio_message.rank, \
                                                     dodag_reference.metric_object, metric_object_through_neighbor)
            if result =="update parent":
                # we found a better preferred parent!
                dodag_reference.prefered_parent = senders_node_id
                dodag_reference.prefered_parent_rank = dio_message.rank
                dodag_reference.metric_object = metric_object_through_neighbor # update metric object
                dodag_reference.rank = winner_rank # we can just use the rank computed from of0_compare_parent - we dont have to compute it again
            

        








        
        
        # rpl_instance_idx = next((idx for idx, instance in enumerate(self.rpl_instaces) 
        #                         if instance.rpl_instance_id == dio_message.rpl_instance_id), None)
        
        # if rpl_instance_idx is None: # if the node doesn't have a rpl instance with the same id as the one in the dio message
        #     self.rpl_instaces.append(dodag.Rpl_Instance(dio_message.rpl_instance_id)) # create a new rpl instance object and add it to the list of rpl instances in the node
        #     rpl_instance_idx = len(self.rpl_instaces) - 1 # get the index of the newly created rpl instance object
            

        # dodag_idx = next((idx for idx, dodag in enumerate(self.rpl_instaces[rpl_instance_idx].dodag_list) 
        #                 if dodag.dodag_id == dio_message.dodag_id), None)
        
        
        # if dodag_idx is None: # if the node doesn't have a dodag with the same id as the one in the dio message
        #     self.rpl_instaces[rpl_instance_idx].dodag_list.append(dodag.Dodag(dio_message.dodag_id, dio_message.version, is_root = False)) # create a new dodag object and add it to the list of dodags in the rpl instance
        #     dodag_idx = len(self.rpl_instaces[rpl_instance_idx].dodag_list) - 1 # get the index of the newly created dodag object
            

        # preferred_parent = self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].preferred_parent
        # rank = self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].rank
        
        # if not preferred_parent or self.OF0(dio_message, preferred_parent): # if the new DIO message provides a better parent than the current preferred parent (or the node doesn't have a preferred parent) then update the node's preferred parent
        #     self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].preferred_parent = source_node_id #TODO new parent object
            
        #     self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].rank = compute_rank(dio_message.dodag_id, rank) # Step 8 in RFC 6552  # self.rank skal være den fra den korrekte dodagi RPLinstance arrayed
            
        #     # TODO update acculimated ETX, hvis vi vælger en ny parent.. ved ikke lige hvordan det hænger sammen..

        #     # broadcast dio message to all neighbors
        #     self.broadcast_dio(dio_message)

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
        #       AKA 3 SET (lister). NABOER, PARENTS OG PREFERD PARENT (i RPL kan man have flere preferd parents.. men det arbejder vi ikke med)
        #       VED IKKE HVAD VI SKAL BRUGE PARENT LISTEN TIL... SÅ TÆNKER VI IGNORE DEM
        #       ELLER HVAD! HVADD ER DET VI PASSER OF0? ER DET PARENTS ELLER HVAD??? FUCK...
        #       OKAY, SÅ VI SKAL HAVE EN LISTE MED PARRENTS?? MEN BEHØVER VI DET MED VORES OF0 IMPLMENETRING??
                #  I OF0 STÅR DER  : As it scans all the candidate neighbors, OF0 keeps the parent that is
                    #the best for the following criteria (in order):
                #   SÅ SPØRGSMÅLET ER OM INPUTTET TIL OF0 KAN VÆRE DIO BESKEDER FRA ALLE NABOER, ELLER!!! OM DEN FORVENTER MAN KUN INPUTTER DEN PARENTS(aka naboer med advetised rank mindre end nodens egen rank)


        # TODO Vores OF0 skal tage metric in mind. og måske også contrains hvis du vælger at tilføje det
                # (cumulative path ETX calculated as the sum of the link ETX
                #    of all of the traversed links from the advertising node to the DAG
                #    root), if it selects that node as its preferred parent, the node
                #    updates the path ETX by adding the ETX of the local link between
                #    itself and the preferred parent to the received path cost (path ETX)
                #    before potentially advertising itself the new path ETX.
                # AKA UPDATE DET KUMMULATIVE ETX I ETX METRIC OBJEKTET, HVIS VI VÆLGER EN NY PARENT
                # TROR OGSÅ KUN VI SKAL UPDATE RANK, HVIS VI FÅR EN NY PREFFERED PARRENT.



        # MEGET VIGTIGT - SE 4.3.2. The ETX Reliability Object I METRIC STANDARDEN




        # tror faktisk ikke noden behøver have en liste over beskeder fra alle de andres dodag info... tror bare, hver gang den får en DIO besked, skal den sammenligne om den giver en bedre preferd parent end tden tidligere. hvis den gør, så update preferd parent, update rank og brug den nye rank i dens dio beskeder. hvis noden får en dio uden at have andre, skal den bare gøre den til preferd parent
        

        pass

    def packet_handler(self, packet: Packet):
        # Read ICMP Header:
        #print(f"yesdu: {packet}")
        icmp_header = packet.payload.icmp
        if icmp_header.type != defines.TYPE_RPL_CONTOL_MSG:
            # invalid packet - ignore it
            return
        if icmp_header.code == defines.CODE_DIO:
            self.dio_handler(packet.src_node_id, packet.payload.dio, packet.payload.option)
            pass # TODO
        elif icmp_header.code == defines.CODE_DAO:
            pass # TODO
        elif icmp_header.code == defines.CODE_DAO_ACK:
            pass # TODO
        elif icmp_header.code == defines.CODE_DIS:
            pass # TODO


    def run(self, env):  # Simpy process
        while(True):
            #print(f"hehe: {self.node_id}")
            if self.silent_mode == True:
                message = yield self.input_msg_queue.get()
                self.silent_mode = False
                print(message)
                print(type(message))
                self.packet_handler(message)
            else: # if silent_mode = False
                event = yield self.input_msg_queue.get() | env.timeout(NODE_TRANSMIT_TIMER, value = "timeooout")  # Periodic timer is replacement for tricle timer
                if (next(iter(event.values())) == "timeooout"): # event was a timeout event. (https://stackoverflow.com/questions/21930498/how-to-get-the-first-value-in-a-python-dictionary)
                    # broadcast_dio() # TODO - NODEN SKAL VEL BROADCASTE ALLE DENS DODAGS TIL ALLE DENS CONNECTIONS
                    print("debug: Node: timeout!")
                    self.broadcast_all_dios()
                    pass
                else: # event was a "message in input_msg_queue" event
                    # TODO HVIS DET DER IF ELSE HALLØJ MED event.values() GIVER FEJL, SÅ PRØV TRY EXECPT
                    print("debug: Node:: packet recieved!")
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
            self.nodes.append(Node(self.env, node_id = node[0], xpos = node[1][0], ypos = node[1][1]))  # node format from networkx: (id, [xpos, ypos])
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

        
        

        # # Check if specified RPL instance already exists:
        # for instance in root_node.rpl_instances:
        #     if instance.rpl_instance_id == rpl_instance_id:
        #         # simply use this instance
        #         # Check if identical DODAG already exists in this RPL Instance:
        #         for dodag in instance.dodag_list:
        #             if dodag.dodag_id == dodag_id and dodag.dodag_version_num == dodag_version_num:
        #                 # Identical dodag already exists within the specified RPL Instance...
        #                 raise 
        #         return # husk at return her! ... medmindre der mere vi skal lave.. f.eks. sende den først dio ud

        # # No rpl instance found with matching rpl_istance_id... create one (including dodag)!
        # rpl_instance = Rpl_Instance(rpl_instance_id)
        # dodag = Dodag(dodag_id, dodag_version_num, rank = 0) # setting rank to 0 makes it root in the new dodag!
        # rpl_instance.add_dodag(dodag)
        # root_node.rpl_instances.append(rpl_instance)


        #V2:
        # Check if specified RPL instance/dodag already exists in root node:
        rpl_instance_idx, dodag_list_idx = find_dodag(root_node.rpl_instances, rpl_instance_id, dodag_id, dodag_version)
        if rpl_instance_idx != None:
            # RPL instance entry found in root node
            if dodag_list_idx != dodag_list_idx:
                print("ERROR: Identical DODAG entry already exists...")
                raise ValueError 
            else:
                # Create DODAG in root node, within the already existing RPL Instance
                new_dodag = Dodag(dodag_id, dodag_version, rank = defines.ROOT_RANK) # setting rank to 0 makes the node the root!
                root_node.rpl_instances[rpl_instance_idx].add_dodag(new_dodag)
        else:
            # No matching RPL entry exists in root node - create one! (including dodag):
            new_rpl_instance = Rpl_Instance(rpl_instance_id)
            new_dodag = Dodag(dodag_id, dodag_version, rank = defines.ROOT_RANK) # setting rank to 0 makes the node the root!
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
        pos = nx.get_node_attributes(self.networkx_graph, "pos") # pos is a dict
        nx.draw_networkx_edges(self.networkx_graph, pos)
        nx.draw_networkx_nodes(self.networkx_graph, pos, node_size=80)

        # Draw ETX edge labels:
        # etx_labels = {}
        # for connection in self.connections:
        #     etx_labels[(connection.from_node, connection.to_node)] =  round(connection.etx_value) #FORKERT!!!  VÆRDIERENE ER KORREKT SAT I PLOTTET
        # nx.draw_networkx_edge_labels(self.networkx_graph, pos, edge_labels=etx_labels, font_size = 6)#verticalalignment="baseline")

        plt.show()

    def plot_resulting_dodag(self):
        #TODO SKAL RENT FAKTISK LAVE ET PLOT 
        # for node in self.nodes:
        #     print(f"Node {node.node_id}, parent: {node.rpl_instances[0].dodag_list[0].prefered_parent}, DAGRank: {DAGRank(node.rpl_instances[0].dodag_list[0].rank)} ")

        for node in self.nodes:
            print(f"Node {node.node_id}, parent: {node.rpl_instances[0].dodag_list[0].prefered_parent}, DAGRank: {DAGRank(node.rpl_instances[0].dodag_list[0].rank)}, HP: {node.rpl_instances[0].dodag_list[0].metric_object.cumulative_hop_count} ")
        # def plot_dodag(): # SKAL NOK VÆRE EN METHOD I DODAG CLASSEN
        # G = nx.DiGraph()
        # #G.add_node(1)
        # #G.add_node("davs")
        # # #G.add_node(3)
        # # G.add_edge(1,2)
        # # #G.add_edge(2,3)
        # # G.add_edge(3,2)
        # # G.add_edge(3,3)

        # G.add_node(1)
        # G.add_node(2)
        # G.add_node(3)
        # G.add_node(4)
        # G.add_node(5)

        # G.add_edge(1,2)
        # G.add_edge(2,3)
        # G.add_edge(5,1)
        # G.add_edge(4,2)

        # G_triangle = nx.DiGraph([(2, 1), (3, 1), (4, 1), (5,2)])

        # #G = nx.petersen_graph()
        # #subax1 = plt.subplot(121)
        # #subax1 = plt.subplot(121)
        # #nx.draw(G,with_labels=True)
        # #nx.draw_planar(G_triangle,with_labels=True)
        # #nx.draw(G_triangle,pos=nx.multipartite_layout(G_triangle),with_labels=True)
        # G = nx.DiGraph([(1, 0), (2, 0), (3, 0), (4, 2),(5, 3)])
        # layers = {"b": [4,5], "c": [1,2,3], "d": [0]}  #når jeg skal gøre det automatisk. start med tomt array. så bare brug rank til at start fra bunden og op, hvor jeg appender hver lag
        # pooos = nx.multipartite_layout(G, subset_key=layers, align="horizontal")
        # nx.draw(G,pos=pooos,with_labels=True)

        # # ER RET SIKKER PÅ VI SKAL BRUGE intergar part of rank (aka dag_rank_macro()) når vi plotter!!!!! Ikke den fulde float rank!

        # #VI SKAL NOK BRUGE DRAW MED POS = multipartite_layout() TIL AT TEGNE DAGS https://networkx.org/documentation/stable/auto_examples/graph/plot_dag_layout.html
        # plt.show()
