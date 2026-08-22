#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
here=Path(__file__).resolve().parent
rc=subprocess.call([sys.executable,'-m','unittest','-v','test_executor_regressions.py','test_materialization_and_contract_regressions.py'],cwd=here)
if rc: raise SystemExit(rc)
rc=subprocess.call([sys.executable,'test_recovery_diagnosis.py'],cwd=here)
if rc: raise SystemExit(rc)
rc=subprocess.call([sys.executable,'test_conversational_recovery.py'],cwd=here)
if rc: raise SystemExit(rc)
rc=subprocess.call(['node','test_recovery_ui.js'],cwd=here)
if rc: raise SystemExit(rc)
raise SystemExit(subprocess.call(['node','test_conversational_recovery_ui.js'],cwd=here))
