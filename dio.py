
# Based on RFC6550 - https://datatracker.ietf.org/doc/html/rfc6550#section-6.3 

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

    # Options has been omitted

    def __init__(self, rpl_instance_id = 0, version = 0, rank = 0, g = False, mop = 0,\
                 prf = None, dtsn = None, flags = 0, reserved = 0, dodag_id = 0):

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
        