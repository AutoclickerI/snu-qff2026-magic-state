#!/bin/bash
# Usage: draw_loop.sh <pid of the running cut_redraws.sh>
# Hourly: when the previous hour's draws are cut, re-draw the stem named in receipts/next_stem.txt until HH:20 for the
# HH:37 slot. Each hour draws an hour-named copy (lanes/MAIN/<name>_h<DDHH>), so logs, draws and the cut pattern never
# mix with an earlier hour's promote that is still picking, checking or submitting.
cd /home/jihoon/competitions/quantumn/work
prev=$1
while true; do
  tail --pid=$prev -f /dev/null
  src=$(cat receipts/next_stem.txt); t=$(date -d "now + 60 min" "+%Y-%m-%d %H:20")
  name=$(basename $src)_h$(date -d "$t" +%d%H); stem=lanes/MAIN/$name
  cp $src.qasm $stem.qasm; cp $src.json $stem.json
  echo "$(date +%T) $src as $name until $t"
  nohup bash receipts/cut_redraws.sh $name "$t" tom jerry hippo sunfish owl zebra > receipts/cut_$name.log 2>&1 &
  prev=$!
  nohup bash promote.sh $stem owl:24:0:384 tom:12:384:192 zebra:16:576:256 jerry:16:832:256 hippo:8:1088:128 \
    sunfish:8:1216:128 > receipts/promote_$name.log 2>&1 &
done
