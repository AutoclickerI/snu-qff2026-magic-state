#!/bin/bash
cd /home/jihoon/competitions/quantumn/work/lanes/ST_BC
while true; do
 for h in jerry hippo; do
  for f in $(ssh -o ControlMaster=no -o ControlPath=none $h "cd $PWD; ls sat4_*.json sat5_*.json sat6_*.json sat7_*.json 2>/dev/null" 2>/dev/null | grep -a '^sat'); do
   if [ ! -f $f ]; then rsync -q -e "ssh -o ControlMaster=no -o ControlPath=none" $h:$PWD/$f . && echo NEW $f && exit 0; fi
  done; sleep 3
 done; sleep 60
done
