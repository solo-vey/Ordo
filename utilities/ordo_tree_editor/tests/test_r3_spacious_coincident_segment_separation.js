const fs=require('fs'), vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v) throw new Error(m);}
for(const token of [
  'function spaciousEdgePortOffset',
  'function spaciousHorizontalOverlap',
  'function spaciousInternalMiniLaneOffsets',
  'const offsets = [0, 7, -7, 14, -14, 21, -21, 28, -28, 35, -35];',
  'reserved.some(other => spaciousHorizontalOverlap(segment, other))',
  'const miniLaneOffset = spaciousInternalMiniLaneOffsets().get(`${sourceId}->${targetId}`) || 0;',
  'spaciousEdgePortOffset(sourceId, sourceId, targetId, "source")',
  'spaciousEdgePortOffset(targetId, sourceId, targetId, "target")'
]) must(js.includes(token), `missing coincident-segment separation contract: ${token}`);

const overlapMatch=js.match(/function spaciousHorizontalOverlap\(a, b, clearance = 5\) \{[\s\S]*?\n\}/);
must(overlapMatch,'horizontal overlap helper must be extractable');
const sandbox={}; vm.createContext(sandbox);
vm.runInContext(overlapMatch[0]+'\nthis.overlap=spaciousHorizontalOverlap;',sandbox);
must(sandbox.overlap({y:100,minX:10,maxX:200},{y:100,minX:150,maxX:260})===true,'partial coincident horizontal segments must be detected');
must(sandbox.overlap({y:100,minX:10,maxX:200},{y:107,minX:150,maxX:260})===false,'mini-lane vertical separation must make overlapping spans visually distinct');
must(sandbox.overlap({y:100,minX:10,maxX:100},{y:100,minX:120,maxX:260})===false,'non-overlapping spans must not be separated unnecessarily');
console.log('PASS Spacious coincident-segment separation regression');
