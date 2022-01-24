#!/bin/bash

if ! [ -n "$1" ]              # Tested variable is quoted.
then
	printf "\n	Usage: ssh_no_pass NAME_OF_REMOTE_NODE \n\n"
	exit
fi 

B="$1"

# Uncomment this if this the first time you run this script
# ssh-keygen -t rsa

printf "\n"
printf "\t1) Creating .ssh directory in %s \n" "$B"

ssh $B  mkdir -p .ssh

printf "\t2) Copying aythorized_keys to %s \n" "$B"

cat .ssh/id_rsa.pub | ssh  $B  'cat >> .ssh/authorized_keys'
cat .ssh/id_rsa.pub | ssh  $B  'cat >> .ssh/authorized_keys2'

printf "\t3) Changing permissions of .ssh and authorized_keys in %s \n" "$B"
ssh $B chmod 700 .ssh
ssh $B chmod 640 .ssh/authorized_keys
ssh $B chmod 640 .ssh/authorized_keys2

printf "\n"
