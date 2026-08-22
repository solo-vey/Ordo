const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root,'web','index.html'),'utf8');
const js = fs.readFileSync(path.join(root,'web','app.js'),'utf8');
const css = fs.readFileSync(path.join(root,'web','styles.css'),'utf8');
function req(ok,msg){ if(!ok){ console.error('FAIL:',msg); process.exit(1); } }
req(html.includes('id="chat-token-usage"'), 'aggregate token badge exists in active chat control bar');
req(html.indexOf('id="chat-token-usage"') < html.indexOf('id="chat-stop-proxy"'), 'token badge is before Stop');
req(js.includes('openTokenDebugModal(buildAggregateTokenDebug())'), 'aggregate token badge opens existing debug inspector');
req(js.includes('state.liveUsage.total_tokens'), 'badge renders aggregate total tokens');
req(css.includes('main[data-workspace-mode="chat"] #live-transcript { flex:1 1 auto; min-height:0; overflow-y:auto'), 'transcript is the scrolling flex region');
req(css.includes('main[data-workspace-mode="chat"] .live-input-form { flex:0 0 auto; position:static'), 'composer is a fixed flex footer instead of transcript sticky content');
req(css.includes('main[data-workspace-mode="chat"] #run-panel { height:100%; min-height:0; display:flex; flex-direction:column; overflow:hidden; }'), 'chat panel fills available viewport height');
req(html.includes('data-token-debug-tab="summary"') && html.includes('data-token-debug-tab="input"') && html.includes('data-token-debug-tab="output"') && html.includes('data-token-debug-tab="runtime"'), 'debug modal retains all four tabs');
req(html.includes('id="token-debug-download"'), 'debug JSON download remains available');
console.log('PASS alpha.20.0.27 chat layout + aggregate token/debug UI contract');
