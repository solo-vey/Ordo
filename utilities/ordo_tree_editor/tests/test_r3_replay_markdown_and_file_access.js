const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'body.innerHTML=renderBasicMarkdown(event.text||"")',
  'body.innerHTML=renderBasicMarkdown(stepData.prompt)',
  'function replayFileAccessCode(row)',
  'return read&&write?"RW":read?"R":write?"W":"—"',
  'label:"Access"',
  'label:"File size"',
  'label:"Read bytes"',
  'label:"Written bytes"',
  'File size is metadata and must not be interpreted as bytes read.'
]) must(js.includes(token),`missing replay markdown/file-access contract: ${token}`);
for(const token of ['.replay-event-markdown','.replay-observed-files-table','.replay-access-code']) must(css.includes(token),`missing replay markdown/file-access CSS: ${token}`);
console.log('PASS Replay Markdown + compact file-access regression');
