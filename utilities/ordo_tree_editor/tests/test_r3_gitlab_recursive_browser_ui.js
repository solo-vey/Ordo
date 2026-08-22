const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const html=fs.readFileSync(path.join(root,'web/index.html'),'utf8');
const css=fs.readFileSync(path.join(root,'web/styles.css'),'utf8');
function must(v,m){if(!v)throw new Error(m);}
must(js.includes('function renderGitLabDirectory(node,depth=0)'), 'GitLab UI must render recursive directory nodes');
must(js.includes('for(const child of node.children||[])body.append(renderGitLabDirectory(child,depth+1));'), 'GitLab UI must recurse through all returned directory depths');
must(js.includes('download.textContent="Download"'), 'ZIP rows must expose a separate Download action');
must(js.includes('/api/gitlab-archive?root_url='), 'ZIP download must use the binary archive endpoint');
must(js.includes('openGitLabReadme(node.readme,node.name||"")'), 'directory README button must open README preview');
must(js.includes('renderBasicMarkdown(data.content||"")'), 'README preview must render Markdown');
must(html.includes('id="gitlab-readme-modal"'), 'README preview modal must exist');
must(html.includes('data-gitlab-readme-close'), 'README preview must expose close controls');
must(css.includes('.gitlab-archive-row'), 'ZIP load/download row styling must exist');
console.log('PASS recursive GitLab browser/download/README UI regression');
