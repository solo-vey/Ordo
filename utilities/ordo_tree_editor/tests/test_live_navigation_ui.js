const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'web', 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'web', 'styles.css'), 'utf8');
function ok(cond, msg) { if (!cond) { console.error('FAIL:', msg); process.exit(1); } }
ok(css.includes('.live-status { position: sticky; top: 52px; z-index: 55;'), 'live status must remain sticky below panel tabs');
ok(app.includes('function scheduleLiveTreeAutoFocus()'), 'live tree auto-focus helper missing');
ok(app.includes('state.liveTreeAutoFocusId === state.liveCurrentId'), 'auto-focus must only trigger when current node changes');
ok(app.includes('workspace.scrollTo({') && app.includes('state.liveTreeAutoFocusId = id'), 'auto-focus must scroll the tree workspace');
ok(app.includes('const gateFailure=debug.alpha20?.gate_failure || {};'), 'recovery evidence must read alpha20 gate failure');
console.log('PASS live navigation UI');
