#!/bin/bash
# push this lane dir to a host (same absolute path)
h=$1
rsync -a --exclude '__pycache__' /home/jihoon/competitions/quantumn/work/lanes/AENC/ $h:/home/jihoon/competitions/quantumn/work/lanes/AENC/
