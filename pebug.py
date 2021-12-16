#!/usr/bin/env python3

import re
import sys

from classes.Cpu import Cpu
from classes.Memory import Memory


def pebug_main():
    print("")

    cpu = Cpu()
    memory = Memory(65536)
    stack = Memory(1)

    prompt = "[C]=> "

    print("pebug - Python 8086 Assembler.")
    print("An x86 old-debug-like program.")
    print("Enter <h> for help.")
    print("By Pablo Niklas <pablo.niklas@gmail.com>.")
    print(f"Main memory size: {memory.pages} pages.")
    print(f"Stack size: {stack.pages} page/s.")

    # https: // montcs.bloomu.edu / Information / LowLevel / DOS - Debug.html
    cmd = input(f"{prompt}").lower()
    while cmd != "q":

        if cmd == "s":
            cpu.print_registers()
        elif re.match("^d [0-9a-f]{,4} [0-9a-f]{,4}$", cmd):
            args = cmd.split(" ")
            a = int(args[1], 16)
            b = int(args[2], 16)
            memory.display(a, b)
        elif re.match("^sp [0-9a-f]{,4}$", cmd):
            arg = cmd.split(" ")
            memory.page_cursor = int(arg[1], 16)
        elif cmd == "demo":
            memory.poke(0, 0, ord("G"))
            memory.poke(0, 1, ord("E"))
            memory.poke(0, 2, ord("E"))
            memory.poke(0, 3, ord("K"))
            memory.poke(0, 4, ord("S"))
            memory.poke(0, 5, ord(" "))
            memory.poke(0, 6, ord("X"))
            memory.poke(0, 7, ord("X"))
            memory.poke(0, 8, ord("X"))
        else:
            print("Input Not recognized.")

        cmd = input(f"{prompt}").lower()


# Python's entry point
if __name__ == '__main__':
    pebug_main()

sys.exit(0)
