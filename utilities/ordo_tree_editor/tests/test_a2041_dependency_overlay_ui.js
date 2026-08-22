const fs = require('fs');
const path = require('path');
const base = fs.existsSync('web/app.js') ? '.' : 'utilities/ordo_tree_editor';
const app = fs.readFileSync(path.join(base, 'web/app.js'), 'utf8');
const css = fs.readFileSync(path.join(base, 'web/styles.css'), 'utf8');

function assert(cond, msg) { if (!cond) { console.error(`FAIL: ${msg}`); process.exit(1); } }
assert(app.includes('if (relation !== "control_flow") return;'), 'automatic layout must ignore non-control relations');
assert(css.includes('marker-end: none;'), 'dependency/output overlays must not use execution arrowheads');
assert(css.includes('.edge-line.edge-validation_dependency'), 'validation dependency style must exist');
assert(css.includes('stroke-dasharray: 5 6;'), 'dependency overlays must be dashed');
console.log('PASS test_a2041_dependency_overlay_ui');
