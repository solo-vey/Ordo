const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'web', 'app.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'web', 'index.html'), 'utf8');
function assert(cond, msg) { if (!cond) throw new Error(msg); }
assert(html.includes('id="live-pause"'), 'runtime pause control missing');
assert(html.includes('id="chat-pause-proxy"'), 'top control-bar pause proxy missing');
assert(html.includes('id="chat-state-proxy"') && html.includes('id="chat-auto-answers-proxy"'), 'state/auto-answer controls must be in top bar');
assert(app.includes('Pause is a manual-answer override, not a hard execution stop.'), 'manual-answer pause semantics missing');
assert(app.includes('if (state.livePaused) return;') && app.includes('const replayAnswer = nextGuidedReplayAnswer(id);') && app.includes('replayAnswer || nextLiveAutoAnswer(id)'), 'pause must suppress replay/auto-answer at waiting boundary');
assert(!app.includes('if (state.livePaused) return;\n    if (++guard'), 'pause must not block enter traversal');
assert(app.includes('if (!result.waiting && result.nextId && !state.liveStopRequested) await advanceLiveUntilInput();'), 'manual response must continue to next enter while paused');
assert(app.includes('if (state.liveAwaitingInput) {') && app.includes('replayAnswer || nextLiveAutoAnswer(id)'), 'resume must consume current waiting replay/auto-answer without re-enter');
assert(app.includes('pauseButton.textContent=state.livePaused ? "Resume Auto" : "Pause";'), 'top pause proxy must reflect pause state');
console.log('manual pause UI regression: PASS');
