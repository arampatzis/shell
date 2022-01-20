#!/bin/bash
# File              : mountit.plugin.sh
# Author            : George Arampatzis <garampat@ethz.ch>
# Date              : 18.01.2022 20:23
# Last Modified Date: 18.01.2022 20:23
# Last Modified By  : George Arampatzis <garampat@ethz.ch>

mountit() {
  mkdir -p .$1
  sshfs -o allow_other,defer_permissions,IdentityFile=~/.ssh/id_rsa  garampat@$1.ethz.ch: .$1
}

unmountit() {
  diskutil umount force .$1/
}
