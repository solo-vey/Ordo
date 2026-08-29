const fs=require('fs');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  '.package-files-layout{--package-tree-width:34%;flex:1;min-height:0;overflow:hidden;',
  'grid-template-rows:minmax(0,1fr)',
  '.package-file-preview{min-width:0;min-height:0;height:100%;max-height:100%;overflow:hidden;',
  '.package-file-preview-content,#package-file-preview-content{flex:1 1 0;min-height:0;height:0;overflow:hidden;',
  '.package-file-preview-body{flex:1 1 0;min-height:0;height:0;max-height:100%;width:100%;overflow-x:auto;overflow-y:scroll;',
  'overscroll-behavior:contain',
  'scrollbar-gutter:stable'
]) must(css.includes(token),`missing Package Files preview scroll contract: ${token}`);
console.log('PASS Package Files preview vertical-scroll regression');
