from .asm8086Listener import *
from . import Memory


class Cpu(asm8086Listener):

    def __init__(self, ram:Memory):
        self.__bits = 16

        # 16 bit X86 registers
        self.AX = 0b0000000000000000
        self.BX = 0b0000000000000000
        self.CX = 0b0000000000000000
        self.DX = 0b0000000000000000
        self.SP = 0b0000000000000000
        self.BP = 0b0000000000000000
        self.SI = 0b0000000000000000
        self.DI = 0b0000000000000000

        # Flags
        self.sf = 0b0
        self.zf = 0b0
        self.acf = 0b0
        self.of = 0b0

        # Control flags not implemented

    def print_registers(self):
        def get_bin(x, n=self.__bits):
            return format(x, 'b').zfill(n)

        def get_hex(x):
            return format(x, 'h').zfill(4)

        print(
            f"AX={get_bin(self.AX)} BX={get_bin(self.BX)}  CX={get_bin(self.CX)}  DX={get_bin(self.DX)}")
        print(f"SP={get_bin(self.SP)} BP={get_bin(self.BP)}  SI={get_bin(self.SI)}  DI={get_bin(self.DI)}")

