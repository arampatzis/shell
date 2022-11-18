#! /usr/bin/env python3

from pathlib import Path
from datetime import datetime
from messages import message as msg
from messages import color
import subprocess
import sys


def backup_folder():
    bf = Path('.install.bak')
    bf.mkdir(exist_ok=True)
    return bf


def home():
    return Path('~').expanduser()


def make_link(source, target):
    source = Path(source).expanduser()
    target = Path(target).resolve()

    print(f'    Source: {source}')
    print(f'    Target: {target}')

    if source.exists():
        msg.warning('    Warning: Source file exists.')
        ext = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        source_bak = backup_folder() / Path(source.stem + '.' + ext)
        msg.warning(f'    Warning: Backup Source to {source_bak}')
        source.rename(source_bak)

    elif source.is_symlink():
        msg.warning(
            '    Warning: Source is an empty symbolic link and it will be removed.'
        )
        source.unlink()

    msg.custom(f'    Linking Source to Target', color.blue)
    source.symlink_to(target)


def install_oh_my_bash():
    omb_install_script = (
        'https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh'
    )

    print('\n* oh-my-bash and .bashrc')

    destination = home() / '.oh-my-bash/'

    if not destination.is_dir():
        msg.error(
            '    Error: oh-my-bash is not installed in the system. '
            'Installl oh-my-bash and rerun:\n'
            f'Error: bash -c "$(wget {omb_install_script} -O -)"'
        )
        sys.exit(0)

    else:
        msg.warning(f'    Warning: oh-my-bash is found in the system.')

    make_link(
        source='~/.bashrc',
        target='oh-my-bash/bashrc'
    )

    make_link(
        source=destination / 'custom',
        target='oh-my-bash/custom'
    )


def link_all(source, targets):

    for f in targets:
        print(f'\n  * {f}')
        make_link(
            source=source / f.name,
            target=f
        )


def install_dot_files():
    print('\n* dotfiles')

    source = home()
    targets = Path('dotfiles').glob('.*')

    link_all(source, targets)


def install_config_folder():
    print('\n* .config')

    source = home() / Path('.config')
    targets = Path('config').glob('*/')

    source.mkdir(exist_ok=True)

    link_all(source, targets)


def install_vim_snippets():
    print('\n* vim snippets')

    source = home() / '.vim/my_snippets'
    targets = Path('vim-pluggins/ultisnips').glob('*')

    source.mkdir(exist_ok=True)

    link_all(source, targets)


def install_fzf():
    print('\n* fzf')
    print('   * Clone fzf into ~/.fzf')

    home_ = home()

    destination = home_ / '.fzf'

    if Path.is_dir(destination):
        msg.warning(
            '   Warning: .fzf already exists in home directory. '
            'Aborting installation...'
        )

    else:
        msg.inseparator('Start git clone', n=60, sep='-', clr=color.orange)
        subprocess.call(
            [
                'git',
                'clone',
                '--depth',
                '1',
                'https://github.com/junegunn/fzf.git',
                str(destination)
            ]
        )
        msg.inseparator('End git clone', n=60, sep='-', clr=color.orange)

        print('\n   * Install fzf: \n')

        destination = home_ / '.fzf/install'

        msg.inseparator('Start fzf installer (external script)', n=60, sep='-', clr=color.orange)
        subprocess.call(['bash', destination, '--no-zsh', '--no-fish'])
        msg.inseparator('End fzf installer', n=60, sep='-', clr=color.orange)


def main():

    install_oh_my_bash()

    install_dot_files()

    install_config_folder()

    install_fzf()

    install_vim_snippets()

    msg.custom(
        f'\nBackup files are stored in folder {backup_folder()}\n',
        color.cyan
    )


if __name__ == '__main__':
    main()
