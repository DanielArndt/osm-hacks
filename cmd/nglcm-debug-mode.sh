#!/usr/bin/env bash

source "./include/check-host.sh"

juju ssh --container nglcm osm-nglcm/0 'sh -c "mkdir -p /root/.ssh"'
juju scp --container nglcm authorized_keys osm-nglcm/0:/root/.ssh/authorized_keys
juju ssh --container nglcm osm-nglcm/0 'sh -c "chown -R root:root /root/.ssh"'

juju config osm-nglcm common-hostpath=$COMMON_LOCAL_PATH
juju config osm-nglcm lcm-hostpath=$LCM_LOCAL_PATH
juju config osm-nglcm n2vc-hostpath=$N2VC_LOCAL_PATH
juju config osm-nglcm debug-mode=True
