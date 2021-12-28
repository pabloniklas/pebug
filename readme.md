# PEBUG

<img src=https://img.shields.io/github/license/pabloniklas/pebug> <img src=https://img.shields.io/github/v/release/pabloniklas/pebug> <img src=https://img.shields.io/github/languages/top/pabloniklas/pebug> <img src=https://img.shields.io/github/downloads/pabloniklas/pebug/total>


An x86 old-debug-like program.

The main goal of this project is to provide an educational and introductory interface to assembler, x86 flavor in
particular.

The user can interact directly with the memory the program presents.

The memory model es similar to the DOS (pages of 64Kb)

# Status

| Stage        | Kanban Status |
|--------------|---------------|
 | Commands     | Done          |
 | Arithmetic   | Doing         | 
 | Assembly     | To Do         | 
 | Dissassembly | To Do         | 


# Commands

## General purpose

| Command Name | Parameters  | Description                                                                                                                                             |
|--------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| c            | aa bb cc    | Compare two blocks of memory. From range _aa-bb_ against _cc_.                                                                                          |
| d            | xx yy       | Display memory from _xx_ to _yy_.                                                                                                                       |
| e            | xx yy       | Write de byte _yy_ in the address _xx_.                                                                                                                 | 
| e            | xx 'string' | Load _string_ in memory, starting from _xx_                                                                                                             |
| f            | xx yy pp    | Fill memory from _xx_ to _yy_ with pattern _pp_. Without the _pp_arguments, just blank the memory in the provided range                                 |
| h            | xx yy       | xx and yy are two Hex values (no more than four digits each) and then it shows first the SUM, then the DIFFERENCE of those values.                      |                                                                                                   |
| l            | aa ff nn    | Load to memory, starting from address _aa_ from a virtual disk starting from firstsector _ff_, sizing _nn_ bytes.                                       |
| m            | xx yy zz    | This command should really be called: COPY (not Move) as it actually copies all the bytes from within the specified range _xx-yy_ to a new address _zz_. |
| n            | aa          | aa goes for the filename to be save on disk.                                                                                                            |
| r            |             | Print cpu registers, including the state bits.                                                                                                          |      
| s            | xx pp       | Searches within the current memory pege, from the address _xx_ for a pattern _pp_                                                                       | 
| q            |             | Quit the program.                                                                                                                                       |
| w            | aa ff nn    | Write to a virtual disk a memory block                                                                                                                  |


### Extra commands

| Command Name | Parameters | Description                                                  |
|--------------|------------|--------------------------------------------------------------|
| alu          |            | Enter the ALU mode.                                          |
| demo         |            | Load a predefined string into the first bytes of its memory. | 
 | cat          | aa bb      | Visualize virtual disk content from _aa_, _bb_ bytes.        |
 | sp           | xx         | Set default memory page to _sp_.                             |
 | ?            |            | Quick help.                                                  |


### Only for the flag register

| Flag Name               | Set | Clear |
|-------------------------|-----|-------|
| Overflow(yes/no)        | ov  | nv    |
| Sign(negative/positive) | ng  | pl    |
| Zero(yes/no)            | zr  | nz    |
| Auxiliary carry(yes/no) | ac  | na    |
| Parity(even/odd)        | pe  | po    |
| Carry(yes/no)           | cy  | nc    |

## ALU Mode

The following operators are available (more are coming):

| Command Name | Parameters | Description                        |
|--------------|------------|------------------------------------|
| xor          | xor a b    | "Exclusive OR" between _a_ and _b_ |


# Screenshots

## display command "d"

![display](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/d.gif "display")

## hex command "h"

![hex](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/h.gif "hex")

## fill and search commands "f" & "s"

![fas](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/fillAndSearch.gif "fas")

# Requirements

* antlr4-python3-runtime
* multipledispatch

# Author

Pablo Niklas <pablo_dot_niklas_at_gmail_dot_com>

# License

[MIT](https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt)