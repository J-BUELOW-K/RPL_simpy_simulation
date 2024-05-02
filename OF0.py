from dodag import Dodag
import network
import defines



# Objective Code Point
OCP = 0

# Constants (as defined in Section 6.3)
DEFAULT_STEP_OF_RANK = 3
MINIMUM_STEP_OF_RANK = 1
MAXIMUM_STEP_OF_RANK = 9
DEFAULT_RANK_STRETCH = 0
MAXIMUM_RANK_STRETCH = 5
DEFAULT_RANK_FACTOR  = 1
MINIMUM_RANK_FACTOR  = 1
MAXIMUM_RANK_FACTOR  = 4

MAX_ETX = network.estimate_etx(defines.RADIUS,'fspl')
DEFAULT_MIN_HOP_RANK_INCREASE = 256

# constant maximum for the Rank
INFINITE_RANK = 0xffff

class OF0:
    def __init__(self, default:bool=True, config_dict:dict=None) -> None:
        if default:
            self.rank_factor = DEFAULT_RANK_FACTOR
            self.stretch_of_rank = DEFAULT_RANK_STRETCH
            self.step_of_rank = DEFAULT_STEP_OF_RANK
            self.MinHopRankIncrease = 256
        else:
            self.rank_factor = config_dict["rank_factor"]
            self.stretch_of_rank = config_dict["stretch_of_rank"]
            self.step_of_rank = config_dict["step_of_rank"]
            self.MinHopRankIncrease = config_dict["MinHopRankIncrease"]
        pass
    
    
def compute_rank_increase(dodag, parent_rank:int=0, OF0:str='ETX'):
    # The step_of_rank Sp that is computed for that link is multiplied by
    # the rank_factor Rf and then possibly stretched by a term Sr that is
    # less than or equal to the configured stretch_of_rank.  The resulting
    # rank_increase is added to the Rank of preferred parent R(P) to obtain
    # that of this node R(N):
    
        # R(N) = R(P) + rank_increase where:

        # rank_increase = (Rf*Sp + Sr) * MinHopRankIncrease
        
        #define STEP_OF_RANK(p)       (((3 * parent_link_metric(p)) / LINK_STATS_ETX_DIVISOR) - 2)
        
    if OF0 == 'ETX':
        step_of_rank = (((3 * dodag.) / LINK_STATS_ETX_DIVISOR) - 2)
    
    rank_increase = (DEFAULT_RANK_FACTOR * DEFAULT_STEP_OF_RANK + DEFAULT_RANK_STRETCH) * dodag.MinHopRankIncrease
    if parent_rank+rank_increase > INFINITE_RANK:
        return INFINITE_RANK
    else:
        return parent_rank+rank_increase
        
        
        
        ...
        
def compute_preferred_parent(dodag, neighbors:list):
    
    # The parent that is selected as the preferred parent is the one that has the lowest rank among all the neighbors that have been heard within the last DIOInterval.
    for neighbor in neighbors:
        out = []
        for i in range(1, len(neighbors)):
            out.append(compare_parent(neighbor, neighbors[i]))
            
    
    
    
    ...
    
def compare_parent(parent_1:object, parent_2:object):
    # The parent that is selected as the preferred parent is the one that has the lowest rank among all the neighbors that have been heard within the last DIOInterval.
    
    # comparison only make sense within the same RPL instance
    if parent_1.dodag.dodag_id != parent_2.dodag.dodag_id:
        raise NotImplementedError("current implementation only support a single RPL instance")
    
    # over two grounded DODAG, select the one with the best administrative preference
    # if (parent_1.dodag.G and parent_2.dodag.G):
    #     if parent_1.dodag.Prf != parent_2.dodag.Prf:
    #         return parent_2.dodag.Prf - parent_1.dodag.Prf
        
        # prefer grounded DODAG over a floating one
    # if (not parent_1.dodag.G and parent_2.dodag.G):
    #     return 1  # parent 2
    # if (not parent_2.dodag.G and parent_1.dodag.G):
    #     return -1 # parent 1
    
    rank1 = compute_rank_increase(parent_1.dodag, parent_1.dodag.rank)
    rank2 = compute_rank_increase(parent_2.dodag, parent_2.dodag.rank)

    
    if (parent_1.dodag.DAGRank(rank1) != parent_2.dodag.DAGRank(rank2)): # step 8 in RFC 6552
        return rank1 - rank2
    
    # a preferred parent should stay preferred. Step 10 in RFC 6552
    if parent_1.preferred:
        return -1

    if parent_2.preferred:
        return 1
    
    # router that has announced a DIO message more recently should be
    # preferred
    return parent_2.dodag.last_dio - parent_1.dodag.last_dio # step 11 in RFC 6552
    ...
        
class node_tester():
    
    def __init__(self, dodag) -> None:
        self.dodag = dodag
        self.preferred = False
        self.rank = 0
        self.G = False
        self.Prf = 0
        self.last_dio = 0
    
if __name__ == "__main__":
    
    
    d1 = Dodag(dodag_id=1, dodag_version_num=1, is_root=False)
    n1 = node_tester(d1)
    d2 = Dodag(dodag_id=1, dodag_version_num=1, is_root=False)
    n2 = node_tester(d2)
    d3 = Dodag(dodag_id=1, dodag_version_num=1, is_root=False)
    n3 = node_tester(d3)
    
    
    n1_neighbors = [n2, n3]

    
    compute_preferred_parent(n1, n1_neighbors)
    