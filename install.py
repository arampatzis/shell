#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : install.py
# Author            : George Arampatzis <garampat@ethz.ch>
# Date              : 15.12.2021
# Last Modified Date: 15.12.2021
# Last Modified By  : George Arampatzis <garampat@ethz.ch>

from pathlib import Path
from messages import *
import subprocess
import random
import string
import sys

def make_link(source, target):
    source = Path(source).expanduser()
    target = Path(target).resolve()

    print(f'    Source: {source}')
    print(f'    Target: {target}')
  
    if source.exists():
        message.warning('    Warning: Source file exists.')
        rnd = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        source_bak = backup_folder / Path(source.stem + '.' + rnd)
        message.warning(f'    Warning: Backup Source to {source_bak}')
        source.rename(source_bak)
    elif source.is_symlink():
        message.warning(f'    Warning: Source is an empty symbolic link and it will be removed.')
        source.unlink()
  
    message.custom(f'    Linking Source to Target', color.blue)
    source.symlink_to(target)


backup_folder = Path('.install.bak')
backup_folder.mkdir(exist_ok=True)

home = Path('~').expanduser()

print('\n* oh-my-bash and .bashrc')
ohmybash_path = home / Path('.oh-my-bash/')
if not ohmybash_path.is_dir():
    message.error(f'    Error: oh-my-bash is not installed in the system. Installl oh-my-bash and rerun:')
    message.error(f'    Error: bash -c "$(wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh -O -)"')
    sys.exit(0)
else:
    message.warning(f'    Warning: oh-my-bash is found in the system.')

make_link(source='~/.bashrc',
          target='oh-my-bash/bashrc')

make_link(source='~/.oh-my-bash/custom',
          target='oh-my-bash/custom')

print('\n* dotfiles')
for f in Path('dotfiles').glob('.*'):
    print(f'\n  * {f}')
    make_link(source=home/f.name,
                target=f)

print('\n* .config')
for f in Path('config').glob('*/'):
    print(f'\n  * {f}')
    make_link(source='~/.config',
            target='config')

print('\n* fzf')
print('   * Clone fzf into ~/.fzf')
destination = home / Path('.fzf')
if Path.is_dir(destination):
    message.warning('   Warning: .fzf already exists in home directory.')
else:
    message.inseparator('Start git clone', n=60, sep='-', clr=color.orange)
    subprocess.call(['git', 'clone', '--depth', '1', 'https://github.com/junegunn/fzf.git', str(destination)])
    message.inseparator('End git clone', n=60, sep='-', clr=color.orange)

    print('\n   * Install fzf: \n')
    destination = home / Path('.fzf/install')
    
    message.inseparator('Start fzf installer (external script)', n=60, sep='-', clr=color.orange)
    subprocess.call(['bash', destination, '--no-zsh', '--no-fish'])
    message.inseparator('End fzf installer', n=60, sep='-', clr=color.orange)

message.custom(f'\nBackup files are stored in folder {backup_folder}\n', color.cyan)
