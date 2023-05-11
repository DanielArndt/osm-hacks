#!/usr/bin/env bash

juju ssh --container nglcm osm-nglcm/0 'sh -c "mkdir -p /root/.local/share/juju/ssh/"'
juju scp --container nglcm "${HOME}"/.local/share/juju/ssh/juju_id_rsa.pub osm-nglcm/0:/root/.local/share/juju/ssh/juju_id_rsa.pub
juju ssh --container nglcm osm-nglcm/0 'sh -c "chown -R root:root /root/.local/share/juju/ssh/"'
