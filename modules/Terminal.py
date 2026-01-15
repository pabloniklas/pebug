from enum import Enum
# modules/Terminal.py
import re
from enum import Enum
from typing import Optional

_ANSI_SGR_RE = re.compile(r"\x1b\[(?P<params>[0-9;]*)m")

# Foreground WWIV pipe colors (00-15) según WWIV docs.
# 00 Black, 01 Blue, 02 Green, 03 Cyan, 04 Red, 05 Magenta, 06 Brown,
# 07 Gray, 08 Dark Gray, 09 Bright Blue, 10 Bright Green, 11 Bright Cyan,
# 12 Bright Red, 13 Bright Magenta, 14 Yellow, 15 White. :contentReference[oaicite:2]{index=2}
_FG_ANSI_30_37_TO_WWIV = {
    30: 0,  # black
    31: 4,  # red
    32: 2,  # green
    33: 6,  # brown (ANSI "yellow" normal suele mapear a brown)
    34: 1,  # blue
    35: 5,  # magenta
    36: 3,  # cyan
    37: 7,  # gray/white (normal)
}

_FG_ANSI_90_97_TO_WWIV = {
    90: 8,   # bright black => dark gray
    91: 12,  # bright red
    92: 10,  # bright green
    93: 14,  # bright yellow
    94: 9,   # bright blue
    95: 13,  # bright magenta
    96: 11,  # bright cyan
    97: 15,  # white
}

_BG_ANSI_40_47_TO_WWIV = {
    40: 16,  # black bg
    41: 20,  # red bg
    42: 18,  # green bg
    43: 22,  # brown bg
    44: 17,  # blue bg
    45: 21,  # magenta bg
    46: 19,  # cyan bg
    47: 23,  # gray bg
}


def strip_ansi(text: str) -> str:
    return _ANSI_SGR_RE.sub("", text)


def ansi_to_wwiv(text: str, reset_code: str = "|07") -> str:
    """
    Convierte ANSI SGR (ESC[...m) a WWIV pipe codes |NN.

    - Reset (0) => reset_code (por defecto |07 = Gray)
    - Soporta fg 30-37/90-97 y bg 40-47.
    - Si viene "1" (bold), lo tratamos como 'bright' si hay fg 30-37.
    """
    def _convert_match(m: re.Match) -> str:
        raw = m.group("params")
        if raw == "" or raw is None:
            params = [0]
        else:
            try:
                params = [int(p) for p in raw.split(";") if p != ""]
            except ValueError:
                return ""  # si algo raro, eliminamos

        if not params:
            params = [0]

        # Estado local para este SGR
        is_bright = False
        out_codes = []

        for p in params:
            if p == 0:
                out_codes.append(reset_code)
            elif p == 1:
                is_bright = True
            elif p in _FG_ANSI_30_37_TO_WWIV:
                ww = _FG_ANSI_30_37_TO_WWIV[p]
                # si venía "bold", elevamos a bright equivalente cuando aplique
                if is_bright:
                    # Mapeo “bright” aproximado para 30-37:
                    bright_map = {0: 8, 1: 9, 2: 10,
                                  3: 11, 4: 12, 5: 13, 6: 14, 7: 15}
                    ww = bright_map.get(ww, ww)
                out_codes.append(f"|{ww:02d}")
            elif p in _FG_ANSI_90_97_TO_WWIV:
                ww = _FG_ANSI_90_97_TO_WWIV[p]
                out_codes.append(f"|{ww:02d}")
            elif p in _BG_ANSI_40_47_TO_WWIV:
                ww = _BG_ANSI_40_47_TO_WWIV[p]
                out_codes.append(f"|{ww:02d}")
            else:
                # otros SGR (underline, etc.) -> ignorar por ahora
                pass

        return "".join(out_codes)

    return _ANSI_SGR_RE.sub(_convert_match, text)


