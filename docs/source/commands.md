# Available Commands

[Source](https://montcs.bloomu.edu/Information/LowLevel/DOS-Debug.html)


## Assemble: A

:::{note}
This is Work in Progress
:::

```A```

Interactive assemble. 

### Example

```
[C]=> a
Welcome to the Assemble mode. Enter 'q' to quit this mode.
Numbers must be in hexadecimal (0x), Decimal, or Binary (0b) format.
[C000:0000]=> mov ax,200
Machine code: [184, 0, 200]
[C000:0003]=> mov cx,10
Machine code: [185, 0, 10]
[C000:0006]=> sub ax,cx
Machine code: [41, 1]
[C000:0008]=> q
[C]=> d 0 10
                                             
C000:0000 B8 00 C8 B9 00 0A 29 01 00 00 00 00 00 00 00 ¸.È¹..)........
C000:000F 00 
[C]=> 

```

## Quit: Q

```Q```

Immediately quits (exits) the PEBUG program! No questions ever asked...
should be the first command you remember along with the "?" command.

## Hex: H value1 value2

A very simple (add and subtract only) Hex calculator.
Never forget that all numbers inside of PEBUG are always Hexadecimal.
Enter two Hex values (no more than four digits each) and PEBUG shows first the SUM,
then the DIFFERENCE of those values. Examples:

```
h 10 1
0011 000F
```

## Dump: D [range]

```D [address] [length]```

Displays the contents of a block of memory.
This first example shows we have a Matrox card in this system.

### Examples

```
d c000:0010

C000:0010 24 12 FF FF 00 00 00 00-60 00 00 00 00 20 49 42 $.......`.... IB
C000:0020 4D 20 43 4F 4D 50 41 54-49 42 4C 45 20 4D 41 54 M COMPATIBLE MAT
C000:0030 52 4F 58 2F 4D 47 41 2D-47 31 30 30 20 56 47 41 ROX/MGA-G100 VGA
C000:0040 2F 56 42 45 20 42 49 4F-53 20 28 56 31 2E 32 20 /VBE BIOS (V1.2
C000:0050 29 00 87 DB 87 DB 87 DB-87 DB 87 DB 87 DB 87 DB )...............
C000:0060 50 43 49 52 2B 10 01 10-00 00 18 00 00 00 00 03 PCIR+...........
C000:0070 40 00 12 10 00 80 00 00-38 37 34 2D 32 00 FF FF @.......874-2...
C000:0080 E8 26 56 8B D8 E8 C6 56-74 22 8C C8 3D 00 C0 74 .&V....Vt"..=..t
```

## Search: S range list

Searches within a range of addresses for a pattern of one or more byte values given in a list.
The list can be comprised of numbers or character strings enclosed by matching single or double quote marks.

### Examples

```
s fe00:0 ffff "BIOS"
FE00:0021
FE00:006F
d fe00:0
FE00:0000 41 77 61 72 64 20 53 6F-66 74 77 61 72 65 49 42 Award SoftwareIB
FE00:0010 4D 20 43 4F 4D 50 41 54-49 42 4C 45 20 34 38 36 M COMPATIBLE 486
FE00:0020 20 42 49 4F 53 20 43 4F-50 59 52 49 47 48 54 20 BIOS COPYRIGHT
FE00:0030 41 77 61 72 64 20 53 6F-66 74 77 61 72 65 20 49 Award Software I
FE00:0040 6E 63 2E 6F 66 74 77 61-72 65 20 49 6E 63 2E 20 nc.oftware Inc.
FE00:0050 41 77 03 0C 04 01 01 6F-66 74 77 E9 12 14 20 43 Aw.....oftw... C
FE00:0060 1B 41 77 61 72 64 20 4D-6F 64 75 6C 61 72 20 42 .Award Modular B
FE00:0070 49 4F 53 20 76 34 2E 35-31 50 47 00 DB 32 EC 33 IOS v4.51PG..2.3
```

## Compare: C range address

Compares two blocks of memory.
If there are no differences, then PEBUG simply displays another prompt.
Here's an example of what happens when there are differences:

```
c 140 148 340
127D:0143 30 6D 127D:0343
127D:0146 10 63 127D:0346
127D:0148 49 30 127D:0348
```

The bytes at locations 140 through 148 are being compared to those at 340 (through 348, implied);
the bytes are displayed side by side for those which are different
(with their exact locations, including the segment, on either side of them).

## Fill: F range list

This command can also be used to clear large areas of Memory as well as filling
smaller areas with a continuously repeating phrase or single byte.

### Example

```
f 100 12f 'BUFFER'
d 100 12f
xxxx:0100 42 55 46 46 45 52 42 55-46 46 45 52 42 55 46 46 BUFFERBUFFERBUFF
xxxx:0110 45 52 42 55 46 46 45 52-42 55 46 46 45 52 42 55 ERBUFFERBUFFERBU
xxxx:0120 46 46 45 52 42 55 46 46-45 52 42 55 46 46 45 52 FFERBUFFERBUFFER
```

## Enter: E address [list]

Used to enter data or instructions (as machine code) directly into Memory locations.

### Example

First we'll change a single byte at location CS:FFCB from whatever it was before to D2

```e ffcb d2```

The next two examples show that either single(') or double(")
quote marks are acceptable for entering ASCII data. By allowing both forms,
you can include the other type of quote mark within your entry string:

```e 200 'An "ASCII-Z string" is always followed by '```

```e 22a "a zero-byte ('00h')." 00```

## Load: L [address] [firstsector] [number]

This command will LOAD the selected number of sectors from the vdisk into Memory.
The address is the location in Memory the data will be copied to
(use only 4 hex digits to keep it within the memory allocated to PEBUG),
firstsector counts from ZERO to the largest sector in the volume and finally
number specifies in hexadecimal the total number of sectors that will be copied into Memory

## Move: M range address

This command should really be called: COPY (not Move) as it actually copies all the bytes from within the specified range to a new address.

### Examples

1) ```m 7c00 7cff 600```

Copies all the bytes between Offset 7C00 and 7CFF (inclusive) to Offset 0600 and following...

2) ```m 100 2ff 70```

This second example shows that it's very easy to overwrite most of the source you're copying from using
the Move command.

:::{warning}
PEBUG has protections to avoid overwritting the source bytes.
:::

## Parse: P [opcode]

```p mox ax,1974```

Allow an interactive way of executing assembler instructions, and allows you to see how this instruction impacts the CPU registers.

### Example:

```
> Type 'q' to quit the program.
[C]=> p mov ax,200
Register Decimal    Hexadecimal  Binary            
--------------------------------------------------
AX       200        0x00C8       0000000011001000  
--------------------------------------------------
[C]=> p mov cx,100
Register Decimal    Hexadecimal  Binary            
--------------------------------------------------
AX       200        0x00C8       0000000011001000  
CX       100        0x0064       0000000001100100  
--------------------------------------------------
[C]=> p add ax,cx
Register Decimal    Hexadecimal  Binary            
--------------------------------------------------
AX       300        0x012C       0000000100101100  
CX       100        0x0064       0000000001100100  
--------------------------------------------------
[C]=> 
```


## Register: R [register]

Entering ```r``` all by itself will display all of the 8086 register's contents

## Write: W [address] [firstsector] [number]

The WRITE (W) command is often used to save a program to the vdisk.

## Extra commands

| Command Name | Parameters      | Description                                                  |
|--------------|-----------------|--------------------------------------------------------------|
| ```a```    |                   | Enter the assemble mode.                                          |
| ```demo```   |                 | Load a predefined string into the first bytes of its memory. |
 | ```cat```    | ```cat aa bb``` | Visualize virtual disk content from _aa_, _bb_ bytes.        |
 | ```sp```     | ```sp xx```     | Set default memory page to _sp_.                             |
 | ```?```      |                 | Quick help.                                                  |

## Only for the flag register

| Flag Name               | Set      | Clear    |
|-------------------------|----------|----------|
| Overflow(yes/no)        | ```ov``` | ```nv``` |
| Sign(negative/positive) | ```ng``` | ```pl``` |
| Zero(yes/no)            | ```zr``` | ```nz``` |
| Auxiliary carry(yes/no) | ```ac``` | ```na``` |
| Parity(even/odd)        | ```pe``` | ```po``` |
| Carry(yes/no)           | ```cy``` | ```nc``` |

## Parse Mode

The following operators are available (more are coming):

| Command Name | Parameters    | Description                        |
|--------------|---------------|------------------------------------|
| ```mov```    | ```mov a, b``` | Move (assign) operation between _a_ and _b_ |
| ```add```    | ```add a, b``` | Add operation between _a_ and _b_ |
| ```sub```    | ```sub a, b``` | Substract operation between _a_ and _b_ |
| ```xor```    | ```xor a b``` | "Exclusive OR" between _a_ and _b_ |
| ```or```     | ```or a b```  | OR between _a_ and _b_             |
| ```and```    | ```and a b``` | AND between _a_ and _b_            |
| ```not```    | ```not a```   | NOT of _a_                         |
| ```shl```    | ```shl a```   | Shift to the left of _a_           |
| ```shr```    | ```shr a```   | Shift to the right of _a_          |

# Work In Progress

## Assemble: A [address]

Enter in interactive assemble mode (IAM). Exit with "q"

## Go: G [=address] [addresses]

Go is used to run a program and set breakpoints in the program's code.

:::{note}
Input / Output commands (regarding ports), are not available.
:::

