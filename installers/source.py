"""Source installer for tools that need to be built from source code."""

import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

from .messages import message as msg
from .messages import color
from .base import Installer


@dataclass(kw_only=True)
class SourceInstaller(Installer):
    """Handles installation from source code."""
    
    version: str = ""
    archive_pattern: str = ""
    binary_name: str = ""
    build_deps: list = field(default_factory=list)
    configure_args: list = field(default_factory=list)
    run_autogen: bool = False
    
    def __post_init__(self):
        """Post-init setup."""
        
        if not self.installation_path:
            self.installation_path = Path.home() / "local/"
        else:
            self.installation_path = Path(self.installation_path).expanduser()
            
        self.check_cmd = self.binary_name
        self.required_deps.extend(['wget', 'tar'])
        
        super().__post_init__()
    
    def _install(self) -> bool:
        """Install a tool from source code."""
        try:
            url = self.archive_pattern.format(version=self.version)
        except ValueError as e:
            msg.error(f"    Invalid archive pattern:\n    {e}")
            return False
        
        msg.custom(
            f"    Installing {self.binary_name} from source:\n    {url}",
            color.orange
        )
        
        if self.dry_run:
            display_path = str(self.installation_path).replace(str(Path.home()), "~")
            msg.custom(
                (
                    "    Would configure, build, and install "
                    f"{self.binary_name} to {display_path}"
                ),
                color.cyan
            )
            return True
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                msg.custom(f"    Downloading {self.name} source...", color.cyan)
                
                with open('install.log', 'a') as log_file:
                    log_file.write(
                        f"\n=== {self.name} download started at {datetime.now()} ===\n"
                    )
                    
                    subprocess.run(
                        [
                            'wget',
                            '-q',
                            '-O',
                            str(temp_path / f'{self.name}.tar.gz'),
                            url
                        ],
                        check=True,
                        cwd=temp_path,
                        stdout=log_file,
                        stderr=log_file
                    )
                    
                    log_file.write(f"\n=== {self.name} source extraction started ===\n")
                    subprocess.run(
                        [
                            'tar',
                            '-xzf',
                            f'{self.name}.tar.gz'
                        ],
                        check=True,
                        cwd=temp_path,
                        stdout=log_file,
                        stderr=log_file
                    )
                
                # Find extracted source directory
                extracted_dirs = [
                    d for d in temp_path.iterdir() 
                    if d.is_dir() and d.name.startswith(self.name)
                ]
                if not extracted_dirs:
                    raise RuntimeError(
                        f"Could not find extracted {self.name} source directory"
                    )
                
                source_dir = extracted_dirs[0]
                
                # Run autogen.sh if needed
                if self.run_autogen:
                    msg.custom(f"    Running autogen.sh for {self.name}...", color.cyan)
                    with open(self.log_file, 'a') as log_file:
                        log_file.write(f"\n=== {self.name} autogen.sh started ===\n")
                        subprocess.run(
                            [
                                './autogen.sh'
                            ],
                            check=True,
                            cwd=source_dir,
                            stdout=log_file,
                            stderr=log_file
                        )
                
                # Configure
                msg.custom(f"    Configuring {self.name}...", color.cyan)
                configure_cmd = [
                    './configure',
                    f'--prefix={self.installation_path}'
                ]
                if self.configure_args:
                    configure_cmd.extend(self.configure_args)
                
                with open(self.log_file, 'a') as log_file:
                    log_file.write(f"\n=== {self.name} configure started ===\n")
                    log_file.write(f"Command: {' '.join(configure_cmd)}\n")
                    
                    subprocess.run(
                        configure_cmd,
                        check=True,
                        cwd=source_dir,
                        stdout=log_file,
                        stderr=log_file
                    )
                
                # Build
                msg.custom(f"    Building {self.name}...", color.cyan)
                with open(self.log_file, 'a') as log_file:
                    log_file.write(f"\n=== {self.name} build started ===\n")
                    subprocess.run(
                        [
                            'make'
                        ],
                        check=True,
                        cwd=source_dir,
                        stdout=log_file,
                        stderr=log_file
                    )
                
                # Install
                display_path = str(self.installation_path)
                display_path = display_path.replace(str(Path.home()), "~")
                
                msg.custom(
                    f"    Installing {self.name} to {display_path}...",
                    color.cyan
                )
                with open(self.log_file, 'a') as log_file:
                    log_file.write(f"\n=== {self.name} install started ===\n")
                    subprocess.run(
                        [
                            'make',
                            'install'
                        ],
                        check=True,
                        cwd=source_dir,
                        stdout=log_file,
                        stderr=log_file
                    )
                return True
                
            except subprocess.CalledProcessError as e:
                return self._handle_error(e)
            except Exception as e:
                return self._handle_error(e) 