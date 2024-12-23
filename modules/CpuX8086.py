from typing import (
    List,
    Dict,
    Tuple,
    Optional
)

import re

from multipledispatch import dispatch

from rply import (
    ParserGenerator,
    LexerGenerator
)

if __name__ is not None and "." in __name__:
    from .Memory import Memory
    from .Disk import Disk
    from .Terminal import Terminal, AnsiColors
else:
    from Memory import Memory
    from Disk import Disk
    from Terminal import Terminal, AnsiColors

# https://joshsharp.com.au/blog/rpython-rply-interpreter-1.html

class RegisterSet:
    """
    Represents a set of processor registers and flags.
    Provides methods to get, set, and display registers, as well as update
    flag values based on assembly operations.
    """
    def __init__(self)  -> None:
        """
        Initializes processor registers and flags.
        Sets up a dictionary to track the previous values of registers before any changes.
        """
        self.registers = {
            'AX': 0, 'BX': 0, 'CX': 0, 'DX': 0,
            'SP': 0, 'BP': 0, 'SI': 0, 'DI': 0,
            'CS': 0, 'DS': 0, 'SS': 0, 'ES': 0, 'FS': 0, 'GS': 0
        }
        # Flags: Zero (ZF), Sign (SF), Parity (PF), and Carry (CF)
        self.flags = {'ZF': 0, 'SF': 0, 'PF': 0, 'CF': 0}

        # Diccionario para rastrear los valores anteriores de los registros
        self.last_values = self.registers.copy()
        self.registers_supported = list(self.registers.keys())        
        self.terminal = Terminal()


    @dispatch(str)
    def get(self, reg: str) -> int:
        """
        Retrieves the value of the specified register.

        Args:
            reg (str): Name of the register.

        Returns:
            int: Current value of the specified register.
        """
        return self.registers.get(reg.upper(), None)

    @dispatch(str, int)
    def set(self, reg: str, value: int) -> None:
        """
        Sets a value in the specified register and updates the previous value.

        Args:
            reg (str): Name of the register.
            value (int): Value to set in the register.

        Returns:
            None
        """
        reg = reg.upper()
        if reg in self.registers:
            # Guarda el valor actual en last_values antes de actualizar
            self.last_values[reg] = self.registers[reg]
            self.registers[reg] = value & 0xFFFF

    def update_flags(self, result: int, operation: Optional[str] = None, carry: Optional[bool] = None) -> None:
        """
        Updates flags (ZF, SF, PF, CF) based on the result of an operation.

        Args:
            result (int): Result of the performed operation.
            operation (str, optional): Type of operation ('ADD' or 'SUB') to update CF.
            carry (bool, optional): Indicates if there was a carry for CF in ADD operations.

        Returns:
            None
        """
        # Zero Flag: Set if the result is zero
        self.flags['ZF'] = 1 if result == 0 else 0
        # Sign Flag: Set if the most significant bit is set (negative in signed interpretation)
        self.flags['SF'] = 1 if (result & 0x8000) != 0 else 0
        # Parity Flag: Set if the number of bits set in result is even
        self.flags['PF'] = 1 if bin(result).count("1") % 2 == 0 else 0
        # Carry Flag: Used in ADD and SUB operations
        if operation == 'ADD':
            self.flags['CF'] = 1 if carry else 0
        elif operation == 'SUB':
            self.flags['CF'] = 1 if result < 0 else 0

    def print_changed_registers(self) -> None:
        """
        Prints only the registers whose value has changed in the last executed operation.

        Returns:
            None
        """
        
        c = AnsiColors  # Alias para simplificar
        
        print(f"{c.BRIGHT_YELLOW.value}{'Register':<8} {'Decimal':<10} {'Hexadecimal':<12} {'Binary':<18}{c.RESET.value}")
        print(c.BRIGHT_BLACK.value+"-" * 50+c.RESET.value)
        for reg, value in self.registers.items():
            if value != self.last_values[reg]:  # Comparar con el valor anterior
                dec_value = value
                hex_value = f"0x{value:04X}"
                bin_value = f"{value:016b}"
                print(f"{c.BRIGHT_GREEN.value}{reg:<8} {c.BRIGHT_WHITE.value}{dec_value:<10} {c.BRIGHT_BLUE.value}{hex_value:<12} {c.BRIGHT_CYAN.value}{bin_value:<18}{c.RESET.value}")
        print(c.BRIGHT_BLACK.value+"-" * 50+c.RESET.value)

    def print_registers(self) -> None:
        """
        Prints all registers and flags in decimal, hexadecimal, and binary formats.

        Returns:
            None
        """
        self.terminal.info_message(f"{'Register':<8} {'Decimal':<10} {'Hexadecimal':<12} {'Binary':<18}")
        self.terminal.info_message("-" * 50)
        for reg, value in self.registers.items():
            dec_value = value
            hex_value = f"0x{value:04X}"
            bin_value = f"{value:016b}"
            self.terminal.info_message(f"{reg:<8} {dec_value:<10} {hex_value:<12} {bin_value:<18}")

        # Print the flags below the registers
        self.terminal.info_message("\nStatus Flags:")
        self.terminal.info_message(f"Zero Flag (ZF): {self.flags['ZF']}")
        self.terminal.info_message(f"Sign Flag (SF): {self.flags['SF']}")
        self.terminal.info_message(f"Parity Flag (PF): {self.flags['PF']}")
        self.terminal.info_message(f"Carry Flag (CF): {self.flags['CF']}")


    def set_register_upper(self, reg: int, value: int) -> int:
        """Set the upper 8 bits of a 16-bit register to a new value.

        Args:
            reg (int): 16bit value
            value (int): 8bit value

        Returns:
            int: 16bit value with the upper 8 bits set to the new value.
        """
        reg = (reg & 0x00ff) | (value << 8)
        return reg

    def set_register_lower(self, reg: int, value: int) -> int:
        """Set the lower 8 bits of a 16-bit register to a new value.

        Args:
            reg (int): 16bit value
            value (int): 8bit value

        Returns:
            int: 16bit value with the lower 8 bits set to the new value.
        """

        # Clear the lower 8 bits of the register
        reg &= 0xFF00

        # Set the lower 8 bits of the register to the new value
        reg |= value

        return reg

