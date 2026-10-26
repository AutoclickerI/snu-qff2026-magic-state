#!/bin/bash
# Usage: race_specs.sh <first variant>  ->  line 1: promote.sh host specs (host:procs:first:count), line 2: variants used
# Processes per host fill what other users and our lanes leave free (runnable counts, max of 5 samples): all our
# processes stay within 75% of the host's cores (CONSTRAINTS); the racer max (4th field) is lower on zebra (main session and lanes)
# and on owl, jerry, hippo, sunfish and tom, which are kept for research lanes.
SSH="ssh -q"
off=$1; specs=
probe='a=0; m=0; for i in 1 2 3 4 5; do r=$(cut -d" " -f4 /proc/loadavg); r=$((${r%/*} - 1)); [ $r -gt $a ] && a=$r
  o=$(ps -u jihoon -o stat= | grep -c "^R"); o=$((o - 1)); [ $o -gt $m ] && m=$o; sleep 1; done; echo $a $m'
for hc in owl:96:72:48 tom:64:48:36 jerry:64:48:24 hippo:48:36:12 sunfish:32:24:4 zebra:64:48:8; do
  IFS=: read -r h cores cap rmax <<< "$hc"
  if [ "$h" = zebra ]; then out=$(bash -c "$probe"); else out=$(timeout 30 $SSH $h "$probe" 2>/dev/null); fi
  read -r busy mine <<< "$out"
  [ -n "$mine" ] || continue
  procs=$((cores - busy - 2)); [ $procs -gt $((cap - mine)) ] && procs=$((cap - mine))
  [ $procs -gt $rmax ] && procs=$rmax; [ $procs -lt 4 ] && continue   # no room: skip the host (75% cap)
  specs="$specs $h:$procs:$off:$((procs * 400))"; off=$((off + procs * 400))
done
echo $specs
echo $((off - $1))
