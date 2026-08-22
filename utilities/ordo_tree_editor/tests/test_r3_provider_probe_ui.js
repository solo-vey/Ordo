const fs=require('fs'),path=require('path');
const app=fs.readFileSync(path.join(__dirname,'..','web','app.js'),'utf8');
function must(c,m){if(!c){console.error('FAIL:',m);process.exit(1)}}
must(app.includes('Probe JSON schema capability'),'probe control must be exposed');
must(app.includes('/api/provider-capability-probe'),'UI must call capability probe endpoint');
must(app.includes('provider_capability_profile: state.liveConfig.capability_profile || null'),'evidence summary must carry probe profile');
console.log('PASS test_r3_provider_probe_ui');
