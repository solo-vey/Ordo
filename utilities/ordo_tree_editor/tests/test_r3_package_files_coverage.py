import io, zipfile
from utilities.ordo_tree_editor import editor_service as es

def _zip(files):
    bio=io.BytesIO()
    with zipfile.ZipFile(bio,'w',zipfile.ZIP_DEFLATED) as z:
        for path,data in files.items(): z.writestr(path,data)
    return bio.getvalue()

def test_package_files_coverage_and_preview():
    files={
        'program.ordo.yaml':'nodes:\n  - id: N1\n    type: task\n    template_ref: refs/prompt.md\ngates: []\n',
        'refs/prompt.md':'# Prompt\nHello',
        'runtime/helper.py':'print("ok")\n',
        'README.md':'# Package\n',
        'authoring_templates/free.md':'# Not surfaced elsewhere\n',
    }
    raw=_zip(files)
    package={
        'id':'pkg','filename':'pkg.zip','source_name':'program.ordo.yaml',
        'source':{'nodes':[{'id':'N1','type':'task','template_ref':'refs/prompt.md'}],'gates':[]},
        'resources':{k:v for k,v in files.items()},
        'manifest':[{'path':k,'size':len(v.encode()),'text':True} for k,v in files.items()],
        'raw_zip':raw,
    }
    data=es._package_files_payload(package,mode='list')
    by={row['path']:row for row in data['files']}
    assert 'Tree' in by['program.ordo.yaml']['coverage']
    assert 'Tree' in by['refs/prompt.md']['coverage']
    assert 'Settings' in by['runtime/helper.py']['coverage']
    assert 'Settings' in by['README.md']['coverage']
    assert by['authoring_templates/free.md']['uncovered'] is True
    assert data['summary']['uncovered'] >= 1
    preview=es._package_files_payload(package,mode='read',resource_path='authoring_templates/free.md')
    assert preview['preview']['available'] is True
    assert preview['preview']['kind']=='markdown'
    assert 'Not surfaced elsewhere' in preview['preview']['content']
