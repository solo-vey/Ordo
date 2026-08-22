from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / 'ordo_editor_defaults.env'
LAUNCHER = ROOT / 'start_ordo_tree_editor.command'


def test_distribution_defaults_do_not_pin_machine_specific_python():
    text = DEFAULTS.read_text(encoding='utf-8')
    assert 'ORDO_PYTHON=' not in text
    assert '/Users/test/' not in text


def test_launcher_has_portable_python_autodetection_and_version_yaml_check():
    text = LAUNCHER.read_text(encoding='utf-8')
    assert 'for candidate in python3.13 python3.12 python3.11 python3.10 python3 python' in text
    assert "sys.version_info >= (3,10)" in text
    assert "-c 'import yaml'" in text
    assert '${ORDO_PYTHON:-}' in text
    assert ' -m venv' in text
