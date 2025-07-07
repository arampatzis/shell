"""
Colored message printing utilities for terminal output.

This module provides colored console output functionality with ANSI escape codes.
"""


class color:
    """ANSI color codes for terminal output."""

    # Standard colors
    black: str = "\033[30m"
    red: str = "\033[31m"
    green: str = "\033[32m"
    orange: str = "\033[33m"
    blue: str = "\033[34m"
    purple: str = "\033[35m"
    cyan: str = "\033[36m"
    white: str = "\033[37m"

    # Light colors
    lightred: str = "\033[91m"
    lightgreen: str = "\033[92m"
    yellow: str = "\033[93m"
    lightblue: str = "\033[94m"
    pink: str = "\033[95m"
    lightcyan: str = "\033[96m"

    # Formatting
    reset: str = "\033[0m"
    bold: str = "\033[1m"
    underline: str = "\033[4m"


class message:
    """Utility class for printing colored messages to the terminal."""

    @classmethod
    def error(cls, msg: str) -> None:
        """Print an error message in red."""
        print(color.lightred + msg + color.reset)

    @classmethod
    def warning(cls, msg: str) -> None:
        """Print a warning message in yellow."""
        print(color.yellow + msg + color.reset)

    @classmethod
    def success(cls, msg: str) -> None:
        """Print a success message in green."""
        print(color.green + msg + color.reset)

    @classmethod
    def custom(cls, s: str, clr: str = color.white) -> None:
        """Print a custom message with specified color."""
        print(clr + s + color.reset)

    @classmethod
    def separator(cls, n: int = 20, sep: str = "-", clr: str = color.white) -> None:
        """Print a separator line."""
        print(clr + n * sep + color.reset)

    @classmethod
    def inseparator(
        cls, s: str, n: int = 20, sep: str = "-", clr: str = color.white
    ) -> None:
        """Print text surrounded by separator lines."""
        print(clr + n * sep)
        print(s)
        print(n * sep + color.reset)


if __name__ == "__main__":
    message.error("error message")
    message.warning("warning message")
    message.success("success message")
    message.separator()
    message.custom("custom message")
    message.custom("custom message", color.red)
    message.custom("custom message", color.green)
    message.custom("custom message", color.orange)
    message.custom("custom message", color.blue)
    message.custom("custom message", color.purple)
    message.custom("custom message", color.cyan)
    message.custom("custom message", color.white)
    message.custom("custom message", color.lightred)
    message.custom("custom message", color.lightgreen)
    message.custom("custom message", color.yellow)
    message.custom("custom message", color.lightblue)
    message.custom("custom message", color.pink)
    message.custom("custom message", color.lightcyan)
