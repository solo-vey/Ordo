const fs = require('fs');
const path = require('path');
const css = fs.readFileSync(path.join(__dirname, '..', 'web', 'styles.css'), 'utf8');

for (const token of [
  'padding-right: 92px',
  'gap: 10px',
  'width: 34px',
  'height: 34px',
  'width: 18px',
  'height: 18px'
]) {
  if (!css.includes(token)) {
    console.error('missing', token);
    process.exit(1);
  }
}
console.log('PASS preview header alignment');
