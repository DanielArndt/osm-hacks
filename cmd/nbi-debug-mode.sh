#!/usr/bin/env bash
juju config nbi common-hostpath=$COMMON_LOCAL_PATH
juju config nbi nbi-hostpath=$NBI_LOCAL_PATH
juju config nbi debug-mode=True

juju ssh --container nbi nbi/0 'sh -c "mkdir -p /root/.ssh"'
juju scp --container nbi authorized_keys nbi/0:/root/.ssh/authorized_keys
juju ssh --container nbi nbi/0 'sh -c "chown -R root:root /root/.ssh"'

