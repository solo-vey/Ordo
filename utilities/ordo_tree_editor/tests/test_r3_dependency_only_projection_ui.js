const fs = require('fs');
const vm = require('vm');
const path = require('path');
const appPath = path.join(__dirname, '..', 'web', 'app.js');
const app = fs.readFileSync(appPath, 'utf8');

function extractFunction(source, name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  if (start < 0) throw new Error(`missing ${name}`);
  const bodyStart = source.indexOf('{', start);
  let depth = 0;
  for (let i = bodyStart; i < source.length; i++) {
    if (source[i] === '{') depth++;
    else if (source[i] === '}') {
      depth--;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

const fn = extractFunction(app, 'automaticPositions');
const context = {
  state: {
    graph: {
      nodes: [
        {id:'START', element_type:'node'},
        {id:'WORK', element_type:'node'},
        {id:'END', element_type:'terminal'},
        {id:'DEP_GATE', element_type:'gate'},
        {id:'UNATTACHED_GATE', element_type:'gate'},
      ],
      edges: [
        {source:'START', target:'WORK', edge_type:'control_flow'},
        {source:'WORK', target:'END', edge_type:'control_flow'},
        {source:'WORK', target:'DEP_GATE', edge_type:'validation_dependency'},
      ],
    },
    source: { graph_contract: { entry_node: 'START' } },
    nodeSizes: {},
  },
  workspace: {clientWidth: 1000},
  NODE_WIDTH:205, NODE_MIN_HEIGHT:88, HORIZONTAL_GAP:55, VERTICAL_GAP:70, CANVAS_MARGIN:42,
  nodeHeight: () => 88,
  entryNodeId: () => 'START',
  console,
};
vm.createContext(context);
vm.runInContext(`${fn}; result = automaticPositions();`, context);
const p = context.result;
if (!(p.START.y < p.WORK.y && p.WORK.y < p.END.y)) throw new Error('control-flow spine order changed');
if (!(p.DEP_GATE.x > p.END.x)) throw new Error('dependency-only gate must be in side overlay lane');
if (!(p.DEP_GATE.y < p.END.y)) throw new Error('dependency-only gate must not be appended after terminal');
if (!(p.UNATTACHED_GATE.x > p.END.x)) throw new Error('unattached projection entity must stay in diagnostic side lane');
if (!(p.UNATTACHED_GATE.y < p.END.y)) throw new Error('unattached projection entity must not appear below terminal by default');
if (!app.includes('relation === "control_flow"')) throw new Error('layout must explicitly classify control flow');
console.log('PASS test_r3_dependency_only_projection_ui');
