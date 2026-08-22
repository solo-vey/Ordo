const fs=require('fs'), path=require('path');
const root=path.resolve(__dirname,'..','web');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const js=fs.readFileSync(path.join(root,'app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
function must(x,m){if(!x) throw new Error(m)}
must(html.includes('id="settings-overview-modal"'),'first-level settings overview modal');
must(html.includes('id="live-setting-modal"'),'second-level model configuration modal');
must(js.includes('renderSettingsOverview'),'settings overview renderer');
must(js.includes('Configure model'),'model configure action in overview');
must(js.includes('Load Playbook ZIP'),'playbook action in overview');
must(js.includes('Auto Answers'),'auto answers status in overview');
must(js.includes('Replay to Checkpoint'),'replay status in overview');
must(!js.includes('addUnifiedSettingsExtras'),'old flat unified settings removed');
must(css.includes('.settings-overview-modal'),'overview styles');
console.log('PASS alpha.20.0.26 two-level settings UI contract');
