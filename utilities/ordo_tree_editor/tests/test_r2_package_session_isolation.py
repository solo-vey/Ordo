from utilities.ordo_tree_editor import editor_service as es


def test_live_run_uses_its_own_loaded_package_id_when_another_package_becomes_current(monkeypatch):
    old_current = dict(es.PLAYBOOK_PACKAGE)
    old_registry = dict(es.PLAYBOOK_PACKAGES)
    try:
        pkg_a = {"id": "pkg-a", "source": {"nodes": []}, "resources": {"a": "A"}, "semantic_plan": {"name": "A"}}
        pkg_b = {"id": "pkg-b", "source": {"nodes": []}, "resources": {"b": "B"}, "semantic_plan": {"name": "B"}}
        es.PLAYBOOK_PACKAGES.clear()
        es.PLAYBOOK_PACKAGES.update({"pkg-a": pkg_a, "pkg-b": pkg_b})
        es.PLAYBOOK_PACKAGE.clear()
        es.PLAYBOOK_PACKAGE.update(pkg_b)  # another tab loaded B after run A started

        def fake_impl(payload):
            active = es._active_playbook_package()
            return {
                "active_id": active.get("id"),
                "resource_keys": sorted((active.get("resources") or {}).keys()),
                "semantic_name": (active.get("semantic_plan") or {}).get("name"),
            }

        monkeypatch.setattr(es, "_call_openai_live_impl", fake_impl)
        result = es._call_openai_live({"package_id": "pkg-a"})
        assert result == {"active_id": "pkg-a", "resource_keys": ["a"], "semantic_name": "A"}
        assert es.PLAYBOOK_PACKAGE.get("id") == "pkg-b"
        assert es._active_playbook_package().get("id") == "pkg-b"
    finally:
        es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old_current)
        es.PLAYBOOK_PACKAGES.clear(); es.PLAYBOOK_PACKAGES.update(old_registry)


def test_unknown_package_id_fails_closed():
    try:
        es._call_openai_live({"package_id": "definitely-not-loaded"})
    except ValueError as exc:
        assert "playbook ZIP package loaded by this editor server" in str(exc)
    else:
        raise AssertionError("unknown package id must fail closed")
