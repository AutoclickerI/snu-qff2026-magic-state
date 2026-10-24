#!/bin/bash
set -euo pipefail
cd /home/jihoon/competitions/quantumn/work/lanes/KNAP
requested=$1
name=$2
shift 2
running=$(ps -eo user,stat,comm | awk '$1=="jihoon" && $2 ~ /R/ && $3 !~ /^(ps|awk|bash|sshd)$/ {n++} END {print n+0}')
all_running=$(ps -eo stat,comm | awk '$1 ~ /R/ && $2 !~ /^(ps|awk|bash|sshd)$/ {n++} END {print n+0}')
available=$((72-running))
total_available=$((96-all_running))
(( available > total_available )) && available=$total_available
# Reserve against other containers' CPU quotas as well as instantaneous runnable work,
# because their child pools can become runnable again between snapshots.
ids=$(docker ps -q)
if [[ -n $ids ]]; then
  reserved=$(docker inspect --format '{{.HostConfig.NanoCpus}}' $ids | awk '{s+=$1} END {printf "%.0f",s/1000000000}')
  quota_available=$((72-reserved))
  (( available > quota_available )) && available=$quota_available
fi
(( available > requested )) && available=$requested
if (( available < 1 )); then
  echo "No current CPU capacity: Jihoon runnable=$running total=$all_running" >&2
  exit 75
fi
uptime
echo "launch $name: quota=$available requested=$requested Jihoon runnable=$running total=$all_running"
args=("$@")
for ((i=1;i<${#args[@]};i++)); do
  if [[ ${args[i-1]} == --workers || ${args[i-1]} == --procs ]]; then
    (( args[i] > available )) && args[i]=$available
  fi
done
exec docker run --rm --name "$name" -u 1010:1012 -e HOME=/home/jihoon -e PYTHONDONTWRITEBYTECODE=1 -e KNAP_CPUS="$available" -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w /home/jihoon/competitions/quantumn/work/lanes/KNAP --cpus="$available" fnc-build:22.04 /home/jihoon/competitions/quantumn/.venv/bin/python "${args[@]}"
