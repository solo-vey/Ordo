
const fs=require("fs");
const html=fs.readFileSync("web/index.html","utf8");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");

for(const token of [
  'data-state="idle"',
  'live-scroll-working-dots',
  'LIVE_SCROLL_TO_BOTTOM_THRESHOLD_PX=100',
  'liveTranscriptRemainingPx',
  'liveModelIsWorking',
  'button.dataset.state=working?"working":"idle"',
  'MutationObserver(()=>updateLiveScrollToBottomControl())'
]) if(!(html.includes(token)||js.includes(token))) throw new Error("missing "+token);

for(const token of [
  '.live-scroll-working-dots',
  '[data-state="working"] .live-scroll-arrow',
  '@keyframes live-scroll-working-wave'
]) if(!css.includes(token)) throw new Error("missing css "+token);

if(js.includes('remaining>24')) throw new Error("old 24px threshold still present");
console.log("PASS scroll-to-latest 100px threshold + working wave contract");
