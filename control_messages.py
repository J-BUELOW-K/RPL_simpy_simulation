
import defines


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
    #        |   Option(s)...
    #        +-+-+-+-+-+-+-+-+


    def __init__(self, rpl_instance_id = 0, k = False, d = False, flags = 0,\
                 reserved = 0, dao_sequence = 0, dodag_id = None, options = None):
        
        self.rpl_instance_id = rpl_instance_id      # Topology instance associated with the DODAG, as learned from the DIO.
        self.k = k                                  # The 'K' flag indicates that the recipient is expected to send a DAO-ACK back.
        self.d = d                                  # The 'D' flag indicates that the DODAGID field is present. This
                                                    # flag MUST be set when a local RPLInstanceID is used.
        self.flags = flags                          # We can ignore this one for now. MUST be set to 0 by sender and ignored by receiver.
        self.reserved = reserved                    # MUST be set to 0 by the sender and ignored by the receiver.
        self.dao_sequence = dao_sequence            # Incremented at each unique DAO message from a node and echoed in the DAO-ACK message.
        self.dodag_id = dodag_id                    # Unsigned integer set by a DODAG root that uniquely identifies a DODAG. This field is only
                                                    # present when the 'D' flag is set.
        self.options = options                      # The DIO message MAY carry valid options. Refer RFC6550 section 6.4.3 for valid options.
        
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
    #    |   Option(s)...
    #    +-+-+-+-+-+-+-+-+

    def __init__(self, rpl_instance_id = 0, d = False, reserved = 0,\
                 dao_sequence = 0, status = None, dodag_id = None, options = None):
        
        self.rpl_instance_id = rpl_instance_id      # Topology instance associated with the DODAG, as learned from the DIO.
        self.d = d                                  # The 'D' flag indicates that the DODAGID field is present. This
                                                    # flag MUST be set when a local RPLInstanceID is used.
        self.reserved = reserved                    # Reserved for flags. We can ignore this one for now.
        self.dao_sequence = dao_sequence            # Incremented at each DAO message from a node, and echoed in the DAO-ACK 
                                                    # by the recipient. The DAOSequence is used to correlate a DAO message and a DAO ACK message
        self.status = status                        # Status 0: Unqualified acceptance (i.e., the node receiving the DAO-ACK is not rejected).
        self.dodag_id = dodag_id                    # Unsigned integer set by a DODAG root that uniquely identifies a DODAG. This field is only
                                                    # present when the 'D' flag is set.
        self.options = options                      # The DIO message MAY carry valid options. Refer RFC6550 section 6.5.3 for valid options.

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



class DIO_message:

    """DODAG Information Object (DIO)""" 

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
    #    |   Option(s)...
    #    +-+-+-+-+-+-+-+-+

    def __init__(self, rpl_instance_id = 0, version = 0, rank = 0, g = False, mop = 0,\
                 prf = None, dtsn = None, flags = 0, reserved = 0, dodag_id = 0, options = None):

        self.rpl_instance_id = rpl_instance_id      # Set by the DODAG root and indicate which RPL Instance the DODAG is a part of.
        self.version = version                      # Unsigned integer set by the DODAG root to the DODAGVersionNumber           
        self.rank = rank                            # Unsigned integer indicating the DODAG Rank of the node sending the DIO message
        self.g = g                                  # The Grounded 'G' flag indicates whether the DODAG advertised can satisfy the 
                                                    # application-defined goal. If the flag is set, the DODAG is grounded. If the 
                                                    # flag is cleared, the DODAG is floating.
        self.mop = mop                              # The Mode of Operation (MOP) field identifies the mode of operation of the RPL 
                                                    # Instance as administratively provisioned at and distributed by the DODAG root.  
                                                    # All nodes who join the DODAG must be able to honor the MOP in order to fully 
                                                    # participate as a router, or else they must only join as a leaf.
        self.prf = prf                              # DODAGPreference (Prf): A 3-bit unsigned integer that defines how preferable the
                                                    # root of this DODAG is compared to other DODAG roots within the instance
        self.dtsn = dtsn                            # Unsigned integer set by the node issuing the DIO message
        self.flags = flags                          # MUST be set to 0 by sender and ignored by receiver. 
        self.reserved = reserved                    # MUST be set to 0 by sender and ignored by receiver.
        self.dodag_id = dodag_id                    # IPv6 address set by a DODAG root that uniquely identifies a DODAG. The DODAGID 
                                                    # MUST be a routable IPv6 address belonging to the DODAG root.
        self.options = options                      # The DIO message MAY carry valid options. Refer RFC6550 section 6.3.3 for valid options.

        self.__self_check()

    def __self_check(self):
        
        if self.version < 0:
            raise ValueError("Version number MUST be an unsigned interger.")
        if self.rank < 0:
            raise ValueError("Rank MUST be an unsigned interger.")
        if self.prf is not None and self.prf < 0:
            raise ValueError("prf MUST be an unsigned interger.")
        if self.dtsn is not None and self.dtsn < 0:
            raise ValueError("DTSN MUST be an unsigned interger.")        


class message:

    def __init__(self, code):
        
        self.code = code
        self.dio = None
        self.dao = None
        self.dao_ack = None

    def dis(self):
        pass

    def define_dio(self, rpl_instance_id = 0, version = 0, rank = 0, g = False, mop = 0,\
                 prf = None, dtsn = None, flags = 0, reserved = 0, dodag_id = 0, options = None):
        
        if not (self.code == defines.CODE_DIO):
            raise ValueError("Incorrect message code. MUST be a DIO message")

        self.dio = DIO_message(rpl_instance_id, version, rank, g, mop,\
                               prf, dtsn, flags, reserved, dodag_id, options)

    def define_dao(self,rpl_instance_id = 0, k = False, d = False, flags = 0,\
                 reserved = 0, dao_sequence = 0, dodag_id = None, options = None):

        if not (self.code == defines.CODE_DAO):
            raise ValueError("Incorrect message code. MUST be a DAO message")

        self.dao = DAO_message(rpl_instance_id, k, d, flags,\
                               reserved, dao_sequence, dodag_id, options)

    def define_dao_ack(self, rpl_instance_id = 0, d = False, reserved = 0,\
                 dao_sequence = 0, status = None, dodag_id = None, options = None):

        if not (self.code == defines.CODE_DAO_ACK):
            raise ValueError("Incorrect message code. MUST be a DAO ACK message")

        self.dao_ack = DAO_ACK_message(rpl_instance_id, d, reserved,\
                                   dao_sequence, status, dodag_id, options)
        

if __name__ == "__main__":
    message_dio = message(defines.CODE_DIO)

    message_dio.dio(rpl_instance_id = 1, version = 2, rank = 3, g = True, mop = 34,\
            prf = 1, dtsn = 1, flags = 2, reserved = 31, dodag_id = 242134, options = 24)

    print(message_dio.msg.version)

    print("Hello world!")