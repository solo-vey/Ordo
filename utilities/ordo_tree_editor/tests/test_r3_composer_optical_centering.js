
const fs=require("fs");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of [
  '.live-composer-shell[data-composer-mode="single"]',
  'padding-top:8px',
  'padding-bottom:8px',
  '.live-composer-shell[data-composer-mode="single"] .live-attach-button',
  '.live-composer-shell[data-composer-mode="single"] .live-send-button',
  'align-self:center'
]) if(!css.includes(token)) throw new Error("missing "+token);
console.log("PASS single-line composer optical centering contract");
