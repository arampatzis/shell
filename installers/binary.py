"""Binary installer for pre-built binaries from GitHub releases."""

import re
import shutil
import subprocess
import tempfile
import socket
import logging
from pathlib import Path
from dataclasses import dataclass

from .messages import message as msg
from .messages import color
from .base import Installer
from .tools import execute_cmd


logger = logging.getLogger(__name__)


def authenticate_github_cli(gh_binary: Path) -> bool:
    """Authenticate GitHub CLI with user token."""
    msg_lines = [
        ("\n    Setting up GitHub CLI authentication...", color.cyan),
        ("    You'll need a GitHub Personal Access Token (PAT)", color.yellow),
        ("    To create one:", color.yellow),
        ("    1. Go to https://github.com/settings/tokens", color.yellow),
        ("    2. Click 'Generate new token (classic)'", color.yellow),
        (
            "    3. Select scopes: repo, workflow, admin:org, admin:public_key",
            color.yellow,
        ),
        ("    4. Copy the generated token", color.yellow),
        ("    Paste your GitHub Personal Access Token below:", color.cyan),
    ]

    for line, col in msg_lines:
        msg.custom(line, col)

    token = input("    Token [leave blank to skip]: ")

    if not token.strip():
        msg.custom(
            (
                "    No token provided. GitHub CLI authentication skipped.\n"
                "    You can set it later with 'gh auth login'"
            ),
            color.yellow,
        )
        return True

    # Authenticate with token
    msg.custom("    Authenticating with GitHub...", color.cyan)

    try:
        result = execute_cmd(
            [
                str(gh_binary),
                "auth",
                "login",
                "--hostname",
                "github.com",
                "--with-token",
            ],
            input=token,
            message="GitHub CLI authentication started",
        )

        if not result.success:
            return False

        msg.custom("    GitHub CLI authenticated successfully!", color.green)

        return True

    except KeyboardInterrupt:
        msg.custom("\n    Authentication cancelled by user.", color.yellow)
        return True

    except Exception as e:
        msg.custom(f"    Unexpected error during authentication: {e}", color.red)
        logger.error(f"Unexpected authentication error: {e}")
        return False


def setup_github_ssh_key(gh_binary: Path) -> bool:
    """Create and upload SSH key to GitHub."""

    msg.custom("\n    Setting up SSH key for GitHub...", color.cyan)

    try:
        # Get email from user with validation
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        while True:
            email = input(
                "    Enter your email for SSH key [leave blank to skip]: "
            ).strip()

            if not email:
                msg.custom(
                    (
                        "    No email provided. SSH key setup skipped.\n"
                        "    You can set it later with 'gh ssh-key add'"
                    ),
                    color.yellow,
                )
                return True

            if email_pattern.match(email):
                break
            else:
                msg.custom(
                    "    Invalid email format. Please enter a valid email address.",
                    color.red,
                )

        # Create .ssh directory if it doesn't exist
        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(mode=0o700, exist_ok=True)

        # Generate SSH key
        msg.custom("    Generating SSH key...", color.cyan)
        ssh_key_path = ssh_dir / "github"

        # Check if key already exists
        if ssh_key_path.exists() or (ssh_key_path.with_suffix(".pub")).exists():
            msg.custom("    SSH key 'github' already exists.", color.yellow)
            overwrite = (
                input("    Do you want to overwrite it? [y/N]: ").strip().lower()
            )
            if overwrite not in ["y", "yes"]:
                msg.custom("    SSH key generation skipped.", color.yellow)
                return True

        # Remove existing keys
        if ssh_key_path.exists():
            ssh_key_path.unlink()
        if (ssh_key_path.with_suffix(".pub")).exists():
            (ssh_key_path.with_suffix(".pub")).unlink()
        msg.custom("    Existing SSH keys removed.", color.cyan)
        result = execute_cmd(
            [
                "ssh-keygen",
                "-t",
                "ed25519",
                "-C",
                email,
                "-f",
                str(ssh_key_path),
                "-N",
                "",  # No passphrase
            ],
            message="SSH key generation started",
        )
        if not result.success:
            msg.error("    SSH key generation failed!")
            return False
        msg.custom("    SSH key generated successfully!", color.green)

        # Get IP address for key title

        result = execute_cmd(
            ["hostname", "-I"],
            message="Getting IP address\n",
        )
        if not result.success or result.result is None:
            msg.error("    Failed to get IP address!")
            hostname = socket.gethostname()
        else:
            hostname = result.result.stdout.strip().split()[0]  # Get first IP address

        # Upload SSH key to GitHub
        msg.custom(f"    Uploading SSH key to GitHub as '{hostname}'...", color.cyan)

        result = execute_cmd(
            [
                str(gh_binary),
                "ssh-key",
                "add",
                str(ssh_key_path) + ".pub",
                "--title",
                hostname,
            ],
            message="SSH key upload started",
        )

        msg.custom("    SSH key uploaded to GitHub successfully!", color.green)

        # Configure SSH config for GitHub
        return configure_ssh_config()

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
        msg.custom(f"    SSH key setup failed: {error_msg}", color.red)
        logger.error(f"SSH key setup failed: {error_msg}")
        return False
    except KeyboardInterrupt:
        msg.custom("\n    SSH key setup cancelled by user.", color.yellow)
        return True
    except Exception as e:
        msg.custom(f"    Unexpected error during SSH key setup: {e}", color.red)
        logger.error(f"Unexpected SSH key setup error: {e}")
        return False


