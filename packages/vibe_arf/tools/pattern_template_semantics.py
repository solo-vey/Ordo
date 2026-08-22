#!/usr/bin/env python3
"""Normalize reusable pattern execution-template dialects without changing semantics."""

def execution_components(template):
    comps = template.get('components')
    if comps is None:
        comps = template.get('required_responsibilities')
    if comps is None:
        comps = template.get('roles', [])
    return list(comps or [])

def canonical_outcome_edges(template):
    if template.get('outcome_edges') is not None:
        return list(template.get('outcome_edges') or [])
    out=[]
    for e in template.get('edges',[]) or []:
        row=dict(e)
        row.setdefault('outcome','NEXT')
        out.append(row)
    return out
