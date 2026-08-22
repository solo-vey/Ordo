from editor_service import _playbook_settings_unbound_resource_groups

package={
    "source_name":"source/program.ordo.yaml",
    "source":{
        "nodes":[{"id":"N1","action":"TOOL.X","tool":"tools/bound.py","template":"templates/bound.md"}],
        "gates":[],
    },
    "resources":{
        "source/program.ordo.yaml":"nodes: []",
        "tools/bound.py":"print('bound')",
        "templates/bound.md":"bound",
        "tools/global_helper.py":"print('global')",
        "runtime/state.initial.json":"{}",
        "README.md":"readme",
        "PACKAGE_PROFILE.json":"{}",
        "verification/GLOBAL_POLICY.md":"policy",
        "verification/tests/test_policy.py":"assert True",
        "knowledge/GENERAL.md":"knowledge",
    },
    "manifest":[
        {"path":"tools/bound.py","size":10},{"path":"templates/bound.md","size":5},
        {"path":"tools/global_helper.py","size":12},{"path":"runtime/state.initial.json","size":2},
        {"path":"README.md","size":6},{"path":"PACKAGE_PROFILE.json","size":2},
        {"path":"verification/GLOBAL_POLICY.md","size":6},{"path":"verification/tests/test_policy.py","size":11},
        {"path":"knowledge/GENERAL.md","size":9},
    ],
}
groups={g["id"]:g for g in _playbook_settings_unbound_resource_groups(package)}
paths=lambda gid:{f["path"] for f in groups[gid]["files"]}
assert paths("runtime")=={"tools/global_helper.py","runtime/state.initial.json"}
assert paths("package")=={"README.md","PACKAGE_PROFILE.json"}
assert paths("verification")=={"verification/GLOBAL_POLICY.md"}
all_paths=set().union(*(paths(x) for x in groups))
assert "tools/bound.py" not in all_paths
assert "templates/bound.md" not in all_paths
assert "verification/tests/test_policy.py" not in all_paths
assert "knowledge/GENERAL.md" not in all_paths
print('PASS Playbook Settings unbound resource classification')