def configure_ssh_config() -> bool:
    """Configure SSH config file for GitHub."""
    try:
        ssh_config_path = Path.home() / ".ssh" / "config"
        github_config = """Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github
    IdentitiesOnly yes
"""

        # Check if config already exists and contains GitHub config
        if ssh_config_path.exists():
            with open(ssh_config_path) as f:
                content = f.read()

            if "Host github.com" in content:
                msg.custom(
                    (
                        "    'github' already exists in ~/.ssh/config\n"
                        "    Skipping configuration."
                    ),
                    color.yellow,
                )
                return True

        # Add GitHub config to SSH config file
        msg.custom("    Configuring SSH config for GitHub...", color.cyan)

        with open(ssh_config_path, "a") as f:
            f.write(f"\n{github_config}")

        # Set proper permissions
        ssh_config_path.chmod(0o600)

        msg.custom("    SSH config configured for GitHub!", color.green)
        return True

    except Exception as e:
        msg.custom(f"    Failed to configure SSH config: {e}", color.red)
        logger.error(f"SSH config setup failed: {e}")
        return False


@dataclass(kw_only=True)
class BinaryInstaller(Installer):
    """Handles installation of pre-built binaries."""

    binary_name: str = ""
    version: str = ""
    archive_pattern: str = ""

    def __post_init__(self):
        """Post-init setup."""
        print(self.installation_path)
        if not self.installation_path:
            self.installation_path = Path.home() / "local/bin"
        else:
            self.installation_path = Path(self.installation_path).expanduser()

        self.check_cmd = self.binary_name
        self.required_deps.extend(["wget", "tar"])

        super().__post_init__()

    def _install(self) -> bool:
        """Install the binary from archive_pattern."""
        try:
            url = self.archive_pattern.format(version=self.version)
        except ValueError as e:
            msg.error(f"    Invalid archive pattern:\n    {e}")
            return False

        msg.custom(
            f"    Installing {self.binary_name} from releases:\n    {url}", color.orange
        )

        if self.dry_run:
            display_path = str(self.installation_path).replace(str(Path.home()), "~")

            msg.custom(
                f"    Would download and install {self.binary_name} to {display_path}",
                color.cyan,
            )
            return True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            msg.custom(f"    Downloading {self.name} binary...", color.cyan)

            result = execute_cmd(
                ["wget", "-q", "-O", str(temp_path / f"{self.name}.tar.gz"), url],
                cwd=temp_path,
                message=(f"{self.name} download started"),
            )

            if not result.success:
                return False

            result = execute_cmd(
                ["tar", "-xzf", f"{self.name}.tar.gz"],
                cwd=temp_path,
                message=f"{self.name} extraction started",
            )

            if not result.success:
                return False

            # Find and copy binary
            display_path = str(self.installation_path).replace(str(Path.home()), "~")
            msg.custom(f"    Copying {self.name} to {display_path}...", color.cyan)
            success = self._find_and_copy_binary(
                temp_path,
                Path(self.installation_path).expanduser(),
            )
            if not success:
                return False

        # Handle GitHub CLI authentication if binary is "gh"
        if self.binary_name == "gh":
            target_binary = Path(self.installation_path) / self.binary_name
            success = authenticate_github_cli(target_binary)
            if success:
                return setup_github_ssh_key(target_binary)
            return success

        return success

    def _find_and_copy_binary(
        self,
        temp_path: Path,
        target_dir: Path,
    ) -> bool:
        """Find the binary in extracted files and copy to target directory."""
        binary_path = None
        for item in temp_path.rglob(self.binary_name):
            if item.is_file() and item.stat().st_mode & 0o111:  # Check if executable
                binary_path = item
                break

        if not binary_path:
            raise FileNotFoundError(
                f"{self.binary_name} binary not found in downloaded archive"
            )

        target_binary = target_dir / self.binary_name
        shutil.copy2(binary_path, target_binary)
        target_binary.chmod(0o755)

        display_path = str(self.installation_path).replace(str(Path.home()), "~")
        msg.custom(
            f"    {self.name} installed successfully to {display_path}", color.green
        )

        return True
