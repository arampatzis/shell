import re
import logging
from dataclasses import dataclass
from pathlib import Path

from ..base import Installer
from ..messages import message as msg
from ..messages import color

logger = logging.getLogger(__name__)

LOCAL_CONFIG = Path.home() / ".config" / "git" / "local"
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(kw_only=True)
class GitIdentityInstaller(Installer):
    """Creates ~/.config/git/local with [user] name and email if absent."""

    check_path: str = str(LOCAL_CONFIG)

    def _install(self) -> bool:
        if self.dry_run:
            msg.custom(f"    Would create {LOCAL_CONFIG}", color.yellow)
            return True

        msg.custom(
            f"    {LOCAL_CONFIG} not found — setting up git identity.", color.cyan
        )

        name = input("    Full name  : ").strip()
        if not name:
            msg.custom("    Skipped (no name provided).", color.yellow)
            return True

        while True:
            email = input("    Email      : ").strip()
            if not email:
                msg.custom("    Skipped (no email provided).", color.yellow)
                return True
            if EMAIL_RE.match(email):
                break
            msg.custom("    Invalid email, try again.", color.red)

        LOCAL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_CONFIG.write_text(f"[user]\n\tname = {name}\n\temail = {email}\n")
        LOCAL_CONFIG.chmod(0o600)
        msg.custom(f"    Written: {LOCAL_CONFIG}", color.green)
        return True
