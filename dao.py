

class DAO_message:

    """DODAG Information Object (DIO)"""

    #         0                   1                   2                   3
    #         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #        | RPLInstanceID |K|D|   Flags   |   Reserved    | DAOSequence   |
    #        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #        |                                                               |
    #        +                                                               +
    #        |                                                               |
    #        +                            DODAGID*                           +
    #        |                                                               |
    #        +                                                               +
    #        |                                                               |
    #        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    # Options bit field has been omitted.

    def __init__(self, rpl_instance_id = 0, k = 0, d = 0, flags = 0,\
                 reserved = 0, dao_sequence = 0, dodag_id = 0):
        
        self.rpl_instance_id = rpl_instance_id 
        self.k = k
        self.d = d
        self.flags = flags
        self.reserved = reserved
        self.dao_sequence = dao_sequence
        self.dodag_id = dodag_id


class DAO_ACK_message:

    """Destination Advertisement Object Acknowledgement"""

    #     0                   1                   2                   3
    #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    | RPLInstanceID |D|  Reserved   |  DAOSequence  |    Status     |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |                                                               |
    #    +                                                               +
    #    |                                                               |
    #    +                            DODAGID*                           +
    #    |                                                               |
    #    +                                                               +
    #    |                                                               |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    # Options bit field has been omitted.

    def __init__(self, rpl_instance_id = 0, d = 0, reserved = 0,\
                 dao_sequence = 0, status = 0, dodag_id = 0):
        
        self.rpl_instance_id = rpl_instance_id
        self.d = d
        self.reserved = reserved
        self.dao_sequence = dao_sequence
        self.status = status
        self.dodag_id = dodag_id