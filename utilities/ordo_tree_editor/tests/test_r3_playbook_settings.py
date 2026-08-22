from utilities.ordo_tree_editor import editor_service as es


def test_playbook_settings_reads_current_values_and_registry_options():
    package={"id":"p","filename":"x.zip","source_name":"source/program.ordo.yaml","source":{
        "ordo":{"version":"0.12","package":"demo","control_level":"strict","execution_mode":"chat_internal"},
        "process_rail":{"state_tracking":"required","backtracking":"enabled","allow_deviation":True},
        "nodes":[],"gates":[],
    }}
    out=es._playbook_settings_payload(package)
    assert out["status"]=="passed"
    groups={g["id"]:g for g in out["groups"]}
    assert "ordo" in groups and "process_rail" in groups
    fields={f["path"]:f for g in out["groups"] for f in g["fields"]}
    assert fields["ordo.control_level"]["current_value"]=="strict"
    assert {o["value"] for o in fields["ordo.control_level"]["options"]} >= {"light","standard","strict"}
    assert {o["value"] for o in fields["ordo.execution_mode"]["options"]} >= {"full_runtime","chat_internal","freeform_only"}
    assert {o["value"] for o in fields["process_rail.backtracking"]["options"]} >= {"disabled","restricted","enabled"}
    assert fields["process_rail.allow_deviation"]["options"] == []


def test_playbook_settings_does_not_dump_graph_nodes_as_settings():
    out=es._playbook_settings_payload({"source":{"ordo":{"version":"0.12"},"nodes":[{"id":"N1","question":"x"}]}})
    paths=[f["path"] for g in out["groups"] for f in g["fields"]]
    assert not any(p.startswith("nodes") for p in paths)
