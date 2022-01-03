# Commands

## General purpose

| Command Name | Usage             | Description                                                                                                                                              |
|--------------|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| ```c```      | ``` c aa bb cc``` | Compare two blocks of memory. From range _aa-bb_ against _cc_.                                                                                           |
| ```d```      | ```d xx yy```     | Display memory from _xx_ to _yy_.                                                                                                                        |
| ```e```      | ```e xx yy```     | Write de byte _yy_ in the address _xx_.                                                                                                                  | 
| ```e```      | ```xx 'string'``` | Load _string_ in memory, starting from _xx_                                                                                                              |
| ```f```      | ```xx yy pp```    | Fill memory from _xx_ to _yy_ with pattern _pp_. Without the _pp_arguments, just blank the memory in the provided range                                  |
| ```h```      | ```h xx yy```     | _xx_ and _yy_ are two Hex values (no more than four digits each) and then it shows first the SUM, then the DIFFERENCE of those values.                   |                                                                                                   |
| ```l```      | ```l aa ff nn```  | Load to memory, starting from address _aa_ from a virtual disk starting from firstsector _ff_, sizing _nn_ bytes.                                        |
| ```m```      | ```m xx yy zz```  | This command should really be called: COPY (not Move) as it actually copies all the bytes from within the specified range _xx-yy_ to a new address _zz_. |
| ```n```      | ```n aa```        | _aa_ goes for the filename to be save on disk.                                                                                                           |
| ```r```      |                   | Print cpu registers, including the state bits.                                                                                                           |      
| ```s```      | ```s xx pp```     | Searches within the current memory pege, from the address _xx_ for a pattern _pp_                                                                        | 
| ```q```      |                   | Quit the program.                                                                                                                                        |
| ```w```      | ```w aa ff nn```  | Write to a virtual disk a memory block                                                                                                                   |

### Extra commands

| Command Name | Parameters      | Description                                                  |
|--------------|-----------------|--------------------------------------------------------------|
| ```alu```    |                 | Enter the ALU mode.                                          |
| ```demo```   |                 | Load a predefined string into the first bytes of its memory. | 
 | ```cat```    | ```cat aa bb``` | Visualize virtual disk content from _aa_, _bb_ bytes.        |
 | ```sp```     | ```sp xx```     | Set default memory page to _sp_.                             |
 | ```?```      |                 | Quick help.                                                  |


### Only for the flag register

| Flag Name               | Set      | Clear    |
|-------------------------|----------|----------|
| Overflow(yes/no)        | ```ov``` | ```nv``` |
| Sign(negative/positive) | ```ng``` | ```pl``` |
| Zero(yes/no)            | ```zr``` | ```nz``` |
| Auxiliary carry(yes/no) | ```ac``` | ```na``` |
| Parity(even/odd)        | ```pe``` | ```po``` |
| Carry(yes/no)           | ```cy``` | ```nc``` |


## ALU Mode

The following operators are available (more are coming):

| Command Name | Parameters    | Description                        |
|--------------|---------------|------------------------------------|
| ```xor```    | ```xor a b``` | "Exclusive OR" between _a_ and _b_ |
| ```or```     | ```or a b```  | OR between _a_ and _b_             |
| ```and```    | ```and a b``` | AND between _a_ and _b_            |
| ```not```    | ```not a```   | NOT of _a_                         |
| ```shl```    | ```shl a```   | Shift to the left of _a_           |
| ```shr```    | ```shr a```   | Shift to the right of _a_          |
