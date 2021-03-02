#! /usr/bin/env bash

rm -rf ~/.vimrc 
src=`realpath vim/.vimrc`
ln -sv $src ~/.vimrc

rm -rf ~/.oh-my-bash/custom 
src=`realpath oh.my.bash/custom`
ln -sv $src ~/.oh-my-bash/custom

rm -rf ~/.bashrc 
src=`realpath oh.my.bash/.bashrc`
ln -sv $src ~/.bashrc

