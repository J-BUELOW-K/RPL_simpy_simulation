import math








ROOT_RANK = 0
MAX_RANK = 0xFFFF






def dag_rank_macro(rank: float, MinHopRankIncrease: float) -> int: # Returns Interger part of rank. see sec 3.5.1 in RPL standard for more info
    return math.floor(rank/MinHopRankIncrease)
    






class Dodag:

    def __init__(self, dodag_id, dodag_version_num, is_root = False):
        self.dodag_id = dodag_id
        self.dodag_version_num = dodag_version_num

        if is_root:
            self.rank = ROOT_RANK
        else:
            self.rank = MAX_RANK
        self.rank 

        # TODO der skal måske være noget herinde til at holde alt dodag info fra de andre nodes (info man får i DIO beskederne)(en liste)

    def set_rank(self, rank):
        self.rank = rank

    # er ikker sikker på om vi skal bruge float rank eller DAGRank() (interger part) her







class Rpl_Instance:

    def __init__(self, rpl_instance_id):
        self.rpl_instance_id = rpl_instance_id
        self.dodag_list = []

    def add_dodag(self, dodag: Dodag):
        self.dodag_list.append(dodag)