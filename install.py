#! /usr/bin/env python3

from pathlib import Path
import subprocess
import random
import string
import sys

bc = {'HEADER': '\033[95m',
      'BLUE': '\033[94m',
      'CYAN': '\033[96m',
      'GREEN': '\033[92m',
      'WARNING': '\033[93m',
      'FAIL': '\033[91m',
      'ENDC': '\033[0m',
      'BOLD': '\033[1m',
      'UNDERLINE': '\033[4m'}

def error_msg(msg):
  print(bc['FAIL'] + msg + bc['ENDC'])
  
def warning_msg(msg):
  print(bc['WARNING'] + msg + bc['ENDC'])

def success_msg(msg, color='GREEN'):
  print(bc[color] + msg + bc['ENDC'])

def make_link(source, target):
  source = Path(source).expanduser()
  target = Path(target).resolve()

  print(f'    Source: {source}')
  print(f'    Target: {target}')
  
  if source.exists():
    warning_msg('    Source file exists.')
    rnd = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    source_bak = backup_folder / Path(source.stem + '.' + rnd)
    warning_msg(f'    Backup Source to {source_bak}')
    source.rename(source_bak)
  elif source.is_symlink():
    warning_msg(f'    Source is an empty symbolic link and it will be removed.')
    source.unlink()
  
  success_msg(f'    Linking Source to Target','BLUE')
  source.symlink_to(target)


backup_folder = Path('.install.bak')
backup_folder.mkdir(exist_ok=True)

home = Path('~').expanduser()

print('\n* oh-my-bash and .bashrc')
ohmybash_path = home / Path('.oh-my-bash/')
if not ohmybash_path.is_dir():
  error_msg(f'    oh-my-bash is not installed in the system. Installl oh-my-bash and rerun:')
  error_msg(f'    bash -c "$(wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh -O -)"')
  sys.exit(0)
else:
  warning_msg(f'    oh-my-bash is found in the system.')

make_link(source='~/.bashrc',
          target='oh-my-bash/bashrc')

make_link(source='~/.oh-my-bash/custom',
          target='oh-my-bash/custom')

print('\n* dotfiles')
pathlist = Path('dotfiles').glob('.*')
for file in pathlist:
  print(f'\n  * {file}')
  src = home/ file.name
  trg = file
  make_link(source=src,
           target=trg)

print('\n* .config')
make_link(source='~/.config',
           target='config')

print('\n* fzf')
print('   * Clone fzf into ~/.fzf')
destination = home / Path('.fzf')
if Path.is_dir(destination):
    warning_msg('   .fzf already exists in home directory.')
else:
    subprocess.call(['git', 'clone', '--depth', '1', 'https://github.com/junegunn/fzf.git', str(destination)])

print('\n   * Install fzf: \n')
destination = home / Path('.fzf/install')
subprocess .call(['bash', destination, '--no-zsh', '--no-fish'])


success_msg(f'\nBackup files are stored in folder {backup_folder}\n', 'CYAN')
