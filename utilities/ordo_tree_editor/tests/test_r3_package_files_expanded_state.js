const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'let packageFilesExpandedDirs=new Set();',
  'data-package-dir-path=',
  "if(details.open)packageFilesExpandedDirs.add(path);else packageFilesExpandedDirs.delete(path);",
  "host?.querySelectorAll('.package-file-row.active').forEach(row=>row.classList.remove('active'))",
  'selected?.classList.add(\'active\')',
  'packageFilesExpandedDirs=new Set();'
]) must(js.includes(token),`missing Package Files expanded-state contract: ${token}`);
const openStart=js.indexOf('async function openPackageFile(path){');
const openEnd=js.indexOf('async function renderPackageFiles()',openStart);
must(openStart>=0&&openEnd>openStart,'openPackageFile block must be extractable');
const openBlock=js.slice(openStart,openEnd);
must(!openBlock.includes('renderPackageFilesTree();'),'opening a file must not rerender/collapse the tree');
console.log('PASS Package Files expanded directory state regression');
