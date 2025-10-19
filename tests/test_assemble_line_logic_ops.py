# tests/test_assemble_line_logic_ops.py
import pytest
from modules.CpuX8086 import InstructionParser

# Mapa de índices de registro (debe coincidir con InstructionParser.register_codes)
REG = {'AX': 0, 'CX': 1, 'DX': 2, 'BX': 3, 'SP': 4, 'BP': 5, 'SI': 6, 'DI': 7}

# Bases de pseudo-encoding educativo
BASES = {
    'AND': {'imm': 0x72, 'rr': 0x12},
    'OR': {'imm': 0x73, 'rr': 0x13},
    'XOR': {'imm': 0x74, 'rr': 0x14},
}


@pytest.fixture
def ip():
    return InstructionParser()


def _get_assemble_line(ip):
    assert hasattr(
        ip, "assemble_line"), "InstructionParser.assemble_line no existe"
    return ip.assemble_line


@pytest.mark.parametrize("mnemonic,dst,imm", [
    ("AND", "AX", 0x0001),
    ("OR",  "CX", 0x00FF),
    ("XOR", "DX", 0xF00D),
    ("AND", "BX", 0x1234),
    ("OR",  "DI", 0xABCD),
    ("XOR", "BP", 0x8000),
])
def test_logic_reg_imm(ip, mnemonic, dst, imm):
    assemble_line = _get_assemble_line(ip)
    got = assemble_line(f"{mnemonic} {dst}, 0x{imm:04X}")

    base_imm = BASES[mnemonic]['imm']
    exp = [base_imm & 0xFF, REG[dst] & 0xFF, imm & 0xFF, (imm >> 8) & 0xFF]
    assert got == exp


@pytest.mark.parametrize("mnemonic,dst,src", [
    ("AND", "BX", "AX"),
    ("OR",  "DI", "SI"),
    ("XOR", "BP", "SP"),
    ("AND", "AX", "CX"),
    ("OR",  "CX", "DX"),
    ("XOR", "DX", "BX"),
])
def test_logic_reg_reg(ip, mnemonic, dst, src):
    assemble_line = _get_assemble_line(ip)
    got = assemble_line(f"{mnemonic} {dst}, {src}")

    base_rr = BASES[mnemonic]['rr']
    modrm = 0xC0 | (REG[dst] << 3) | REG[src]
    exp = [base_rr & 0xFF, modrm & 0xFF]
    assert got == exp
