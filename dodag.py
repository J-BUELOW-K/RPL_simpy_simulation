import math
#import time

import control_messages
import defines
from defines import METRIC_OBJECT_TYPE, METRIC_OBJECT_NONE, METRIC_OBJECT_HOPCOUNT, METRIC_OBJECT_ETX

# def dag_rank_macro(rank: float, MinHopRankIncrease: float) -> int: # Returns Interger part of rank. see sec 3.5.1 in RPL standard for more info
#     return math.floor(rank/MinHopRankIncrease)
    






class Dodag:

    def __init__(self, dodag_id, dodag_version_num, is_root = False):  # , MinHopRankIncrease = 256.0):
        self.dodag_id = dodag_id # 0
        self.dodag_version_num = dodag_version_num # 0
        #self.MinHopRankIncrease = MinHopRankIncrease # 256.0
        # self.last_dio = time.time() # TODO skal være en timestamp. DET SKAL NOK VÆRE EN SIMPY TIME! IKKE "time" TIME env.now er en ting
        self.prefered_parent = None # node_id of prefered parent
        self.prefered_parent_rank = defines.INFINITE_RANK

        self.metric_object = None
        if METRIC_OBJECT_TYPE == METRIC_OBJECT_HOPCOUNT:
            self.metric_object = control_messages.HP_OBJ(defines.INFINITE_HOP_COUNT)
        elif METRIC_OBJECT_TYPE == METRIC_OBJECT_ETX:
            self.metric_object = control_messages.ETX_OBJ(defines.INFINITE_CUMULATIVE_ETX)


        if is_root:
            self.rank = defines.ROOT_RANK
        else:
            self.rank = defines.INFINITE_RANK
        self.rank 

        # TODO der skal måske være noget herinde til at holde alt dodag info fra de andre nodes (info man får i DIO beskederne)(en liste)

    # def set_rank(self, rank):
    #     self.rank = rank
        
        
    # def set_prefered_parent(self, parent):
    #     ...
        
    # def DAGRank(self, rank):
    #     return math.floor(float(rank)/ self.MinHopRankIncrease) # Returns Interger part of rank. see sec 3.5.1 in RPL standard for more info

    # er ikker sikker på om vi skal bruge float rank eller DAGRank() (interger part) her







class Rpl_Instance:

    def __init__(self, rpl_instance_id):
        self.rpl_instance_id = rpl_instance_id
        self.dodag_list = []

    def add_dodag(self, dodag: Dodag):
        self.dodag_list.append(dodag)