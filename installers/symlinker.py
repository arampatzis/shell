"""Symlinker installer for handling file and directory symlink operations."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
import logging

from .messages import message as msg
from .messages import color
from .base import Installer

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class SymlinkerInstaller(Installer):
    """Handles file and directory symlinking operations."""

    source: str = ""
    target: str = ""
    expand: bool = False
    backup_dir: Path = field(default_factory=lambda: Path(".install.bak"))
    operations_log: list = field(default_factory=list)
    required_deps: list[str] = field(default_factory=list)  # No external dependencies

    def __post_init__(self):
        """Initialize backup directory after dataclass initialization."""
        # Always ensure backup directory exists (both dry-run and real)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize component name for safe use in filenames."""
        # Replace unsafe characters with underscores
        return re.sub(r"[^\w\-.]", "_", name)

    def _is_broken_symlink(self, path: Path) -> bool:
        """Check if a path is a broken symlink."""
        try:
            return path.is_symlink() and not path.exists()
        except (OSError, RuntimeError):
            return False

    def _install(self) -> bool:
        """Install files using symlinking."""
        source_path = Path(self.source)
        target_path = Path(self.target).expanduser()

        if not source_path.exists():
            msg.error(f"    Source directory {source_path} not found")
            return False

        # Handle expand pattern - contents of source go into target
        if self.expand:
            success = True
            for item in source_path.iterdir():
                target = target_path / item.name
                if not self.create_symlink(item, target):
                    success = False
            return success
        # Handle direct mapping - source to target
        else:
            return self.create_symlink(source_path, target_path)

    def backup_file(
        self,
        system_path: Path,
        source_path: Path | None = None,
        source_root: Path | None = None,
    ) -> Path | None:
        """
        Create backup of existing file/directory, dereferencing symlinks and
        preserving dotfiles/ structure.
        """
        if not system_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        backup_timestamp_dir = self.backup_dir / timestamp
        backup_timestamp_dir.mkdir(parents=True, exist_ok=True)

        # Use source_path to determine backup structure
        if source_path is not None:
            if source_root is None:
                source_root = Path(self.source).expanduser().resolve()
            try:
                rel_path = source_path.expanduser().resolve().relative_to(source_root)
            except ValueError:
                rel_path = source_path.name
        else:
            rel_path = system_path.name
        backup_path = backup_timestamp_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            msg.warning(f"    Would backup {system_path.name} to {backup_path}")
            logger.info(f"[DRY RUN] Would backup {system_path} to {backup_path}")
            return backup_path

        try:
            # If system_path is a symlink, dereference and copy the real
            # file/folder recursively
            if system_path.is_symlink():
                real_path = system_path.resolve()
                if real_path.is_dir():
                    shutil.copytree(real_path, backup_path, symlinks=False)
                    logger.info(
                        f"Backed up dereferenced directory {real_path} to {backup_path}"
                    )
                else:
                    shutil.copy2(real_path, backup_path)
                    logger.info(
                        f"Backed up dereferenced file {real_path} to {backup_path}"
                    )
            elif system_path.is_dir():
                shutil.copytree(system_path, backup_path, symlinks=False)
                logger.info(f"Backed up directory {system_path} to {backup_path}")
            else:
                shutil.copy2(system_path, backup_path)
                logger.info(f"Backed up file {system_path} to {backup_path}")

            msg.warning(f"    Backed up {system_path.name} to {backup_path}")
            return backup_path
        except OSError as e:
            msg.error(f"    Failed to backup {system_path.name}: {e}")
            logger.error(f"Failed to backup {system_path}: {e}")
            return None

    def create_symlink(self, source: Path, target: Path) -> bool:
        """Create symbolic link with proper error handling."""
        source = source.expanduser().resolve()
        target_expanded = target.expanduser()

        source_root = Path(self.source).expanduser().resolve().parent

        logger.info(f"Creating symlink: {target_expanded} -> {source}")

        target_display = str(target_expanded).replace(str(Path.home()), "~")
        source_display = str(source).replace(str(Path.home()), "~")

        if self.dry_run:
            msg.custom(f"\n    {target_display} -> {source_display}", color.yellow)
            return True
        else:
            msg.custom(f"\n    {target_display} -> {source_display}", color.yellow)

        # Remove existing file/symlink
        if target_expanded.exists() or target_expanded.is_symlink():
            # Check if existing symlink is broken
            if self._is_broken_symlink(target_expanded):
                msg.warning(
                    f"    Found broken symlink {target_expanded.name}, "
                    "removing without backup\n"
                )
                logger.info(
                    f"Found broken symlink {target_expanded}, removing without backup"
                )
                target_expanded.unlink()
            else:
                # Check if existing symlink already points to our source
                should_backup = True
                if target_expanded.is_symlink():
                    try:
                        existing_target = target_expanded.readlink().resolve()
                        if existing_target == source:
                            should_backup = False
                            msg.warning(
                                f"    Symlink {target_expanded.name} "
                                "already points to source, skipping backup\n"
                            )
                            logger.info(
                                f"Symlink {target_expanded} already points to {source}, "
                                "skipping backup"
                            )
                    except (OSError, RuntimeError):
                        should_backup = True

                if should_backup:
                    backup_path = self.backup_file(
                        target_expanded, source_path=source, source_root=source_root
                    )
                    if backup_path:
                        self.operations_log.append(
                            {
                                "action": "backup",
                                "original": str(target_expanded),
                                "backup": str(backup_path),
                            }
                        )
                    else:
                        msg.error(
                            f"    Cannot proceed: backup of {target_expanded.name} failed"
                        )
                        return False

                # Only remove original after successful backup (or no backup needed)
                if target_expanded.is_symlink():
                    target_expanded.unlink()
                elif target_expanded.is_dir():
                    shutil.rmtree(target_expanded)
                else:
                    target_expanded.unlink()

        # Create parent directory if needed (resolve parent path to avoid issues)
        parent_dir = target_expanded.parent.resolve()
        parent_dir.mkdir(parents=True, exist_ok=True)

        try:
            target_expanded.symlink_to(source)
            self.operations_log.append(
                {
                    "action": "symlink",
                    "source": str(source),
                    "target": str(target_expanded),
                }
            )
            return True
        except OSError as e:
            msg.error(f"    Failed to create symlink {target_expanded.name}: {e}")
            logger.error(f"Failed to create symlink {target_expanded} -> {source}: {e}")
            return False

    def install_dotfiles_from_dir(
        self, source_dir: Path, description: str = "files"
    ) -> bool:
        """Install dotfiles from a source directory."""
        if not source_dir.exists():
            msg.error(f"{description} directory {source_dir} not found")
            logger.error(f"{description} directory {source_dir} not found")
            return False

        msg.custom(f"Installing {description}", color.cyan)

        success = True
        for dotfile in source_dir.glob(".*"):
            if dotfile.is_file():
                target = Path.home() / dotfile.name
                if not self.create_symlink(dotfile, target):
                    success = False

        return success

    def install_config_from_dir(
        self, source_dir: Path, description: str = "config files"
    ) -> bool:
        """Install config files from a source directory to ~/.config."""
        if not source_dir.exists():
            msg.error(f"{description} directory {source_dir} not found")
            logger.error(f"{description} directory {source_dir} not found")
            return False

        msg.custom(f"Installing {description}", color.cyan)

        config_dir = Path.home() / ".config"
        success = True

        for item in source_dir.iterdir():
            target = config_dir / item.name
            if not self.create_symlink(item, target):
                success = False

        return success
