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
    
    repo: str = ""
    version: str = ""
    archive_pattern: str = ""
    binary_name: str = ""
    build_deps: list = field(default_factory=list)
    configure_args: list = field(default_factory=list)
    run_autogen: bool = False
    required_deps: list[str] = field(default_factory=lambda: ['wget', 'tar', 'make', 'gcc'])
    
    def _install(self) -> bool:
        """Install a tool from source code."""
        # Check build dependencies
        if self.build_deps:
            missing = [dep for dep in self.build_deps if not shutil.which(dep)]
            if missing:
                msg.error(f"Missing build dependencies for {self.name}: {', '.join(missing)}")
                self.logger.error(f"Missing {self.name} build dependencies: {', '.join(missing)}")
                return False
        
        if self.dry_run:
            msg.custom(f"Installing {self.name} from source", color.cyan)
            version_no_v = self.version.lstrip('v')
            download_url = self.archive_pattern.format(
                repo=self.repo, version=self.version, version_no_v=version_no_v
            )
            msg.custom(f"    Would download source from: {download_url}", color.cyan)
            target_display = str(self.installation_path).replace(str(Path.home()), "~")
            msg.custom(f"    Would configure, build and install to {target_display}", color.cyan)
            return True
        
        msg.custom(f"Installing {self.name} from source", color.cyan)
        
        # Create local installation directory
        self.installation_path.mkdir(parents=True, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Download source
                msg.custom(f"   Downloading {self.name} source...", color.cyan)
                version_no_v = self.version.lstrip('v')  # Remove 'v' prefix if present
                download_url = self.archive_pattern.format(
                    repo=self.repo, version=self.version, version_no_v=version_no_v
                )
                
                # Determine archive format from URL
                if '.tar.bz2' in download_url:
                    archive_name = f'{self.name}.tar.bz2'
                    tar_flags = '-xjf'
                else:
                    archive_name = f'{self.name}.tar.gz'
                    tar_flags = '-xzf'
                
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} source download started at {datetime.now()} ===\n")
                    
                    subprocess.run([
                        'wget', '-q', '-O', str(temp_path / archive_name),
                        download_url
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                    
                    log_file.write(f"\n=== {self.name} source extraction started ===\n")
                    subprocess.run([
                        'tar', tar_flags, archive_name
                    ], check=True, cwd=temp_path, stdout=log_file, stderr=log_file)
                
                # Find extracted source directory
                extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and d.name.startswith(self.name)]
                if not extracted_dirs:
                    raise RuntimeError(f"Could not find extracted {self.name} source directory")
                
                source_dir = extracted_dirs[0]
                
                # Run autogen.sh if needed
                if self.run_autogen:
                    msg.custom(f"   Running autogen.sh for {self.name}...", color.cyan)
                    with open('install.log', 'a') as log_file:
                        log_file.write(f"\n=== {self.name} autogen.sh started ===\n")
                        
                        subprocess.run(['./autogen.sh'], check=True, cwd=source_dir, stdout=log_file, stderr=log_file)
                
                # Configure
                msg.custom(f"   Configuring {self.name}...", color.cyan)
                configure_cmd = ['./configure', f'--prefix={self.installation_path}']
                if self.configure_args:
                    configure_cmd.extend(self.configure_args)
                
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} configure started ===\n")
                    log_file.write(f"Command: {' '.join(configure_cmd)}\n")
                    
                    subprocess.run(configure_cmd, check=True, cwd=source_dir, stdout=log_file, stderr=log_file)
                
                # Build
                msg.custom(f"   Building {self.name}...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} build started ===\n")
                    
                    subprocess.run(['make'], check=True, cwd=source_dir, stdout=log_file, stderr=log_file)
                
                # Install
                target_display = str(self.installation_path).replace(str(Path.home()), "~")
                msg.custom(f"   Installing {self.name} to {target_display}...", color.cyan)
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} install started ===\n")
                    
                    subprocess.run(['make', 'install'], check=True, cwd=source_dir, stdout=log_file, stderr=log_file)
                
                msg.custom(f"   {self.name} installed successfully to {target_display}", color.green)
                msg.custom("   Detailed logs written to install.log", color.yellow)
                
                with open('install.log', 'a') as log_file:
                    log_file.write(f"\n=== {self.name} installation completed successfully at {datetime.now()} ===\n")
                
                return True
                
            except subprocess.CalledProcessError as e:
                return self._handle_error(e)
            except Exception as e:
                return self._handle_error(e) 