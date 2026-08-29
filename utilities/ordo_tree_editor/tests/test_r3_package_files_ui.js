const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'data-workspace-tab="packagefiles">Package Files',
  'id="package-files-uncovered"',
  'id="package-files-all"',
  'id="package-files-search"',
  'id="package-files-tree"',
  'id="package-file-preview-body"',
  'id="package-file-download"'
]) must(html.includes(token),`missing Package Files UI: ${token}`);
for(const token of [
  'async function renderPackageFiles()',
  "request('/api/package-files'",
  'packageFilesMode=\'uncovered\'',
  'function packageFilesTreeModel',
  'function renderPackageFilePreview',
  '/api/package-file-download?package_id=',
  'if (tab === "packagefiles") renderPackageFiles();'
]) must(js.includes(token),`missing Package Files behavior: ${token}`);
must(css.includes('main[data-workspace-mode="packagefiles"]'),'Package Files needs standalone workspace layout');
must(css.includes('.package-file-coverage.uncovered'),'coverage badges must visually expose Uncovered files');
console.log('PASS Package Files UI regression');
