const fs=require('fs');
const html=fs.readFileSync('web/index.html','utf8');
const css=fs.readFileSync('web/styles.css','utf8');
function must(v,m){if(!v)throw new Error(m);}
must(html.includes('id="package-file-preview-content" class="package-file-preview-content" hidden'),'preview content must carry the CSS class that defines the constrained flex container');
must(css.includes('.package-file-preview-content,#package-file-preview-content{flex:1 1 0;min-height:0;height:0;overflow:hidden;display:flex;flex-direction:column}'),'preview content must be height-constrained by both class and id fallback');
must(css.includes('.package-file-preview-body{flex:1 1 0;min-height:0;height:0;max-height:100%;width:100%;overflow-x:auto;overflow-y:scroll;'),'preview body must own vertical scrolling inside the constrained preview pane');
console.log('PASS Package Files preview DOM/CSS scroll contract');
