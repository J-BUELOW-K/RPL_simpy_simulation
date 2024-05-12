
import defines

""" DAO Option - RPL Target """

    #     0                   1                   2                   3
    #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |   Type = 0x05 | Option Length |     Flags     | Prefix Length |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |                                                               |
    #    +                                                               +
    #    |                Target Prefix (Variable Length)                |
    #    .                                                               .
    #    .                                                               .
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


class RPL_target:
    def __init__(self, target_prefix, prefix_len):
        self.option_type = 0x05
        self.prefix_len = prefix_len
        self.target_prefix = target_prefix  # identifying an IPv6 destination address. 
                                   # The bits in the prefix after the prefix length (if any) are
                                   # reserved and MUST be set to zero on transmission and MUST be
                                   # ignored on receipt.



""" ICMP header implementation """

class ICMP_header:

    """ICMP "header" only"""

    def __init__(self, type, code):
        
    #     0                   1                   2                   3
    #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |     Type      |     Code      |          Checksum             |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |                                                               |
    #    .                             Base                              .
    #    .                                                               .
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |                                                               |
    #    .                           Option(s)                           .
    #    .                                                               .
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    # Source: rfc6550

        self.type = type
        self.code = code

        # Checksum and options not included. Base field is implemented at a higher level.
        # Refer https://datatracker.ietf.org/doc/html/rfc6550#section-6



""" DIS, DIO, DAO and DAO ACK body implementations """

class DIO:

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

    # Options field is implemented in the ICMP_DIO

    def __init__(self, rpl_instance_id: int, vers: int, rank: int, dodag_id: int):

        self.rpl_instance_id = rpl_instance_id      # Set by the DODAG root and indicate which RPL Instance the DODAG is a part of.
        self.vers = vers                            # Unsigned integer set by the DODAG root to the DODAGVersionNumber           
        self.rank = rank                            # Unsigned integer indicating the DODAG Rank of the node sending the DIO message
        self.dodag_id = dodag_id                    # IPv6 address set by a DODAG root that uniquely identifies a DODAG. The DODAGID 
                                                    # MUST be a routable IPv6 address belonging to the DODAG root.
        
        self.__self_check()

    def __self_check(self):
        
        if self.vers < 0:
            raise ValueError("Version MUST be an unsigned int")
        if self.rank < 0:
            raise ValueError("Rank MUST be an unsigned int")

        # Unused field has been omitted.
        # Reference: https://datatracker.ietf.org/doc/html/rfc6550#section-6.3


class DAO:

    """DODAG Information Object (DAO)"""

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


    def __init__(self, rpl_instance_id, dodag_id, dodag_version, dao_sequence = 0):
        
        self.rpl_instance_id = rpl_instance_id      # Topology instance associated with the DODAG, as learned from the DIO.
        self.dao_sequence = dao_sequence            # Incremented at each unique DAO message from a node.
        self.dodag_id = dodag_id                    # Unsigned integer set by a DODAG root that uniquely identifies a DODAG.
        self.dodag_version = dodag_version          # note: THIS IS NOT A PART OF THE STANDARD. we added it to simplify the implementation
    
    # k flag, d flag and flags fields are not used and has been omitted.
    # Reference: https://datatracker.ietf.org/doc/html/rfc6550#section-6.4


class DIS:

    """DODAG Information Solicitation"""

    # 0                   1                   2
    #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |     Flags     |   Reserved    |   Option(s)...
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    def __init__(self, opt = None):
        self.opt = opt

    # Reference: https://datatracker.ietf.org/doc/html/rfc6550#section-6.2



""" DAG Metric Container implementations """

class HP_OBJ():
    
    # The Hop Count (HP) object is used to report the number of traversed
    # nodes along the path.

    #   0                   1             
    #   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #   |  Res  | Flags |   Hop Count   |
    #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    # The HP object may also contain a set of TLVs used to convey various
    # node characteristics. No TLV is currently defined and has thus been opmitted.
    # Hop count may be used as a metric or as a constraint. Is only used as a metric

    
    def __init__(self, cumulative_hop_count, res = 0, flags = 0):
        
        self.res = res                                      # Reserved field.  This field MUST be set to zero on 
                                                            # transmission and MUST be ignored on receipt.
        self.flags = flags                                  # No Flag is currently defined.  Unassigned bits are considered reserved.
                                                            # They MUST be set to zero on transmission and MUST be ignored on receipt.
        self.cumulative_hop_count = cumulative_hop_count    # Cumulative hop count to root - Used as a metric

    # Referce: https://datatracker.ietf.org/doc/html/rfc6551#section-3.3


class ETX_OBJ():
    
    # The ETX metric is the number of transmissions a node expects to make
    # to a destination in order to successfully deliver a packet.
    # In this project it is used as a metric which is used in the parent select process.

    #     0                   1
    #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #    |              ETX              |
    #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


    # according to RFC6551 the ETX value applies some encoding scheme. This is not used in this project.

    def __init__(self, cumulative_etx):
        
        self.cumulative_etx = cumulative_etx     # Cumulative etx to root

    # Referce: https://datatracker.ietf.org/doc/html/rfc6551#section-4.3.2

class Prefix_info:
    def __init__(self, prefix, prefix_len):
        self.option_type = 0x08
        self.prefix = prefix
        self.prefix_len = prefix_len



""" ICMP implementations """

class ICMP_DIS:

    def __init__(self, opt = None):
        self.icmp = ICMP_header(type = defines.TYPE_RPL_CONTOL_MSG, code = defines.CODE_DIS)
        self.dis = DIS(opt=opt)
        self.option = None

class ICMP_DIO:

    # The options field of the ICMP_DIO is limited to 1 option per packet. 
    # This is in contrast to the standard.

    def __init__(self, rpl_instance_id: int, vers: int, rank: int, dodag_id, prefix = None, prefix_len = 0):

        self.icmp = ICMP_header(type = defines.TYPE_RPL_CONTOL_MSG, code = defines.CODE_DIO)
        self.dio = DIO(rpl_instance_id = rpl_instance_id,\
                       vers = vers,\
                       rank = rank,\
                       dodag_id = dodag_id)
        self.metric_option = None # acording to the standard, options are normally attached to the DIO, not the ICMP_DIO... however, we do it this way
        self.prefix_option = Prefix_info(prefix, prefix_len) # acording to the standard, options are normally attached to the DIO, not the ICMP_DIO... however, we do it this way

    def add_HP_metric(self, cumu_hopcount):
        self.metric_option = HP_OBJ(cumulative_hop_count = cumu_hopcount) # note, we skip the "DAG Metric Container" header (sec 6.7.4 in RPL standard)

    def add_ETX_metric(self, cumu_etx):
        self.metric_option = ETX_OBJ(cumulative_etx = cumu_etx) # note, we skip the "DAG Metric Container" header (sec 6.7.4 in RPL standard)



class ICMP_DAO:
    def __init__(self, rpl_instance_id: int, dodag_id, dodag_version, dao_sequence = 0, amount_of_targets = 0) -> None:
        self.icmp = ICMP_header(type = defines.TYPE_RPL_CONTOL_MSG, code = defines.CODE_DAO)
        self.dao = DAO(rpl_instance_id, dodag_id, dodag_version, dao_sequence)
        self.targets = []
        
    def add_target(self, target_prefix, prefix_len):
        self.targets.append(RPL_target(target_prefix, prefix_len))


class ICMP_DAO_ACK:

    def __init__(self) -> None:
        pass


""" Packet implementation """

class Packet:

    def __init__(self, src_node_id: int, payload):
        
        self.src_node_id = src_node_id
        self.payload = payload
