import simpy

import networkx as nx
import matplotlib.pyplot as plt
import math

SPEED_OF_LIGHT = 299792458
LINK_FREQ = 2.4 * pow(10, 9)  # Hz

def estimate_etx(distance: float, model: str) -> float:
    if model == "linear":
        pass
        return 999 #placeholder
    elif model == "fspl":
        fspl = pow((4*math.pi*distance*LINK_FREQ) / SPEED_OF_LIGHT, 2)  # https://en.wikipedia.org/wiki/Free-space_path_loss
        return fspl

    # ETX calc is not specific, however is it usually calculated as: ETX = 1 / (Df*Dr) 
                                        # where Df is the measured probability that a packet is received by the neighbor and Dr is 
                                        # the measured probability that the acknowledgment packet is successfully received.
                                        # https://datatracker.ietf.org/doc/html/rfc6551#page-21)
                                        # https://hal.science/hal-01165655/document
    # HOWEVER, as we just use the ETX to compare against other ETX values, it only needs to be relative to itself.
    # Note: this also means tht we CANT think of our specific ETX value as "expected transmission count"


class Node:
    def __init__(self, node_id, xpos, ypos ,rank = 999):
        self.node_id = node_id
        self.rank = rank
        self.xpos = xpos  # used to estimate ETX
        self.ypos = ypos  # used to estimate ETX

    def set_rank(self, rank):
        self.rank = rank

    def send_to(self, asd):
        pass

    def run(self, env):  # Simpy process
        while(True):
            #print(f"hehe: {self.node_id}")
            yield env.timeout(2000) #placeholder

class Connection:
    def __init__(self, from_node, to_node, etx_value = 999):
        self.from_node = from_node
        self.to_node = to_node
        self.etx_value = etx_value

class Network:
    # https://networkx.org/documentation/stable/auto_examples/drawing/plot_random_geometric_graph.html 

    def __init__(self):
        self.nodes = []
        self.connections = [] # this line is not strickly needed (is here for completeness)
        pass

    def generate_nodes_and_edges(self, number_of_nodes: int, radius: float, seed = None):

        # Generate geometric network (nodes are places at random, edges are drawn if within radius):
        self.networkx_graph = nx.random_geometric_graph(number_of_nodes, radius, seed=seed)

        # tranlate networkx nodes/edges to our own nodes/connections setup (to make them easier to work with):
        #self.nodes = [Node(node_id = x) for x in self.networkx_graph.nodes()]
        for node in self.networkx_graph.nodes(data="pos"):
            self.nodes.append(Node(node_id = node[0], xpos = node[1][0], ypos = node[1][1]))  # node format from networkx: (id, [xpos, ypos])

        self.connections = [Connection(x[0],x[1]) for x in self.networkx_graph.edges()]
        # self.nodes = self.networkx_graph.nodes())

        # Select a root node by "random" (we simply choose the root with root_it 0):
        self.nodes[0].rank = 0

        print(self.networkx_graph.nodes(data="pos"))
        # for connection in self.connections:
        #     print(self.networkx_graph.edges(data=True))
            #distance =   # DEN HER SKAL VÆRE EN DEN AF CONNECTION OBJEKTET
            #connection.etx_value = estimate_etx(distance, "fspl")
            
            


        # TODO HUSK AT GENERATE ETX VÆRDIER TIL CONNECTIONEN
        # TODO EN NODE SKAL VÆLGES TIL ROOT (giv den rank 0) - bare en tilfældig
        # TODO skal vi emulere packet loss?? altså at der er en x risiko for at vi ikke sender beskeden afsted, hvis vi prøver packet_loss_propability
                # vi kan måske udregne ETX = 1 / Df  (Df is the measured probability that a packet is received by the neighbor)
                # og så bestemme Df udfra afstanden. Jo tættere conenction afstand er på radius, jo tættet Df --> 0
                # 

        # for node in self.nodes:
        #     print(node.node_id)
        # for connection in self.connections:
        #     print(f"Connection from node: {connection.from_node} to node:{connection.to_node}")

    
        # for node_id in range(number_of_nodes):
        #     self.nodes.append(Node(node_id))

        # for node in self.nodes:
        #     #create connection from individual node to other nodes
        #     exclude_con_to = [node.node_id] #exclude connection to itself
        #     for _ in range(random.randint(1, max_number_of_connection_pr_node)): #its a network so min connections are 1
        #         connection_to = random.choice([x for x in range(number_of_nodes) if x not in exclude_con_to]) # choose at random who the node should have connection to
        #         self.connections.append(Connection(node.node_id, connection_to))
        #         exclude_con_to.append(connection_to) # update exclude_con_to list as to not create multiple connections to same node later

        #         #UPDATE: gnp_random_graph gør vidst basically det jeg har gang i her...

        #         

    def register_node_processes(self, env):
        for node in self.nodes:
            env.process(node.run(env))

    
    def plot(self):
        pos = nx.get_node_attributes(self.networkx_graph, "pos") # pos er et dict!
        nx.draw_networkx_edges(self.networkx_graph, pos)
        nx.draw_networkx_nodes(self.networkx_graph, pos, node_size=80)
        plt.show()



        # G = nx.Graph()

        # # translate from our Nodes/Connections setup to networkx nodes and edges:
        # for node in self.nodes:
        #     G.add_node(node.node_id)
        # for connection in self.connections:
        #     G.add_edge(connection.from_node, connection.to_node)

        # # TODO NOK OGSÅ PLOT ETX

        # #Draw nodes and edges (Note: this figure does not match the actual x and y values of each node)
        # nx.draw(G, with_labels = True)
        # plt.show()


            



