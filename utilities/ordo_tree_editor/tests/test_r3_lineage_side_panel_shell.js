const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(cond,msg){ if(!cond) throw new Error(msg); }
must(html.includes('id="side-pane-toggle"'),'shared side-pane toggle missing');
must(css.includes('main[data-workspace-mode="lineage"]'),'lineage shell css missing');
must(!/main\[data-workspace-mode="lineage"\][^{]*#side-pane-toggle\s*\{[^}]*display\s*:\s*none/i.test(css),'lineage must not hide shared side-pane toggle');
must(/main\[data-workspace-mode="lineage"\][\s\S]{0,220}grid-template-columns\s*:\s*minmax\([^;]+var\(--side-width\)/.test(css),'lineage grid must use the resizable --side-width variable');
must(css.includes('main.side-collapsed[data-workspace-mode="lineage"]'),'lineage collapsed side-panel optics missing');
must(js.includes('lineage') && js.includes('side-collapsed'),'lineage side-panel shell integration missing');
console.log('PASS lineage side panel resize/collapse contract');
