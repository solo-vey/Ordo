const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'web', 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'web', 'styles.css'), 'utf8');
function must(x, msg){ if(!x){ console.error('FAIL:',msg); process.exit(1); } }
must(app.includes('makeDraggable(element);'), 'rendered nodes must be draggable');
must(app.includes('state.manualPositions.has(node.id) ? positionFor(node.id) : (focusLayout?.[node.id] || automatic[node.id])'), 'manual node positions must override focus layouts');
must(app.includes('state.manualPositions.add(id)'), 'drag must persist in local manual-position state');
must(css.includes('.node { cursor:grab; }'), 'draggable cursor must be visible');
console.log('PASS alpha.20.0.28 visual-only node drag UI contract');
