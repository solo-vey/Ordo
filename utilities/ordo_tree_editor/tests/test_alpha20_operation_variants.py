import alpha20_runtime as rt

ROW_SCHEMA={
    'type':'array',
    'items':{
        'type':'object',
        'required':['id','value'],
        'properties':{'id':{'type':'string'},'value':{'type':'string'}},
        'additionalProperties':False,
    },
}
VARIANTS=[
    {
        'type':'object',
        'required':['op','path','value','basis','reason','row_key','row_match'],
        'properties':{
            'op':{'const':'append'},
            'path':{'const':'catalog.rows'},
            'value':ROW_SCHEMA['items'],
            'basis':{'enum':['generated',None]},
            'reason':{'type':['string','null']},
            'row_key':{'type':['string','null']},
            'row_match':{'type':['string','number','integer','boolean','null']},
        },
        'additionalProperties':False,
    }
]

def patch(op, value=None):
    item={'op':op,'path':'catalog.rows','basis':'generated','reason':'test','row_key':None,'row_match':None}
    if op!='remove': item['value']=value
    return {'base_revision':0,'operations':[item]}

def test_declared_operation_variant_is_accepted():
    result=rt.validate_state_patch(
        patch('append',{'id':'r1','value':'x'}),
        allowed_paths=['catalog.rows'], current_revision=0,
        value_schemas={'catalog.rows':ROW_SCHEMA}, operation_variants=VARIANTS,
    )
    assert result['valid'], result

def test_undeclared_operation_is_rejected_even_when_path_and_value_are_valid():
    result=rt.validate_state_patch(
        patch('set',[{'id':'r1','value':'x'}]),
        allowed_paths=['catalog.rows'], current_revision=0,
        value_schemas={'catalog.rows':ROW_SCHEMA}, operation_variants=VARIANTS,
    )
    assert not result['valid']
    assert any('does not match any declared operation variant' in e for e in result['errors'])
