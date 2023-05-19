#!/usr/bin/env bash

if [ "$HOSTNAME" == "ringwood" ]; then
    echo "Running on host";
    exit 1;
fi
