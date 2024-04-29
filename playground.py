import simpy

import networkx as nx
import matplotlib.pyplot as plt
import random

NETWORKGRID_DIMENSION_X = 300
NETWORKGRID_DIMENSION_Y = 300

class Node:

    def __init__(self, node_id, position: tuple[int, int], rank = 999):
        self.node_id = node_id
        self.pos_x = position[0]
        self.pox_y = position[1]
        self.rank = rank

    def set_rank(self, rank):
        self.rank = rank

    def send_to(self, asd):
        pass

    def run(self, env):  # Simpy process
        while(True):
            pass

class Connection:
    def __init__(self, from_node, to_node, etx_value = 999):
        self.from_node = from_node
        self.to_node = to_node
        self.etx_value = etx_value

class Network:
    # https://networkx.org/documentation/stable/auto_examples/drawing/plot_random_geometric_graph.html 

    def __init__(self, dimensions: tuple[int, int]):
        # self.dimension_x = dimensions[0]
        # self.dimension_y = dimensions[1] 
        self.nodes = []
        self.connections = []

    def generate_nodes_and_edges(self, number_of_nodes: int, radius: float, seed = None):

        self.networkx_graph = nx.random_geometric_graph(number_of_nodes, radius, seed=seed)



    
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

        #         # TODO HUSK AT GENERATE ETX VÆRDIER TIL CONNECTIONEN


                
        # for node in self.nodes:
        #     print(node.rank)
        # for connection in self.connections:
        #     print(f"Connection from node: {connection.from_node} to node:{connection.to_node}")
    
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
    pass

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

    # nw = Network()
    # nw.generate_nodes_and_edges(20, 3)
    # nw.plot()


    #UPDATE, VI ER NØDT TIL AT LAVE ET AFSTANDSCONCEPT... ELLERS VIRKER DET SIMPELHEN IKKE ORDENTLIG...
    # så skal max_number_of_connection_pr_node nok også udskiftet med noget node_signal_range_base hvor jeg så +- noget random for at variabere deres signalstyrke lidt. tænk over hvordan det relatere til ETX

    # Create an environment and start the setup process
    #env = simpy.Environment()
    #env.process(test_process(env, "ja taak"))

    # Execute simulation
    #env.run()

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