#!/usr/bin/env bash

source "./include/check-host.sh"

juju deploy ./osm-nglcm_ubuntu-20.04-amd64.charm --resource lcm-image=localhost:32000/opensourcemano/nglcm:devel
