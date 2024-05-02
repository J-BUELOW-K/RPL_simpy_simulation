import network
import math

from dodag import Dodag
import defines
from defines import METRIC_OBJECT_TYPE, METRIC_OBJECT_NONE, METRIC_OBJECT_HOPCOUNT, METRIC_OBJECT_ETX
from network import Node


# # Objective Code Point
# OCP = 0

def DAGRank(rank):
    return math.floor(float(rank) / defines.DEFAULT_MIN_HOP_RANK_INCREASE) # Returns Interger part of rank. see sec 3.5.1 in RPL standard for more info

# MAX_ETX = network.estimate_etx(defines.RADIUS,'fspl')


# class OF0:
#     def __init__(self, default:bool=True, config_dict:dict=None) -> None:
#         if default:
#             self.rank_factor = DEFAULT_RANK_FACTOR
#             self.stretch_of_rank = DEFAULT_RANK_STRETCH
#             self.step_of_rank = DEFAULT_STEP_OF_RANK
#             self.MinHopRankIncrease = 256
#         else:
#             self.rank_factor = config_dict["rank_factor"]
#             self.stretch_of_rank = config_dict["stretch_of_rank"]
#             self.step_of_rank = config_dict["step_of_rank"]
#             self.MinHopRankIncrease = config_dict["MinHopRankIncrease"]
#         pass
    
    
#def of0_compute_rank(dodag, parent_rank, metric_object = None, metric_object_type = None):
def of0_compute_rank(parent_rank, metric_object = None):  
    # note, metric_object is the full metric_object all the way from the node to the root
    # The step_of_rank Sp that is computed for that link is multiplied by
    # the rank_factor Rf and then possibly stretched by a term Sr that is
    # less than or equal to the configured stretch_of_rank.  The resulting
    # rank_increase is added to the Rank of preferred parent R(P) to obtain
    # that of this node R(N):
    
        # R(N) = R(P) + rank_increase where:

        # rank_increase = (Rf*Sp + Sr) * MinHopRankIncrease
        
        #define STEP_OF_RANK(p)       (((3 * parent_link_metric(p)) / LINK_STATS_ETX_DIVISOR) - 2)
        
    # if OF0 == 'ETX':
    #     step_of_rank = (((3 * etx) / LINK_STATS_ETX_DIVISOR) - 2)

    # UDREGNE STEP OF RANK. ENTEN VED BRUG AF DEFAULT step_of_rank (hvis der ingen metric object gives), eller "HP" eller "ETX"
    
    # rank_increase = (DEFAULT_RANK_FACTOR * DEFAULT_STEP_OF_RANK + DEFAULT_RANK_STRETCH) * dodag.MinHopRankIncrease
    # if parent_rank+rank_increase > INFINITE_RANK:
    #     return INFINITE_RANK
    # else:
    #     return parent_rank+rank_increase
        
    
    if METRIC_OBJECT_TYPE == METRIC_OBJECT_NONE:
        pass # TODO BRUG KUN DEFAULT VÆRDIER
        rank_increase = (defines.DEFAULT_RANK_FACTOR*defines.DEFAULT_STEP_OF_RANK) * defines.DEFAULT_MIN_HOP_RANK_INCREASE
    elif METRIC_OBJECT_TYPE == METRIC_OBJECT_HOPCOUNT:
        pass # TODO map hop count til STEP_OF_RANK mellem 1 og 9 
    elif METRIC_OBJECT_TYPE == METRIC_OBJECT_ETX:
        pass # TODO map ETX til STEP_OF_RANK mellem 1 og 9
    else:
        pass # TODO lav error med invalid param

    return parent_rank + rank_increase    

        

            
    
    
    

    
#def of0_compare_parent(current_parent: Node, challenger_parent: Node, ICMP_DIO, metric_object_to_challenger = None, metric_object_type = None):
def of0_compare_parent(current_parent_rank, challenger_parent_rank, metric_object_through_current_parrent = None, metric_object_through_challenger = None):
    # note, "parent" in parameter names means "prefered parent"


    rank_through_current_parent = of0_compute_rank(current_parent_rank, metric_object_through_current_parrent)
    rank_through_challenger_parent = of0_compute_rank(challenger_parent_rank, metric_object_through_challenger)

    if DAGRank(rank_through_challenger_parent) > DAGRank(rank_through_current_parent):    # only choose challenger parent as new prefered parent IF it results in a better DAGRank (if equal, keep current parent)
        # note, DAGRank() is used when comparing ranks (see RPL standard)
        return "update parent", DAGRank(rank_through_challenger_parent)
    else:
        return "keep parent", DAGRank(rank_through_current_parent)

    # rank1 = of0_compute_rank(parent_1.dodag, parent_1.dodag.rank)
    # rank2 = of0_compute_rank(parent_2.dodag, parent_2.dodag.rank)



    
    # if (parent_1.dodag.DAGRank(rank1) != parent_2.dodag.DAGRank(rank2)): # step 8 in RFC 6552
    #     return rank1 - rank2
    
    # # a preferred parent should stay preferred. Step 10 in RFC 6552
    # if parent_1.preferred:
    #     return -1

    # if parent_2.preferred:
    #     return 1
    
    # router that has announced a DIO message more recently should be
    # preferred
    #return parent_2.dodag.last_dio - parent_1.dodag.last_dio # step 11 in RFC 6552
    ...
        












# def of0_compute_preferred_parent(dodag, neighbors:list):
    
#     # The parent that is selected as the preferred parent is the one that has the lowest rank among all the neighbors that have been heard within the last DIOInterval.
#     for neighbor in neighbors:
#         out = []
#         for i in range(1, len(neighbors)):
#             out.append(of0_compare_parent(neighbor, neighbors[i]))

# class node_tester():
    
#     def __init__(self, dodag) -> None:
#         self.dodag = dodag
#         self.preferred = False
#         self.rank = 0
#         self.G = False
#         self.Prf = 0
#         self.last_dio = 0
    
# if __name__ == "__main__":
    
    
#     d1 = Dodag(dodag_id=1, dodag_version_num=1, is_root=False)
#     n1 = node_tester(d1)
#     d2 = Dodag(dodag_id=1, dodag_version_num=1, is_root=False)
#     n2 = node_tester(d2)
#     d3 = Dodag(dodag_id=1, dodag_version_num=1, is_root=False)
#     n3 = node_tester(d3)
    
    
#     n1_neighbors = [n2, n3]

    
#     of0_compute_preferred_parent(n1, n1_neighbors)
    