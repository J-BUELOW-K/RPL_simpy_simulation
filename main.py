import simpy
from network import *
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

    # Generate network and construct new dodag
    nw.generate_nodes_and_edges(defines.NUMBER_OF_NODES, defines.RADIUS)#,seed=4242424)
    nw.register_node_processes(env)
    nw.construct_new_dodag(rpl_instance, dodag_id, dodag_version)

    # Execute simulation:
    env.run(until=defines.SIM_TIME) 

    # Print Result:
    nw.plot_network_and_dodag(rpl_instance, dodag_id, dodag_version, save = True)
    nw.print_resulting_routing_tables(rpl_instance, dodag_id, dodag_version)



if __name__ == '__main__':
    main()