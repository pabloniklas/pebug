from enum import Enum

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

class Terminal:
    """Class for styled terminal messages."""

    # ANSI color codes
    def __init__(self, default_color='white'):
        """
        Initialize the Terminal class with a default color.
        
        Args:
            default_color (str): Default color for messages. Defaults to 'white'.
        """
        
        self.default_color = AnsiColors.WHITE.value

    def _format_message(self, message, color='white', bold=False):
        """
        Format a message with the specified style.

        Args:
            message (str): The message content.
            color (str): Color of the message. Defaults to 'white'.
            bold (bool): Whether the message should be bold. Defaults to False.

        Returns:
            str: Formatted message.
        """
        color_code = AnsiColors.BRIGHT_WHITE.value if color == self.default_color else color
        style_code = AnsiColors.BOLD.value if bold else ''
        
        return f"{color_code}{style_code}{message}{AnsiColors.RESET.value}"

    def success_message(self, message, end="\n", flush=False):
        """
        Generate a success message in green.

        Args:
            message (str): The success message to display.
            end (str): String appended after the last value. Defaults to a newline.
            flush (bool): Whether to forcibly flush the stream.

        """
        print(self._format_message(message, color='green', bold=True), end=end, flush=flush)

    def error_message(self, message, end="\n", flush=False):
        """
        Generate an error message in red.

        Args:
            message (str): The error message to display.
            end (str): String appended after the last value. Defaults to a newline.
            flush (bool): Whether to forcibly flush the stream.

        """
        print(self._format_message(message, color='red', bold=True), end=end, flush=flush)

    def info_message(self, message, end="\n", flush=False):
        """
        Generate an informational message in cyan.

        Args:
            message (str): The informational message to display.
            end (str): String appended after the last value. Defaults to a newline.
            flush (bool): Whether to forcibly flush the stream.

        """
        print(self._format_message(message, color='cyan'), end=end, flush=flush)

    def warning_message(self, message, end="\n", flush=False):
        """
        Generate a warning message in yellow.

        Args:
            message (str): The warning message to display.
            end (str): String appended after the last value. Defaults to a newline.
            flush (bool): Whether to forcibly flush the stream.

        """
        print(self._format_message(message, color='yellow', bold=True), end=end, flush=flush)

    def common_message(self, message, color='white', bold=False, end="\n", flush=False):
        """
        Generate a customizable message with any specified color and optional bold styling.

        Args:
            message (str): The message to display.
            color (str): Color of the message. Defaults to 'white'.
            bold (bool): Whether the message should be bold. Defaults to False.
            end (str): String appended after the last value. Defaults to a newline.
            flush (bool): Whether to forcibly flush the stream.

        """
        print(self._format_message(message, color=color, bold=bold), end=end, flush=flush)
