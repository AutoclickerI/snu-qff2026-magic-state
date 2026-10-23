for h in jerry tom; do ssh -o ControlMaster=no -o ControlPath=none $h "cd $PWD; for f in log4*; do echo \$f \$(tail -n1 \$f); done; ls sat4_*.json 2>/dev/null" 2>&1 | grep -aE 'log4|json'; done
