
const fs=require("fs");
const js=fs.readFileSync("web/app.js","utf8");
const css=fs.readFileSync("web/styles.css","utf8");
for(const token of ["verificationSkippedLabel","Needs runtime evidence","Needs selected gate","Release-only","skip_label:item.skip_label"]) if(!js.includes(token)) throw new Error("missing "+token);
for(const token of [".verification-status.SKIPPED","padding-top:14px","padding-bottom:14px"]) if(!css.includes(token)) throw new Error("missing css "+token);
console.log("PASS skipped subtype + balanced composer UI contract");
