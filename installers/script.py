"""Script installer for tools that use git repositories with installer scripts."""

import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

from messages import message as msg
from messages import color
from .base import Installer


@dataclass(kw_only=True)
class ScriptInstaller(Installer):
    """Handles installation from git repositories with installer scripts."""

    script_type: str = ""
    repo_url: str = ""
    target_dir: str = ""
    installer_script: str = ""
    installer_args: list = field(default_factory=list)
    script_url: str = ""
    required_deps: list[str] = field(default_factory=lambda: ['git'])
    
    def _install(self) -> bool:
        """
        Install a tool using script-based installation.
        """
        if self.dry_run:
            if self.script_type == 'git_clone':
                msg.custom(f"Installing {self.name} from git repository", color.cyan)
                msg.custom(
                    f"    Would clone {self.repo_url} to {self.target_dir}",
                    color.cyan
                )
                msg.custom(
                    f"    Would run installer script: {self.installer_script}",
                    color.cyan
                )
            elif self.script_type == 'direct_script':
                msg.custom(f"Installing {self.name} from script", color.cyan)
                msg.custom(
                    f"    Would download and run script from: {self.script_url}",
                    color.cyan
                )
            return True
        
        if self.script_type == 'git_clone':
            return self._install_git_clone_script()
        elif self.script_type == 'direct_script':
            return self._install_direct_script()
        else:
            raise ValueError(f"Unknown script_type: {self.script_type}")
    
    def _install_git_clone_script(self) -> bool:
        """Install using git clone + installer script pattern."""
        msg.custom(f"Installing {self.name} from git repository", color.cyan)
        
        # Determine installation directory
        install_dir = Path(self.target_dir)
        
        try:
            # Clone repository
            msg.custom(f"   Cloning {self.name} repository...", color.cyan)
            with open('install.log', 'a') as log_file:
                log_file.write(
                    f"\n=== {self.name} git clone started at {datetime.now()} ===\n"
                )
                
                result = subprocess.run(
                    [
                        'git',
                        'clone',
                        '--depth',
                        '1',
                        self.repo_url,
                        str(install_dir)
                    ],
                    stdout=log_file,
                    stderr=log_file
                )
                
                # Check if clone was successful by verifying the directory exists
                if not install_dir.exists() or not (install_dir / '.git').exists():
                    raise subprocess.CalledProcessError(
                        result.returncode, 
                        f"git clone failed with return code {result.returncode}"
                    )
            
            # Run installer script
            msg.custom(f"   Running {self.name} installer...", color.cyan)
            installer_path = install_dir / self.installer_script
            
            if not installer_path.exists():
                raise FileNotFoundError(f"Installer script not found: {installer_path}")
            
            # Prepare installer command
            install_cmd = ['bash', str(installer_path)]
            if self.installer_args:
                install_cmd.extend(self.installer_args)
            
            with open('install.log', 'a') as log_file:
                log_file.write(f"\n=== {self.name} installer started ===\n")
                log_file.write(f"Command: {' '.join(install_cmd)}\n")
                
                subprocess.run(
                    install_cmd,
                    check=True,
                    stdout=log_file,
                    stderr=log_file
                )
            
            msg.custom(f"   {self.name} installed successfully", color.green)
            msg.custom("   Detailed logs written to install.log", color.yellow)
            
            with open('install.log', 'a') as log_file:
                log_file.write(
                    f"\n=== {self.name} installation completed successfully "
                    f"at {datetime.now()} ===\n"
                )
            
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
            msg.custom(f"   {self.name} installation failed: {error_msg}", color.red)
            with open('install.log', 'a') as log_file:
                log_file.write(f"{self.name} installation failed: {error_msg}\n")
            return False
        except Exception as e:
            return self._handle_error(e)
    
    def _install_direct_script(self) -> bool:
        """Install using direct script download and execution."""
        msg.custom(f"Installing {self.name} from script", color.cyan)
        
        try:
            # Inform the user
            msg.custom(
                f"   Downloading and running {self.name} installer...",
                color.cyan
            )

            # Correct install command: download script and pipe to bash
            install_cmd = ['bash', '-c', f'wget -qO - {self.script_url} | bash']

            with open('install.log', 'a') as log_file:
                log_file.write(
                    f"\n=== {self.name} direct script installation "
                    f"started at {datetime.now()} ===\n"
                )
                log_file.write(f"Script URL: {self.script_url}\n")

                # Run and capture output
                result = subprocess.run(
                    install_cmd,
                    capture_output=True,
                    text=True
                )

                log_file.write(result.stdout)
                log_file.write(result.stderr)

                if result.returncode != 0:
                    log_file.write(
                        "\n=== ERROR: Command failed with return code "
                        f"{result.returncode} ===\n"
                    )
                    raise subprocess.CalledProcessError(
                        result.returncode, install_cmd, result.stdout, result.stderr
                    )

            msg.custom(f"   {self.name} installed successfully", color.green)
            msg.custom("   Detailed logs written to install.log", color.yellow)

            with open('install.log', 'a') as log_file:
                log_file.write(
                    f"\n=== {self.name} installation completed successfully "
                    f"at {datetime.now()} ===\n"
                )

            return True

        except subprocess.CalledProcessError as e:
            return self._handle_error(e)
        except Exception as e:
            return self._handle_error(e)
