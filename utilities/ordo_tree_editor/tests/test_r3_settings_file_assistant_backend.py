from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEXT=(ROOT/'editor_service.py').read_text(encoding='utf-8')
for token in [
    'resource_mode=mode=="resource_chat"',
    '_resolve_package_text_resource(package,resource_path)',
    '"selected_file":{"path":resolved_resource_path,"content":resource_text[:60000]}',
    'You are the read-only Package File Assistant inside Ordo Editor.',
    '"yaml_settings_block":"" if resource_mode'
]:
    assert token in TEXT, token
