import simpy
from network import Network
import defines



def main():
    print("hello world")


    rpl_instance = 1  # arbitrarily chosen 
    dodag_id = defines.IPV6_GLOBAL_UCAST_NETWORK_PREFIX + ":0:0:0:1" +f"/{defines.IPV6_ADDRESS_PREFIX_LEN}" # From the RPL standard: The DODAGID is a Global or Unique Local IPv6 address of the root.
                                                                                                            # we simply assign the root the imaginary global unicast address 2001:db8:0:1::1 (sunbet is 1, interface is 1)
    dodag_version = 1 # arbitrarily chosen 

    # Setup simulation
    env = simpy.Environment()
    nw = Network(env)

    nw.generate_nodes_and_edges(defines.NUMBER_OF_NODES, defines.RADIUS)
    nw.plot_network()

    nw.register_node_processes(env)
    nw.construct_new_dodag(rpl_instance, dodag_id, dodag_version)

    # Execute simulation

    env.process(nw.at_interval_plot(rpl_instance, dodag_id, dodag_version,1000))
    env.run(until=defines.SIM_TIME) 

    nw.print_resulting_routing_tables(rpl_instance, dodag_id, dodag_version)
    #nw.plot_resulting_dodag(rpl_instance, dodag_id, dodag_version)

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


if __name__ == '__main__':
    main()