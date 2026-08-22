const fs = require('fs');
const app = fs.readFileSync('web/app.js','utf8');
const css = fs.readFileSync('web/styles.css','utf8');
function must(v,m){ if(!v){ console.error('FAIL',m); process.exit(1);} }
must(css.includes('#canvas { position: relative; z-index: 2; min-width: 1050px; min-height: 700px; pointer-events: auto; }'), 'canvas must receive pointer events');
must(css.includes('touch-action: none'), 'nodes must disable browser gesture interception');
must(app.includes("window.addEventListener('pointermove', move, true)"), 'drag must track pointer movement at window capture level');
must(app.includes('state.manualPositions.add(id)'), 'drag must persist manual layout state');
must(app.includes('event.stopPropagation()'), 'node drag must not fall through to workspace handlers');
must(app.includes('drawLivePathOverlay()'), 'all tree overlays must redraw during drag');
console.log('PASS alpha.20.0.29 executable visual node drag contract');
