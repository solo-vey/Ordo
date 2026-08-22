const fs=require('fs'), path=require('path');
const root=path.resolve(__dirname,'..');
const js=fs.readFileSync(path.join(root,'web/app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'web/styles.css'),'utf8');
function must(v,m){if(!v) throw new Error(m);}
must(js.includes('loadedDirectories:{}'), 'GitLab state must keep a lazy directory cache');
must(js.includes('request("/api/gitlab-directory",{root_url:gitLabRootUrl(),path:node.path})'), 'opening a directory must fetch only that directory');
must(js.includes('box.addEventListener("toggle",()=>{if(box.open&&!node.loaded)loadGitLabDirectoryNode'), 'directory disclosure must trigger lazy loading');
must(js.includes('Reading first GitLab directory level…'), 'initial status must describe shallow loading');
must(js.includes('Open a directory to load its contents.'), 'catalog status must explain lazy navigation');
must(js.includes('state.gitlab.loadedDirectories[node.path]'), 'loaded directories must be cached');
must(css.includes('.gitlab-loading-spinner'), 'lazy directory load must show a spinner');
must(css.includes('@keyframes gitlab-spin'), 'spinner animation must exist');
console.log('PASS GitLab lazy browser UI regression');
