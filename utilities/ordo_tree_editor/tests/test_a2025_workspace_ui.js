const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..','web');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const js=fs.readFileSync(path.join(root,'app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
function must(cond,msg){ if(!cond){ console.error('FAIL:',msg); process.exit(1);} }
for (const tab of ['tree','paths','replay','chat']) must(html.includes(`data-workspace-tab="${tab}"`),`workspace tab ${tab}`);
must(!html.includes('data-workspace-tab="validate"'),'Validate must not be a workspace tab');
must(html.includes('id="side-pane-toggle"'),'side pane collapse toggle');
must(html.includes('id="dialog-start-node"') && html.includes('id="dialog-end-node"'),'path range selectors');
must(html.includes('id="chat-settings"'),'chat Settings button');
must(html.includes('Parameters</button>') && html.includes('>YAML</button>'),'read-only inspector view tabs');
must(css.includes('#node-tooltip { display:none !important; }'),'node hover tooltip disabled');
must(css.includes('.node-toolbar') && css.includes('display:none !important'),'node authoring toolbar hidden');
must(js.includes('field.readOnly=true'),'node parameter fields read-only');
must(js.includes('state.panelTab !== "dialog"'),'context menu limited to Paths');
must(js.includes('openUnifiedSettings'),'unified settings dialog');
console.log('PASS alpha.20.0.25 workspace UI static contract');
