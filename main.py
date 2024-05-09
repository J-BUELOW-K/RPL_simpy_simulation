import simpy
from network import *
import defines




def main():
    print("hello world")
    #plot_dodag()

    # Setup simulation
    env = simpy.Environment()
    nw = Network(env)
    nw.generate_nodes_and_edges(defines.NUMBER_OF_NODES, defines.RADIUS)
    nw.plot()
    nw.register_node_processes(env)
    nw.construct_new_dodag(123, 123, 123)

    # TODO: VI SKAL HAVE EN MÅDE HVOR VORES NETWÆRK IKKE KAN HAVE NODE NETWÆRK DER "FLYVER" UDE I INGENTING, for hvis en af de nodes bliver valgt til root er vi fucked

    # Execute simulation
    # env.process(nw.at_interval_plot(100))
    env.run(until=defines.SIM_TIME)

    nw.plot_resulting_dodag(123, 123, 123)

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


if __name__ == '__main__':
    main()