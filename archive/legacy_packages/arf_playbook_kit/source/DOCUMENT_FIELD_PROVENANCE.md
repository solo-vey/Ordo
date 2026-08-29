# Document field provenance validation

Before a playbook materializes a document, every required document field must
be declared in the playbook state and collected on every applicable path.
Authoring contracts should keep this relationship explicit:

```yaml
documents:
  - document_id: event_passport
    materialization_node: N_MATERIALIZE_EVENT_PASSPORT
    required_fields:
      - field: display_name_uk
        required: true
        collection_mode: analyst_answer
      - field: display_name_en
        required: true
        collection_mode: analyst_answer
```

The Ordo CLI validates this contract with:

```text
ordo validate-document-fields <package> --bindings path/to/document_bindings.yaml
```

The validator follows all graph paths to each materialization node and reports
structured findings. A missing state declaration or a field with no producer on
an applicable path is an error and blocks document readiness. A producer that
exists but is not marked required (or protected by an upstream gate) is a
warning: the field can be reached, but the playbook should make the collection
requirement explicit. The JSON report records the document, field, path,
producer node, collection mode, severity, and actionable source location.

This check is deterministic and complementary to runtime validation. It does
not expose hidden model reasoning; it verifies the observable contract between
state, nodes, gates, and document templates.
