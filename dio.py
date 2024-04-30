


class dio_packet:
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

    def __init__(self, RPL_Instance_ID, version_Number, rank, grouped, mop, prf, dtsn, flags, dodag_id):

        self.RPL_Instance_ID = RPL_Instance_ID 
        self.version_Number = version_Number          
        self.rank = rank                    
        self.grouped = grouped
        self.mop = mop
        self.prf = prf
        self.dtsn = dtsn
        self.flags = flags
        self.dodag_id = dodag_id

