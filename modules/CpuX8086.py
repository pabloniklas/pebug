from multipledispatch import dispatch
from rply import (
    ParserGenerator,
    LexerGenerator,
    errors
)
from typing import (
    List,
    Set,
    Dict,
    Tuple,
    Optional
)
import re

if __name__ is not None and "." in __name__:
    from .Memory import Memory
    from .Disk import Disk
else:
    from Memory import Memory
    from Disk import Disk

# https://joshsharp.com.au/blog/rpython-rply-interpreter-1.html


class CpuX8086():
    """
    Class emulating a 8086 CPU.
    """

    def __init__(self):
        self.lexer = LexerGenerator()

        # Opcodes
        self.lexer.add('OPCODE',
                       r'(aaa|aad|aam|aas|adc|add|and|call|cbw|cdq|clc|cld|cmc|cmp|cmpsb|cmpsd|cmpsw|cwd|cwde|daa|das|dec|div|idiv|imul|inc|ja|jae|jb|jbe|jc|je|jecxz|jg|jge|jl|jle|jmp|jna|jnae|jnb|jnbe|jnc|jne|jng|jnge|jnl|jnle|jno|jnp|jns|jnz|jo|jp|jpe|jpo|js|jz|lodsb|lodsd|lodsw|loop|loope|loopne|loopnz|loopz|mov|movsb|movsd|movsw|movsx|movzx|mul|neg|not|or|pop|popa|popad|popf|popfd|push|pusha|pushad|pushf|pushfd|rep|repe|repne|repne|repnz|repz|ret|rol|ror|sar|sbb|scasb|scasd|scasw|shl|shld|shr|shrd|stc|std|stosb|stosb|stosd|stosw|stosw|sub|test|xchg|xlat|xor)')

        # Registers
        self.lexer.add(
            'REG8', r'(af|ah|al|ax|bh|bl|bp|bp|bx|cl|cs|cx|ch|dh|di|dl|ds|dx|es|fs|gs|si|sp|ss)')
        self.lexer.add('REG16', r'(eax|eax|ebp|ebx|ecx|edi|edx|esi|esp)')

        # Signs and operators
        self.lexer.add('COMMA', r',')
        # self.lexer.add('PLUS', r'\+')

        # Integers
        self.lexer.add('IMM8', r'[0-9a-f]{2}')
        self.lexer.add('IMM16', r'[0-9a-f]{4}')

        # Memory
        self.lexer.add('MEMORY', r'\[.*?\]')

        self.lexer.ignore('\s+')

        self.cpu_lexer = self.lexer.build()

        self.pg = ParserGenerator(
            ["OPCODE", "REG8", "REG16", "IMM8", "IMM16", "MEMORY",
             "COMMA"],
            precedence=[
                ('left', ['OPCODE']),
                ('left', ['REG8', 'REG16']),
                ('left', ['COMMA']),
            ],
            cache_id="my_parser"
        )

        @self.pg.production('instruction : OPCODE operands')
        def expression(p):
            opcode = p[0].getstr()
            operands = p[1]  # ALL the operands (is a list).

            if opcode == "xor":
                arg1 = operands[0].getstr()
                arg2 = operands[2].getstr()

                setattr(self, arg1.upper(), self.asm_xor(getattr(self, arg1.upper()),
                                                         getattr(self, arg2.upper())))

        # @self.pg.production('mem8 : MLEFT_BRACKET REG8 RIGHT_BRACKET')
        # @self.pg.production('mem8 : LEFT_BRACKET REG8 PLUS REG8 RIGHT_BRACKET')
        @self.pg.production('operand : operand COMMA operand')
        def multiple_operands(p):
            return p

        @self.pg.production('operand : REG8')
        @self.pg.production('operand : REG16')
        @self.pg.production('operand : IMM8')
        @self.pg.production('operand : IMM16')
        @self.pg.production('operand : MEMORY')
        @self.pg.production('operands : operand')
        def operands_single(p):
            return p[0]

        @self.pg.error
        def error_handle(token):
            raise ValueError(f"ERROR: Invalid token '{token.getstr()}'.")

        self._bits = 16

        # 8 bit X86 registers
        self.AH = 0b0 * self._bits / 2
        self.AL = 0b0 * self._bits / 2
        self.BH = 0b0 * self._bits / 2
        self.BL = 0b0 * self._bits / 2
        self.CH = 0b0 * self._bits / 2
        self.CL = 0b0 * self._bits / 2
        self.DH = 0b0 * self._bits / 2
        self.DL = 0b0 * self._bits / 2

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

        # Control flags not implemented

        # Define the grammar rules for decoding x86 instructions
        # https://pastraiser.com/cpu/i8088/i8088_opcodes.html

    def parse_instruction(self, cmd):
        tokens = self.cpu_lexer.lex(cmd)
        parser = self.pg.build()

        try:
            parser.parse(tokens)
        except errors.LexingError as e:
            error = e.args[1]
            idx = error.idx
            lineno = error.lineno
            colno = error.colno
            print(" " * (cmd.count(" ") + idx + 7) + "^")
            print("ERROR: Invalid token.")

    def set_register_upper(self, reg: int, value: int) -> int:
        reg = (reg & 0x00ff) | (value << 8)
        return reg

    def set_register_lower(self, reg: int, value: int) -> int:

        # Clear the lower 8 bits of the register
        reg &= 0xFF00

        # Set the lower 8 bits of the register to the new value
        reg |= value

        return reg

    #  https://www.geeksforgeeks.org/python-program-to-add-two-binary-numbers/
    def _find_matches(self, d: Dict[str, str], item: str) -> str:
        """

        Parameters:
            d {str}: Regex Dictionary
            item (str): Item to be look for.

        Returns:
            Dict[str]: Item found, or None if not.

        """
        for k in d:
            if re.match(k, item):
                return d[k]

        return None

    def _16to8(self, hl: int) -> List[int]:
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

        result = a + b

        # Update the carry flag
        self.CF = 1 if result > 0xFFFF else 0

        # Update the zero flag
        self.ZF = 1 if result == 0 else 0

        # Update the sign flag
        self.SF = 1 if result & 0x8000 else 0

        # Update the overflow flag
        self.OF = 1 if ((a ^ b) & 0x8000 == 0 and (a ^ b) & 0x8000) else 0

        # Update the auxiliary carry flag
        self.AC = 1 if ((a & 0x0F) + (b & 0x0F) > 0x0F) else 0

        # Update the parity flag
        self.PF = 1 if bin(result).count("1") % 2 == 0 else 0

        print(result.zfill(self.max_len))

        return result

    def asm_sub(self, a, b):
        result = a - b

        # Update the zero flag
        self.ZF = 1 if result == 0 else 0

        # Update the sign flag
        self.SF = 1 if result & 0x8000 else 0

        # Update the parity flag
        self.PF = 1 if bin(result).count("1") % 2 == 0 else 0

        # Update the carry flag
        self.CF = 1 if result > 0xFFFF else 0

        # Update the auxiliary carry flag
        self.AC = 1 if ((a & 0x0F) + (b & 0x0F) > 0x0F) else 0

        print(result.zfill(self.max_len))

        return result

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

    @dispatch(int)
    def get_bin(self, x: int) -> str:
        """Convert any integer into n bit binary format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 16 bit binary as string.
        """
        return format(x, '0' + str(self._bits) + 'b')

    @dispatch(int)
    def get_hex(self, x: int) -> str:
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
            f"CX={self.get_bin(self.CX)} DX={self.get_bin(self.DX)}")
        print(
            f"SP={self.get_bin(self.SP)} BP={self.get_bin(self.BP)}  "
            f"SI={self.get_bin(self.SI)} DI={self.get_bin(self.DI)}")

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

    # https://github.com/Maratyszcza/Opcodes
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
                print("Invalid opcode.")
            else:
                value = opcode.get("opcode")

                if opcode.get("mnemonic") == "add oper,int":
                    args = op.split(" ")
                    oper1 = int(args[1], 16)
                    oper2 = int(args[2], 16)

                    memory.poke(memory.active_page,
                                memory.offset_cursor, value)
                    memory.offset_cursor += 1
                    memory.poke(memory.active_page,
                                memory.offset_cursor, oper1)
                    memory.offset_cursor += 1
                    memory.poke(memory.active_page,
                                memory.offset_cursor, oper2)
                    memory.offset_cursor += 1
                elif opcode.get('mnemonic') == "ret":
                    memory.poke(memory.active_page,
                                memory.offset_cursor, value)
                    memory.offset_cursor += 1
                elif opcode.get('mnemonic') == "push es":
                    memory.poke(memory.active_page,
                                memory.offset_cursor, value)
                    memory.offset_cursor += 1
                elif opcode.get('mnemonic') == "nop":
                    memory.poke(memory.active_page,
                                memory.offset_cursor, value)
                    memory.offset_cursor += 1
                else:
                    print("Internal Error.")

            prompt = f"{self.get_hex(memory.active_page)}:{self.get_hex(memory.offset_cursor)}"
