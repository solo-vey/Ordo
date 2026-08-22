const fs=require('fs');
const js=fs.readFileSync(__dirname+'/../web/app.js','utf8');
const css=fs.readFileSync(__dirname+'/../web/styles.css','utf8');
function must(v,msg){if(!v) throw new Error(msg)}
must(js.includes("live-artifact-card live-artifact-card-download-only"),'non-preview artifact must use file card');
must(js.includes("artifactTypeLabel(item.artifact.path)"),'non-preview card type label missing');
must(!js.includes('link.textContent=`Download ${filename}`'),'legacy blue/text download renderer must be removed');
must(css.includes('.live-artifact-card-download-only { cursor:default; }'),'download-only card must not look clickable');
must(js.includes('aria-label="Download file"'),'download icon accessibility label missing');
console.log('PASS R3 non-preview artifact card');
