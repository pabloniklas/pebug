import pytest
from modules.CpuX8086 import CpuX8086

# Mapa de registros usado por el pseudo-encoder propuesto
REG = {'AX':0,'CX':1,'DX':2,'BX':3,'SP':4,'BP':5,'SI':6,'DI':7}

def _get_assemble_line(ip):
    """
    Devuelve una función assemble_line(line: str) -> list[int].
    Si no existe ip.assemble_line, usa _encode_pseudo_bytes como fallback.
    """
    if hasattr(ip, "assemble_line"):
        return ip.assemble_line

    if hasattr(ip, "_encode_pseudo_bytes"):
        def wrapper(line: str):
            line = line.strip()
            if not line or line.endswith(":"):
                return []
            parts = line.split(None, 1)
            op = parts[0].upper()
            ops = [p.strip() for p in parts[1].split(",")] if len(parts) > 1 else []
            res = ip._encode_pseudo_bytes(op, ops)
            if res is None:
                raise ValueError(f"Unsupported or unencodable: {line}")
            return res
        return wrapper

    pytest.skip("No hay assemble_line ni _encode_pseudo_bytes en InstructionParser")

@pytest.fixture
def ip():
    cpu = CpuX8086()
    return cpu.instruction_parser

def test_mov_reg_imm(ip):
    assemble_line = _get_assemble_line(ip)
    got = assemble_line("MOV AX, 0x1234")
    exp = [0xB8 + REG['AX'], 0x34, 0x12]
    assert got == exp

def test_mov_reg_reg(ip):
    assemble_line = _get_assemble_line(ip)
    got = assemble_line("MOV BX, AX")
    exp = [0x8B, 0xC0 | (REG['BX'] << 3) | REG['AX']]
    assert got == exp

def test_add_reg_imm(ip):
    assemble_line = _get_assemble_line(ip)
    got = assemble_line("ADD AX, 1")
    exp = [0x70, REG['AX'], 0x01, 0x00]  # base 0x70 en pseudo-encoding
    assert got == exp

def test_add_reg_reg(ip):
    assemble_line = _get_assemble_line(ip)
    got = assemble_line("ADD BX, AX")
    exp = [0x10, 0xC0 | (REG['BX'] << 3) | REG['AX']]
    assert got == exp

def test_int_21(ip):
    assemble_line = _get_assemble_line(ip)
    got = assemble_line("INT 0x21")
    assert got == [0xCD, 0x21]

@pytest.mark.parametrize("line", [
    "  ", "LABEL:", "\tLABEL2:\t"
])
def test_lines_sin_bytes(ip, line):
    assemble_line = _get_assemble_line(ip)
    assert assemble_line(line) == []

def test_bytes_son_uint8(ip):
    assemble_line = _get_assemble_line(ip)
    seqs = [
        assemble_line("MOV AX, 0x0001"),
        assemble_line("ADD AX, 0x00FF"),
        assemble_line("MOV BX, AX"),
        assemble_line("INT 0x21"),
    ]
    for seq in seqs:
        for b in seq:
            assert isinstance(b, int)
            assert 0 <= b <= 255

def test_instruccion_no_soportada(ip):
    assemble_line = _get_assemble_line(ip)
    with pytest.raises(ValueError):
        assemble_line("NOP")
