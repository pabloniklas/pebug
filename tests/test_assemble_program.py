import pytest
from modules.CpuX8086 import CpuX8086

REG = {'AX':0,'CX':1,'DX':2,'BX':3,'SP':4,'BP':5,'SI':6,'DI':7}

def _get_assemble_line(ip):
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

def test_assemble_program_flatten(ip):
    if not hasattr(ip, "assemble_program"):
        pytest.skip("assemble_program no implementado; solo probamos assemble_line")
    prog = [
        "START:",
        "MOV AX, 0x0003",   # B8 03 00
        "ADD AX, 5",        # 70 00 05 00
        "MOV BX, AX",       # 8B C3
        "INT 0x21",         # CD 21
    ]
    blob = ip.assemble_program(prog, base_addr=0x0100)
    # Admitimos que devuelva bytes, bytearray o list[int]
    if isinstance(blob, (bytes, bytearray)):
        got = list(blob)
    elif isinstance(blob, list):
        got = blob
    elif isinstance(blob, tuple):
        # Por si devuelve (base_addr, bytes)
        _, seq = blob
        got = list(seq) if not isinstance(seq, list) else seq
    else:
        raise AssertionError(f"Tipo inesperado de retorno: {type(blob)}")

    exp = []
    exp += [0xB8 + 0, 0x03, 0x00]
    exp += [0x70, 0, 0x05, 0x00]
    exp += [0x8B, 0xC0 | (3 << 3) | 0]
    exp += [0xCD, 0x21]
    assert got == exp

def test_labels_ignoran_bytes(ip):
    assemble_line = _get_assemble_line(ip)
    parts = [
        assemble_line("L1:"),
        assemble_line("MOV AX, 1"),
        assemble_line("L2:"),
        assemble_line("MOV AX, 2"),
    ]
    flat = [b for part in parts for b in part]
    # MOV AX,1 -> 3 bytes ; MOV AX,2 -> 3 bytes
    assert flat == [0xB8, 0x01, 0x00, 0xB8, 0x02, 0x00]
