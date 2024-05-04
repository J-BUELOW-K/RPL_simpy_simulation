import simpy
from network import *
import defines

SIM_TIME = 1000


def main():
    print("hello world")
    #plot_dodag()

    # Setup simulation
    env = simpy.Environment()
    nw = Network(env)
    nw.generate_nodes_and_edges(defines.NUMBER_OF_NODES, defines.RADIUS)
    nw.plot()
    nw.register_node_processes(env)

    # TODO: VI SKAL HAVE EN MÅDE HVOR VORES NETWÆRK IKKE KAN HAVE NODE NETWÆRK DER "FLYVER" UDE I INGENTING, for hvis en af de nodes bliver valgt til root er vi fucked

    # Execute simulation
    env.run(until=SIM_TIME)

    # TODO print dodag her (lav til funktion i netowrk klassen, der hent rank og parent fra alle nodes og plotter dem)

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





3








def plot_dodag(): # SKAL NOK VÆRE EN METHOD I DODAG CLASSEN
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

    # ER RET SIKKER PÅ VI SKAL BRUGE intergar part of rank (aka dag_rank_macro()) når vi plotter!!!!! Ikke den fulde float rank!

    #VI SKAL NOK BRUGE DRAW MED POS = multipartite_layout() TIL AT TEGNE DAGS https://networkx.org/documentation/stable/auto_examples/graph/plot_dag_layout.html
    plt.show()


if __name__ == '__main__':
    main()