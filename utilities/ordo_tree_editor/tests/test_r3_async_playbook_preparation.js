const fs=require('fs');
const js=fs.readFileSync('utilities/ordo_tree_editor/web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m);}
must(js.includes('async function waitForPlaybookPreparation(runId)'), 'async preparation polling helper missing');
must(js.includes('request("/api/playbook-package-start"'), 'Upload Playbook must use async start endpoint');
must(js.includes('request("/api/playbook-package-status"'), 'Upload Playbook must poll status endpoint');
must(!/package-file-input[\s\S]{0,500}request\("\/api\/playbook-package"/.test(js), 'local upload must not use the long synchronous package endpoint');
console.log('PASS async Upload Playbook preparation contract');
must(js.includes('playbook-preparation-progress-value'), 'visible preparation percentage missing');
must(js.includes('playbook-preparation-elapsed'), 'elapsed preparation time missing');
must(js.includes('PLAYBOOK_PREPARATION_STAGE_LABELS'), 'granular stage labels missing');
must(js.includes('status.stages'), 'frontend must render backend-reported stages');
must(js.includes('This subprocess does not expose an internal percentage'), 'long subprocess heartbeat explanation missing');
console.log('PASS granular Upload Playbook preparation progress');
