const fs=require('fs'), path=require('path');
const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
function must(v,m){if(!v) throw new Error(m);}
must(js.includes('const activeMode={inspection:"tree",dialog:"paths",replay:"replay",run:"chat",help:"help"}[state.panelTab] || "tree";'), 'workspace shell must restore mode from panelTab after source load');
must(js.includes('editorMain.dataset.workspaceMode=activeMode;'), 'workspace shell must commit restored mode');
must(css.includes('main[data-workspace-mode="replay"] #inspector, main[data-workspace-mode="chat"] #inspector { grid-area: primary;'), 'chat must place inspector/chat in primary left pane');
must(css.includes('main[data-workspace-mode="replay"] #workspace, main[data-workspace-mode="chat"] #workspace { grid-area: side;'), 'chat must place tree workspace in right side pane');
console.log('R3 initial Execute Playbook layout regression PASS');
