
import math

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from rich.console import Console
from rich.table import Table
from rich.terminal_theme import MONOKAI

import defines
from control_messages import *
from dodag import Dodag, Rpl_Instance
from node import Node

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
    
    
def find_dodag(rpl_instances: list, rpl_instance_id, dodag_id, dodag_version): # return index of dodag and/or rpl instance in list of rpl instances

    rpl_instance_idx = None
    dodag_list_idx = None

    # Find associated RPL Instance:
    for i in range(len(rpl_instances)):
        if rpl_instances[i].rpl_instance_id == rpl_instance_id:
            rpl_instance_idx = i
            break

    if rpl_instance_idx is not None: # If there exists an entry for the recieved RPL instance in self.rpl_instances!
        # Find associated Dodag:
        for i in range(len(rpl_instances[rpl_instance_idx].dodag_list)):
            temp_dodag = rpl_instances[rpl_instance_idx].dodag_list[i]
            if temp_dodag.dodag_id == dodag_id and temp_dodag.dodag_version_num == dodag_version: # Both ID and Version has to match!
                dodag_list_idx = i
                break

    return rpl_instance_idx, dodag_list_idx

        
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
        while(True):
            self.networkx_graph = nx.random_geometric_graph(number_of_nodes, radius, seed=seed) # seed is used to make the network deterministic
            if nx.is_connected(self.networkx_graph): 
                break #if graph is not connected, try again...

        # tranlate networkx nodes/edges to our own nodes/connections setup (to make them easier to work with):
        self.connections = [Connection(x[0],x[1]) for x in self.networkx_graph.edges()]
        # self.nodes = [Node(node_id = x) for x in self.networkx_graph.nodes()] # does not include position
        for node in self.networkx_graph.nodes(data="pos"):
            self.nodes.append(Node(self.env, self, node_id = node[0], xpos = node[1][0], ypos = node[1][1]))  # node format from networkx: (id, [xpos, ypos])
                                                                                              # note: node_id matches index in self.nodes array!

        # Estimate relative ETX values for each connection:
        for connection in self.connections:
            a = self.nodes[connection.from_node].xpos  # assumption: index in self.nodes array matches node_id
            b = self.nodes[connection.to_node].ypos    # assumption: index in self.nodes array matches node_id
            connection.distance = math.sqrt(a**2 + b**2) # pythagoras
            connection.etx_value = estimate_etx(connection.distance, "fspl")

        # Make all nodes aware of their neighbors:
        for connection in self.connections:
            # note: At network cration, connection/edges are NOT generated in both directions between nodes. Therefore, we inform both nodes in a connection about the neighboring node
            self.nodes[connection.from_node].add_to_neighbors_list(self.nodes[connection.to_node], connection)  # assumption: index in self.nodes array matches node_id
            self.nodes[connection.to_node].add_to_neighbors_list(self.nodes[connection.from_node], connection)  # assumption: index in self.nodes array matches node_id
        return number_of_nodes - 1
    
    def construct_new_dodag(self, rpl_instance_id, dodag_id, dodag_version, desired_root_node_id = None):

        # Pick Root Node:
        if desired_root_node_id == None:
            # pick root "by random" (we arbitrarily choose index 0, the indexes themselves are "randomly given" to nodes):
            root_node = self.nodes[0]
            pass
        else:
            # use the specified node as root
            root_node = self.nodes[desired_root_node_id] # assumption: index in self.nodes array matches node_id
        
        # Check if specified RPL instance/dodag already exists in root node:
        rpl_instance_idx, dodag_list_idx = find_dodag(root_node.rpl_instances, rpl_instance_id, dodag_id, dodag_version)
        if rpl_instance_idx != None:
            # RPL instance entry found in root node
            if dodag_list_idx != dodag_list_idx:
                print("ERROR: Identical DODAG entry already exists...")
                raise ValueError 
            else:
                # Create DODAG in root node, within the already existing RPL Instance
                new_dodag = Dodag(env = self.env, dodag_id= dodag_id, dodag_version_num= dodag_version, rank=defines.ROOT_RANK) # setting rank to 0 makes the node the root!
                root_node.rpl_instances[rpl_instance_idx].add_dodag(new_dodag)
        else:
            # No matching RPL entry exists in root node - create one! (including dodag):
            new_rpl_instance = Rpl_Instance(rpl_instance_id)
            new_dodag = Dodag(env=self.env, dodag_id=dodag_id, dodag_version_num=dodag_version, rank = defines.ROOT_RANK) # setting rank to 0 makes the node the root!
            new_rpl_instance.add_dodag(new_dodag)
            root_node.rpl_instances.append(new_rpl_instance)

        # initialize dodag formation:
        root_node.broadcast_all_dios()
        return root_node.node_id

    def register_node_processes(self, env):
        for node in self.nodes:
            env.process(node.rpl_process(env))
            env.process(node.recieve_process(env))
    
    def plot_network(self):
        poss = nx.get_node_attributes(self.networkx_graph, "pos") # pos is a dict
        color_map = ['tab:olive' if i == 0 else 'tab:blue' for i in range(len(self.networkx_graph.nodes()))]

        nx.draw_networkx_edges(self.networkx_graph, poss, node_size=defines.NETWORK_NODE_SIZE)
        nx.draw_networkx_nodes(self.networkx_graph, poss, node_size=defines.NETWORK_NODE_SIZE, node_color=color_map)

        plt.title("Network")
        plt.show()


    def plot_resulting_dodag(self, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version, nr = "", show = True, save = False): # input: rpl instance, dodag id og dodag version  

        if len(self.nodes) == 0:
            raise ValueError("No nodes in network")
        
        rpl_instances = self.nodes[0].rpl_instances
        rpl_instance_idx, dodag_list_idx = find_dodag(rpl_instances, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version) # return index of dodag and/or rpl instance in list of rpl instances
        if (rpl_instance_idx is None) or (dodag_list_idx is None):
            raise ValueError("No Dodag to print with the provided IDs and version.")

        # set up a list containing all edges.
        edges = []
        for node in self.nodes[1:]:
            child = node.node_id
            parent = node.rpl_instances[rpl_instance_idx].dodag_list[dodag_list_idx].prefered_parent
            edges.append((child, parent))
       
        # plot the DODAG using networkx and graphviz
        G = nx.DiGraph(edges)
        poss = graphviz_layout(G, prog="dot") 
        flipped_poss = {node: (x,-y) for (node, (x,y)) in poss.items()}

        color_map = []
        for nodex in G.nodes():
            for node in self.nodes:
                rank = node.rpl_instances[rpl_instance_idx].dodag_list[dodag_list_idx].rank
                if node.node_id == nodex:
                    if node.alive:
                        color_map.append('tab:olive' if rank == defines.ROOT_RANK else 'tab:blue')
                    else:
                        color_map.append('tab:red')

        nx.draw_networkx_edges(G, flipped_poss, node_size=defines.DODAG_NODE_SIZE)
        nx.draw_networkx_nodes(G, flipped_poss, node_size=defines.DODAG_NODE_SIZE, node_color=color_map)
        nx.draw_networkx_labels(G, flipped_poss, font_size=defines.LABLE_SIZE)


        # nx.draw(G, flipped_poss, with_labels = True, node_size=250, node_color=color_map, font_size=6, width=.7, arrowsize=7)
        
        plt.title("Dodag")
        if save is True:
            plt.savefig(f"Graph{nr}.jpg", format="JPG", dpi=200)
    
        if show is True:
            plt.show()
        else:
            plt.close()


    def plot_network_and_dodag(self, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version, nr = "", show = True, save = False):
        fig, axs = plt.subplots(1, 2, figsize=(15, 7))  # Create a figure and a set of subplots
        # Plot network
        poss = nx.get_node_attributes(self.networkx_graph, "pos") # pos is a dict
        color_map = ['tab:olive' if i == 0 else 'tab:red' if self.nodes[i].alive is False else 'tab:blue' for i in range(len(self.networkx_graph.nodes()))]
        nx.draw_networkx_edges(self.networkx_graph, poss, node_size=defines.NETWORK_NODE_SIZE, ax=axs[0])
        nx.draw_networkx_nodes(self.networkx_graph, poss, node_size=defines.NETWORK_NODE_SIZE, node_color=color_map, ax=axs[0])
        nx.draw_networkx_labels(self.networkx_graph, poss, font_size=defines.LABLE_SIZE, ax=axs[0])
        axs[0].set_title("Network")

        # Plot DODAG
        rpl_instances = self.nodes[0].rpl_instances
        rpl_instance_idx, dodag_list_idx = find_dodag(rpl_instances, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version)
        if (rpl_instance_idx == None) or (dodag_list_idx == None):
            raise ValueError("No Dodag to print with the provided IDs and version.")
        edges = []
        for node in self.nodes[1:]:
            child = node.node_id
            try:
                parent = node.rpl_instances[rpl_instance_idx].dodag_list[dodag_list_idx].prefered_parent
            except IndexError:
                parent = child
            edges.append((child, parent))
        G = nx.DiGraph((edges))
        poss = graphviz_layout(G, prog="dot") 
        flipped_poss = {node: (x,-y) for (node, (x,y)) in poss.items()}
        color_map = []
        edgde_alphas = []
        node_IDs = []
        for nodex in G.nodes():
            for node in self.nodes:
                try:
                    rank = node.rpl_instances[rpl_instance_idx].dodag_list[dodag_list_idx].rank
                    if node.node_id == nodex:
                        node_IDs.append(node.node_id)
                        if node.alive:
                            if rank == defines.ROOT_RANK:
                                color_map.append('tab:olive')
                            else:
                                color_map.append('tab:blue')
                                edgde_alphas.append(1)
                        else:
                            color_map.append('tab:red')
                            edgde_alphas.append(0)
                except IndexError:
                    pass
        nx.draw_networkx_edges(G, flipped_poss, node_size=defines.DODAG_NODE_SIZE, alpha=edgde_alphas, ax=axs[1])
        nx.draw_networkx_nodes(G, flipped_poss, node_size=defines.DODAG_NODE_SIZE, node_color=color_map, ax=axs[1])
        nx.draw_networkx_labels(G, flipped_poss, font_size=defines.LABLE_SIZE, ax=axs[1])
        axs[1].set_title("Dodag")

        if save is True:
            plt.savefig(f"CombinedGraph{nr}.jpg", format="JPG", dpi=200)

        if show is True:
            plt.show()
    

    def ipv6_addr_2_node_id(self, ipv6_address: str) -> int:
        for node in self.nodes:
            if node.ipv6_address == ipv6_address:
                return node.node_id
        return None

    # prints routing tabels for all nodes in the network (in the specified dodag) to a .txt file
    def print_resulting_routing_tables(self, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version, file_name = "routing_tables.txt"): 

        with open(file_name, "wt") as report_file:
            console = Console(file=report_file)

            for node in self.nodes:

