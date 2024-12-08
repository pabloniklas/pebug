class Terminal:
    """Class for styled terminal messages."""

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    COLORS = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'magenta': '\033[35m',
    }

    def __init__(self, default_color='white'):
        """
        Initialize the Terminal class with a default color.
        
        Args:
            default_color (str): Default color for messages. Defaults to 'white'.
        """
        self.default_color = self.COLORS.get(default_color.lower(), self.COLORS['white'])

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
        color_code = self.COLORS.get(color.lower(), self.default_color)
        style_code = self.BOLD if bold else ''
        return f"{color_code}{style_code}{message}{self.RESET}"

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