class InstructionParser:
    """
    Parses and executes assembly instructions, handling arithmetic and bitwise operations
    on registers, and providing detailed error messages.
    """
    def __init__(self) -> None:
        """
        Configures the lexer and parser to analyze assembly instructions.
        Initializes the maps of instruction methods and machine codes.
        """
        # Configuración de lexer y parser
        self.lexer = LexerGenerator()
        self.lexer.add("OPCODE", r"(?i)mov|add|sub|and|or|xor|not|neg|inc|dec|shl|shr|rol|ror|push|pop|int")
        self.lexer.add("REGISTER", r"(?i)AX|BX|CX|DX|SP|BP|SI|DI|CS|DS|SS|ES|FS|GS")
        self.lexer.add("NUMBER", r"0b[01]+|0x[0-9a-fA-F]+|\d+")
        self.lexer.add("COMMA", r",")
        self.lexer.add("COMMENT", r";.*")
        self.lexer.ignore(r"\s+")
        self.lexer = self.lexer.build()

        self.pg = ParserGenerator(["OPCODE", "REGISTER", "NUMBER", "COMMA"])
        self.pg.production("instruction : OPCODE operands")(self.handle_instruction)
        self.pg.production("operands : operand COMMA operand")(self.operands_multiple)
        self.pg.production("operand : REGISTER")(self.operand_register)
        self.pg.production("operand : NUMBER")(self.operand_number)
        self.pg.error(self.handle_parse_error)
        self.parser = self.pg.build()
        self.terminal = Terminal()

        self.opcode_map = {
            'MOV': {'reg, imm16': 'B8', 'reg, reg': '89', 'mem, reg': '8B', 'reg, mem': '8A'},
            'ADD': {'reg, imm16': '05', 'reg, reg': '01'},
            'SUB': {'reg, imm16': '2D', 'reg, reg': '29'},
            'AND': {'reg, imm16': '25', 'reg, reg': '21'},
            'OR': {'reg, imm16': '0D', 'reg, reg': '09'},
            'XOR': {'reg, imm16': '35', 'reg, reg': '31'},
            'INC': {'reg': '40'},
            'DEC': {'reg': '48'},
            'SHL': {'reg': 'D0E0'},
            'SHR': {'reg': 'D0E8'},
            'ROL': {'reg': 'D0C0'},
            'ROR': {'reg': 'D0C8'},
            'NOT': {'reg': 'F7D0'},
            'NEG': {'reg': 'F7D8'},
            'PUSH': {'reg': '50'},
            'POP': {'reg': '58'},
            'INT' : ['0x21'],
        }

        self.mnemonic_map = {
            'B8': 'MOV reg, imm16', '89': 'MOV reg, reg', '8B': 'MOV mem, reg', '8A': 'MOV reg, mem',
            '05': 'ADD reg, imm16', '01': 'ADD reg, reg',
            '2D': 'SUB reg, imm16', '29': 'SUB reg, reg',
            '25': 'AND reg, imm16', '21': 'AND reg, reg',
            '0D': 'OR reg, imm16',  '09': 'OR reg, reg',
            '35': 'XOR reg, imm16', '31': 'XOR reg, reg',
            '40': 'INC reg', '48': 'DEC reg',
            'D0E0': 'SHL reg', 'D0E8': 'SHR reg',
            'D0C0': 'ROL reg', 'D0C8': 'ROR reg',
            'F7D0': 'NOT reg', 'F7D8': 'NEG reg',
            '50': 'PUSH reg', '58': 'POP reg',
        }

        self.opcode_methods = {
            'MOV': self.asm_mov,
            'ADD': self.asm_add,
            'SUB': self.asm_sub,
            'AND': self.asm_and,
            'OR': self.asm_or,
            'XOR': self.asm_xor,
            'NOT': self.asm_not,
            'NEG': self.asm_neg,
            'INC': self.asm_inc,
            'DEC': self.asm_dec,
            'SHL': self.asm_shl,
            'SHR': self.asm_shr,
            'ROL': self.asm_rol,
            'ROR': self.asm_ror,
            'PUSH': self.asm_push,
            'POP': self.asm_pop,
        }

        self.supported_instructions = list(self.opcode_methods.keys())  # Lista de instrucciones soportadas

        # Mapeo de registros a sus correspondientes códigos binarios
        self.register_codes = {'AX': '000', 'CX': '001', 'DX': '010', 'BX': '011'}

        # Instancia de RegisterSet
        self.register_collection = RegisterSet()
        self.supported_registers = self.register_collection.registers_supported

    def handle_instruction(self, p: list) -> None:
        """
        Calls the appropriate operation method based on the opcode.

        Args:
            p (list): List of instruction tokens.

        Returns:
            None
        """
        opcode = p[0].getstr().upper()
        operands = p[1]
        method = self.opcode_methods.get(opcode)
        if method:
            try:
                method(operands)
            except Exception as e:
                self.terminal.error_message(f"ERROR: Execution error in '{opcode} {operands}': {e}")
        else:
            self.terminal.error_message(f"ERROR: Unsupported instruction '{opcode}'.")

    def operands_multiple(self, p: list) -> list:
        """
        Converts a list of operands into a manageable list of two elements.

        Args:
            p (list): List of operand tokens.

        Returns:
            list: List containing the first and third tokens.
        """
        return [p[0], p[2]]

    def operand_register(self, p: list) -> str:
        """
        Gets the register name in uppercase.

        Args:
            p (list): Register token.

        Returns:
            str: Register name in uppercase.
        """
        return p[0].getstr().upper()

    def operand_number(self, p: list) -> Optional[int]:
        """
        Converts a number from binary, hexadecimal, or decimal to decimal format.

        Args:
            p (list): Number token in binary, hexadecimal, or decimal format.

        Returns:
            int: Decimal value of the number.
        """
        value = p[0].getstr()
        # Detecta el formato y convierte el valor
        try:
            if value.startswith("0b"):
                return int(value, 2)  # Binario
            elif value.startswith("0x"):
                return int(value, 16)  # Hexadecimal
            else:
                return int(value)  # Decimal
        except ValueError:
            self.terminal.error_message(f"ERROR: Invalid number format '{value}'. Expected binary (0b), hex (0x), or decimal.")
            return None

    def handle_parse_error(self, token) -> None:
        """
        Displays an error message when a syntax error occurs in the parser.

        Args:
            token (Token): Token that caused the syntax error.

        Returns:
            None
        """
        self.terminal.error_message(f"SYNTAX ERROR: Unexpected token '{token.getstr()}' at position {token.getsourcepos().idx}.")
        self.terminal.info_message("TIP: Check the instruction format. An instruction should follow 'OPCODE REGISTER, NUMBER' or 'OPCODE REGISTER, REGISTER'.")

    def parse(self, instruction: str, memory: Memory) -> dict:
        """
        Parses a single assembly instruction, executes it, and returns its details.

        Args:
            instruction (str): Assembly instruction as a text string.
            memory (Memory): Memory object representing the system's memory.

        Returns:
            dict: Parsed tokens including opcode and operands.

        Raises:
            ValueError: If the instruction format is invalid.
            KeyError: If the opcode is not supported.
        """
        instruction = instruction.strip().upper()
        tokens = instruction.split()

        if len(tokens) < 1:
            raise ValueError(f"Invalid instruction format: '{instruction}'")

        try:
            # Handle INT 0x21
            if tokens[0] == "INT" and len(tokens) == 2 and tokens[1] == "0X21":
                ah = self.register_collection.get('AX') >> 8  # Obtener AH (parte alta de AX)
                self.int_0x21(ah, memory, self.register_collection)
                return {'opcode': 'INT', 'operands': ['0x21']}

            opcode = tokens[0]
            if opcode not in self.opcode_methods:
                raise KeyError(f"Unsupported opcode '{opcode}' in instruction: '{instruction}'")

            # Split operands by comma and strip spaces
            operands = [op.strip() for op in ' '.join(tokens[1:]).split(',')]

            # Manejo especial para PUSH y POP (un solo operando)
            if opcode in ['PUSH', 'POP'] and len(operands) != 1:
                raise ValueError(f"Invalid operand format for '{opcode}': '{instruction}'")

            # Convert immediate values to integers
            for i, operand in enumerate(operands):
                if operand.isdigit() or operand.startswith("0X"):
                    operands[i] = int(operand, 16) if operand.startswith("0X") else int(operand)

            # Invocar el método correspondiente al opcode
            method = self.opcode_methods[opcode]
            method(operands)

            return {'opcode': opcode, 'operands': operands}

        except Exception as e:
            raise ValueError(f"Error parsing instruction: '{instruction}' -> {e}")

    def int_0x21(self, ah: int, memory: dict, registers: dict) -> None:
        """
        Simula la interrupción 0x21 para servicios básicos de DOS.

        Args:
            ah (int): El registro AH contiene el número del servicio.
            memory (dict): Simulación de la memoria del sistema.
            registers (dict): Registros del procesador (AX, BX, CX, etc.).

        Returns:
            None
        """
        
        print('''
            Welcome to INT21:
            ~~~~~~~~~~~~~~~~~
            Only a few services are supported:

            - Service 0x09: Print strings terminated in '$'.
            - Service 0x0A: Read strings with a limit.
            - Service 0x4C: End program. ''')        
        
        if ah == 0x09:  # Mostrar cadena terminada en '$'
            self.service_09(memory, registers)
        elif ah == 0x0A:  # Leer cadena con límite
            self.service_0a(memory, registers)
        elif ah == 0x4C:  # Terminar programa
            self.service_4c(registers)
        else:
            raise ValueError(f"Unsupported INT 0x21 service: 0x{ah:02X}")

    def service_09(self, memory: dict, registers: dict) -> None:
        """
        Servicio 0x09: Mostrar cadena terminada en '$'.

        Args:
            memory (dict): Simulación de la memoria del sistema.
            registers (dict): Registros del procesador.

        Returns:
            None
        """
        ds = registers['DS']  # Segmento de datos
        dx = registers['DX']  # Desplazamiento
        address = (ds << 4) + dx

        output = ""
        while memory[address] != ord('$'):  # Leer hasta encontrar '$'
            output += chr(memory[address])
            address += 1

        print(output, end="")

    def service_0a(self, memory: dict, registers: dict) -> None:
        """
        Servicio 0x0A: Leer cadena con límite.

        Args:
            memory (dict): Simulación de la memoria del sistema.
            registers (dict): Registros del procesador.

        Returns:
            None
        """
        ds = registers['DS']  # Segmento de datos
        dx = registers['DX']  # Desplazamiento
        address = (ds << 4) + dx

        max_length = memory[address]  # Longitud máxima de la cadena
        address += 1

        input_str = input("Enter string: ")[:max_length]
        memory[address] = len(input_str)  # Longitud real de la cadena
        address += 1

        for i, char in enumerate(input_str):
            memory[address + i] = ord(char)

        memory[address + len(input_str)] = 0x00  # Fin de cadena

    def service_4c(self, registers: dict) -> None:
        """
        Servicio 0x4C: Terminar programa.

        Args:
            registers (dict): Registros del procesador.

        Returns:
            None
        """
        exit_code = registers['AL']
        print(f"\nProgram terminated with exit code {exit_code}")
        exit(exit_code)

    @dispatch(list)
    def asm_push(self, operands: list, memory: Memory) -> None:
        """
        Handles the 'PUSH' instruction.

        Args:
            operands (list): A list containing the register to push.

        Returns:
            None
        """
        reg = operands[0]
        if reg not in self.register_codes:
            raise ValueError(f"Invalid register '{reg}' for PUSH")

        value = self.register_collection.get(reg)
        sp = self.register_collection.get("SP")

        # Decrement SP and store value at the memory location
        sp -= 2
        memory.poke(sp, value & 0xFF)  # Lower byte
        memory.poke(sp + 1, (value >> 8) & 0xFF)  # Upper byte
        self.register_collection.set("SP", sp)

    @dispatch(list)
    def asm_pop(self, operands: list, memory: Memory) -> None:
        """
        Handles the 'POP' instruction.

        Args:
            operands (list): A list containing the register to pop.

        Returns:
            None
        """
        reg = operands[0]
        if reg not in self.register_codes:
            raise ValueError(f"Invalid register '{reg}' for POP")

        sp = self.register_collection.get("SP")

        # Retrieve value from memory and increment SP
        low = memory.peek(sp)
        high = memory.peek(sp + 1)
        value = (high << 8) | low
        self.register_collection.set(reg, value)
        self.register_collection.set("SP", sp + 2)


    # Operaciones de ensamblador
    @dispatch(list)
    def asm_mov(self, operands: list) -> None:
        """
        Executes the MOV instruction, moving a value to a register.

        Args:
            operands (list): List of operands (destination and source).

        Returns:
            None
        """
        try:
            dest, src = operands
            if isinstance(src, int):
                self.register_collection.set(dest, src)
            else:
                self.register_collection.set(dest, self.register_collection.get(src))
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' or '{src}' in MOV operation.")
            self.terminal.info_message("TIP: Ensure that both operands are valid registers or an immediate value.")

    @dispatch(list)
    def asm_add(self, operands: list) -> None:
        """
        Executes the ADD instruction, adding a value to a register.

        Args:
            operands (list): List of operands (destination and source).

        Returns:
            None
        """
        try:
            dest, src = operands
            result = self.register_collection.get(dest) + (src if isinstance(src, int) else self.register_collection.get(src))
            self.register_collection.set(dest, result & 0xFFFF)
            self.register_collection.update_flags(result, operation='ADD')
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' or '{src}' in ADD operation.")
            self.terminal.info_message("TIP: Both operands must be valid registers or an immediate value.")

    @dispatch(list)
    def asm_sub(self, operands: list) -> None:
        """
        Executes the SUB instruction, subtracting a value from a register.

        Args:
            operands (list): List of operands (destination and source).

        Returns:
            None
        """
        try:
            dest, src = operands
            result = self.register_collection.get(dest) - (src if isinstance(src, int) else self.register_collection.get(src))
            self.register_collection.set(dest, result & 0xFFFF)
            self.register_collection.update_flags(result, operation='SUB')
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' or '{src}' in SUB operation.")
            self.terminal.info_message("TIP: Both operands must be valid registers or an immediate value.")

    @dispatch(list)
    def asm_and(self, operands: list) -> None:
        """
        Executes the AND instruction, performing a bitwise AND on a register.

        Args:
            operands (list): List of operands (destination and source).

        Returns:
            None
        """
        try:
            dest, src = operands
            result = self.register_collection.get(dest) & (src if isinstance(src, int) else self.register_collection.get(src))
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' or '{src}' in AND operation.")
            self.terminal.info_message("TIP: Both operands must be valid registers or an immediate value.")

    @dispatch(list)
    def asm_or(self, operands: list) -> None:
        """
        Executes the OR instruction, performing a bitwise OR on a register.

        Args:
            operands (list): List of operands (destination and source).

        Returns:
            None
        """
        try:
            dest, src = operands
            result = self.register_collection.get(dest) | (src if isinstance(src, int) else self.register_collection.get(src))
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' or '{src}' in OR operation.")
            self.terminal.info_message("TIP: Both operands must be valid registers or an immediate value.")

    @dispatch(list)
    def asm_xor(self, operands: list) -> None:
        """
        Executes the XOR instruction, performing a bitwise XOR on a register.

        Args:
            operands (list): List of operands (destination and source).

        Returns:
            None
        """
        try:
            dest, src = operands
            result = self.register_collection.get(dest) ^ (src if isinstance(src, int) else self.register_collection.get(src))
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' or '{src}' in XOR operation.")
            self.terminal.info_message("TIP: Both operands must be valid registers or an immediate value.")

    @dispatch(list)
    def asm_not(self, operands: list) -> None:
        """
        Executes the NOT instruction, performing a bitwise NOT on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            result = ~self.register_collection.get(dest) & 0xFFFF
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in NOT operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_neg(self, operands: list) -> None:
        """
        Executes the NEG instruction, negating the value of a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            result = -self.register_collection.get(dest) & 0xFFFF
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result, operation='SUB')
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in NEG operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_inc(self, operands: list) -> None:
        """
        Executes the INC instruction, incrementing the value of a register by one.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            result = self.register_collection.get(dest) + 1
            self.register_collection.set(dest, result & 0xFFFF)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in INC operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_dec(self, operands: list) -> None:
        """
        Executes the DEC instruction, decrementing the value of a register by one.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            result = self.register_collection.get(dest) - 1
            self.register_collection.set(dest, result & 0xFFFF)
            self.register_collection.update_flags(result, operation='SUB')
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in DEC operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_shl(self, operands: list) -> None:
        """
        Executes the SHL instruction, performing a bitwise shift left on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
            
        Example:
            [C]=> p mov ax,1
            Register Decimal    Hexadecimal  Binary            
            --------------------------------------------------
            AX       1          0x0001       0000000000000001  
            --------------------------------------------------
            [C]=> p shl ax
            Register Decimal    Hexadecimal  Binary            
            --------------------------------------------------
            AX       2          0x0002       0000000000000010  
            --------------------------------------------------
            [C]=> p shl ax
            Register Decimal    Hexadecimal  Binary            
            --------------------------------------------------
            AX       4          0x0004       0000000000000100  
            --------------------------------------------------            
        """
        try:
            dest = operands[0]
            result = self.register_collection.get(dest) << 1
            self.register_collection.set(dest, result & 0xFFFF)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in SHL operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_shr(self, operands: list) -> None:
        """
        Executes the SHR instruction, performing a bitwise shift right on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            result = self.register_collection.get(dest) >> 1
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in SHR operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_rol(self, operands: list) -> None:
        """
        Executes the ROL instruction, performing a bitwise rotate left on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            value = self.register_collection.get(dest)
            result = ((value << 1) | (value >> 15)) & 0xFFFF
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in ROL operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_ror(self, operands: list) -> None:
        """
        Executes the ROR instruction, performing a bitwise rotate right on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            value = self.register_collection.get(dest)
            result = ((value >> 1) | (value << 15)) & 0xFFFF
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(f"ERROR: Invalid register '{dest}' in ROR operation.")
            self.terminal.info_message("TIP: Ensure the operand is a valid register.")


    def assemble(self, asm_code: str, memory: Memory) -> List[int]:
        """
        Converts assembly code into machine code as a list of byte integers.

        Args:
            asm_code (str): Multiline string of assembly code instructions.

        Returns:
            List[int]: Machine code as an array of integer bytes.
        """
        machine_code = []
        lines = asm_code.strip().splitlines()

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            try:
                # Use parse() to validate and extract the instruction details
                parsed = self.parse(line, memory)
                opcode = parsed['opcode']
                operands = parsed['operands']

                # Generate machine code based on operands
                if len(operands) == 2:
                    dest, src = operands

                    # reg, imm16
                    if src.isdigit() or src.startswith("0X"):
                        op_key = 'reg, imm16'
                        opcode_hex = self.opcode_map[opcode][op_key]
                        opcode_hex = f"{int(opcode_hex, 16) + int(self.register_codes[dest], 2):02X}"
                        imm_value = int(src, 16) if src.startswith("0X") else int(src)
                        imm_hex = f"{imm_value:04X}"
                        machine_code.extend([int(opcode_hex, 16)] + [int(imm_hex[i:i+2], 16) for i in range(0, 4, 2)])

                    # reg, reg
                    elif dest in self.register_codes and src in self.register_codes:
                        op_key = 'reg, reg'
                        opcode_hex = self.opcode_map[opcode][op_key]
                        mod_reg_rm = f"{int(self.register_codes[src] + self.register_codes[dest], 2):02X}"
                        machine_code.extend([int(opcode_hex, 16), int(mod_reg_rm, 16)])

                    else:
                        raise ValueError(f"Unsupported operand format in line {line_num}: '{line}'")

            except (ValueError, KeyError) as e:
                self.terminal.error_message(f"ERROR: {e}")
                continue

        return machine_code

    def execute_and_print(self, instruction: str, memory: Memory) -> None:
        """
        Executes an assembly instruction and shows only the registers that changed.

        Args:
            instruction (str): Assembly instruction as a text string.

        Returns:
            None
        """        # Ejecuta la instrucción y maneja errores
        try:
            self.parse(instruction, memory)
            self.register_collection.print_changed_registers()
        except Exception as e:
            self.terminal.error_message(f"ERROR: Execution failed for instruction '{instruction}'. Details: {e}")

class CpuX8086():
    """
    Class emulating a 8086 CPU.
    """

    def __init__(self) -> None:
        self.instruction_parser = InstructionParser()
        self.instructions_set = self.instruction_parser.supported_instructions
        self.register_set = self.instruction_parser.supported_registers
        self.terminal = Terminal()

    def parse_instruction(self, cmd: str, memory: Memory) -> None:
        """Parse the assembler instructions affecting the registers if necesary.
        

        Parameters:
            cmd {str}: Assembler instruction.


        Returns:
            None.

        """       
        self.instruction_parser.execute_and_print(cmd, memory)

    #  https://www.geeksforgeeks.org/python-program-to-add-two-binary-numbers/
    def _find_matches(self, d: Dict[str, str], item: str):
        """

        Parameters:
            d {str}: Regex Dictionary
            item (str): Item to be look for.

        Returns:
            Dict[str]: Item found, or None if not.

        """
        for k in d:
            if re.match(k, item):
                return d[k]

        return None

    def _16to8(self, hl: int) -> Tuple[int]:
        """Decode a 16-bit number in 2 8-bit numbers

        Parameters:
            hl (int): 16-bit numbers

        Returns:
            int, int: 8-bit higher part and 8-bit lower part, respectively.

        """
        h = int(hl / 256)
        l = h % 256

        return h, l

    @staticmethod
    def _not_yet():
        print("This part of the CPU hasn't been implemented yet. =)")

    @dispatch(int)
    def get_bin(self, x: int) -> str:
        """Convert any integer into n bit binary format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 16 bit binary as string.
        """
        return format(x, '016b')

    @dispatch(int)
    def get_hex(self, x: int) -> str:
        """Convert any integer into 16 bit hexadecimal format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 16 bit hexadecimal as string.
        """

        return format(x, '04X')

    def assemble(self, memory: Memory, code: str) -> str:
        """
        Assemble the code into machine code.

        Args:
            memory (Memory): Memory object class.
            code (str): Code to be assembled.

        Returns:
            str: Machine code.
        """

        machine_code = self.instruction_parser.assemble(code, memory)
        if len(machine_code)>0:
            self.terminal.info_message("Machine code:", machine_code)
            memory.offset_cursor+=len(machine_code)

        return machine_code

    def print_registers(self) -> None:
        """ Print the CPU registers and it's value."""
        self.instruction_parser.register_collection.print_registers()

    def move(self, memory: Memory, from_begin: int, from_end: int, destination: int) -> bool:
        """Copy a memory region to other memory region.

        Parameters:
            memory (Memory): A Memory class object.
            from_begin (int): Source's begin.
            from_end (int): Source's end.
            destination (int): Destination's begin.

        Returns:
            bool: Operation result.
        """

        if destination > from_end:
            for source in range(from_begin, from_end):
                dist_pointer = from_begin \
                    if destination + source == from_begin else destination + source - from_begin
                memory.poke(memory.active_page, dist_pointer,
                            memory.peek(memory.active_page, source))
            self.terminal.success_message(f"{from_end - from_begin} byte/s copied.")
            return True

        self.terminal.error_message("Invalid value.")
        return False

    def fill(self, memory: Memory, start: int, end: int, pattern: str) -> bool:
        """Fill a memory region with a specified pattern.

        Parameters:
            memory (Memory): A Memory class object.
            start (int): Source's begin.
            end (int): Source's end.
            pattern (str): Pattern.

        Returns:
            bool: Operation result. Always true.
        """
        cursor = 0
        for idx in range(start, end):
            memory.poke(memory.active_page, idx, ord(pattern[cursor]))
            cursor += 1
            if cursor > len(pattern) - 1:
                cursor = 0

        return True

    def search(self, memory: Memory, start: int, pattern: str) -> List[str]:
        """Search a pattern in the memory. Staring from <start> to the end of the page.

        Parameters:
            memory (Memory): Memory class object.
            start (int): Starting point from the search.
            pattern (str): Pattern to search for.

        Returns:
            [str]
        """
        found_list = []
        pointer = start
        while pointer < memory._offsets:
            idx = 0

            # Did I find the first char of the pattern? If so, let's search for the rest
            if memory.peek(memory.active_page, pointer) == ord(pattern[idx]):
                pointer_aux = pointer
                while idx < len(pattern) and pointer_aux < memory._offsets and \
                        memory.peek(memory.active_page, pointer_aux) == ord(pattern[idx]):
                    idx += 1
                    pointer_aux += 1

                if pointer_aux - pointer == len(pattern):
                    found_list.append(
                        f"{'%04X' % memory.active_page}:{'%04X' % pointer}")

            pointer += 1

        return found_list

    def load_into(self, memory: Memory, start: int, text: str) -> None:
        """
        Load a text into memory, starting from an address.

        Args:
            memory (Memory): Memory object class.
            start (int): Address memory where to begin.
            text (str): Text to be load into.

        Returns:
            None
        """
        for idx in range(0, len(text) - 1):
            memory.poke(memory.active_page, start + idx, ord(text[idx]))

    def compare(self, memory: Memory, cfrom: int, cend: int, cto: int) -> List[str]:
        """
        Compares two memory regions.

        Args:
            memory (Memory): Memory object class.
            cfrom (int): Source address memory where to start.
            cend (int): Source address memory where to end.
            cto (int): Destination address memory.

        Returns:
            [str]: The differences between regions.
        """
        diffs = []

        for a in range(cfrom, cend):
            org = memory.peek(memory.active_page, a)
            dist_pointer = cfrom if cto + a == cfrom else cto + a - cfrom - 1

            dist = memory.peek(memory.active_page, dist_pointer)
            if org != dist:
                diffs.append('%04X' % memory.active_page + ":" + '%04X' % a + " " +
                             '%02X' % org + " " + '%02X' % dist + " " +
                             '%04X' % memory.active_page + ":" + '%04X' % dist_pointer)

        return diffs

    def cat(self, disk: Disk, addrb: int, addrn: int) -> None:
        """
        Shows the content of the vdisk region.

        Args:
            disk: A Disk class type object.
            addrb: Start address.
            addrn: End address.

        Returns:

        """
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row:  # One single row
            print(f"{'%06X' % (pointer + addrb)} ", end="", flush=True)
            for address in range(addrb, addrn):
                byte = disk.read(pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.success_message(f"{peek} ", end="", flush=True)

            self.terminal.success_message(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else:  # two or more rows
            while pointer + addrb < addrn:
                if pointer % bytes_per_row == 0:
                    self.terminal.success_message(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    self.terminal.success_message(f"{'%06X' % (pointer + addrb)} ", end="", flush=True)

                byte = disk.read(pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.success_message(f"{peek} ", end="", flush=True)
                pointer += 1

        print("")

    def display(self, memory: Memory, addrb: int, addrn: int) -> None:
        """
        Displays a memory region.

        Args:
            memory: A Memory class type object.
            addrb: Start address.
            addrn: End address.

        Returns:
            None.
        """
        page = memory.active_page
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row:  # One single row
            self.terminal.success_message(
                f"{'%04X' % memory.active_page}:{'%04X' % (pointer + addrb)} ", end="", flush=True)
            for address in range(addrb, addrn):
                byte = memory.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.success_message(f"{peek} ", end="", flush=True)

            print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else:  # two or more rows
            while pointer + addrb < addrn:
                if pointer % bytes_per_row == 0:
                    print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    self.terminal.success_message(f"{'%04X' % memory.active_page}:{'%04X' % (pointer + addrb)} ", end="")

                byte = memory.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.success_message(f"{peek} ", end="", flush=True)
                pointer += 1

        print("")

    def write_to_vdisk(self, memory: Memory, disk: Disk, address: int, firstsector: int, number: int) -> None:
        """
        Writes onto vdisk a memory block.

        Args:
            memory (Memory): A Memory type class object.
            disk (Disk): A Disk type class object.
            address (int): Source memory address.
            firstsector (int): Destination sector address.
            number (int): Number of bytes to be copied.

        Returns:
            None.
        """
        for i in range(0, number - 1):
            print("Writing to vdisk...", firstsector + i, memory.peek(address + i))
            disk.write(firstsector+i, memory.peek(address + i))

    def read_from_vdisk(self, memory: Memory, disk: Disk, address: int, firstsector: int, number: int) -> None:
        """
        Loads into memory a vdisk block.

        Args:
            memory (Memory): A Memory type class object.
            disk (Disk): A Disk type class object.
            address (int): Destination memory address.
            firstsector (int): Source sector address.
            number (int): Number of bytes to be copied.

        Returns:
            None.
        """
        for i in range(0, number - 1):
            memory.poke(memory.active_page, address, disk.read(firstsector + i))

