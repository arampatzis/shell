#!/bin/bash
# File              : passwordless-ssh.plugin.sh
# Author            : George Arampatzis <garampat@ethz.ch>
# Date              : 29.01.2022 23:15
# Last Modified Date: 30.01.2022 12:47
# Last Modified By  : George Arampatzis <garampat@ethz.ch>


function passwordless_login {
  
  if [ "$#" -ne 1 ]; then
    printf "Usage:  $0 valid_ip\n"
    return 1
  fi
  
  ip="$1"

  file=$HOME/.ssh/id_rsa.pub
  if [ ! -f "$file" ]; then
    printf "The file $file, containing the public ssh key, does not exist.\n"
    printf "Run 'ssh-keygen -t rsa'\n"
    return 1
  fi

  printf "\n\t1) Create .ssh directory in $ip \n"
  ssh $ip  mkdir -p .ssh
  if [ $? -ne 0 ]; then return 1; fi

  printf "\n\t2) Copy local public key to aythorized_keys in $ip \n"
  cat $file | ssh  $ip  'cat >> .ssh/authorized_keys'
  if [ $? -ne 0 ]; then return 1; fi

  cat $file | ssh  $ip  'cat >> .ssh/authorized_keys2'
  if [ $? -ne 0 ]; then return 1; fi

  printf "\n\t3) Change permissions of .ssh and authorized_keys in $ip \n"
  ssh $ip chmod 700 .ssh
  if [ $? -ne 0 ]; then return 1; fi

  ssh $ip chmod 640 .ssh/authorized_keys
  if [ $? -ne 0 ]; then return 1; fi

  ssh $ip chmod 640 .ssh/authorized_keys2
  if [ $? -ne 0 ]; then return 1; fi
}
