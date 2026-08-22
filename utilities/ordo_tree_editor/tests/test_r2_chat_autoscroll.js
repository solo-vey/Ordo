const fs = require('fs');
const path = require('path');
const app = fs.readFileSync(path.join(__dirname, '..', 'web', 'app.js'), 'utf8');
function must(cond, msg) { if (!cond) throw new Error(msg); }
const start = app.indexOf('function scrollLiveLatestAboveComposer');
const end = app.indexOf('function scheduleLiveTranscriptScroll', start);
must(start >= 0 && end > start, 'autoscroll function must exist');
const body = app.slice(start, end);
must(body.includes('transcript.scrollTo'), 'autoscroll must scroll #live-transcript');
must(!body.includes('inspector.scrollTo'), 'autoscroll must not scroll #inspector in chat mode');
must(body.includes('transcript.scrollTop'), 'autoscroll must use transcript scroll position');
console.log('R2 chat autoscroll regression PASS');
