import os
from typing import List

from multipledispatch import dispatch

from .asm8086Listener import *
from .asm8086Parser import *


class Disk:
    """
    Class emulating a Disk.
    """

    def __init__(self, size, filename):
        """
        Class constructor. Initialize the vdisk object.

        Args:
            size (int): Size in bytes of the vdisk.
            filename (str): Real filename of the vdisk in the filesystem.
        """
        self._filename = os.path.join(os.path.expanduser("~"), "." + filename)
        self._size = size
        self._disk = [0b00000000 * self._size]

    @property
    def __str__(self):
        """ Diskinfo """
        return f"Filename: {self._filename} // Size: {self._size} bytes."

    @property
    def size(self):
        """ Disk size """
        return self._size

    @property
    def filename(self):
        """ Filename of the real disk """
        return self._filename

    def write(self, sector: int, value: int) -> bool:
        """Write bytes to the virtual disk.

        Args:
            sector:  Sector where the byte is written.
            value: The byte to be written.

        Returns:
            bool: True if successful, False if not.

        """

        if sector < 0 or sector > self._size - 1:
            print("Invalid sector.")
            return False
        elif value < 0 or value > 255:
            print("Invalid value.")
            return False
        else:
            self._disk[int(sector)] = value
            return True

    def read(self, sector: int) -> int:
        """Read a virtual disk sector.

        Parameters:
            sector (int): Sector to be read.

        Returns:
            int: the read byte or -1 if there were any problem.
        """
        if sector < 0 or sector > self._size - 1:
            print("Invalid sector.")
            return -1
        else:
            return self._disk[int(sector)]

    def load(self) -> bool:
        """Load the virtual disk from a real file.

        Parameters:
            None

        Returns:
            bool: True if was successful, False if not,
        """
        try:
            f = open(self._filename, 'rb')
        except IOError:
            print(f"Disk::load() => Problem accessing {self._filename}")
            return False
        else:
            content = f.read()
            f.close()
            for i in range(0, len(content) - 1):
                self._disk[i] = content[i]
            return True

    def save(self) -> bool:
        """Save the virtual disk to a real file.

        Parameters:
            None

        Returns:
            bool: True if was successful, False if not,
        """
        try:
            f = open(self._filename, 'w+b')
        except IOError:
            print(f"Disk.save() => Problem accessing {self._filename}")
            return False
        else:
            binary_format = bytearray(self._disk)
            f.write(binary_format)
            f.close()
            return True


class Memory:
    """
    Class emulating paginated memory bank.

    Methods:
        peek: Retrieve the content of a memory address.
        poke: Write a value to a memory address.
    """

    def __init__(self, pages=1):
        self.pages = pages
        self._offset_cursor = 0
        self.active_page = 49152  # Like the old one C000
        self._offsets = 65536  # 64K for page.
        self._memory = [[0b00000000] * self._offsets] * self.pages

    def __str__(self):
        return str(self.pages) + " * " + str(self._offsets)

    @dispatch(int)
    def peek(self, address: int) -> int:
        """
        peek(self, address: int) -> int
        Retrieve the content of a memory address.

        Parameters:
            address (int): Adress where to peek.

        Returns:
            int: Pointed address value.
        """
        page = self.active_page
        return self.peek(page, address)

    @dispatch(int, int)
    def peek(self, page: int, address: int) -> int:
        """
        peek(self, page: int, address: int) -> int
        Retrieve the content of a memory address.

        Parameters:
            page (int): Page memory.
            address (int): Adress where to peek.

        Returns:
            int: Pointed address value.
        """
        if int(page) < 0 or int(page) >= len(self._memory) or \
                int(address) < 0 or int(page) >= self._offsets:
            print("Memory.peek(): Invalid address.")
            return -1
        else:
            self.active_page = page
            return self._memory[int(page)][int(address)]

    @dispatch(str, str)
    def peek(self, page: str, address: str) -> int:
        """
        peek(self, page: str, address: str) -> int
        Retrieve the content of a memory address.

        Parameters:
            page (str): Page memory in hexadecimal.
            address (str): Adress where to peek in hexadecimal.

        Returns:
            int: Pointed address value.
        """
        return self.peek(int(page, 16), int(address, 16))

    @dispatch(int, int, int)
    def poke(self, page: int, address: int, value: int) -> bool:
        """
        poke(self, page: int, ºaddress: int, value: int) -> bool
        Write a value to a memory address.

        Parameters:
            page (int): Page memory.
            address (int): Adress where to peek.

        Returns:
            bool: Operation result.
        """
        if value < 0 or value > 255 or \
                page < 0 or page >= len(self._memory) or \
                address > self._offsets or address < 0:
            print("Memory.poke(): Invalid address or value.")
            return False
        else:
            self.active_page = page
            self._memory[page][address] = value
            return True


class Cpu(asm8086Listener):
    """
    Class emulating a 8086 CPU.
    """

    def __init__(self):
        self._bits = 16

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

        # Control flags not implemented

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

    @staticmethod
    def _not_yet(self):
        print("This part of the CPU hasn't been implemented yet. =)")

    @dispatch(str)
    def get_bin(x: int) -> str:
        """Convert any integer into 8 bit binary format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 8 bit binary as string.
        """

        return format(int(x, 2), 'b').zfill(8)

    @dispatch(int, n=int)
    def get_bin(x: int, n: int = bits) -> str:
        """Convert any integer into n bit binary format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: n bit binary as string.
        """
        return format(x, 'b').zfill(8)

    @dispatch(int)
    def get_hex(x: int) -> str:
        """Convert any integer into 16 bit hexadecimal format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 16 bit hexadecimal as string.
        """

        return format(x, 'h').zfill(4)

    def print_status_flags(self) -> None:
        """ Print the status of the flags. """
        print(f"SF={self.SF} ZF={self.ZF} CY={self.CY} OP={self.OP} OF={self.OF} AC={self.AC}")

    def print_registers(self) -> None:
        """ Print the CPU registers and it's value."""
        print(
            f"AX={self.get_bin(self.AX)} BX={self.get_bin(self.BX)}  CX={self.get_bin(self.CX)}  DX={self.get_bin(self.DX)}")
        print(
            f"SP={self.get_bin(self.SP)} BP={self.get_bin(self.BP)}  SI={self.get_bin(self.SI)}  DI={self.get_bin(self.DI)}")

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
                memory.poke(memory.active_page, dist_pointer, memory.peek(memory.active_page, source))
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

    def search(self, memory: Memory, start: int, pattern: str) -> List[int]:
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
                    found_list.append(f"{'%04X' % memory.active_page}:{'%04X' % pointer}")

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
                byte = disk.read_from_vdisk(pointer + addrb)
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

                byte = disk.read_from_vdisk(pointer + addrb)
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
            print(f"{'%04X' % memory.active_page}:{'%04X' % (pointer + addrb)} ", end="", flush=True)
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
                    print(f"{'%04X' % memory.active_page}:{'%04X' % (pointer + addrb)} ", end="", flush=True)

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

    def enterProg(self, ctx: asm8086Parser.ProgContext):
        super().enterProg(ctx)
        self._not_yet()

    def exitProg(self, ctx: asm8086Parser.ProgContext):
        super().exitProg(ctx)
        self._not_yet()

    def enterLine(self, ctx: asm8086Parser.LineContext):
        super().enterLine(ctx)
        self._not_yet()

    def exitLine(self, ctx: asm8086Parser.LineContext):
        super().exitLine(ctx)
        self._not_yet()

    def enterInstruction(self, ctx: asm8086Parser.InstructionContext):
        super().enterInstruction(ctx)
        self._not_yet()

    def exitInstruction(self, ctx: asm8086Parser.InstructionContext):
        super().exitInstruction(ctx)
        self._not_yet()

    def enterLbl(self, ctx: asm8086Parser.LblContext):
        super().enterLbl(ctx)
        self._not_yet()

    def exitLbl(self, ctx: asm8086Parser.LblContext):
        super().exitLbl(ctx)
        self._not_yet()

    def enterAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        super().enterAssemblerdirective(ctx)
        self._not_yet()

    def exitAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        super().exitAssemblerdirective(ctx)
        self._not_yet()

    def enterRw(self, ctx: asm8086Parser.RwContext):
        super().enterRw(ctx)
        self._not_yet()

    def exitRw(self, ctx: asm8086Parser.RwContext):
        super().exitRw(ctx)
        self._not_yet()

    def enterRb(self, ctx: asm8086Parser.RbContext):
        super().enterRb(ctx)
        self._not_yet()

    def exitRb(self, ctx: asm8086Parser.RbContext):
        super().exitRb(ctx)
        self._not_yet()

    def enterRs(self, ctx: asm8086Parser.RsContext):
        super().enterRs(ctx)
        self._not_yet()

    def exitRs(self, ctx: asm8086Parser.RsContext):
        super().exitRs(ctx)
        self._not_yet()

    def enterCseg(self, ctx: asm8086Parser.CsegContext):
        super().enterCseg(ctx)
        self._not_yet()

    def exitCseg(self, ctx: asm8086Parser.CsegContext):
        super().exitCseg(ctx)
        self._not_yet()

    def enterDseg(self, ctx: asm8086Parser.DsegContext):
        super().enterDseg(ctx)
        self._not_yet()

    def exitDseg(self, ctx: asm8086Parser.DsegContext):
        super().exitDseg(ctx)
        self._not_yet()

    def enterDw(self, ctx: asm8086Parser.DwContext):
        super().enterDw(ctx)
        self._not_yet()

    def exitDw(self, ctx: asm8086Parser.DwContext):
        super().exitDw(ctx)
        self._not_yet()

    def enterDb(self, ctx: asm8086Parser.DbContext):
        super().enterDb(ctx)
        self._not_yet()

    def exitDb(self, ctx: asm8086Parser.DbContext):
        super().exitDb(ctx)
        self._not_yet()

    def enterDd(self, ctx: asm8086Parser.DdContext):
        super().enterDd(ctx)
        self._not_yet()

    def exitDd(self, ctx: asm8086Parser.DdContext):
        super().exitDd(ctx)
        self._not_yet()

    def enterEqu(self, ctx: asm8086Parser.EquContext):
        super().enterEqu(ctx)
        self._not_yet()

    def exitEqu(self, ctx: asm8086Parser.EquContext):
        super().exitEqu(ctx)
        self._not_yet()

    def enterIf_(self, ctx: asm8086Parser.If_Context):
        super().enterIf_(ctx)
        self._not_yet()

    def exitIf_(self, ctx: asm8086Parser.If_Context):
        super().exitIf_(ctx)
        self._not_yet()

    def enterAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        super().enterAssemblerexpression(ctx)
        self._not_yet()

    def exitAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        super().exitAssemblerexpression(ctx)
        self._not_yet()

    def enterAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        super().enterAssemblerlogical(ctx)
        self._not_yet()

    def exitAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        super().exitAssemblerlogical(ctx)
        self._not_yet()

    def enterAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        super().enterAssemblerterm(ctx)
        self._not_yet()

    def exitAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        super().exitAssemblerterm(ctx)
        self._not_yet()

    def enterEndif_(self, ctx: asm8086Parser.Endif_Context):
        super().enterEndif_(ctx)
        self._not_yet()

    def exitEndif_(self, ctx: asm8086Parser.Endif_Context):
        super().exitEndif_(ctx)
        self._not_yet()

    def enterEnd(self, ctx: asm8086Parser.EndContext):
        super().enterEnd(ctx)
        self._not_yet()

    def exitEnd(self, ctx: asm8086Parser.EndContext):
        super().exitEnd(ctx)
        self._not_yet()

    def enterOrg(self, ctx: asm8086Parser.OrgContext):
        super().enterOrg(ctx)
        self._not_yet()

    def exitOrg(self, ctx: asm8086Parser.OrgContext):
        super().exitOrg(ctx)
        self._not_yet()

    def enterTitle(self, ctx: asm8086Parser.TitleContext):
        super().enterTitle(ctx)
        self._not_yet()

    def exitTitle(self, ctx: asm8086Parser.TitleContext):
        super().exitTitle(ctx)
        self._not_yet()

    def enterInclude_(self, ctx: asm8086Parser.Include_Context):
        super().enterInclude_(ctx)
        self._not_yet()

    def exitInclude_(self, ctx: asm8086Parser.Include_Context):
        super().exitInclude_(ctx)
        self._not_yet()

    def enterExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        super().enterExpressionlist(ctx)
        self._not_yet()

    def exitExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        super().exitExpressionlist(ctx)
        self._not_yet()

    def enterLabel(self, ctx: asm8086Parser.LabelContext):
        super().enterLabel(ctx)
        self._not_yet()

    def exitLabel(self, ctx: asm8086Parser.LabelContext):
        super().exitLabel(ctx)
        self._not_yet()

    def enterExpression(self, ctx: asm8086Parser.ExpressionContext):
        super().enterExpression(ctx)
        self._not_yet()

    def exitExpression(self, ctx: asm8086Parser.ExpressionContext):
        super().exitExpression(ctx)
        self._not_yet()

    def enterMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        super().enterMultiplyingExpression(ctx)
        self._not_yet()

    def exitMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        super().exitMultiplyingExpression(ctx)
        self._not_yet()

    def enterArgument(self, ctx: asm8086Parser.ArgumentContext):
        super().enterArgument(ctx)
        self._not_yet()

    def exitArgument(self, ctx: asm8086Parser.ArgumentContext):
        super().exitArgument(ctx)
        self._not_yet()

    def enterPtr(self, ctx: asm8086Parser.PtrContext):
        super().enterPtr(ctx)
        self._not_yet()

    def exitPtr(self, ctx: asm8086Parser.PtrContext):
        super().exitPtr(ctx)
        self._not_yet()

    def enterDollar(self, ctx: asm8086Parser.DollarContext):
        super().enterDollar(ctx)
        self._not_yet()

    def exitDollar(self, ctx: asm8086Parser.DollarContext):
        super().exitDollar(ctx)
        self._not_yet()

    def enterRegister_(self, ctx: asm8086Parser.Register_Context):
        super().enterRegister_(ctx)
        self._not_yet()

    def exitRegister_(self, ctx: asm8086Parser.Register_Context):
        super().exitRegister_(ctx)
        self._not_yet()

    def enterString_(self, ctx: asm8086Parser.String_Context):
        super().enterString_(ctx)
        self._not_yet()

    def exitString_(self, ctx: asm8086Parser.String_Context):
        super().exitString_(ctx)
        self._not_yet()

    def enterName(self, ctx: asm8086Parser.NameContext):
        super().enterName(ctx)
        self._not_yet()

    def exitName(self, ctx: asm8086Parser.NameContext):
        super().exitName(ctx)
        self._not_yet()

    def enterNumber(self, ctx: asm8086Parser.NumberContext):
        super().enterNumber(ctx)
        self._not_yet()

    def exitNumber(self, ctx: asm8086Parser.NumberContext):
        super().exitNumber(ctx)
        self._not_yet()

    def enterOpcode(self, ctx: asm8086Parser.OpcodeContext):
        super().enterOpcode(ctx)
        self._not_yet()

    def exitOpcode(self, ctx: asm8086Parser.OpcodeContext):
        super().exitOpcode(ctx)
        self._not_yet()

    def enterRep(self, ctx: asm8086Parser.RepContext):
        super().enterRep(ctx)
        self._not_yet()

    def exitRep(self, ctx: asm8086Parser.RepContext):
        super().exitRep(ctx)
        self._not_yet()

    def enterComment(self, ctx: asm8086Parser.CommentContext):
        super().enterComment(ctx)
        self._not_yet()

    def exitComment(self, ctx: asm8086Parser.CommentContext):
        super().exitComment(ctx)
        self._not_yet()
