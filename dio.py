
import random
import numpy as np
import simpy



class dio_message:
    # DIO messages used to advertise a DODAG and its characteristics

    # Format of the DIO Base Object

    #     0                   1                   2                   3
    #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    | RPLInstanceID |Version Number |             Rank              |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |G|0| MOP | Prf |     DTSN      |     Flags     |   Reserved    |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |                                                               |
    #    +                                                               +
    #    |                                                               |
    #    +                            DODAGID                            +
    #    |                                                               |
    #    +                                                               +
    #    |                                                               |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    # Options has been omitted

    def __init__(self, RPLInstanceID, versionNumber, rank, grouped, mop, prf, dtsn, flags, dodagid):

        self.RPLInstanceID = RPLInstanceID 
        self.versionNumber = versionNumber          
        self.rank = rank                    # DAGRank
        self.grouped = grouped
        self.mop = mop
        self.prf = prf
        self.dtsn = dtsn
        self.flags = flags
        self.dodagid = dodagid



class dio:
    
    pass
