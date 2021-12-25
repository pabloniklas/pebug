# PEBUG

<img src=https://img.shields.io/github/license/pabloniklas/pebug> <img src=https://img.shields.io/github/v/release/pabloniklas/pebug> <img src=https://img.shields.io/github/languages/top/pabloniklas/pebug> <img src=https://img.shields.io/github/downloads/pabloniklas/pebug/total>


An x86 old-debug-like program.

The main goal of this project is to provide an educational and introductory interface to assembler, x86 flavor in
particular.

The user can interact directly with the memory the program presents.

The memory model es similar to the DOS (pages of 64Kb)

## Status

| Stage        | Kanban Status |
|--------------|---------------|
 | Commands     | Doing         |
 | Arithmetic   | To Do         | 
 | Assembly     | To Do         | 
 | Dissassembly | To Do         | 


## Commands

### General purpose

| Command Name | Parameters  | Description                                                                                                                                              |
|--------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| d            | xx yy       | Display memory from _xx_ to _yy_.                                                                                                                        |
| e            | xx yy       | Write de byte _yy_ in the address _xx_.                                                                                                                  | 
| e            | xx 'string' | Load _string_ in memory, starting from _xx_                                                                                                              |
| f            | xx yy pp    | Fill memory from _xx_ to _yy_ with pattern _pp_. Without the _pp_ arguments, just blank the memory in the provided range                                 |
| h            | xx yy       | xx and yy are two Hex values (no more than four digits each) and then it shows first the SUM, then the DIFFERENCE of those values.                       |                                                                                                   |
| m            | xx yy zz    | This command should really be called: COPY (not Move) as it actually copies all the bytes from within the specified range _xx-yy_ to a new address _zz_. |
| r            |             | Print cpu registers, including the state bits.                                                                                                           |      
| s            | xx pp       | Searches within the current memory pege, from the address _xx_ for a pattern _pp_                                                                        | 
| q            |             | Quit the programm.                                                                                                                                       |


### Extra commands

| Command Name | Parameters | Description                                                  |
|--------------|------------|--------------------------------------------------------------|
| demo         |            | Load a predefined string into the first bytes of its memory. | 
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

## Screeshots

### display command "d"

![display](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/d.gif "display")

### hex command "h"

![hex](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/h.gif "hex")

### fill and search commands "f" & "s"

![fas](https://raw.githubusercontent.com/pabloniklas/pebug/main/screenshots/fillAndSearch.gif "fas")

