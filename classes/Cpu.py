from multipledispatch import dispatch

from . import Memory
from .asm8086Listener import *
from .asm8086Parser import *


class Cpu(asm8086Listener):

    def __init__(self, ram: Memory):
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
        """https://www.tutorialspoint.com/flag-register-of-8086-microprocessor"""
        self.sf = 0b0  # Sign (D7)
        self.zf = 0b0  # Zero (D6)
        self.cy = 0b0  # Carry bit (D0)
        self.op = 0b0  # Parity (D2)
        self.of = 0b0  # Overflow (D11)
        self.ac = 0b0  # Auxiliary carry (for BCD Arithmetic) (D4)

        # Control flags not implemented

    @property
    def bits(self):
        return self._bits

    def not_yet(self):
        print("This part of the CPU hasn't been implemented yet.")

    def print_status(self):
        print(f"SF={self.sf} ZF={self.zf} CY={self.cy} OP={self.op} OF={self.of} AC={self.ac}")

    def print_registers(self):
        def get_bin(x, n=self._bits):
            return format(x, 'b').zfill(n)

        def get_hex(x):
            return format(x, 'h').zfill(4)

        print(
            f"AX={get_bin(self.AX)} BX={get_bin(self.BX)}  CX={get_bin(self.CX)}  DX={get_bin(self.DX)}")
        print(f"SP={get_bin(self.SP)} BP={get_bin(self.BP)}  SI={get_bin(self.SI)}  DI={get_bin(self.DI)}")

    @dispatch(object, int, int, int)
    def move(self, memory, from_begin, from_end, destination):
        if destination > from_end:
            for source in range(from_begin, from_end):
                dist_pointer = from_begin \
                    if destination + source == from_begin else destination + source - from_begin
                memory.poke(memory.active_page, dist_pointer, memory.peek(memory.active_page, source))
            print(f"{from_end - from_begin} byte/s copied.")
        else:
            print("Invalid value.")

    @dispatch(object, int, int, str)
    def fill(self, memory, start, end, pattern):
        cursor = 0
        for idx in range(start, end):
            memory.poke(memory.active_page, idx, ord(pattern[cursor]))
            cursor += 1
            if cursor > len(pattern) - 1:
                cursor = 0

    @dispatch(object, int, str)
    def search(self, memory, start, pattern):
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

    @dispatch(object, int, str)
    def load_into(self, memory, start, text):
        for idx in range(0, len(text) - 1):
            memory.poke(memory.active_page, start + idx, ord(text[idx]))

    @dispatch(object, int, int, int)
    def compare(self, memory, cfrom, cend, cto):
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

    @dispatch(object, int, int)
    def display(self, memory, addrb, addrn):
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

    @dispatch(object, object, int, int, int)
    def write(self, memory, disk, address, firstsector, number):
        for i in range(0, number - 1):
            disk.write(firstsector, memory.peek(address + i))

    @dispatch(object, object, int, int, int)
    def read(self, memory, disk, address, firstsector, number):
        for i in range(0, number - 1):
            disk.write(firstsector, memory.peek(address + i))

    def enterProg(self, ctx: asm8086Parser.ProgContext):
        super().enterProg(ctx)
        self.not_yet()

    def exitProg(self, ctx: asm8086Parser.ProgContext):
        super().exitProg(ctx)
        self.not_yet()

    def enterLine(self, ctx: asm8086Parser.LineContext):
        super().enterLine(ctx)
        self.not_yet()

    def exitLine(self, ctx: asm8086Parser.LineContext):
        super().exitLine(ctx)
        self.not_yet()

    def enterInstruction(self, ctx: asm8086Parser.InstructionContext):
        super().enterInstruction(ctx)
        self.not_yet()

    def exitInstruction(self, ctx: asm8086Parser.InstructionContext):
        super().exitInstruction(ctx)
        self.not_yet()

    def enterLbl(self, ctx: asm8086Parser.LblContext):
        super().enterLbl(ctx)
        self.not_yet()

    def exitLbl(self, ctx: asm8086Parser.LblContext):
        super().exitLbl(ctx)
        self.not_yet()

    def enterAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        super().enterAssemblerdirective(ctx)
        self.not_yet()

    def exitAssemblerdirective(self, ctx: asm8086Parser.AssemblerdirectiveContext):
        super().exitAssemblerdirective(ctx)
        self.not_yet()

    def enterRw(self, ctx: asm8086Parser.RwContext):
        super().enterRw(ctx)
        self.not_yet()

    def exitRw(self, ctx: asm8086Parser.RwContext):
        super().exitRw(ctx)
        self.not_yet()

    def enterRb(self, ctx: asm8086Parser.RbContext):
        super().enterRb(ctx)
        self.not_yet()

    def exitRb(self, ctx: asm8086Parser.RbContext):
        super().exitRb(ctx)
        self.not_yet()

    def enterRs(self, ctx: asm8086Parser.RsContext):
        super().enterRs(ctx)
        self.not_yet()

    def exitRs(self, ctx: asm8086Parser.RsContext):
        super().exitRs(ctx)
        self.not_yet()

    def enterCseg(self, ctx: asm8086Parser.CsegContext):
        super().enterCseg(ctx)
        self.not_yet()

    def exitCseg(self, ctx: asm8086Parser.CsegContext):
        super().exitCseg(ctx)
        self.not_yet()

    def enterDseg(self, ctx: asm8086Parser.DsegContext):
        super().enterDseg(ctx)
        self.not_yet()

    def exitDseg(self, ctx: asm8086Parser.DsegContext):
        super().exitDseg(ctx)
        self.not_yet()

    def enterDw(self, ctx: asm8086Parser.DwContext):
        super().enterDw(ctx)
        self.not_yet()

    def exitDw(self, ctx: asm8086Parser.DwContext):
        super().exitDw(ctx)
        self.not_yet()

    def enterDb(self, ctx: asm8086Parser.DbContext):
        super().enterDb(ctx)
        self.not_yet()

    def exitDb(self, ctx: asm8086Parser.DbContext):
        super().exitDb(ctx)
        self.not_yet()

    def enterDd(self, ctx: asm8086Parser.DdContext):
        super().enterDd(ctx)
        self.not_yet()

    def exitDd(self, ctx: asm8086Parser.DdContext):
        super().exitDd(ctx)
        self.not_yet()

    def enterEqu(self, ctx: asm8086Parser.EquContext):
        super().enterEqu(ctx)
        self.not_yet()

    def exitEqu(self, ctx: asm8086Parser.EquContext):
        super().exitEqu(ctx)
        self.not_yet()

    def enterIf_(self, ctx: asm8086Parser.If_Context):
        super().enterIf_(ctx)
        self.not_yet()

    def exitIf_(self, ctx: asm8086Parser.If_Context):
        super().exitIf_(ctx)
        self.not_yet()

    def enterAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        super().enterAssemblerexpression(ctx)
        self.not_yet()

    def exitAssemblerexpression(self, ctx: asm8086Parser.AssemblerexpressionContext):
        super().exitAssemblerexpression(ctx)
        self.not_yet()

    def enterAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        super().enterAssemblerlogical(ctx)
        self.not_yet()

    def exitAssemblerlogical(self, ctx: asm8086Parser.AssemblerlogicalContext):
        super().exitAssemblerlogical(ctx)
        self.not_yet()

    def enterAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        super().enterAssemblerterm(ctx)
        self.not_yet()

    def exitAssemblerterm(self, ctx: asm8086Parser.AssemblertermContext):
        super().exitAssemblerterm(ctx)
        self.not_yet()

    def enterEndif_(self, ctx: asm8086Parser.Endif_Context):
        super().enterEndif_(ctx)
        self.not_yet()

    def exitEndif_(self, ctx: asm8086Parser.Endif_Context):
        super().exitEndif_(ctx)
        self.not_yet()

    def enterEnd(self, ctx: asm8086Parser.EndContext):
        super().enterEnd(ctx)
        self.not_yet()

    def exitEnd(self, ctx: asm8086Parser.EndContext):
        super().exitEnd(ctx)
        self.not_yet()

    def enterOrg(self, ctx: asm8086Parser.OrgContext):
        super().enterOrg(ctx)
        self.not_yet()

    def exitOrg(self, ctx: asm8086Parser.OrgContext):
        super().exitOrg(ctx)
        self.not_yet()

    def enterTitle(self, ctx: asm8086Parser.TitleContext):
        super().enterTitle(ctx)
        self.not_yet()

    def exitTitle(self, ctx: asm8086Parser.TitleContext):
        super().exitTitle(ctx)
        self.not_yet()

    def enterInclude_(self, ctx: asm8086Parser.Include_Context):
        super().enterInclude_(ctx)
        self.not_yet()

    def exitInclude_(self, ctx: asm8086Parser.Include_Context):
        super().exitInclude_(ctx)
        self.not_yet()

    def enterExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        super().enterExpressionlist(ctx)
        self.not_yet()

    def exitExpressionlist(self, ctx: asm8086Parser.ExpressionlistContext):
        super().exitExpressionlist(ctx)
        self.not_yet()

    def enterLabel(self, ctx: asm8086Parser.LabelContext):
        super().enterLabel(ctx)
        self.not_yet()

    def exitLabel(self, ctx: asm8086Parser.LabelContext):
        super().exitLabel(ctx)
        self.not_yet()

    def enterExpression(self, ctx: asm8086Parser.ExpressionContext):
        super().enterExpression(ctx)
        self.not_yet()

    def exitExpression(self, ctx: asm8086Parser.ExpressionContext):
        super().exitExpression(ctx)
        self.not_yet()

    def enterMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        super().enterMultiplyingExpression(ctx)
        self.not_yet()

    def exitMultiplyingExpression(self, ctx: asm8086Parser.MultiplyingExpressionContext):
        super().exitMultiplyingExpression(ctx)
        self.not_yet()

    def enterArgument(self, ctx: asm8086Parser.ArgumentContext):
        super().enterArgument(ctx)
        self.not_yet()

    def exitArgument(self, ctx: asm8086Parser.ArgumentContext):
        super().exitArgument(ctx)
        self.not_yet()

    def enterPtr(self, ctx: asm8086Parser.PtrContext):
        super().enterPtr(ctx)
        self.not_yet()

    def exitPtr(self, ctx: asm8086Parser.PtrContext):
        super().exitPtr(ctx)
        self.not_yet()

    def enterDollar(self, ctx: asm8086Parser.DollarContext):
        super().enterDollar(ctx)
        self.not_yet()

    def exitDollar(self, ctx: asm8086Parser.DollarContext):
        super().exitDollar(ctx)
        self.not_yet()

    def enterRegister_(self, ctx: asm8086Parser.Register_Context):
        super().enterRegister_(ctx)
        self.not_yet()

    def exitRegister_(self, ctx: asm8086Parser.Register_Context):
        super().exitRegister_(ctx)
        self.not_yet()

    def enterString_(self, ctx: asm8086Parser.String_Context):
        super().enterString_(ctx)
        self.not_yet()

    def exitString_(self, ctx: asm8086Parser.String_Context):
        super().exitString_(ctx)
        self.not_yet()

    def enterName(self, ctx: asm8086Parser.NameContext):
        super().enterName(ctx)
        self.not_yet()

    def exitName(self, ctx: asm8086Parser.NameContext):
        super().exitName(ctx)
        self.not_yet()

    def enterNumber(self, ctx: asm8086Parser.NumberContext):
        super().enterNumber(ctx)
        self.not_yet()

    def exitNumber(self, ctx: asm8086Parser.NumberContext):
        super().exitNumber(ctx)
        self.not_yet()

    def enterOpcode(self, ctx: asm8086Parser.OpcodeContext):
        super().enterOpcode(ctx)
        self.not_yet()

    def exitOpcode(self, ctx: asm8086Parser.OpcodeContext):
        super().exitOpcode(ctx)
        self.not_yet()

    def enterRep(self, ctx: asm8086Parser.RepContext):
        super().enterRep(ctx)
        self.not_yet()

    def exitRep(self, ctx: asm8086Parser.RepContext):
        super().exitRep(ctx)
        self.not_yet()

    def enterComment(self, ctx: asm8086Parser.CommentContext):
        super().enterComment(ctx)
        self.not_yet()

    def exitComment(self, ctx: asm8086Parser.CommentContext):
        super().exitComment(ctx)
        self.not_yet()
