const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const js=fs.readFileSync('web/app.js','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
for(const token of [
  'id="package-files-splitter"',
  'role="separator"',
  'id="package-file-discuss"',
  'Discuss with model',
  'id="settings-assistant-close"'
]) must(html.includes(token),`missing Package Files splitter/discuss UI: ${token}`);
for(const token of [
  'function applyPackageFilesTreeWidth',
  'async function openPackageFileDiscussion()',
  "document.querySelector('#package-file-discuss')?.addEventListener('click',openPackageFileDiscussion)",
  "packageFilesAssistantOpen=true;editorMain.classList.add('package-files-chat-open')",
  'function settingsAssistantInPackageFiles()',
  'function settingsAssistantResourcePath()'
]) must(js.includes(token),`missing Package Files splitter/discuss behavior: ${token}`);
for(const token of [
  '.package-files-splitter{',
  'cursor:col-resize',
  'main.package-files-chat-open[data-workspace-mode="packagefiles"]',
  '.package-file-preview-document{max-width:900px;margin:0 auto}',
  '.package-file-preview-body.markdown{max-width:none;'
]) must(css.includes(token),`missing Package Files splitter/discuss CSS: ${token}`);
console.log('PASS Package Files splitter + file assistant regression');
