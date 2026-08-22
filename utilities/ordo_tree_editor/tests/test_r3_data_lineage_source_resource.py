
from pathlib import Path
from utilities.ordo_tree_editor import editor_service as es

def test_static_package_resource_role():
    source={"nodes":[{"id":"N","action":"DOCUMENT.GENERATE","inputs":["templates/T.md"],"output":"generated/O.md"}],"gates":[]}
    package={"resources":{"templates/T.md":"# T"}}
    data=es._build_data_lineage(package,source,{})
    by={n["id"]:n for n in data["nodes"]}
    assert by["artifact:templates/T.md"]["artifact_role"]=="package_source_resource"
    assert by["artifact:generated/O.md"]["artifact_role"]=="generated_or_runtime_artifact"
