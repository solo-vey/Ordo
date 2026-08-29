const fs=require('fs'), path=require('path');
const root=path.join(__dirname,'..','web');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const js=fs.readFileSync(path.join(root,'app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
function must(hay,needle,msg){ if(!hay.includes(needle)) throw new Error(msg||`missing ${needle}`); }
const tabSeq=['data-workspace-tab="upload">Upload Playbook','data-workspace-tab="tree">Show Tree','data-workspace-tab="lineage">Show Data Flow','data-workspace-tab="settings">Playbook Settings','data-workspace-tab="verification">Verify Playbook','data-workspace-tab="packagefiles">Package Files','data-workspace-tab="paths">Show Path','data-workspace-tab="chat">Execute Playbook','data-workspace-tab="replay">Replay Real Chat','data-workspace-tab="modelchat">Model Chat','data-workspace-tab="help">Help'];
let pos=-1; for(const x of tabSeq){const n=html.indexOf(x); if(n<=pos) throw new Error('workspace tab order/labels invalid'); pos=n;}
for(const id of ['chat-state-proxy','chat-pause-proxy','chat-auto-answers-proxy','tree-zoom-out','tree-zoom-reset','tree-zoom-in']) must(html,id);
must(html,'live-composer-shell'); must(html,'aria-label="Attach files"'); must(html,'aria-label="Send"');
must(css,'.live-message.live-analyst'); must(css,'align-self:flex-end'); must(css,'.live-model-activity'); must(css,'@keyframes ordo-shimmer'); must(css,'.live-send-button.is-stop');
must(css,'.recovery-clarification-scope label'); must(css,'.tree-zoom-controls');
if(css.includes('\\n')) throw new Error('stylesheet contains escaped newline serialization artifacts');
must(js,'showPanelTab("run");','playbook load must activate Execute Playbook');
if(js.includes('if (state.liveConfig.enabled) showPanelTab("run");')) throw new Error('playbook load must not conditionally remain on tree');
must(js,'input.disabled = !state.liveRunning || !!state.liveOutcome;','input must remain editable while model works');
must(js,'send.classList.add("is-stop")','send must morph to stop');
must(js,'if (state.liveBusy) return; const input = document.querySelector("#live-input")','busy submit must preserve typed draft');
must(js,'if (state.liveBusy || event.target.disabled','Enter must not submit while model works');
must(js,'state.liveStepAbortController.abort()','current fetch must be aborted');
must(js,'No partial state was committed','interruption contract must be explicit');
must(js,'function uiText(uk,en) { return en; }','system UI must be English');
console.log('PASS R3 ChatGPT-style UI redesign contract');
