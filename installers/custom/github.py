import logging
from pathlib import Path
import re
import socket

from ..messages import message as msg
from ..messages import color
from ..tools import Executor


logger = logging.getLogger(__name__)


def get_short_hostname():
    """Get the short hostname of the machine."""
    return socket.gethostname().split(".")[0]


def get_ip_address():
    """Get the IP address of the machine."""
    # This reliably gets the main non-loopback IP address,
    # even on multi-interface systems.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable; just used to determine the default interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


short_hostname = get_short_hostname()
ip = get_ip_address()


class GitHubSSHSetup:
    def __init__(self, gh_binary: Path):
        self.gh_binary = gh_binary

    def authenticate_cli(self) -> bool:
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

        msg.custom("    Authenticating with GitHub...", color.cyan)

        try:
            result = Executor().execute_cmd(
                [
                    str(self.gh_binary),
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

    def get_email_for_key(self) -> str:
        """Prompt the user for email and validate."""
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
                return ""
            if email_pattern.match(email):
                return email
            msg.custom(
                "    Invalid email format. Please enter a valid email address.",
                color.red,
            )

    def generate_ssh_key(self, ssh_key_path: Path, email: str) -> bool:
        """Generate a new SSH key, possibly overwriting the existing one."""
        # If key exists, ask about overwrite
        if ssh_key_path.exists() or ssh_key_path.with_suffix(".pub").exists():
            msg.custom("    SSH key 'github' already exists.", color.yellow)
            overwrite = (
                input("    Do you want to overwrite it? [y/N]: ").strip().lower()
            )
            if overwrite not in ["y", "yes"]:
                msg.custom("    SSH key generation skipped.", color.yellow)
                return False
            if ssh_key_path.exists():
                ssh_key_path.unlink()
            if ssh_key_path.with_suffix(".pub").exists():
                ssh_key_path.with_suffix(".pub").unlink()
            msg.custom("    Existing SSH keys removed.", color.cyan)

        result = Executor().execute_cmd(
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
        return True

    def get_github_key_id_by_title(self, title: str) -> list[str]:
        result = Executor().execute_cmd(
            [
                str(self.gh_binary),
                "ssh-key",
                "list",
            ],
            message="Checking existing SSH keys on GitHub",
        )
        if not result.success or result.result is None:
            return []

        key_ids = []
        for line in result.result.stdout.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                key_title, key_id = parts[0], parts[4]
                if key_title == title:
                    key_ids.append(key_id)
        return key_ids

    def delete_github_key(self, key_id: str) -> bool:
        """Delete the GitHub SSH key with the given ID."""
        result = Executor().execute_cmd(
            [
                str(self.gh_binary),
                "ssh-key",
                "delete",
                key_id,
                "--yes",
            ],
            message=f"Deleting SSH key id={key_id} from GitHub",
        )
        if result.success:
            msg.custom(
                f"    Deleted existing SSH key id={key_id} from GitHub.",
                color.green,
            )
            return True
        else:
            msg.error(f"    Failed to delete SSH key id={key_id} from GitHub.")
            return False

    def upload_ssh_key_to_github(self, pubkey_path: Path, title: str) -> bool:
        """Upload a public SSH key to GitHub with a given title."""
        result = Executor().execute_cmd(
            [
                str(self.gh_binary),
                "ssh-key",
                "add",
                str(pubkey_path),
                "--title",
                title,
            ],
            message="SSH key upload started",
        )
        if result.success:
            msg.custom("    SSH key uploaded to GitHub successfully!", color.green)
            return True
        msg.error("    SSH key upload to GitHub failed!")
        return False

    def configure_ssh_config(self) -> bool:
        try:
            ssh_config_path = Path.home() / ".ssh" / "config"
            github_config = """Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github
    IdentitiesOnly yes
"""
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
            msg.custom("    Configuring SSH config for GitHub...", color.cyan)
            with open(ssh_config_path, "a") as f:
                f.write(f"\n{github_config}")
            ssh_config_path.chmod(0o600)
            msg.custom("    SSH config configured for GitHub!", color.green)
            return True
        except Exception as e:
            msg.custom(f"    Failed to configure SSH config: {e}", color.red)
            logger.error(f"SSH config setup failed: {e}")
            return False

    def setup_ssh_key(self) -> bool:
        msg.custom("\n    Setting up SSH key for GitHub...", color.cyan)
        email = self.get_email_for_key()
        if not email:
            return True

        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
        ssh_key_path = ssh_dir / "github"

        if not self.generate_ssh_key(ssh_key_path, email):
            return False

        hostname = f"{get_short_hostname()}-{get_ip_address()}"
        existing_ids = self.get_github_key_id_by_title(hostname)

        if existing_ids:
            msg.custom(
                f"    SSH key with title '{hostname}' already exists on GitHub"
                f" {len(existing_ids)} times!",
                color.yellow,
            )

            overwrite = (
                input("    Do you want to overwrite it? [y/N]: ").strip().lower()
            )

            if overwrite in ["y", "yes"]:
                for key in existing_ids:
                    if not self.delete_github_key(key):
                        return False
            else:
                msg.custom("    SSH key upload skipped.", color.yellow)
                return True

        if not self.upload_ssh_key_to_github(
            ssh_key_path.with_suffix(".pub"),
            hostname,
        ):
            return False

        return self.configure_ssh_config()
