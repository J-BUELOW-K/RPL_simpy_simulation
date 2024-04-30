

class DIO_message:

    """DODAG Information Object (DIO)"""
    # 

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

    def __init__(self, RPL_Instance_ID=0, version=0, rank=0, g=0, mop=0,\
                 prf=0, dtsn=0, flags=0, reserved=0, dodag_id='\x00' * 16):

        self.RPL_Instance_ID = RPL_Instance_ID 
        self.version = version          
        self.rank = rank                    
        self.g = g
        self.mop = mop
        self.prf = prf
        self.dtsn = dtsn
        self.flags = flags
        self.reserved = reserved
        self.dodag_id = dodag_id

        self.value_check()

    def value_check(self):

        # verifies the field content
        if self.RPL_Instance_ID < 0 or self.RPL_Instance_ID > 255:
            raise ValueError("RPL Instance ID must be within range 0 to 255")

        if self.version < 0 or self.version > 255:
            raise ValueError("DODAG version must be within range 0 to 255")
        
        if self.rank < 0 or self.rank > pow(2, 16):
            raise ValueError("Rank must be within range 0 to 2^16")

        if self.g < 0 or self.g > 1:
            raise ValueError("G must be 0 or 1")
        
        if self.mop < 0 or self.mop > 4:
            raise ValueError("MOP must be within range 0 to 4")

        if self.prf < 0 or self.prf > 7:
            raise ValueError("Prf (DODAGPreference) must be within range 0 to 7")
        
        if self.dtsn < 0 or self.dtsn > 255:
            raise ValueError("DTSN must be within range 0 to 255")

        if self.flags < 0 or self.flags > 255:
            raise ValueError("Total value of flags must be within range 0 to 255")

        if self.dodag_id < 0 or self.dodag_id > pow(2, 128):
            raise ValueError("DODAGID must be within range 0 to 2^128")

