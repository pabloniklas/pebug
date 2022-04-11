import re
from typing import List

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
        self.AX = 0b0 * self._bits
        self.BX = 0b0 * self._bits
        self.CX = 0b0 * self._bits
        self.DX = 0b0 * self._bits
        self.SP = 0b0 * self._bits
        self.BP = 0b0 * self._bits
        self.SI = 0b0 * self._bits
        self.DI = 0b0 * self._bits

        self.IP = 0b0 * self._bits

        # Register Flags
        # https://www.tutorialspoint.com/flag-register-of-8086-microprocessor
        self.SF = 0b0  # Sign (D7)
        self.ZF = 0b0  # Zero (D6)
        self.CY = 0b0  # Carry bit (D0)
        self.OP = 0b0  # Parity (D2)
        self.OF = 0b0  # Overflow (D11)
        self.AC = 0b0  # Auxiliary carry (for BCD Arithmetic) (D4)

        # Opcode dictionary
        # https://pastraiser.com/cpu/i8088/i8088_opcodes.html
        # TODO: Fill in the dictionary
        self._opcode = {
            r"^(\s*)add(\s+)[abcd][hl](\s*),(\s*)[abcd][hl](\s*)$": {
                "mnemonic": "add r8,r8",
                "opcode": int(0x02),
                "flags": "OSZAPC"
            },
            r"^(\s*)ret(\s*)$": {
                "mnemonic": "ret",
                "opcode": int(0xc3),
                "flags": ""
            },
            r"^(\s*)aaa(\s*)$": {
                "mnemonic": "aaa",
                "opcode": int(0x37),
                "flags": "AC"
            },
            r"^(\s*)aas(\s*)$": {
                "mnemonic": "aas",
                "opcode": int(0x37),
                "flags": "3F"
            },
            r"^(\s*)daa(\s*)$": {
                "mnemonic": "daa",
                "opcode": int(0x27),
                "flags": "SZPA"
            },
            r"^(\s*)das(\s*)$": {
                "mnemonic": "das",
                "opcode": int(0x2F),
                "flags": "SZPA"
            },
            r"^(\s*)push(\s+)es(\s*)$": {
                "mnemonic": "push es",
                "opcode": int(0x06),
                "flags": ""
            },
            r"^(\s*)pop(\s+)es(\s*)$": {
                "mnemonic": "push es",
                "opcode": int(0x07),
                "flags": ""
            },
            r"^(\s*)push(\s+)ad?(\s*)$": {
                "mnemonic": "push a",
                "opcode": int(0x60),
                "flags": ""
            },
            r"^(\s*)pop(\s+)ad?(\s*)$": {
                "mnemonic": "pop a",
                "opcode": int(0x61),
                "flags": ""
            },
            r"^(\s*)nop(\s*)$": {
                "mnemonic": "nop",
                "opcode": int(0x90),
                "flags": ""
            }
        }

        # Control flags not implemented

    # TODO: Setter para los registros. Ya que los de uso general tienen contraparte de 8 bits.
    def set_register(self, *reg, value: int):
        pass

    # https://www.geeksforgeeks.org/python-program-to-add-two-binary-numbers/
    def _find_matches(self, d: {str}, item: str) -> {str}:
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
    def _not_yet(self):
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
            f"SF={self.SF} ZF={self.ZF} CY={self.CY} OP={self.OP} OF={self.OF} AC={self.AC}")

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
