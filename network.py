import simpy

import networkx as nx
import matplotlib.pyplot as plt
import math
import dodag
from dio import *

SPEED_OF_LIGHT = 299792458
LINK_FREQ = 2.4 * pow(10, 9)  # Hz

MAX_ETX = 0xFFFF
MAX_DISTANCE = 0xFFFF

NODE_TRANSMIT_TIMER = 200 # Periodic transmit timer - in simpy time units

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
        self.neighbors = [] # List of all neighboring nodes and associated connection objects (aka other nodes which this node has a connection/edge to) 
                            # Each element is a tuple: (node object, connection object). 
                            # This list has nothing to do with any RPLInstance or DODAG, its simply information about the physical network.

        # RPL values:
        self.rpl_instaces = [] # list of RPLIncances that the node is a part of (contains all dodags)
        self.input_msg_queue = simpy.Store(self.env, capacity=simpy.core.Infinity)
        self.silent_mode = True  # node will stay silent untill (this approach is mentioned as valid in the RPL standard)

    def add_to_neighbors_list(self, neighbor_object, connection_object): # add a single neighbor to the self.neighbors list
        self.neighbors.append((neighbor_object, connection_object))
        pass

    def broadcast_message(self, msg):
        # broadcast message to all neighbors 
        for neighbor in self.neighbors:
            neighbor.input_msg_queue.put(msg)   # some simpy examples yield at put(), some dont

    # def debug_print_neighbors(self):
    #     for nabo in self.neighbors:
    #         print(f"neighbor node: {nabo[0].node_id}, conection to:{nabo[1].from_node}, connection to: {nabo[1].to_node}, etx: {nabo[1].etx_value}")

    def broadcast_dio(self):
        #lav dio object (måske fra en funktion i en anden fil) # ænk over  hvordan den får info til at lave dio objekete. hvordan det lige virker...
        # MÅSKE er broadcast_dio difineret i en anden fil (der hvor dio handleren er) - og så gør den fil bare brug af node_objectet.broadcast_message (skal man noden så passe sig selv? hvordan virker det? kan man passe "self" måske)
        #broadcast_message(dio_object)

    # TODO i OF0 "Selection of the Preferred Parent" Step 1, nævner de at en nabo skal overholder alle steps fra 8.2.1 i RPL standarden, før den overhoevedet kan overvejes i OF0.
    # TODO Dio beskeder kan carry options - overvej om vi skal sende en metric object med dio beskederne (forskellige metric objekter er definineret i RFC 6551) (se sec 6.3.3 og 6.7.4 i RPL stanarden)

    # def dio_handler(self):  # om det her skal være i method i Node, eller en funktion i dodag.py file, er spørgsmålet.. det kommer an på hvor meget handleren skal bruge af variabler er i klassen. Hvis den ikke skal bruge nogle self variabler.. så bare lav den i dodag.py filen
         pass
    
    def dio_handler(self, source_node_id, dio_message: DIO_message):
        # see section 8 in RPL standarden (RFC 6550) 
        # Ehhh:
        #  DODAGID: The DODAGID is a Global or Unique Local IPv6 address of the
        #          root.  A node that joins a DODAG SHOULD provision a host route
        #          via a DODAG parent to the address used by the root as the
        #          DODAGID.
        # AKA DODAG ID ER IPV6 ADDRESSEN?!?!?!?

        
        
        
        rpl_instance_idx = next((idx for idx, instance in enumerate(self.rpl_instaces) 
                                if instance.rpl_instance_id == dio_message.rpl_instance_id), None)
        
        if rpl_instance_idx is None: # if the node doesn't have a rpl instance with the same id as the one in the dio message
            self.rpl_instaces.append(dodag.Rpl_Instance(dio_message.rpl_instance_id)) # create a new rpl instance object and add it to the list of rpl instances in the node
            rpl_instance_idx = len(self.rpl_instaces) - 1 # get the index of the newly created rpl instance object
            

        dodag_idx = next((idx for idx, dodag in enumerate(self.rpl_instaces[rpl_instance_idx].dodag_list) 
                        if dodag.dodag_id == dio_message.dodag_id), None)
        
        
        if dodag_idx is None: # if the node doesn't have a dodag with the same id as the one in the dio message
            self.rpl_instaces[rpl_instance_idx].dodag_list.append(dodag.Dodag(dio_message.dodag_id, dio_message.version, is_root = False)) # create a new dodag object and add it to the list of dodags in the rpl instance
            dodag_idx = len(self.rpl_instaces[rpl_instance_idx].dodag_list) - 1 # get the index of the newly created dodag object
            

        preferred_parent = self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].preferred_parent
        rank = self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].rank
        
        if not preferred_parent or self.OF0(dio_message, preferred_parent): # if the new DIO message provides a better parent than the current preferred parent (or the node doesn't have a preferred parent) then update the node's preferred parent
            self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].preferred_parent = source_node_id #TODO new parent object
            
            self.rpl_instaces[rpl_instance_idx].dodag_list[dodag_idx].rank = compute_rank(dio_message.dodag_id, rank) # Step 8 in RFC 6552  # self.rank skal være den fra den korrekte dodagi RPLinstance arrayed
            
            # TODO update acculimated ETX, hvis vi vælger en ny parent.. ved ikke lige hvordan det hænger sammen..

            # broadcast dio message to all neighbors
            self.broadcast_dio(dio_message)

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

    def run(self, env):  # Simpy process
        while(True):
            print(f"hehe: {self.node_id}")
            if self.silent_mode == True:
                message = yield self.input_msg_queue.get()
                self.silent_mode = False
                # msg_handler(message) # TODO
            else: # if silent_mode = False
                event = yield self.input_msg_queue.get() | env.timeout(NODE_TRANSMIT_TIMER, value = "timeooout")  # Periodic timer is replacement for tricle timer
                if (next(iter(event.values())) == "timeooout"): # event was a timeout event. (https://stackoverflow.com/questions/21930498/how-to-get-the-first-value-in-a-python-dictionary)
                    # broadcast_dio() # TODO
                    pass
                    pass
                else: # event was a "message in input_msg_queue" event
                    # msg_handler(message)  # TODO
                    pass
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
