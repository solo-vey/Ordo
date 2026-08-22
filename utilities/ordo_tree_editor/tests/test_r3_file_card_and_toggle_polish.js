const fs=require('fs'), path=require('path');
const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'web','app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'web','styles.css'),'utf8');
function must(h,n,m){if(!h.includes(n)) throw new Error(m||n)}
must(js,'editorMain.classList.remove("side-collapsed")','preview must reveal collapsed side pane');
must(js,"card.innerHTML=`<span class=\"live-artifact-card-icon\"",'markdown card markup missing');
must(js,"card.querySelector('.live-artifact-card-download')",'download must live inside markdown card');
must(js,"artifactWrap.append(card);",'markdown card should be appended as one unit');
must(js,"Show more <span aria-hidden=\"true\">⌄</span>",'neutral show-more chevron missing');
must(css,'.live-artifact-card-download { display:grid','download icon-button style missing');
must(css,'.live-message-toggle { display:inline-flex','toggle neutral style missing');
console.log('PASS R3 file-card preview and transcript-toggle polish');
