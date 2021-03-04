mountit() {
  mkdir -p .$1
  sshfs -o allow_other,defer_permissions,IdentityFile=~/.ssh/id_rsa  garampat@$1.ethz.ch: .$1
}

unmountit() {
  diskutil umount force .$1/
}