#                table = Table(show_header=True, header_style="bold dark_orange3", show_lines=True)
                table = Table(show_header=True, header_style="bold dark_orange3") # (header_style dosent work when saving to txt file)

                rpl_instance_idx, dodag_list_idx = find_dodag(node.rpl_instances, arg_rpl_instance_id, arg_dodag_id, arg_dodag_version)
                if (rpl_instance_idx == None) or (dodag_list_idx == None):
                    raise ValueError("No Dodag to print with the provided IDs and version.")
                intance_reference = node.rpl_instances[rpl_instance_idx]
                dodag_reference = intance_reference.dodag_list[dodag_list_idx]

                table.add_column(f"Node ID: {node.node_id}", style="dim", width=12)
                table.add_column("Dest. (IPv6)", justify="left")
                table.add_column("Dest. (ID)", justify="left")
                table.add_column("Next Hop (IPv6)", justify="left")
                table.add_column("Next Hop (ID)", justify="left")
                for dest_ipv6_address in dodag_reference.downward_routes.keys():
                    table.add_row(
                        "", 
                        str(dest_ipv6_address).upper() + "/" + str(defines.IPV6_ADDRESS_PREFIX_LEN), 
                        str(self.ipv6_addr_2_node_id(dest_ipv6_address)),  
                        str(dodag_reference.downward_routes[dest_ipv6_address]).upper() + "/" + str(defines.IPV6_ADDRESS_PREFIX_LEN),
                        str(self.ipv6_addr_2_node_id(dodag_reference.downward_routes[dest_ipv6_address])),  
                    )
                console.print(table)
