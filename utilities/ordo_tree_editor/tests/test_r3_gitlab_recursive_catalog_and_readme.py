from utilities.ordo_tree_editor import editor_service as svc


def test_gitlab_catalog_is_shallow_and_child_loading_can_continue_to_any_depth(monkeypatch):
    root='https://gitlab.example/ML/promts/-/tree/main/analitics/lu/ordo'
    base='analitics/lu/ordo'
    responses={
        base:[{'type':'tree','name':'risk-factors','path':f'{base}/risk-factors'}],
        f'{base}/risk-factors':[
            {'type':'blob','name':'README.md','path':f'{base}/risk-factors/README.md'},
            {'type':'tree','name':'only-impliment-code','path':f'{base}/risk-factors/only-impliment-code'},
        ],
        f'{base}/risk-factors/only-impliment-code':[
            {'type':'tree','name':'0.4.4-experimental','path':f'{base}/risk-factors/only-impliment-code/0.4.4-experimental'},
        ],
        f'{base}/risk-factors/only-impliment-code/0.4.4-experimental':[
            {'type':'tree','name':'nested','path':f'{base}/risk-factors/only-impliment-code/0.4.4-experimental/nested'},
        ],
        f'{base}/risk-factors/only-impliment-code/0.4.4-experimental/nested':[
            {'type':'blob','name':'DEEP_PLAYBOOK.zip','path':f'{base}/risk-factors/only-impliment-code/0.4.4-experimental/nested/DEEP_PLAYBOOK.zip'},
        ],
    }
    calls=[]
    monkeypatch.setattr(svc,'_gitlab_repository_tree',lambda spec,path: calls.append(path) or responses.get(path,[]))
    data=svc._gitlab_playbook_catalog(root)
    assert calls == [base]
    risk=data['directories'][0]
    assert risk['loaded'] is False
    assert risk['children'] == []

    spec=svc._parse_gitlab_tree_url(root)
    risk_loaded=svc._gitlab_directory_listing(spec,risk['path'])
    assert risk_loaded['readme']['filename']=='README.md'
    child=risk_loaded['children'][0]
    child_loaded=svc._gitlab_directory_listing(spec,child['path'])
    experimental=child_loaded['children'][0]
    exp_loaded=svc._gitlab_directory_listing(spec,experimental['path'])
    nested=exp_loaded['children'][0]
    nested_loaded=svc._gitlab_directory_listing(spec,nested['path'])
    assert nested_loaded['archives'][0]['filename']=='DEEP_PLAYBOOK.zip'
