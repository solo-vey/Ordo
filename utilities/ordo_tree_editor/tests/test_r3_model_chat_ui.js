const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
for(const token of ['data-workspace-tab="modelchat"','id="model-chat-main-panel"','id="model-chat-preview-panel"','id="model-chat-file-input"']) if(!html.includes(token)) throw new Error('missing '+token);
for(const token of ['/api/model-chat','/api/model-chat-playbook-preview','openModelChatPlaybookPreview','renderModelChatPreview','bindModelChat']) if(!js.includes(token)) throw new Error('missing '+token);
for(const token of ['main[data-workspace-mode="modelchat"]','.model-chat-file-card','.model-chat-preview-node']) if(!css.includes(token)) throw new Error('missing '+token);
console.log('PASS Model Chat UI + playbook preview contract');