def main():
    print("hello world")

    # Setup simulation
    env = simpy.Environment()
    nw = Network()
    nw.generate_nodes_and_edges(70, 0.2)
    nw.plot()
    nw.register_node_processes(env)

    # Execute simulation
    env.run()


    #Vi leder efter Geometric grapghs!
    # https://networkx.org/documentation/stable/reference/generators.html
    # HER ER VIGTIG GUIDE: https://networkx.org/documentation/stable/auto_examples/drawing/plot_random_geometric_graph.html 

    #G = nx.binomial_graph(20, 0.2)
    #G = nx.barabasi_albert_graph(50, 0.2)
    # n = 40
    # #pos = {i: (random.gauss(0, 2), random.gauss(0, 2)) for i in range(n)}
    # G = nx.random_geometric_graph(n, 0.3)
    # nx.draw(G, with_labels = True)
    # plt.show()

    # Use seed when creating the graph for reproducibility
    # G = nx.random_geometric_graph(70, 0.2, seed=896803)
    # # position is stored as node attribute data for random_geometric_graph
    # pos = nx.get_node_attributes(G, "pos") # pos er et dict!
    # nx.draw_networkx_edges(G, pos)
    # nx.draw_networkx_nodes(G, pos, node_size=80,)
    # plt.show()




    #UPDATE, VI ER NØDT TIL AT LAVE ET AFSTANDSCONCEPT... ELLERS VIRKER DET SIMPELHEN IKKE ORDENTLIG...
    # så skal max_number_of_connection_pr_node nok også udskiftet med noget node_signal_range_base hvor jeg så +- noget random for at variabere deres signalstyrke lidt. tænk over hvordan det relatere til ETX



# class testy:

#     def __init__(self, env, okaya):
#         self.env = env
#         self.okaya = okaya
#         pass

#     def testyy(self, asd2):
#         pass

#     def testy_process(self):
#         self.env.timeout(2000)

# def test_process(env, yapper):

#     while True:
#         yield env.timeout(1000)
#         print(yapper)







# def plot_network(network: Network):
#     pass


def plot_dodag(): #SKAL HAVE DODAG CLASS SOM INPUT? TBD  (dodag: Dodag)
    G = nx.DiGraph()
    #G.add_node(1)
    #G.add_node("davs")
    # #G.add_node(3)
    # G.add_edge(1,2)
    # #G.add_edge(2,3)
    # G.add_edge(3,2)
    # G.add_edge(3,3)

    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)

    G.add_edge(1,2)
    G.add_edge(2,3)
    G.add_edge(5,1)
    G.add_edge(4,2)

    G_triangle = nx.DiGraph([(2, 1), (3, 1), (4, 1), (5,2)])

    #G = nx.petersen_graph()
    #subax1 = plt.subplot(121)
    #subax1 = plt.subplot(121)
    #nx.draw(G,with_labels=True)
    #nx.draw_planar(G_triangle,with_labels=True)
    #nx.draw(G_triangle,pos=nx.multipartite_layout(G_triangle),with_labels=True)
    G = nx.DiGraph([(1, 0), (2, 0), (3, 0), (4, 2),(5, 3)])
    layers = {"b": [4,5], "c": [1,2,3], "d": [0]}  #når jeg skal gøre det automatisk. start med tomt array. så bare brug rank til at start fra bunden og op, hvor jeg appender hver lag
    pooos = nx.multipartite_layout(G, subset_key=layers, align="horizontal")
    nx.draw(G,pos=pooos,with_labels=True)

    #VI SKAL NOK BRUGE DRAW MED POS = multipartite_layout() TIL AT TEGNE DAGS https://networkx.org/documentation/stable/auto_examples/graph/plot_dag_layout.html
    plt.show()


if __name__ == '__main__':
    main()