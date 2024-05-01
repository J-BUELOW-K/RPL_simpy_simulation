
# Based on RFC6550 - https://datatracker.ietf.org/doc/html/rfc6550#section-6.4

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

    def __init__(self, rpl_instance_id = 0, k = False, d = False, flags = 0,\
                 reserved = 0, dao_sequence = 0, dodag_id = None):
        
        self.rpl_instance_id = rpl_instance_id      # Topology instance associated with the DODAG, as learned from the DIO.
        self.k = k                                  # The 'K' flag indicates that the recipient is expected to send a DAO-ACK back.
        self.d = d                                  # The 'D' flag indicates that the DODAGID field is present. This
                                                    # flag MUST be set when a local RPLInstanceID is used.
        self.flags = flags                          # We can ignore this one for now. MUST be set to 0 by sender and ignored by receiver.
        self.reserved = reserved                    # MUST be set to 0 by the sender and ignored by the receiver.
        self.dao_sequence = dao_sequence            # Incremented at each unique DAO message from a node and echoed in the DAO-ACK message.
        self.dodag_id = dodag_id                    # Unsigned integer set by a DODAG root that uniquely identifies a DODAG. This field is only
                                                    # present when the 'D' flag is set.

        self.__self_check()

    def __self_check(self):

        if self.d:
            if self.dodag_id is None:
                raise ValueError("D is set but no DODAGID given.")
            if self.dodag_id < 0:
                raise ValueError("DODAGID MUST be an unsigned interger.")
        else:
            if self.dodag_id is not None:
                raise ValueError("D flag not set. MUST be set when DODAGID field is used.")


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

    def __init__(self, rpl_instance_id = 0, d = False, reserved = 0,\
                 dao_sequence = 0, status = 0, dodag_id = None):
        
        self.rpl_instance_id = rpl_instance_id      # Topology instance associated with the DODAG, as learned from the DIO.
        self.d = d                                  # The 'D' flag indicates that the DODAGID field is present. This
                                                    # flag MUST be set when a local RPLInstanceID is used.
        self.reserved = reserved                    # Reserved for flags. We can ignore this one for now.
        self.dao_sequence = dao_sequence            # Incremented at each DAO message from a node, and echoed in the DAO-ACK 
                                                    # by the recipient. The DAOSequence is used to correlate a DAO message and a DAO ACK message
        self.status = status                        # Status 0: Unqualified acceptance (i.e., the node receiving the DAO-ACK is not rejected).
        self.dodag_id = dodag_id                    # Unsigned integer set by a DODAG root that uniquely identifies a DODAG. This field is only
                                                    # present when the 'D' flag is set.
        
        self.__self_check()

    def __self_check(self):

        if self.d:
            if self.dodag_id is None:
                raise ValueError("D is set but no DODAGID given.")
            if self.dodag_id < 0:
                raise ValueError("DODAGID MUST be an unsigned interger.")
        else:
            if self.dodag_id is not None:
                raise ValueError("D flag not set. MUST be set when DODAGID field is used.")
            
