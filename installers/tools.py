from dataclasses import dataclass
from pathlib import Path
import subprocess
import logging
import tempfile
from textwrap import indent

from .messages import message as msg

logger = logging.getLogger(__name__)


@dataclass
class FailedCommand:
    cmd: list[str] | str
    stdout: str
    stderr: str


@dataclass
class CommandResult:
    success: bool
    result: subprocess.CompletedProcess | FailedCommand | None


class Executor:
    def __init__(self):
        pass

    def execute_cmd(
        self, cmd: list[str] | str, message: str = "", **kwargs
    ) -> CommandResult:
        """Execute a command and print output. Print stdout and stderr if it fails."""

        if any(key in kwargs for key in ["capture_output", "text", "check"]):
            raise ValueError("capture_output should not be in kwargs")

        logger.info("==============================================")
        if message:
            logger.info(message)
        logger.info(f"Executing command: {cmd}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, **kwargs
            )

            if result.stdout:
                logger.info("STDOUT:\n%s", result.stdout)
            if result.stderr:
                logger.info("STDERR:\n%s", result.stderr)
            logger.info("==============================================")

            return CommandResult(True, result)

        except subprocess.CalledProcessError as e:
            if e.stdout:
                logger.info("STDOUT:\n%s", e.stdout)
            if e.stderr:
                logger.info("STDERR:\n%s", e.stderr)
            logger.info("==============================================")

            msg.error("    Command failed with message:")
            if e.stdout:
                msg.error(indent(e.stdout.strip(), "    "))
            if e.stderr:
                msg.error(indent(e.stderr.strip(), "    "))

            return CommandResult(False, FailedCommand(cmd, e.stdout, e.stderr))

    def install_from_url(
        self,
        url: str,
        message: str = "Installing from remote script...",
    ) -> CommandResult:
        """Download script to a temp file then execute it — avoids shell=True."""
        with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
            tmp = Path(f.name)
        try:
            result = self.execute_cmd(["wget", "-qO", str(tmp), url], message=message)
            if not result.success:
                return result
            tmp.chmod(0o700)
            return self.execute_cmd(["bash", str(tmp)], message=message)
        finally:
            tmp.unlink(missing_ok=True)
