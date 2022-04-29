import re
from typing import (
    List, 
    Set, 
    Dict, 
    Tuple, 
    Optional
)

from multipledispatch import dispatch

if __name__ is not None and "." in __name__:
    from .asm8086Parser import asm8086Parser
    from .asm8086Listener import *
    from .Memory import Memory
    from .Disk import Disk
else:
    from asm8086Parser import asm8086Parser
    from asm8086Listener import *
    from Memory import Memory
    from Disk import Disk


class Cpu(asm8086Listener):
    """
    Class emulating a 8086 CPU.
    """

    def __init__(self):
        self._bits = 16

        # 8 bit X86 registers
        self.AH = 0b0 * self._bits/2
        self.AL = 0b0 * self._bits/2
        self.BH = 0b0 * self._bits/2
        self.BL = 0b0 * self._bits/2
        self.CH = 0b0 * self._bits/2
        self.CL = 0b0 * self._bits/2
        self.DH = 0b0 * self._bits/2
        self.DL = 0b0 * self._bits/2

        # 16 bit X86 registers
        # Data registers
        self.AX = 0b0 * self._bits  # Accumulator
        self.BX = 0b0 * self._bits  # Base
        self.CX = 0b0 * self._bits  # Counter
        self.DX = 0b0 * self._bits  # Data

        # Pointer registers
        self.SP = 0b0 * self._bits  # Stack Pointer
        self.BP = 0b0 * self._bits  # Base Pointer
        self.IP = 0b0 * self._bits  # Instruction Pointer

        # Index registers
        self.SI = 0b0 * self._bits  # Source Index
        self.DI = 0b0 * self._bits  # Destination Index

        # Segment registers

        # Code Segment − It contains all the instructions to be executed.
        # A 16-bit Code Segment register or CS register stores the starting
        # address of the code segment.
        self.CS = 0b0 * self._bits

        # Data Segment − It contains data, constants and work areas.
        # A 16-bit Data Segment register or DS register stores the starting address
        # of the data segment
        self.DS = 0b0 * self._bits

        # Stack Segment − It contains data and return addresses of procedures or
        # subroutines. It is implemented as a 'stack' data structure.
        # The Stack Segment register or SS register stores the starting address
        # of the stack.
        self.SS = 0b0 * self._bits

        # Apart from the DS, CS and SS registers,
        # there are other extra segment registers -
        # ES (extra segment), FS and GS, which provide additional segments
        # for storing data.
        self.ES = 0b0 * self._bits
        self.FS = 0b0 * self._bits
        self.GS = 0b0 * self._bits

        # Register Flags
        # https://www.tutorialspoint.com/flag-register-of-8086-microprocessor
        # https://www.tutorialspoint.com/assembly_programming/assembly_registers.htm

        # Sign Flag (SF) − It shows the sign of the result of an arithmetic
        # operation. This flag is set according to the sign of a data item following
        # the arithmetic operation. The sign is indicated by the high-order of
        # leftmost bit. A positive result clears the value of SF to 0 and negative
        # result sets it to 1.
        self.SF = 0b0  # Sign (D7)

        # Zero Flag (ZF) − It indicates the result of an arithmetic or comparison
        # operation. A nonzero result clears the zero flag to 0, and a zero result
        # sets it to 1.
        self.ZF = 0b0  # Zero (D6)

        # Carry Flag (CF) − It contains the carry of 0 or 1 from a high-order bit
        # (leftmost) after an arithmetic operation. It also stores the contents of
        # last bit of a shift or rotate operation.
        self.CF = 0b0  # Carry bit (D0)

        # Parity Flag (PF) − It indicates the total number of 1-bits in the result
        # obtained from an arithmetic operation. An even number of 1-bits clears
        # the parity flag to 0 and an odd number of 1-bits sets the parity flag to 1.
        self.PF = 0b0  # Parity (D2)

        # Direction Flag (DF) − It determines left or right direction for moving
        # or comparing string data. When the DF value is 0, the string operation
        # takes left-to-right direction and when the value is set to 1,
        # the string operation takes right-to-left direction.
        self.DF = 0b0

        # Overflow Flag (D11) - It indicates the overflow of a high-order bit
        # (leftmost bit) of data after a signed arithmetic operation.
        self.OF = 0b0

        # Auxiliary Carry Flag (AF) − It contains the carry from bit 3 to bit 4
        # following an arithmetic operation; used for specialized arithmetic.
        # The AF is set when a 1-byte arithmetic operation causes a carry from
        # bit 3 into bit 4.
        self.AF = 0b0

        # Interrupt Flag (IF) − It determines whether the external interrupts
        # like keyboard entry, etc., are to be ignored or processed.
        # It disables the external interrupt when the value is 0 and enables
        # interrupts when set to 1
        self.IF = 0b1

        #  Trap Flag (TF) − It allows setting the operation of the processor in
        #  single-step mode. The DEBUG program we used sets the trap flag,
        #  so we could step through the execution one instruction at a time.
        self.TF = 0b0

        # Opcode dictionary
        # https://pastraiser.com/cpu/i8088/i8088_opcodes.html
        # Generated by opcode_dict/txt2pydict.py
        # At least one space after the comma. Just to keep happy my OCD ;o)
        self._opcode = {
            # LINE ==> 00     add      mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "add mem8,reg8",
                "opcodes": [int(0x00), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 01     add      mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "add mem16,reg16",
                "opcodes": [int(0x01), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 01     add      mem32,reg32
            r"^(\s*)add(\s+)[0-9a-f]{8}e[abcd]x,(\s+)": {
                "mnemonic": "add mem32,reg32",
                "opcodes": [int(0x01), ],
                "flags": ""},
            # LINE ==> 02     add      reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "add reg8,reg8",
                "opcodes": [int(0x02), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 02     add      reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "add reg8,mem8",
                "opcodes": [int(0x02), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 03     add      reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "add reg16,reg16",
                "opcodes": [int(0x03), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)add(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "add reg16,reg16",
                "opcodes": [int(0x03), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 04     add      AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)al,(\s+)": {
                "mnemonic": "add AL,imm8",
                "opcodes": [int(0x04), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 05     add      AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)ax,(\s+)": {
                "mnemonic": "add AX,imm16",
                "opcodes": [int(0x05), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)add(\s+)ax,(\s+)": {
                "mnemonic": "add AX,imm16",
                "opcodes": [int(0x05), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 06     push     ES                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push ES",
                "opcodes": [int(0x06), ],
                "flags": "none"},
            # LINE ==> 07     pop      ES                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop ES",
                "opcodes": [int(0x07), ],
                "flags": "none"},
            # LINE ==> 08     or       mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "or mem8,reg8",
                "opcodes": [int(0x08), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 09     or       mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "or mem16,reg16",
                "opcodes": [int(0x09), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)or(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "or mem16,reg16",
                "opcodes": [int(0x09), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 0A     or       reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "or reg8,reg8",
                "opcodes": [int(0x0A), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 0A     or       reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "or reg8,mem8",
                "opcodes": [int(0x0A), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 0B     or       reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "or reg16,reg16",
                "opcodes": [int(0x0B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)or(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "or reg16,reg16",
                "opcodes": [int(0x0B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 0B     or       reg16,mem16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "or reg16,mem16",
                "opcodes": [int(0x0B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)or(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "or reg16,mem16",
                "opcodes": [int(0x0B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 0C     or       AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)al,(\s+)": {
                "mnemonic": "or AL,imm8",
                "opcodes": [int(0x0C), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 0D     or       AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)ax,(\s+)": {
                "mnemonic": "or AX,imm16",
                "opcodes": [int(0x0D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)or(\s+)ax,(\s+)": {
                "mnemonic": "or AX,imm16",
                "opcodes": [int(0x0D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 0E     push     CS                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push CS",
                "opcodes": [int(0x0E), ],
                "flags": "none"},
            # LINE ==> 0F 04  shld     reg16,reg16,imm8  SF,ZF,CF,PF
            r"^(\s*)shld(\s+)[abcd]x[abcd]xal,(\s+)": {
                "mnemonic": "shld reg16,reg16,imm8",
                "opcodes": [int(0x0F), int(0x04), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 reg32,reg32,imm8  OF,AF
            r"^(\s*)shld(\s+)[abcd]x[abcd]xal,(\s+)": {
                "mnemonic": "shld reg16,reg16,imm8",
                "opcodes": [int(0x0F), int(0x04), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F 04  shld     mem16,reg16,imm8  SF,ZF,CF,PF
            r"^(\s*)shld(\s+)[0-9a-f]{4}[abcd]xal,(\s+)": {
                "mnemonic": "shld mem16,reg16,imm8",
                "opcodes": [int(0x0F), int(0x04), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 mem32,reg32,imm8  OF,AF
            r"^(\s*)shld(\s+)[0-9a-f]{4}[abcd]xal,(\s+)": {
                "mnemonic": "shld mem16,reg16,imm8",
                "opcodes": [int(0x0F), int(0x04), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F 05  shld     reg16,reg16,CL    SF,ZF,CF,PF
            r"^(\s*)shld(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "shld reg16,reg16,CL",
                "opcodes": [int(0x0F), int(0x05), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 reg32,reg32,CL    OF,AF
            r"^(\s*)shld(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "shld reg16,reg16,CL",
                "opcodes": [int(0x0F), int(0x05), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F 05  shld     mem16,reg16,CL    SF,ZF,CF,PF
            r"^(\s*)shld(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "shld mem16,reg16,CL",
                "opcodes": [int(0x0F), int(0x05), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 mem32,reg32,CL    OF,AF
            r"^(\s*)shld(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "shld mem16,reg16,CL",
                "opcodes": [int(0x0F), int(0x05), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F 80  jo       rel32             none
            r"^(\s*)jo(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jo rel32",
                "opcodes": [int(0x0F), int(0x80), ],
                "flags": "none"},
            # LINE ==> 0F 81  jno      rel32             none
            r"^(\s*)jno(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jno rel32",
                "opcodes": [int(0x0F), int(0x81), ],
                "flags": "none"},
            # LINE ==> 0F 82  jb       rel32             none
            r"^(\s*)jb(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jb rel32",
                "opcodes": [int(0x0F), int(0x82), ],
                "flags": "none"},
            # LINE ==>        jnae
            r"^(\s*)jb(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jb rel32",
                "opcodes": [int(0x0F), int(0x82), ],
                "flags": "none"},
            # LINE ==> 0F 82  jc       rel32             none
            r"^(\s*)jc(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jc rel32",
                "opcodes": [int(0x0F), int(0x82), ],
                "flags": "none"},
            # LINE ==> 0F 83  jae      rel32             none
            r"^(\s*)jae(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jae rel32",
                "opcodes": [int(0x0F), int(0x83), ],
                "flags": "none"},
            # LINE ==>        jnb
            r"^(\s*)jae(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jae rel32",
                "opcodes": [int(0x0F), int(0x83), ],
                "flags": "none"},
            # LINE ==> 0F 83  jnc      rel32             none
            r"^(\s*)jnc(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jnc rel32",
                "opcodes": [int(0x0F), int(0x83), ],
                "flags": "none"},
            # LINE ==> 0F 84  je       rel32             none
            r"^(\s*)je(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "je rel32",
                "opcodes": [int(0x0F), int(0x84), ],
                "flags": "none"},
            # LINE ==>        jz
            r"^(\s*)je(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "je rel32",
                "opcodes": [int(0x0F), int(0x84), ],
                "flags": "none"},
            # LINE ==> 0F 85  jne      rel32             none
            r"^(\s*)jne(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jne rel32",
                "opcodes": [int(0x0F), int(0x85), ],
                "flags": "none"},
            # LINE ==>        jnz
            r"^(\s*)jne(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jne rel32",
                "opcodes": [int(0x0F), int(0x85), ],
                "flags": "none"},
            # LINE ==> 0F 86  jbe      rel32             none
            r"^(\s*)jbe(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jbe rel32",
                "opcodes": [int(0x0F), int(0x86), ],
                "flags": "none"},
            # LINE ==>        jna
            r"^(\s*)jbe(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jbe rel32",
                "opcodes": [int(0x0F), int(0x86), ],
                "flags": "none"},
            # LINE ==> 0F 87  ja       rel32             none
            r"^(\s*)ja(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "ja rel32",
                "opcodes": [int(0x0F), int(0x87), ],
                "flags": "none"},
            # LINE ==>        jnbe
            r"^(\s*)ja(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "ja rel32",
                "opcodes": [int(0x0F), int(0x87), ],
                "flags": "none"},
            # LINE ==> 0F 88  js       rel32             none
            r"^(\s*)js(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "js rel32",
                "opcodes": [int(0x0F), int(0x88), ],
                "flags": "none"},
            # LINE ==> 0F 89  jns      rel32             none
            r"^(\s*)jns(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jns rel32",
                "opcodes": [int(0x0F), int(0x89), ],
                "flags": "none"},
            # LINE ==> 0F 8A  jp       rel32             none
            r"^(\s*)jp(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jp rel32",
                "opcodes": [int(0x0F), int(0x8A), ],
                "flags": "none"},
            # LINE ==>        jpe
            r"^(\s*)jp(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jp rel32",
                "opcodes": [int(0x0F), int(0x8A), ],
                "flags": "none"},
            # LINE ==> 0F 8B  jnp      rel32             none
            r"^(\s*)jnp(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jnp rel32",
                "opcodes": [int(0x0F), int(0x8B), ],
                "flags": "none"},
            # LINE ==>        jpo
            r"^(\s*)jnp(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jnp rel32",
                "opcodes": [int(0x0F), int(0x8B), ],
                "flags": "none"},
            # LINE ==> 0F 8C  jl       rel32             none
            r"^(\s*)jl(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jl rel32",
                "opcodes": [int(0x0F), int(0x8C), ],
                "flags": "none"},
            # LINE ==>        jnge
            r"^(\s*)jl(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jl rel32",
                "opcodes": [int(0x0F), int(0x8C), ],
                "flags": "none"},
            # LINE ==> 0F 8D  jge      rel32             none
            r"^(\s*)jge(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jge rel32",
                "opcodes": [int(0x0F), int(0x8D), ],
                "flags": "none"},
            # LINE ==>        jnl
            r"^(\s*)jge(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jge rel32",
                "opcodes": [int(0x0F), int(0x8D), ],
                "flags": "none"},
            # LINE ==> 0F 8E  jle      rel32             none
            r"^(\s*)jle(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jle rel32",
                "opcodes": [int(0x0F), int(0x8E), ],
                "flags": "none"},
            # LINE ==>        jng
            r"^(\s*)jle(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jle rel32",
                "opcodes": [int(0x0F), int(0x8E), ],
                "flags": "none"},
            # LINE ==> 0F 8F  jg       rel32             none
            r"^(\s*)jg(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jg rel32",
                "opcodes": [int(0x0F), int(0x8F), ],
                "flags": "none"},
            # LINE ==>        jnle
            r"^(\s*)jg(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jg rel32",
                "opcodes": [int(0x0F), int(0x8F), ],
                "flags": "none"},
            # LINE ==> 0F A0  push     FS                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push FS",
                "opcodes": [int(0x0F), int(0xA0), ],
                "flags": "none"},
            # LINE ==> 0F A1  pop      FS                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop FS",
                "opcodes": [int(0x0F), int(0xA1), ],
                "flags": "none"},
            # LINE ==> 0F A8  push     GS                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push GS",
                "opcodes": [int(0x0F), int(0xA8), ],
                "flags": "none"},
            # LINE ==> 0F A9  pop      GS                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop GS",
                "opcodes": [int(0x0F), int(0xA9), ],
                "flags": "none"},
            # LINE ==> 0F AC  shrd     reg16,reg16,imm8  SF,ZF,CF,PF
            r"^(\s*)shrd(\s+)[abcd]x[abcd]xal,(\s+)": {
                "mnemonic": "shrd reg16,reg16,imm8",
                "opcodes": [int(0x0F), int(0xAC), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 reg32,reg32,imm8  OF,AF
            r"^(\s*)shrd(\s+)[abcd]x[abcd]xal,(\s+)": {
                "mnemonic": "shrd reg16,reg16,imm8",
                "opcodes": [int(0x0F), int(0xAC), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F AC  shrd     mem16,reg16,imm8  SF,ZF,CF,PF
            r"^(\s*)shrd(\s+)[0-9a-f]{4}[abcd]xal,(\s+)": {
                "mnemonic": "shrd mem16,reg16,imm8",
                "opcodes": [int(0x0F), int(0xAC), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 mem32,reg32,imm8  OF,AF
            r"^(\s*)shrd(\s+)[0-9a-f]{4}[abcd]xal,(\s+)": {
                "mnemonic": "shrd mem16,reg16,imm8",
                "opcodes": [int(0x0F), int(0xAC), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F AD  shrd     reg16,reg16,CL    SF,ZF,CF,PF
            r"^(\s*)shrd(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "shrd reg16,reg16,CL",
                "opcodes": [int(0x0F), int(0xAD), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 reg32,reg32,CL    OF,AF
            r"^(\s*)shrd(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "shrd reg16,reg16,CL",
                "opcodes": [int(0x0F), int(0xAD), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F AD  shrd     mem16,reg16,CL    SF,ZF,CF,PF
            r"^(\s*)shrd(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "shrd mem16,reg16,CL",
                "opcodes": [int(0x0F), int(0xAD), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==>                 mem32,reg32,CL    OF,AF
            r"^(\s*)shrd(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "shrd mem16,reg16,CL",
                "opcodes": [int(0x0F), int(0xAD), ],
                "flags": "SF,ZF,CF,PF"},
            # LINE ==> 0F AF  imul     reg16,reg16       OF,CF
            r"^(\s*)imul(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "imul reg16,reg16",
                "opcodes": [int(0x0F), int(0xAF), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32,reg32       SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "imul reg16,reg16",
                "opcodes": [int(0x0F), int(0xAF), ],
                "flags": "OF,CF"},
            # LINE ==> 0F AF  imul     reg16,mem16       OF,CF
            r"^(\s*)imul(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "imul reg16,mem16",
                "opcodes": [int(0x0F), int(0xAF), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32,mem32       SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "imul reg16,mem16",
                "opcodes": [int(0x0F), int(0xAF), ],
                "flags": "OF,CF"},
            # LINE ==> 0F B6  movzx    reg16,reg8        none
            r"^(\s*)movzx(\s+)[abcd]x[abcd][hl],(\s+)": {
                "mnemonic": "movzx reg16,reg8",
                "opcodes": [int(0x0F), int(0xB6), ],
                "flags": "none"},
            # LINE ==>                 reg32,reg8
            r"^(\s*)movzx(\s+)[abcd]x[abcd][hl],(\s+)": {
                "mnemonic": "movzx reg16,reg8",
                "opcodes": [int(0x0F), int(0xB6), ],
                "flags": "none"},
            # LINE ==> 0F B6  movzx    reg16,mem8        none
            r"^(\s*)movzx(\s+)[abcd]x[0-9a-f]{2},(\s+)": {
                "mnemonic": "movzx reg16,mem8",
                "opcodes": [int(0x0F), int(0xB6), ],
                "flags": "none"},
            # LINE ==>                 reg32,mem8
            r"^(\s*)movzx(\s+)[abcd]x[0-9a-f]{2},(\s+)": {
                "mnemonic": "movzx reg16,mem8",
                "opcodes": [int(0x0F), int(0xB6), ],
                "flags": "none"},
            # LINE ==> 0F B7  movzx    reg32,reg16       none
            r"^(\s*)movzx(\s+)e[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "movzx reg32,reg16",
                "opcodes": [int(0x0F), int(0xB7), ],
                "flags": "none"},
            # LINE ==> 0F B7  movzx    reg32,mem16       none
            r"^(\s*)movzx(\s+)e[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "movzx reg32,mem16",
                "opcodes": [int(0x0F), int(0xB7), ],
                "flags": "none"},
            # LINE ==> 0F BE  movsx    reg16,reg8        none
            r"^(\s*)movsx(\s+)[abcd]x[abcd][hl],(\s+)": {
                "mnemonic": "movsx reg16,reg8",
                "opcodes": [int(0x0F), int(0xBE), ],
                "flags": "none"},
            # LINE ==>                 reg32,reg8
            r"^(\s*)movsx(\s+)[abcd]x[abcd][hl],(\s+)": {
                "mnemonic": "movsx reg16,reg8",
                "opcodes": [int(0x0F), int(0xBE), ],
                "flags": "none"},
            # LINE ==> 0F BE  movsx    reg16,mem8        none
            r"^(\s*)movsx(\s+)[abcd]x[0-9a-f]{2},(\s+)": {
                "mnemonic": "movsx reg16,mem8",
                "opcodes": [int(0x0F), int(0xBE), ],
                "flags": "none"},
            # LINE ==>                 reg32,mem8
            r"^(\s*)movsx(\s+)[abcd]x[0-9a-f]{2},(\s+)": {
                "mnemonic": "movsx reg16,mem8",
                "opcodes": [int(0x0F), int(0xBE), ],
                "flags": "none"},
            # LINE ==> 0F BF  movsx    reg32,reg16       none
            r"^(\s*)movsx(\s+)e[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "movsx reg32,reg16",
                "opcodes": [int(0x0F), int(0xBF), ],
                "flags": "none"},
            # LINE ==> 0F BF  movsx    reg32,mem16       none
            r"^(\s*)movsx(\s+)e[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "movsx reg32,mem16",
                "opcodes": [int(0x0F), int(0xBF), ],
                "flags": "none"},
            # LINE ==> 10     adc      mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "adc mem8,reg8",
                "opcodes": [int(0x10), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 11     adc      mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "adc mem16,reg16",
                "opcodes": [int(0x11), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)adc(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "adc mem16,reg16",
                "opcodes": [int(0x11), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 12     adc      reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "adc reg8,reg8",
                "opcodes": [int(0x12), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 12     adc      reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "adc reg8,mem8",
                "opcodes": [int(0x12), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 13     adc      reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "adc reg16,reg16",
                "opcodes": [int(0x13), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)adc(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "adc reg16,reg16",
                "opcodes": [int(0x13), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 13     adc      reg16,mem16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "adc reg16,mem16",
                "opcodes": [int(0x13), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)adc(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "adc reg16,mem16",
                "opcodes": [int(0x13), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 14     adc      AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)al,(\s+)": {
                "mnemonic": "adc AL,imm8",
                "opcodes": [int(0x14), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 15     adc      AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)ax,(\s+)": {
                "mnemonic": "adc AX,imm16",
                "opcodes": [int(0x15), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)adc(\s+)ax,(\s+)": {
                "mnemonic": "adc AX,imm16",
                "opcodes": [int(0x15), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 16     push     SS                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push SS",
                "opcodes": [int(0x16), ],
                "flags": "none"},
            # LINE ==> 17     pop      SS                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop SS",
                "opcodes": [int(0x17), ],
                "flags": "none"},
            # LINE ==> 18     sbb      mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "sbb mem8,reg8",
                "opcodes": [int(0x18), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 19     sbb      mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "sbb mem16,reg16",
                "opcodes": [int(0x19), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)sbb(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "sbb mem16,reg16",
                "opcodes": [int(0x19), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 1A     sbb      reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "sbb reg8,reg8",
                "opcodes": [int(0x1A), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 1A     sbb      reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "sbb reg8,mem8",
                "opcodes": [int(0x1A), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 1B     sbb      reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "sbb reg16,reg16",
                "opcodes": [int(0x1B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)sbb(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "sbb reg16,reg16",
                "opcodes": [int(0x1B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 1B     sbb      reg16,mem16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "sbb reg16,mem16",
                "opcodes": [int(0x1B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)sbb(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "sbb reg16,mem16",
                "opcodes": [int(0x1B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 1C     sbb      AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)al,(\s+)": {
                "mnemonic": "sbb AL,imm8",
                "opcodes": [int(0x1C), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 1D     sbb      AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)ax,(\s+)": {
                "mnemonic": "sbb AX,imm16",
                "opcodes": [int(0x1D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)sbb(\s+)ax,(\s+)": {
                "mnemonic": "sbb AX,imm16",
                "opcodes": [int(0x1D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 1E     push     DS                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push DS",
                "opcodes": [int(0x1E), ],
                "flags": "none"},
            # LINE ==> 1F     pop      DS                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop DS",
                "opcodes": [int(0x1F), ],
                "flags": "none"},
            # LINE ==> 20     and      mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "and mem8,reg8",
                "opcodes": [int(0x20), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 21     and      mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "and mem16,reg16",
                "opcodes": [int(0x21), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)and(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "and mem16,reg16",
                "opcodes": [int(0x21), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 22     and      reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "and reg8,reg8",
                "opcodes": [int(0x22), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 22     and      reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "and reg8,mem8",
                "opcodes": [int(0x22), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 23     and      reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "and reg16,reg16",
                "opcodes": [int(0x23), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)and(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "and reg16,reg16",
                "opcodes": [int(0x23), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 23     and      reg16,mem16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "and reg16,mem16",
                "opcodes": [int(0x23), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)and(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "and reg16,mem16",
                "opcodes": [int(0x23), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 24     and      AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)al,(\s+)": {
                "mnemonic": "and AL,imm8",
                "opcodes": [int(0x24), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 25     and      AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)ax,(\s+)": {
                "mnemonic": "and AX,imm16",
                "opcodes": [int(0x25), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)and(\s+)ax,(\s+)": {
                "mnemonic": "and AX,imm16",
                "opcodes": [int(0x25), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 27     daa      none              SF,ZF,PF,AF,OF
            r"^(\s*)daa(\s+),(\s+)": {
                "mnemonic": "daa none",
                "opcodes": [int(0x27), ],
                "flags": "SF,ZF,PF,AF,OF"},
            # LINE ==> 28     sub      mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "sub mem8,reg8",
                "opcodes": [int(0x28), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 29     sub      mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "sub mem16,reg16",
                "opcodes": [int(0x29), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)sub(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "sub mem16,reg16",
                "opcodes": [int(0x29), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 2A     sub      reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "sub reg8,reg8",
                "opcodes": [int(0x2A), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 2A     sub      reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "sub reg8,mem8",
                "opcodes": [int(0x2A), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 2B     sub      reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "sub reg16,reg16",
                "opcodes": [int(0x2B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)sub(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "sub reg16,reg16",
                "opcodes": [int(0x2B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 2B     sub      reg16,mem16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "sub reg16,mem16",
                "opcodes": [int(0x2B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)sub(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "sub reg16,mem16",
                "opcodes": [int(0x2B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 2C     sub      AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)al,(\s+)": {
                "mnemonic": "sub AL,imm8",
                "opcodes": [int(0x2C), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 2D     sub      AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)ax,(\s+)": {
                "mnemonic": "sub AX,imm16",
                "opcodes": [int(0x2D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)sub(\s+)ax,(\s+)": {
                "mnemonic": "sub AX,imm16",
                "opcodes": [int(0x2D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 2F     das      none              SF,ZF,PF,AF,OF
            r"^(\s*)das(\s+),(\s+)": {
                "mnemonic": "das none",
                "opcodes": [int(0x2F), ],
                "flags": "SF,ZF,PF,AF,OF"},
            # LINE ==> 30     xor      mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "xor mem8,reg8",
                "opcodes": [int(0x30), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 31     xor      mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "xor mem16,reg16",
                "opcodes": [int(0x31), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)xor(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "xor mem16,reg16",
                "opcodes": [int(0x31), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 32     xor      reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "xor reg8,reg8",
                "opcodes": [int(0x32), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 32     xor      reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "xor reg8,mem8",
                "opcodes": [int(0x32), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 33     xor      reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "xor reg16,reg16",
                "opcodes": [int(0x33), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)xor(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "xor reg16,reg16",
                "opcodes": [int(0x33), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 33     xor      reg16,mem16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "xor reg16,mem16",
                "opcodes": [int(0x33), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)xor(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "xor reg16,mem16",
                "opcodes": [int(0x33), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 34     xor      AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)al,(\s+)": {
                "mnemonic": "xor AL,imm8",
                "opcodes": [int(0x34), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 35     xor      AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)ax,(\s+)": {
                "mnemonic": "xor AX,imm16",
                "opcodes": [int(0x35), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)xor(\s+)ax,(\s+)": {
                "mnemonic": "xor AX,imm16",
                "opcodes": [int(0x35), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 37     aaa      none              AF,CF,SF,ZF,OF,PF
            r"^(\s*)aaa(\s+),(\s+)": {
                "mnemonic": "aaa none",
                "opcodes": [int(0x37), ],
                "flags": "AF,CF,SF,ZF,OF,PF"},
            # LINE ==> 38     cmp      reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "cmp reg8,reg8",
                "opcodes": [int(0x38), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 38     cmp      mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "cmp mem8,reg8",
                "opcodes": [int(0x38), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 39     cmp      mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "cmp mem16,reg16",
                "opcodes": [int(0x39), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)cmp(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "cmp mem16,reg16",
                "opcodes": [int(0x39), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 3A     cmp      reg8,mem8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "cmp reg8,mem8",
                "opcodes": [int(0x3A), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 3B     cmp      reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "cmp reg16,reg16",
                "opcodes": [int(0x3B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)cmp(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "cmp reg16,reg16",
                "opcodes": [int(0x3B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 3B     cmp      reg16,mem16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "cmp reg16,mem16",
                "opcodes": [int(0x3B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)cmp(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "cmp reg16,mem16",
                "opcodes": [int(0x3B), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 3C     cmp      AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)al,(\s+)": {
                "mnemonic": "cmp AL,imm8",
                "opcodes": [int(0x3C), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 3D     cmp      AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)ax,(\s+)": {
                "mnemonic": "cmp AX,imm16",
                "opcodes": [int(0x3D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)cmp(\s+)ax,(\s+)": {
                "mnemonic": "cmp AX,imm16",
                "opcodes": [int(0x3D), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 3F     aas      none              AF,CF,SF,ZF,OF,PF
            r"^(\s*)aas(\s+),(\s+)": {
                "mnemonic": "aas none",
                "opcodes": [int(0x3F), ],
                "flags": "AF,CF,SF,ZF,OF,PF"},
            # LINE ==> 40     inc      AX                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc AX",
                "opcodes": [int(0x40), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EAX
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc AX",
                "opcodes": [int(0x40), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 41     inc      CX                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc CX",
                "opcodes": [int(0x41), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 ECX
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc CX",
                "opcodes": [int(0x41), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 42     inc      DX                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc DX",
                "opcodes": [int(0x42), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EDX
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc DX",
                "opcodes": [int(0x42), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 43     inc      BX                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc BX",
                "opcodes": [int(0x43), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EBX
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc BX",
                "opcodes": [int(0x43), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 44     inc      SP                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc SP",
                "opcodes": [int(0x44), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 ESP
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc SP",
                "opcodes": [int(0x44), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 45     inc      BP                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc BP",
                "opcodes": [int(0x45), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EBP
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc BP",
                "opcodes": [int(0x45), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 47     inc      SI                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc SI",
                "opcodes": [int(0x47), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 ESI
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc SI",
                "opcodes": [int(0x47), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 48     dec      AX                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec AX",
                "opcodes": [int(0x48), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EAX
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec AX",
                "opcodes": [int(0x48), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 48     inc      DI                SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc DI",
                "opcodes": [int(0x48), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EDI
            r"^(\s*)inc(\s+),(\s+)": {
                "mnemonic": "inc DI",
                "opcodes": [int(0x48), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 49     dec      CX                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec CX",
                "opcodes": [int(0x49), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 ECX
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec CX",
                "opcodes": [int(0x49), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 4A     dec      DX                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec DX",
                "opcodes": [int(0x4A), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EDX
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec DX",
                "opcodes": [int(0x4A), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 4B     dec      BX                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec BX",
                "opcodes": [int(0x4B), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EBX
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec BX",
                "opcodes": [int(0x4B), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 4C     dec      SP                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec SP",
                "opcodes": [int(0x4C), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 ESP
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec SP",
                "opcodes": [int(0x4C), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 4D     dec      BP                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec BP",
                "opcodes": [int(0x4D), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EBP
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec BP",
                "opcodes": [int(0x4D), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 4E     dec      SI                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec SI",
                "opcodes": [int(0x4E), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 ESI
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec SI",
                "opcodes": [int(0x4E), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 4F     dec      DI                SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec DI",
                "opcodes": [int(0x4F), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 EDI
            r"^(\s*)dec(\s+),(\s+)": {
                "mnemonic": "dec DI",
                "opcodes": [int(0x4F), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> 50     push     AX                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push AX",
                "opcodes": [int(0x50), ],
                "flags": "none"},
            # LINE ==>                 EAX
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push AX",
                "opcodes": [int(0x50), ],
                "flags": "none"},
            # LINE ==> 51     push     CX                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push CX",
                "opcodes": [int(0x51), ],
                "flags": "none"},
            # LINE ==>                 ECX
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push CX",
                "opcodes": [int(0x51), ],
                "flags": "none"},
            # LINE ==> 52     push     DX                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push DX",
                "opcodes": [int(0x52), ],
                "flags": "none"},
            # LINE ==>                 EDX
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push DX",
                "opcodes": [int(0x52), ],
                "flags": "none"},
            # LINE ==> 53     push     BX                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push BX",
                "opcodes": [int(0x53), ],
                "flags": "none"},
            # LINE ==>                 EBX
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push BX",
                "opcodes": [int(0x53), ],
                "flags": "none"},
            # LINE ==> 54     push     SP                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push SP",
                "opcodes": [int(0x54), ],
                "flags": "none"},
            # LINE ==>                 ESP
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push SP",
                "opcodes": [int(0x54), ],
                "flags": "none"},
            # LINE ==> 55     push     BP                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push BP",
                "opcodes": [int(0x55), ],
                "flags": "none"},
            # LINE ==>                 EBP
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push BP",
                "opcodes": [int(0x55), ],
                "flags": "none"},
            # LINE ==> 56     push     SI                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push SI",
                "opcodes": [int(0x56), ],
                "flags": "none"},
            # LINE ==>                 ESI
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push SI",
                "opcodes": [int(0x56), ],
                "flags": "none"},
            # LINE ==> 57     push     DI                none
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push DI",
                "opcodes": [int(0x57), ],
                "flags": "none"},
            # LINE ==>                 EDI
            r"^(\s*)push(\s+),(\s+)": {
                "mnemonic": "push DI",
                "opcodes": [int(0x57), ],
                "flags": "none"},
            # LINE ==> 58     pop      AX                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop AX",
                "opcodes": [int(0x58), ],
                "flags": "none"},
            # LINE ==>                 EAX
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop AX",
                "opcodes": [int(0x58), ],
                "flags": "none"},
            # LINE ==> 59     pop      CX                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop CX",
                "opcodes": [int(0x59), ],
                "flags": "none"},
            # LINE ==>                 ECX
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop CX",
                "opcodes": [int(0x59), ],
                "flags": "none"},
            # LINE ==> 5A     pop      DX                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop DX",
                "opcodes": [int(0x5A), ],
                "flags": "none"},
            # LINE ==>                 EDX
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop DX",
                "opcodes": [int(0x5A), ],
                "flags": "none"},
            # LINE ==> 5B     pop      BX                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop BX",
                "opcodes": [int(0x5B), ],
                "flags": "none"},
            # LINE ==>                 EBX
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop BX",
                "opcodes": [int(0x5B), ],
                "flags": "none"},
            # LINE ==> 5C     pop      SP                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop SP",
                "opcodes": [int(0x5C), ],
                "flags": "none"},
            # LINE ==>                 ESP
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop SP",
                "opcodes": [int(0x5C), ],
                "flags": "none"},
            # LINE ==> 5D     pop      BP                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop BP",
                "opcodes": [int(0x5D), ],
                "flags": "none"},
            # LINE ==>                 EBP
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop BP",
                "opcodes": [int(0x5D), ],
                "flags": "none"},
            # LINE ==> 5E     pop      SI                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop SI",
                "opcodes": [int(0x5E), ],
                "flags": "none"},
            # LINE ==>                 ESI
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop SI",
                "opcodes": [int(0x5E), ],
                "flags": "none"},
            # LINE ==> 5F     pop      DI                none
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop DI",
                "opcodes": [int(0x5F), ],
                "flags": "none"},
            # LINE ==>                 EDI
            r"^(\s*)pop(\s+),(\s+)": {
                "mnemonic": "pop DI",
                "opcodes": [int(0x5F), ],
                "flags": "none"},
            # LINE ==> 60     pusha    none              none
            r"^(\s*)pusha(\s+),(\s+)": {
                "mnemonic": "pusha none",
                "opcodes": [int(0x60), ],
                "flags": "none"},
            # LINE ==>        pushad
            r"^(\s*)pusha(\s+),(\s+)": {
                "mnemonic": "pusha none",
                "opcodes": [int(0x60), ],
                "flags": "none"},
            # LINE ==> 61     popa     none              none
            r"^(\s*)popa(\s+),(\s+)": {
                "mnemonic": "popa none",
                "opcodes": [int(0x61), ],
                "flags": "none"},
            # LINE ==>        popad
            r"^(\s*)popa(\s+),(\s+)": {
                "mnemonic": "popa none",
                "opcodes": [int(0x61), ],
                "flags": "none"},
            # LINE ==> 68     push     imm16             none
            r"^(\s*)push(\s+)ax,(\s+)": {
                "mnemonic": "push imm16",
                "opcodes": [int(0x68), ],
                "flags": "none"},
            # LINE ==>                 imm32
            r"^(\s*)push(\s+)ax,(\s+)": {
                "mnemonic": "push imm16",
                "opcodes": [int(0x68), ],
                "flags": "none"},
            # LINE ==> 69     imul     reg16,reg16,imm16 OF,CF
            r"^(\s*)imul(\s+)[abcd]x[abcd]xax,(\s+)": {
                "mnemonic": "imul reg16,reg16,imm16",
                "opcodes": [int(0x69), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32,reg32,imm32 SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]x[abcd]xax,(\s+)": {
                "mnemonic": "imul reg16,reg16,imm16",
                "opcodes": [int(0x69), ],
                "flags": "OF,CF"},
            # LINE ==> 69     imul     reg16,mem16,imm16 OF,CF
            r"^(\s*)imul(\s+)[abcd]x[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "imul reg16,mem16,imm16",
                "opcodes": [int(0x69), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32,mem32,imm32 SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]x[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "imul reg16,mem16,imm16",
                "opcodes": [int(0x69), ],
                "flags": "OF,CF"},
            # LINE ==> 6A     push     imm8              none
            r"^(\s*)push(\s+)al,(\s+)": {
                "mnemonic": "push imm8",
                "opcodes": [int(0x6A), ],
                "flags": "none"},
            # LINE ==> 6B     imul     reg16,imm8        OF,CF
            r"^(\s*)imul(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "imul reg16,imm8",
                "opcodes": [int(0x6B), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32,imm8        SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "imul reg16,imm8",
                "opcodes": [int(0x6B), ],
                "flags": "OF,CF"},
            # LINE ==> 6B     imul     reg16,reg16,imm8  OF,CF
            r"^(\s*)imul(\s+)[abcd]x[abcd]xal,(\s+)": {
                "mnemonic": "imul reg16,reg16,imm8",
                "opcodes": [int(0x6B), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32,reg32,imm8  SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]x[abcd]xal,(\s+)": {
                "mnemonic": "imul reg16,reg16,imm8",
                "opcodes": [int(0x6B), ],
                "flags": "OF,CF"},
            # LINE ==> 6B     imul     reg16,mem16,imm8  OF,CF
            r"^(\s*)imul(\s+)[abcd]x[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "imul reg16,mem16,imm8",
                "opcodes": [int(0x6B), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32,mem32,imm8  SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]x[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "imul reg16,mem16,imm8",
                "opcodes": [int(0x6B), ],
                "flags": "OF,CF"},
            # LINE ==> 70     jo       rel8              none
            r"^(\s*)jo(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jo rel8",
                "opcodes": [int(0x70), ],
                "flags": "none"},
            # LINE ==> 71     jno      rel8              none
            r"^(\s*)jno(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jno rel8",
                "opcodes": [int(0x71), ],
                "flags": "none"},
            # LINE ==> 72     jb       rel8              none
            r"^(\s*)jb(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jb rel8",
                "opcodes": [int(0x72), ],
                "flags": "none"},
            # LINE ==>        jnae
            r"^(\s*)jb(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jb rel8",
                "opcodes": [int(0x72), ],
                "flags": "none"},
            # LINE ==> 72     jc       rel8              none
            r"^(\s*)jc(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jc rel8",
                "opcodes": [int(0x72), ],
                "flags": "none"},
            # LINE ==> 73     jae      rel8              none
            r"^(\s*)jae(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jae rel8",
                "opcodes": [int(0x73), ],
                "flags": "none"},
            # LINE ==>        jnb
            r"^(\s*)jae(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jae rel8",
                "opcodes": [int(0x73), ],
                "flags": "none"},
            # LINE ==> 73     jnc      rel8              none
            r"^(\s*)jnc(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jnc rel8",
                "opcodes": [int(0x73), ],
                "flags": "none"},
            # LINE ==> 74     je       rel8              none
            r"^(\s*)je(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "je rel8",
                "opcodes": [int(0x74), ],
                "flags": "none"},
            # LINE ==>        jz
            r"^(\s*)je(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "je rel8",
                "opcodes": [int(0x74), ],
                "flags": "none"},
            # LINE ==> 75     jne      rel8              none
            r"^(\s*)jne(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jne rel8",
                "opcodes": [int(0x75), ],
                "flags": "none"},
            # LINE ==>        jnz
            r"^(\s*)jne(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jne rel8",
                "opcodes": [int(0x75), ],
                "flags": "none"},
            # LINE ==> 76     jbe      rel8              none
            r"^(\s*)jbe(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jbe rel8",
                "opcodes": [int(0x76), ],
                "flags": "none"},
            # LINE ==>        jna
            r"^(\s*)jbe(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jbe rel8",
                "opcodes": [int(0x76), ],
                "flags": "none"},
            # LINE ==> 77     ja       rel8              none
            r"^(\s*)ja(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "ja rel8",
                "opcodes": [int(0x77), ],
                "flags": "none"},
            # LINE ==>        jnbe
            r"^(\s*)ja(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "ja rel8",
                "opcodes": [int(0x77), ],
                "flags": "none"},
            # LINE ==> 78     js       rel8              none
            r"^(\s*)js(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "js rel8",
                "opcodes": [int(0x78), ],
                "flags": "none"},
            # LINE ==> 79     jns      rel8              none
            r"^(\s*)jns(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jns rel8",
                "opcodes": [int(0x79), ],
                "flags": "none"},
            # LINE ==> 7A     jp       rel8              none
            r"^(\s*)jp(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jp rel8",
                "opcodes": [int(0x7A), ],
                "flags": "none"},
            # LINE ==>        jpe
            r"^(\s*)jp(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jp rel8",
                "opcodes": [int(0x7A), ],
                "flags": "none"},
            # LINE ==> 7B     jnp      rel8              none
            r"^(\s*)jnp(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jnp rel8",
                "opcodes": [int(0x7B), ],
                "flags": "none"},
            # LINE ==>        jpo
            r"^(\s*)jnp(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jnp rel8",
                "opcodes": [int(0x7B), ],
                "flags": "none"},
            # LINE ==> 7C     jl       rel8              none
            r"^(\s*)jl(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jl rel8",
                "opcodes": [int(0x7C), ],
                "flags": "none"},
            # LINE ==>        jnge
            r"^(\s*)jl(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jl rel8",
                "opcodes": [int(0x7C), ],
                "flags": "none"},
            # LINE ==> 7D     jge      rel8              none
            r"^(\s*)jge(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jge rel8",
                "opcodes": [int(0x7D), ],
                "flags": "none"},
            # LINE ==>        jnl
            r"^(\s*)jge(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jge rel8",
                "opcodes": [int(0x7D), ],
                "flags": "none"},
            # LINE ==> 7E     jle      rel8              none
            r"^(\s*)jle(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jle rel8",
                "opcodes": [int(0x7E), ],
                "flags": "none"},
            # LINE ==>        jng
            r"^(\s*)jle(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jle rel8",
                "opcodes": [int(0x7E), ],
                "flags": "none"},
            # LINE ==> 7F     jg       rel8              none
            r"^(\s*)jg(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jg rel8",
                "opcodes": [int(0x7F), ],
                "flags": "none"},
            # LINE ==>        jnle
            r"^(\s*)jg(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jg rel8",
                "opcodes": [int(0x7F), ],
                "flags": "none"},
            # LINE ==> 80     adc      reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "adc reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     adc      mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "adc mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     add      reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "add reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     add      mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "add mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     and      reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "and reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     and      mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "and mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     cmp      reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "cmp reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     cmp      mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "cmp mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     or       reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "or reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     or       mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "or mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     sbb      reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "sbb reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     sbb      mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "sbb mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     sub      reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "sub reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     sub      mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "sub mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     xor      reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "xor reg8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 80     xor      mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "xor mem8,imm8",
                "opcodes": [int(0x80), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     adc      reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "adc reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)adc(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "adc reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     adc      mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "adc mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)adc(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "adc mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     add      reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "add reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)add(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "add reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     add      mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "add mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)add(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "add mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     and      reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "and reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)and(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "and reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     and      mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "and mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)and(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "and mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     cmp      reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "cmp reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)cmp(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "cmp reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     cmp      mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "cmp mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)cmp(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "cmp mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     or       reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "or reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)or(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "or reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     or       mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "or mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)or(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "or mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     sbb      reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "sbb reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)sbb(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "sbb reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     sbb      mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "sbb mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)sbb(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "sbb mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     sub      reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "sub reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)sub(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "sub reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     sub      mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "sub mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)sub(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "sub mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     xor      reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "xor reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)xor(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "xor reg16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 81     xor      mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "xor mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)xor(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "xor mem16,imm16",
                "opcodes": [int(0x81), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     adc      reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "adc reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)adc(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "adc reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     adc      mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)adc(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "adc mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)adc(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "adc mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     add      reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "add reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)add(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "add reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     add      mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)add(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "add mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)add(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "add mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     and      reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "and reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)and(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "and reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     and      mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)and(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "and mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)and(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "and mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     cmp      reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "cmp reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)cmp(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "cmp reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     cmp      mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)cmp(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "cmp mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)cmp(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "cmp mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     or       reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "or reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)or(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "or reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     or       mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)or(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "or mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)or(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "or mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     sbb      reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "sbb reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)sbb(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "sbb reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     sbb      mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)sbb(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "sbb mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)sbb(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "sbb mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     sub      reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "sub reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)sub(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "sub reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     sub      mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)sub(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "sub mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)sub(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "sub mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     xor      reg16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "xor reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm8
            r"^(\s*)xor(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "xor reg16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 83     xor      mem16,imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)xor(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "xor mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm8
            r"^(\s*)xor(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "xor mem16,imm8",
                "opcodes": [int(0x83), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 84     test     reg8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "test reg8,reg8",
                "opcodes": [int(0x84), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 84     test     mem8,reg8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "test mem8,reg8",
                "opcodes": [int(0x84), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 85     test     reg16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "test reg16,reg16",
                "opcodes": [int(0x85), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)test(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "test reg16,reg16",
                "opcodes": [int(0x85), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 85     test     mem16,reg16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "test mem16,reg16",
                "opcodes": [int(0x85), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)test(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "test mem16,reg16",
                "opcodes": [int(0x85), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> 86     xchg     reg8,reg8         none
            r"^(\s*)xchg(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "xchg reg8,reg8",
                "opcodes": [int(0x86), ],
                "flags": "none"},
            # LINE ==> 86     xchg     reg8,mem8         none
            r"^(\s*)xchg(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "xchg reg8,mem8",
                "opcodes": [int(0x86), ],
                "flags": "none"},
            # LINE ==> 87     xchg     reg16,reg16       none
            r"^(\s*)xchg(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "xchg reg16,reg16",
                "opcodes": [int(0x87), ],
                "flags": "none"},
            # LINE ==> 87     xchg     reg16,mem16       none
            r"^(\s*)xchg(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "xchg reg16,mem16",
                "opcodes": [int(0x87), ],
                "flags": "none"},
            # LINE ==> 88     mov      mem8,reg8         none
            r"^(\s*)mov(\s+)[0-9a-f]{2}[abcd][hl],(\s+)": {
                "mnemonic": "mov mem8,reg8",
                "opcodes": [int(0x88), ],
                "flags": "none"},
            # LINE ==> 89     mov      mem16,reg16       none
            r"^(\s*)mov(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "mov mem16,reg16",
                "opcodes": [int(0x89), ],
                "flags": "none"},
            # LINE ==>                 mem32,reg32
            r"^(\s*)mov(\s+)[0-9a-f]{4}[abcd]x,(\s+)": {
                "mnemonic": "mov mem16,reg16",
                "opcodes": [int(0x89), ],
                "flags": "none"},
            # LINE ==> 8A     mov      reg8,reg8         none
            r"^(\s*)mov(\s+)[abcd][hl][abcd][hl],(\s+)": {
                "mnemonic": "mov reg8,reg8",
                "opcodes": [int(0x8A), ],
                "flags": "none"},
            # LINE ==> 8A     mov      reg8,mem8         none
            r"^(\s*)mov(\s+)[abcd][hl][0-9a-f]{2},(\s+)": {
                "mnemonic": "mov reg8,mem8",
                "opcodes": [int(0x8A), ],
                "flags": "none"},
            # LINE ==> 8B     mov      reg16,reg16       none
            r"^(\s*)mov(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "mov reg16,reg16",
                "opcodes": [int(0x8B), ],
                "flags": "none"},
            # LINE ==>                 reg32,reg32
            r"^(\s*)mov(\s+)[abcd]x[abcd]x,(\s+)": {
                "mnemonic": "mov reg16,reg16",
                "opcodes": [int(0x8B), ],
                "flags": "none"},
            # LINE ==> 8B     mov      reg16,mem16       none
            r"^(\s*)mov(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "mov reg16,mem16",
                "opcodes": [int(0x8B), ],
                "flags": "none"},
            # LINE ==>                 reg32,mem32
            r"^(\s*)mov(\s+)[abcd]x[0-9a-f]{4},(\s+)": {
                "mnemonic": "mov reg16,mem16",
                "opcodes": [int(0x8B), ],
                "flags": "none"},
            # LINE ==> 8C     mov      reg16, sreg       none
            r"^(\s*)mov(\s+)[abcd]x,(\s+)": {
                "mnemonic": "mov reg16, sreg",
                "opcodes": [int(0x8C), ],
                "flags": "none"},
            # LINE ==> 8C     mov      mem16,sreg        none
            r"^(\s*)mov(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "mov mem16,sreg",
                "opcodes": [int(0x8C), ],
                "flags": "none"},
            # LINE ==> 8D     lea      reg32,mem32       none
            r"^(\s*)lea(\s+)e[abcd]x[0-9a-f]{8},(\s+)": {
                "mnemonic": "lea reg32,mem32",
                "opcodes": [int(0x8D), ],
                "flags": "none"},
            # LINE ==> 8E     mov      sreg, reg16       none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov sreg, reg16",
                "opcodes": [int(0x8E), ],
                "flags": "none"},
            # LINE ==> 8E     mov      sreg,mem16        none
            r"^(\s*)mov(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "mov sreg,mem16",
                "opcodes": [int(0x8E), ],
                "flags": "none"},
            # LINE ==> 8F     pop      mem16             none
            r"^(\s*)pop(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "pop mem16",
                "opcodes": [int(0x8F), ],
                "flags": "none"},
            # LINE ==>                 mem32
            r"^(\s*)pop(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "pop mem16",
                "opcodes": [int(0x8F), ],
                "flags": "none"},
            # LINE ==> 91     xchg     AX, CX            none
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, CX",
                "opcodes": [int(0x91), ],
                "flags": "none"},
            # LINE ==>                 EAX, ECX
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, CX",
                "opcodes": [int(0x91), ],
                "flags": "none"},
            # LINE ==> 92     xchg     AX, DX            none
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, DX",
                "opcodes": [int(0x92), ],
                "flags": "none"},
            # LINE ==>                 EAX, EDX
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, DX",
                "opcodes": [int(0x92), ],
                "flags": "none"},
            # LINE ==> 93     xchg     AX, BX            none
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, BX",
                "opcodes": [int(0x93), ],
                "flags": "none"},
            # LINE ==>                 EAX, EBX
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, BX",
                "opcodes": [int(0x93), ],
                "flags": "none"},
            # LINE ==> 94     xchg     AX, SP            none
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, SP",
                "opcodes": [int(0x94), ],
                "flags": "none"},
            # LINE ==>                 EAX, ESP
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, SP",
                "opcodes": [int(0x94), ],
                "flags": "none"},
            # LINE ==> 95     xchg     AX, BP            none
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, BP",
                "opcodes": [int(0x95), ],
                "flags": "none"},
            # LINE ==>                 EAX, EBP
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, BP",
                "opcodes": [int(0x95), ],
                "flags": "none"},
            # LINE ==> 96     xchg     AX, SI            none
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, SI",
                "opcodes": [int(0x96), ],
                "flags": "none"},
            # LINE ==>                 EAX, ESI
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, SI",
                "opcodes": [int(0x96), ],
                "flags": "none"},
            # LINE ==> 97     xchg     AX, DI            none
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, DI",
                "opcodes": [int(0x97), ],
                "flags": "none"},
            # LINE ==>                 EAX, EDI
            r"^(\s*)xchg(\s+),(\s+)": {
                "mnemonic": "xchg AX, DI",
                "opcodes": [int(0x97), ],
                "flags": "none"},
            # LINE ==> 98     cbw      none              none
            r"^(\s*)cbw(\s+),(\s+)": {
                "mnemonic": "cbw none",
                "opcodes": [int(0x98), ],
                "flags": "none"},
            # LINE ==> 98     cwde     none              none
            r"^(\s*)cwde(\s+),(\s+)": {
                "mnemonic": "cwde none",
                "opcodes": [int(0x98), ],
                "flags": "none"},
            # LINE ==> 99     cdq      none              none
            r"^(\s*)cdq(\s+),(\s+)": {
                "mnemonic": "cdq none",
                "opcodes": [int(0x99), ],
                "flags": "none"},
            # LINE ==> 99     cwd      none              none
            r"^(\s*)cwd(\s+),(\s+)": {
                "mnemonic": "cwd none",
                "opcodes": [int(0x99), ],
                "flags": "none"},
            # LINE ==> 9A     call     far direct        none
            r"^(\s*)call(\s+),(\s+)": {
                "mnemonic": "call far direct",
                "opcodes": [int(0x9A), ],
                "flags": "none"},
            # LINE ==> 9C     pushf    none              none
            r"^(\s*)pushf(\s+),(\s+)": {
                "mnemonic": "pushf none",
                "opcodes": [int(0x9C), ],
                "flags": "none"},
            # LINE ==>        pushfd
            r"^(\s*)pushf(\s+),(\s+)": {
                "mnemonic": "pushf none",
                "opcodes": [int(0x9C), ],
                "flags": "none"},
            # LINE ==> 9D     popf     none              none
            r"^(\s*)popf(\s+),(\s+)": {
                "mnemonic": "popf none",
                "opcodes": [int(0x9D), ],
                "flags": "none"},
            # LINE ==>        popfd
            r"^(\s*)popf(\s+),(\s+)": {
                "mnemonic": "popf none",
                "opcodes": [int(0x9D), ],
                "flags": "none"},
            # LINE ==> A0     mov      AL, direct        none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov AL, direct",
                "opcodes": [int(0xA0), ],
                "flags": "none"},
            # LINE ==> A1     mov      AX, direct        none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov AX, direct",
                "opcodes": [int(0xA1), ],
                "flags": "none"},
            # LINE ==>                 EAX, direct
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov AX, direct",
                "opcodes": [int(0xA1), ],
                "flags": "none"},
            # LINE ==> A2     mov      direct ,AL        none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov direct ,AL",
                "opcodes": [int(0xA2), ],
                "flags": "none"},
            # LINE ==> A3     mov      direct, AX        none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov direct, AX",
                "opcodes": [int(0xA3), ],
                "flags": "none"},
            # LINE ==>                 direct, EAX
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov direct, AX",
                "opcodes": [int(0xA3), ],
                "flags": "none"},
            # LINE ==> A4     movsb    none              none
            r"^(\s*)movsb(\s+),(\s+)": {
                "mnemonic": "movsb none",
                "opcodes": [int(0xA4), ],
                "flags": "none"},
            # LINE ==> A5     movsw    none              none
            r"^(\s*)movsw(\s+),(\s+)": {
                "mnemonic": "movsw none",
                "opcodes": [int(0xA5), ],
                "flags": "none"},
            # LINE ==>        movsd
            r"^(\s*)movsw(\s+),(\s+)": {
                "mnemonic": "movsw none",
                "opcodes": [int(0xA5), ],
                "flags": "none"},
            # LINE ==> A6     cmpsb    none              none
            r"^(\s*)cmpsb(\s+),(\s+)": {
                "mnemonic": "cmpsb none",
                "opcodes": [int(0xA6), ],
                "flags": "none"},
            # LINE ==> A7     cmpsw    none              none
            r"^(\s*)cmpsw(\s+),(\s+)": {
                "mnemonic": "cmpsw none",
                "opcodes": [int(0xA7), ],
                "flags": "none"},
            # LINE ==>        cmpsd
            r"^(\s*)cmpsw(\s+),(\s+)": {
                "mnemonic": "cmpsw none",
                "opcodes": [int(0xA7), ],
                "flags": "none"},
            # LINE ==> A8     test     AL,imm8           SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)al,(\s+)": {
                "mnemonic": "test AL,imm8",
                "opcodes": [int(0xA8), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> A9     test     AX,imm16          SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)ax,(\s+)": {
                "mnemonic": "test AX,imm16",
                "opcodes": [int(0xA9), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 EAX,imm32
            r"^(\s*)test(\s+)ax,(\s+)": {
                "mnemonic": "test AX,imm16",
                "opcodes": [int(0xA9), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> AA     stosb    none              none
            r"^(\s*)stosb(\s+),(\s+)": {
                "mnemonic": "stosb none",
                "opcodes": [int(0xAA), ],
                "flags": "none"},
            # LINE ==> AB     stosw    none              none
            r"^(\s*)stosw(\s+),(\s+)": {
                "mnemonic": "stosw none",
                "opcodes": [int(0xAB), ],
                "flags": "none"},
            # LINE ==>        stosd
            r"^(\s*)stosw(\s+),(\s+)": {
                "mnemonic": "stosw none",
                "opcodes": [int(0xAB), ],
                "flags": "none"},
            # LINE ==> AC     lodsb    none              none
            r"^(\s*)lodsb(\s+),(\s+)": {
                "mnemonic": "lodsb none",
                "opcodes": [int(0xAC), ],
                "flags": "none"},
            # LINE ==> AD     lodsw    none              none
            r"^(\s*)lodsw(\s+),(\s+)": {
                "mnemonic": "lodsw none",
                "opcodes": [int(0xAD), ],
                "flags": "none"},
            # LINE ==>        lodsd
            r"^(\s*)lodsw(\s+),(\s+)": {
                "mnemonic": "lodsw none",
                "opcodes": [int(0xAD), ],
                "flags": "none"},
            # LINE ==> AE     scasb    none              none
            r"^(\s*)scasb(\s+),(\s+)": {
                "mnemonic": "scasb none",
                "opcodes": [int(0xAE), ],
                "flags": "none"},
            # LINE ==> AE     scasw    none              none
            r"^(\s*)scasw(\s+),(\s+)": {
                "mnemonic": "scasw none",
                "opcodes": [int(0xAE), ],
                "flags": "none"},
            # LINE ==>        scasd
            r"^(\s*)scasw(\s+),(\s+)": {
                "mnemonic": "scasw none",
                "opcodes": [int(0xAE), ],
                "flags": "none"},
            # LINE ==> B0     mov      AL, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov AL, imm8",
                "opcodes": [int(0xB0), ],
                "flags": "none"},
            # LINE ==> B1     mov      CL, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov CL, imm8",
                "opcodes": [int(0xB1), ],
                "flags": "none"},
            # LINE ==> B2     mov      DL, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov DL, imm8",
                "opcodes": [int(0xB2), ],
                "flags": "none"},
            # LINE ==> B3     mov      BL, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov BL, imm8",
                "opcodes": [int(0xB3), ],
                "flags": "none"},
            # LINE ==> B4     mov      AH, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov AH, imm8",
                "opcodes": [int(0xB4), ],
                "flags": "none"},
            # LINE ==> B5     mov      CH, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov CH, imm8",
                "opcodes": [int(0xB5), ],
                "flags": "none"},
            # LINE ==> B6     mov      DH, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov DH, imm8",
                "opcodes": [int(0xB6), ],
                "flags": "none"},
            # LINE ==> B7     mov      BH, imm8          none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov BH, imm8",
                "opcodes": [int(0xB7), ],
                "flags": "none"},
            # LINE ==> B8     mov      AX, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov AX, imm16",
                "opcodes": [int(0xB8), ],
                "flags": "none"},
            # LINE ==>                 EAX, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov AX, imm16",
                "opcodes": [int(0xB8), ],
                "flags": "none"},
            # LINE ==> B9     mov      CX, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov CX, imm16",
                "opcodes": [int(0xB9), ],
                "flags": "none"},
            # LINE ==>                 ECX, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov CX, imm16",
                "opcodes": [int(0xB9), ],
                "flags": "none"},
            # LINE ==> BA     mov      DX, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov DX, imm16",
                "opcodes": [int(0xBA), ],
                "flags": "none"},
            # LINE ==>                 EDX, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov DX, imm16",
                "opcodes": [int(0xBA), ],
                "flags": "none"},
            # LINE ==> BB     mov      BX, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov BX, imm16",
                "opcodes": [int(0xBB), ],
                "flags": "none"},
            # LINE ==>                 EBX, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov BX, imm16",
                "opcodes": [int(0xBB), ],
                "flags": "none"},
            # LINE ==> BC     mov      SP, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov SP, imm16",
                "opcodes": [int(0xBC), ],
                "flags": "none"},
            # LINE ==>                 ESP, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov SP, imm16",
                "opcodes": [int(0xBC), ],
                "flags": "none"},
            # LINE ==> BD     mov      BP, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov BP, imm16",
                "opcodes": [int(0xBD), ],
                "flags": "none"},
            # LINE ==>                 EPB, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov BP, imm16",
                "opcodes": [int(0xBD), ],
                "flags": "none"},
            # LINE ==> BE     mov      SI, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov SI, imm16",
                "opcodes": [int(0xBE), ],
                "flags": "none"},
            # LINE ==>                 ESI, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov SI, imm16",
                "opcodes": [int(0xBE), ],
                "flags": "none"},
            # LINE ==> BF     mov      DI, imm16         none
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov DI, imm16",
                "opcodes": [int(0xBF), ],
                "flags": "none"},
            # LINE ==>                 EDI, imm32
            r"^(\s*)mov(\s+),(\s+)": {
                "mnemonic": "mov DI, imm16",
                "opcodes": [int(0xBF), ],
                "flags": "none"},
            # LINE ==> C0     rol      reg8, imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)rol(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "rol reg8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>        ror
            r"^(\s*)rol(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "rol reg8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> C0     rol      mem8, imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)rol(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "rol mem8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>        ror
            r"^(\s*)rol(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "rol mem8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> C0     shl sal  reg8, imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>        shr
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> C0     shl sal  mem8, imm8        SF,ZF,OF,CF,PF,AF
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>        shr
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8, imm8",
                "opcodes": [int(0xC0), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> C1     rol      reg16,imm8        SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "rol reg16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror      reg32,imm8        AF
            r"^(\s*)rol(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "rol reg16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> C1     rol      mem16,imm8        SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "rol mem16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror      mem32,imm8        AF
            r"^(\s*)rol(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "rol mem16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> C1     shl sal  reg16,imm8        SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "shl sal reg16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr      reg32,imm8        AF
            r"^(\s*)shl sal(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "shl sal reg16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[abcd]xal,(\s+)": {
                "mnemonic": "shl sal reg16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> C1     shl sal  mem16,imm8        SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "shl sal mem16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr      mem32,imm8        AF
            r"^(\s*)shl sal(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "shl sal mem16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[0-9a-f]{4}al,(\s+)": {
                "mnemonic": "shl sal mem16,imm8",
                "opcodes": [int(0xC1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> C2     ret      imm16             none
            r"^(\s*)ret(\s+)ax,(\s+)": {
                "mnemonic": "ret imm16",
                "opcodes": [int(0xC2), ],
                "flags": "none"},
            # LINE ==> C3     ret      none              none
            r"^(\s*)ret(\s+),(\s+)": {
                "mnemonic": "ret none",
                "opcodes": [int(0xC3), ],
                "flags": "none"},
            # LINE ==> C6     mov      mem8, imm8        none
            r"^(\s*)mov(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "mov mem8, imm8",
                "opcodes": [int(0xC6), ],
                "flags": "none"},
            # LINE ==> C7     mov      mem16,imm16       none
            r"^(\s*)mov(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "mov mem16,imm16",
                "opcodes": [int(0xC7), ],
                "flags": "none"},
            # LINE ==>                 mem32,imm32       6+
            r"^(\s*)mov(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "mov mem16,imm16",
                "opcodes": [int(0xC7), ],
                "flags": "none"},
            # LINE ==> CA     ret      imm16             none
            r"^(\s*)ret(\s+)ax,(\s+)": {
                "mnemonic": "ret imm16",
                "opcodes": [int(0xCA), ],
                "flags": "none"},
            # LINE ==> CB     ret      none              none
            r"^(\s*)ret(\s+),(\s+)": {
                "mnemonic": "ret none",
                "opcodes": [int(0xCB), ],
                "flags": "none"},
            # LINE ==> D0     rol      reg8              SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "rol reg8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror                        AF
            r"^(\s*)rol(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "rol reg8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D0     rol      mem8              SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "rol mem8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror                        AF
            r"^(\s*)rol(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "rol mem8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D0     shl sal  reg8              SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr                        AF
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D0     shl sal  mem8              SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr                        AF
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8",
                "opcodes": [int(0xD0), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D1     rol      reg16             SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[abcd]x,(\s+)": {
                "mnemonic": "rol reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror      reg32             AF
            r"^(\s*)rol(\s+)[abcd]x,(\s+)": {
                "mnemonic": "rol reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D1     rol      reg16             SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[abcd]x,(\s+)": {
                "mnemonic": "rol reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror      reg32             AF
            r"^(\s*)rol(\s+)[abcd]x,(\s+)": {
                "mnemonic": "rol reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D1     shl sal  reg16             SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr      reg32             AF
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D1     shl sal  reg16             SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr      reg32             AF
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16",
                "opcodes": [int(0xD1), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D2     rol      reg8, CL          SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "rol reg8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror      AF
            r"^(\s*)rol(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "rol reg8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D2     rol      mem8, CL          SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "rol mem8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror                        AF
            r"^(\s*)rol(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "rol mem8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D2     shl sal  reg8, CL          SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr                        AF
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "shl sal reg8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D2     shl sal  mem8, CL          SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr                        AF
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "shl sal mem8, CL",
                "opcodes": [int(0xD2), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D3     rol      reg16,CL          SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[abcd]x,(\s+)": {
                "mnemonic": "rol reg16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror      reg32,CL          AF
            r"^(\s*)rol(\s+)[abcd]x,(\s+)": {
                "mnemonic": "rol reg16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D3     rol      mem16,CL          SF,ZF,OF,CF,PF
            r"^(\s*)rol(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "rol mem16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        ror      mem32,CL          AF
            r"^(\s*)rol(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "rol mem16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D3     shl sal  reg16,CL          SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr      reg32,CL          AF
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[abcd]x,(\s+)": {
                "mnemonic": "shl sal reg16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D3     shl sal  mem16,CL          SF,ZF,OF,CF,PF
            r"^(\s*)shl sal(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "shl sal mem16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        shr      mem32,CL          AF
            r"^(\s*)shl sal(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "shl sal mem16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==>        sar
            r"^(\s*)shl sal(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "shl sal mem16,CL",
                "opcodes": [int(0xD3), ],
                "flags": "SF,ZF,OF,CF,PF"},
            # LINE ==> D4 0A  aam      none              SF,ZF,PF
            r"^(\s*)aam(\s+),(\s+)": {
                "mnemonic": "aam none",
                "opcodes": [int(0xD4), int(0x0A), ],
                "flags": "SF,ZF,PF"},
            # LINE ==>                                   OF,AF,CF
            r"^(\s*)aam(\s+),(\s+)": {
                "mnemonic": "aam none",
                "opcodes": [int(0xD4), int(0x0A), ],
                "flags": "SF,ZF,PF"},
            # LINE ==> D5 0A  aad      none              SF,ZF,PF
            r"^(\s*)aad(\s+),(\s+)": {
                "mnemonic": "aad none",
                "opcodes": [int(0xD5), int(0x0A), ],
                "flags": "SF,ZF,PF"},
            # LINE ==>                                   OF,AF,CF
            r"^(\s*)aad(\s+),(\s+)": {
                "mnemonic": "aad none",
                "opcodes": [int(0xD5), int(0x0A), ],
                "flags": "SF,ZF,PF"},
            # LINE ==> D7     xlat     none              none
            r"^(\s*)xlat(\s+),(\s+)": {
                "mnemonic": "xlat none",
                "opcodes": [int(0xD7), ],
                "flags": "none"},
            # LINE ==> E0     loopne   none              none
            r"^(\s*)loopne(\s+),(\s+)": {
                "mnemonic": "loopne none",
                "opcodes": [int(0xE0), ],
                "flags": "none"},
            # LINE ==>        loopnz
            r"^(\s*)loopne(\s+),(\s+)": {
                "mnemonic": "loopne none",
                "opcodes": [int(0xE0), ],
                "flags": "none"},
            # LINE ==> E1     loope    none              none
            r"^(\s*)loope(\s+),(\s+)": {
                "mnemonic": "loope none",
                "opcodes": [int(0xE1), ],
                "flags": "none"},
            # LINE ==>        loopz
            r"^(\s*)loope(\s+),(\s+)": {
                "mnemonic": "loope none",
                "opcodes": [int(0xE1), ],
                "flags": "none"},
            # LINE ==> E2     loop     none              none
            r"^(\s*)loop(\s+),(\s+)": {
                "mnemonic": "loop none",
                "opcodes": [int(0xE2), ],
                "flags": "none"},
            # LINE ==> E3     jecxz    rel8              none
            r"^(\s*)jecxz(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jecxz rel8",
                "opcodes": [int(0xE3), ],
                "flags": "none"},
            # LINE ==> E8     call     rel32             none
            r"^(\s*)call(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "call rel32",
                "opcodes": [int(0xE8), ],
                "flags": "none"},
            # LINE ==> E9     jmp      rel32             none
            r"^(\s*)jmp(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jmp rel32",
                "opcodes": [int(0xE9), ],
                "flags": "none"},
            # LINE ==> EB     jmp      rel8              none
            r"^(\s*)jmp(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "jmp rel8",
                "opcodes": [int(0xEB), ],
                "flags": "none"},
            # LINE ==> F2     repnz    none              none
            r"^(\s*)repnz(\s+),(\s+)": {
                "mnemonic": "repnz none",
                "opcodes": [int(0xF2), ],
                "flags": "none"},
            # LINE ==>        repne

            r"^(\s*)repnz(\s+),(\s+)": {
                "mnemonic": "repnz none",
                "opcodes": [int(0xF2), ],
                "flags": "none"},
            # LINE ==> F2 A6  repne    none              none
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xA6), ],
                "flags": "none"},
            # LINE ==>        cmpsb
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xA6), ],
                "flags": "none"},
            # LINE ==> F2 A7  repne    none              none
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        cmpsw
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        repne
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        cmpsd
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xA7), ],
                "flags": "none"},
            # LINE ==> F2 AE  repne    none              none
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xAE), ],
                "flags": "none"},
            # LINE ==>        scasb
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xAE), ],
                "flags": "none"},
            # LINE ==> F2 AF  repne    none              none
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xAF), ],
                "flags": "none"},
            # LINE ==>        scasw
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xAF), ],
                "flags": "none"},
            # LINE ==>        repne
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xAF), ],
                "flags": "none"},
            # LINE ==>        scasd
            r"^(\s*)repne(\s+),(\s+)": {
                "mnemonic": "repne none",
                "opcodes": [int(0xF2), int(0xAF), ],
                "flags": "none"},
            # LINE ==> F3     rep      none              none
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), ],
                "flags": "none"},
            # LINE ==>        repz
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), ],
                "flags": "none"},
            # LINE ==>        repe

            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), ],
                "flags": "none"},
            # LINE ==> F3 A4  rep      none              none
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA4), ],
                "flags": "none"},
            # LINE ==>        movsb
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA4), ],
                "flags": "none"},
            # LINE ==> F3 A5  rep      none              none
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA5), ],
                "flags": "none"},
            # LINE ==>        movsw
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA5), ],
                "flags": "none"},
            # LINE ==>        rep
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA5), ],
                "flags": "none"},
            # LINE ==>        movsd
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA5), ],
                "flags": "none"},
            # LINE ==> F3 A6  rep      none              none
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA6), ],
                "flags": "none"},
            # LINE ==>        stosb

            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA6), ],
                "flags": "none"},
            # LINE ==> F3 A6  repe     none              none
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xA6), ],
                "flags": "none"},
            # LINE ==>        cmpsb
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xA6), ],
                "flags": "none"},
            # LINE ==> F3 A7  rep      none              none
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        stosw

            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        rep      stosd
            r"^(\s*)rep(\s+),(\s+)": {
                "mnemonic": "rep none",
                "opcodes": [int(0xF3), int(0xA7), ],
                "flags": "none"},
            # LINE ==> F3 A7  repe     none              none
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        cmpsw
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        repe
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xA7), ],
                "flags": "none"},
            # LINE ==>        cmpsd
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xA7), ],
                "flags": "none"},
            # LINE ==> F3 AE  repe     none              none
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xAE), ],
                "flags": "none"},
            # LINE ==>        scasb
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xAE), ],
                "flags": "none"},
            # LINE ==> F3 AF  repe     none              none
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xAF), ],
                "flags": "none"},
            # LINE ==>        scasw
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xAF), ],
                "flags": "none"},
            # LINE ==>        repe
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xAF), ],
                "flags": "none"},
            # LINE ==>        scasd
            r"^(\s*)repe(\s+),(\s+)": {
                "mnemonic": "repe none",
                "opcodes": [int(0xF3), int(0xAF), ],
                "flags": "none"},
            # LINE ==> F5     cmc      none              CF
            r"^(\s*)cmc(\s+),(\s+)": {
                "mnemonic": "cmc none",
                "opcodes": [int(0xF5), ],
                "flags": "CF"},
            # LINE ==> F6     div      reg8              SF,ZF,OF,PF,AF
            r"^(\s*)div(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "div reg8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F6     div      mem8              SF,ZF,OF,PF,AF
            r"^(\s*)div(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "div mem8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F6     idiv     reg8              SF,ZF,OF,PF,AF
            r"^(\s*)idiv(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "idiv reg8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F6     idiv     mem8              SF,ZF,OF,PF,AF
            r"^(\s*)idiv(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "idiv mem8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F6     imul     reg8              OF,CF
            r"^(\s*)imul(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "imul reg8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==>                                   SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "imul reg8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==> F6     imul     mem8              OF,CF
            r"^(\s*)imul(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "imul mem8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==>                                   SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "imul mem8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==> F6     mul      reg8              OF,CF
            r"^(\s*)mul(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "mul reg8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==>                                   SF,ZF, PF,AF
            r"^(\s*)mul(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "mul reg8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==> F6     mul      mem8              OF,CF
            r"^(\s*)mul(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "mul mem8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==>                                   SF,ZF, PF,AF
            r"^(\s*)mul(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "mul mem8",
                "opcodes": [int(0xF6), ],
                "flags": "OF,CF"},
            # LINE ==> F6     neg      reg8              SF,ZF,OF,CF,PF,AF
            r"^(\s*)neg(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "neg reg8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F6     neg      mem8              SF,ZF,OF,CF,PF,AF
            r"^(\s*)neg(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "neg mem8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F6     not      reg8              none
            r"^(\s*)not(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "not reg8",
                "opcodes": [int(0xF6), ],
                "flags": "none"},
            # LINE ==> F6     not      mem8              none
            r"^(\s*)not(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "not mem8",
                "opcodes": [int(0xF6), ],
                "flags": "none"},
            # LINE ==> F6     test     reg8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[abcd][hl]al,(\s+)": {
                "mnemonic": "test reg8,imm8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F6     test     mem8,imm8         SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[0-9a-f]{2}al,(\s+)": {
                "mnemonic": "test mem8,imm8",
                "opcodes": [int(0xF6), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F7     div      reg16             SF,ZF,OF,PF,AF
            r"^(\s*)div(\s+)[abcd]x,(\s+)": {
                "mnemonic": "div reg16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 reg32
            r"^(\s*)div(\s+)[abcd]x,(\s+)": {
                "mnemonic": "div reg16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F7     div      mem16             SF,ZF,OF,PF,AF
            r"^(\s*)div(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "div mem16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 mem32
            r"^(\s*)div(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "div mem16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F7     idiv     reg16             SF,ZF,OF,PF,AF
            r"^(\s*)idiv(\s+)[abcd]x,(\s+)": {
                "mnemonic": "idiv reg16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 reg32
            r"^(\s*)idiv(\s+)[abcd]x,(\s+)": {
                "mnemonic": "idiv reg16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F7     idiv     mem16             SF,ZF,OF,PF,AF
            r"^(\s*)idiv(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "idiv mem16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 mem32
            r"^(\s*)idiv(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "idiv mem16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> F7     imul     reg16             OF,CF
            r"^(\s*)imul(\s+)[abcd]x,(\s+)": {
                "mnemonic": "imul reg16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32             SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[abcd]x,(\s+)": {
                "mnemonic": "imul reg16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==> F7     imul     mem16             OF,CF
            r"^(\s*)imul(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "imul mem16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==>                 mem32             SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "imul mem16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==> F7     imul     mem16             OF,CF
            r"^(\s*)imul(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "imul mem16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==>                 mem32             SF,ZF, PF,AF
            r"^(\s*)imul(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "imul mem16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==> F7     mul      reg16             OF,CF
            r"^(\s*)mul(\s+)[abcd]x,(\s+)": {
                "mnemonic": "mul reg16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==>                 reg32             SF,ZF, PF,AF
            r"^(\s*)mul(\s+)[abcd]x,(\s+)": {
                "mnemonic": "mul reg16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==> F7     mul      mem16             OF,CF
            r"^(\s*)mul(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "mul mem16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==>                 mem32             SF,ZF, PF,AF
            r"^(\s*)mul(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "mul mem16",
                "opcodes": [int(0xF7), ],
                "flags": "OF,CF"},
            # LINE ==> F7     neg      reg16             SF,ZF,OF,CF,PF,AF
            r"^(\s*)neg(\s+)[abcd]x,(\s+)": {
                "mnemonic": "neg reg16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32
            r"^(\s*)neg(\s+)[abcd]x,(\s+)": {
                "mnemonic": "neg reg16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F7     neg      mem16             SF,ZF,OF,CF,PF,AF
            r"^(\s*)neg(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "neg mem16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32
            r"^(\s*)neg(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "neg mem16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F7     not      reg16             none
            r"^(\s*)not(\s+)[abcd]x,(\s+)": {
                "mnemonic": "not reg16",
                "opcodes": [int(0xF7), ],
                "flags": "none"},
            # LINE ==>                 reg32
            r"^(\s*)not(\s+)[abcd]x,(\s+)": {
                "mnemonic": "not reg16",
                "opcodes": [int(0xF7), ],
                "flags": "none"},
            # LINE ==> F7     not      mem16             none
            r"^(\s*)not(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "not mem16",
                "opcodes": [int(0xF7), ],
                "flags": "none"},
            # LINE ==>                 mem32
            r"^(\s*)not(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "not mem16",
                "opcodes": [int(0xF7), ],
                "flags": "none"},
            # LINE ==> F7     test     reg16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "test reg16,imm16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 reg32,imm32
            r"^(\s*)test(\s+)[abcd]xax,(\s+)": {
                "mnemonic": "test reg16,imm16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F7     test     mem16,imm16       SF,ZF,OF,CF,PF,AF
            r"^(\s*)test(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "test mem16,imm16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==>                 mem32,imm32
            r"^(\s*)test(\s+)[0-9a-f]{4}ax,(\s+)": {
                "mnemonic": "test mem16,imm16",
                "opcodes": [int(0xF7), ],
                "flags": "SF,ZF,OF,CF,PF,AF"},
            # LINE ==> F8     clc      none              CF
            r"^(\s*)clc(\s+),(\s+)": {
                "mnemonic": "clc none",
                "opcodes": [int(0xF8), ],
                "flags": "CF"},
            # LINE ==> F9     stc      none              CF
            r"^(\s*)stc(\s+),(\s+)": {
                "mnemonic": "stc none",
                "opcodes": [int(0xF9), ],
                "flags": "CF"},
            # LINE ==> FC     cld      none              DF
            r"^(\s*)cld(\s+),(\s+)": {
                "mnemonic": "cld none",
                "opcodes": [int(0xFC), ],
                "flags": "DF"},
            # LINE ==> FD     std      none              DF
            r"^(\s*)std(\s+),(\s+)": {
                "mnemonic": "std none",
                "opcodes": [int(0xFD), ],
                "flags": "DF"},
            # LINE ==> FE     dec      reg8
            r"^(\s*)dec(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "dec reg8",
                "opcodes": [int(0xFE), ],
                "flags": ""},
            # LINE ==> FE     dec      mem8              SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "dec mem8",
                "opcodes": [int(0xFE), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> FE     inc      reg8              SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+)[abcd][hl],(\s+)": {
                "mnemonic": "inc reg8",
                "opcodes": [int(0xFE), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> FE     inc      mem8              SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+)[0-9a-f]{2},(\s+)": {
                "mnemonic": "inc mem8",
                "opcodes": [int(0xFE), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> FF     call     reg32             none
            r"^(\s*)call(\s+)e[abcd]x,(\s+)": {
                "mnemonic": "call reg32",
                "opcodes": [int(0xFF), ],
                "flags": "none"},
            # LINE ==> FF     call     mem32             none
            r"^(\s*)call(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "call mem32",
                "opcodes": [int(0xFF), ],
                "flags": "none"},
            # LINE ==> FF     call     far indirect      none
            r"^(\s*)call(\s+),(\s+)": {
                "mnemonic": "call far indirect",
                "opcodes": [int(0xFF), ],
                "flags": "none"},
            # LINE ==> FF     dec      mem16             SF,ZF,OF,PF,AF
            r"^(\s*)dec(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "dec mem16",
                "opcodes": [int(0xFF), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 mem32
            r"^(\s*)dec(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "dec mem16",
                "opcodes": [int(0xFF), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> FF     inc      mem16             SF,ZF,OF,PF,AF
            r"^(\s*)inc(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "inc mem16",
                "opcodes": [int(0xFF), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==>                 mem32
            r"^(\s*)inc(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "inc mem16",
                "opcodes": [int(0xFF), ],
                "flags": "SF,ZF,OF,PF,AF"},
            # LINE ==> FF     jmp      reg32             none
            r"^(\s*)jmp(\s+)e[abcd]x,(\s+)": {
                "mnemonic": "jmp reg32",
                "opcodes": [int(0xFF), ],
                "flags": "none"},
            # LINE ==> FF     jmp      mem32             none
            r"^(\s*)jmp(\s+)[0-9a-f]{8},(\s+)": {
                "mnemonic": "jmp mem32",
                "opcodes": [int(0xFF), ],
                "flags": "none"},
            # LINE ==> FF     push     mem16             none
            r"^(\s*)push(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "push mem16",
                "opcodes": [int(0xFF), ],
                "flags": "none"},
            # LINE ==>                 mem32
            r"^(\s*)push(\s+)[0-9a-f]{4},(\s+)": {
                "mnemonic": "push mem16",
                "opcodes": [int(0xFF), ],
                "flags": "none"},
        }

        # Control flags not implemented

    # TODO: Setter para los registros. Ya que los de uso general tienen contraparte de 8 bits.
    def set_register(self, reg, value: int):
        pass

    #  https://www.geeksforgeeks.org/python-program-to-add-two-binary-numbers/
    def _find_matches(self, d: {str}, item: str) -> Dict[str]:
        """

        Parameters:
            d {str}: Regex Dictionary
            item (str): Item to be look for.

        Returns:
            str: Item found, or None if not.

        """
        for k in d:
            if re.match(k, item):
                return d[k]

        return None

    def _16to8(self, hl: int) -> [int, int]:
        """Decode a 16-bit number in 2 8-bit numbers

        Parameters:
            hl (int): 16-bit numbers

        Returns:
            int, int: 8-bit higher part and 8-bit lower part, respectively.

        """
        h = int(hl / 256)
        l = h % 256

        return h, l

    @property
    def bits(self):
        return self._bits

    def asm_shr(self, x: int):
        rest, self.CY = x >> 1, x & 1
        return rest

    def asm_shl(self, x):
        rest, self.CY = x << 1, x & 1
        return rest

    def asm_not(self, a):
        return ~a

    def asm_or(self, a, b):
        return a | b

    def asm_xor(self, a, b):
        return a ^ b

    def asm_and(self, a, b):
        return a & b

    def asm_add(self, a, b):

        max_len = max(len(a), len(b))
        a = a.zfill(max_len)
        b = b.zfill(max_len)

        # Initialize the result
        result = ''

        # Traverse the string
        for i in range(max_len - 1, -1, -1):
            r = self.CY
            r += 1 if a[i] == '1' else 0
            r += 1 if b[i] == '1' else 0
            result = ('1' if r % 2 == 1 else '0') + result

            # Compute the carry.
            self.CY = 0 if r < 2 else 1

        if self != 0:
            result = '1' + result

        print(result.zfill(max_len))

        return a

    @staticmethod
    def _not_yet():
        print("This part of the CPU hasn't been implemented yet. =)")

    @dispatch(int)
    def get_bin(x: int) -> str:
        """Convert any integer into 8 bit binary format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 8 bit binary as string.
        """

        return format(int(x, 2), '08b')

    @dispatch(int, n=int)
    def get_bin(x: int, n: int = bits) -> str:
        """Convert any integer into n bit binary format.

        Parameters:
            x (int): The integer to be converted.
            n (int): Number of bits.

        Returns:
            str: n bit binary as string.
        """
        return format(x, '0' + str(n) + 'b')

    @dispatch(int)
    def get_hex(x: int) -> str:
        """Convert any integer into 16 bit hexadecimal format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 16 bit hexadecimal as string.
        """

        return format(x, '04X')

    def print_status_flags(self) -> None:
        """ Print the status of the flags. """
        print(
            f"SF={self.SF} ZF={self.ZF} CY={self.CY} PF={self.PF} OF={self.OF} CY={self.CY}")

    def print_registers(self) -> None:
        """ Print the CPU registers and it's value."""
        print(
            f"AX={self.get_bin(self.AX)} BX={self.get_bin(self.BX)}"
            f"  CX={self.get_bin(self.CX)}  DX={self.get_bin(self.DX)}")
        print(
            f"SP={self.get_bin(self.SP)} BP={self.get_bin(self.BP)}  "
            f"SI={self.get_bin(self.SI)}  DI={self.get_bin(self.DI)}")

    def move(self, memory: Memory, from_begin: int, from_end: int, destination: int) -> bool:
        """Copy a memory region to other memory region.

        Parameters:
            memory (Memory): A Memory class object.
            from_begin (int): Source's begin.
            from_end (int): Source's end.
            destination (int): Destination's begin.

        Returns:
            bool: Operation result.
        """

        if destination > from_end:
            for source in range(from_begin, from_end):
                dist_pointer = from_begin \
                    if destination + source == from_begin else destination + source - from_begin
                memory.poke(memory.active_page, dist_pointer,
                            memory.peek(memory.active_page, source))
            print(f"{from_end - from_begin} byte/s copied.")
            return True
        else:
            print("Invalid value.")
            return False

    def fill(self, memory: Memory, start: int, end: int, pattern: str) -> bool:
        """Fill a memory region with a specified pattern.

        Parameters:
            memory (Memory): A Memory class object.
            start (int): Source's begin.
            end (int): Source's end.
            pattern (str): Pattern.

        Returns:
            bool: Operation result. Always true.
        """
        cursor = 0
        for idx in range(start, end):
            memory.poke(memory.active_page, idx, ord(pattern[cursor]))
            cursor += 1
            if cursor > len(pattern) - 1:
                cursor = 0

        return True

    def search(self, memory: Memory, start: int, pattern: str) -> List[str]:
        """Search a pattern in the memory. Staring from <start> to the end of the page.

        Parameters:
            memory (Memory): Memory class object.
            start (int): Starting point from the search.
            pattern (str): Pattern to search for.

        Returns:
            [str]
        """
        found_list = []
        pointer = start
        while pointer < memory._offsets:
            idx = 0

            # Did I find the first char of the pattern? If so, let's search for the rest
            if memory.peek(memory.active_page, pointer) == ord(pattern[idx]):
                pointer_aux = pointer
                while idx < len(pattern) and pointer_aux < memory._offsets and \
                        memory.peek(memory.active_page, pointer_aux) == ord(pattern[idx]):
                    idx += 1
                    pointer_aux += 1

                if pointer_aux - pointer == len(pattern):
                    found_list.append(
                        f"{'%04X' % memory.active_page}:{'%04X' % pointer}")

            pointer += 1

        return found_list

    def load_into(self, memory: Memory, start: int, text: str) -> None:
        """
        Load a text into memory, starting from an address.

        Args:
            memory (Memory): Memory object class.
            start (int): Address memory where to begin.
            text (str): Text to be load into.

        Returns:
            None
        """
        for idx in range(0, len(text) - 1):
            memory.poke(memory.active_page, start + idx, ord(text[idx]))

    def compare(self, memory: Memory, cfrom: int, cend: int, cto: int) -> List[str]:
        """
        Compares two memory regions.

        Args:
            memory (Memory): Memory object class.
            cfrom (int): Source address memory where to start.
            cend (int): Source address memory where to end.
            cto (int): Destination address memory.

        Returns:
            [str]: The differences between regions.
        """
        diffs = []

        for a in range(cfrom, cend):
            org = memory.peek(memory.active_page, a)
            dist_pointer = cfrom if cto + a == cfrom else cto + a - cfrom - 1

            dist = memory.peek(memory.active_page, dist_pointer)
            if org != dist:
                diffs.append('%04X' % memory.active_page + ":" + '%04X' % a + " " +
                             '%02X' % org + " " + '%02X' % dist + " " +
                             '%04X' % memory.active_page + ":" + '%04X' % dist_pointer)

        return diffs

    def cat(self, disk: Disk, addrb: int, addrn: int) -> None:
        """
        Shows the content of the vdisk region.

        Args:
            disk: A Disk class type object.
            addrb: Start address.
            addrn: End address.

        Returns:

        """
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row:  # One single row
            print(f"{'%06X' % (pointer + addrb)} ", end="", flush=True)
            for address in range(addrb, addrn):
                byte = disk.read(pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)

            print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else:  # two or more rows
            while pointer + addrb < addrn:
                if pointer % bytes_per_row == 0:
                    print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    print(f"{'%06X' % (pointer + addrb)} ", end="", flush=True)

                byte = disk.read(pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)
                pointer += 1

        print("")

    def display(self, memory: Memory, addrb: int, addrn: int) -> None:
        """
        Displays a memory region.

        Args:
            memory: A Memory class type object.
            addrb: Start address.
            addrn: End address.

        Returns:
            None.
        """
        page = memory.active_page
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row:  # One single row
            print(
                f"{'%04X' % memory.active_page}:{'%04X' % (pointer + addrb)} ", end="", flush=True)
            for address in range(addrb, addrn):
                byte = memory.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)

            print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else:  # two or more rows
            while pointer + addrb < addrn:
                if pointer % bytes_per_row == 0:
                    print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    print(
                        f"{'%04X' % memory.active_page}:{'%04X' % (pointer + addrb)} ", end="", flush=True)

                byte = memory.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)
                pointer += 1

        print("")

    def write_to_vdisk(self, memory: Memory, disk: Disk, address: int, firstsector: int, number: int) -> None:
        """
        Writes to vdisk a memory block.

        Args:
            memory (Memory): A Memory type class object.
            disk (Disk): A Disk type class object.
            address (int): Source memory address.
            firstsector (int): Destination sector address.
            number (int): Number of bytes to be copied.

        Returns:
            None.
        """
        for i in range(0, number - 1):
            disk.write(firstsector, memory.peek(address + i))

    def read_from_vdisk(self, memory: Memory, disk: Disk, address: int, firstsector: int, number: int) -> None:
        """
        Writes to memory a vdisk block.

        Args:
            memory (Memory): A Memory type class object.
            disk (Disk): A Disk type class object.
            address (int): Destination memory address.
            firstsector (int): Source sector address.
            number (int): Number of bytes to be copied.

        Returns:
            None.
        """
        for i in range(0, number - 1):
            memory.poke(address, disk.read(firstsector + i))

    def assemble(self, memory: Memory) -> None:
        prompt = f"{self.get_hex(memory.active_page)}:{self.get_hex(memory.offset_cursor)}"

        # TODO: Start assembling (OMG)
        # http://www.c-jump.com/CIS77/CPU/x86/lecture.html
        # The Koky's way of NOT doing things.
        while True:
            op = input(f"{prompt} ")

            if re.match(r"^$", op) or re.match(r"^q$", op):
                break

            opcode = self._find_matches(self._opcode, op)

            if opcode is None:
                print("Illegal Instruction.")
            else:
                value = opcode.get("opcode")

                if opcode.get("mnemonic") == "add oper,int":
                    args = op.split(" ")
                    oper1 = int(args[1], 16)
                    oper2 = int(args[2], 16)

                    memory.poke(memory.active_page, memory.offset_cursor, value)
                    memory.offset_cursor += 1
                    memory.poke(memory.active_page, memory.offset_cursor, oper1)
                    memory.offset_cursor += 1
                    memory.poke(memory.active_page, memory.offset_cursor, oper2)
                    memory.offset_cursor += 1
                elif opcode.get('mnemonic') == "ret":
                    memory.poke(memory.active_page, memory.offset_cursor, value)
                    memory.offset_cursor += 1
                elif opcode.get('mnemonic') == "push es":
                    memory.poke(memory.active_page, memory.offset_cursor, value)
                    memory.offset_cursor += 1
                elif opcode.get('mnemonic') == "nop":
                    memory.poke(memory.active_page, memory.offset_cursor, value)
                    memory.offset_cursor += 1
                else:
                    print("Internal Error.")

            prompt = f"{self.get_hex(memory.active_page)}:{self.get_hex(memory.offset_cursor)}"

    def enterProg(self, ctx: asm8086Parser.ProgContext):
        super().enterProg(ctx)
        print("BEGIN PARSING")

    def exitProg(self, ctx: asm8086Parser.ProgContext):
        super().exitProg(ctx)
        print("END PARSING")

    def enterLine(self, ctx: asm8086Parser.LineContext):
        super().enterLine(ctx)

    def exitLine(self, ctx: asm8086Parser.LineContext):
        super().exitLine(ctx)

    def enterInstruction(self, ctx: asm8086Parser.InstructionContext):
        super().enterInstruction(ctx)

    def exitInstruction(self, ctx: asm8086Parser.InstructionContext):
        super().exitInstruction(ctx)

    def enterLbl(self, ctx: asm8086Parser.LblContext):
        super().enterLbl(ctx)

    def exitLbl(self, ctx: asm8086Parser.LblContext):
        super().exitLbl(ctx)

    def enterAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        super().enterAssemblerdirective(ctx)

    def exitAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        super().exitAssemblerdirective(ctx)

    def enterRw(self, ctx: asm8086Parser.RwContext):
        super().enterRw(ctx)

    def exitRw(self, ctx: asm8086Parser.RwContext):
        super().exitRw(ctx)

    def enterRb(self, ctx: asm8086Parser.RbContext):
        super().enterRb(ctx)

    def exitRb(self, ctx: asm8086Parser.RbContext):
        super().exitRb(ctx)

    def enterRs(self, ctx: asm8086Parser.RsContext):
        super().enterRs(ctx)

    def exitRs(self, ctx: asm8086Parser.RsContext):
        super().exitRs(ctx)

    def enterCseg(self, ctx: asm8086Parser.CsegContext):
        super().enterCseg(ctx)

    def exitCseg(self, ctx: asm8086Parser.CsegContext):
        super().exitCseg(ctx)

    def enterDseg(self, ctx: asm8086Parser.DsegContext):
        super().enterDseg(ctx)

    def exitDseg(self, ctx: asm8086Parser.DsegContext):
        super().exitDseg(ctx)

    def enterDw(self, ctx: asm8086Parser.DwContext):
        super().enterDw(ctx)

    def exitDw(self, ctx: asm8086Parser.DwContext):
        super().exitDw(ctx)

    def enterDb(self, ctx: asm8086Parser.DbContext):
        super().enterDb(ctx)

    def exitDb(self, ctx: asm8086Parser.DbContext):
        super().exitDb(ctx)

    def enterDd(self, ctx: asm8086Parser.DdContext):
        super().enterDd(ctx)

    def exitDd(self, ctx: asm8086Parser.DdContext):
        super().exitDd(ctx)

    def enterEqu(self, ctx: asm8086Parser.EquContext):
        super().enterEqu(ctx)

    def exitEqu(self, ctx: asm8086Parser.EquContext):
        super().exitEqu(ctx)

    def enterIf_(self, ctx: asm8086Parser.If_Context):
        super().enterIf_(ctx)

    def exitIf_(self, ctx: asm8086Parser.If_Context):
        super().exitIf_(ctx)

    def enterAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        super().enterAssemblerexpression(ctx)

    def exitAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        super().exitAssemblerexpression(ctx)

    def enterAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        super().enterAssemblerlogical(ctx)

    def exitAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        super().exitAssemblerlogical(ctx)

    def enterAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        super().enterAssemblerterm(ctx)

    def exitAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        super().exitAssemblerterm(ctx)

    def enterEndif_(self, ctx: asm8086Parser.Endif_Context):
        super().enterEndif_(ctx)

    def exitEndif_(self, ctx: asm8086Parser.Endif_Context):
        super().exitEndif_(ctx)

    def enterEnd(self, ctx: asm8086Parser.EndContext):
        super().enterEnd(ctx)

    def exitEnd(self, ctx: asm8086Parser.EndContext):
        super().exitEnd(ctx)

    def enterOrg(self, ctx: asm8086Parser.OrgContext):
        super().enterOrg(ctx)

    def exitOrg(self, ctx: asm8086Parser.OrgContext):
        super().exitOrg(ctx)

    def enterTitle(self, ctx: asm8086Parser.TitleContext):
        super().enterTitle(ctx)

    def exitTitle(self, ctx: asm8086Parser.TitleContext):
        super().exitTitle(ctx)

    def enterInclude_(self, ctx: asm8086Parser.Include_Context):
        super().enterInclude_(ctx)

    def exitInclude_(self, ctx: asm8086Parser.Include_Context):
        super().exitInclude_(ctx)

    def enterExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        super().enterExpressionlist(ctx)

    def exitExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        super().exitExpressionlist(ctx)

    def enterLabel(self, ctx: asm8086Parser.LabelContext):
        super().enterLabel(ctx)

    def exitLabel(self, ctx: asm8086Parser.LabelContext):
        super().exitLabel(ctx)

    def enterExpression(self, ctx: asm8086Parser.ExpressionContext):
        super().enterExpression(ctx)

    def exitExpression(self, ctx: asm8086Parser.ExpressionContext):
        super().exitExpression(ctx)

    def enterMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        super().enterMultiplyingExpression(ctx)

    def exitMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        super().exitMultiplyingExpression(ctx)

    def enterArgument(self, ctx: asm8086Parser.ArgumentContext):
        super().enterArgument(ctx)

    def exitArgument(self, ctx: asm8086Parser.ArgumentContext):
        super().exitArgument(ctx)

    def enterPtr(self, ctx: asm8086Parser.PtrContext):
        super().enterPtr(ctx)

    def exitPtr(self, ctx: asm8086Parser.PtrContext):
        super().exitPtr(ctx)

    def enterDollar(self, ctx: asm8086Parser.DollarContext):
        super().enterDollar(ctx)

    def exitDollar(self, ctx: asm8086Parser.DollarContext):
        super().exitDollar(ctx)

    def enterRegister_(self, ctx: asm8086Parser.Register_Context):
        super().enterRegister_(ctx)

    def exitRegister_(self, ctx: asm8086Parser.Register_Context):
        super().exitRegister_(ctx)

    def enterString_(self, ctx: asm8086Parser.String_Context):
        super().enterString_(ctx)

    def exitString_(self, ctx: asm8086Parser.String_Context):
        super().exitString_(ctx)

    def enterName(self, ctx: asm8086Parser.NameContext):
        super().enterName(ctx)

    def exitName(self, ctx: asm8086Parser.NameContext):
        super().exitName(ctx)

    def enterNumber(self, ctx: asm8086Parser.NumberContext):
        super().enterNumber(ctx)

    def exitNumber(self, ctx: asm8086Parser.NumberContext):
        super().exitNumber(ctx)

    def enterOpcode(self, ctx: asm8086Parser.OpcodeContext):
        super().enterOpcode(ctx)

    def exitOpcode(self, ctx: asm8086Parser.OpcodeContext):
        super().exitOpcode(ctx)

    def enterRep(self, ctx: asm8086Parser.RepContext):
        super().enterRep(ctx)

    def exitRep(self, ctx: asm8086Parser.RepContext):
        super().exitRep(ctx)

    def enterComment(self, ctx: asm8086Parser.CommentContext):
        super().enterComment(ctx)

    def exitComment(self, ctx: asm8086Parser.CommentContext):
        super().exitComment(ctx)
