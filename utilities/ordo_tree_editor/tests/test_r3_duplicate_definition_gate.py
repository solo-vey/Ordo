from pathlib import Path
from utilities.ordo_tree_editor.check_duplicate_definitions import scan

def test_editor_service_has_no_duplicate_top_level_definitions():
    path=Path(__file__).resolve().parents[1]/'editor_service.py'
    assert scan(path)==[]
