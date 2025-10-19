# tests/test_cli_commands.py
import builtins
import runpy
import types
from pathlib import Path

import pytest


def _find_cli_script(repo_root: Path) -> Path | None:
    """
    Busca un script del CLI en ubicaciones típicas y verifica que sea archivo.
    """
    candidates = [
        repo_root / "pebug.py",
        repo_root / "pebug",
        repo_root / "bin" / "pebug",
        repo_root / "scripts" / "pebug",
        repo_root / "cli" / "pebug.py",
        repo_root / "cli" / "pebug",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def _load_pebug_namespace():
    """
    Carga el CLI ejecutando el script con runpy.run_path para obtener su namespace.
    Si no encuentra script, intenta importar paquete 'pebug'.
    """
    repo_root = Path(__file__).resolve().parents[1]

    # Aseguramos que 'modules' sea importable por los imports relativos del CLI
    import sys
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    script = _find_cli_script(repo_root)
    if script is not None:
        ns_dict = runpy.run_path(str(script))
        return types.SimpleNamespace(**ns_dict)

    # Fallback: intentar importar como paquete (por si el CLI está empaquetado)
    try:
        import pebug as pkg  # type: ignore
        return pkg
    except Exception as e:
        raise RuntimeError("No se encontró el script del CLI (pebug/pebug.py) ni el paquete 'pebug'.") from e


def test_cli_happy_path(monkeypatch, capsys, tmp_path):
    """
    Smoke test del CLI: ejecuta algunos comandos básicos sin crashear.
    No requiere 'pebug' en PATH ni plugins extra.
    """
    pebug_cli = _load_pebug_namespace()

    # Trabajamos en un directorio temporal para no tocar archivos del repo
    monkeypatch.chdir(tmp_path)

    # Secuencia simulando entradas de usuario.
    # Evitamos 'a' (assemble) para no depender de InstructionParser.assemble(...)
    inputs = iter([
        "r",
        "p mov ax, 1",
        "p add ax, 1",
        "d 0000 0010",
        "f 0000 0004 ABCD",
        "d 0000 0004",
        "q",
    ])

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            return "q"

    monkeypatch.setattr(builtins, "input", fake_input)

    # Ejecutar el CLI
    term = pebug_cli.Terminal()
    pebug_cli.pebug_main(term)

    out = capsys.readouterr().out

    # Asserts suaves; validan que los comandos corrieron sin crashear
    assert "Type 'q' to quit the program" in out
    assert "Register" in out              # por 'r' o impresión de regs
    assert ":" in out                     # por 'd' que imprime direcciones 0000:XXXX
