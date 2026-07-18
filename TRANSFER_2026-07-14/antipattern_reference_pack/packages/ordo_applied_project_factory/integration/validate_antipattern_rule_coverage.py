from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
import yaml

CANONICAL = {
    'PROMPT_AS_IMPLEMENTATION',
    'PACKAGE_VALIDATION_WITHOUT_COMPLETENESS_VALIDATION',
    'MANDATORY_BRANCH_SHORT_CIRCUIT',
    'FINAL_LABEL_OVERCLAIM',
    'SCOPE_CONFIRMATION_AS_IMPLEMENTATION_AUTHORIZATION',
    'COMPLEXITY_ROUTING_AND_EXECUTION_IN_ONE_NODE',
}

def validate(package_root: Path) -> dict:
    repo_root = package_root.parents[1]
    language_root = repo_root / 'language'
    source = yaml.safe_load((package_root/'source/program.ordo.yaml').read_text(encoding='utf-8'))
    inventory = json.loads((package_root/'integration/antipattern_hook_inventory.apf.v1.json').read_text(encoding='utf-8'))
    profile = json.loads((language_root/'integration/antipattern_activation_profile.apf.v1.json').read_text(encoding='utf-8'))
    registry = json.loads((language_root/'registries/antipattern_registry.v1.json').read_text(encoding='utf-8'))
    detect = json.loads((language_root/'registries/detect_rule_registry.v1.json').read_text(encoding='utf-8'))

    active = {x['id'] for x in registry['items'] if x.get('status') == 'active'}
    allowed_contexts = defaultdict(set)
    for rule in detect['items']:
        if rule.get('status') == 'active':
            allowed_contexts[rule['antipattern_id']].update(rule['input_contract'].get('allowed_contexts', []))

    source_hooks = []
    for node in source['nodes']:
        for hook in node.get('antipattern_hooks', []):
            source_hooks.append((node['id'], hook))

    errors=[]
    warnings=[]
    ids=[]
    coverage=Counter()
    by_rule=defaultdict(list)
    for source_id, hook in source_hooks:
        hid=hook['hook_id']; ids.append(hid)
        rules=hook.get('enabled_antipattern_overrides', [])
        if not rules:
            errors.append(f'{hid}: empty enabled_antipattern_overrides')
        for rid in rules:
            coverage[rid]+=1
            by_rule[rid].append({'source_id':source_id,'hook_id':hid,'context_type':hook['context_type'],'phase':hook['phase']})
            if rid not in active:
                errors.append(f'{hid}: unknown or inactive rule {rid}')
            if hook['context_type'] not in allowed_contexts[rid]:
                errors.append(f'{hid}: {rid} unsupported in context {hook["context_type"]}')
        if hook['context_type'] not in profile['contexts']:
            errors.append(f'{hid}: context not activated: {hook["context_type"]}')

    dup=[k for k,v in Counter(ids).items() if v>1]
    if dup: errors.append(f'duplicate hook ids: {dup}')
    missing=sorted(CANONICAL-set(coverage))
    unknown=sorted(set(coverage)-CANONICAL)
    if missing: errors.append(f'canonical rules without hook coverage: {missing}')
    if unknown: errors.append(f'non-canonical rules in hooks: {unknown}')

    inventory_pairs={(h['source_id'],h['hook_id'],h['context_type'],tuple(h['rules'])) for h in inventory['hooks']}
    source_pairs={(sid,h['hook_id'],h['context_type'],tuple(h.get('enabled_antipattern_overrides',[]))) for sid,h in source_hooks}
    if inventory_pairs != source_pairs:
        errors.append('hook inventory differs from assembled source')

    return {
        'schema_version':'ordo.apf.antipattern_rule_coverage_report.v1',
        'package_id':'ordo.applied_project_factory',
        'status':'passed' if not errors else 'failed',
        'canonical_rule_count':len(CANONICAL),
        'covered_rule_count':len(set(coverage)&CANONICAL),
        'source_node_count':len({sid for sid,_ in source_hooks}),
        'hook_count':len(source_hooks),
        'coverage_counts':dict(sorted(coverage.items())),
        'rule_bindings':dict(sorted(by_rule.items())),
        'errors':errors,
        'warnings':warnings,
    }

if __name__ == '__main__':
    root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).parents[1]).resolve()
    report=validate(root)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status']=='passed' else 1)
