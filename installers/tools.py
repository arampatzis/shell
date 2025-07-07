from pathlib import Path
import subprocess
import re

from .messages import message as msg

def execute_cmd(
        cmd: list[str],
        message: str = "",
        log_file: Path | str = "",
        **kwargs
    ) -> tuple[bool, subprocess.CompletedProcess | None]:
        """Execute a command and print output. Print stdout and stderr if it fails."""
        
        if not log_file:
            log_file = Path("install.log")
        
        if any(key in kwargs for key in ['capture_output', 'text', 'check']):
            raise ValueError("capture_output should not be in kwargs")
        
        with open(log_file, 'a') as lf:
            lf.write("\n==============================================\n")
            lf.write(f"{message}\n")
            lf.write(f"Executing command:\n{cmd}\n")
            lf.flush()
        
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    **kwargs
                )
                
                lf.write("STDOUT:\n")
                lf.write(result.stdout)
                lf.write("STDERR:\n")
                lf.write(result.stderr)
                lf.write("\n==============================================\n")
                lf.flush()
                
                return True, result

            except subprocess.CalledProcessError as e:
                lf.write("STDOUT:\n")
                lf.write(e.stdout)
                lf.write("STDERR:\n")
                lf.write(e.stderr)
                lf.write("\n==============================================\n")
                lf.flush()
                
                msg.error("    Command failed with message:")
                if e.stdout:
                    s = re.sub(r'^\s*', '    ', e.stdout)
                    s = re.sub(r'\n\s*', '\n    ', s)
                    msg.error(s)
                if e.stderr:
                    s = re.sub(r'^\s*', '    ', e.stderr)
                    s = re.sub(r'\n\s*', '\n    ', s)
                    msg.error(s)
                
                return False, None
            
            except Exception as e:
                raise e
