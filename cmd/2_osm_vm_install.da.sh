#!/usr/bin/env bash

sudo ln -s ~/OSM/devops /usr/share/osm-devops
cd ~/OSM/devops/installers || exit
./charmed_install.sh --bundle ./charm/bundles/osm/bundle.yaml | tee ~/charmed_install.log

grep '^export OSM' ~/charmed_install.log >> ~/.bashrc

cat << 'EOF' > $HOME/osm-vars.sh
export GIT_PATH=$HOME/OSM
export COMMON_LOCAL_PATH="$GIT_PATH/common"
export LCM_LOCAL_PATH="$GIT_PATH/LCM"
export MON_LOCAL_PATH="$GIT_PATH/MON"
export N2VC_LOCAL_PATH="$GIT_PATH/N2VC"
export NBI_LOCAL_PATH="$GIT_PATH/NBI"
export POL_LOCAL_PATH="$GIT_PATH/POL"
export RO_LOCAL_PATH="$GIT_PATH/RO"
EOF
echo ". $HOME/osm-vars.sh" >> $HOME/.bashrc
. $HOME/osm-vars.sh

juju config lcm common-hostpath=$COMMON_LOCAL_PATH
juju config lcm lcm-hostpath=$LCM_LOCAL_PATH
juju config lcm n2vc-hostpath=$N2VC_LOCAL_PATH

juju config mon common-hostpath=$COMMON_LOCAL_PATH
juju config mon mon-hostpath=$MON_LOCAL_PATH
juju config mon n2vc-hostpath=$N2VC_LOCAL_PATH

juju config nbi common-hostpath=$COMMON_LOCAL_PATH
juju config nbi nbi-hostpath=$NBI_LOCAL_PATH

juju config pol common-hostpath=$COMMON_LOCAL_PATH
juju config pol pol-hostpath=$POL_LOCAL_PATH

juju config ro common-hostpath=$COMMON_LOCAL_PATH
juju config ro ro-hostpath=$RO_LOCAL_PATH

# Show the exports
grep '^export OSM' ~/charmed_install.log
printf "Run: \n. %s/osm-vars.sh" "$HOME"
