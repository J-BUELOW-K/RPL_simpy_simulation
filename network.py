import simpy

import networkx as nx
import matplotlib.pyplot as plt
import math

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
        self.neighbors = [] # list of all neighboring nodes (aka other nodes which this node has a connection/edge to). This list is filled with other Node objects

        # RPL values:_
        self.rpl_instaces = [] # list of RPLIncances that the node is a part of (contains all dodags)
        self.input_msg_queue = simpy.Store(self.env, capacity=simpy.core.Infinity)

    def add_to_connections_list(self, neighbor_id):
        self.neighbors.append(neighbor_id)
        pass

    def broadcast_message(self, msg):
        # broadcast message to all neighbors 
        for neighbor in  self.neighbors:
            neighbor.input_msg_queue.put(msg)   # some simpy examples yield at put(), some dont


    def dio_handler(self):  # om det her skal være i method i Node, eller en funktion i dodag.py file, er spørgsmålet.. skal nok i dodag.py filen for ikke at lav denne class for cluderet
        pass

    def run(self, env):  # Simpy process
        while(True):
            #print(f"hehe: {self.node_id}")
            yield env.timeout(2000) #placeholder Yield på send_timer OG input_msg_queue

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
        self.networkx_graph = nx.random_geometric_graph(number_of_nodes, radius, seed=seed)  # TODO: DET KAN VÆRE VI SKAL LAVE VORES EGEN AF DEN HER. FRA OPGAVEBESKRIVELSEN: Implement and simulate a neighbor discovery mechanism that ensures that each nodeestablish connectivity with its nearest neighbors. MEN VI BESTEMMER SELV! VI LADER DEN BARE STÅ

        # tranlate networkx nodes/edges to our own nodes/connections setup (to make them easier to work with):
        self.connections = [Connection(x[0],x[1]) for x in self.networkx_graph.edges()]
        # self.nodes = [Node(node_id = x) for x in self.networkx_graph.nodes()] # does not include position
        for node in self.networkx_graph.nodes(data="pos"):
            self.nodes.append(Node(self.env, node_id = node[0], xpos = node[1][0], ypos = node[1][1]))  # node format from networkx: (id, [xpos, ypos])
                                                                                              # note: node_id matches index in self.nodes array!

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
            self.nodes[connection.from_node].add_to_connections_list(self.nodes[connection.to_node])  # assumption: index in self.nodes array matches node_id
            self.nodes[connection.to_node].add_to_connections_list(self.nodes[connection.from_node])  # assumption: index in self.nodes array matches node_id


        for connection in self.connections:
            print(f"connection from:{connection.from_node} to:{connection.to_node}")

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
