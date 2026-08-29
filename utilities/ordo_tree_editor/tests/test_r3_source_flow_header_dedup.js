const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8'),js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m);}
must(!html.includes('id="source-flow-summary"'),'lower Source Data Flow metadata row must not duplicate page counters');
must(js.includes('pageSummary=document.querySelector("#lineage-summary")'),'page-level Data Flow counters must remain populated');
must(js.includes('if(pageSummary){const q=data?.summary||{}'),'rendering must write counters only to the page header');
console.log('PASS Source Data Flow header counter de-dup regression');
