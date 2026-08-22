#!/usr/bin/env python3
"""Normalize reusable pattern Data-Layer template dialects without changing pattern semantics."""

def data_roles(template):
    roles = template.get('required_roles')
    if roles is not None:
        return list(roles or [])
    state = template.get('state_template') or {}
    out=[]
    for role, spec in state.items():
        spec = spec or {}
        out.append({
            'role': role,
            'binds_to': spec.get('binds_to','information_or_artifact'),
            'required': bool(spec.get('required',False)),
            'generator_binding': spec.get('generator_binding'),
            'meaning': spec.get('meaning'),
        })
    return out

def data_module_edges(template):
    return list(template.get('module_edges') or [])
