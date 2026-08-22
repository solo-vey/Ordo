const fs=require('fs');
const js=fs.readFileSync(require('path').join(__dirname,'../web/app.js'),'utf8');
for (const needle of ['const stateLineage = trace.flatMap','const artifactLineage = trace.flatMap','run_journal: {state_lineage:stateLineage, artifact_lineage:artifactLineage}']) {
  if (!js.includes(needle)) throw new Error('missing '+needle);
}
console.log('PASS R2-D03 aggregate run journal');
