#!/usr/bin/env bash

source "./include/check-host.sh"

juju deploy ./osm-nbi_ubuntu-20.04-amd64.charm --resource nbi-image=localhost:32000/opensourcemano/nbi:devel nbi
