# About

[PEBUG](https://github.com/pabloniklas/pebug) is a x86 old-debug-like program focused on didactic use.

An x86 old-debug-like program.

The main goal of this project is to build an educational simulator for the 8086 assembly language that enables students to learn and practice assembly instructions interactively. This simulator should provide detailed feedback, real-time error detection, and a clear, visual display of register and flag changes after each instruction to help students understand both syntax and low-level register manipulation.

The memory model es similar to DOS (pages of 64Kb)

## Simulator Description

### Assembler Functionality

- **Assembler**: `assemble_line` / `assemble_program` convert assembly to pseudo machine code (educational encoding).
- **Step-by-step execution**: `load_program`, `step`, `cont`, basic breakpoints and watches, and **compact trace** (*mnem → bytes → regs/flags Δ → mem access*).
- **INT 21h**: supported services AH=09h (print `$` string), AH=0Ah (buffered input), AH=4Ch (terminate).

### Disassembler Functionality

- **Mini-disassembler**: `disassemble_line` / `disassemble_program` over the same pseudo-encoding.
- Recognizes mnemonics and immediates and shows **pseudo bytes** alongside the source line.
- Show meaningful errors if any unsupported or unknown opcodes are encountered.

### Educational Error Messages

- Include a function to show only the registers that changed after each instruction, helping students focus on the operations performed.
- Visualize flags (Zero, Sign, Parity, Carry) and show their updates after each executed instruction.

### Visualization of Registers and Flags

- Offer a register view that displays values in decimal, hexadecimal, and binary formats.
- Include a function to show only the registers that changed after each instruction, helping students focus on the operations performed.
- Visualize flags (Zero, Sign, Parity, Carry) and show their updates after each executed instruction.

### Support for Multiple Numeric Formats

- Allow numbers to be inputted in binary (0b...), hexadecimal (0x... **or 0X...**), and decimal formats, with automatic conversion.

### Real-Time Feedback and Step-by-Step Execution

- Enable step-by-step execution of each assembly instruction, showing in real-time how each operation affects registers and flags.
- After each step, display modified registers and updated flag values.

## Educational Goal

This simulator aims to provide an interactive learning tool for students of 8086 assembly language, helping them understand both the structure and syntax of assembly code and the internal workings of register and flag manipulation on a processor level.

## Status

| Stage        | Kanban Status |
|--------------|---------------|
| Commands     | Done          |
| Arithmetic   | Done          |
| Assembler    | Done          |
| Disassembly  | **Basic Done** |
| Tracing/Debug | **Done**      |

:::{note}
The memory model is similar to DOS's (pages of 64Kb).
:::
