# PEBUG

<img src=https://img.shields.io/github/languages/top/pabloniklas/pebug>

An x86 old-debug-like program.

_still an ongoing project_

The main goal of this project is to provide 
an educational and introductory interface to assmebler, x86 flavor in particular.

The user can interact directly with the memory the program presents.

The memory model es similar to the DOS (pages of 64Kb)

## Commands

This modes are available at this time;

* command mode
* arithmetic mode

### Command mode

* **d** xx yy: display memoru from _xx_ to _yy_
* **demo**: load a predefined string into the first bytes of its memoru.
* **sp** xx: set default memory page to _sp_.
* **q** or **quit**: to quit this program.