class AnsiColors(Enum):
    """
    AnsiColors Enum for managing ANSI escape codes for terminal styling.

    This class provides an organized way to use ANSI escape codes for adding
    colors and styles to terminal output. The escape codes can be used to 
    set foreground colors, styles (like bold), and reset the formatting.

    Attributes:
        RESET: Resets all formatting to the default.
        BOLD: Makes the text bold.
        BLACK: Sets the text color to black.
        RED: Sets the text color to red.
        GREEN: Sets the text color to green.
        YELLOW: Sets the text color to yellow.
        BLUE: Sets the text color to blue.
        MAGENTA: Sets the text color to magenta.
        CYAN: Sets the text color to cyan.
        WHITE: Sets the text color to white.
        BRIGHT_BLACK: Sets the text color to bright black (gray).
        BRIGHT_RED: Sets the text color to bright red.
        BRIGHT_GREEN: Sets the text color to bright green.
        BRIGHT_YELLOW: Sets the text color to bright yellow.
        BRIGHT_BLUE: Sets the text color to bright blue.
        BRIGHT_MAGENTA: Sets the text color to bright magenta.
        BRIGHT_CYAN: Sets the text color to bright cyan.
        BRIGHT_WHITE: Sets the text color to bright white.

    Usage:
        To apply a color, use the `value` property of the Enum member. For example:

            print(f"{AnsiColors.BRIGHT_GREEN.value}This text is bright green!{AnsiColors.RESET.value}")

    Note:
        Ensure your terminal supports ANSI escape codes to see the styling correctly.
        Most modern terminals (Linux, macOS, and many on Windows) support ANSI codes.

    """
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"
    BRIGHT_BLACK = "\033[1;30m"
    BRIGHT_RED = "\033[1;31m"
    BRIGHT_GREEN = "\033[1;32m"
    BRIGHT_YELLOW = "\033[1;33m"
    BRIGHT_BLUE = "\033[1;34m"
    BRIGHT_MAGENTA = "\033[1;35m"
    BRIGHT_CYAN = "\033[1;36m"
    BRIGHT_WHITE = "\033[1;37m"

    # CRT Terminal Colors,
    # based on https://superuser.com/questions/361297/what-colour-is-the-dark-green-on-old-fashioned-green-screen-computer-displays/1206781#1206781
    P1_AMBAR = "#FFB000"
    P1_LIGHT_AMBAR = "#FFCC00"
    P1_GREEN = "#33FF00"
    P1_WHITE = "#282828"


class TerminalIcons(Enum):
    """Icons used in the terminal interface."""
    ERROR: str = "‼️ "
    INFO: str = "ℹ️ "
    SUCCESS: str = "✅ "
    WARNING: str = "⚠️ "


class Terminal:
    """Class for styled terminal messages."""

    def __init__(self, default_color: str = 'white', color_mode: str = "ansi"):
        """
        Initialize the Terminal class with a default color and color mode.
        Args:
            default_color (str): Default color for messages. Defaults to 'white'.
            color_mode (str): 'ansi' (default), 'wwiv', or 'none'.
        """
        # mantenemos tu lógica: default_color se guarda como ANSI code WHITE
        self.default_color = AnsiColors.WHITE.value
        self.color_mode = ColorMode(color_mode)

    def set_color_mode(self, mode: str):
        """Switch output mode: 'ansi', 'wwiv', 'none'."""
        self.color_mode = ColorMode(mode)

    def _format_message(self, message, color='white', bold=False):
        """
        Format a message with the specified style (ANSI SGR).
        """
        color_code = (
            AnsiColors.BRIGHT_WHITE.value
            if color == self.default_color
            else AnsiColors[color.upper()].value
        )
        style_code = AnsiColors.BOLD.value if bold else ''
        return f"{color_code}{style_code}{message}{AnsiColors.RESET.value}"

    def _render(self, text: str) -> str:
        """Apply final output transformation depending on color_mode."""
        if self.color_mode == ColorMode.ANSI:
            return text
        if self.color_mode == ColorMode.WWIV:
            return ansi_to_wwiv(text)
        # NONE: strip ANSI
        return strip_ansi(text)

    def _print(self, text: str, end="\n", flush=False):
        print(self._render(text), end=end, flush=flush)

    def default_message(self, message, end="\n", flush=False):
        self._print(self._format_message(message), end=end, flush=flush)

    def success_message(self, message, end="\n", flush=False):
        self._print(
            self._format_message(
                f"{TerminalIcons.SUCCESS.value} {message}", color='green', bold=True),
            end=end,
            flush=flush,
        )

    def error_message(self, message, end="\n", flush=False):
        self._print(
            self._format_message(
                f"{TerminalIcons.ERROR.value} {message}", color='red', bold=True),
            end=end,
            flush=flush,
        )

    def info_message(self, message, end="\n", flush=False):
        self._print(
            self._format_message(
                f"{TerminalIcons.INFO.value} {message}", color='cyan'),
            end=end,
            flush=flush,
        )

    def warning_message(self, message, end="\n", flush=False):
        self._print(
            self._format_message(
                f"{TerminalIcons.WARNING.value} {message}", color='yellow', bold=True),
            end=end,
            flush=flush,
        )

    def common_message(self, message, color='white', bold=False, end="\n", flush=False):
        self._print(
            self._format_message(message, color=color, bold=bold),
            end=end,
            flush=flush,
        )


class ColorMode(Enum):
    ANSI = "ansi"
    WWIV = "wwiv"
    NONE = "none"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value