from utilities.ordo_tree_editor import editor_service as svc


def _spec():
    return {"path":"analytics/lu/ordo","project":"ML/promts","ref":"main","base":"https://gitlab.example"}


def test_directory_listing_reads_one_level_only(monkeypatch):
    calls=[]
    def fake_tree(spec,path):
        calls.append(path)
        if path == "analytics/lu/ordo":
            return [
                {"type":"tree","name":"risk-factors","path":"analytics/lu/ordo/risk-factors"},
                {"type":"blob","name":"ROOT.zip","path":"analytics/lu/ordo/ROOT.zip"},
            ]
        raise AssertionError(f"unexpected recursive read: {path}")
    monkeypatch.setattr(svc,"_gitlab_repository_tree",fake_tree)
    node=svc._gitlab_directory_listing(_spec(),"analytics/lu/ordo")
    assert calls == ["analytics/lu/ordo"]
    assert node["archives"][0]["filename"] == "ROOT.zip"
    assert node["children"] == [{"name":"risk-factors","path":"analytics/lu/ordo/risk-factors","readme":None,"archives":[],"children":[],"loaded":False}]


def test_child_payload_is_loaded_independently(monkeypatch):
    def fake_parse(root_url): return _spec()
    def fake_tree(spec,path):
        assert path == "analytics/lu/ordo/risk-factors"
        return [
            {"type":"blob","name":"README.md","path":path+"/README.md"},
            {"type":"tree","name":"0.3.7","path":path+"/0.3.7"},
        ]
    monkeypatch.setattr(svc,"_parse_gitlab_tree_url",fake_parse)
    monkeypatch.setattr(svc,"_gitlab_repository_tree",fake_tree)
    payload=svc._gitlab_directory_payload("https://example/tree/main/analytics/lu/ordo", "analytics/lu/ordo/risk-factors")
    assert payload["directory"]["readme"]["filename"] == "README.md"
    assert payload["directory"]["children"][0]["loaded"] is False


def test_directory_path_must_stay_under_root():
    try:
        svc._gitlab_validate_directory_path(_spec(),"analytics/lu/other")
    except ValueError as exc:
        assert "outside" in str(exc)
    else:
        raise AssertionError("outside-root lazy request must fail")
