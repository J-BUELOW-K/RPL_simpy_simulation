import simpy
from network import *
import defines



def main():
    convergence_time = []
    nr_of_runs = 100
    for i in range(nr_of_runs):
        print("hello world")

        rpl_instance = 1  # arbitrarily chosen 
        dodag_id = defines.IPV6_GLOBAL_UCAST_NETWORK_PREFIX + ":0:0:0:1" +f"/{defines.IPV6_ADDRESS_PREFIX_LEN}" # From the RPL standard: The DODAGID is a Global or Unique Local IPv6 address of the root.
                                                                                                                # we simply assign the root the imaginary global unicast address 2001:db8:0:1::1 (sunbet is 1, interface is 1)
        dodag_version = 1 # arbitrarily chosen 

        # Setup simulation
        env = simpy.Environment()
        nw = Network(env)
        env.process(nw.log_dodag_information(env, rpl_instance, dodag_id, dodag_version))
        # Generate network and construct new dodag
        nw.generate_nodes_and_edges(defines.NUMBER_OF_NODES, defines.RADIUS)#,seed=4242424)
        nw.register_node_processes(env)
        
        nw.construct_new_dodag(rpl_instance, dodag_id, dodag_version)
        
        

        # Execute simulation:
        env.run(until=defines.SIM_TIME) 

        # Print Result:
        nw.plot_network_and_dodag(rpl_instance, dodag_id, dodag_version, show=False, save = True)
        nw.print_resulting_routing_tables(rpl_instance, dodag_id, dodag_version)
        convergence_time.append(nw.plot_dodag_inclusion(False))

    nw.plot_network_and_dodag(rpl_instance, dodag_id, dodag_version, show=True, save = True)
    nw.print_resulting_routing_tables(rpl_instance, dodag_id, dodag_version)
    nw.plot_dodag_inclusion(True)
    nw.plot_convergence_time(convergence_time, nr_of_runs)

if __name__ == '__main__':
    main()