from utilities.ordo_tree_editor import editor_service as svc


def test_gitlab_catalog_returns_first_level_only(monkeypatch):
    root='https://gitlab.example/ML/promts/-/tree/main/analitics/lu/ordo'
    calls=[]
    responses={
      'analitics/lu/ordo':[
        {'type':'tree','name':'monitoring-business','path':'analitics/lu/ordo/monitoring-business'},
        {'type':'tree','name':'risk-factors','path':'analitics/lu/ordo/risk-factors'},
        {'type':'blob','name':'ROOT_PLAYBOOK.zip','path':'analitics/lu/ordo/ROOT_PLAYBOOK.zip'},
      ],
    }
    monkeypatch.setattr(svc,'_gitlab_repository_tree',lambda spec,path: calls.append(path) or responses.get(path,[]))
    data=svc._gitlab_playbook_catalog(root)
    assert calls == ['analitics/lu/ordo']
    assert [x['name'] for x in data['directories']]==['monitoring-business','risk-factors']
    assert data['archive_count']==1
    assert data['directory_count']==2
    assert data['lazy'] is True
    assert data['root']['archives'][0]['filename']=='ROOT_PLAYBOOK.zip'
