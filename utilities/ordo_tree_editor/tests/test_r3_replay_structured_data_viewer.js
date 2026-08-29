const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'function replayStructuredSummary(value)',
  'function replayAddJsonDetails(host,label,value)',
  'summaryTab.textContent="Summary"',
  'jsonTab.textContent="JSON"',
  'copy.textContent="Copy JSON"',
  'JSON.stringify(value,null,2)',
  'replay-structured-table',
  'replay-structured-row'
]) must(js.includes(token),`missing structured replay viewer contract: ${token}`);
for(const token of ['.replay-structured-tabs','.replay-structured-table','.replay-json-copy','.replay-structured-pane.json-pane']) must(css.includes(token),`missing structured replay viewer CSS: ${token}`);
console.log('PASS Replay structured Summary/JSON viewer regression');
