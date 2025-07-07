"""Script installer for tools that use git repositories with installer scripts."""

from dataclasses import dataclass, field

from .messages import message as msg
from .messages import color
from .base import Installer
from .tools import install_from_url


@dataclass(kw_only=True)
class ScriptInstaller(Installer):
    """Handles installation from git repositories with installer scripts."""

    target_dir: str = ""
    installer_script: str = ""
    installer_args: list = field(default_factory=list)
    script_url: str = ""

    def _install(self) -> bool:
        """
        Install a tool using script-based installation.
        """
        msg.custom(
            f"    Installing {self.name} from script:\n    {self.script_url}",
            color.orange,
        )

        msg.custom(f"    Downloading and running {self.name} installer...", color.cyan)

        result = install_from_url(
            self.script_url,
            message=f"Starting {self.name} installation",
        )
        return result.success
