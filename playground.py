import simpy

import networkx as nx
import matplotlib.pyplot as plt
import random

class Node:
    #skal også have en nodeid?
    def __init__(self, node_id, rank = 999):
        self.node_id = node_id
        self.rank = rank

    def set_rank(self, rank):
        self.rank = rank

    def send_to(asd):
        pass

class Connection:
    def __init__(self, from_node, to_node, etx_value = 999):
        self.from_node = from_node
        self.to_node = to_node
        self.etx_value = etx_value

class Network:
    
    def __init__(self):
        self.nodes = []
        self.connections = []

    def generate_nodes_and_edges(self, number_of_nodes: int, max_number_of_connection_pr_node: int):
        for node_id in range(number_of_nodes):
            self.nodes.append(Node(node_id))

        for node in self.nodes:
            #create connection from individual node to other nodes
            exclude_con_to = [node.node_id] #exclude connection to itself
            for _ in range(random.randint(1, max_number_of_connection_pr_node)): #its a network so min connections are 1
                connection_to = random.choice([x for x in range(number_of_nodes) if x not in exclude_con_to]) # choose at random who the node should have connection to
                self.connections.append(Connection(node.node_id, connection_to))
                exclude_con_to.append(connection_to) # update exclude_con_to list as to not create multiple connections to same node later

                # OGSÅ HUSK AT GENERATE ETX VÆRDIER TIL CONNECTIONEN
    
    def plot(self):
        # create networkx nodes og edges udfra vores Node og Connection setup

        G = nx.Graph()

        # translate from our Nodes/Connections setup to networkx nodes and edges
        for node in self.nodes:
            G.add_node(node.node_id)
        for connection in self.connections:
            G.add_edge(connection.from_node, connection.to_node)
        
        nx.draw(G, with_labels = True)
        plt.show()
            

        # for node in self.nodes:
        #     print(node.rank)
        # for connection in self.connections:
        #     print(f"Connection from node: {connection.from_node} to node:{connection.to_node}")
        

    #SKAL HAVE NOGET TIL AT LAVE NETWORK 
    # (AKA OGSÅ TEGNE NODES OG EDGES I NETWORKX)
        




    

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



def main():
    print("hello world")

    # Setup simulation
    pass


    nw = Network()
    nw.generate_nodes_and_edges(20, 3)
    nw.plot()


    #UPDATE, VI ER NØDT TIL AT LAVE ET AFSTANDSCONCEPT... ELLERS VIRKER DET SIMPELHEN IKKE ORDENTLIG...

    # Create an environment and start the setup process
    env = simpy.Environment()
    #env.process(test_process(env, "ja taak"))

    # Execute simulation
    #env.run()









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