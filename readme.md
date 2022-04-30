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
 | Arithmetic   | Done          | 
 | Assembly     | Doing         | 
 | Dissassembly | To Do         | 


# Docs

I've migrated the docs to https://pebug.readthedocs.io/en/latest/

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