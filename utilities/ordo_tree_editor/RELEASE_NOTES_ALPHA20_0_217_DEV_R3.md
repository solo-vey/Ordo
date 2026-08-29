# Ordo Tree Editor 0.2.0-alpha.20.0.217-dev

- Restored Editor-native graph context menus and SVG export after separating them from the removed standalone Graphviz utility.
- General graph actions are no longer hidden inside legacy edit-only actions, so the context menu is available on the read-only main graph.
- Show Tree / Show Path context menu includes collapse/expand, current-graph SVG export, YAML export, and full-playbook download.
- Show Data Flow now has its own graph context menu with current-graph SVG export, Fit, Auto layout, and Top/Left direction controls.
- The removed standalone `ordo_visual_graph_generator` and `graph_render` verification remain removed; no Graphviz `dot` dependency was restored.
- No canonical Ordo/playbook/runtime semantics changed.
