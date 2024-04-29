import simpy

import networkx as nx
import matplotlib.pyplot as plt


class network:
    
    def __init__(self):
        self.nodes = []

    def add_node(node):
        self.nodes.append(node)

        

class node:
    #skal også have en nodeid?

    def __init__(self, pos_x, pos_y, rank = 999):
        self.posx = pos_x
        self.posy = pos_y
        self.rank = rank

    def send_to(asd):
        pass

class connection:
    def __init__(self, from_node, to_node, etx_value = 999):
        self.from_node = from_node
        self.to_node = to_node
        self.etx_value = etx_value
    

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

    G = nx.Graph()
    #G.add_node(1)
    #G.add_node("davs")
    #G.add_node(3)
    G.add_edge(1,2)
    #G.add_edge(2,3)
    G.add_edge(3,2)
    G.add_edge(3,3)



    #G = nx.petersen_graph()
    #subax1 = plt.subplot(121)
    subax1 = plt.subplot(121)
    nx.draw(G)
    plt.show()


    # Create an environment and start the setup process
    env = simpy.Environment()
    #env.process(test_process(env, "ja taak"))

    # Execute simulation
    #env.run()















if __name__ == '__main__':
    main()