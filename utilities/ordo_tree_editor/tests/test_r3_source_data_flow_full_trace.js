const fs=require('fs');
const vm=require('vm');
const js=fs.readFileSync('web/app.js','utf8');

function extractFunction(name){
  const start=js.indexOf(`function ${name}(`);
  if(start<0) throw new Error(`missing function ${name}`);
  const brace=js.indexOf('{',start);
  let depth=0,end=-1;
  for(let i=brace;i<js.length;i++){
    if(js[i]==='{') depth++;
    else if(js[i]==='}') { depth--; if(depth===0){end=i+1;break;} }
  }
  if(end<0) throw new Error(`unterminated function ${name}`);
  return js.slice(start,end);
}
const sandbox={};
vm.createContext(sandbox);
vm.runInContext(extractFunction('sourceFlowDirectionalTrace'),sandbox);
const graph={
  nodes:['A','B','C','D','X','Y','U','V'].map(id=>({id})),
  edges:[
    {from:'A',to:'B',type:'derived'},
    {from:'X',to:'B',type:'derived'},
    {from:'B',to:'C',type:'derived'},
    {from:'C',to:'D',type:'artifact_input'},
    {from:'C',to:'Y',type:'validation'},
    {from:'U',to:'V',type:'derived'},
    {from:'V',to:'C',type:'invisible'}
  ]
};
const trace=sandbox.sourceFlowDirectionalTrace(graph,'C');
const arr=s=>Array.from(s).sort();
const assertEq=(actual,expected,label)=>{
  const a=JSON.stringify(actual),e=JSON.stringify(expected);
  if(a!==e) throw new Error(`${label}: ${a} != ${e}`);
};
assertEq(arr(trace.upstream),['A','B','C','X'],'full upstream');
assertEq(arr(trace.downstream),['C','D','Y'],'full downstream');
assertEq(arr(trace.visible),['A','B','C','D','X','Y'],'full through-node path');
if(trace.visible.has('U')||trace.visible.has('V')) throw new Error('unrelated/invisible-only nodes must not be highlighted');
if(!js.includes('sourceFlowDirectionalTrace(graph,state.lineage.sourceFocusRoot)')) throw new Error('rendering must use full directional trace');
if(!js.includes('source-flow-upstream')||!js.includes('source-flow-downstream')) throw new Error('rendering must distinguish upstream/downstream optics');
console.log('PASS full transitive Source Data Flow trace contract');
