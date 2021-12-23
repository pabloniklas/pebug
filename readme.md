# PEBUG

<img src=https://img.shields.io/github/license/pabloniklas/pebug> <img src=https://img.shields.io/github/v/release/pabloniklas/pebug> <img src=https://img.shields.io/github/languages/top/pabloniklas/pebug> <img src=https://img.shields.io/github/downloads/pabloniklas/pebug/total>


An x86 old-debug-like program.

_still an ongoing project_

The main goal of this project is to provide an educational and introductory interface to assembler, x86 flavor in
particular.

The user can interact directly with the memory the program presents.

The memory model es similar to the DOS (pages of 64Kb)

## Commands

These modes are available at this time;

* command mode
* _in the future_ arithmetic mode

### Command mode

#### General purpose

* **d** xx yy: display memory from _xx_ to _yy_
* **h** xx yy: xx and yy are two Hex values (no more than four digits each) and then it shows first the SUM, then the DIFFERENCE of those values. 
* **s** xx pp: Searches within a page, from the address _xx_ for a pattern _pp_
* **f** xx yy pp: fill memory from _xx_ to _yy_ with pattern _pp_. Without the _pp_ arguments, just blank the memory in
  the provided range.
* **demo**: load a predefined string into the first bytes of its memory.
* **r**: print cpu registers, including the state bits.
* **sp** xx: set default memory page to _sp_.
* **q**: to quit this program.
* **?** Quick help.

#### Only for the flag register

| Flag Name               | Set | Clear |
|-------------------------|-----|-------|
| Overflow(yes/no)        | ov  | nv    |
| Sign(negative/positive) | ng  | pl    |
| Zero(yes/no)            | zr  | nz    |
| Auxiliary carry(yes/no) | ac  | na    |
| Parity(even/odd)        | pe  | po    |
| Carry(yes/no)           | cy  | nc    |

## Screeshots

### display command "d"

![display](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/d.gif "display")

### hex command "h"

![hex](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/h.gif "hex")

### fill and search commands

![fas](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/fillAndSearch.gif "fas")

