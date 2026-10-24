#!/bin/bash
# Usage: draw_loop.sh <pid of the running cut_redraws.sh>
# Hourly: when the previous hour's draws are cut, race draws of the stem named in receipts/next_stem.txt until HH:20
# for the HH:37 slot. Each hour draws an hour-named copy (lanes/MAIN/<name>_h<DDHH>), so logs, draws and the cut
# pattern never mix with an earlier hour's promote that is still picking, checking or submitting. race.py drops draws
# that cannot get below our board key (3 significant figures), so only draws that would lower it are completed.
cd /home/jihoon/competitions/quantumn/work
prev=$1
while true; do
  tail --pid=$prev -f /dev/null
  src=$(cat receipts/next_stem.txt); t=$(date -d "now + 60 min" "+%Y-%m-%d %H:20")
  name=$(basename $src)_h$(date -d "$t" +%d%H); stem=lanes/MAIN/$name
  cp $src.qasm $stem.qasm; cp $src.json $stem.json
  key=$(timeout 60 ../.venv/bin/python submit.py board 2>/dev/null | grep -m1 "초정밀모델제어학회쨩" | sed -n 's/.*(key \([0-9.e+-]*\)).*/\1/p')
  thr=$(python3 -c "import math,sys; k=float(sys.argv[1]); print(k - 0.5 * 10 ** (math.floor(math.log10(k)) - 2))" "${key:-x}" 2>/dev/null || echo inf)
  echo "$(date +%T) $src as $name until $t, threshold $thr"
  nohup bash receipts/cut_redraws.sh $name "$t" tom jerry hippo sunfish owl zebra > receipts/cut_$name.log 2>&1 &
  prev=$!
  RACE_THRESHOLD=$thr nohup bash promote.sh $stem owl:24:0:4000 tom:12:4000:2000 zebra:16:6000:3000 jerry:16:9000:3000 \
    hippo:8:12000:1000 sunfish:8:13000:1000 > receipts/promote_$name.log 2>&1 &
done
