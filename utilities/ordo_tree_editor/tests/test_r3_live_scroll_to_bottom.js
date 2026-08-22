
const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

for(const token of [
  'id="live-scroll-to-bottom"',
  'aria-label="Scroll to latest message"'
]) if(!html.includes(token)) throw new Error("missing html "+token);

for(const token of [
  'liveTranscriptCanScrollDown',
  'updateLiveScrollToBottomControl',
  'scrollLiveTranscriptToBottom',
  'scrollHeight-transcript.clientHeight-transcript.scrollTop',
  'addEventListener("scroll",updateLiveScrollToBottomControl',
  'addEventListener("click",()=>scrollLiveTranscriptToBottom("smooth"))',
  'form.offsetHeight+12'
]) if(!js.includes(token)) throw new Error("missing js "+token);

for(const token of [
  '.live-scroll-to-bottom',
  'position:absolute',
  'left:50%',
  'border-radius:50%',
  '.live-scroll-to-bottom[hidden]'
]) if(!css.includes(token)) throw new Error("missing css "+token);

console.log("PASS Execute Playbook scroll-to-latest control contract");
