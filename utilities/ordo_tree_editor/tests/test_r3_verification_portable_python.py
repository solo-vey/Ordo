from utilities.ordo_tree_editor.verification import runner
import sys

def test_python_tokens_resolve_to_current_interpreter():
    for token in ('python','python3','{python}'):
        cmd=runner._normalize_command([token,'-c','print(1)'])
        assert cmd[0] == sys.executable

def test_non_python_command_is_not_rewritten():
    assert runner._normalize_command(['bash','-lc','true'])[0] == 'bash'
