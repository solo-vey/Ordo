const fs=require('fs'); const assert=require('assert');
const app=fs.readFileSync(__dirname+'/../web/app.js','utf8');
const css=fs.readFileSync(__dirname+'/../styles.css','utf8');
for (const token of ['templateResourcePreview','data-resource-preview-index','Resource Preview','Preview file','template-resource-inline-preview','template-resource-preview-close']) assert(app.includes(token),token);
for (const token of ['.template-reference-card.is-clickable','.template-resource-inline-preview','.template-resource-preview-body']) assert(css.includes(token),token);
console.log('PASS inline resource preview UI contract');
for (const token of ['margin-top:22px','padding-top:18px','border-top:1px solid #d0d5dd']) assert(css.includes(token),token);
