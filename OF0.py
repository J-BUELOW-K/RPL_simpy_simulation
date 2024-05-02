# TODO i OF0 "Selection of the Preferred Parent" Step 1, nævner de at en nabo skal overholder alle steps fra 8.2.1 i RPL standarden, før den overhoevedet kan overvejes i OF0.


# The Routing Protocol for Low-Power and Lossy Networks (RPL)
# specification [RFC6550] defines a generic Distance Vector protocol
# that is adapted to a variety of Low-Power and Lossy Network (LLN)
# types by the application of specific Objective Functions (OFs).

# A RPL OF states the outcome of the process used by a RPL node to
# select and optimize routes within a RPL Instance based on the
# Information Objects available.  As a general concept, an OF is not an
# algorithm.  For example, outside RPL, "shortest path first" is an OF
# where the least cost path between two points is derived as an
# outcome; there are a number of algorithms that can be used to satisfy
# the OF, of which the well-known Dijkstra algorithm is an example.

# The separation of OFs from the core protocol specification allows RPL
# to be adapted to meet the different optimization criteria required by
# the wide range of deployments, applications, and network designs.




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
    
    
    def compute_rank_increase(self, parent_rank:int=0):
        # The step_of_rank Sp that is computed for that link is multiplied by
        # the rank_factor Rf and then possibly stretched by a term Sr that is
        # less than or equal to the configured stretch_of_rank.  The resulting
        # rank_increase is added to the Rank of preferred parent R(P) to obtain
        # that of this node R(N):
        
            # R(N) = R(P) + rank_increase where:

            # rank_increase = (Rf*Sp + Sr) * MinHopRankIncrease
        
        rank_increase = (self.rank_factor * self.step_of_rank + self.stretch_of_rank) * self.MinHopRankIncrease
        if parent_rank+rank_increase > INFINITE_RANK:
            return INFINITE_RANK
        else:
            return parent_rank+rank_increase
        
        
        
        ...
        
    def compute_preferred_parent(self, neighbors:list, parent:dict):
        
        # The parent that is selected as the preferred parent is the one that has the lowest rank among all the neighbors that have been heard within the last DIOInterval.
        # If there is a tie, the parent with the lowest MAC address is selected.
        # If the node has no neighbors that have been heard within the last DIOInterval, the node MUST select the DODAG root as the preferred parent.
        

        
        # The node MUST NOT select a parent that is not in the list of neighbors that have been heard within the last DIOInterval.
        
        
        
        ...
        
    def compare_parent(self, parent_1, parent_2):
        # The parent that is selected as the preferred parent is the one that has the lowest rank among all the neighbors that have been heard within the last DIOInterval.
        
        rank1 = parent_1.compute_rank_increase(parent_1["rank"])
        rank2 = parent_2.compute_rank_increase(parent_2["rank"])
        
        if 
        
        
        ...
        
    def compute_backup_parent(self):
        ...