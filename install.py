#! /usr/bin/env python3

from pathlib import Path
import random
import string
import requests
import subprocess

class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def make_link(source, target):
  source = Path(source).expanduser()
  target = Path(target).resolve()

  print(f'\n    Source: {source}')
  print(f'    Target: {target}')
  
  if source.exists():
    print(f'{bc.WARNING}    Source file exists.')
    rnd = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    source_bak = backup_folder / Path(source.stem + '.' + rnd)
    print(f'    Backup Source to {source_bak}{bc.ENDC}')
    source.rename(source_bak)
  elif source.is_symlink():
    print(f'{bc.WARNING}    Source is an empty symbolic link and it will be removed. {bc.ENDC}')
    source.unlink()
  
  print(f'{bc.OKBLUE}    Linking Source to Target.{bc.ENDC}')
  source.symlink_to(target)



backup_folder = Path('.install.bak')
backup_folder.mkdir(exist_ok=True)

print('1. vimrc')
make_link(source='~/.vimrc',
          target='vim/vimrc')

print('\n2. oh my bash')
ohmybash_path = Path('~/.oh-my-bash/').expanduser()
if not ohmybash_path.is_dir():
    print(f'{bc.WARNING}    oh-my-bash not found in system and it will be installed.{bc.ENDC}')
    res = requests.get('https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh')
    subprocess.run(['bash','-c', res.content])
else:
    print(f'{bc.WARNING}    oh-my-bash is found in the system.{bc.ENDC}')

make_link(source='~/.oh-my-bash/custom',
          target='oh-my-bash/custom')


  
print('\n3. bashrc')
make_link(source='~/.bashrc',
          target='oh-my-bash/bashrc')



print(f'{bc.OKCYAN}\nBackup files are stored in folder {backup_folder}{bc.ENDC}\n')
