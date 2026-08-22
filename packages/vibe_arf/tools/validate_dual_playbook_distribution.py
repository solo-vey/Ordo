#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
if len(sys.argv)==3:
    # Historical pair lacks MODEL_RUN; validate the two supplied profiles only for compatibility.
    e=subprocess.run(['python',str(Path(__file__).with_name('validate_distribution_package.py')),sys.argv[1],'--mode','edit'])
    c=subprocess.run(['python',str(Path(__file__).with_name('validate_distribution_package.py')),sys.argv[2],'--mode','cli_run'])
    raise SystemExit(0 if e.returncode==0 and c.returncode==0 else 1)
print('usage: validate_dual_playbook_distribution.py EDIT.zip CLI_RUN.zip',file=sys.stderr); raise SystemExit(2)
