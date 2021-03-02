#! /usr/bin/env bash

rm -rf ~/.vimrc 
ln -sv vim/vimrc ~/.vimrc

rm -rf ~/.oh-my-bash/custom 
ln -sv oh.my.bash/custom  ~/.oh-my-bash/custom

rm -rf ~/.bashrc 
ln -sv oh.my.bash/.bashrc  ~/.bashrc

