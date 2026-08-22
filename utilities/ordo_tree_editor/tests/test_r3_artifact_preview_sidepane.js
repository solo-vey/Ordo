const fs=require('fs'), path=require('path');
const root=path.resolve(__dirname,'..','web');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const js=fs.readFileSync(path.join(root,'app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
function must(h,n,m){if(!h.includes(n)) throw new Error(m||`missing ${n}`)}
const workspaceClose=html.indexOf('</section>', html.indexOf('id="workspace"'));
const preview=html.indexOf('id="artifact-preview-panel"');
if(preview < workspaceClose) throw new Error('artifact preview must be outside scrollable #workspace');
must(css,'.artifact-preview-panel { grid-area:side; position:relative','preview must occupy stable side-pane grid area');
must(js,"editorMain.classList.add('artifact-preview-open')",'open state class missing');
must(js,'editorMain.classList.remove("artifact-preview-open")','close state class missing');
must(js,"card.addEventListener('click',()=>openArtifactPreview(item.artifact))",'card click preview handler missing');
must(js,'<svg viewBox="0 0 24 24"','neutral svg download icon missing');
must(css,'.live-artifact-card-download svg { width:18px; height:18px; fill:none; stroke:currentColor; stroke-width:1.7','compact neutral download icon style missing');
if(css.includes('.artifact-preview-icon { color:#1677ff')) throw new Error('blue artifact preview icon must be removed');
console.log('PASS R3 artifact preview stable side pane and neutral download icon');
