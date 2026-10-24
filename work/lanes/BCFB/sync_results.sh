#!/bin/bash
set -euo pipefail
cd /home/jihoon/competitions/quantumn
ssh -q -o ControlMaster=no -o ControlPath=none owl 'docker exec bcfb_fast521 /home/jihoon/competitions/quantumn/.venv/bin/python /home/jihoon/competitions/quantumn/work/lanes/BCFB/snapshot.py'
rsync -a -e 'ssh -q -o ControlMaster=no -o ControlPath=none' owl:/home/jihoon/competitions/quantumn/work/lanes/BCFB/search_snapshot.sqlite work/lanes/BCFB/search.sqlite
rsync -a -e 'ssh -q -o ControlMaster=no -o ControlPath=none' owl:/home/jihoon/competitions/quantumn/work/lanes/BCFB/finalists/ work/lanes/BCFB/finalists/
rsync -a -e 'ssh -q -o ControlMaster=no -o ControlPath=none' owl:/home/jihoon/competitions/quantumn/work/lanes/BCFB/runs/ work/lanes/BCFB/runs/
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python work/lanes/BCFB/report.py
