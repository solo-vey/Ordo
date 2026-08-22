const fs=require('fs'), path=require('path');
const root=path.join(__dirname,'..','web');
const js=fs.readFileSync(path.join(root,'app.js'),'utf8');
const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
function must(h,n,m){if(!h.includes(n))throw new Error(m||`missing ${n}`)}
for(const token of [
  'function attachChatCopyButton(',
  'function copyTextToClipboard(',
  'attachChatCopyButton(block, text, item.role === "analyst" ? "right" : "left")',
  'attachChatCopyButton(el, msg.content || "", msg.role === "user" ? "right" : "left")',
  'attachChatCopyButton(el, msg.content || "", msg.role === "user" ? "right" : "left")'
]) must(js,token);
// Model Chat plus three assistant side chats use the shared helper too.
const count=(js.match(/attachChatCopyButton\(el, msg\.content \|\| "", msg\.role === "user" \? "right" : "left"\)/g)||[]).length;
if(count<4) throw new Error(`expected shared copy helper in Model Chat + settings + lineage + verification; got ${count}`);
for(const token of [
  '.chat-message-copy',
  '.chat-copy-host',
  '.chat-copy-host.copy-align-right .chat-message-copy',
  'width:18px',
  'height:18px'
]) must(css,token);
if(!js.includes('navigator.clipboard.writeText')) throw new Error('clipboard API missing');
if(!js.includes('document.execCommand("copy")')) throw new Error('clipboard fallback missing');
console.log('PASS shared chat message copy button contract');
