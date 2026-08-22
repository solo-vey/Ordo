const fs = require('fs');
const path = require('path');

const css = fs.readFileSync(path.join(__dirname, '..', 'web', 'styles.css'), 'utf8');

function mustContain(x) {
  if (!css.includes(x)) {
    console.error('missing:', x);
    process.exit(1);
  }
}
mustContain('scrollbar-color: rgba(15, 23, 42, 0.34) transparent');
mustContain('::-webkit-scrollbar-track');
mustContain('background: transparent');
mustContain('::-webkit-scrollbar-thumb');
console.log('PASS transparent scrollbar tracks');
