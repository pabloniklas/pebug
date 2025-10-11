¡Listo! Acá tenés una **versión actualizada del README** (en inglés, manteniendo el estilo original), con la nueva sección **“New in this version”** y reflejando todos los cambios recientes (assembler/disassembler, trace, breakpoints, watches, INT 21h, etc.). Solo **copiá y pegá** en tu `README.md`.

---

<img src="https://raw.githubusercontent.com/pabloniklas/pebug/refs/heads/main/logo/pebug_logo.png">

<img src="https://img.shields.io/github/license/pabloniklas/pebug"> <img src="https://img.shields.io/github/v/release/pabloniklas/pebug"> <img src="https://img.shields.io/github/languages/top/pabloniklas/pebug"> <img src="https://img.shields.io/github/downloads/pabloniklas/pebug/total">

An x86 old-debug-like program.

The main goal of this project is to build an educational simulator for the 8086 assembly language that enables students to learn and practice assembly instructions interactively. The simulator provides detailed feedback, real-time error detection, and a clear, visual display of register and flag changes after each instruction to help students understand both syntax and low-level register manipulation.

The memory model is similar to DOS (pages of 64 KB).

---

## New in this version

* **Assembler is now stable (educational / pseudo-encoding)**
  `assemble_line` / `assemble_program` for mnemonics like `MOV`, `ADD`, `SUB`, `AND`, `OR`, `XOR`, `NOT`, `NEG`, `INC`, `DEC`, `SHL`, `SHR`, `ROL`, `ROR`, `PUSH`, `POP`, and `INT`.
  Supports immediates in **hex (`0x` or `0X`)**, decimal, and binary (`0b`).

* **Step-by-step execution & compact trace**
  `load_program`, `step`, `cont`, with a compact trace format:
  *mnem → pseudo-bytes → regs/flags Δ → memory access* (toggle on/off for demos).

* **Simple breakpoints & watches**
  Breakpoints by **label** or **address**; watches for **registers** (e.g., `AX`), **flags** (e.g., `FLAGS.CF`), and **memory** (e.g., `[DS:DX]`).

* **PUSH/POP via Memory & correct CF on shifts/rotates**
  Proper little-endian stack writes/reads; `SHL/SHR/ROL/ROR` update **CF** and flags.

* **INT 21h DOS services (subset)**
  AH=**09h** (print `$`-terminated string), AH=**0Ah** (buffered input), AH=**4Ch** (terminate).

* **Mini–disassembler**
  `disassemble_line` / `disassemble_program` over the same pseudo-encoding, showing source + pseudo-bytes.

* **Test suite expanded**
  Unit tests for assembler, stepping, breakpoints, watches, INT 21h, and memory/CPU ops.

---

## Simulator Description

### Assembler Functionality

* Supports arithmetic, logical, and bitwise operations on registers:
  **MOV, ADD, SUB, AND, OR, XOR, NOT, NEG, INC, DEC, SHL, SHR, ROL, ROR, PUSH, POP, INT**.
* `assemble_line()` / `assemble_program()` convert assembly into **educational pseudo machine code** (documented in the project).
* Step-by-step execution helpers to run assembled lines and observe effects.

### Disassembler Functionality

* `disassemble_line()` / `disassemble_program()` convert pseudo machine code back to assembly (didactic subset).
* Shows pseudo-bytes alongside the instruction.
* Emits helpful messages for unsupported patterns.

### Educational Error Messages

* Clear, detailed messages to identify syntax and logic errors.
* Actionable tips (e.g., “TIP: ensure both operands are valid registers or an immediate value”).

### Visualization of Registers and Flags

* Register view in **decimal**, **hex**, and **binary**.
* “Changed-only” view to focus on what each instruction modified.
* Flag visualization (**ZF**, **SF**, **PF**, **CF**) with updates per step.

### Support for Multiple Numeric Formats

* Accepts **binary** (`0b...`), **hex** (`0x...` or `0X...`), and **decimal** immediates with automatic conversion.

### Real-Time Feedback and Step-by-Step Execution

* Execute instructions step-by-step and see in real time the effect on registers and flags.
* After each step, display modified registers and updated flags.

---

## Educational Goal

This simulator provides an interactive learning tool for 8086 assembly students, helping them understand both the structure and syntax of assembly code and the internal workings of register/flag manipulation at processor level.

---

## Status

| Stage         | Kanban Status  |
| ------------- | -------------- |
| Commands      | Done           |
| Arithmetic    | Done           |
| Assembler     | Done           |
| Disassembly   | **Basic Done** |
| Tracing/Debug | **Done**       |

---

## Docs

Docs are published at: **[https://pebug.readthedocs.io/en/latest/](https://pebug.readthedocs.io/en/latest/)**

To build locally (Sphinx + MyST):

```bash
# from repo root
python3 -m pip install -r requirements-dev.txt
sphinx-build -M html docs/source docs/output
# open docs/output/html/index.html
```

> If you enable MyST’s `linkify`, also install `linkify-it-py`.
> If Sphinx warns about `_static`, either create `docs/source/_static` or remove `html_static_path` from `conf.py`.

---

## Screenshots

### display command `d`

![display](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/d.gif "display")

### hex command `h`

![hex](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/h.gif "hex")

### fill and search commands `f` & `s`

![fas](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/fillAndSearch.gif "fas")

---

## Quickstart (CLI, example)

```text
A                ; enter Assemble mode (educational encoding)
; numbers: 0x.. / 0X.. / decimal / 0b..
[C000:0000]=> mov ax,200
[C000:0003]=> add ax,1
[C000:0007]=> mov ax,0x0900   ; AH=09h
[C000:000A]=> int 0x21        ; prints DS:DX '$'-terminated string

P MOV AX,1974   ; Parse & execute an instruction and see effects
TRACE ON        ; enable compact trace (mnem → bytes → regs/flags Δ → mem)
BP EMIT         ; set breakpoint by label or address
WATCH AX        ; watch a register/flag/memory location
```

---

## Tests

```bash
python3 -m pip install -r requirements-dev.txt
pytest
# or
pytest -q
```

---

## Requirements

**Runtime**

* `rply`
* `multipledispatch`

**Dev/Test (optional)**

* `pytest`, `pytest-cov`
* `sphinx`, `myst-parser` (and optionally `linkify-it-py` if you enable linkify)
* `sphinx-autobuild` (live docs)
* `black`, `ruff`, `mypy` (optional quality checks)

---

## Author

Pablo Niklas <pablo_dot_niklas_at_gmail_dot_com>

---

## License

[MIT](https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt)
