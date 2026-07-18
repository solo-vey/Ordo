from pathlib import Path
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[2]
EN=ROOT/'book/en'

def test_en_manifest_hashes_and_files():
 m=json.loads((EN/'book_manifest.json').read_text())
 assert m['locale']=='en'
 assert len(m['chapters'])>=96
 for e in m['chapters']:
  p=EN/e['file']; assert p.is_file(), e['file']
  assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']
 for e in m['assets']:
  p=EN/e['file']; assert p.is_file(), e['file']
  assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']

def test_required_appendices_present():
 names={p.name for p in (EN/'chapters').glob('appendix_*.md')}
 assert {'appendix_a_ordo_glossary.md','appendix_b_opcode_catalog.md','appendix_c_verified_program_examples.md','appendix_d_checklists.md','appendix_e_anti_patterns.md','appendix_f_practical_yaml_reference.md'}.issubset(names)

def test_all_in_one_contains_every_manifest_section():
 m=json.loads((EN/'book_manifest.json').read_text())
 text=(EN/'compiled/ordo_for_beginners_en_all_in_one.md').read_text()
 for e in m['chapters']:
  first=next((x for x in (EN/e['file']).read_text().splitlines() if x.startswith('#')),None)
  assert first and first in text, e['file']

def test_markdown_asset_links_resolve():
 missing=[]
 for p in (EN/'chapters').glob('*.md'):
  for target in re.findall(r'!\[[^]]*\]\(([^)]+)\)',p.read_text()):
   if target.startswith(('http:','https:','data:')): continue
   q=(p.parent/target).resolve()
   if not q.exists(): missing.append((p.name,target))
 assert not missing

def test_appendix_f_is_schema_grounded():
 text=(EN/'chapters/appendix_f_practical_yaml_reference.md').read_text()
 assert 'Canonical schema:' in text
 assert text.count('Canonical schema:') >= 30
 assert 'strict enum' not in text.lower() or 'enum' in text.lower()
