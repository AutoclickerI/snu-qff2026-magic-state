#!/bin/bash
# Starts v36b's re-draws when v36a's draws are cut (02:20), for the 03:37 slot.
cd /home/jihoon/competitions/quantumn/work
tail --pid=3724939 -f /dev/null
nohup bash receipts/cut_redraws.sh v36b "03:20" tom jerry hippo sunfish owl zebra > receipts/cut_v36b.log 2>&1 &
bash promote.sh lanes/MAIN/v36b owl:24:0:384 tom:12:384:192 zebra:16:576:256 jerry:16:832:256 hippo:8:1088:128 sunfish:8:1216:128 > receipts/promote_v36b.log 2>&1
