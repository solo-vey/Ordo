const liveSessionId = (() => {
  const key = "ordo_tree_editor_live_session";
  let value = localStorage.getItem(key);
  if (!value) { value = crypto.randomUUID ? crypto.randomUUID() : `session-${Date.now()}-${Math.random().toString(16).slice(2)}`; localStorage.setItem(key, value); }
  return value;
})();
const state = { source: null, graph: null, positions: {}, nodeSizes: {}, manualPositions: new Set(), selected: null, selectedNodes: new Set(), selectedEdge: null, pendingTransitionSource: null, inspectorTab: "fields", panelTab: "upload", canvasMenuPosition: null, marqueeStart: null, dialogPath: null, dialogFocusId: null, dialogPlayMode: false, dialogPlaying: false, dialogVisibleCount: null, dialogDelay: 2, dialogAdvanceMode: "manual", dialogAutoPassGates: true, dialogTimer: null, dialogAsyncToken: 0, dialogSyncTimer: null, collapsedNodes: new Set(), replayData: null, replayFocusId: null, replaySyncTimer: null, liveConfig: { enabled: false, provider: "openai", base_url: "https://api.openai.com/v1", model: "gpt-5.6-terra", shared_key: false, personal_key: false, capability_profile: null, structured_output_mode: "auto", semantic_fallback_policy: "automatic_safe", models: ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"] }, packageInfo: null, liveRunId: "", liveRunning: false, livePaused: false, liveStopRequested: false, liveCurrentId: null, liveState: {}, liveRevision: 0, liveHistory: [], livePath: [], liveBusy: false, liveStepAbortController: null, liveInterruptedNode: null, liveAwaitingInput: false, liveOutcome: null, liveDebugTrace: [], liveUsage: { input_tokens: 0, output_tokens: 0, total_tokens: 0, cached_tokens: 0, reasoning_tokens: 0, calls: 0 }, liveAutoAnswers: { enabled: false, filename: "", answersByNode: {}, cursors: {}, total: 0 }, liveGuidedReplay: { enabled:false, active:false, filename:"", checkpointId:"", recordedCalls:[], callCursor:0, answersByNode:{}, answerCursors:{}, totalCalls:0, totalAnswers:0 }, liveAttachments: [], liveExpandedMessages: new Set(), liveComposerExpanded: false, liveChoiceContext: null, liveRecoveryDiagnoses: {}, liveAnalystOverride: null, pendingRecoveryClarification: null, liveNoProgressGateFailures: {}, livePendingEntryMode: null, liveTreeAutoFocusId: null, interactionContract: {locale:"uk-UA",model_output_language:"uk"}, templateInspectorData:null, templateResourcePreview:null, nodeExplanations:{}, resourceExplanations:{}, explanationBusy:null, verification:{catalog:[],runId:"",running:false,checks:[],progress:0,summary:null,pollTimer:null,lastResult:null,explanations:{},explanationBusy:null,assistantCheck:null,assistantMessages:[],assistantBusy:false}, lineage:{viewMode:"source",data:null,loading:false,selected:null,focusRoot:null,messages:[],busy:false,zoom:1,layoutMode:"auto",filterMode:"all",positions:{},worldWidth:0,worldHeight:0,drag:null,pan:null,sourceData:null,sourceLoading:false,sourceError:null,sourceSelected:null,sourceFocusRoot:null,sourceZoom:1,sourceLayoutMode:"auto",sourcePositions:{},sourceWorldWidth:0,sourceWorldHeight:0,sourceDrag:null,sourcePan:null,sourceDataClassFilter:"all",sourceLegend:null,sourceTraceDirection:null,assistantThreads:{}}, gitlab:{root:"",catalog:null,loading:false,error:"",loadedDirectories:{}}, treeLayoutDensity:"normal", modelChat:{messages:[],attachments:[],busy:false,sessionId:liveSessionId,abortController:null,preview:null,agentTrace:[],usageHistory:[],errors:[],generatedFiles:[],activeRunId:null,activityBuffer:[],activitySeq:0} };
const canvas = document.querySelector("#canvas"), edges = document.querySelector("#edges");
const empty = document.querySelector("#empty-state"), form = document.querySelector("#node-form");
const workspace = document.querySelector("#workspace"), editorMain = document.querySelector("main"), inspectorResizer = document.querySelector("#inspector-resizer");
const directFileOpen = location.protocol === "file:";
const nodeTooltip = document.createElement("div");
nodeTooltip.id = "node-tooltip";
nodeTooltip.hidden = true;
nodeTooltip.setAttribute("role", "tooltip");
document.body.append(nodeTooltip);
if (directFileOpen) {
  document.querySelector("#launch-warning").hidden = false;
  document.querySelector("header").hidden = true;
  document.querySelector("main").hidden = true;
}
async function request(path, payload, options = {}) {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: options.signal });
  const data = await response.json(); if (!response.ok) throw new Error(data.error || "Request failed."); return data;
}
function uniqueId(base) { const ids = new Set((state.graph?.nodes || []).map(item => item.id)); let id = base, number = 1; while (ids.has(id)) id = `${base}_${number++}`; return id; }
function sourceRecord(id) { return [...(state.source?.nodes || []), ...(state.source?.gates || [])].find(record => record.id === id); }
function selectedRecord() { return sourceRecord(state.selected); }
function selectedView() { return (state.graph?.nodes || []).find(item => item.id === state.selected); }

function graphNodeView(id) { return (state.graph?.nodes || []).find(item => item.id === id); }
function knownGraphIds() { return new Set((state.graph?.nodes || []).map(item => item.id)); }
const GRAPH_RESOURCE_PATH_RE = /(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)+\.(?:py|md|markdown|json|ya?ml|txt|html?|css|js|mjs|cjs|ts|tsx|jsx|xml|csv|sql|sh|toml|ini|cfg))(?![A-Za-z0-9_.-])/gi;
const GRAPH_REFERENCE_TYPE_ORDER = ["py", "yaml", "md", "json", "other"];
function classifyGraphReferenceType(pathValue) {
  const text = String(pathValue || "").trim().toLowerCase();
  if (/\.py$/.test(text)) return "py";
  if (/\.(?:yaml|yml)$/.test(text)) return "yaml";
  if (/\.(?:md|markdown)$/.test(text)) return "md";
  if (/\.json$/.test(text)) return "json";
  return "other";
}
function graphReferenceTypeLabel(type) {
  return ({py:"Py", yaml:"YAML", md:"MD", json:"JSON", other:"FILE"})[type] || "FILE";
}
function discoverGraphRecordReferences(record) {
  const discovered = [];
  const seen = new Set();
  const add = (pathValue) => {
    const clean = String(pathValue || "").trim().replace(/^[`"']+|[`"']+$/g, "");
    if (!clean || seen.has(clean)) return;
    seen.add(clean);
    discovered.push(clean);
  };
  const walk = (value) => {
    if (Array.isArray(value)) { value.forEach(walk); return; }
    if (value && typeof value === "object") { Object.values(value).forEach(walk); return; }
    if (typeof value !== "string") return;
    const text = value.trim();
    if (GRAPH_RESOURCE_PATH_RE.test(text) && GRAPH_RESOURCE_PATH_RE.lastIndex === text.length) {
      GRAPH_RESOURCE_PATH_RE.lastIndex = 0;
      add(text);
      return;
    }
    GRAPH_RESOURCE_PATH_RE.lastIndex = 0;
    for (const match of value.matchAll(GRAPH_RESOURCE_PATH_RE)) add(match[1]);
    GRAPH_RESOURCE_PATH_RE.lastIndex = 0;
  };
  walk(record);
  return discovered;
}
function graphReferenceBadgesForNode(node) {
  if (!node || node.element_type === "terminal") return [];
  const refs=Array.isArray(node.resource_references)?node.resource_references:[];
  const grouped=new Map();
  for(const ref of refs){const type=classifyGraphReferenceType(ref);const bucket=grouped.get(type)||[];bucket.push(ref);grouped.set(type,bucket);}
  return GRAPH_REFERENCE_TYPE_ORDER.filter(type=>grouped.has(type)).map(type=>({type,label:graphReferenceTypeLabel(type),refs:grouped.get(type)||[],count:(grouped.get(type)||[]).length}));
}

function collectKnownTargets(value, known, out = []) {
  if (typeof value === "string") {
    if (!value.startsWith("$") && known.has(value)) out.push(value);
    return out;
  }
  if (Array.isArray(value)) { value.forEach(item => collectKnownTargets(item, known, out)); return out; }
  if (value && typeof value === "object") Object.values(value).forEach(item => collectKnownTargets(item, known, out));
  return out;
}
function dialogStructuralEdges() {
  const known = knownGraphIds(), edgesByKey = new Map();
  for (const edge of state.graph?.edges || []) {
    if (edge.edge_type && edge.edge_type !== "control_flow") continue;
    if (!known.has(edge.source) || !known.has(edge.target)) continue;
    const key = `${edge.source}\u0000${edge.target}\u0000${edge.storage || ""}\u0000${edge.key || ""}`;
    edgesByKey.set(key, { ...edge, dynamic: false });
  }
  for (const record of [...(state.source?.nodes || []), ...(state.source?.gates || [])]) {
    if (!record?.id || !known.has(record.id) || !record.declared_dynamic_routes || typeof record.declared_dynamic_routes !== "object") continue;
    for (const [routeName, route] of Object.entries(record.declared_dynamic_routes)) {
      for (const target of [...new Set(collectKnownTargets(route, known))]) {
        const key = `${record.id}\u0000${target}\u0000declared_dynamic_routes\u0000${routeName}`;
        edgesByKey.set(key, { source: record.id, target, storage: "declared_dynamic_routes", key: routeName, dynamic: true });
      }
    }
  }
  return [...edgesByKey.values()];
}
function isGatePassEdge(edge) {
  return edge?.storage === "gate_route" && ["on_pass", "pass_to", "pass"].includes(String(edge.key || "").toLowerCase());
}
function isGateFailEdge(edge) {
  return edge?.storage === "gate_route" && ["on_fail", "fail_to", "fail"].includes(String(edge.key || "").toLowerCase());
}
function dialogEdgePreference(edge) {
  if (isGatePassEdge(edge)) return 0;
  if (isGateFailEdge(edge)) return 2;
  return 1;
}
function shortestDialogPath(startId, endId) {
  if (!startId || !endId) return null;
  if (startId === endId) return { nodes: [startId], edges: [] };
  const adjacency = new Map();
  for (const edge of dialogStructuralEdges()) {
    if (!adjacency.has(edge.source)) adjacency.set(edge.source, []);
    adjacency.get(edge.source).push(edge);
  }
  for (const list of adjacency.values()) list.sort((a, b) => dialogEdgePreference(a) - dialogEdgePreference(b));

  // Prefer successful gate outcomes before failure outcomes, even when the
  // successful route is a little longer. A fail route is used only when a
  // pass-preferred path to the requested destination does not exist.
  const frontier = [{ id: startId, failCount: 0, steps: 0 }];
  const best = new Map([[startId, { failCount: 0, steps: 0 }]]);
  const previous = new Map();
  const better = (a, b) => !b || a.failCount < b.failCount || (a.failCount === b.failCount && a.steps < b.steps);
  while (frontier.length) {
    frontier.sort((a, b) => a.failCount - b.failCount || a.steps - b.steps);
    const current = frontier.shift();
    const known = best.get(current.id);
    if (!known || known.failCount !== current.failCount || known.steps !== current.steps) continue;
    if (current.id === endId) break;
    for (const edge of adjacency.get(current.id) || []) {
      const candidate = { failCount: current.failCount + (isGateFailEdge(edge) ? 1 : 0), steps: current.steps + 1 };
      if (!better(candidate, best.get(edge.target))) continue;
      best.set(edge.target, candidate);
      previous.set(edge.target, { from: current.id, edge });
      frontier.push({ id: edge.target, ...candidate });
    }
  }
  if (!best.has(endId)) return null;
  const nodes = [endId], pathEdges = []; let walk = endId;
  while (walk !== startId) {
    const step = previous.get(walk); if (!step) return null;
    pathEdges.push(step.edge); walk = step.from; nodes.push(walk);
  }
  nodes.reverse(); pathEdges.reverse(); return { nodes, edges: pathEdges };
}

function dialogOutgoingEdges(nodeId) {
  const seen = new Set();
  return dialogStructuralEdges().filter(edge => edge.source === nodeId).filter(edge => {
    const key = `${edge.target}\u0000${dialogRouteLabel(edge)}`;
    if (seen.has(key)) return false;
    seen.add(key); return true;
  });
}
function pathFromChosenEdge(prefixNodes, prefixEdges, edge, desiredEndId) {
  const nodes = [...prefixNodes, edge.target], edges = [...prefixEdges, edge];
  if (!desiredEndId || edge.target === desiredEndId) return { nodes, edges, endId: edge.target };
  const tail = shortestDialogPath(edge.target, desiredEndId);
  if (tail) return { nodes: [...nodes, ...tail.nodes.slice(1)], edges: [...edges, ...tail.edges], endId: desiredEndId };
  const fallback = reachableTerminalPaths(edge.target)[0];
  if (!fallback) return { nodes, edges, endId: edge.target, fallback: true };
  return { nodes: [...nodes, ...fallback.path.nodes.slice(1)], edges: [...edges, ...fallback.path.edges], endId: fallback.terminal.id, fallback: true };
}
function clearDialogPlaybackTimer() {
  state.dialogAsyncToken += 1;
  if (state.dialogTimer) clearTimeout(state.dialogTimer);
  state.dialogTimer = null;
}
function centerDialogPlaybackNode(id) {
  const pos = state.positions?.[id]; if (!pos) return;
  state.dialogFocusId = id;
  render();
  requestAnimationFrame(() => {
    workspace.scrollTo({
      left: Math.max(0, pos.x + NODE_WIDTH / 2 - workspace.clientWidth / 2),
      top: Math.max(0, pos.y + nodeHeight(id) / 2 - workspace.clientHeight / 2),
      behavior: "smooth",
    });
  });
}
function dialogCurrentPlaybackIndex() {
  if (!state.dialogPath) return -1;
  const count = state.dialogPlayMode ? Math.max(1, Math.min(state.dialogVisibleCount || 1, state.dialogPath.nodes.length)) : state.dialogPath.nodes.length;
  return count - 1;
}
function scrollDialogPlaybackToLatest() {
  if (!state.dialogPlayMode || state.panelTab !== "dialog") return;
  requestAnimationFrame(() => {
    const inspector = document.querySelector("#inspector");
    const transcript = document.querySelector("#dialog-transcript");
    const latest = transcript?.querySelector(".dialog-step:last-child");
    if (!inspector || !latest) return;
    const inspectorRect = inspector.getBoundingClientRect();
    const latestRect = latest.getBoundingClientRect();
    const bottomPadding = 24;
    if (latestRect.bottom > inspectorRect.bottom - bottomPadding || latestRect.top < inspectorRect.top) {
      const delta = latestRect.bottom - inspectorRect.bottom + bottomPadding;
      inspector.scrollTo({ top: Math.max(0, inspector.scrollTop + delta), behavior: "smooth" });
    }
  });
}
function advanceDialogPlaybackAfterCurrent() {
  if (!state.dialogPlayMode || !state.dialogPlaying || !state.dialogPath) return;
  const index = dialogCurrentPlaybackIndex();
  if (index < 0 || index >= state.dialogPath.nodes.length - 1) { state.dialogPlaying = false; renderDialog(); return; }
  const currentId = state.dialogPath.nodes[index];
  const currentView = graphNodeView(currentId);
  const choices = dialogOutgoingEdges(currentId);
  const autoPassEdge = state.dialogAutoPassGates && currentView?.element_type === "gate" ? choices.find(isGatePassEdge) : null;
  if (choices.length > 1 && !autoPassEdge) { state.dialogPlaying = false; renderDialog(); scrollDialogPlaybackToLatest(); return; }
  if (autoPassEdge) {
    const activeEdge = state.dialogPath.edges[index];
    const samePass = activeEdge && activeEdge.source === autoPassEdge.source && activeEdge.target === autoPassEdge.target && dialogRouteLabel(activeEdge) === dialogRouteLabel(autoPassEdge);
    if (!samePass) { switchDialogBranch(index, autoPassEdge); return; }
  }
  state.dialogVisibleCount = Math.min(state.dialogPath.nodes.length, (state.dialogVisibleCount || 1) + 1);
  const nextId = state.dialogPath.nodes[state.dialogVisibleCount - 1];
  state.dialogFocusId = nextId;
  render(); renderDialog(); centerDialogPlaybackNode(nextId); scrollDialogPlaybackToLatest();
  scheduleDialogPlayback();
}
function scheduleDialogPlayback() {
  clearDialogPlaybackTimer();
  if (!state.dialogPlayMode || !state.dialogPlaying || !state.dialogPath) return;
  const index = dialogCurrentPlaybackIndex();
  if (index < 0) return;
  const currentId = state.dialogPath.nodes[index];
  if (state.dialogAdvanceMode === "manual") return;
  const token = state.dialogAsyncToken;
  state.dialogTimer = setTimeout(() => {
    if (token !== state.dialogAsyncToken) return;
    state.dialogTimer = null;
    advanceDialogPlaybackAfterCurrent();
  }, Math.max(1, Number(state.dialogDelay) || 2) * 1000);
}
function startDialogPlayback(restart = false) {
  if (!state.dialogPath) return;
  clearDialogPlaybackTimer();
 
  if (restart || !state.dialogPlayMode) state.dialogVisibleCount = 1;
  state.dialogPlayMode = true; state.dialogPlaying = true;
  const id = state.dialogPath.nodes[Math.max(0, (state.dialogVisibleCount || 1) - 1)];
  state.dialogFocusId = id; render(); renderDialog(); centerDialogPlaybackNode(id); scrollDialogPlaybackToLatest(); scheduleDialogPlayback();
}
function pauseDialogPlayback() { clearDialogPlaybackTimer(); state.dialogPlaying = false; renderDialog(); }
function passDialogPlaybackStep() {
  if (!state.dialogPlayMode || !state.dialogPath) return;
  const index = dialogCurrentPlaybackIndex();
  if (index < 0 || index >= state.dialogPath.nodes.length - 1) return;
  const wasPlaying = state.dialogPlaying;
  clearDialogPlaybackTimer();
 
  if (!state.dialogPlaying) state.dialogPlaying = true;
  advanceDialogPlaybackAfterCurrent();
  if (!wasPlaying && state.dialogPlaying) {
    clearDialogPlaybackTimer();
   
    state.dialogPlaying = false;
    renderDialog();
    scrollDialogPlaybackToLatest();
  }
}
function showFullDialog() { clearDialogPlaybackTimer(); state.dialogPlayMode = false; state.dialogPlaying = false; state.dialogVisibleCount = state.dialogPath?.nodes.length || null; render(); renderDialog(); }
function switchDialogBranch(stepIndex, chosenEdge) {
  if (!state.dialogPath) return;
  clearDialogPlaybackTimer();
 
  const wasPlayback = state.dialogPlayMode;
  const prefixNodes = state.dialogPath.nodes.slice(0, stepIndex + 1);
  const prefixEdges = state.dialogPath.edges.slice(0, stepIndex);
  const desiredEndId = state.dialogPath.requestedEndId || state.dialogPath.endId || state.dialogPath.nodes.at(-1);
  const next = pathFromChosenEdge(prefixNodes, prefixEdges, chosenEdge, desiredEndId);
  state.dialogPath = {
    ...state.dialogPath,
    nodes: next.nodes, edges: next.edges, endId: next.endId,
    branchFallback: !!next.fallback,
  };
  if (wasPlayback) {
    state.dialogPlayMode = true;
    state.dialogVisibleCount = Math.min(next.nodes.length, stepIndex + 2);
    state.dialogPlaying = state.dialogVisibleCount < next.nodes.length;
    state.dialogFocusId = next.nodes[Math.min(next.nodes.length - 1, stepIndex + 1)];
  } else state.dialogFocusId = chosenEdge.source;
  render(); renderDialog();
  if (wasPlayback) { centerDialogPlaybackNode(state.dialogFocusId); scrollDialogPlaybackToLatest(); scheduleDialogPlayback(); }
}
function dialogTargetDisplayLabel(targetId) {
  const view = graphNodeView(targetId);
  const record = sourceRecord(targetId);
  let value;
  if (view?.element_type === "gate") {
    value = record?.title || record?.purpose || record?.condition || record?.description || record?.summary || record?.question || record?.prompt || record?.instruction || record?.propose || record?.proposal || record?.display_name || record?.name || record?.label || record?.specification || record?.validator || record?.method || record?.type || record?.kind || view?.label;
  } else if (view?.terminal) {
    value = record?.title || record?.purpose || record?.description || record?.summary || view?.label;
  } else {
    value = dialogQuestion(record, view);
  }
  const text = String(value || "").trim();
  if (text && text !== String(targetId || "").trim()) return text;
  return view?.terminal ? "Terminal outcome" : view?.element_type === "gate" ? "Gate" : "Next step";
}
function attachDialogTargetTip(button, targetId) {
  if (!button || !targetId) return;
  const tip = document.createElement("span");
  tip.className = "dialog-target-tip";
  tip.setAttribute("role", "tooltip");
  tip.textContent = dialogTargetDisplayLabel(targetId);
  button.append(tip);
}

function renderDialogBranchChoices(step, nodeId, stepIndex, activeEdge) {
  const choices = dialogOutgoingEdges(nodeId);
  if (choices.length < 2) return;
  const wrap = document.createElement("div"); wrap.className = "dialog-branch-choices";
  const caption = document.createElement("div"); caption.className = "dialog-branch-caption"; caption.textContent = "Alternative path at this step"; wrap.append(caption);
  const buttons = document.createElement("div"); buttons.className = "dialog-branch-buttons";
  choices.forEach(edge => {
    const button = document.createElement("button"); button.type = "button"; button.className = "dialog-branch-button";
    const same = activeEdge && activeEdge.source === edge.source && activeEdge.target === edge.target && dialogRouteLabel(activeEdge) === dialogRouteLabel(edge);
    if (same) button.classList.add("active");
    button.textContent = `${dialogRouteLabel(edge)} → ${edge.target}`;
    button.setAttribute("aria-label", `${dialogRouteLabel(edge)} to ${dialogTargetDisplayLabel(edge.target)}`);
    attachDialogTargetTip(button, edge.target);
    button.addEventListener("click", () => switchDialogBranch(stepIndex, edge));
    buttons.append(button);
  });
  wrap.append(buttons); step.append(wrap);
}

function renderDialogManualNext(step, nodeId, stepIndex) {
  if (state.dialogAdvanceMode !== "manual" || !state.dialogPlayMode || !state.dialogPlaying || !state.dialogPath) return;
  const currentIndex = dialogCurrentPlaybackIndex();
  if (stepIndex !== currentIndex || stepIndex >= state.dialogPath.nodes.length - 1) return;
  const choices = dialogOutgoingEdges(nodeId);
  if (choices.length > 1) return;
  const activeEdge = state.dialogPath.edges[stepIndex];
  if (!activeEdge) return;
  const wrap = document.createElement("div"); wrap.className = "dialog-branch-choices dialog-manual-next";
  const caption = document.createElement("div"); caption.className = "dialog-branch-caption"; caption.textContent = "Continue"; wrap.append(caption);
  const buttons = document.createElement("div"); buttons.className = "dialog-branch-buttons";
  const button = document.createElement("button"); button.type = "button"; button.className = "dialog-branch-button dialog-next-button";
  button.textContent = "Next";
  button.setAttribute("aria-label", `Continue to ${dialogTargetDisplayLabel(activeEdge.target)}`);
  attachDialogTargetTip(button, activeEdge.target);
  button.addEventListener("click", passDialogPlaybackStep);
  buttons.append(button); wrap.append(buttons); step.append(wrap);
}

function reachableTerminalPaths(startId) {
  return (state.graph?.nodes || [])
    .filter(item => item.terminal)
    .map(item => ({ terminal: item, path: shortestDialogPath(startId, item.id) }))
    .filter(item => item.path)
    .sort((a, b) => a.path.nodes.length - b.path.nodes.length || a.terminal.id.localeCompare(b.terminal.id));
}
function dialogQuestion(record, view) {
  return record?.title || record?.question || record?.purpose || record?.description || record?.summary || record?.prompt || record?.instruction || record?.propose || record?.proposal || view?.label || record?.action || record?.type || record?.kind || view?.id || "Step";
}
function possibleAnswers(record) {
  const answers = [];
  const branch = record?.on_answer?.branch;
  if (branch && typeof branch === "object" && !Array.isArray(branch)) answers.push(...Object.keys(branch));
  if (record?.answer_type) answers.push(`answer type: ${record.answer_type}`);
  return [...new Set(answers)];
}
function dialogRouteLabel(edge) {
  if (!edge) return "";
  if (edge.storage === "declared_dynamic_routes") return `dynamic route: ${edge.key}`;
  if (edge.storage === "gate_route") return `gate outcome: ${edge.key}`;
  if (edge.storage === "on_answer") return `answer outcome: ${edge.key}`;
  if (edge.storage === "transitions" || edge.storage === "transitions_list") return `transition: ${edge.key}`;
  if (edge.storage === "on_answer_next" || edge.storage === "next") return "next";
  return edge.key || edge.storage || "transition";
}
function dialogIdButton(id) {
  const button = document.createElement("button"); button.type = "button"; button.className = "dialog-node-link"; button.textContent = id;
  button.addEventListener("click", () => focusGraphElement(id, true)); return button;
}

function updateDialogFocusVisuals(id) {
  if (!id) return;
  state.dialogFocusId = id;
  canvas.querySelectorAll('.node.dialog-current-node').forEach(el => el.classList.remove('dialog-current-node'));
  const graphEl = canvas.querySelector(`.node[data-id="${CSS.escape(id)}"]`);
  if (graphEl) graphEl.classList.add('dialog-current-node');
  document.querySelectorAll('#dialog-transcript .dialog-step.dialog-sync-current').forEach(el => el.classList.remove('dialog-sync-current'));
  const step = document.querySelector(`#dialog-transcript .dialog-step[data-node-id="${CSS.escape(id)}"]`);
  if (step) step.classList.add('dialog-sync-current');
}
function scrollDialogToNode(id, behavior = 'smooth') {
  if (state.panelTab !== 'dialog' || !state.dialogPath?.nodes.includes(id)) return;
  const inspector = document.querySelector('#inspector');
  const step = document.querySelector(`#dialog-transcript .dialog-step[data-node-id="${CSS.escape(id)}"]`);
  if (!inspector || !step) return;
  updateDialogFocusVisuals(id);
  const inspectorRect = inspector.getBoundingClientRect();
  const stepRect = step.getBoundingClientRect();
  const controls = document.querySelector('.dialog-playback-controls');
  const stickyOffset = controls?.getBoundingClientRect().height || 0;
  const target = inspector.scrollTop + (stepRect.top - inspectorRect.top) - Math.max(16, stickyOffset + 14);
  inspector.scrollTo({ top: Math.max(0, target), behavior });
}
function syncDialogFromWorkspaceScroll() {
  if (state.panelTab !== 'dialog' || !state.dialogPath || state.dialogPlaying) return;
  const visibleIds = dialogVisiblePathNodes();
  if (!visibleIds.length) return;
  const cx = workspace.scrollLeft + workspace.clientWidth / 2;
  const cy = workspace.scrollTop + workspace.clientHeight / 2;
  let bestId = null, bestDistance = Infinity;
  for (const id of visibleIds) {
    const pos = state.positions?.[id]; if (!pos) continue;
    const dx = pos.x + NODE_WIDTH / 2 - cx;
    const dy = pos.y + nodeHeight(id) / 2 - cy;
    const distance = dx * dx + dy * dy;
    if (distance < bestDistance) { bestDistance = distance; bestId = id; }
  }
  if (bestId && bestId !== state.dialogFocusId) scrollDialogToNode(bestId, 'smooth');
}
function renderDialog() {
  const emptyState = document.querySelector("#dialog-empty"), view = document.querySelector("#dialog-view"), header = document.querySelector("#dialog-header"), transcript = document.querySelector("#dialog-transcript");
  if (!state.dialogPath) { emptyState.hidden = false; view.hidden = true; return; }
  emptyState.hidden = true; view.hidden = false; header.innerHTML = ""; transcript.innerHTML = "";
  const title = document.createElement("strong"); title.textContent = state.dialogPath.title; header.append(title);
  const visibleCount = state.dialogPlayMode ? Math.max(1, Math.min(state.dialogVisibleCount || 1, state.dialogPath.nodes.length)) : state.dialogPath.nodes.length;
  const modeLabel = state.dialogAdvanceMode === "timer" ? `timer ${state.dialogDelay || 2}s` : "manual";
  const meta = document.createElement("span"); meta.textContent = `${visibleCount}/${state.dialogPath.nodes.length} elements · ${state.dialogPlayMode ? (state.dialogPlaying ? `playing · ${modeLabel}` : `playback paused · ${modeLabel}`) : "structural path preview"}${state.dialogPath.branchFallback ? " · selected branch cannot reach original ending; showing nearest reachable outcome" : ""}`; header.append(meta);
  const playToggle = document.querySelector("#dialog-play-toggle"), restart = document.querySelector("#dialog-restart"), staticButton = document.querySelector("#dialog-static"), mode = document.querySelector("#dialog-advance-mode"), delayWrap = document.querySelector("#dialog-delay-wrap"), delay = document.querySelector("#dialog-delay");
  if (playToggle) { playToggle.textContent = state.dialogPlayMode && state.dialogPlaying ? "Pause" : "Play"; playToggle.classList.toggle("active", state.dialogPlayMode); }
  if (restart) restart.disabled = !state.dialogPath;
  if (mode) mode.value = state.dialogAdvanceMode || "manual";
  if (delayWrap) delayWrap.hidden = state.dialogAdvanceMode !== "timer";
  if (delay) delay.value = String(state.dialogDelay || 2);
  if (staticButton) staticButton.classList.toggle("active", !state.dialogPlayMode);
  state.dialogPath.nodes.slice(0, visibleCount).forEach((id, index) => {
    const graphView = graphNodeView(id), record = sourceRecord(id), outgoing = state.dialogPath.edges[index];
    const step = document.createElement("section"); step.className = `dialog-step replay-step dialog-kind-${graphView?.element_type || "terminal"}`; step.dataset.nodeId = id; if (state.dialogFocusId === id) step.classList.add("dialog-sync-current");
    if (state.dialogPlayMode && index === visibleCount - 1) step.classList.add("play-current");
    const stepHead = document.createElement("div"); stepHead.className = "dialog-step-head replay-step-head"; stepHead.append(dialogIdButton(id));
    const type = document.createElement("span"); type.textContent = graphView?.element_type || "terminal"; stepHead.append(type); step.append(stepHead);
    if (graphView?.element_type === "gate") {
      const bubble = document.createElement("div"); bubble.className = "replay-bubble gate";
      bubble.innerHTML = `<strong>Gate</strong><div>${String(record?.title || record?.purpose || record?.condition || record?.description || record?.summary || graphView?.label || id)}</div>`;
      step.append(bubble);
    } else if (graphView?.terminal) {
      const bubble = document.createElement("div"); bubble.className = "replay-bubble system";
      bubble.innerHTML = `<strong>Outcome</strong><div>${String(record?.title || record?.purpose || graphView?.label || id)}</div>`;
      step.append(bubble);
    } else {
      const assistant = document.createElement("div"); assistant.className = "replay-bubble assistant";
      const role = document.createElement("strong"); role.textContent = "Assistant"; assistant.append(role);
      const q = document.createElement("div"); q.textContent = dialogQuestion(record, graphView); assistant.append(q); step.append(assistant);
      const analyst = document.createElement("div"); analyst.className = "replay-bubble analyst";
      const analystRole = document.createElement("strong"); analystRole.textContent = "Analyst"; analyst.append(analystRole);
      const answers = possibleAnswers(record);
      const response = document.createElement("div"); response.textContent = answers.length ? `Possible response: ${answers.join(" · ")}` : "Analyst response / confirmation according to this node contract."; analyst.append(response); step.append(analyst);
    }
    if (outgoing) {
      const tech = document.createElement("div"); tech.className = "dialog-transition";
      tech.textContent = `${dialogRouteLabel(outgoing)} → ${outgoing.target}${outgoing.dynamic ? " (declared runtime possibility)" : ""}`; step.append(tech);
    }
    renderDialogBranchChoices(step, id, index, outgoing);
    renderDialogManualNext(step, id, index);
    if (state.dialogPlayMode && index === visibleCount - 1 && dialogOutgoingEdges(id).length > 1 && index < state.dialogPath.nodes.length - 1) {
      const view = graphNodeView(id);
      const autoPassAvailable = state.dialogAutoPassGates && view?.element_type === "gate" && dialogOutgoingEdges(id).some(isGatePassEdge);
      if (!autoPassAvailable) {
        const waiting = document.createElement("div"); waiting.className = "dialog-play-waiting"; waiting.textContent = "Playback is waiting for your branch choice."; step.append(waiting);
      }
    }
    transcript.append(step);
  });
}
function openDialogPath(path, title, requestedEndId = null) {
  if (!path) return alert("No structural path was found for this dialog preview.");
  clearDialogPlaybackTimer();
  state.dialogPath = { ...path, title, requestedEndId: requestedEndId || path.nodes.at(-1), endId: path.nodes.at(-1), branchFallback: false };
  state.dialogPlayMode = false; state.dialogPlaying = false; state.dialogVisibleCount = path.nodes.length;
  state.dialogFocusId = path.nodes[0] || null;
  state.panelTab = "dialog"; hideCanvasContextMenu(); render(); showPanelTab("dialog"); renderDialog();
}
function openEntryToNodeDialog(nodeId) {
  const path = shortestDialogPath(entryNodeId(), nodeId);
  openDialogPath(path, `Start → ${nodeId}`, nodeId);
  state.dialogFocusId = nodeId; syncPathBuilder(entryNodeId(), nodeId); render();
}
function openNodeToTerminalDialog(nodeId, terminalId) {
  const path = shortestDialogPath(nodeId, terminalId);
  openDialogPath(path, `${nodeId} → ${terminalId}`, terminalId);
  state.dialogFocusId = nodeId; syncPathBuilder(nodeId, terminalId); render();
}

function focusGraphElement(id, preserveDialog = false) {
  const view = (state.graph?.nodes || []).find(item => item.id === id);
  const pos = state.positions?.[id];
  if (!view || !pos) return;
  state.selected = id;
  state.selectedNodes = new Set([id]);
  state.selectedEdge = null;
  if (preserveDialog && state.dialogPath) {
    state.dialogFocusId = id;
    state.panelTab = "dialog";
  } else {
    state.panelTab = "inspection";
  }
  render();
  requestAnimationFrame(() => {
    const targetLeft = Math.max(0, pos.x + NODE_WIDTH / 2 - workspace.clientWidth / 2);
    const targetTop = Math.max(0, pos.y + nodeHeight(id) / 2 - workspace.clientHeight / 2);
    workspace.scrollTo({ left: targetLeft, top: targetTop, behavior: "smooth" });
    const element = canvas.querySelector(`.node[data-id="${CSS.escape(id)}"]`);
    if (element) {
      element.classList.remove("validation-focus");
      void element.offsetWidth;
      element.classList.add("validation-focus");
      setTimeout(() => element.classList.remove("validation-focus"), 1800);
    }
  });
}
const NODE_WIDTH = 205, NODE_MIN_HEIGHT = 88, HORIZONTAL_GAP = 55, VERTICAL_GAP = 70, CANVAS_MARGIN = 42;
function treeLayoutMetrics() {
  const density = state.treeLayoutDensity || "normal";
  const presets = {
    compact: { horizontalGap: 40, verticalGap: 52, margin: 34, overlayGapY: 22, producerGapX: 28, producerGapY: 18, pathGapY: 96, branchGapX: 96, minCanvasWidth: 980, minPrimaryWidth: 720 },
    normal: { horizontalGap: HORIZONTAL_GAP, verticalGap: VERTICAL_GAP, margin: CANVAS_MARGIN, overlayGapY: 28, producerGapX: 34, producerGapY: 20, pathGapY: 115, branchGapX: 115, minCanvasWidth: 1050, minPrimaryWidth: 760 },
    spacious: { horizontalGap: 78, verticalGap: 112, margin: 150, overlayGapY: 40, producerGapX: 46, producerGapY: 28, pathGapY: 154, branchGapX: 154, minCanvasWidth: 1240, minPrimaryWidth: 900 },
  };
  return presets[density] || presets.normal;
}
function nodeSize(id) { return state.nodeSizes[id] || { width: NODE_WIDTH, height: NODE_MIN_HEIGHT }; }
function nodeHeight(id) { return nodeSize(id).height; }
function measureNodeSizes() {
  const next = {};
  canvas.querySelectorAll('.node[data-id]').forEach(element => {
    next[element.dataset.id] = { width: element.offsetWidth || NODE_WIDTH, height: Math.max(NODE_MIN_HEIGHT, element.offsetHeight || NODE_MIN_HEIGHT) };
  });
  state.nodeSizes = next;
}
function applyMeasuredLayout() {
  measureNodeSizes();
  const automatic = automaticPositions();
  // Keep the same focus layout after real DOM node heights are measured.
  // Previously this second layout pass only reapplied Dialog layout, which
  // silently replaced Replay focus coordinates with the ordinary/manual
  // layout immediately after render().
  const dialogLayout = dialogFocusPositions();
  const replayLayout = replayFocusPositions();
  const liveLayout = liveFocusPositions();
  const focusLayout = dialogLayout || replayLayout || liveLayout;
  for (const node of state.graph?.nodes || []) {
    const pos = focusLayout?.[node.id] || (state.manualPositions.has(node.id) ? state.positions[node.id] : automatic[node.id]);
    if (!pos) continue;
    state.positions[node.id] = pos;
    const element = canvas.querySelector(`.node[data-id="${CSS.escape(node.id)}"]`);
    if (element) { element.style.left = `${pos.x}px`; element.style.top = `${pos.y}px`; }
  }
}
function entryNodeId() { return state.source?.graph_contract?.entry_node || state.source?.playbook?.entry_node || state.graph?.nodes?.find(item => item.element_type === "node")?.id; }
function smartSpaciousOrderedGroups(groups, levels, nodes, edges) {
  const ordered = new Map([...groups.entries()].map(([level, ids]) => [level, [...ids]]));
  if ((state.treeLayoutDensity || "normal") !== "spacious" || ordered.size < 2) return ordered;
  const controlEdges = (edges || []).filter(edge => (edge.edge_type || edge.relation_type || "control_flow") === "control_flow" && levels.has(edge.source) && levels.has(edge.target));
  const incoming = new Map(nodes.map(node => [node.id, []]));
  const outgoing = new Map(nodes.map(node => [node.id, []]));
  for (const edge of controlEdges) {
    incoming.get(edge.target)?.push(edge.source);
    outgoing.get(edge.source)?.push(edge.target);
  }
  const originalRank = new Map(nodes.map((node, index) => [node.id, index]));
  const sortedLevels = [...ordered.keys()].sort((a, b) => a - b);
  const rankMap = () => {
    const ranks = new Map();
    for (const level of sortedLevels) (ordered.get(level) || []).forEach((id, index) => ranks.set(id, index));
    return ranks;
  };
  const reorder = (level, neighborMap, ranks) => {
    const ids = ordered.get(level) || [];
    const scored = ids.map((id, currentIndex) => {
      const neighbors = (neighborMap.get(id) || []).filter(other => ranks.has(other));
      const score = neighbors.length ? neighbors.reduce((sum, other) => sum + ranks.get(other), 0) / neighbors.length : currentIndex;
      return { id, score, currentIndex, original: originalRank.get(id) ?? Number.MAX_SAFE_INTEGER };
    });
    scored.sort((a, b) => a.score - b.score || a.currentIndex - b.currentIndex || a.original - b.original || a.id.localeCompare(b.id));
    ordered.set(level, scored.map(item => item.id));
  };
  // Deterministic barycentric sweeps. Downward sweeps align children/merges to
  // their predecessors; upward sweeps keep sibling branches near their common
  // successors. Repeating both directions reduces crossings without randomness.
  for (let pass = 0; pass < 4; pass += 1) {
    let ranks = rankMap();
    for (const level of sortedLevels.slice(1)) { reorder(level, incoming, ranks); ranks = rankMap(); }
    ranks = rankMap();
    for (const level of [...sortedLevels].reverse().slice(1)) { reorder(level, outgoing, ranks); ranks = rankMap(); }
  }
  return ordered;
}
function relaxSmartSpaciousPositions(positions, groups, edges, horizontalGap, canvasMargin) {
  if ((state.treeLayoutDensity || "normal") !== "spacious") return positions;
  const controlEdges = (edges || []).filter(edge => (edge.edge_type || edge.relation_type || "control_flow") === "control_flow" && positions[edge.source] && positions[edge.target]);
  const neighbors = new Map(Object.keys(positions).map(id => [id, []]));
  for (const edge of controlEdges) { neighbors.get(edge.source)?.push(edge.target); neighbors.get(edge.target)?.push(edge.source); }
  const minStep = NODE_WIDTH + horizontalGap;
  for (let pass = 0; pass < 3; pass += 1) {
    for (const [, ids] of [...groups.entries()].sort((a, b) => a[0] - b[0])) {
      if (ids.length < 1) continue;
      const desired = ids.map(id => {
        const linked = (neighbors.get(id) || []).filter(other => positions[other]);
        if (!linked.length) return positions[id].x;
        const center = linked.reduce((sum, other) => sum + positions[other].x + nodeSize(other).width / 2, 0) / linked.length;
        return Math.max(canvasMargin, positions[id].x * 0.55 + (center - nodeSize(id).width / 2) * 0.45);
      });
      const next = [];
      desired.forEach((x, index) => { next[index] = index ? Math.max(x, next[index - 1] + minStep) : x; });
      // Preserve the layer's approximate center so relaxation improves alignment
      // without causing the entire graph to drift sideways on every pass.
      const oldCenter = ids.reduce((sum, id) => sum + positions[id].x, 0) / ids.length;
      const newCenter = next.reduce((sum, x) => sum + x, 0) / next.length;
      const shift = oldCenter - newCenter;
      ids.forEach((id, index) => { positions[id].x = Math.max(canvasMargin, next[index] + shift); });
      // Re-assert non-overlap after clamping the leftmost node to the canvas.
      for (let index = 1; index < ids.length; index += 1) positions[ids[index]].x = Math.max(positions[ids[index]].x, positions[ids[index - 1]].x + minStep);
    }
  }
  return positions;
}
function automaticPositions() {
  const nodes = state.graph?.nodes || [], edges = state.graph?.edges || [];
  const metrics = treeLayoutMetrics();
  const horizontalGap = metrics.horizontalGap, verticalGap = metrics.verticalGap, canvasMargin = metrics.margin;
  const ids = new Set(nodes.map(node => node.id));
  const outgoing = new Map(nodes.map(node => [node.id, []]));
  // R3: control-flow topology owns the primary vertical spine. Dependency-only
  // entities are projected into a side overlay lane and never receive a rank
  // after the execution terminal merely because they are control-flow-unreachable.
  edges.forEach(edge => {
    const relation = edge.edge_type || edge.relation_type || "control_flow";
    if (relation !== "control_flow") return;
    if (ids.has(edge.source) && ids.has(edge.target)) outgoing.get(edge.source).push(edge.target);
  });
  const overlayEdges = edges.filter(edge => {
    const relation = edge.edge_type || edge.relation_type || "control_flow";
    return relation !== "control_flow" && ids.has(edge.source) && ids.has(edge.target);
  });

  const entry = entryNodeId(), levels = new Map(), queue = [];
  if (entry && ids.has(entry)) { levels.set(entry, 0); queue.push(entry); }
  for (let cursor = 0; cursor < queue.length; cursor += 1) {
    const source = queue[cursor], nextLevel = levels.get(source) + 1;
    (outgoing.get(source) || []).forEach(target => {
      if (!levels.has(target)) { levels.set(target, nextLevel); queue.push(target); }
    });
  }

  const primaryNodes = nodes.filter(node => levels.has(node.id));
  const overlayOnlyNodes = nodes.filter(node => !levels.has(node.id));
  const groups = new Map();
  primaryNodes.forEach(node => {
    const level = levels.get(node.id);
    if (!groups.has(level)) groups.set(level, []);
    groups.get(level).push(node.id);
  });

  const layoutGroups = smartSpaciousOrderedGroups(groups, levels, nodes, edges);
  const widestGroup = Math.max(1, ...[...layoutGroups.values()].map(group => group.length));
  const primaryContentWidth = widestGroup * NODE_WIDTH + (widestGroup - 1) * horizontalGap;
  const overlayLaneWidth = overlayOnlyNodes.length ? NODE_WIDTH + horizontalGap * 2 : 0;
  const primaryAreaWidth = Math.max(metrics.minPrimaryWidth, primaryContentWidth + canvasMargin * 2);
  const canvasWidth = Math.max(metrics.minCanvasWidth, workspace.clientWidth, primaryAreaWidth + overlayLaneWidth + canvasMargin);
  const positions = {};
  const levelY = new Map();
  let currentY = canvasMargin;

  [...layoutGroups.keys()].sort((a, b) => a - b).forEach(level => {
    const group = layoutGroups.get(level);
    const groupWidth = group.length * NODE_WIDTH + (group.length - 1) * horizontalGap;
    const startX = Math.max(canvasMargin, (primaryAreaWidth - groupWidth) / 2);
    levelY.set(level, currentY);
    group.forEach((id, index) => {
      positions[id] = { x: startX + index * (NODE_WIDTH + horizontalGap), y: currentY };
    });
    const levelHeight = Math.max(NODE_MIN_HEIGHT, ...group.map(id => nodeHeight(id)));
    currentY += levelHeight + verticalGap;
  });

  relaxSmartSpaciousPositions(positions, layoutGroups, edges, horizontalGap, canvasMargin);

  if (overlayOnlyNodes.length) {
    const overlayIds = new Set(overlayOnlyNodes.map(node => node.id));
    const overlayAdjacency = new Map(overlayOnlyNodes.map(node => [node.id, new Set()]));
    const overlayAnchorLevel = new Map();

    // Seed dependency-only entities from the execution node they annotate.
    for (const edge of overlayEdges) {
      const sourcePrimary = levels.has(edge.source), targetPrimary = levels.has(edge.target);
      if (overlayIds.has(edge.target) && sourcePrimary) overlayAnchorLevel.set(edge.target, levels.get(edge.source));
      if (overlayIds.has(edge.source) && targetPrimary) overlayAnchorLevel.set(edge.source, levels.get(edge.target));
      if (overlayIds.has(edge.source) && overlayIds.has(edge.target)) {
        overlayAdjacency.get(edge.source).add(edge.target);
        overlayAdjacency.get(edge.target).add(edge.source);
      }
    }

    // Propagate an anchor through overlay-only chains without converting any
    // overlay relation into execution flow.
    const anchorQueue = [...overlayAnchorLevel.keys()];
    for (let cursor = 0; cursor < anchorQueue.length; cursor += 1) {
      const id = anchorQueue[cursor], anchor = overlayAnchorLevel.get(id);
      for (const next of overlayAdjacency.get(id) || []) {
        if (overlayAnchorLevel.has(next)) continue;
        overlayAnchorLevel.set(next, anchor);
        anchorQueue.push(next);
      }
    }

    const overlayX = Math.max(primaryAreaWidth + horizontalGap, canvasWidth - canvasMargin - NODE_WIDTH);
    const anchoredGroups = new Map();
    const unattached = [];
    const outputProducerGroups = new Map();
    const producerPlacedOutputs = new Set();
    for (const node of overlayOnlyNodes) {
      const producerId = node.entity_type === "declared_output" && Array.isArray(node.producers) && node.producers.length === 1 ? node.producers[0] : null;
      if (producerId && positions[producerId]) {
        if (!outputProducerGroups.has(producerId)) outputProducerGroups.set(producerId, []);
        outputProducerGroups.get(producerId).push(node.id);
        producerPlacedOutputs.add(node.id);
        continue;
      }
      if (!overlayAnchorLevel.has(node.id)) { unattached.push(node.id); continue; }
      const level = overlayAnchorLevel.get(node.id);
      if (!anchoredGroups.has(level)) anchoredGroups.set(level, []);
      anchoredGroups.get(level).push(node.id);
    }

    // Declared outputs are semantic attachments to their unique producer, not
    // terminal branches. Place them beside that producer before generic overlays.
    const collides = (x, y, id) => Object.entries(positions).some(([otherId, pos]) => {
      if (otherId === id) return false;
      const a=nodeSize(id), b=nodeSize(otherId);
      return x < pos.x + b.width + 14 && x + a.width + 14 > pos.x && y < pos.y + b.height + 14 && y + a.height + 14 > pos.y;
    });
    for (const [producerId, group] of outputProducerGroups) {
      const producerPos = positions[producerId];
      group.sort();
      group.forEach((id, index) => {
        let x = producerPos.x + nodeSize(producerId).width + metrics.producerGapX;
        let y = producerPos.y + index * (nodeHeight(id) + metrics.producerGapY);
        let attempts = 0;
        while (collides(x, y, id) && attempts < 8) { x += NODE_WIDTH + metrics.producerGapX; attempts += 1; }
        positions[id] = { x, y };
      });
    }

    for (const [level, group] of [...anchoredGroups.entries()].sort((a, b) => a[0] - b[0])) {
      const anchorY = levelY.get(level) ?? canvasMargin;
      group.sort();
      group.forEach((id, index) => {
        positions[id] = { x: overlayX, y: anchorY + index * (nodeHeight(id) + metrics.overlayGapY) };
      });
    }

    // Truly unattached projection entities stay in a diagnostic side lane at
    // the top of the canvas. They are never appended below END/terminal.
    let diagnosticY = canvasMargin;
    unattached.sort().forEach(id => {
      while (Object.entries(positions).some(([otherId, pos]) => otherId !== id && pos.x === overlayX && Math.abs(pos.y - diagnosticY) < nodeHeight(id) + metrics.producerGapY)) {
        diagnosticY += nodeHeight(id) + metrics.overlayGapY;
      }
      positions[id] = { x: overlayX, y: diagnosticY };
      diagnosticY += nodeHeight(id) + metrics.overlayGapY;
    });
  }

  return positions;
}
function pathFocusPositions(path, active) {
  const nodes = state.graph?.nodes || [];
  const metrics = treeLayoutMetrics();
  if (!active || !path?.length) return null;
  const base = automaticPositions();
  const ids = new Set(nodes.map(node => node.id));
  const pathIds = path.filter(id => ids.has(id));
  if (!pathIds.length) return null;

  const pathSet = new Set(pathIds);
  const pathIndex = new Map(pathIds.map((id, index) => [id, index]));
  const adjacency = new Map(nodes.map(node => [node.id, new Set()]));
  for (const edge of state.graph?.edges || []) {
    if (!ids.has(edge.source) || !ids.has(edge.target)) continue;
    adjacency.get(edge.source).add(edge.target);
    adjacency.get(edge.target).add(edge.source);
  }

  // Multi-source BFS assigns every alternative element to the closest step on
  // the active dialog path.  That step becomes its visual branch anchor.
  const owner = new Map();
  const distance = new Map();
  const queue = [];
  pathIds.forEach((id, index) => { owner.set(id, index); distance.set(id, 0); queue.push(id); });
  for (let cursor = 0; cursor < queue.length; cursor += 1) {
    const id = queue[cursor];
    const nextDistance = distance.get(id) + 1;
    for (const next of adjacency.get(id) || []) {
      if (distance.has(next)) continue;
      distance.set(next, nextDistance);
      owner.set(next, owner.get(id));
      queue.push(next);
    }
  }

  const pathGapY = NODE_MIN_HEIGHT + metrics.pathGapY;
  const branchGapX = NODE_WIDTH + metrics.branchGapX;
  const mainX = Math.max(metrics.margin + branchGapX * 2, Math.round(Math.max(metrics.minPrimaryWidth, workspace.clientWidth) * 0.48));
  const positions = {};
  let pathY = metrics.margin;
  pathIds.forEach((id, index) => {
    positions[id] = { x: mainX, y: pathY };
    pathY += nodeHeight(id) + metrics.pathGapY;
  });

  const groups = new Map();
  for (const node of nodes) {
    if (pathSet.has(node.id)) continue;
    const anchor = owner.has(node.id) ? owner.get(node.id) : 0;
    const dist = Math.max(1, distance.get(node.id) || 1);
    const anchorId = pathIds[Math.min(anchor, pathIds.length - 1)];
    const baseNode = base[node.id] || { x: mainX, y: metrics.margin };
    const baseAnchor = base[anchorId] || { x: mainX, y: metrics.margin };
    let side = Math.sign(baseNode.x - baseAnchor.x);
    if (!side) side = ((node.id.length + anchor) % 2 === 0) ? -1 : 1;
    const key = `${anchor}:${side}:${Math.min(dist, 4)}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push({ id: node.id, anchor, side, dist, baseY: baseNode.y });
  }

  for (const group of groups.values()) {
    group.sort((a, b) => a.baseY - b.baseY || a.id.localeCompare(b.id));
    const count = group.length;
    group.forEach((item, rank) => {
      const lane = Math.min(item.dist, 4);
      const anchorY = positions[pathIds[Math.min(item.anchor, pathIds.length - 1)]]?.y || metrics.margin;
      const spread = Math.max(NODE_MIN_HEIGHT, nodeHeight(item.id)) + Math.max(34, Math.round(metrics.verticalGap * 0.48));
      const offsetY = (rank - (count - 1) / 2) * spread;
      positions[item.id] = {
        x: Math.max(metrics.margin, mainX + item.side * lane * branchGapX),
        y: Math.max(metrics.margin, anchorY + offsetY),
      };
    });
  }

  // Disconnected items that could not be assigned by BFS are placed in a
  // quiet far-right column instead of disturbing the active route.
  let orphanIndex = 0;
  for (const node of nodes) {
    if (positions[node.id]) continue;
    positions[node.id] = { x: mainX + branchGapX * 5, y: metrics.margin + orphanIndex++ * (NODE_MIN_HEIGHT + Math.max(42, Math.round(metrics.verticalGap * 0.6))) };
  }
  return positions;
}
function dialogFocusPositions() { return pathFocusPositions(state.dialogPath?.nodes || [], dialogPathIsActive()); }
function replayTraversedNodeIds() {
  if (state.panelTab !== "replay" || !state.replayData) return [];
  const ids = new Set((state.graph?.nodes || []).map(node => node.id));
  return (state.replayData.steps || []).map(step => step.id).filter(id => id && ids.has(id));
}
function replayPathNodes() { return [...new Set(replayTraversedNodeIds())]; }
function replayPathIsActive() { return state.panelTab === "replay" && replayPathNodes().length > 0; }
function replayFocusPositions() { return pathFocusPositions(replayPathNodes(), replayPathIsActive()); }
function livePathNodes() { return (state.livePath || []).filter(id => knownGraphIds().has(id)); }
function livePathIsActive() { return state.panelTab === "run" && state.liveRunning && livePathNodes().length > 0; }
function liveFocusPositions() { return pathFocusPositions(livePathNodes(), livePathIsActive()); }
function livePathEdges() {
  const nodes = state.livePath || [], graphEdges = state.graph?.edges || [], result = [];
  for (let index = 0; index < nodes.length - 1; index += 1) {
    const edge = graphEdges.find(item => item.source === nodes[index] && item.target === nodes[index + 1]);
    if (edge) result.push(edge);
  }
  return result;
}
function replayPathEdges() {
  const nodes = replayTraversedNodeIds();
  const graphEdges = state.graph?.edges || [];
  const result = [];
  for (let index = 0; index < nodes.length - 1; index += 1) {
    const source = nodes[index], target = nodes[index + 1];
    const edge = graphEdges.find(item => item.source === source && item.target === target);
    if (edge) result.push(edge);
  }
  return result;
}
function positionFor(id) { return state.positions[id]; }
function resizeCanvas() {
  const entries = Object.entries(state.positions);
  const metrics = treeLayoutMetrics();
  const routing = (state.treeLayoutDensity || "normal") === "spacious" ? spaciousExternalCorridorLanes() : null;
  const rightReserve = routing?.rightLaneCount ? 34 + Math.max(0, routing.rightLaneCount - 1) * 34 + 62 : 0;
  const envelope = routing?.envelope || spaciousRoutingEnvelope();
  const naturalRight = Math.max(metrics.minCanvasWidth, ...entries.map(([id, pos]) => pos.x + nodeSize(id).width + metrics.margin));
  const routedRight = envelope ? envelope.maxRight + rightReserve + metrics.margin : naturalRight;
  const width = Math.max(naturalRight, routedRight);
  const height = Math.max(700, ...entries.map(([id, pos]) => pos.y + nodeHeight(id) + metrics.margin));
  canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
  edges.setAttribute("width", String(width)); edges.setAttribute("height", String(height)); edges.setAttribute("viewBox", `0 0 ${width} ${height}`);
}
let nodeTooltipHideTimer;
function hideNodeTooltip() { clearTimeout(nodeTooltipHideTimer); nodeTooltip.hidden = true; }
function scheduleNodeTooltipHide() { clearTimeout(nodeTooltipHideTimer); nodeTooltipHideTimer = setTimeout(() => { if (!nodeTooltip.matches(":hover")) nodeTooltip.hidden = true; }, 650); }
nodeTooltip.addEventListener("pointerenter", () => clearTimeout(nodeTooltipHideTimer));
nodeTooltip.addEventListener("pointerleave", scheduleNodeTooltipHide);
function collapsibleGraphIds() {
  return (state.graph?.nodes || []).filter(item => item.element_type === "node" || item.element_type === "gate").map(item => item.id);
}
function setNodeCollapsed(id, collapsed) {
  if (!id) return;
  if (collapsed) state.collapsedNodes.add(id); else state.collapsedNodes.delete(id);
  render();
}
function setAllNodesCollapsed(collapsed) {
  const ids = collapsibleGraphIds();
  state.collapsedNodes = collapsed ? new Set(ids) : new Set();
  render();
}
function updateCollapseMenuState(singleNodeId = null) {
  const ids = collapsibleGraphIds();
  const collapsedCount = ids.filter(id => state.collapsedNodes.has(id)).length;
  const collapseAll = document.querySelector("#canvas-collapse-all");
  const expandAll = document.querySelector("#canvas-expand-all");
  if (collapseAll) collapseAll.hidden = !ids.length || collapsedCount === ids.length;
  if (expandAll) expandAll.hidden = !ids.length || collapsedCount === 0;
  const toggle = document.querySelector("#canvas-toggle-collapse");
  if (toggle) {
    toggle.dataset.nodeId = singleNodeId || "";
    toggle.hidden = !singleNodeId;
    toggle.textContent = singleNodeId && state.collapsedNodes.has(singleNodeId) ? "Expand" : "Collapse";
  }
}
function hideCanvasContextMenu() {
  const menu = document.querySelector("#canvas-context-menu");
  menu.hidden = true;
  state.canvasMenuPosition = null;
}
function showCanvasContextMenu(event) {
  if (!state.source) return;
  const nodeElement = event.target.closest?.(".node");
  if (event.target.closest?.(".edge-hit")) return;
  const clickedView = nodeElement ? (state.graph?.nodes || []).find(item => item.id === nodeElement.dataset.id) : null;
  const clickedDeletable = Boolean(clickedView && (clickedView.element_type === "node" || clickedView.element_type === "gate") && sourceRecord(clickedView.id));
  if (clickedDeletable) {
    const nodeId = nodeElement.dataset.id;
    if (!state.selectedNodes.has(nodeId)) {
      state.selectedNodes = new Set([nodeId]);
      state.selected = nodeId;
      render();
    }
  }
  event.preventDefault();
  hideNodeTooltip(); hideEdgeMenu();
  const rect = canvas.getBoundingClientRect();
  state.canvasMenuPosition = { x: Math.max(0, event.clientX - rect.left), y: Math.max(0, event.clientY - rect.top) };
  const menu = document.querySelector("#canvas-context-menu");
  const selectedDeletableIds = [...state.selectedNodes].filter(id => {
    const view = (state.graph?.nodes || []).find(item => item.id === id);
    return Boolean(view && (view.element_type === "node" || view.element_type === "gate") && sourceRecord(id));
  });
  const hasSelection = Boolean(clickedDeletable && state.selectedNodes.has(nodeElement.dataset.id) && selectedDeletableIds.length > 0);
  const singleSelection = hasSelection && selectedDeletableIds.length === 1;
  updateCollapseMenuState(singleSelection ? selectedDeletableIds[0] : null);
  document.querySelector("#canvas-create-actions").hidden = true;
  document.querySelector("#canvas-general-actions").hidden = false;
  document.querySelector("#canvas-selection-actions").hidden = !hasSelection;
  document.querySelector("#canvas-delete-selection").hidden = true;
  const dialogActions = document.querySelector("#canvas-dialog-actions");
  dialogActions.hidden = !singleSelection;
  if (singleSelection) {
    const nodeId = selectedDeletableIds[0], entryPath = shortestDialogPath(entryNodeId(), nodeId), terminals = reachableTerminalPaths(nodeId);
    const fromEntry = document.querySelector("#canvas-dialog-from-entry");
    fromEntry.disabled = !entryPath; fromEntry.textContent = entryPath ? "Show dialog: start → this node" : "Show dialog: start → this node (no path)";
    fromEntry.dataset.nodeId = nodeId;
    const terminalMenu = document.querySelector("#canvas-dialog-terminal-menu"); terminalMenu.innerHTML = "";
    if (!terminals.length) { const item = document.createElement("button"); item.type = "button"; item.disabled = true; item.textContent = "No reachable endings"; terminalMenu.append(item); }
    else terminals.forEach(({ terminal, path }) => { const item = document.createElement("button"); item.type = "button"; item.role = "menuitem"; item.textContent = `${terminal.id} · ${path.nodes.length - 1} step${path.nodes.length - 1 === 1 ? "" : "s"}`; item.addEventListener("click", () => openNodeToTerminalDialog(nodeId, terminal.id)); terminalMenu.append(item); });
  }
  if (nodeElement && !hasSelection) { menu.hidden = true; state.canvasMenuPosition = null; return; }
  menu.hidden = false; menu.style.left = `${event.clientX}px`; menu.style.top = `${event.clientY}px`;
  requestAnimationFrame(() => {
    let menuRect = menu.getBoundingClientRect();
    if (menuRect.right > window.innerWidth - 8) menu.style.left = `${Math.max(8, event.clientX - menuRect.width)}px`;
    if (menuRect.bottom > window.innerHeight - 8) menu.style.top = `${Math.max(8, event.clientY - menuRect.height)}px`;
    menuRect = menu.getBoundingClientRect();
    menu.classList.toggle("submenu-left", menuRect.right + 230 > window.innerWidth - 8);
  });
}
function disconnectedNodeTemplate() {
  return {
    id: uniqueId("N_NEW_NODE"),
    question: "Describe the decision or action for this node.",
    answer_type: "free_text",
    allow_unmatched_input: true,
    allowed_from: [],
  };
}
function disconnectedGateTemplate() {
  return {
    id: uniqueId("G_NEW_GATE"),
    method: "mechanical",
    trust_class: "deterministic",
    condition: "Describe the condition this gate evaluates.",
  };
}
function disconnectedMaterializationTemplate() {
  return {
    id: uniqueId("N_NEW_MATERIALIZATION"),
    question: "Materialize the reviewed document artifact.",
    answer_type: "confirmation",
    allow_unmatched_input: true,
    allowed_from: [],
  };
}
function disconnectedTerminalTemplate() {
  return {
    id: uniqueId("N_NEW_TERMINAL"),
    question: "Confirm the terminal outcome.",
    answer_type: "confirmation",
    allow_unmatched_input: true,
    terminal: true,
    allowed_from: [],
  };
}
async function createDisconnectedElement(kind) {
  if (!state.source || !state.canvasMenuPosition) return;
  const position = { ...state.canvasMenuPosition };
  const record = kind === "gate" ? disconnectedGateTemplate()
    : kind === "materialization" ? disconnectedMaterializationTemplate()
    : kind === "terminal" ? disconnectedTerminalTemplate()
    : disconnectedNodeTemplate();
  const collection = kind === "gate" ? "gates" : "nodes";
  if (!Array.isArray(state.source[collection])) state.source[collection] = [];
  state.source[collection].push(record);
  hideCanvasContextMenu();
  try {
    const data = await request("/api/parse", { source: state.source });
    state.source = data.source; state.graph = data.graph;
    state.positions[record.id] = position; state.manualPositions.add(record.id);
    state.selected = record.id; state.selectedNodes = new Set([record.id]); state.selectedEdge = null;
    render();
  } catch (error) {
    state.source[collection] = state.source[collection].filter(item => item !== record);
    alert(error.message);
  }
}
function moveNodeTooltip(event) {
  const padding = 14;
  nodeTooltip.style.left = `${event.clientX + padding}px`;
  nodeTooltip.style.top = `${event.clientY + padding}px`;
  requestAnimationFrame(() => {
    if (nodeTooltip.hidden) return;
    const rect = nodeTooltip.getBoundingClientRect();
    if (rect.right > window.innerWidth - 8) nodeTooltip.style.left = `${Math.max(8, event.clientX - rect.width - padding)}px`;
    if (rect.bottom > window.innerHeight - 8) nodeTooltip.style.top = `${Math.max(8, event.clientY - rect.height - padding)}px`;
  });
}
function showNodeTooltip(node, event) {
  if (!node || !["node", "gate"].includes(node.element_type) || !node.record_yaml) return hideNodeTooltip();
  nodeTooltip.textContent = node.record_yaml;
  clearTimeout(nodeTooltipHideTimer);
  nodeTooltip.hidden = false;
  moveNodeTooltip(event);
}

function dialogPathIsActive() { return state.panelTab === "dialog" && Boolean(state.dialogPath); }
function dialogVisiblePathNodes() {
  if (!dialogPathIsActive()) return [];
  const count = state.dialogPlayMode ? Math.max(1, Math.min(state.dialogVisibleCount || 1, state.dialogPath.nodes.length)) : state.dialogPath.nodes.length;
  return state.dialogPath.nodes.slice(0, count);
}
function dialogVisiblePathEdges() {
  if (!dialogPathIsActive()) return [];
  const count = state.dialogPlayMode ? Math.max(0, Math.min((state.dialogVisibleCount || 1) - 1, state.dialogPath.edges.length)) : state.dialogPath.edges.length;
  return state.dialogPath.edges.slice(0, count);
}
function dialogPathNodeSet() { return new Set(dialogVisiblePathNodes()); }
function sameDialogEdge(a, b) {
  if (!a || !b) return false;
  return a.source === b.source && a.target === b.target && dialogRouteLabel(a) === dialogRouteLabel(b);
}
function drawDialogPathOverlay() {
  if (!dialogPathIsActive()) return;
  for (const edge of dialogVisiblePathEdges()) {
    const source = state.positions[edge.source], target = state.positions[edge.target];
    if (!source || !target) continue;
    const geometry = edgeGeometry(source, target, edge.source, edge.target);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
    line.classList.add("dialog-path-edge");
    if (edge.dynamic) line.classList.add("dynamic");
    line.setAttribute("d", geometry.path);
    edges.append(line);
  }
}
function drawReplayPathOverlay() {
  if (!replayPathIsActive()) return;
  for (const edge of replayPathEdges()) {
    const source = state.positions[edge.source], target = state.positions[edge.target];
    if (!source || !target) continue;
    const geometry = edgeGeometry(source, target, edge.source, edge.target);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
    line.classList.add("replay-path-edge");
    line.setAttribute("d", geometry.path);
    edges.append(line);
  }
}

function drawLivePathOverlay() {
  if (!livePathIsActive()) return;
  for (const edge of livePathEdges()) {
    const source = state.positions[edge.source], target = state.positions[edge.target];
    if (!source || !target) continue;
    const geometry = edgeGeometry(source, target, edge.source, edge.target);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
    line.classList.add("live-path-edge"); line.setAttribute("d", geometry.path); edges.append(line);
  }
}

function renderTransitionMode() {
  const banner = document.querySelector("#transition-mode"), text = document.querySelector("#transition-mode-text");
  const source = state.pendingTransitionSource;
  banner.hidden = !source;
  if (source) text.textContent = `Select the target node for a transition from ${source}.`;
}
function breakableIdentifier(value) {
  return String(value ?? "").replaceAll("_", "_\u200b");
}

function render() {
  updateWorkspaceShell();
  if (!document.querySelector("#settings-overview-modal")?.hidden) renderSettingsOverview();
  canvas.innerHTML = ""; edges.innerHTML = '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#6680ae"/></marker></defs>';
  document.querySelector("#validate").hidden = !state.source;
  if (!state.source) { empty.hidden = false; return; } empty.hidden = true;
  const automatic = automaticPositions();
  const dialogLayout = dialogFocusPositions();
  const replayLayout = replayFocusPositions();
  const liveLayout = liveFocusPositions();
  const focusLayout = dialogLayout || replayLayout || liveLayout;
  canvas.classList.toggle("dialog-focus-layout", Boolean(dialogLayout));
  canvas.classList.toggle("replay-focus-layout", Boolean(replayLayout));
  (state.graph.nodes || []).forEach(node => {
    const pos = state.manualPositions.has(node.id) ? positionFor(node.id) : (focusLayout?.[node.id] || automatic[node.id]); state.positions[node.id] = pos;
    const element = document.createElement("article");
    const onDialogPath = dialogPathIsActive() && dialogPathNodeSet().has(node.id);
    const dialogCurrent = dialogPathIsActive() && state.dialogFocusId === node.id;
    const onReplayPath = replayPathIsActive() && replayPathNodes().includes(node.id);
    const replayCurrent = replayPathIsActive() && state.replayFocusId === node.id;
    const onLivePath = livePathIsActive() && livePathNodes().includes(node.id);
    const liveCurrent = livePathIsActive() && state.liveCurrentId === node.id;
    const outputTraceClass = node.entity_type === "declared_output" ? `output-${String(node.traceability_status || "unknown").toLowerCase()}` : "";
    element.className = `node ${node.element_type || "node"} ${node.terminal ? "terminal" : ""} ${outputTraceClass} ${state.collapsedNodes.has(node.id) ? "collapsed" : ""} ${state.selectedNodes.has(node.id) ? "selected" : ""} ${state.pendingTransitionSource === node.id ? "transition-source" : ""} ${onDialogPath ? "dialog-path-node" : ""} ${dialogCurrent ? "dialog-current-node" : ""} ${onReplayPath ? "replay-path-node" : ""} ${replayCurrent ? "replay-current-node" : ""} ${onLivePath ? "live-path-node" : ""} ${liveCurrent ? "live-current-node" : ""}`;
    element.style.left = `${pos.x}px`; element.style.top = `${pos.y}px`; element.dataset.id = node.id;
    element.innerHTML = `<div class="node-ref-badges" hidden></div><div class="node-id"></div><div class="node-label"></div><div class="node-type"></div><div class="node-toolbar"><button type="button">Add transition</button></div>`;
    const referenceBadges = graphReferenceBadgesForNode(node);
    const badgeHost = element.querySelector(".node-ref-badges");
    if (badgeHost && referenceBadges.length) {
      badgeHost.hidden = false;
      badgeHost.innerHTML = referenceBadges.map(item => {
        const refsText = item.refs.join("\n");
        const noun = item.count === 1 ? "reference" : "references";
        return `<span class="node-ref-badge node-ref-${escapeHtml(item.type)}" title="${escapeHtml(`${item.label}: ${item.count} ${noun}\n${refsText}`)}" aria-label="${escapeHtml(`${item.label} ${noun}`)}"><span class="node-ref-badge-file" aria-hidden="true"></span><span class="node-ref-badge-text">${escapeHtml(item.label)}</span></span>`;
      }).join("");
    }
    const visitSteps = livePathIsActive() ? (state.livePath || []).map((id, index) => id === node.id ? index + 1 : null).filter(Boolean) : [];
    const visitSuffix = visitSteps.length > 1 ? `  ↻ steps ${visitSteps.join(",")}` : (visitSteps.length === 1 ? `  · step ${visitSteps[0]}` : "");
    element.querySelector(".node-id").textContent = (node.element_type === "gate" ? `◆ ${breakableIdentifier(node.id)}` : breakableIdentifier(node.id)) + visitSuffix;
    element.querySelector(".node-label").textContent = node.label;
    element.querySelector(".node-type").textContent = node.answer_type;
    const addButton = element.querySelector(".node-toolbar button");
    if (node.element_type === "terminal") addButton.hidden = true;
    addButton.hidden = true;
    element.addEventListener("click", event => handleNodeClick(node.id, event));
    makeDraggable(element);
    canvas.append(element);
  });
  applyMeasuredLayout(); resizeCanvas(); renderTransitionMode(); requestAnimationFrame(() => { drawEdges(); drawDialogPathOverlay(); drawReplayPathOverlay(); drawLivePathOverlay(); }); renderInspector();
}
let edgeMenuTimer;
function hideEdgeMenu() { document.querySelector("#edge-context-menu").hidden = true; }
function scheduleEdgeMenuHide() { clearTimeout(edgeMenuTimer); edgeMenuTimer = setTimeout(hideEdgeMenu, 180); }
function showEdgeMenu(edge, event) {
  if (!sourceRecord(edge.source)) return;
  clearTimeout(edgeMenuTimer); state.selectedEdge = edge;
  const menu = document.querySelector("#edge-context-menu");
  menu.hidden = false; menu.style.left = `${event.clientX + 10}px`; menu.style.top = `${event.clientY + 10}px`;
}
function deterministicEdgeLane(sourceId, targetId) {
  const value = `${sourceId || ""}->${targetId || ""}`;
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) hash = ((hash * 31) + value.charCodeAt(index)) >>> 0;
  return hash % 5;
}
function spaciousRoutingParticipantIds() {
  const ids = new Set();
  for (const edge of state.graph?.edges || []) {
    const relation = edge.edge_type || edge.relation_type || "control_flow";
    if (relation !== "control_flow") continue;
    if (state.positions?.[edge.source]) ids.add(edge.source);
    if (state.positions?.[edge.target]) ids.add(edge.target);
  }
  return ids;
}
function spaciousRoutingEnvelope() {
  const ids = spaciousRoutingParticipantIds();
  const entries = [...ids].map(id => [id, state.positions?.[id]]).filter(([, pos]) => pos);
  const fallback = Object.entries(state.positions || {});
  const routedEntries = entries.length ? entries : fallback;
  if (!routedEntries.length) return null;
  return {
    minLeft: Math.min(...routedEntries.map(([, pos]) => pos.x)),
    maxRight: Math.max(...routedEntries.map(([id, pos]) => pos.x + nodeSize(id).width)),
  };
}
function spaciousEdgePortOffset(nodeId, sourceId, targetId, endpoint) {
  const edges = (state.graph?.edges || []).filter(edge => {
    const relation = edge.edge_type || edge.relation_type || "control_flow";
    if (relation !== "control_flow") return false;
    return endpoint === "source" ? edge.source === nodeId : edge.target === nodeId;
  }).sort((a, b) => {
    const aPeer = endpoint === "source" ? a.target : a.source;
    const bPeer = endpoint === "source" ? b.target : b.source;
    return String(aPeer).localeCompare(String(bPeer)) || String(a.key || "").localeCompare(String(b.key || ""));
  });
  const index = edges.findIndex(edge => edge.source === sourceId && edge.target === targetId);
  if (index < 0 || edges.length <= 1) return 0;
  const slot = index - (edges.length - 1) / 2;
  return Math.max(-28, Math.min(28, slot * 12));
}
function spaciousHorizontalOverlap(a, b, clearance = 5) {
  if (Math.abs(a.y - b.y) >= clearance) return false;
  return Math.max(a.minX, b.minX) < Math.min(a.maxX, b.maxX) - 2;
}
let spaciousInternalMiniLaneCache = null;
let spaciousInternalRoutePlanCache = null;
function resetSpaciousInternalMiniLaneCache() { spaciousInternalMiniLaneCache = null; spaciousInternalRoutePlanCache = null; }
function spaciousIntervalsOverlap(aMin, aMax, bMin, bMax, clearance = 0) {
  return Math.max(aMin, bMin) < Math.min(aMax, bMax) - clearance;
}
function spaciousSegmentsOverlap(a, b, clearance = 2) {
  if (a.orientation !== b.orientation) return false;
  if (a.orientation === "h") return Math.abs(a.y1 - b.y1) < clearance && spaciousIntervalsOverlap(Math.min(a.x1, a.x2), Math.max(a.x1, a.x2), Math.min(b.x1, b.x2), Math.max(b.x1, b.x2), 1);
  return Math.abs(a.x1 - b.x1) < clearance && spaciousIntervalsOverlap(Math.min(a.y1, a.y2), Math.max(a.y1, a.y2), Math.min(b.y1, b.y2), Math.max(b.y1, b.y2), 1);
}
function spaciousSegmentsCross(a, b, clearance = 1) {
  if (a.orientation === b.orientation) return false;
  const h = a.orientation === "h" ? a : b;
  const v = a.orientation === "v" ? a : b;
  const hx1 = Math.min(h.x1, h.x2), hx2 = Math.max(h.x1, h.x2);
  const vy1 = Math.min(v.y1, v.y2), vy2 = Math.max(v.y1, v.y2);
  if (v.x1 <= hx1 + clearance || v.x1 >= hx2 - clearance) return false;
  if (h.y1 <= vy1 + clearance || h.y1 >= vy2 - clearance) return false;
  return true;
}
function spaciousSegmentsFromPoints(points) {
  const segments = [];
  for (let index = 1; index < points.length; index += 1) {
    const a = points[index - 1], b = points[index];
    if (a.x === b.x && a.y === b.y) continue;
    segments.push({ x1: a.x, y1: a.y, x2: b.x, y2: b.y, orientation: a.y === b.y ? "h" : "v" });
  }
  return segments;
}
function spaciousPathFromPoints(points) {
  return points.map((point, index) => `${index ? "L" : "M"} ${point.x} ${point.y}`).join(" ");
}
function spaciousPointInsideNode(point, nodeId, clearance = 8) {
  const pos = state.positions?.[nodeId];
  if (!pos) return false;
  const size = nodeSize(nodeId);
  return point.x >= pos.x - clearance && point.x <= pos.x + size.width + clearance && point.y >= pos.y - clearance && point.y <= pos.y + size.height + clearance;
}
function spaciousSegmentBlockedByNodes(segment, sourceId, targetId, clearance = 8) {
  for (const node of state.graph?.nodes || []) {
    if (node.id === sourceId || node.id === targetId) continue;
    const pos = state.positions?.[node.id];
    if (!pos) continue;
    const size = nodeSize(node.id);
    const minX = pos.x - clearance, maxX = pos.x + size.width + clearance;
    const minY = pos.y - clearance, maxY = pos.y + size.height + clearance;
    if (segment.orientation === "h") {
      const y = segment.y1; const sx1 = Math.min(segment.x1, segment.x2), sx2 = Math.max(segment.x1, segment.x2);
      if (y >= minY && y <= maxY && sx2 > minX && sx1 < maxX) return true;
    } else {
      const x = segment.x1; const sy1 = Math.min(segment.y1, segment.y2), sy2 = Math.max(segment.y1, segment.y2);
      if (x >= minX && x <= maxX && sy2 > minY && sy1 < maxY) return true;
    }
  }
  return false;
}
function spaciousRankLookup() {
  const values = [...new Set(Object.values(state.positions || {}).map(pos => Number(pos?.y || 0)))].sort((a, b) => a - b);
  const map = new Map();
  values.forEach((value, index) => map.set(value, index));
  const ranks = new Map();
  for (const [id, pos] of Object.entries(state.positions || {})) ranks.set(id, map.get(Number(pos?.y || 0)) || 0);
  return ranks;
}
function spaciousInternalBandLaneAssignments() {
  const ranks = spaciousRankLookup(), groups = new Map(), assignments = new Map();
  const edges = (state.graph?.edges || []).filter(edge => (edge.edge_type || edge.relation_type || "control_flow") === "control_flow")
    .filter(edge => state.positions?.[edge.source] && state.positions?.[edge.target])
    .filter(edge => !spaciousDirectHorizontalGeometry(edge.source, edge.target) && !spaciousCorridorEdgeInfo(edge.source, edge.target));
  for (const edge of edges) {
    const sourceRank = ranks.get(edge.source) || 0, targetRank = ranks.get(edge.target) || 0;
    const bandKey = `y:${Math.min(sourceRank, targetRank)}-${Math.max(sourceRank, targetRank)}`;
    if (!groups.has(bandKey)) groups.set(bandKey, []);
    groups.get(bandKey).push(edge);
  }
  for (const [bandKey, list] of groups) {
    const sorted = [...list].sort((a, b) => {
      const ap = state.positions?.[a.source], at = state.positions?.[a.target], bp = state.positions?.[b.source], bt = state.positions?.[b.target];
      return (Number(ap?.x || 0) - Number(bp?.x || 0)) || (Number(at?.x || 0) - Number(bt?.x || 0)) || `${a.source}->${a.target}`.localeCompare(`${b.source}->${b.target}`);
    });
    const count = sorted.length;
    sorted.forEach((edge, index) => {
      const slot = index - (count - 1) / 2;
      assignments.set(`${edge.source}->${edge.target}`, { x: slot * 18, y: 0, band: bandKey });
    });
  }
  return assignments;
}
function spaciousBuildReservedSegments() {
  const reserved = [];
  const controlEdges = (state.graph?.edges || []).filter(edge => (edge.edge_type || edge.relation_type || "control_flow") === "control_flow");
  const routing = spaciousExternalCorridorLanes();
  const envelope = routing.envelope || spaciousRoutingEnvelope();
  const metrics = treeLayoutMetrics();
  const corridorBaseGap = 34, corridorStep = 34;
  // Reserve small local stems around every control-flow attachment so nearby
  // routes avoid cutting through a node's obvious fan-out / fan-in corridor.
  for (const edge of controlEdges) {
    const source = state.positions?.[edge.source], target = state.positions?.[edge.target];
    if (!source || !target) continue;
    const sourceSize = nodeSize(edge.source), targetSize = nodeSize(edge.target);
    const sourceCenter = { x: source.x + sourceSize.width / 2 + spaciousEdgePortOffset(edge.source, edge.source, edge.target, "source"), y: source.y + sourceSize.height / 2 };
    const targetCenter = { x: target.x + targetSize.width / 2 + spaciousEdgePortOffset(edge.target, edge.source, edge.target, "target"), y: target.y + targetSize.height / 2 };
    if (Math.abs(targetCenter.x - sourceCenter.x) >= Math.abs(targetCenter.y - sourceCenter.y)) {
      const startSideX = targetCenter.x >= sourceCenter.x ? source.x + sourceSize.width : source.x;
      const endSideX = targetCenter.x >= sourceCenter.x ? target.x : target.x + targetSize.width;
      reserved.push({ x1: startSideX, y1: sourceCenter.y, x2: startSideX + (targetCenter.x >= sourceCenter.x ? 22 : -22), y2: sourceCenter.y, orientation: "h", owner: `${edge.source}->${edge.target}:source-stem`, hard: false });
      reserved.push({ x1: endSideX, y1: targetCenter.y, x2: endSideX + (targetCenter.x >= sourceCenter.x ? -22 : 22), y2: targetCenter.y, orientation: "h", owner: `${edge.source}->${edge.target}:target-stem`, hard: false });
    } else {
      const downward = targetCenter.y >= sourceCenter.y;
      const startY = downward ? source.y + sourceSize.height : source.y;
      const endY = downward ? target.y : target.y + targetSize.height;
      reserved.push({ x1: sourceCenter.x, y1: startY, x2: sourceCenter.x, y2: startY + (downward ? 26 : -26), orientation: "v", owner: `${edge.source}->${edge.target}:source-stem`, hard: false });
      reserved.push({ x1: targetCenter.x, y1: endY, x2: targetCenter.x, y2: endY + (downward ? -26 : 26), orientation: "v", owner: `${edge.source}->${edge.target}:target-stem`, hard: false });
    }
  }

  for (const edge of controlEdges) {
    const direct = spaciousDirectHorizontalGeometry(edge.source, edge.target);
    if (direct) {
      const segs = spaciousSegmentsFromPoints([{ x: Number(direct.path.split(" ")[1]), y: Number(direct.path.split(" ")[2]) }, { x: Number(direct.path.split(" ")[4]), y: Number(direct.path.split(" ")[5]) }]);
      segs.forEach(segment => reserved.push({ ...segment, owner: `${edge.source}->${edge.target}`, hard: true }));
      continue;
    }
    const info = spaciousCorridorEdgeInfo(edge.source, edge.target);
    if (!info) continue;
    const assignment = routing.lanes.get(`${edge.source}->${edge.target}`) || { side: "right", lane: 0 };
    const lane = assignment.lane;
    const source = state.positions?.[edge.source], target = state.positions?.[edge.target];
    if (!source || !target) continue;
    const sourceSize = nodeSize(edge.source), targetSize = nodeSize(edge.target);
    const sourceCenter = { x: source.x + sourceSize.width / 2 + spaciousEdgePortOffset(edge.source, edge.source, edge.target, "source"), y: source.y + sourceSize.height / 2 };
    const targetCenter = { x: target.x + targetSize.width / 2 + spaciousEdgePortOffset(edge.target, edge.source, edge.target, "target"), y: target.y + targetSize.height / 2 };
    const start = { x: sourceCenter.x, y: targetCenter.y >= sourceCenter.y ? source.y + sourceSize.height : source.y };
    const end = { x: targetCenter.x, y: targetCenter.y >= sourceCenter.y ? target.y : target.y + targetSize.height };
    const corridorX = assignment.side === "left"
      ? Math.max(12, (envelope?.minLeft ?? metrics.margin) - corridorBaseGap - lane * corridorStep)
      : (envelope?.maxRight ?? metrics.minCanvasWidth - metrics.margin) + corridorBaseGap + lane * corridorStep;
    const startStubY = start.y + (info.backEdge ? -24 : 24 + lane * 3);
    const endStubY = end.y + (info.backEdge ? 24 : -24 - lane * 3);
    const points = [start, { x: start.x, y: startStubY }, { x: corridorX, y: startStubY }, { x: corridorX, y: endStubY }, { x: end.x, y: endStubY }, end];
    spaciousSegmentsFromPoints(points).forEach(segment => reserved.push({ ...segment, owner: `${edge.source}->${edge.target}`, hard: true }));
  }
  return reserved;
}
function spaciousInternalRouteCandidates(sourceId, targetId, sourceCenter, targetCenter, laneOffset, miniLaneOffset, laneHint = { x: 0, y: 0 }) {
  const source = state.positions?.[sourceId], target = state.positions?.[targetId];
  if (!source || !target) return [];
  const sourceSize = nodeSize(sourceId), targetSize = nodeSize(targetId);
  const startVertical = { x: sourceCenter.x, y: targetCenter.y >= sourceCenter.y ? source.y + sourceSize.height : source.y };
  const endVertical = { x: targetCenter.x, y: targetCenter.y >= sourceCenter.y ? target.y : target.y + targetSize.height };
  const dy = endVertical.y - startVertical.y;
  const candidates = [];
  const verticalOffsets = [0, 10, -10, 20, -20, 32, -32, 46, -46, 64, -64, 84, -84];
  const nominalY = startVertical.y + dy * 0.5 + laneOffset + miniLaneOffset + (laneHint.y || 0);
  for (const delta of verticalOffsets) {
    const midY = nominalY + delta;
    candidates.push({
      mode: "vertical",
      points: [startVertical, { x: startVertical.x, y: midY }, { x: endVertical.x, y: midY }, endVertical],
      label: { x: (startVertical.x + endVertical.x) / 2 + 6, y: midY - 6 },
    });
  }
  const horizontalDistance = Math.abs(targetCenter.x - sourceCenter.x);
  if (horizontalDistance >= 90) {
    const sourceSideX = targetCenter.x >= sourceCenter.x ? source.x + sourceSize.width : source.x;
    const targetSideX = targetCenter.x >= sourceCenter.x ? target.x : target.x + targetSize.width;
    const startSide = { x: sourceSideX, y: sourceCenter.y };
    const endSide = { x: targetSideX, y: targetCenter.y };
    const nominalMidX = (startSide.x + endSide.x) / 2 + (laneHint.x || 0);
    const horizontalOffsets = [0, 16, -16, 30, -30, 48, -48, 70, -70, 96, -96];
    for (const delta of horizontalOffsets) {
      const midX = nominalMidX + delta;
      candidates.push({
        mode: "horizontal",
        points: [startSide, { x: midX, y: startSide.y }, { x: midX, y: endSide.y }, endSide],
        label: { x: midX + 6, y: (startSide.y + endSide.y) / 2 - 6 },
      });
    }
  }
  const leftX = Math.min(source.x, target.x) - 28 + (laneHint.x || 0), rightX = Math.max(source.x + sourceSize.width, target.x + targetSize.width) + 28 + (laneHint.x || 0);
  const detourStartY = startVertical.y + (dy >= 0 ? 18 : -18), detourEndY = endVertical.y + (dy >= 0 ? -18 : 18);
  candidates.push({ mode: "detour", points: [startVertical, { x: startVertical.x, y: detourStartY }, { x: leftX, y: detourStartY }, { x: leftX, y: detourEndY }, { x: endVertical.x, y: detourEndY }, endVertical], label: { x: leftX + 6, y: (detourStartY + detourEndY) / 2 - 6 } });
  candidates.push({ mode: "detour", points: [startVertical, { x: startVertical.x, y: detourStartY }, { x: rightX, y: detourStartY }, { x: rightX, y: detourEndY }, { x: endVertical.x, y: detourEndY }, endVertical], label: { x: rightX + 6, y: (detourStartY + detourEndY) / 2 - 6 } });
  return candidates;
}
function spaciousScoreRouteCandidate(candidate, sourceId, targetId, reservedSegments, laneHint = { x: 0, y: 0 }) {
  const segments = spaciousSegmentsFromPoints(candidate.points);
  let crossings = 0, overlaps = 0, blocked = 0, lengthPenalty = 0;
  for (const segment of segments) {
    if (spaciousSegmentBlockedByNodes(segment, sourceId, targetId)) blocked += 1;
    lengthPenalty += Math.abs(segment.x2 - segment.x1) + Math.abs(segment.y2 - segment.y1);
    for (const reserved of reservedSegments) {
      if (reserved.owner === `${sourceId}->${targetId}`) continue;
      if (spaciousSegmentsOverlap(segment, reserved)) overlaps += reserved.hard ? 1 : 0.5;
      else if (spaciousSegmentsCross(segment, reserved)) crossings += reserved.hard ? 1 : 0.5;
    }
  }
  const bends = Math.max(0, segments.length - 1), orientationPenalty = candidate.mode === "horizontal" ? 0 : candidate.mode === "vertical" ? 2 : 6;
  const lanePenalty = (Math.abs(laneHint.x || 0) + Math.abs(laneHint.y || 0)) * 0.03;
  return { score: blocked * 10000000 + overlaps * 2000000 + crossings * 4000 + bends * 4 + lengthPenalty * 0.01 + orientationPenalty + lanePenalty, segments };
}
function spaciousPlannedInternalRoutes() {
  if (spaciousInternalRoutePlanCache) return spaciousInternalRoutePlanCache;
  const result = new Map();
  const reservedSegments = spaciousBuildReservedSegments();
  const laneHints = spaciousInternalBandLaneAssignments();
  const controlEdges = (state.graph?.edges || []).filter(edge => (edge.edge_type || edge.relation_type || "control_flow") === "control_flow");
  const candidates = controlEdges
    .filter(edge => !spaciousDirectHorizontalGeometry(edge.source, edge.target) && !spaciousCorridorEdgeInfo(edge.source, edge.target))
    .map(edge => {
      const source = state.positions?.[edge.source], target = state.positions?.[edge.target];
      const sourceSize = source ? nodeSize(edge.source) : null, targetSize = target ? nodeSize(edge.target) : null;
      const span = source && target && sourceSize && targetSize ? Math.abs((target.y + targetSize.height / 2) - (source.y + sourceSize.height / 2)) : 0;
      return { edge, key: `${edge.source}->${edge.target}`, span };
    })
    .sort((a, b) => a.span - b.span || String(a.edge.source).localeCompare(String(b.edge.source)) || String(a.edge.target).localeCompare(String(b.edge.target)) || String(a.edge.key || "").localeCompare(String(b.edge.key || "")));
  for (const item of candidates) {
    const { edge, key } = item;
    const source = state.positions?.[edge.source], target = state.positions?.[edge.target];
    if (!source || !target) continue;
    const sourceSize = nodeSize(edge.source), targetSize = nodeSize(edge.target);
    const sourceCenter = { x: source.x + sourceSize.width / 2 + spaciousEdgePortOffset(edge.source, edge.source, edge.target, "source"), y: source.y + sourceSize.height / 2 };
    const targetCenter = { x: target.x + targetSize.width / 2 + spaciousEdgePortOffset(edge.target, edge.source, edge.target, "target"), y: target.y + targetSize.height / 2 };
    const lane = deterministicEdgeLane(edge.source, edge.target);
    const laneOffset = (lane - 2) * 8;
    const miniLaneOffset = spaciousInternalMiniLaneOffsets().get(key) || 0;
    const laneHint = laneHints.get(key) || { x: 0, y: 0 };
    const options = spaciousInternalRouteCandidates(edge.source, edge.target, sourceCenter, targetCenter, laneOffset, miniLaneOffset, laneHint);
    let best = null;
    for (const option of options) {
      const scored = spaciousScoreRouteCandidate(option, edge.source, edge.target, reservedSegments, laneHint);
      const candidate = { ...option, score: scored.score, segments: scored.segments };
      if (!best || candidate.score < best.score - 0.001 || (Math.abs(candidate.score - best.score) <= 0.001 && candidate.mode < best.mode)) best = candidate;
    }
    if (best) {
      result.set(key, { path: spaciousPathFromPoints(best.points), label: best.label, mode: best.mode });
      best.segments.forEach(segment => reservedSegments.push({ ...segment, owner: key, hard: false }));
    }
  }
  spaciousInternalRoutePlanCache = result;
  return result;
}
function spaciousInternalMiniLaneOffsets() {
  if (spaciousInternalMiniLaneCache) return spaciousInternalMiniLaneCache;
  const reserved = [];
  const result = new Map();
  const controlEdges = (state.graph?.edges || []).filter(edge => (edge.edge_type || edge.relation_type || "control_flow") === "control_flow");
  const routing = spaciousExternalCorridorLanes();
  const envelope = routing.envelope || spaciousRoutingEnvelope();
  const metrics = treeLayoutMetrics();
  const corridorBaseGap = 34, corridorStep = 34;

  // Direct horizontal edges own their clean path. Other routes move around them.
  for (const edge of controlEdges) {
    const direct = spaciousDirectHorizontalGeometry(edge.source, edge.target);
    if (!direct) continue;
    const source = state.positions?.[edge.source], target = state.positions?.[edge.target];
    if (!source || !target) continue;
    const sourceSize = nodeSize(edge.source), targetSize = nodeSize(edge.target);
    const leftToRight = source.x <= target.x;
    const startX = leftToRight ? source.x + sourceSize.width : source.x;
    const endX = leftToRight ? target.x : target.x + targetSize.width;
    reserved.push({ y: direct.label.y + 6, minX: Math.min(startX, endX), maxX: Math.max(startX, endX), owner: `${edge.source}->${edge.target}` });
  }

  // Corridor horizontal stubs are also real occupied segments; internal routes must not disappear under them.
  for (const edge of controlEdges) {
    if (spaciousDirectHorizontalGeometry(edge.source, edge.target)) continue;
    const info = spaciousCorridorEdgeInfo(edge.source, edge.target);
    if (!info) continue;
    const assignment = routing.lanes.get(`${edge.source}->${edge.target}`) || { side: "right", lane: 0 };
    const lane = assignment.lane;
    const source = state.positions?.[edge.source], target = state.positions?.[edge.target];
    if (!source || !target) continue;
    const sourceSize = nodeSize(edge.source), targetSize = nodeSize(edge.target);
    const sourceCenter = { x: source.x + sourceSize.width / 2 + spaciousEdgePortOffset(edge.source, edge.source, edge.target, "source"), y: source.y + sourceSize.height / 2 };
    const targetCenter = { x: target.x + targetSize.width / 2 + spaciousEdgePortOffset(edge.target, edge.source, edge.target, "target"), y: target.y + targetSize.height / 2 };
    const start = { x: sourceCenter.x, y: targetCenter.y >= sourceCenter.y ? source.y + sourceSize.height : source.y };
    const end = { x: targetCenter.x, y: targetCenter.y >= sourceCenter.y ? target.y : target.y + targetSize.height };
    const corridorX = assignment.side === "left"
      ? Math.max(12, (envelope?.minLeft ?? metrics.margin) - corridorBaseGap - lane * corridorStep)
      : (envelope?.maxRight ?? metrics.minCanvasWidth - metrics.margin) + corridorBaseGap + lane * corridorStep;
    const startStubY = start.y + (info.backEdge ? -24 : 24 + lane * 3);
    const endStubY = end.y + (info.backEdge ? 24 : -24 - lane * 3);
    reserved.push({ y: startStubY, minX: Math.min(start.x, corridorX), maxX: Math.max(start.x, corridorX), owner: `${edge.source}->${edge.target}:start` });
    reserved.push({ y: endStubY, minX: Math.min(end.x, corridorX), maxX: Math.max(end.x, corridorX), owner: `${edge.source}->${edge.target}:end` });
  }

  const candidates = [];
  for (const edge of controlEdges) {
    const key = `${edge.source}->${edge.target}`;
    if (spaciousDirectHorizontalGeometry(edge.source, edge.target) || spaciousCorridorEdgeInfo(edge.source, edge.target)) continue;
    const source = state.positions?.[edge.source], target = state.positions?.[edge.target];
    if (!source || !target) continue;
    const sourceSize = nodeSize(edge.source), targetSize = nodeSize(edge.target);
    const sourceX = source.x + sourceSize.width / 2 + spaciousEdgePortOffset(edge.source, edge.source, edge.target, "source");
    const targetX = target.x + targetSize.width / 2 + spaciousEdgePortOffset(edge.target, edge.source, edge.target, "target");
    const sourceCenterY = source.y + sourceSize.height / 2, targetCenterY = target.y + targetSize.height / 2;
    const startY = targetCenterY >= sourceCenterY ? source.y + sourceSize.height : source.y;
    const endY = targetCenterY >= sourceCenterY ? target.y : target.y + targetSize.height;
    const lane = deterministicEdgeLane(edge.source, edge.target);
    const nominalY = startY + (endY - startY) * 0.5 + (lane - 2) * 8;
    candidates.push({ key, sourceId: edge.source, targetId: edge.target, nominalY, minX: Math.min(sourceX, targetX), maxX: Math.max(sourceX, targetX) });
  }
  candidates.sort((a, b) => a.nominalY - b.nominalY || a.minX - b.minX || a.maxX - b.maxX || a.key.localeCompare(b.key));
  // baseline regression token: const offsets = [0, 7, -7, 14, -14, 21, -21, 28, -28, 35, -35];
  const offsets = [0, 8, -8, 16, -16, 24, -24, 34, -34, 46, -46, 60, -60];
  for (const edge of candidates) {
    let chosen = offsets[offsets.length - 1];
    for (const offset of offsets) {
      const segment = { y: edge.nominalY + offset, minX: edge.minX, maxX: edge.maxX };
      if (!reserved.some(other => spaciousHorizontalOverlap(segment, other))) { chosen = offset; break; }
    }
    result.set(edge.key, chosen);
    reserved.push({ y: edge.nominalY + chosen, minX: edge.minX, maxX: edge.maxX, owner: edge.key });
  }
  spaciousInternalMiniLaneCache = result;
  return result;
}
function spaciousDirectHorizontalGeometry(sourceId, targetId) {
  const source = state.positions?.[sourceId], target = state.positions?.[targetId];
  if (!source || !target) return null;
  const sourceSize = nodeSize(sourceId), targetSize = nodeSize(targetId);
  const sourceCenterY = source.y + sourceSize.height / 2, targetCenterY = target.y + targetSize.height / 2;
  const alignmentTolerance = 10;
  if (Math.abs(sourceCenterY - targetCenterY) > alignmentTolerance) return null;
  const leftToRight = source.x <= target.x;
  const startX = leftToRight ? source.x + sourceSize.width : source.x;
  const endX = leftToRight ? target.x : target.x + targetSize.width;
  if ((leftToRight && endX <= startX) || (!leftToRight && endX >= startX)) return null;
  const y = (sourceCenterY + targetCenterY) / 2;
  const minX = Math.min(startX, endX), maxX = Math.max(startX, endX), clearance = 10;
  for (const node of state.graph?.nodes || []) {
    if (node.id === sourceId || node.id === targetId) continue;
    const pos = state.positions?.[node.id];
    if (!pos) continue;
    const size = nodeSize(node.id);
    const overlapsX = maxX > pos.x - clearance && minX < pos.x + size.width + clearance;
    const crossesY = y >= pos.y - clearance && y <= pos.y + size.height + clearance;
    if (overlapsX && crossesY) return null;
  }
  return {
    path: `M ${startX} ${y} L ${endX} ${y}`,
    label: { x: (startX + endX) / 2 + 6, y: y - 6 },
  };
}
function spaciousCorridorEdgeInfo(sourceId, targetId) {
  const source = state.positions?.[sourceId], target = state.positions?.[targetId];
  if (!source || !target) return null;
  const sourceSize = nodeSize(sourceId), targetSize = nodeSize(targetId), metrics = treeLayoutMetrics();
  const sourceCenterY = source.y + sourceSize.height / 2, targetCenterY = target.y + targetSize.height / 2;
  const downward = targetCenterY >= sourceCenterY;
  const startY = downward ? source.y + sourceSize.height : source.y;
  const endY = downward ? target.y : target.y + targetSize.height;
  const span = Math.abs(endY - startY);
  const longThreshold = (NODE_MIN_HEIGHT + metrics.verticalGap) * 1.65;
  const backEdge = endY - startY <= 0;
  if (!backEdge && span <= longThreshold) return null;
  const sourceCenterX = source.x + sourceSize.width / 2, targetCenterX = target.x + targetSize.width / 2;
  return { sourceId, targetId, startY, endY, minY: Math.min(startY, endY), maxY: Math.max(startY, endY), span, backEdge, midX: (sourceCenterX + targetCenterX) / 2 };
}
function spaciousExternalCorridorLanes() {
  const eligible = [];
  const seen = new Set(), envelope = spaciousRoutingEnvelope();
  for (const edge of state.graph?.edges || []) {
    const relation = edge.edge_type || edge.relation_type || "control_flow";
    if (relation !== "control_flow") continue;
    const key = `${edge.source}->${edge.target}`;
    if (seen.has(key)) continue;
    seen.add(key);
    if (spaciousDirectHorizontalGeometry(edge.source, edge.target)) continue;
    const info = spaciousCorridorEdgeInfo(edge.source, edge.target);
    if (info) eligible.push({ ...info, key });
  }
  eligible.sort((a, b) => a.span - b.span || a.minY - b.minY || a.maxY - b.maxY || a.key.localeCompare(b.key));
  const intervals = { left: [], right: [] }, result = new Map(), clearance = 18;
  const metrics = treeLayoutMetrics(), spanUnit = (NODE_MIN_HEIGHT + metrics.verticalGap) * 1.65;
  const overlaps = (a, b) => a.minY < b.maxY + clearance && a.maxY + clearance > b.minY;
  const firstFreeLane = (side, edge, baseLane) => {
    let lane = baseLane;
    while ((intervals[side][lane] || []).some(other => overlaps(edge, other))) lane += 1;
    return lane;
  };
  const sideLoad = side => intervals[side].reduce((sum, lane) => sum + (lane?.length || 0), 0);
  for (const edge of eligible) {
    const baseLane = Math.max(0, Math.min(3, Math.floor(edge.span / Math.max(1, spanUnit * 1.7))));
    const leftLane = firstFreeLane("left", edge, baseLane), rightLane = firstFreeLane("right", edge, baseLane);
    const leftExit = envelope ? Math.max(0, edge.midX - envelope.minLeft) : 0;
    const rightExit = envelope ? Math.max(0, envelope.maxRight - edge.midX) : 0;
    const leftScore = leftLane * 1000 + leftExit * 0.08 + sideLoad("left") * 16;
    const rightScore = rightLane * 1000 + rightExit * 0.08 + sideLoad("right") * 16;
    let side;
    if (Math.abs(leftScore - rightScore) > 0.001) side = leftScore < rightScore ? "left" : "right";
    else side = deterministicEdgeLane(edge.sourceId, edge.targetId) % 2 ? "left" : "right";
    const lane = side === "left" ? leftLane : rightLane;
    if (!intervals[side][lane]) intervals[side][lane] = [];
    intervals[side][lane].push(edge);
    result.set(edge.key, { side, lane });
  }
  return {
    lanes: result,
    leftLaneCount: intervals.left.length,
    rightLaneCount: intervals.right.length,
    laneCount: Math.max(intervals.left.length, intervals.right.length),
    envelope,
  };
}
function smartSpaciousEdgeGeometry(source, target, sourceId, targetId) {
  const directHorizontal = spaciousDirectHorizontalGeometry(sourceId, targetId);
  if (directHorizontal) return directHorizontal;
  const sourceSize = nodeSize(sourceId), targetSize = nodeSize(targetId), metrics = treeLayoutMetrics();
  const sourceCenter = { x: source.x + sourceSize.width / 2 + spaciousEdgePortOffset(sourceId, sourceId, targetId, "source"), y: source.y + sourceSize.height / 2 };
  const targetCenter = { x: target.x + targetSize.width / 2 + spaciousEdgePortOffset(targetId, sourceId, targetId, "target"), y: target.y + targetSize.height / 2 };
  const start = { x: sourceCenter.x, y: targetCenter.y >= sourceCenter.y ? source.y + sourceSize.height : source.y };
  const end = { x: targetCenter.x, y: targetCenter.y >= sourceCenter.y ? target.y : target.y + targetSize.height };
  const dy = end.y - start.y;
  const corridorInfo = spaciousCorridorEdgeInfo(sourceId, targetId);
  if (corridorInfo) {
    const routing = spaciousExternalCorridorLanes();
    const assignment = routing.lanes.get(`${sourceId}->${targetId}`) || { side: "right", lane: 0 };
    const lane = assignment.lane, envelope = routing.envelope || spaciousRoutingEnvelope();
    const corridorBaseGap = 34, corridorStep = 34;
    const corridorX = assignment.side === "left"
      ? Math.max(12, (envelope?.minLeft ?? metrics.margin) - corridorBaseGap - lane * corridorStep)
      : (envelope?.maxRight ?? metrics.minCanvasWidth - metrics.margin) + corridorBaseGap + lane * corridorStep;
    const startStubY = start.y + (corridorInfo.backEdge ? -24 : 24 + lane * 3);
    const endStubY = end.y + (corridorInfo.backEdge ? 24 : -24 - lane * 3);
    return {
      path: `M ${start.x} ${start.y} L ${start.x} ${startStubY} L ${corridorX} ${startStubY} L ${corridorX} ${endStubY} L ${end.x} ${endStubY} L ${end.x} ${end.y}`,
      label: { x: corridorX + (assignment.side === "left" ? -8 : 6), y: (startStubY + endStubY) / 2 },
    };
  }
  const planned = spaciousPlannedInternalRoutes().get(`${sourceId}->${targetId}`);
  if (planned) return planned;
  const lane = deterministicEdgeLane(sourceId, targetId);
  const laneOffset = (lane - 2) * 8;
  const miniLaneOffset = spaciousInternalMiniLaneOffsets().get(`${sourceId}->${targetId}`) || 0;
  const midY = start.y + dy * 0.5 + laneOffset + miniLaneOffset;
  return {
    path: `M ${start.x} ${start.y} L ${start.x} ${midY} L ${end.x} ${midY} L ${end.x} ${end.y}`,
    label: { x: (start.x + end.x) / 2 + 6, y: midY - 6 },
  };
}
function edgeGeometry(source, target, sourceId, targetId) {
  if ((state.treeLayoutDensity || "normal") === "spacious") return smartSpaciousEdgeGeometry(source, target, sourceId, targetId);
  const sourceSize = nodeSize(sourceId), targetSize = nodeSize(targetId);
  const sourceCenter = { x: source.x + sourceSize.width / 2, y: source.y + sourceSize.height / 2 };
  const targetCenter = { x: target.x + targetSize.width / 2, y: target.y + targetSize.height / 2 };
  const dx = targetCenter.x - sourceCenter.x, dy = targetCenter.y - sourceCenter.y;
  if (dx === 0 && dy === 0) {
    const start = { x: source.x + sourceSize.width, y: source.y + sourceSize.height / 2 - 12 };
    const end = { x: source.x + sourceSize.width, y: source.y + sourceSize.height / 2 + 12 };
    return { path: `M ${start.x} ${start.y} C ${start.x + 72} ${start.y - 48}, ${end.x + 72} ${end.y + 48}, ${end.x} ${end.y}`, label: { x: start.x + 78, y: source.y + sourceSize.height / 2 } };
  }
  let start, end, controlOne, controlTwo;
  if (Math.abs(dx) >= Math.abs(dy)) {
    const direction = Math.sign(dx) || 1;
    start = { x: direction > 0 ? source.x + sourceSize.width : source.x, y: sourceCenter.y };
    end = { x: direction > 0 ? target.x : target.x + targetSize.width, y: targetCenter.y };
    const bend = Math.max(48, Math.abs(dx) * 0.45);
    controlOne = { x: start.x + direction * bend, y: start.y };
    controlTwo = { x: end.x - direction * bend, y: end.y };
  } else {
    const direction = Math.sign(dy) || 1;
    start = { x: sourceCenter.x, y: direction > 0 ? source.y + sourceSize.height : source.y };
    end = { x: targetCenter.x, y: direction > 0 ? target.y : target.y + targetSize.height };
    const bend = Math.max(48, Math.abs(dy) * 0.45);
    controlOne = { x: start.x, y: start.y + direction * bend };
    controlTwo = { x: end.x, y: end.y - direction * bend };
  }
  return { path: `M ${start.x} ${start.y} C ${controlOne.x} ${controlOne.y}, ${controlTwo.x} ${controlTwo.y}, ${end.x} ${end.y}`, label: { x: (start.x + end.x) / 2 + 6, y: (start.y + end.y) / 2 - 6 } };
}

function spaciousParseOrthogonalPath(path) {
  const values = String(path || "").match(/-?\d+(?:\.\d+)?/g)?.map(Number) || [];
  if (!values.length || values.length % 2) return null;
  const commands = String(path || "").match(/[MLC]/g) || [];
  if (commands.some(command => command === "C")) return null;
  const points = [];
  for (let index = 0; index < values.length; index += 2) points.push({ x: values[index], y: values[index + 1] });
  return points.length >= 2 ? points : null;
}
function spaciousRouteSegmentsWithRoles(points) {
  const segments = spaciousSegmentsFromPoints(points);
  return segments.map((segment, index) => ({ ...segment, terminal: index === 0 || index === segments.length - 1, segmentIndex: index }));
}
function spaciousTerminalStemInvariant(originalPoints, candidatePoints) {
  if (!originalPoints || !candidatePoints || originalPoints.length !== candidatePoints.length || originalPoints.length < 2) return false;
  const samePoint = (a,b) => Math.abs(a.x-b.x) < 0.001 && Math.abs(a.y-b.y) < 0.001;
  if (!samePoint(originalPoints[0], candidatePoints[0]) || !samePoint(originalPoints.at(-1), candidatePoints.at(-1))) return false;
  const originalSegments = spaciousSegmentsFromPoints(originalPoints), candidateSegments = spaciousSegmentsFromPoints(candidatePoints);
  if (!originalSegments.length || originalSegments.length !== candidateSegments.length) return false;
  const vectorSign = segment => segment.orientation === "h" ? Math.sign(segment.x2-segment.x1) : Math.sign(segment.y2-segment.y1);
  const length = segment => segment.orientation === "h" ? Math.abs(segment.x2-segment.x1) : Math.abs(segment.y2-segment.y1);
  const originalFirst=originalSegments[0], candidateFirst=candidateSegments[0], originalLast=originalSegments.at(-1), candidateLast=candidateSegments.at(-1);
  if (originalFirst.orientation!==candidateFirst.orientation || originalLast.orientation!==candidateLast.orientation) return false;
  if (vectorSign(originalFirst)!==vectorSign(candidateFirst) || vectorSign(originalLast)!==vectorSign(candidateLast)) return false;
  return length(candidateFirst)>=12 && length(candidateLast)>=12;
}
function spaciousRouteConflictScore(points, sourceId, targetId, otherRoutes) {
  const segments = spaciousSegmentsFromPoints(points);
  let overlaps = 0, crossings = 0, blocked = 0, terminalConflicts = 0;
  for (const segment of segments) {
    if (spaciousSegmentBlockedByNodes(segment, sourceId, targetId, 8)) blocked += 1;
    for (const other of otherRoutes) {
      const otherSegments = other.segmentRoles || spaciousRouteSegmentsWithRoles(other.points || []);
      for (const otherSegment of otherSegments) {
        const overlap = spaciousSegmentsOverlap(segment, otherSegment, 3), cross = !overlap && spaciousSegmentsCross(segment, otherSegment, 1);
        if (!overlap && !cross) continue;
        if (otherSegment.terminal) terminalConflicts += 1;
        else if (overlap) overlaps += 1;
        else crossings += 1;
      }
    }
  }
  return { score: blocked * 10000000 + terminalConflicts * 8000000 + overlaps * 2000000 + crossings * 4000, overlaps, crossings, blocked, terminalConflicts };
}
function spaciousShiftInternalSegment(points, segmentIndex, delta) {
  const next = points.map(point => ({ ...point }));
  const a = next[segmentIndex], b = next[segmentIndex + 1];
  if (!a || !b || !delta) return next;
  if (a.y === b.y) { a.y += delta; b.y += delta; }
  else if (a.x === b.x) { a.x += delta; b.x += delta; }
  return next;
}
function spaciousRouteWithinCanvas(points) {
  const metrics = treeLayoutMetrics(), nodes = state.graph?.nodes || [];
  const maxBottom = Math.max(metrics.minCanvasWidth ? 0 : 0, ...nodes.map(node => { const pos = state.positions?.[node.id], size = nodeSize(node.id); return pos ? pos.y + size.height : 0; }));
  const maxRight = Math.max(0, ...nodes.map(node => { const pos = state.positions?.[node.id], size = nodeSize(node.id); return pos ? pos.x + size.width : 0; }));
  const maxY = Math.max(700, maxBottom + metrics.margin + 120), maxX = Math.max(metrics.minCanvasWidth, maxRight + metrics.margin + 120);
  return points.every(point => point.x >= 8 && point.y >= 8 && point.x <= maxX && point.y <= maxY);
}
function spaciousLabelForPoints(points, fallback) {
  const segments = spaciousSegmentsFromPoints(points);
  const horizontal = segments.filter(segment => segment.orientation === "h").sort((a, b) => Math.abs(b.x2 - b.x1) - Math.abs(a.x2 - a.x1))[0];
  if (horizontal) return { x: (horizontal.x1 + horizontal.x2) / 2 + 6, y: horizontal.y1 - 6 };
  const vertical = segments.filter(segment => segment.orientation === "v").sort((a, b) => Math.abs(b.y2 - b.y1) - Math.abs(a.y2 - a.y1))[0];
  if (vertical) return { x: vertical.x1 + 6, y: (vertical.y1 + vertical.y2) / 2 };
  return fallback;
}
function spaciousPostProcessGeometries(items) {
  if ((state.treeLayoutDensity || "normal") !== "spacious") return items;
  const routes = items.map(item => {
    const points = spaciousParseOrthogonalPath(item.geometry?.path);
    return { ...item, points, originalPoints: points ? points.map(point => ({...point})) : null, segments: points ? spaciousSegmentsFromPoints(points) : [], segmentRoles: points ? spaciousRouteSegmentsWithRoles(points) : [] };
  });
  const movable = routes.filter(route => route.points && route.points.length >= 4 && (route.relation || "control_flow") === "control_flow");
  const conflictCount = route => {
    const others = routes.filter(other => other !== route && other.segments?.length);
    const score = spaciousRouteConflictScore(route.points, route.edge.source, route.edge.target, others);
    return score.terminalConflicts * 1000 + score.overlaps * 10 + score.crossings + score.blocked * 100;
  };
  movable.sort((a, b) => conflictCount(b) - conflictCount(a) || String(a.edge.source).localeCompare(String(b.edge.source)) || String(a.edge.target).localeCompare(String(b.edge.target)));
  const offsets = [0, 8, -8, 16, -16, 24, -24, 36, -36, 48, -48, 64, -64, 84, -84, 108, -108, 140, -140, 180, -180];
  for (let pass = 0; pass < 2; pass += 1) {
    for (const route of movable) {
      let points = route.points;
      for (let segmentIndex = 1; segmentIndex < points.length - 2; segmentIndex += 1) {
        const segment = spaciousSegmentsFromPoints(points)[segmentIndex];
        if (!segment) continue;
        const length = segment.orientation === "h" ? Math.abs(segment.x2 - segment.x1) : Math.abs(segment.y2 - segment.y1);
        if (length < 120) continue;
        const others = routes.filter(other => other !== route && other.segments?.length);
        const baseline = spaciousRouteConflictScore(points, route.edge.source, route.edge.target, others);
        if (!baseline.terminalConflicts && !baseline.overlaps && baseline.crossings < 2) continue;
        let bestPoints = points, best = baseline;
        for (const offset of offsets.slice(1)) {
          const candidate = spaciousShiftInternalSegment(points, segmentIndex, offset);
          if (!spaciousRouteWithinCanvas(candidate) || !spaciousTerminalStemInvariant(route.originalPoints, candidate)) continue;
          const scored = spaciousRouteConflictScore(candidate, route.edge.source, route.edge.target, others);
          const movementPenalty = Math.abs(offset) * 0.25;
          if (scored.score + movementPenalty < best.score - 0.001) { best = { ...scored, score: scored.score + movementPenalty }; bestPoints = candidate; }
        }
        points = bestPoints;
      }
      route.points = points;
      route.segments = spaciousSegmentsFromPoints(points);
      route.segmentRoles = spaciousRouteSegmentsWithRoles(points);
      route.geometry = { ...route.geometry, path: spaciousPathFromPoints(points), label: spaciousLabelForPoints(points, route.geometry.label) };
    }
  }
  return routes;
}
function drawEdges() {
  resetSpaciousInternalMiniLaneCache();
  const planned = [];
  state.graph.edges.forEach(edge => {
    const source = state.positions[edge.source], target = state.positions[edge.target];
    if (!source || !target) return;
    const relation = edge.edge_type || edge.relation_type || "control_flow";
    planned.push({ edge, relation, geometry: edgeGeometry(source, target, edge.source, edge.target) });
  });
  const routed = spaciousPostProcessGeometries(planned);
  routed.forEach(({ edge, relation, geometry }) => {
    const hit = document.createElementNS("http://www.w3.org/2000/svg", "path");
    hit.classList.add("edge-hit");
    hit.setAttribute("d", geometry.path);
    edges.append(hit);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
    line.classList.add("edge-line");
    line.classList.add(`edge-${relation}`);
    if (edge.storage === "gate_route") line.classList.add("gate-route");
    line.setAttribute("d", geometry.path);
    edges.append(line);
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.classList.add("edge-label");
    label.classList.add(`edge-label-${relation}`);
    label.setAttribute("x", String(geometry.label.x));
    label.setAttribute("y", String(geometry.label.y));
    label.textContent = relation === "control_flow" ? (edge.key || "") : (relation === "declares_output" ? (edge.label || "declares output") : (edge.state_path || edge.artifact_path || relation));
    edges.append(label);
  });
}
function makeDraggable(element) {
  let drag = null;
  let suppressClick = false;
  const redrawDraggedGraph = () => {
    resizeCanvas();
    edges.innerHTML = '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#6680ae"/></marker></defs>';
    drawEdges(); drawDialogPathOverlay(); drawReplayPathOverlay(); drawLivePathOverlay();
  };
  const move = event => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const dx = event.clientX - drag.pointerX, dy = event.clientY - drag.pointerY;
    if (!drag.moved && Math.hypot(dx, dy) < 3) return;
    drag.moved = true;
    suppressClick = true;
    event.preventDefault();
    const id = element.dataset.id;
    state.manualPositions.add(id);
    const next = { x: Math.max(0, drag.nodeX + dx), y: Math.max(0, drag.nodeY + dy) };
    state.positions[id] = next;
    element.style.left = `${next.x}px`; element.style.top = `${next.y}px`;
    redrawDraggedGraph();
  };
  const end = event => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    try { if (element.hasPointerCapture?.(event.pointerId)) element.releasePointerCapture(event.pointerId); } catch (_) {}
    drag = null;
    window.removeEventListener('pointermove', move, true);
    window.removeEventListener('pointerup', end, true);
    window.removeEventListener('pointercancel', end, true);
  };
  element.addEventListener('pointerdown', event => {
    if (event.button !== 0 || state.pendingTransitionSource || event.target.closest?.('button,a,input,textarea,select')) return;
    const current = state.positions[element.dataset.id]; if (!current) return;
    suppressClick = false;
    drag = { pointerId: event.pointerId, pointerX: event.clientX, pointerY: event.clientY, nodeX: current.x, nodeY: current.y, moved: false };
    event.preventDefault();
    event.stopPropagation();
    try { element.setPointerCapture?.(event.pointerId); } catch (_) {}
    window.addEventListener('pointermove', move, true);
    window.addEventListener('pointerup', end, true);
    window.addEventListener('pointercancel', end, true);
  });
  element.addEventListener('click', event => {
    if (!suppressClick) return;
    suppressClick = false;
    event.preventDefault(); event.stopImmediatePropagation();
  }, true);
}
function selectNode(id, additive = false) {
  if (additive) {
    if (state.selectedNodes.has(id)) state.selectedNodes.delete(id); else state.selectedNodes.add(id);
    state.selected = state.selectedNodes.has(id) ? id : (state.selectedNodes.values().next().value || null);
  } else {
    state.selectedNodes = new Set([id]);
    state.selected = id;
  }
  state.selectedEdge = null; hideEdgeMenu(); render();
}
function selectTransition(edge) { state.selectedEdge = edge; renderInspector(); }
const sectionLabels = {
  title: ["Title", "title"], id: ["ID", "id"], kind: ["Node type", "kind"], purpose: ["Purpose", "purpose"], question: ["Question", "question"],
  inputs: ["Input parameters", "inputs"], outputs: ["Output parameters", "outputs"], questions: ["Analyst questions", "questions"],
  user_interaction: ["Analyst interaction", "user_interaction"], entry_gate: ["Entry gate", "entry_gate"], exit_gate: ["Exit gate", "exit_gate"],
  on_gap: ["Gap handling", "on_gap"], transitions: ["Transitions", "transitions"], on_answer: ["Answer transitions", "on_answer"],
  route_context: ["Route context", "route_context"], artifact_contract: ["Artifact contract", "artifact_contract"],
  expected_artifacts: ["Expected artifacts", "expected_artifacts"], order: ["Order", "order"], terminal: ["Terminal node", "terminal"],
  method: ["Evaluation method", "method"], trust_class: ["Trust class", "trust_class"], condition: ["Gate condition", "condition"],
  on_pass: ["On pass", "on_pass"], on_fail: ["On fail", "on_fail"], severity: ["Failure severity", "severity"],
};
function yamlBlock(key, value) { const content = value.trim() || "null"; const lines = content.split("\n"); return lines.length === 1 ? `${key}: ${lines[0]}` : `${key}:\n${lines.map(line => `  ${line}`).join("\n")}`; }
function updateYamlPreview() {
  const preview = document.querySelector("#node-yaml-preview"); preview.innerHTML = "";
  if (state.templateInspectorData?.entity_type === "output" && state.selected === state.templateInspectorData.node_id) {
    preview.textContent = yamlLike(state.templateInspectorData.record || {});
    return;
  }
  document.querySelectorAll("[data-section-key]").forEach(field => { const block = document.createElement("span"); block.textContent = `${yamlBlock(field.dataset.sectionKey, field.value)}\n`; if (field.value !== field.dataset.originalValue) block.className = "yaml-change"; preview.append(block); });
}
function showInspectorTab(tab) {
  state.inspectorTab = tab;
  document.querySelector("#node-fields-view").hidden = tab !== "fields";
  document.querySelector("#node-yaml-view").hidden = tab !== "yaml";
  document.querySelector("#template-inspector-view").hidden = tab !== "references";
  document.querySelector("#node-explanation-view").hidden = tab !== "explanation";
  document.querySelectorAll("[data-inspector-tab]").forEach(button => button.classList.toggle("active", button.dataset.inspectorTab === tab));
  if (tab === "yaml") updateYamlPreview();
  if (tab === "references") renderTemplateInspectorTab();
  if (tab === "explanation") renderNodeExplanationTab();
}

function replayPrettyValue(value) {
  if (typeof value === "string") return value;
  try { return JSON.stringify(value, null, 2); } catch (_) { return String(value); }
}
function renderReplayDecision(container, decision) {
  const bubble = document.createElement("div"); bubble.className = "replay-bubble analyst";
  const role = document.createElement("strong"); role.textContent = "Analyst · accepted decision"; bubble.append(role);
  const meta = document.createElement("div"); meta.className = "replay-decision-meta";
  meta.textContent = [decision?.decision_id, decision?.checkpoint_id ? `checkpoint ${decision.checkpoint_id}` : null].filter(Boolean).join(" · "); bubble.append(meta);
  const values = document.createElement("pre"); values.className = "replay-values"; values.textContent = replayPrettyValue(decision?.accepted_values); bubble.append(values);
  container.append(bubble);
}
function replayGraphHasElement(id) {
  return Boolean(id && (state.graph?.nodes || []).some(item => item.id === id) && state.positions?.[id]);
}
function updateReplayFocusVisuals(id) {
  state.replayFocusId = id || null;
  canvas.querySelectorAll('.node.replay-current-node').forEach(el => el.classList.remove('replay-current-node'));
  document.querySelectorAll('#replay-transcript .replay-step.replay-sync-current').forEach(el => el.classList.remove('replay-sync-current'));
  if (!id) return;
  const graphEl = canvas.querySelector(`.node[data-id="${CSS.escape(id)}"]`);
  if (graphEl) graphEl.classList.add('replay-current-node');
  const stepEl = document.querySelector(`#replay-transcript .replay-step[data-node-id="${CSS.escape(id)}"]`);
  if (stepEl) stepEl.classList.add('replay-sync-current');
}
function focusReplayGraphElement(id, behavior = 'smooth') {
  if (!replayGraphHasElement(id)) return;
  const pos = state.positions[id];
  state.selected = id; state.selectedNodes = new Set([id]); state.selectedEdge = null;
  updateReplayFocusVisuals(id);
  requestAnimationFrame(() => {
    workspace.scrollTo({
      left: Math.max(0, pos.x + NODE_WIDTH / 2 - workspace.clientWidth / 2),
      top: Math.max(0, pos.y + nodeHeight(id) / 2 - workspace.clientHeight / 2),
      behavior,
    });
    updateReplayFocusVisuals(id);
  });
}
function syncReplayFromInspectorScroll() {
  if (state.panelTab !== 'replay' || !state.replayData) return;
  const inspector = document.querySelector('#inspector');
  const steps = [...document.querySelectorAll('#replay-transcript .replay-step[data-node-id]')].filter(step => replayGraphHasElement(step.dataset.nodeId));
  if (!inspector || !steps.length) return;
  const rect = inspector.getBoundingClientRect();
  const centerY = rect.top + rect.height / 2;
  let best = null, bestDistance = Infinity;
  for (const step of steps) {
    const r = step.getBoundingClientRect();
    const stepCenter = r.top + r.height / 2;
    const distance = Math.abs(stepCenter - centerY);
    if (distance < bestDistance) { bestDistance = distance; best = step; }
  }
  const id = best?.dataset.nodeId;
  if (id && id !== state.replayFocusId) focusReplayGraphElement(id, 'smooth');
}
function replayDurationText(ms){const n=Number(ms);if(!Number.isFinite(n))return"";if(n<1000)return`${Math.round(n)} ms`;return`${(n/1000).toFixed(n<10000?2:1)} s`;}
function replayNumber(value){const n=Number(value);return Number.isFinite(n)?n.toLocaleString():"";}
function replayAddMetric(host,label,value,kind=""){if(value===null||value===undefined||value==="")return;const badge=document.createElement("span");badge.className=`replay-metric-badge${kind?` ${kind}`:""}`;badge.textContent=`${label}: ${value}`;host.append(badge);}
function replayStructuredScalar(value){
  if(value===null)return "null";
  if(value===undefined)return "—";
  if(typeof value==="boolean")return value?"true":"false";
  if(typeof value==="number")return Number.isFinite(value)?value.toLocaleString():String(value);
  if(typeof value==="string")return value||"(empty)";
  if(Array.isArray(value))return `${value.length} item${value.length===1?"":"s"}`;
  if(typeof value==="object")return `object · ${Object.keys(value).length} field${Object.keys(value).length===1?"":"s"}`;
  return String(value);
}
function replayFileAccessCode(row){
  const read=Boolean(row?.read_observed),write=Boolean(row?.write_observed);
  return read&&write?"RW":read?"R":write?"W":"—";
}
function replayFileAccessTitle(row){
  const code=replayFileAccessCode(row);
  return code==="RW"?"Observed read and write access":code==="R"?"Observed read access":code==="W"?"Observed write access":"No read/write access was observed";
}
function replayExactReadBytes(row){
  for(const key of ["exact_read_bytes","read_bytes","bytes_read","observed_read_bytes"]){const value=row?.[key];if(value!==null&&value!==undefined&&Number.isFinite(Number(value)))return Number(value);}
  return null;
}
function replayExactWriteBytes(row){
  for(const key of ["exact_write_bytes","write_bytes","bytes_written","observed_write_bytes"]){const value=row?.[key];if(value!==null&&value!==undefined&&Number.isFinite(Number(value)))return Number(value);}
  return null;
}
function replayLooksLikeObservedFiles(value){
  return Array.isArray(value)&&value.length>0&&value.every(row=>row&&typeof row==="object"&&!Array.isArray(row)&&("path" in row)&&("read_observed" in row||"write_observed" in row||"file_size_bytes" in row));
}
function replayObservedFilesSummary(rows){
  const root=document.createElement("div");root.className="replay-structured-summary replay-files-summary";
  const wrap=document.createElement("div");wrap.className="replay-structured-table-wrap";const table=document.createElement("table");table.className="replay-structured-table replay-observed-files-table";
  const hasReadBytes=rows.some(row=>replayExactReadBytes(row)!=null),hasWriteBytes=rows.some(row=>replayExactWriteBytes(row)!=null);
  const columns=[{key:"path",label:"Path"},{key:"access",label:"Access"},{key:"file_size_bytes",label:"File size"}];
  if(hasReadBytes)columns.push({key:"read_bytes",label:"Read bytes"});if(hasWriteBytes)columns.push({key:"write_bytes",label:"Written bytes"});
  const thead=document.createElement("thead"),trh=document.createElement("tr");columns.forEach(col=>{const th=document.createElement("th");th.textContent=col.label;if(col.key==="access")th.title="R = observed read, W = observed write, RW = both";trh.append(th);});thead.append(trh);table.append(thead);
  const tbody=document.createElement("tbody");rows.forEach(row=>{const tr=document.createElement("tr");columns.forEach(col=>{const td=document.createElement("td");if(col.key==="access"){td.textContent=replayFileAccessCode(row);td.title=replayFileAccessTitle(row);td.className="replay-access-code";}else if(col.key==="file_size_bytes"){td.textContent=row.file_size_bytes!=null?`${replayNumber(row.file_size_bytes)} B`:"—";td.title="File size from evidence; not bytes read by the model.";}else if(col.key==="read_bytes"){const n=replayExactReadBytes(row);td.textContent=n==null?"—":`${replayNumber(n)} B`;}else if(col.key==="write_bytes"){const n=replayExactWriteBytes(row);td.textContent=n==null?"—":`${replayNumber(n)} B`;}else{td.textContent=String(row.path||"—");td.title=td.textContent;}tr.append(td);});tbody.append(tr);});table.append(tbody);wrap.append(table);root.append(wrap);
  const note=document.createElement("div");note.className="replay-structured-note";note.textContent="Access shows observed file activity (R / W / RW). File size is metadata and must not be interpreted as bytes read. Exact byte columns appear only when exact byte evidence exists.";root.append(note);return root;
}
function replayStructuredSummary(value){
  const root=document.createElement("div");root.className="replay-structured-summary";
  if(Array.isArray(value)){
    if(!value.length){root.textContent="No items";return root;}
    if(replayLooksLikeObservedFiles(value))return replayObservedFilesSummary(value);
    const objectRows=value.filter(item=>item&&typeof item==="object"&&!Array.isArray(item));
    if(objectRows.length===value.length){
      const scalarKeys=[];const seen=new Set();
      for(const row of objectRows){for(const [key,val] of Object.entries(row)){if(seen.has(key))continue;if(val===null||["string","number","boolean"].includes(typeof val)){seen.add(key);scalarKeys.push(key);}}}
      const columns=scalarKeys.slice(0,8);
      if(columns.length){
        const wrap=document.createElement("div");wrap.className="replay-structured-table-wrap";const table=document.createElement("table");table.className="replay-structured-table";
        const thead=document.createElement("thead"),trh=document.createElement("tr");columns.forEach(key=>{const th=document.createElement("th");th.textContent=key;trh.append(th);});thead.append(trh);table.append(thead);
        const tbody=document.createElement("tbody");objectRows.forEach(row=>{const tr=document.createElement("tr");columns.forEach(key=>{const td=document.createElement("td");td.textContent=replayStructuredScalar(row[key]);td.title=td.textContent;tr.append(td);});tbody.append(tr);});table.append(tbody);wrap.append(table);root.append(wrap);
        if(scalarKeys.length>columns.length){const note=document.createElement("div");note.className="replay-structured-note";note.textContent=`Showing ${columns.length} of ${scalarKeys.length} scalar fields. Use JSON for full data.`;root.append(note);}return root;
      }
    }
    const list=document.createElement("div");list.className="replay-structured-list";value.forEach((item,index)=>{const row=document.createElement("div");row.className="replay-structured-row";const key=document.createElement("span");key.className="replay-structured-key";key.textContent=`#${index+1}`;const val=document.createElement("span");val.className="replay-structured-value";val.textContent=replayStructuredScalar(item);row.append(key,val);list.append(row);});root.append(list);return root;
  }
  if(value&&typeof value==="object"){
    const list=document.createElement("div");list.className="replay-structured-list";
    for(const [key,item] of Object.entries(value)){
      const row=document.createElement("div");row.className="replay-structured-row";const k=document.createElement("span");k.className="replay-structured-key";k.textContent=key;const val=document.createElement("span");val.className="replay-structured-value";
      if(item&&typeof item==="object"){
        const nested=document.createElement("details");nested.className="replay-structured-nested";const sum=document.createElement("summary");sum.textContent=replayStructuredScalar(item);nested.append(sum,replayStructuredSummary(item));val.append(nested);
      }else val.textContent=replayStructuredScalar(item);
      row.append(k,val);list.append(row);
    }
    root.append(list);return root;
  }
  root.textContent=replayStructuredScalar(value);return root;
}
async function replayCopyJson(button,value){
  const json=JSON.stringify(value,null,2);let ok=false;
  try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(json);ok=true;}}catch{}
  if(!ok){const ta=document.createElement("textarea");ta.value=json;ta.style.position="fixed";ta.style.opacity="0";document.body.append(ta);ta.select();try{ok=document.execCommand("copy");}catch{}ta.remove();}
  const old=button.textContent;button.textContent=ok?"Copied":"Copy failed";setTimeout(()=>{button.textContent=old;},1200);
}
function replayAddJsonDetails(host,label,value){
  if(value===null||value===undefined||(typeof value==="object"&&!Object.keys(value||{}).length))return;
  const details=document.createElement("details");details.className="replay-details replay-structured-details";const summary=document.createElement("summary");summary.textContent=label;details.append(summary);
  const viewer=document.createElement("div");viewer.className="replay-structured-viewer";
  const tabs=document.createElement("div");tabs.className="replay-structured-tabs";tabs.setAttribute("role","tablist");
  const summaryTab=document.createElement("button");summaryTab.type="button";summaryTab.className="active";summaryTab.textContent="Summary";summaryTab.setAttribute("role","tab");summaryTab.setAttribute("aria-selected","true");
  const jsonTab=document.createElement("button");jsonTab.type="button";jsonTab.textContent="JSON";jsonTab.setAttribute("role","tab");jsonTab.setAttribute("aria-selected","false");tabs.append(summaryTab,jsonTab);viewer.append(tabs);
  const summaryPane=document.createElement("div");summaryPane.className="replay-structured-pane summary-pane";summaryPane.append(replayStructuredSummary(value));
  const jsonPane=document.createElement("div");jsonPane.className="replay-structured-pane json-pane";jsonPane.hidden=true;
  const jsonTools=document.createElement("div");jsonTools.className="replay-json-tools";const copy=document.createElement("button");copy.type="button";copy.className="replay-json-copy";copy.textContent="Copy JSON";copy.addEventListener("click",()=>replayCopyJson(copy,value));jsonTools.append(copy);jsonPane.append(jsonTools);
  const pre=document.createElement("pre");pre.className="replay-values compact";pre.textContent=JSON.stringify(value,null,2);jsonPane.append(pre);viewer.append(summaryPane,jsonPane);
  const activate=mode=>{const json=mode==="json";summaryPane.hidden=json;jsonPane.hidden=!json;summaryTab.classList.toggle("active",!json);jsonTab.classList.toggle("active",json);summaryTab.setAttribute("aria-selected",json?"false":"true");jsonTab.setAttribute("aria-selected",json?"true":"false");};
  summaryTab.addEventListener("click",()=>activate("summary"));jsonTab.addEventListener("click",()=>activate("json"));details.append(viewer);host.append(details);
}
function renderCanonicalReplayEvent(host,event){
  const type=String(event?.event_type||"");const box=document.createElement("div");box.className=`replay-event ${type.toLowerCase().replace(/_/g,"-")}`;
  const label=document.createElement("span");label.className="replay-event-label";label.textContent=type==="ASSISTANT_MESSAGE"?"Assistant · verbatim":type==="ANALYST_MESSAGE"?"Analyst · verbatim":type==="MODEL_ACTION"?"Model action":type==="PAUSE"?"Pause":type==="RESUME"?"Resume":type||"Event";box.append(label);
  if(type==="ASSISTANT_MESSAGE"||type==="ANALYST_MESSAGE"){const body=document.createElement("div");body.className="replay-event-markdown";body.innerHTML=renderBasicMarkdown(event.text||"");box.append(body);}
  else if(type==="MODEL_ACTION"){
    const body=document.createElement("div");body.className="replay-action-summary";body.textContent=event.action_summary||event.action_type||"Structured model action";box.append(body);
    const tags=document.createElement("div");tags.className="replay-action-tags";
    [event.action_type,event.status,event.route,event.to_node?`→ ${event.to_node}`:null].filter(Boolean).forEach(value=>{const tag=document.createElement("span");tag.className="replay-action-tag";tag.textContent=value;tags.append(tag);});if(tags.childNodes.length)box.append(tags);
    if(event.changed_paths?.length){const paths=document.createElement("div");paths.className="replay-decision-meta";paths.textContent=`Changed: ${event.changed_paths.join(", ")}`;box.append(paths);}
    if(event.decision_ids?.length){const decisions=document.createElement("div");decisions.className="replay-decision-meta";decisions.textContent=`Decisions: ${event.decision_ids.join(", ")}`;box.append(decisions);}
    replayAddJsonDetails(box,"State patch",event.state_patch);replayAddJsonDetails(box,"Structured result",event.structured_result);
  }
  if(event.timestamp){const meta=document.createElement("div");meta.className="replay-decision-meta";meta.textContent=event.timestamp;box.append(meta);}host.append(box);
}
function renderReplayFileActions(step,actions){if(!actions?.length)return;const details=document.createElement("details");details.className="replay-details";const summary=document.createElement("summary");summary.textContent=`Files / tools · ${actions.length} observation${actions.length===1?"":"s"}`;details.append(summary);const list=document.createElement("div");list.className="replay-files-list";
  actions.forEach(action=>{const item=document.createElement("div");item.className="replay-file-action";const coverage=action.coverage_class||action.coverage_mode||"OBSERVED";const command=Array.isArray(action.command)?action.command.join(" "):action.command;const main=action.path||command||action.event||"File/tool observation";item.textContent=`${coverage} · ${main}`;const meta=[];if(action.file_size_bytes!=null)meta.push(`file size ${replayNumber(action.file_size_bytes)} B`);if(action.exact_observed_bytes!=null)meta.push(`exact observed ${replayNumber(action.exact_observed_bytes)} B`);if(action.sum_file_size_bytes_for_read_files!=null)meta.push(`sum file sizes ${replayNumber(action.sum_file_size_bytes_for_read_files)} B`);if(action.exit_code!=null)meta.push(`exit ${action.exit_code}`);if(meta.length){const m=document.createElement("div");m.className="replay-decision-meta";m.textContent=meta.join(" · ");item.append(m);}if(action.files?.length)replayAddJsonDetails(item,`Observed files (${action.files.length}${action.files.length>=40?"+":""})`,action.files);list.append(item);});details.append(list);step.append(details);
}
function renderReplay() {
  const empty=document.querySelector("#replay-empty"),view=document.querySelector("#replay-view"),header=document.querySelector("#replay-header"),note=document.querySelector("#replay-note"),transcript=document.querySelector("#replay-transcript");if(!empty||!view||!header||!note||!transcript)return;
  const replay=state.replayData;if(!replay){empty.hidden=false;view.hidden=true;return;}empty.hidden=true;view.hidden=false;header.innerHTML="";transcript.innerHTML="";
  const title=document.createElement("strong");title.textContent=replay.run_id?`Run ${replay.run_id}`:"Canonical debug replay";header.append(title);
  const meta=document.createElement("span");meta.textContent=[`${replay.steps?.length||0} executions`,replay.debug_run_index?.mode,replay.debug_run_index?.status].filter(Boolean).join(" · ");header.append(meta);
  const summary=document.createElement("div");summary.className="replay-summary-grid";const s=replay.summary||{};replayAddMetric(summary,"Process quality",replay.process_quality?.status);replayAddMetric(summary,"Integrity",replay.integrity?.status);replayAddMetric(summary,"Executions",s.executions);if(replay.process_quality?.telemetry_rows!=null&&replay.process_quality?.canonical_execution_count!=null)replayAddMetric(summary,"Telemetry coverage",`${replay.process_quality.telemetry_rows}/${replay.process_quality.canonical_execution_count}`);if(s.total_duration_ms!=null)replayAddMetric(summary,"Observed execution time",replayDurationText(s.total_duration_ms));if(s.runtime_observable_input_tokens!=null||s.runtime_observable_output_tokens!=null)replayAddMetric(summary,"Runtime-observable token equivalent",`${replayNumber(s.runtime_observable_input_tokens||0)} in / ${replayNumber(s.runtime_observable_output_tokens||0)} out`);if(s.exact_host_input_tokens!=null||s.exact_host_output_tokens!=null)replayAddMetric(summary,"Exact host tokens",`${replayNumber(s.exact_host_input_tokens||0)} in / ${replayNumber(s.exact_host_output_tokens||0)} out`);replayAddMetric(summary,"Artifact quality",replay.artifact_quality?.status);header.append(summary);
  note.textContent=replay.chat_coverage?.statement||"Canonical debug replay. Hidden model reasoning is not captured or displayed.";
  if(replay.integrity?.status==="FAIL"){const warning=document.createElement("div");warning.className="replay-note replay-integrity-fail";warning.textContent=`Integrity-invalid replay package: ${replay.integrity.failures?.length||0} manifest failure(s).`;header.append(warning);}
  replayAddJsonDetails(header,"Process quality details",replay.process_quality);replayAddJsonDetails(header,"Performance / token report",replay.performance);replayAddJsonDetails(header,"Artifact quality details",replay.artifact_quality);
  if(replay.artifacts?.length){const details=document.createElement("details");details.className="replay-details";const sum=document.createElement("summary");sum.textContent=`Artifacts · ${replay.artifacts.length}`;details.append(sum);const list=document.createElement("div");list.className="replay-artifacts";replay.artifacts.forEach(a=>{const row=document.createElement("div");row.className="replay-artifact-row";const title=document.createElement("div");title.textContent=`${a.role||"artifact"} · ${a.path||a.archive_path||""}${a.bytes!=null?` · ${replayNumber(a.bytes)} B`:""}`;row.append(title);if(a.content_text){const open=document.createElement("details");open.className="replay-details";const os=document.createElement("summary");os.textContent="Open artifact";open.append(os);if(/\.(md|markdown)$/i.test(String(a.path||a.archive_path||""))){const md=document.createElement("div");md.className="replay-event-markdown replay-artifact-markdown";md.innerHTML=renderBasicMarkdown(a.content_text);open.append(md);}else{const pre=document.createElement("pre");pre.className="replay-values compact";pre.textContent=a.content_text;open.append(pre);}row.append(open);}list.append(row);});details.append(list);header.append(details);}
  (replay.steps||[]).forEach(stepData=>{
    const step=document.createElement("section");step.className="replay-step";if(stepData.id)step.dataset.nodeId=stepData.id;
    const head=document.createElement("div");head.className="replay-step-head";const id=document.createElement(replayGraphHasElement(stepData.id)?"button":"span");id.className=replayGraphHasElement(stepData.id)?"replay-step-id replay-node-link":"replay-step-id";id.textContent=stepData.id||"(unknown)";if(id.tagName==="BUTTON"){id.type="button";id.addEventListener("click",()=>focusReplayGraphElement(stepData.id));}head.append(id);
    const seq=document.createElement("span");seq.className="replay-seq";seq.textContent=`Execution #${stepData.execution_sequence||stepData.index} · ${stepData.kind||"step"}${stepData.status?` · ${stepData.status}`:""}`;head.append(seq);
    const metrics=document.createElement("div");metrics.className="replay-step-metrics";const tele=stepData.telemetry||{};if(tele.duration_ms!=null)replayAddMetric(metrics,"Duration",replayDurationText(tele.duration_ms));if(tele.estimated_input_tokens!=null||tele.estimated_output_tokens!=null)replayAddMetric(metrics,"Runtime-observable token equivalent",`${replayNumber(tele.estimated_input_tokens||0)} in / ${replayNumber(tele.estimated_output_tokens||0)} out`);if(tele.exact_host_input_tokens!=null||tele.exact_host_output_tokens!=null)replayAddMetric(metrics,"Exact host tokens",`${replayNumber(tele.exact_host_input_tokens||0)} in / ${replayNumber(tele.exact_host_output_tokens||0)} out`);if(stepData.receipt?.receipt_sha256)replayAddMetric(metrics,"Receipt","✓");if(stepData.ledger_sha256)replayAddMetric(metrics,"Ledger","✓");if(metrics.childNodes.length)head.append(metrics);step.append(head);
    const chronology=document.createElement("div");chronology.className="replay-chronology";
    if(stepData.prompt&&stepData.prompt_source==="SOURCE_RECONSTRUCTION"){const reconstructed=document.createElement("div");reconstructed.className="replay-event assistant-message replay-reconstruction";reconstructed.innerHTML='<span class="replay-event-label">Playbook source · reconstructed</span>';const body=document.createElement("div");body.className="replay-event-markdown";body.innerHTML=renderBasicMarkdown(stepData.prompt);reconstructed.append(body);chronology.append(reconstructed);}
    (stepData.chronology||[]).forEach(event=>renderCanonicalReplayEvent(chronology,event));if(!chronology.childNodes.length){const quiet=document.createElement("div");quiet.className="replay-event";quiet.textContent=`No user-visible message recorded for this execution. Route: ${stepData.route||"unknown"}${stepData.to_node?` → ${stepData.to_node}`:""}.`;chronology.append(quiet);}step.append(chronology);
    renderReplayFileActions(step,stepData.file_actions||[]);if(stepData.receipt)replayAddJsonDetails(step,"Receipt / integrity details",stepData.receipt);transcript.append(step);
  });
  if(state.replayFocusId)updateReplayFocusVisuals(state.replayFocusId);
}

function bytesToBase64(bytes) {
  let binary = ""; const chunk = 0x8000;
  for (let offset = 0; offset < bytes.length; offset += chunk) binary += String.fromCharCode(...bytes.subarray(offset, offset + chunk));
  return btoa(binary);
}


const HELP_PAGES = [
  {
    id:"getting-started", title:"Getting Started", lead:"Understand the Editor workflow from source playbook to a verified executable run.",
    sections:[
      ["What the Editor does", `<p>Ordo Editor is both a playbook explorer and a runtime host. You load a playbook source, the embedded Compiler converts it into a runtime semantic plan, the Editor validates the result, and only then can the playbook be executed.</p><p>You do not need to manually build a runtime JSON file. Compilation is part of the normal load process.</p>`],
      ["Choose what to load", `<h3>Standalone YAML</h3><p>Use <strong>Upload YAML</strong> for a self-contained playbook that does not depend on external templates, validators, bindings, schemas, or other package files.</p><h3>Source package</h3><p>Use <strong>Upload Playbook</strong> for a ZIP package containing the playbook source and its referenced resources. If a standalone YAML references files that are not present, loading fails closed and the Editor asks for a complete source package.</p>`],
      ["What happens after upload", `<ol><li>The source is parsed.</li><li>The embedded Compiler builds a runtime semantic plan.</li><li>Structural and semantic validation runs.</li><li>Package resources and compatibility requirements are checked.</li><li>If everything passes, the Editor opens <strong>Execute Playbook</strong>.</li></ol><div class="help-callout"><strong>Fail closed:</strong> the Editor does not invent missing semantics or silently repair an invalid playbook.</div>`],
      ["Configure a model", `<p>Use <strong>Model Settings</strong> on the start screen or in the global header. Configure the provider, base URL, model, credentials, and structured-output capability before starting a live run.</p><p>Model configuration is also used by optional Explorer features such as <strong>Explain with model</strong>.</p>`],
      ["Recommended workflow", `<ol><li>Load the source playbook.</li><li>Resolve any compilation or validation errors.</li><li>Configure the model provider.</li><li>Explore the tree and references if needed.</li><li>Optionally load Auto Answers.</li><li>Run the playbook from <strong>Execute Playbook</strong>.</li><li>Use Replay, Current State, or Evidence tools for inspection and debugging.</li></ol>`]
    ]
  },
  {id:"execute-playbook", title:"Execute Playbook", lead:"Run the loaded playbook as a live analyst-model conversation while the runtime enforces the compiled semantic contracts.", sections:[
    ["What happens during execution", `<p>The runtime follows the control-flow graph produced by the Compiler. Model nodes call the configured provider, human-decision nodes wait for analyst input, gates evaluate their declared conditions, and deterministic nodes execute their registered runtime behavior.</p><p>The playbook owns domain semantics; the Editor owns orchestration, validation, state safety, retries, and presentation.</p>`],
    ["Conversation layout", `<p>Analyst messages are aligned to the right. Model responses appear directly in the transcript. Runtime events such as transitions, gate results, generated artifacts, and activity status are intentionally quieter so the conversation remains readable.</p><p>The tree remains available in the side pane so the current execution position can be inspected without leaving the conversation.</p>`],
    ["Composer", `<p>The composer begins as a single-line field, grows automatically up to three lines, and then scrolls internally. Use the expand control when you need a larger editing area. Draft text, focus, and cursor position are preserved when expanding or collapsing.</p><p>While the model is working you may keep typing, but sending is disabled until the current model request finishes or is stopped.</p>`],
    ["Stopping a model request", `<p>While the model is running, the send control becomes <strong>Stop</strong>. Stop aborts only the current provider request.</p><ul><li>No partial state patch is committed.</li><li>The last committed revision remains canonical.</li><li>The execution pointer remains on the same node.</li><li>Your draft stays in the composer.</li><li>You can retry or resume the same node.</li></ul>`],
    ["Human decisions", `<p>When the playbook declares explicit analyst choices, the Editor shows semantic action buttons instead of raw target-node names. The target node remains secondary information. Hovering an action can show the node purpose/description when available.</p><p>You may also type a manual response when the playbook allows free-form analyst input.</p>`],
    ["Generated files", `<p>Generated files appear inline in the transcript. Markdown files can be opened in a side preview and downloaded. ZIP and other non-preview files use the same file-card design but are download-only.</p>`]
  ]},
  {id:"replay-real-chat", title:"Replay Real Chat", lead:"Reconstruct a recorded execution for inspection, debugging, comparison, and reporting without executing the playbook again.", sections:[
    ["What Replay is", `<p>Replay reads a canonical debug handoff ZIP. <code>MODEL_EXECUTION_LEDGER.jsonl</code> is execution truth; <code>INTERACTION_AND_ACTION_TRACE.jsonl</code> provides recorded user-visible chat and structured actions. Telemetry, file/tool evidence, receipts, integrity, and artifact quality are overlaid when present.</p><div class="help-callout">Replay never displays hidden model reasoning, does not make provider calls, and does not change runtime state.</div>`],
    ["What may be missing", `<p>A replay package can contain full verbatim interaction data or only structural run evidence. If raw model wording was not recorded, the Editor may fall back to the packaged playbook wording where appropriate and clearly marks the reconstruction as read-only.</p>`],
    ["Reading the transcript", `<p>Assistant/playbook steps, analyst decisions, gate results, and checkpoint payloads use different visual treatments. Technical metadata is secondary to the conversational flow.</p>`],
    ["Download MD", `<p><strong>Download MD</strong> exports the reconstructed transcript as Markdown for review, issue attachments, or archival use.</p>`],
    ["Print / Save PDF", `<p><strong>Print / Save PDF</strong> opens the browser print view using the same replay renderer and styling as the screen view. Long messages are allowed to continue across physical pages to avoid large blank areas. Analyst responses retain their visual distinction in print.</p><p>Printer margins, headers/footers, paper size, and background graphics may still be controlled by the browser or operating-system print dialog.</p>`]
  ]},
  {id:"show-tree", title:"Show Tree", lead:"Explore the complete playbook graph, inspect individual elements, and understand package resources without changing execution state.", sections:[
    ["What the tree represents", `<p>The tree is a structural projection of the compiled semantic plan. Nodes represent executable or inspectable elements; edges show routing or dependency relationships.</p><p>Selecting a node opens its inspector in the side pane.</p>`],
    ["Control flow vs dependencies", `<p><strong>Control-flow edges</strong> are executable routes. <strong>Dependency relations</strong> are overlays showing that an element uses or produces another resource; they do not become executable control flow.</p><div class="help-callout">Dependency arrows must never be interpreted as additional runtime transitions.</div>`],
    ["Inspector tabs", `<h3>Parameters</h3><p>A structured, readable view of the selected element's main properties.</p><h3>YAML</h3><p>The source-level definition for detailed inspection.</p><h3>References</h3><p>Package files used by the node, such as templates, bindings, validators, schemas, specifications, and other resources.</p><h3>Explanation</h3><p>An optional model-generated explanation of what the node does in human language. Explanation is read-only and does not execute the node.</p>`],
    ["Reference files", `<p>Resolved reference files can be opened inline. Markdown files provide <strong>Preview</strong> and <strong>Source</strong> views. Text resources such as Python, YAML, and JSON are shown as source text.</p><p>Python references can also expose <strong>Explain with model</strong>, which asks the configured model to describe what the script validates or performs.</p>`],
    ["Zoom and navigation", `<p>Use the bottom-right <strong>−</strong>, <strong>1:1</strong>, and <strong>+</strong> controls to adjust viewport scale only. <strong>1:1</strong> returns to canonical 100% rather than fitting the entire graph to the screen.</p>`],
    ["Safe exploration", `<p>Tree inspection is read-only. Opening nodes, references, previews, or explanations does not change the active runtime node, canonical state, or run history.</p>`]
  ]},
  {id:"show-data-flow", title:"Show Data Flow", lead:"Inspect the canonical authoring data-flow model shipped inside the playbook package.", sections:[
    ["Canonical authoring flow", `<p>Show Data Flow presents the canonical authoring data model. Packages using <code>ordo.design.editor_projection.v1</code> are projected from their referenced <code>ordo.authoring.canonical_data_layer.v1</code>; legacy <code>canonical_sources.graph</code> bundles remain supported as a fallback.</p><p>Canonical state variables may declare <code>state_path_annotations.&lt;path&gt;.data_class</code> in the canonical Data Layer; <code>editor_projection.state_path_data_classes</code> is accepted as the derived UI projection. Allowed values are <code>business</code>, <code>technical</code>, <code>control</code>, or <code>metadata</code>. The Data filter shows only classes actually present; missing/unknown declarations remain <code>unclassified</code> and are never guessed by the Editor.</p><div class="help-callout">The authoring data-flow model and data-class filter are visualization/evidence only. They never extend Ordo runtime syntax and never change execution semantics.</div>`],
    ["Dependency Tree", `<p>The dependency tree shows typed information objects and their declared relations with orthogonal connectors, zoom/pan, top-to-bottom or left-to-right layout, and double-click full upstream/downstream tracing.</p>`],
    ["Variable Passports", `<p>Variable groups and passports are available as a dedicated subview and open the same canonical information objects used in the dependency graph.</p>`],
    ["Inspector", `<p>The right pane is a read-only technical inspector for the selected information object and its canonical passport metadata. <strong>Explain with model</strong> uses that same selected Source Data Flow entity and its declared incoming/outgoing relations.</p>`],
    ["Package without embedded flow", `<p>If the loaded package does not include a canonical authoring data-flow bundle, the page shows an explicit empty-state message instead of falling back to a reconstructed approximation.</p>`]
  ]},
  {id:"show-path", title:"Show Path", lead:"Build and walk a selected control-flow route to understand how the playbook can move from one element to another.", sections:[
    ["Build a path", `<p>Select a <strong>From</strong> node and a <strong>To</strong> node, then choose <strong>Build path</strong>. The path builder uses executable control-flow edges only.</p>`],
    ["Playback controls", `<p>The sticky playback bar remains visible while a long path is being inspected.</p><ul><li><strong>Play</strong> starts automatic path playback.</li><li><strong>Restart</strong> returns to the beginning of the built path.</li><li><strong>Advance</strong> controls whether progression is manual or timer-based.</li><li><strong>Delay</strong> controls timer speed.</li><li><strong>Auto-pass gates via OnPass</strong> follows the successful gate route automatically.</li><li><strong>Show all</strong> expands the complete structural path view.</li></ul>`],
    ["Alternative routes", `<p>At gates or branch points, the path view can show alternative legal transitions. These are structural possibilities, not evidence that a particular live run took those branches.</p>`],
    ["When to use Show Path", `<p>Use it to explain routing, review recovery branches, inspect long processes, or understand why two distant nodes are connected without executing the playbook.</p>`]
  ]},
  {id:"playbook-settings", title:"Playbook Settings", lead:"Inspect the effective program-level configuration declared by the loaded playbook and compare it with values documented by the Ordo language registry.", sections:[
    ["What you see", `<p>Each setting is shown as a concrete current value rather than a raw YAML block. When the language registry declares alternatives, the page lists every known value with its English meaning and highlights the current one.</p>`],
    ["Registry-driven behavior", `<p>The Editor reads value definitions from the bundled language registry. Future language-package builds can extend the registry without rewriting this page.</p>`],
    ["Read-only by design", `<p>Playbook Settings is an inspection view. It does not mutate the playbook or silently change execution semantics.</p>`]
  ]},
  {id:"verify-playbook", title:"Verify Playbook", lead:"Run the complete descriptor-driven verification catalog against an isolated copy of the loaded playbook.", sections:[
    ["How it works", `<p>The Editor discovers verification descriptors from <code>verification/checks/</code>. <strong>Run all verifications</strong> executes applicable checks sequentially and reports <strong>PASS</strong>, <strong>FAIL</strong>, <strong>ERROR</strong>, or <strong>SKIPPED</strong> as each check finishes.</p>`],
    ["Why some checks are skipped", `<p>Some language/tooling checks require extra context such as a concrete gate ID, document bindings, a template contract, a tree-module instance, or release inputs. They stay visible in the catalog but are marked <strong>SKIPPED</strong> when that context is not available.</p>`],
    ["Adding future checks", `<p>New checks are added as descriptor files rather than hard-coded UI entries. A language/tooling package integration should copy the executable dependency plus a descriptor into the Editor verification registry. The page and runner discover it automatically on the next build.</p>`]
  ]},
  {id:"auto-answers", title:"Auto Answers", lead:"Automatically supply analyst answers at matching human-interaction nodes while keeping model execution live.", sections:[
    ["What Auto Answers contains", `<p>A native Auto Answers package contains analyst responses indexed by interaction/node order. It does not contain model responses.</p>`],
    ["How it behaves", `<p>When execution reaches a matching analyst-input node, the Editor injects the recorded analyst answer and continues as if the analyst had supplied it manually.</p><p>Unmatched nodes still require manual input.</p>`],
    ["Auto Answers vs Replay", `<p><strong>Auto Answers</strong> automate only analyst input in a live run. <strong>Replay</strong> reconstructs an already recorded run and makes no model calls. These are different mechanisms.</p>`],
    ["Acceptance use", `<p>For pure-live acceptance, keep Guided Replay off and verify that replayed model calls remain zero. Auto Answers can still be used because model responses are generated live.</p>`]
  ]},
  {id:"current-state", title:"Current State", lead:"Inspect the canonical runtime state, current revision, and committed values used by subsequent nodes.", sections:[
    ["Canonical state", `<p>Current State is the runtime's committed source of truth. Model output does not become state merely because it was generated; it must pass the relevant output contract and state-patch validation first.</p>`],
    ["State revisions", `<p>Successful commits advance the state revision. Artifact lineage and other runtime evidence can refer to these revisions to prove that outputs were produced from the correct state.</p>`],
    ["Interrupted or invalid output", `<p>If a provider request is stopped, fails, or returns an invalid patch, partial values are not committed. The last valid revision remains canonical.</p>`],
    ["How to use it", `<p>Use Current State when debugging a gate, checking whether a human answer was committed, comparing before/after revisions, or confirming that a generated artifact reflects the latest approved data.</p>`]
  ]},
  {id:"pause-resume", title:"Pause and Resume", lead:"Temporarily stop automatic traversal at safe boundaries without losing committed progress.", sections:[
    ["Pause", `<p><strong>Pause</strong> prevents the runtime from automatically entering the next eligible step once the current safe boundary is reached. Already committed state is preserved.</p>`],
    ["Resume", `<p><strong>Resume Auto</strong> continues from the current execution pointer using the same run and canonical state.</p>`],
    ["Pause vs Stop", `<p><strong>Pause</strong> controls traversal between steps. <strong>Stop</strong> aborts an in-flight model request. They solve different problems and have different safety semantics.</p>`]
  ]},
  {id:"recovery", title:"Recovery Flow", lead:"Understand how the runtime responds when a gate, validator, or state contract identifies a correctable problem.", sections:[
    ["Why recovery exists", `<p>A failed gate should not always restart the entire playbook. Recovery routes can return to the earliest safe producer that is allowed to repair the missing or invalid state.</p>`],
    ["Recovery target selection", `<p>The runtime uses the compiled recovery/revisit contract to determine where correction is allowed. It does not invent a shortcut route just because two nodes are related in the dependency graph.</p>`],
    ["Analyst clarification", `<p>Some recovery paths ask the analyst for clarification. Clarification supplements the next attempt but cannot override schemas, state-path permissions, deterministic evidence, or canonical routing contracts.</p>`],
    ["No-progress protection", `<p>The runtime detects recovery cycles that return to the same state without meaningful progress. This prevents an invalid playbook or repeated failed correction from looping forever.</p>`],
    ["Debugging recovery", `<p>Inspect the failed gate, Current State, recovery target, and subsequent state diff. If a recovery path is wrong because of the playbook definition, treat it as a playbook issue rather than changing the Editor to guess domain intent.</p>`]
  ]},
  {id:"files", title:"Package Files", lead:"Browse package contents that are not otherwise exposed by the Editor, or inspect the complete physical ZIP tree.", sections:[
    ["Uncovered and All files", `<p><strong>Uncovered</strong> shows package files that are not exposed through Show Tree, Show Data Flow, Playbook Settings, verification, or another standard Editor surface. <strong>All files</strong> shows the complete physical ZIP contents with coverage badges.</p>`],
    ["File tree and search", `<p>Expand directories to navigate the package hierarchy or use search to filter by path. Expanded directories remain open while you select files and preview their contents.</p>`],
    ["Preview and download", `<p>Markdown is rendered as formatted content. YAML, JSON, Python, and other text files are shown as readable source. Binary files expose metadata and download without pretending to be text.</p>`],
    ["Discuss with model", `<p>For previewable text files, <strong>Discuss with model</strong> opens the read-only AI File Assistant in the right pane with the selected file as context. This never modifies package contents.</p>`],
    ["Coverage badges", `<p>In <strong>All files</strong>, badges such as <strong>Tree</strong>, <strong>Settings</strong>, <strong>Data Flow</strong>, and <strong>Uncovered</strong> show where each file is already exposed by the Editor.</p>`]
  ]},

  {id:"settings", title:"Model and Provider Settings", lead:"Configure the provider used for live execution and optional model-assisted Explorer features.", sections:[
    ["Where settings are available", `<p><strong>Model Settings</strong> is available on the initial source-loading screen and in the global header after a playbook is loaded. You can configure the provider before starting execution.</p>`],
    ["Typical fields", `<p>Depending on provider mode, configure the base URL, model name, credentials, timeout/retry settings, and structured-output behavior.</p>`],
    ["Structured-output capability", `<p>When available, run the JSON Schema capability probe. The result records whether the selected provider/model supports the strict structured-output contract expected by the runtime.</p>`],
    ["Explorer explanations", `<p><strong>Explain with model</strong> for nodes and Python references uses the same configured provider. These explanation calls are read-only and are not counted as execution steps or state commits.</p>`],
    ["If no model is configured", `<p>You can still load, compile, inspect, and navigate a playbook. Live model nodes and model-assisted explanation actions remain unavailable until a provider is configured.</p>`]
  ]},
  {id:"evidence", title:"Evidence and Debug Information", lead:"Understand the evidence used to reproduce runs, diagnose failures, and support release acceptance.", sections:[
    ["What evidence records", `<p>Run evidence can include route traversal, accepted analyst decisions, gate outcomes, state revisions, retries, provider attempts, token accounting, artifact lineage, capability information, and final terminal status.</p>`],
    ["Live vs Replay provenance", `<p>Live model calls and replayed model calls are tracked separately. A pure-live acceptance run should explicitly show zero replayed model calls.</p>`],
    ["Retry accounting", `<p>Logical model calls, provider attempts, retries, and exhausted retry budgets are distinct values. A model step may require more than one provider attempt while still representing a single logical step.</p>`],
    ["Artifact lifecycle", `<p>Generated artifacts record materialization and dependency information so the verifier can detect stale outputs that were produced before the state they claim to represent.</p>`],
    ["Using evidence", `<p>Use evidence exports for regression analysis, replay, release verification, and root-cause investigation. Evidence should describe what actually happened; it should not silently reinterpret an unsuccessful run as successful.</p>`]
  ]},
  {id:"troubleshooting", title:"Troubleshooting", lead:"Diagnose common loading, model, execution, preview, and replay problems without guessing at domain semantics.", sections:[
    ["Playbook will not load", `<p>Read the compilation/validation report first. Common causes include missing package resources, invalid routes, undeclared state writes, incompatible capabilities, or incomplete source packages.</p><p>Do not bypass a failing semantic check by editing generated runtime JSON manually.</p>`],
    ["Unknown API endpoint", `<p>Confirm that the browser UI and Python backend come from the same Editor package/version. Restart the local Editor service and reload the browser after upgrading.</p>`],
    ["Model call fails", `<p>Check Model Settings, provider URL, credentials, model name, timeout, structured-output capability, and Semantic fallback policy. Provider failures should not partially commit model output to state.</p>`],
    ["Run stops at a node", `<p>Inspect the visible error/activity status and Current State. Determine whether the problem is a runtime/editor defect or a playbook-contract problem. If a model request was manually stopped, retry or resume from the same node.</p>`],
    ["A gate keeps failing", `<p>Inspect the gate condition, state paths it reads, the producer node that should populate them, and any recovery route. If the playbook declares a write but never binds analyst/model output to that state path, the Compiler should report the contract issue.</p>`],
    ["Reference preview is missing", `<p>Open the node's <strong>References</strong> tab and check whether the resource is marked <strong>Resolved</strong>. Missing resources are not previewable and should be fixed in the source package.</p>`],
    ["Explanation is unavailable", `<p>Configure a model first. Explanation actions are optional read-only tools and do not affect the ability to compile or inspect the playbook.</p>`],
    ["Replay looks incomplete", `<p>The replay can only show evidence that was captured. If the package lacks raw verbatim model conversation, the Editor may reconstruct structural steps from the playbook and run trace instead.</p>`],
    ["PDF differs from the browser", `<p>The Replay print view shares the same renderer, but final pagination, system headers/footers, paper size, margins, and background printing can still be affected by browser print settings.</p>`]
  ]}

];
HELP_PAGES.push({
  id:"rest-api", title:"REST API", lead:"Browse the local HTTP contract used by the Editor web application and download its OpenAPI/Swagger specification.",
  sections:[
    ["API Reference", `<p>The Editor exposes a local HTTP API between the browser UI and the Python server. The reference is generated from the documented server contract and grouped by functional area.</p><p><a class="help-link-button" href="/api-docs/" target="_blank" rel="noopener">Open REST API Reference ↗</a> <a class="help-link-button" href="/api-docs/execute-playbook.html" target="_blank" rel="noopener">Execute Playbook API Guide ↗</a></p>`],
    ["OpenAPI / Swagger files", `<p>Machine-readable OpenAPI 3.1 files are available directly from the running Editor:</p><ul><li><a href="/api-docs/openapi.yaml" target="_blank" rel="noopener"><code>/api-docs/openapi.yaml</code></a></li><li><a href="/api-docs/swagger.yaml" target="_blank" rel="noopener"><code>/api-docs/swagger.yaml</code> (Swagger alias)</a></li><li><a href="/api-docs/openapi.json" target="_blank" rel="noopener"><code>/api-docs/openapi.json</code></a></li></ul><p>The YAML file can be imported into Swagger Editor, Swagger UI, Postman, Insomnia, or another OpenAPI-compatible client.</p>`],
    ["Scope and safety", `<div class="help-callout"><strong>Local by default:</strong> the Editor server binds to <code>127.0.0.1</code>. Publishing this reference does not make the API an Internet-facing service.</div><p>The REST contract is an Editor integration interface, not canonical Ordo language syntax. Endpoints that execute model calls, package tools, or live runtime steps can have the same side effects as using the corresponding Editor UI action.</p>`],
    ["Contract drift protection", `<p>Release verification compares the HTTP routes implemented by <code>EditorHandler</code> with the methods and paths present in OpenAPI. If an API route is added or removed without updating the specification, the regression test fails.</p>`]
  ]
});
HELP_PAGES.push({
  id:"model-chat", title:"Model Chat", lead:"Use the configured model for free-form discussion without executing the loaded playbook.",
  sections:[
    ["Independent conversation", `<p>Model Chat is a free conversation workspace. Messages here do not advance execution, change canonical runtime state, or traverse the playbook graph.</p>`],
    ["Files and generated artifacts", `<p>You can attach supported files and inspect files generated by the model. Previewable playbook files can be opened from the chat while archives remain download-oriented.</p>`],
    ["Model configuration", `<p>Model Chat uses the same configured provider and model as the rest of the Editor. Configure credentials and capability settings before starting a conversation.</p>`],
    ["Safety boundary", `<p>Model Chat can help analyze or draft material, but its conversation is not canonical playbook execution evidence unless you explicitly use the appropriate execution or package workflow.</p>`]
  ]
});
const HELP_NAV_GROUPS = [
  ["getting-started"],
  ["show-tree","show-data-flow","playbook-settings","verify-playbook","files"],
  ["show-path","execute-playbook","replay-real-chat","auto-answers","current-state","pause-resume","recovery","evidence"],
  ["model-chat","settings","troubleshooting","rest-api"]
];

let playbookSettingsCache=null;
let playbookSettingsSubtab="settings";
let playbookSettingsResourcePreviewPath="";
let settingsAssistantMessages=[];
let settingsAssistantBusy=false;
let settingsAssistantSelectedField=null;
let settingsResourceAssistantThreads={};
let activeHelpPageId="getting-started";


let packageFilesCache=null;
let packageFilesCachePackageId="";
let packageFilesMode="uncovered";
let packageFilesQuery="";
let packageFilesSelectedPath="";
let packageFilePreviewCache=new Map();
let packageFilesTreeWidth=null;
let packageFilesSplitDrag=null;
let packageFilesAssistantOpen=false;
let packageFilesExpandedDirs=new Set();

function packageFilesFormatBytes(size){
  const n=Number(size||0);if(n<1024)return `${n} B`;if(n<1024*1024)return `${(n/1024).toFixed(n<10240?1:0)} KB`;return `${(n/(1024*1024)).toFixed(1)} MB`;
}
function packageFilesCoverageBadge(surface){
  const cls=String(surface||'').toLowerCase().replace(/[^a-z0-9]+/g,'-');
  return `<span class="package-file-coverage ${cls}">${escapeHtml(surface)}</span>`;
}
function packageFilesTreeModel(files){
  const root={name:'',path:'',dirs:new Map(),files:[]};
  for(const file of files){
    const parts=String(file.path||'').split('/').filter(Boolean);let node=root,current=[];
    parts.slice(0,-1).forEach(part=>{current.push(part);if(!node.dirs.has(part))node.dirs.set(part,{name:part,path:current.join('/'),dirs:new Map(),files:[]});node=node.dirs.get(part);});
    node.files.push(file);
  }
  return root;
}
function packageFilesRenderTreeNode(node,depth=0,forceOpen=false){
  const dirs=[...node.dirs.values()].sort((a,b)=>a.name.localeCompare(b.name)),files=[...node.files].sort((a,b)=>String(a.path).localeCompare(String(b.path)));
  const innerDirs=dirs.map(dir=>{const open=forceOpen||depth===0||packageFilesExpandedDirs.has(dir.path);return `<details class="package-files-dir" data-package-dir-path="${escapeHtml(dir.path)}" ${open?'open':''}><summary><span class="package-files-folder">▸</span><strong>${escapeHtml(dir.name)}</strong><small>${dir.files.length+[...dir.dirs.values()].reduce((sum,d)=>sum+d.files.length,0)}</small></summary><div class="package-files-dir-body">${packageFilesRenderTreeNode(dir,depth+1,forceOpen)}</div></details>`;}).join('');
  const innerFiles=files.map(file=>{const coverage=(file.coverage||[]);return `<button type="button" class="package-file-row ${file.path===packageFilesSelectedPath?'active':''}" data-package-file-path="${escapeHtml(file.path)}"><span class="package-file-row-main"><span class="package-file-icon">${file.text?'▤':'◫'}</span><span><strong>${escapeHtml(String(file.path).split('/').pop())}</strong><small>${packageFilesFormatBytes(file.size)}${file.extension?` · ${escapeHtml(String(file.extension).replace(/^\./,'').toUpperCase())}`:''}</small></span></span><span class="package-file-row-badges">${coverage.length?coverage.map(packageFilesCoverageBadge).join(''):packageFilesCoverageBadge('Uncovered')}</span></button>`}).join('');
  return innerDirs+innerFiles;
}
function renderPackageFilesTree(){
  const host=document.querySelector('#package-files-tree'),summary=document.querySelector('#package-files-summary');if(!host)return;
  const data=packageFilesCache,all=Array.isArray(data?.files)?data.files:[];
  const q=packageFilesQuery.trim().toLowerCase();
  const visible=all.filter(file=>(packageFilesMode==='all'||file.uncovered)&&(!q||String(file.path||'').toLowerCase().includes(q)));
  if(summary){const s=data?.summary||{};summary.innerHTML=`<span>${Number(s.total||0)} files</span><span>${Number(s.uncovered||0)} uncovered</span><span>${visible.length} shown</span>`;}
  document.querySelector('#package-files-uncovered')?.classList.toggle('active',packageFilesMode==='uncovered');
  document.querySelector('#package-files-all')?.classList.toggle('active',packageFilesMode==='all');
  if(!data){host.innerHTML='<div class="package-files-loading">Loading package files…</div>';return;}
  if(!visible.length){host.innerHTML=`<div class="package-files-empty">${q?'No files match the search.':packageFilesMode==='uncovered'?'Every package file is covered by a standard Editor surface.':'The package contains no files.'}</div>`;return;}
  host.innerHTML=packageFilesRenderTreeNode(packageFilesTreeModel(visible),0,Boolean(q));
  host.querySelectorAll('.package-files-dir[data-package-dir-path]').forEach(details=>details.addEventListener('toggle',()=>{const path=String(details.dataset.packageDirPath||'');if(!path)return;if(details.open)packageFilesExpandedDirs.add(path);else packageFilesExpandedDirs.delete(path);}));
  host.querySelectorAll('[data-package-file-path]').forEach(button=>button.addEventListener('click',()=>openPackageFile(button.dataset.packageFilePath||'')));
}
function renderPackageFilePreview(data=null){
  const empty=document.querySelector('#package-file-preview-empty'),wrap=document.querySelector('#package-file-preview-content'),name=document.querySelector('#package-file-preview-name'),meta=document.querySelector('#package-file-preview-meta'),body=document.querySelector('#package-file-preview-body'),discuss=document.querySelector('#package-file-discuss');
  if(!empty||!wrap||!body)return;
  if(!data){empty.hidden=false;wrap.hidden=true;body.innerHTML='';if(discuss)discuss.hidden=true;return;}
  empty.hidden=true;wrap.hidden=false;const file=data.file||{},preview=data.preview||{};
  if(name)name.textContent=file.path||'';
  if(meta)meta.innerHTML=`${packageFilesFormatBytes(file.size)} · ${(file.coverage||[]).length?(file.coverage||[]).map(packageFilesCoverageBadge).join(' '):packageFilesCoverageBadge('Uncovered')}`;
  const discussable=Boolean(file.text&&preview.available);
  if(discuss){discuss.hidden=!discussable;discuss.disabled=!settingsAssistantAvailable();discuss.title=settingsAssistantAvailable()?'Discuss this text file with the configured model.':'Configure a model to discuss this file.';}
  if(!preview.available){body.className='package-file-preview-body';body.innerHTML=`<div class="package-file-preview-empty">${preview.reason==='too_large'?'This file is too large for inline preview.':'Binary preview is not available.'}<br>Use Download to inspect the original file.</div>`;return;}
  const content=String(preview.content||'');
  body.className=`package-file-preview-body ${preview.kind==='markdown'?'markdown':'source'}`;
  body.innerHTML=preview.kind==='markdown'?`<div class="package-file-preview-document">${renderBasicMarkdown(content)}</div>`:`<pre><code>${escapeHtml(content)}</code></pre>`;
}
function applyPackageFilesTreeWidth(widthPx){
  const layout=document.querySelector('#package-files-layout');if(!layout)return;
  const total=Math.max(1,layout.getBoundingClientRect().width),min=240,max=Math.max(min,Math.min(total-300,total*.72));
  const width=Math.max(min,Math.min(max,Number(widthPx)||total*.34));packageFilesTreeWidth=width;layout.style.setProperty('--package-tree-width',`${Math.round(width)}px`);
  document.querySelector('#package-files-splitter')?.setAttribute('aria-valuenow',String(Math.round(width)));
}
function closePackageFileAssistant(){
  packageFilesAssistantOpen=false;editorMain.classList.remove('package-files-chat-open');
  const panel=document.querySelector('#playbook-settings-assistant-panel');if(panel)panel.hidden=true;
  document.querySelector('#settings-assistant-close')?.setAttribute('hidden','');refreshWorkspaceAfterShellChange();
}
async function openPackageFileDiscussion(){
  if(!packageFilesSelectedPath||!settingsAssistantAvailable())return;
  const data=packageFilePreviewCache.get(packageFilesSelectedPath);if(!data?.file?.text||!data?.preview?.available)return;
  const changed=playbookSettingsResourcePreviewPath!==packageFilesSelectedPath;
  playbookSettingsResourcePreviewPath=packageFilesSelectedPath;settingsAssistantSelectedField=null;
  if(changed)settingsAssistantMessages=settingsResourceAssistantThreads[packageFilesSelectedPath]||[];
  packageFilesAssistantOpen=true;editorMain.classList.add('package-files-chat-open');
  const panel=document.querySelector('#playbook-settings-assistant-panel');if(panel)panel.hidden=false;
  const close=document.querySelector('#settings-assistant-close');if(close)close.hidden=false;
  renderSettingsAssistant();refreshWorkspaceAfterShellChange();
  requestAnimationFrame(()=>document.querySelector('#settings-assistant-input')?.focus());
}
async function openPackageFile(path){
  packageFilesSelectedPath=String(path||'');
  const host=document.querySelector('#package-files-tree');
  host?.querySelectorAll('.package-file-row.active').forEach(row=>row.classList.remove('active'));
  if(packageFilesSelectedPath){const selected=host?.querySelector(`[data-package-file-path="${CSS.escape(packageFilesSelectedPath)}"]`);selected?.classList.add('active');}
  if(!packageFilesSelectedPath){renderPackageFilePreview(null);return;}
  const cached=packageFilePreviewCache.get(packageFilesSelectedPath);if(cached){renderPackageFilePreview(cached);return;}
  const body=document.querySelector('#package-file-preview-body'),empty=document.querySelector('#package-file-preview-empty'),wrap=document.querySelector('#package-file-preview-content');if(empty)empty.hidden=true;if(wrap)wrap.hidden=false;if(body)body.innerHTML='<div class="package-files-loading">Loading preview…</div>';
  try{const data=await request('/api/package-files',{package_id:state.packageInfo?.id||'',mode:'read',path:packageFilesSelectedPath});packageFilePreviewCache.set(packageFilesSelectedPath,data);renderPackageFilePreview(data);}catch(error){if(body)body.innerHTML=`<div class="package-files-error">${escapeHtml(error.message)}</div>`;}
}
async function renderPackageFiles(){
  const id=state.packageInfo?.id||'';
  if(!id)return;
  if(packageFilesCache&&packageFilesCachePackageId===id){renderPackageFilesTree();renderPackageFilePreview(packageFilePreviewCache.get(packageFilesSelectedPath)||null);requestAnimationFrame(()=>{if(packageFilesTreeWidth)applyPackageFilesTreeWidth(packageFilesTreeWidth);});return;}
  packageFilesCache=null;packageFilesCachePackageId=id;packageFilesSelectedPath='';packageFilePreviewCache=new Map();packageFilesExpandedDirs=new Set();renderPackageFilesTree();renderPackageFilePreview(null);
  try{packageFilesCache=await request('/api/package-files',{package_id:id,mode:'list'});renderPackageFilesTree();}catch(error){const host=document.querySelector('#package-files-tree');if(host)host.innerHTML=`<div class="package-files-error">${escapeHtml(error.message)}</div>`;}
}
function bindPackageFiles(){
  document.querySelector('#package-files-uncovered')?.addEventListener('click',()=>{packageFilesMode='uncovered';renderPackageFilesTree();});
  document.querySelector('#package-files-all')?.addEventListener('click',()=>{packageFilesMode='all';renderPackageFilesTree();});
  document.querySelector('#package-files-search')?.addEventListener('input',event=>{packageFilesQuery=String(event.target.value||'');renderPackageFilesTree();});
  document.querySelector('#package-file-download')?.addEventListener('click',()=>{if(!packageFilesSelectedPath||!state.packageInfo?.id)return;window.location.href=`/api/package-file-download?package_id=${encodeURIComponent(state.packageInfo.id)}&path=${encodeURIComponent(packageFilesSelectedPath)}`;});
  document.querySelector('#package-file-discuss')?.addEventListener('click',openPackageFileDiscussion);
  const splitter=document.querySelector('#package-files-splitter'),layout=document.querySelector('#package-files-layout');
  splitter?.addEventListener('pointerdown',event=>{if(event.button!==0||!layout)return;const rect=layout.getBoundingClientRect();packageFilesSplitDrag={id:event.pointerId,left:rect.left,top:rect.top,width:rect.width,height:rect.height,mobile:matchMedia('(max-width:900px)').matches};splitter.setPointerCapture?.(event.pointerId);splitter.classList.add('dragging');event.preventDefault();});
  splitter?.addEventListener('pointermove',event=>{const drag=packageFilesSplitDrag;if(!drag||drag.id!==event.pointerId)return;if(drag.mobile){const y=Math.max(150,Math.min(drag.height-240,event.clientY-drag.top));layout.style.gridTemplateRows=`${Math.round(y)}px 7px minmax(240px,1fr)`;}else applyPackageFilesTreeWidth(event.clientX-drag.left);event.preventDefault();});
  const stopSplit=event=>{if(packageFilesSplitDrag&&event?.pointerId!=null&&packageFilesSplitDrag.id!==event.pointerId)return;packageFilesSplitDrag=null;splitter?.classList.remove('dragging');};
  splitter?.addEventListener('pointerup',stopSplit);splitter?.addEventListener('pointercancel',stopSplit);
  splitter?.addEventListener('keydown',event=>{if(!layout||!['ArrowLeft','ArrowRight'].includes(event.key))return;event.preventDefault();const current=packageFilesTreeWidth||layout.getBoundingClientRect().width*.34;applyPackageFilesTreeWidth(current+(event.key==='ArrowRight'?24:-24));});
}


function renderPlaybookSettingsResourcePreview(file){
  const host=document.querySelector("#playbook-settings-resource-preview"); if(!host)return;
  if(!file){host.innerHTML='<div class="playbook-settings-resource-preview-empty">Select a file to preview it.</div>';return;}
  const path=String(file.path||""), text=String(file.text||"");
  const markdown=/\.(?:md|markdown)$/i.test(path);
  host.innerHTML=`<div class="playbook-settings-resource-preview-head"><strong>${escapeHtml(path)}</strong><span>${Number(file.size||0).toLocaleString()} bytes</span></div><div class="playbook-settings-resource-preview-body ${markdown?"markdown":"source"}">${markdown?renderBasicMarkdown(text):`<pre><code>${escapeHtml(text)}</code></pre>`}</div>`;
}
function renderPlaybookSettingsSubtab(){
  const catalog=document.querySelector("#playbook-settings-catalog-view"), resources=document.querySelector("#playbook-settings-resources-view"), assistant=document.querySelector("#playbook-settings-assistant-panel");
  const isCatalog=playbookSettingsSubtab==="settings";
  if(catalog)catalog.hidden=!isCatalog; if(resources)resources.hidden=isCatalog;
  if(assistant)assistant.hidden=state.panelTab!=="settings";
  editorMain.classList.toggle("settings-resource-mode",!isCatalog && state.panelTab==="settings");
  document.querySelectorAll("[data-playbook-settings-subtab]").forEach(b=>b.classList.toggle("active",b.dataset.playbookSettingsSubtab===playbookSettingsSubtab));
  if(isCatalog)return;
  const groups=Array.isArray(playbookSettingsCache?.unbound_resource_groups)?playbookSettingsCache.unbound_resource_groups:[];
  const group=groups.find(g=>g.id===playbookSettingsSubtab);
  const intro=document.querySelector("#playbook-settings-resource-intro"), list=document.querySelector("#playbook-settings-resource-list");
  if(intro)intro.innerHTML=group?`<h2>${escapeHtml(group.title||"")}</h2><p>${escapeHtml(group.description||"")}</p><span>${Number((group.files||[]).length)} unbound file${(group.files||[]).length===1?"":"s"}</span>`:"";
  if(!list)return; const files=Array.isArray(group?.files)?group.files:[];
  if(!files.length){list.innerHTML='<div class="playbook-settings-empty">No unbound files in this group.</div>';renderPlaybookSettingsResourcePreview(null);return;}
  list.innerHTML=files.map(f=>`<button type="button" class="playbook-settings-resource-row ${String(f.path||"")===playbookSettingsResourcePreviewPath?"active":""}" data-settings-resource-path="${escapeHtml(f.path||"")}"><span class="playbook-settings-resource-icon">▤</span><span><strong>${escapeHtml(f.path||"")}</strong><small>${escapeHtml(String(f.extension||"").replace(/^\./,"").toUpperCase()||"TEXT")} · ${Number(f.size||0).toLocaleString()} bytes</small></span><span aria-hidden="true">›</span></button>`).join("");
  list.querySelectorAll("[data-settings-resource-path]").forEach(button=>button.addEventListener("click",()=>{
    playbookSettingsResourcePreviewPath=button.dataset.settingsResourcePath||"";
    settingsAssistantSelectedField=null;
    settingsAssistantMessages=settingsResourceAssistantThreads[playbookSettingsResourcePreviewPath]||[];
    const file=files.find(f=>f.path===playbookSettingsResourcePreviewPath);
    renderPlaybookSettingsSubtab();renderPlaybookSettingsResourcePreview(file||null);renderSettingsAssistant();
  }));
  const selected=files.find(f=>f.path===playbookSettingsResourcePreviewPath); renderPlaybookSettingsResourcePreview(selected||null);
  renderSettingsAssistant();
}
function bindPlaybookSettingsSubtabs(){
  document.querySelectorAll("[data-playbook-settings-subtab]").forEach(button=>button.addEventListener("click",()=>{
    playbookSettingsSubtab=button.dataset.playbookSettingsSubtab||"settings"; playbookSettingsResourcePreviewPath=""; settingsAssistantSelectedField=null; settingsAssistantMessages=[]; renderPlaybookSettingsSubtab(); renderSettingsAssistant();
  }));
}

function formatSettingValue(value, specified=true) {
  if (!specified) return "Not specified";
  if (value === null || value === undefined) return "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (Array.isArray(value)) return value.length ? value.map(v=>typeof v === "object" ? JSON.stringify(v) : String(v)).join(", ") : "[]";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
async function renderPlaybookSettings() {
  const host=document.querySelector("#playbook-settings-list"), source=document.querySelector("#playbook-settings-source"), summary=document.querySelector("#playbook-settings-summary");
  if (!host) return;
  host.innerHTML='<div class="playbook-settings-loading">Loading playbook settings…</div>';
  try {
    const data=await request("/api/playbook-settings",{package_id:state.packageInfo?.id || ""});
    playbookSettingsCache=data;
    if (source) source.innerHTML=`Current values come from <code>${escapeHtml(data.package?.source_name || "loaded playbook")}</code>. The complete settings catalog, allowed values and meanings come from <code>${escapeHtml(data.registry_source || "Ordo language schema/registry")}</code>.`;
    const info=data.summary||{};
    if(summary) summary.innerHTML=`<span><strong>${Number(info.total_settings||0)}</strong> language-defined settings</span><span><strong>${Number(info.specified||0)}</strong> explicitly specified</span><span><strong>${Number(info.not_specified||0)}</strong> not specified</span>`;
    const groups=Array.isArray(data.groups)?data.groups:[];
    if (!groups.length) { host.innerHTML='<div class="playbook-settings-empty">No language-defined settings catalog is available.</div>'; return; }

    const renderField=(field)=>{
      const options=Array.isArray(field.options)?field.options:[];
      const specified=field.specified!==false;
      const current=formatSettingValue(field.current_value,specified);
      const description=field.description?`<div class="playbook-setting-description">${escapeHtml(field.description)}</div>`:"";
      const choices=options.length ? `<div class="setting-options"><div class="setting-options-title">Allowed values</div>${options.map(opt=>`<div class="setting-option ${specified&&String(opt.value)===String(field.current_value)?"current":""}"><code>${escapeHtml(opt.value)}</code><span>${escapeHtml(opt.meaning || "")}${opt.guarantee?` <em>Guarantee: ${escapeHtml(opt.guarantee)}</em>`:""}</span>${specified&&String(opt.value)===String(field.current_value)?'<b>Current</b>':''}</div>`).join("")}</div>` : '<div class="setting-no-options">No enumerated alternatives are declared in the language registry.</div>';
      return `<article class="playbook-setting-card ${specified?"":"not-specified"}" data-setting-path="${escapeHtml(field.path)}"><div class="playbook-setting-name"><div><strong>${escapeHtml(field.label)}</strong><code>${escapeHtml(field.path)}</code></div><div class="playbook-setting-actions">${field.language_defined===false?'<span class="setting-package-defined">Package-defined</span>':''}<button type="button" class="setting-discuss-button" data-setting-discuss="${escapeHtml(field.path)}">Discuss in chat</button></div></div>${description}<div class="playbook-setting-current"><span>Current value</span><strong class="${specified?"":"missing"}">${escapeHtml(current)}</strong></div>${choices}</article>`;
    };

    const renderBucket=(title,wantedSpecified)=>{
      const sections=groups.map(group=>{
        const fields=(group.fields||[]).filter(field=>(field.specified!==false)===wantedSpecified);
        if(!fields.length) return "";
        return `<section class="playbook-settings-group"><h3>${escapeHtml(group.title)}</h3>${fields.map(renderField).join("")}</section>`;
      }).join("");
      return `<section class="playbook-settings-status-section ${wantedSpecified?"specified":"unspecified"}"><div class="playbook-settings-status-head"><h2>${title}</h2></div>${sections || '<div class="playbook-settings-empty">None.</div>'}</section>`;
    };

    host.innerHTML=renderBucket("Specified settings",true)+renderBucket("Not specified settings",false);
    host.querySelectorAll("[data-setting-discuss]").forEach(button=>{
      button.disabled=!settingsAssistantAvailable();
      button.title=settingsAssistantAvailable()?"Discuss this setting with the configured model.":"Configure a model to discuss this setting.";
      button.addEventListener("click",()=>{
        const path=button.dataset.settingDiscuss||"";
        const field=groups.flatMap(group=>group.fields||[]).find(item=>item.path===path);
        if(field) discussPlaybookSetting(field);
      });
    });
    renderSettingsAssistant();
    renderPlaybookSettingsSubtab();
  } catch (err) {
    host.innerHTML=`<div class="playbook-settings-error">${escapeHtml(err?.message || String(err))}</div>`;
  }
}

function settingsAssistantInPackageFiles(){return state.panelTab==="packagefiles"&&packageFilesAssistantOpen;}
function settingsAssistantResourceMode(){return settingsAssistantInPackageFiles()||playbookSettingsSubtab!=="settings";}
function settingsAssistantResourcePath(){return settingsAssistantInPackageFiles()?String(packageFilesSelectedPath||""):String(playbookSettingsResourcePreviewPath||"");}
function settingsAssistantAvailable(){ return modelExplanationAvailable(); }
function renderSettingsAssistant(){
  const messages=document.querySelector("#settings-assistant-messages"), unavailable=document.querySelector("#settings-assistant-unavailable"), analyze=document.querySelector("#settings-assistant-analyze"), send=document.querySelector("#settings-assistant-send"), input=document.querySelector("#settings-assistant-input"), context=document.querySelector("#settings-assistant-context"), title=document.querySelector("#settings-assistant-title"), subtitle=document.querySelector("#settings-assistant-subtitle");
  if(!messages) return;
  const resourceMode=settingsAssistantResourceMode();
  const resourcePath=settingsAssistantResourcePath();
  const modelAvailable=settingsAssistantAvailable();
  const available=modelAvailable && (!resourceMode || Boolean(resourcePath));
  if(title) title.textContent=resourceMode?"AI File Assistant":"AI Settings Assistant";
  if(subtitle) subtitle.textContent=resourceMode?"Discuss the selected package file with the configured model. Read-only: the assistant never changes the package.":"Read-only guidance. The model never edits the playbook.";
  const close=document.querySelector('#settings-assistant-close');if(close)close.hidden=!settingsAssistantInPackageFiles();
  if(unavailable){ unavailable.hidden=available; unavailable.textContent=!modelAvailable?"Configure a model to use the assistant.":resourceMode&&!resourcePath?"Select a file to discuss it with the model.":""; }
  if(analyze){ analyze.hidden=resourceMode; analyze.disabled=!available||settingsAssistantBusy; analyze.textContent=settingsAssistantBusy?"Working…":"Analyze current settings"; }
  if(send) send.disabled=!available||settingsAssistantBusy;
  if(input){ input.disabled=!available||settingsAssistantBusy; input.placeholder=resourceMode?"Ask about the selected file…":"Describe how you want the playbook settings to behave…"; }
  if(context){
    if(resourceMode){
      context.hidden=!resourcePath;
      context.innerHTML=resourcePath?`<strong>File:</strong> <code>${escapeHtml(resourcePath)}</code>`:"";
    } else if(!settingsAssistantSelectedField){ context.hidden=true; context.innerHTML=""; }
    else {
      const f=settingsAssistantSelectedField, specified=f.specified!==false;
      context.hidden=false;
      context.innerHTML=`<strong>${escapeHtml(f.label||f.path)}</strong><code>${escapeHtml(f.path||"")}</code><span>${specified?"Current value: "+escapeHtml(formatSettingValue(f.current_value,true)):"Current value: Not specified"}</span>`;
    }
  }
  if(!settingsAssistantMessages.length){
    messages.innerHTML=`<div class="settings-assistant-placeholder">${resourceMode?(resourcePath?"Ask what this file does, how it relates to the playbook, or discuss its contents.":"Select a file to start a discussion."):"Ask how the current settings behave, describe how you want them changed, or request a proposed YAML settings block."}</div>`;
    return;
  }
  const visibleSettingsAssistantMessages=settingsAssistantMessages.filter(msg=>!msg.hidden);
  messages.innerHTML=visibleSettingsAssistantMessages.map(msg=>{
    const role=msg.role==="user"?"user":"assistant";
    let body=role==="assistant"?renderBasicMarkdown(msg.content||""):escapeHtml(msg.content||"").replace(/\n/g,"<br>");
    if(role==="assistant"&&msg.yaml&&!resourceMode){
      body+=`<div class="settings-yaml-proposal"><div class="settings-yaml-title">Proposed YAML settings block <span>Copy this into the playbook manually.</span></div><pre><code>${escapeHtml(msg.yaml)}</code></pre><button type="button" class="settings-copy-yaml">Copy YAML</button></div>`;
    }
    return `<div class="settings-assistant-message ${role}">${body}</div>`;
  }).join("");
  messages.querySelectorAll(".settings-assistant-message").forEach((el,i)=>{const msg=visibleSettingsAssistantMessages[i];if(msg)attachChatCopyButton(el, msg.content || "", msg.role === "user" ? "right" : "left");});
  messages.querySelectorAll(".settings-copy-yaml").forEach((button,index)=>{
    const assistants=settingsAssistantMessages.filter(m=>m.role==="assistant"&&m.yaml);
    const item=assistants[index];
    button.addEventListener("click",async()=>{ try{ await copyTextToClipboard(item?.yaml||""); button.textContent="Copied"; setTimeout(()=>button.textContent="Copy YAML",1200); }catch{} });
  });
  messages.scrollTop=messages.scrollHeight;
}
function settingBootstrapPrompt(field){
  const specified=field.specified!==false;
  const options=(field.options||[]).map(opt=>`${opt.value}: ${opt.meaning||""}`).join("\\n");
  return `Explain this playbook setting in detail: ${field.path}.
Describe what the setting controls, its current value (${specified?formatSettingValue(field.current_value,true):"Not specified"}), all documented allowed values and what each means, and how changing it can affect playbook/chat behavior or interact with other settings. Distinguish documented relationships from inference. Allowed values:\\n${options || "No enumerated alternatives are declared."}`;
}
async function discussPlaybookSetting(field){
  if(!field || !settingsAssistantAvailable()) return;
  const changed=!settingsAssistantSelectedField || settingsAssistantSelectedField.path!==field.path;
  settingsAssistantSelectedField=field;
  if(changed) settingsAssistantMessages=[];
  renderSettingsAssistant();
  if(changed){
    await runSettingsAssistant("chat",settingBootstrapPrompt(field),{hiddenUser:true});
  }
  document.querySelector("#settings-assistant-input")?.focus();
}
async function runSettingsAssistant(mode,message="",options={}){
  const resourceMode=settingsAssistantResourceMode();
  const resourcePath=settingsAssistantResourcePath();
  if(!settingsAssistantAvailable()||settingsAssistantBusy||(resourceMode&&!resourcePath)) return false;
  if(mode==="chat"&&!String(message).trim()) return false;
  if(mode==="chat") settingsAssistantMessages.push({role:"user",content:String(message).trim(),hidden:Boolean(options.hiddenUser)});
  if(resourceMode) settingsResourceAssistantThreads[resourcePath]=settingsAssistantMessages;
  settingsAssistantBusy=true; renderSettingsAssistant();
  try{
    const history=settingsAssistantMessages.map(m=>({role:m.role,content:m.content,yaml:m.yaml||""}));
    const data=await request("/api/playbook-settings-assistant",{session_id:liveSessionId,package_id:state.packageInfo?.id||"",mode:resourceMode?"resource_chat":mode,message,messages:history,resource_path:resourceMode?resourcePath:""});
    const answer=String(data.answer_markdown||"").trim();
    if(!answer) throw new Error("The model returned an empty settings-assistant response.");
    settingsAssistantMessages.push({role:"assistant",content:answer,yaml:data.yaml_settings_block||"",model:data.model||""});
    return true;
  }catch(err){
    settingsAssistantMessages.push({role:"assistant",content:`Settings analysis could not be generated: ${err?.message||String(err)}`,error:true});
    return false;
  }finally{settingsAssistantBusy=false;renderSettingsAssistant();}
}
function bindSettingsAssistant(){
  document.querySelector("#settings-assistant-close")?.addEventListener("click",()=>{if(settingsAssistantInPackageFiles())closePackageFileAssistant();});
  document.querySelector("#settings-assistant-analyze")?.addEventListener("click",()=>{
    settingsAssistantSelectedField=null;
    settingsAssistantMessages=[];
    runSettingsAssistant("analyze");
  });
  const form=document.querySelector("#settings-assistant-form");
  const input=document.querySelector("#settings-assistant-input");
  const submitSettingsAssistant=()=>{
    if(settingsAssistantBusy) return false;
    const value=String(input?.value||"");
    if(!value.trim()) return false;
    if(input) input.value="";
    runSettingsAssistant("chat",value);
    return true;
  };
  form?.addEventListener("submit",event=>{
    event.preventDefault();
    submitSettingsAssistant();
  });
  input?.addEventListener("keydown",event=>{
    if(event.key!=="Enter"||event.shiftKey||event.isComposing) return;
    event.preventDefault();
    submitSettingsAssistant();
  });
}

const LINEAGE_CARD_W=164,LINEAGE_CARD_H=72,LINEAGE_GAP_X=20,LINEAGE_GAP_Y=18,LINEAGE_LAYER_GAP=48,LINEAGE_LAYER_HEADING_H=28,LINEAGE_ZOOM_MIN=.45,LINEAGE_ZOOM_MAX=1.8;
const LINEAGE_SEMANTIC_LAYERS=[
  {id:"analyst",label:"Analyst input / collection",category:"data"},
  {id:"input-transform",label:"Transformation · input → state",category:"operation"},
  {id:"derived",label:"Derived state",category:"data"},
  {id:"state-transform",label:"Transformation · state processing",category:"operation"},
  {id:"document-materialization",label:"Transformation · state → document / materialization",category:"operation"},
  {id:"document",label:"Document",category:"data"},
  {id:"document-transform",label:"Transformation · document processing / rematerialization",category:"operation"},
  {id:"package-transform",label:"Transformation · document → package",category:"operation"},
  {id:"archive",label:"Archive / package",category:"data"},
];
function lineageIsTransformation(node){return Boolean(node&&String(node.kind||"").startsWith("transform_"));}
function lineageIsPackageSourceResource(node){return Boolean(node&&(node.kind==="document"||node.kind==="artifact")&&node.artifact_role==="package_source_resource");}
function lineageBaseDataRank(node){
  if(!node) return null;
  if(node.kind==="analyst_input") return 0;
  if(node.kind==="derived_state") return 2;
  if(node.kind==="document"||node.kind==="artifact"){
    if(lineageIsPackageSourceResource(node)) return null;
    return 5;
  }
  if(node.kind==="archive") return 8;
  return null;
}
function lineageTransformationRank(node,data){
  if(!lineageIsTransformation(node)) return lineageBaseDataRank(node);
  const graph=data||state.lineage.data||{},nodes=graph.nodes||[],edges=(graph.edges||[]).filter(e=>!e.hidden_projection),byId=new Map(nodes.map(n=>[n.id,n]));
  const incoming=[],outgoing=[];
  for(const edge of edges){
    if(edge.target===node.id){
      const rank=lineageBaseDataRank(byId.get(edge.source));
      if(rank!==null) incoming.push(rank);
    }
    if(edge.source===node.id){
      const rank=lineageBaseDataRank(byId.get(edge.target));
      if(rank!==null) outgoing.push(rank);
    }
  }
  const inMax=incoming.length?Math.max(...incoming):null;
  const outMax=outgoing.length?Math.max(...outgoing):null;

  // Package creation is always its own operation lane.
  if(node.kind==="transform_package" || outMax===8) return 7;

  // Operations that consume a generated document belong after the Document lane.
  // This keeps document→document rematerialization visually separate from documents.
  if(inMax===5) return 6;

  // Operations that produce documents but consume only input/state belong immediately
  // before Document.
  if(outMax===5) return 4;

  // State→state operations get their own lane after Derived state.
  if(inMax===2 && outMax===2) return 3;

  // Input/analyst values transformed into state belong between input and state.
  if((inMax===0||inMax===null) && outMax===2) return 1;

  // Analyst-interaction/model operations that remain in analyst-input semantics stay
  // in the input-transform lane rather than sharing the Analyst input row.
  if(outMax===0) return 1;

  // State-consuming operations with unresolved/no data output are state-processing.
  if(inMax===2) return 3;

  // Template-only operation producing a document without discovered state inputs.
  if(node.kind==="transform_template") return 4;
  if(node.kind==="transform_analyst") return 1;

  return 3;
}
function lineageSemanticLayer(node,data){
  if(!node) return 2;
  const rank=lineageIsTransformation(node)?lineageTransformationRank(node,data):lineageBaseDataRank(node);
  if(rank!==null&&Number.isFinite(rank)) return Math.max(0,Math.min(8,rank));
  if(lineageIsPackageSourceResource(node)) return 5;
  return 2;
}
function lineageNonTransformRank(node,data){
  if(!node) return null;
  return lineageSemanticLayer(node,data);
}
function lineageInitialBound(data,entityId,direction){
  const selected=(data.nodes||[]).find(n=>n.id===entityId);
  const rank=lineageSemanticLayer(selected,data);
  return Number.isFinite(rank)?rank:(direction==="up"?LINEAGE_SEMANTIC_LAYERS.length-1:0);
}
function lineageAllowsCausalStep(fromNode,toNode,direction,data){
  if(lineageIsPackageSourceResource(fromNode)||lineageIsPackageSourceResource(toNode)) return false;
  const fromRank=lineageSemanticLayer(fromNode,data),toRank=lineageSemanticLayer(toNode,data);
  if(direction==="down") return toRank>=fromRank;
  if(direction==="up") return toRank<=fromRank;
  return false;
}
function lineageDirectedReachable(data,entityId,direction){
  const edges=(data.edges||[]).filter(e=>!e.hidden_projection);
  const visited=new Set([entityId]),reachable=new Set(),traversedEdges=[],distance=new Map([[entityId,0]]),queue=[entityId];
  while(queue.length){
    const current=queue.shift(),currentDistance=distance.get(current)||0;
    for(const edge of edges){
      const matches=direction==="up"?edge.target===current:edge.source===current;
      if(!matches) continue;
      const nextId=direction==="up"?edge.source:edge.target;
      if(!nextId||visited.has(nextId)) continue;
      visited.add(nextId);
      reachable.add(nextId);
      distance.set(nextId,currentDistance+1);
      traversedEdges.push(edge);
      queue.push(nextId);
    }
  }
  return {nodes:reachable,edges:traversedEdges,distance};
}
function lineageFocusedSlice(data,entityId){
  const up=lineageDirectedReachable(data,entityId,"up");
  const down=lineageDirectedReachable(data,entityId,"down");
  const visible=new Set([entityId,...up.nodes,...down.nodes]);
  const edgeMap=new Map();
  for(const edge of [...up.edges,...down.edges]){
    const key=`${edge.source}|${edge.target}|${edge.relation||""}`;
    if(!edgeMap.has(key)) edgeMap.set(key,edge);
  }
  const signedDistance=new Map([[entityId,0]]),membership=new Map([[entityId,new Set(["root"])]]);
  for(const [id,d] of up.distance.entries()){
    if(id===entityId) continue;
    signedDistance.set(id,-d);
    membership.set(id,new Set(["up"]));
  }
  for(const [id,d] of down.distance.entries()){
    if(id===entityId) continue;
    const existing=signedDistance.get(id);
    if(existing===undefined || d<Math.abs(existing) || (d===Math.abs(existing)&&existing>0)) signedDistance.set(id,d);
    const set=membership.get(id)||new Set();set.add("down");membership.set(id,set);
  }
  return {visible,edges:[...edgeMap.values()],up,down,signedDistance,membership};
}
function lineageFocusedDisplayEdges(){
  const data=state.lineage.data||{},base=(data.edges||[]).filter(e=>!e.hidden_projection);
  if(!state.lineage.focusRoot) return base;
  return lineageFocusedSlice(data,state.lineage.focusRoot).edges;
}
function lineageVisibleNodeIds(){
  const data=state.lineage.data||{},all=data.nodes||[];
  if(state.lineage.focusRoot) return lineageFocusedSlice(data,state.lineage.focusRoot).visible;
  if(state.lineage.filterMode==="issues") return lineageIssueContextIds();
  return new Set(all.map(n=>n.id));
}
function lineageIssueNodes(){
  return (state.lineage.data?.nodes||[]).filter(node=>Boolean(node.lineage_diagnostic));
}
function lineageIssueContextIds(){
  const data=state.lineage.data||{},edges=(data.edges||[]).filter(e=>!e.hidden_projection),issueIds=new Set(lineageIssueNodes().map(n=>n.id)),visible=new Set(issueIds);
  for(const edge of edges){
    if(issueIds.has(edge.source)) visible.add(edge.target);
    if(issueIds.has(edge.target)) visible.add(edge.source);
  }
  return visible;
}
function setLineageFilterMode(mode){
  state.lineage.filterMode=mode==="issues"?"issues":"all";
  state.lineage.selected=null;state.lineage.focusRoot=null;state.lineage.messages=[];state.lineage.busy=false;
  renderLineageGraph();
}
function buildLineageExportReport(){
  const data=state.lineage.data||{},nodes=data.nodes||[],edges=(data.edges||[]).filter(e=>!e.hidden_projection);
  const issues=nodes.filter(n=>n.lineage_diagnostic).map(n=>({
    id:n.id,label:n.label||n.id,kind:n.kind,
    semantic_layer:LINEAGE_SEMANTIC_LAYERS[lineageSemanticLayer(n,data)]?.label||"Derived state",
    diagnostic:n.lineage_diagnostic,
    producer_nodes:n.producer_nodes||[],
    consumer_nodes:n.consumer_nodes||[],
    candidate_usage_resources:n.candidate_usage_resources||[]
  }));
  const isolated=nodes.filter(n=>!edges.some(e=>e.source===n.id||e.target===n.id)).map(n=>n.id);
  return {
    schema:"ordo.editor.data_flow_report",version:"1.0",generated_at:new Date().toISOString(),
    package:{id:state.packageInfo?.id||null,name:state.packageInfo?.name||state.packageInfo?.filename||null},
    summary:{
      entities:nodes.length,relations:edges.length,final_artifacts:nodes.filter(n=>n.final_artifact).length,
      issues:issues.length,isolated_entities:isolated.length,
      semantic_layers:LINEAGE_SEMANTIC_LAYERS.map((layer,index)=>({id:layer.id,label:layer.label,entities:nodes.filter(n=>lineageSemanticLayer(n,data)===index).length}))
    },
    issues,isolated_entities:isolated,
    final_artifacts:nodes.filter(n=>n.final_artifact).map(n=>n.id),
    entities:nodes,relations:edges,source_summary:data.summary||{}
  };
}
function exportLineageReportJson(){
  const report=buildLineageExportReport(),blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"}),url=URL.createObjectURL(blob),a=document.createElement("a");
  const base=(state.packageInfo?.name||state.packageInfo?.filename||"playbook").replace(/\.[^.]+$/,"").replace(/[^A-Za-z0-9._-]+/g,"_");
  a.href=url;a.download=`${base}_DATA_FLOW_REPORT.json`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function lineageClampZoom(v){return Math.max(LINEAGE_ZOOM_MIN,Math.min(LINEAGE_ZOOM_MAX,Number(v)||1));}
function updateLineageViewportTransform(){const stage=document.querySelector("#lineage-stage"),world=document.querySelector("#lineage-world"),reset=document.querySelector("#lineage-zoom-reset");if(!stage||!world)return;const z=lineageClampZoom(state.lineage.zoom);state.lineage.zoom=z;const w=Math.max(1,state.lineage.worldWidth||1),h=Math.max(1,state.lineage.worldHeight||1);stage.style.width=`${Math.ceil(w*z)}px`;stage.style.height=`${Math.ceil(h*z)}px`;world.style.width=`${w}px`;world.style.height=`${h}px`;world.style.transform=`scale(${z})`;if(reset)reset.textContent=`${Math.round(z*100)}%`;}
function setLineageZoom(v){const vp=document.querySelector("#lineage-viewport");if(!vp)return;const old=state.lineage.zoom||1,cx=vp.scrollLeft+vp.clientWidth/2,cy=vp.scrollTop+vp.clientHeight/2;state.lineage.zoom=lineageClampZoom(v);updateLineageViewportTransform();const ratio=state.lineage.zoom/old;vp.scrollLeft=Math.max(0,cx*ratio-vp.clientWidth/2);vp.scrollTop=Math.max(0,cy*ratio-vp.clientHeight/2);}
function fitLineageToViewport(){const vp=document.querySelector("#lineage-viewport");if(!vp||!state.lineage.worldWidth||!state.lineage.worldHeight)return;state.lineage.zoom=lineageClampZoom(Math.min(1,(vp.clientWidth-36)/state.lineage.worldWidth,(vp.clientHeight-36)/state.lineage.worldHeight));updateLineageViewportTransform();vp.scrollTo({left:0,top:0,behavior:"smooth"});}
function lineageRedrawEdges(){
  const svg=document.querySelector("#lineage-edges"),edges=state.lineage.focusRoot?lineageFocusedDisplayEdges():(state.lineage.data?.edges||[]).filter(e=>!e.hidden_projection),pos=state.lineage.positions||{};
  if(!svg)return;
  svg.innerHTML="";
  for(const e of edges){
    const a=pos[e.source],b=pos[e.target];if(!a||!b)continue;
    const sx=a.x+LINEAGE_CARD_W/2,sy=a.y+LINEAGE_CARD_H,tx=b.x+LINEAGE_CARD_W/2,ty=b.y;
    const vertical=Math.max(22,Math.abs(ty-sy)*.46),d=`M ${sx} ${sy} C ${sx} ${sy+vertical}, ${tx} ${ty-vertical}, ${tx} ${ty}`;
    const p=document.createElementNS("http://www.w3.org/2000/svg","path");
    p.setAttribute("d",d);
    p.setAttribute("class",`lineage-edge relation-${e.relation}${state.lineage.focusRoot?" active":""}${e.collapsed?" collapsed":""}`);
    p.dataset.source=e.source;p.dataset.target=e.target;
    const t=document.createElementNS("http://www.w3.org/2000/svg","title");t.textContent=e.relation;p.append(t);svg.append(p);
    if(state.lineage.focusRoot){
      const hit=document.createElementNS("http://www.w3.org/2000/svg","path");
      hit.setAttribute("d",d);hit.setAttribute("class","lineage-edge-hit");
      hit.dataset.source=e.source;hit.dataset.target=e.target;
      svg.append(hit);bindLineageEdgeHover(hit,p);
    }
  }
}
function clearLineageEdgeHover(){
  const vp=document.querySelector("#lineage-viewport");if(!vp)return;
  vp.classList.remove("edge-hover-active");
  vp.querySelectorAll(".lineage-edge.edge-hovered,.lineage-node.edge-endpoint").forEach(el=>el.classList.remove("edge-hovered","edge-endpoint"));
}
function bindLineageEdgeHover(hitPath,visualPath){
  hitPath.addEventListener("pointerenter",()=>{
    if(!state.lineage.focusRoot) return;
    const vp=document.querySelector("#lineage-viewport");if(!vp)return;
    clearLineageEdgeHover();vp.classList.add("edge-hover-active");visualPath.classList.add("edge-hovered");
    for(const id of [hitPath.dataset.source,hitPath.dataset.target]){
      vp.querySelector(`.lineage-node[data-lineage-id="${CSS.escape(id||"")}"]`)?.classList.add("edge-endpoint");
    }
  });
  hitPath.addEventListener("pointerleave",clearLineageEdgeHover);
}
function setLineageLayoutMode(mode){
  state.lineage.layoutMode=mode==="free"?"free":"auto";
  document.querySelector("#lineage-layout-auto")?.classList.toggle("active",state.lineage.layoutMode==="auto");
  document.querySelector("#lineage-layout-free")?.classList.toggle("active",state.lineage.layoutMode==="free");
  document.querySelector("#lineage-viewport")?.classList.toggle("free-layout",state.lineage.layoutMode==="free");
}
function lineageLocalFallback(entity){const d=entity?.lineage_diagnostic,p=(entity?.producer_nodes||[]).join(", ")||"none declared",c=(entity?.consumer_nodes||[]).join(", ")||"none discovered";let x=`### ${entity?.label||entity?.id||"Selected entity"}\n\n**Type:** ${lineageKindLabel(entity?.kind)}  \n**Produced by:** ${p}  \n**Consumed by:** ${c}.`;if(d)x+=`\n\n**Lineage diagnostic — ${d.label}:** ${d.message}`;const r=entity?.candidate_usage_resources||[];if(r.length)x+=`\n\n**Candidate resource references:**\n${r.map(v=>`- \`${v}\``).join("\n")}`;return x+`\n\nThis fallback is generated locally from discovered lineage metadata because the model explanation was unavailable. It does not add undeclared dependencies.`;}
function bindLineageInteractions(){
  document.querySelector("#lineage-zoom-out")?.addEventListener("click",()=>setLineageZoom((state.lineage.zoom||1)-.1));
  document.querySelector("#lineage-zoom-in")?.addEventListener("click",()=>setLineageZoom((state.lineage.zoom||1)+.1));
  document.querySelector("#lineage-zoom-reset")?.addEventListener("click",()=>setLineageZoom(1));
  document.querySelector("#lineage-zoom-fit")?.addEventListener("click",fitLineageToViewport);
  document.querySelector("#lineage-layout-auto")?.addEventListener("click",()=>{state.lineage.positions={};setLineageLayoutMode("auto");renderLineageGraph();});
  document.querySelector("#lineage-layout-free")?.addEventListener("click",()=>setLineageLayoutMode("free"));
  document.querySelector("#lineage-filter-all")?.addEventListener("click",()=>setLineageFilterMode("all"));
  document.querySelector("#lineage-filter-issues")?.addEventListener("click",()=>setLineageFilterMode("issues"));
  document.querySelector("#lineage-export-json")?.addEventListener("click",exportLineageReportJson);
  const vp=document.querySelector("#lineage-viewport");
  vp?.addEventListener("pointerdown",e=>{
    if(e.button!==0||e.target.closest(".lineage-node")||e.target.closest(".lineage-controls"))return;
    state.lineage.pan={x:e.clientX,y:e.clientY,left:vp.scrollLeft,top:vp.scrollTop,id:e.pointerId,moved:false};
    vp.setPointerCapture?.(e.pointerId);vp.classList.add("panning");
  });
  vp?.addEventListener("pointermove",e=>{
    const p=state.lineage.pan;if(!p||p.id!==e.pointerId)return;
    const dx=e.clientX-p.x,dy=e.clientY-p.y;if(Math.abs(dx)>4||Math.abs(dy)>4)p.moved=true;
    vp.scrollLeft=p.left-dx;vp.scrollTop=p.top-dy;
  });
  const stop=e=>{
    const p=state.lineage.pan,wasClick=Boolean(p&&p.id===e.pointerId&&!p.moved);
    state.lineage.pan=null;vp?.classList.remove("panning");
    if(wasClick&&state.lineage.focusRoot){state.lineage.focusRoot=null;state.lineage.selected=null;state.lineage.positions={};state.lineage.messages=[];state.lineage.busy=false;renderLineageGraph();}
  };
  vp?.addEventListener("pointerup",stop);
  vp?.addEventListener("pointercancel",()=>{state.lineage.pan=null;vp?.classList.remove("panning");});
}

const SOURCE_FLOW_CARD_W=196,SOURCE_FLOW_CARD_H=82,SOURCE_FLOW_GAP_X=34,SOURCE_FLOW_GAP_Y=54;
function sourceFlowClampZoom(v){return Math.max(.25,Math.min(2.2,Number(v)||1));}
function sourceFlowNodeTypeLabel(type){return ({analyst_question:"analyst question",analyst_input:"analyst input",interaction:"interaction",transformation:"transformation",variable:"variable",gate:"gate",gate_fragment:"gate",artifact:"artifact",contract_branch:"contract branch",verified_contract:"verified contract",verified_artifact_set:"verified artifact set",terminal:"terminal",reference:"reference"})[type]||type||"information object";}
function sourceFlowNodeTypeIcon(type){return ({analyst_question:"↔",analyst_input:"↔",interaction:"↔",transformation:"ƒ",variable:"{}",gate:"◇",gate_fragment:"◇",artifact:"▤",contract_branch:"⋮",verified_contract:"✓",verified_artifact_set:"✓",terminal:"■",reference:"↗"})[type]||"·";}
function sourceFlowLegendNodeGroup(type){
  if(type==="variable")return "variable";
  if(type==="transformation")return "transformation";
  if(["interaction","analyst_input","analyst_question"].includes(type))return "interaction";
  if(["gate","gate_fragment"].includes(type))return "gate";
  if(type==="artifact")return "artifact";
  if(["contract_branch","verified_contract","verified_artifact_set"].includes(type))return "contract";
  return "other";
}
function sourceFlowLegendEdgeGroup(edge,role=""){
  if((edge?.type||"")==="validation")return "validation";
  return "relation";
}
function sourceFlowLegendMatchesNode(node,selection){
  return selection&&selection.kind==="node"&&sourceFlowLegendNodeGroup(node?.type)===selection.value;
}
function sourceFlowLegendMatchesEdge(edge,role,selection){
  return selection&&selection.kind==="edge"&&sourceFlowLegendEdgeGroup(edge,role)===selection.value;
}
function sourceFlowTraceRoot(){return state.lineage.sourceFocusRoot||state.lineage.sourceSelected||null;}
function sourceFlowActiveTrace(graph=activeSourceFlowGraph()){
  const root=sourceFlowTraceRoot();
  return root?sourceFlowDirectionalTrace(graph,root):null;
}
function setSourceFlowLegendSelection(kind,value){
  if(kind==="trace"){
    state.lineage.sourceTraceDirection=state.lineage.sourceTraceDirection===value?null:value;
    state.lineage.sourceLegend=null;
  }else{
    const current=state.lineage.sourceLegend;
    state.lineage.sourceLegend=current&&current.kind===kind&&current.value===value?null:{kind,value};
    state.lineage.sourceTraceDirection=null;
  }
  renderSourceDataFlow();
}
function clearSourceFlowLegendSelection(){state.lineage.sourceLegend=null;state.lineage.sourceTraceDirection=null;}
function updateSourceFlowLegend(graph=activeSourceFlowGraph(),trace=sourceFlowActiveTrace(graph)){
  const buttons=[...document.querySelectorAll('.source-flow-legend-item')],selection=state.lineage.sourceLegend,traceDirection=state.lineage.sourceTraceDirection;
  const nodeGroups=new Set((graph?.nodes||[]).map(n=>sourceFlowLegendNodeGroup(n.type)));
  const semanticEdges=(graph?.edges||[]).filter(e=>e.type!=="invisible"),hasValidation=semanticEdges.some(e=>(e.type||'')==='validation'),hasSemanticEdges=semanticEdges.length>0;
  for(const btn of buttons){
    const kind=btn.dataset.legendKind||'',value=btn.dataset.legendValue||'';
    let available=true;
    if(kind==='node') available=nodeGroups.has(value);
    else if(kind==='edge') available=value==='validation'?hasValidation:hasSemanticEdges;
    else if(kind==='trace') available=hasSemanticEdges;
    btn.disabled=!available;
    const active=kind==='trace'?traceDirection===value:Boolean(selection&&selection.kind===kind&&selection.value===value);
    btn.classList.toggle('active',active);
    btn.classList.toggle('awaiting-root',kind==='trace'&&active&&!sourceFlowTraceRoot());
    btn.setAttribute('aria-pressed',active?'true':'false');
    if(kind==='trace') btn.title=sourceFlowTraceRoot()?`Highlight ${value} relations from ${sourceFlowTraceRoot()}`:`Choose ${value}, then click a graph node to set the trace root`;
  }
}
function sourceFlowDirectionalTrace(graph,root){
  const ids=new Set((graph?.nodes||[]).map(n=>n.id)),edges=(graph?.edges||[]).filter(e=>ids.has(e.from)&&ids.has(e.to)&&e.type!=="invisible");
  const upstream=new Set(root&&ids.has(root)?[root]:[]),downstream=new Set(root&&ids.has(root)?[root]:[]);
  const walk=(seen,forward)=>{
    const queue=[...seen];
    while(queue.length){
      const id=queue.shift();
      for(const edge of edges){
        const next=forward?(edge.from===id?edge.to:null):(edge.to===id?edge.from:null);
        if(next&&!seen.has(next)){seen.add(next);queue.push(next);}
      }
    }
  };
  walk(upstream,false);walk(downstream,true);
  const visible=new Set([...upstream,...downstream]);
  return {upstream,downstream,visible};
}
function sourceFlowArtifactPresentation(node){
  if(node?.type!=="artifact") return {className:"",badge:""};
  const meta=node.artifact_metadata||{},text=[node.label,node.id,node.artifact_ref,meta.expected_path,meta.path,meta.state_path].filter(Boolean).join(" ");
  const archive=text.match(/\.(zip|tar|tgz|gz|bz2|7z)(?:\b|$)/i);
  if(archive) return {className:"artifact-archive",badge:String(archive[1]||"archive").toUpperCase()};
  const doc=text.match(/\.(md|markdown|json|ya?ml|txt|csv|tsv|html?|xml|pdf|docx?|xlsx?)(?:\b|$)/i);
  return {className:"artifact-document",badge:doc?String(doc[1]).toUpperCase():"FILE"};
}
function sourceFlowSegments(points){
  const out=[];for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i];if(a.x===b.x&&a.y===b.y)continue;out.push({x1:a.x,y1:a.y,x2:b.x,y2:b.y,o:a.y===b.y?"h":"v"});}return out;
}
function sourceFlowPath(points){return points.map((p,i)=>`${i?"L":"M"} ${p.x} ${p.y}`).join(" ");}
function sourceFlowSegmentOverlap(a,b,clearance=4){
  if(a.o!==b.o)return false;if(a.o==="h"){if(Math.abs(a.y1-b.y1)>=clearance)return false;return Math.max(Math.min(a.x1,a.x2),Math.min(b.x1,b.x2))<Math.min(Math.max(a.x1,a.x2),Math.max(b.x1,b.x2))-2;}
  if(Math.abs(a.x1-b.x1)>=clearance)return false;return Math.max(Math.min(a.y1,a.y2),Math.min(b.y1,b.y2))<Math.min(Math.max(a.y1,a.y2),Math.max(b.y1,b.y2))-2;
}
function sourceFlowSegmentCross(a,b,clearance=2){
  if(a.o===b.o)return false;const h=a.o==="h"?a:b,v=a.o==="v"?a:b,hx1=Math.min(h.x1,h.x2),hx2=Math.max(h.x1,h.x2),vy1=Math.min(v.y1,v.y2),vy2=Math.max(v.y1,v.y2);return v.x1>hx1+clearance&&v.x1<hx2-clearance&&h.y1>vy1+clearance&&h.y1<vy2-clearance;
}
function sourceFlowSegmentHitsNode(seg,node,clearance=8){
  const minX=node.x-clearance,maxX=node.x+SOURCE_FLOW_CARD_W+clearance,minY=node.y-clearance,maxY=node.y+SOURCE_FLOW_CARD_H+clearance;
  if(seg.o==="h"){const x1=Math.min(seg.x1,seg.x2),x2=Math.max(seg.x1,seg.x2);return seg.y1>=minY&&seg.y1<=maxY&&x2>minX&&x1<maxX;}
  const y1=Math.min(seg.y1,seg.y2),y2=Math.max(seg.y1,seg.y2);return seg.x1>=minX&&seg.x1<=maxX&&y2>minY&&y1<maxY;
}
function sourceFlowPortOffset(graph,nodeId,fromId,toId,endpoint){
  const edges=(graph.edges||[]).filter(e=>e.type!=="invisible"&&(endpoint==="source"?e.from===nodeId:e.to===nodeId)).sort((a,b)=>{
    const ap=endpoint==="source"?a.to:a.from,bp=endpoint==="source"?b.to:b.from;
    return String(ap).localeCompare(String(bp))||String(a.type||"").localeCompare(String(b.type||""));
  });
  const index=edges.findIndex(e=>e.from===fromId&&e.to===toId);if(index<0||edges.length<=1)return 0;
  const slot=index-(edges.length-1)/2;
  return Math.max(-36,Math.min(36,slot*14));
}
function sourceFlowRankLookup(positions,direction="TB"){
  const axis=direction==="LR"?"x":"y",values=[...new Set(Object.values(positions||{}).map(p=>Number(p?.[axis]||0)))].sort((a,b)=>a-b),map=new Map();
  values.forEach((v,i)=>map.set(v,i));
  const ranks=new Map();
  for(const [id,pos] of Object.entries(positions||{}))ranks.set(id,map.get(Number(pos?.[axis]||0))||0);
  return ranks;
}
function sourceFlowBandLaneAssignments(graph,positions,direction="TB"){
  const ranks=sourceFlowRankLookup(positions,direction),groups=new Map(),assignments=new Map();
  const keyOf=e=>`${e.from}->${e.to}:${e.type||"relation"}`;
  const edges=(graph.edges||[]).filter(e=>e.type!=="invisible"&&positions[e.from]&&positions[e.to]);
  for(const e of edges){
    const sr=ranks.get(e.from)||0,tr=ranks.get(e.to)||0;
    const bandKey=direction==="LR"?`x:${Math.min(sr,tr)}-${Math.max(sr,tr)}`:`y:${Math.min(sr,tr)}-${Math.max(sr,tr)}`;
    if(!groups.has(bandKey))groups.set(bandKey,[]);
    groups.get(bandKey).push(e);
  }
  for(const [bandKey,list] of groups){
    const sorted=[...list].sort((a,b)=>{
      const ap=positions[a.from],at=positions[a.to],bp=positions[b.from],bt=positions[b.to];
      if(direction==="LR") return (ap.y-bp.y)||(at.y-bt.y)||keyOf(a).localeCompare(keyOf(b));
      return (ap.x-bp.x)||(at.x-bt.x)||keyOf(a).localeCompare(keyOf(b));
    });
    const count=sorted.length;
    sorted.forEach((edge,index)=>{
      const slot=index-(count-1)/2;
      const base=slot*16;
      assignments.set(keyOf(edge),direction==="LR"?{x:0,y:base,band:bandKey}:{x:base,y:0,band:bandKey});
    });
  }
  return assignments;
}
function sourceFlowRouteCandidates(a,b,direction="TB",ports={source:0,target:0},laneHint={x:0,y:0}){
  const c=[];
  if(direction==="LR"){
    const start={x:a.x+SOURCE_FLOW_CARD_W,y:a.y+SOURCE_FLOW_CARD_H/2+(ports.source||0)},end={x:b.x,y:b.y+SOURCE_FLOW_CARD_H/2+(ports.target||0)};
    if(Math.abs(start.y-end.y)<=8&&Math.abs(laneHint.y||0)<=6)c.push({kind:"direct",points:[start,end]});
    const base=(start.x+end.x)/2+(laneHint.x||0);
    for(const d of [0,12,-12,24,-24,38,-38,54,-54,74,-74,98,-98,126,-126]){const x=base+d;c.push({kind:"elbow",points:[start,{x,y:start.y},{x,y:end.y},end]});}
    const topY=Math.min(a.y,b.y)-32+(laneHint.y||0),bottomY=Math.max(a.y+SOURCE_FLOW_CARD_H,b.y+SOURCE_FLOW_CARD_H)+32+(laneHint.y||0);
    c.push({kind:"detour",points:[start,{x:start.x+18,y:start.y},{x:start.x+18,y:topY},{x:end.x-18,y:topY},{x:end.x-18,y:end.y},end]});
    c.push({kind:"detour",points:[start,{x:start.x+18,y:start.y},{x:start.x+18,y:bottomY},{x:end.x-18,y:bottomY},{x:end.x-18,y:end.y},end]});
    return c;
  }
  const start={x:a.x+SOURCE_FLOW_CARD_W/2+(ports.source||0),y:a.y+SOURCE_FLOW_CARD_H},end={x:b.x+SOURCE_FLOW_CARD_W/2+(ports.target||0),y:b.y};
  if(Math.abs(start.x-end.x)<=8&&Math.abs(laneHint.x||0)<=6)c.push({kind:"direct",points:[start,end]});
  const base=(start.y+end.y)/2+(laneHint.y||0);
  for(const d of [0,10,-10,20,-20,32,-32,46,-46,64,-64,84,-84,108,-108,136,-136]){const y=base+d;c.push({kind:"elbow",points:[start,{x:start.x,y},{x:end.x,y},end]});}
  const leftX=Math.min(a.x,b.x)-28+(laneHint.x||0),rightX=Math.max(a.x+SOURCE_FLOW_CARD_W,b.x+SOURCE_FLOW_CARD_W)+28+(laneHint.x||0);
  c.push({kind:"detour",points:[start,{x:start.x,y:start.y+18},{x:leftX,y:start.y+18},{x:leftX,y:end.y-18},{x:end.x,y:end.y-18},end]});
  c.push({kind:"detour",points:[start,{x:start.x,y:start.y+18},{x:rightX,y:start.y+18},{x:rightX,y:end.y-18},{x:end.x,y:end.y-18},end]});
  if(Math.abs(start.x-end.x)>90){
    const sourceRight=end.x>=start.x,aSide=sourceRight?a.x+SOURCE_FLOW_CARD_W:a.x,bSide=sourceRight?b.x:b.x+SOURCE_FLOW_CARD_W,sy=a.y+SOURCE_FLOW_CARD_H/2+(ports.source||0),ey=b.y+SOURCE_FLOW_CARD_H/2+(ports.target||0),mid=(aSide+bSide)/2+(laneHint.x||0);
    for(const d of [0,16,-16,30,-30,48,-48,70,-70,96,-96]){const x=mid+d;c.push({kind:"side",points:[{x:aSide,y:sy},{x,y:sy},{x,y:ey},{x:bSide,y:ey}]});}
  }
  return c;
}
function sourceFlowPlanRoutes(graph,positions,direction="TB"){
  const edges=(graph.edges||[]).filter(e=>e.type!=="invisible"&&positions[e.from]&&positions[e.to]);
  const reserved=[],routes=new Map();let totalOverlap=0,totalCross=0,totalBlocked=0,totalScore=0;
  const laneHints=sourceFlowBandLaneAssignments(graph,positions,direction);
  const edgeItems=edges.map(e=>{const a=positions[e.from],b=positions[e.to],span=direction==="LR"?Math.abs(b.x-a.x):Math.abs(b.y-a.y);return {e,span,key:`${e.from}->${e.to}:${e.type||"relation"}`};}).sort((a,b)=>a.span-b.span||a.key.localeCompare(b.key));
  for(const item of edgeItems){
    const {e,key}=item,a=positions[e.from],b=positions[e.to];let best=null;
    const ports={source:sourceFlowPortOffset(graph,e.from,e.from,e.to,"source"),target:sourceFlowPortOffset(graph,e.to,e.from,e.to,"target")};
    const laneHint=laneHints.get(key)||{x:0,y:0};
    for(const candidate of sourceFlowRouteCandidates(a,b,direction,ports,laneHint)){
      const segs=sourceFlowSegments(candidate.points);let blocked=0,cross=0,overlap=0,length=0;
      for(const seg of segs){
        length+=Math.abs(seg.x2-seg.x1)+Math.abs(seg.y2-seg.y1);
        for(const n of graph.nodes||[]){if(n.id===e.from||n.id===e.to)continue;const p=positions[n.id];if(p&&sourceFlowSegmentHitsNode(seg,p))blocked++;}
        for(const r of reserved){const hitOverlap=sourceFlowSegmentOverlap(seg,r),hitCross=!hitOverlap&&sourceFlowSegmentCross(seg,r);if(!hitOverlap&&!hitCross)continue;if(r.terminal){blocked+=4;}else if(hitOverlap)overlap++;else if(hitCross)cross++;}
      }
      const bends=Math.max(0,segs.length-1),kindPenalty=candidate.kind==="direct"?0:candidate.kind==="elbow"?2:candidate.kind==="side"?5:10;
      const lanePenalty=(Math.abs(laneHint.x||0)+Math.abs(laneHint.y||0))*0.03;
      const score=blocked*10000000+overlap*2000000+cross*4000+bends*4+length*.01+kindPenalty+lanePenalty;
      if(!best||score<best.score-.001){best={...candidate,segs,score,blocked,cross,overlap};}
    }
    if(best){routes.set(key,sourceFlowPath(best.points));best.segs.forEach((s,index)=>reserved.push({...s,owner:key,terminal:index===0||index===best.segs.length-1}));totalOverlap+=best.overlap;totalCross+=best.cross;totalBlocked+=best.blocked;totalScore+=best.score;}
  }
  routes.stats={overlap:totalOverlap,cross:totalCross,blocked:totalBlocked,score:totalScore,edgeCount:edgeItems.length};
  return routes;
}
function sourceFlowOrthogonalPath(a,b,direction="TB"){
  const first=sourceFlowRouteCandidates(a,b,direction)[0];return first?sourceFlowPath(first.points):"";
}
function updateSourceFlowTransform(){
  const stage=document.querySelector("#source-flow-stage"),world=document.querySelector("#source-flow-world"),reset=document.querySelector("#source-flow-zoom-reset");if(!stage||!world)return;
  const z=sourceFlowClampZoom(state.lineage.sourceZoom);state.lineage.sourceZoom=z;const w=Math.max(1,state.lineage.sourceWorldWidth||1),h=Math.max(1,state.lineage.sourceWorldHeight||1);
  stage.style.width=`${Math.ceil(w*z)}px`;stage.style.height=`${Math.ceil(h*z)}px`;world.style.width=`${w}px`;world.style.height=`${h}px`;world.style.transform=`scale(${z})`;if(reset)reset.textContent=`${Math.round(z*100)}%`;
}
function setSourceFlowZoom(v){const vp=document.querySelector("#source-flow-viewport");if(!vp)return;const old=state.lineage.sourceZoom||1,cx=vp.scrollLeft+vp.clientWidth/2,cy=vp.scrollTop+vp.clientHeight/2;state.lineage.sourceZoom=sourceFlowClampZoom(v);updateSourceFlowTransform();const ratio=state.lineage.sourceZoom/old;vp.scrollLeft=Math.max(0,cx*ratio-vp.clientWidth/2);vp.scrollTop=Math.max(0,cy*ratio-vp.clientHeight/2);}
function fitSourceFlowToViewport(){const vp=document.querySelector("#source-flow-viewport");if(!vp||!state.lineage.sourceWorldWidth||!state.lineage.sourceWorldHeight)return;const zx=(vp.clientWidth-24)/state.lineage.sourceWorldWidth,zy=(vp.clientHeight-24)/state.lineage.sourceWorldHeight;state.lineage.sourceZoom=sourceFlowClampZoom(Math.min(1,zx,zy));updateSourceFlowTransform();vp.scrollTo({left:0,top:0});}
function setSourceFlowLayoutMode(mode){state.lineage.sourceLayoutMode=mode==="free"?"free":"auto";document.querySelector("#source-flow-layout-auto")?.classList.toggle("active",state.lineage.sourceLayoutMode==="auto");document.querySelector("#source-flow-layout-free")?.classList.toggle("active",state.lineage.sourceLayoutMode==="free");document.querySelector("#source-flow-viewport")?.classList.toggle("free-layout",state.lineage.sourceLayoutMode==="free");}
function setSourceFlowDirection(direction){state.lineage.sourceDirection=direction==="LR"?"LR":"TB";document.querySelector("#source-flow-direction-tb")?.classList.toggle("active",state.lineage.sourceDirection==="TB");document.querySelector("#source-flow-direction-lr")?.classList.toggle("active",state.lineage.sourceDirection==="LR");state.lineage.sourcePositions={};renderSourceDataFlow();}
function setSourceFlowSubview(view){state.lineage.sourceSubview=view==="passports"?"passports":"tree";document.querySelector("#source-flow-subview-tree")?.classList.toggle("active",state.lineage.sourceSubview==="tree");document.querySelector("#source-flow-subview-passports")?.classList.toggle("active",state.lineage.sourceSubview==="passports");const tree=document.querySelector("#source-flow-tree-view"),passports=document.querySelector("#source-flow-passports-view");if(tree)tree.hidden=state.lineage.sourceSubview!=="tree";if(passports)passports.hidden=state.lineage.sourceSubview!=="passports";if(state.lineage.sourceSubview==="passports")renderSourceVariablePassports();}
function sourceFlowNodeDataClass(node){
  if(node?.type!=="variable")return null;
  const value=String(node?.variable_metadata?.data_class||"unclassified").trim().toLowerCase();
  return ["business","technical","control","metadata"].includes(value)?value:"unclassified";
}
function sourceFlowDataClassLabel(value){return ({business:"Business",technical:"Technical",control:"Control",metadata:"Metadata",unclassified:"Unclassified"})[value]||value;}
function updateSourceFlowDataClassFilter(graph){
  const select=document.querySelector("#source-flow-data-class-filter");if(!select)return;
  const counts=new Map();for(const n of graph.nodes||[]){const cls=sourceFlowNodeDataClass(n);if(cls)counts.set(cls,(counts.get(cls)||0)+1);}
  const order=["business","technical","control","metadata","unclassified"],available=order.filter(x=>counts.has(x));
  const current=state.lineage.sourceDataClassFilter||"all";
  select.innerHTML='<option value="all">All</option>'+available.map(x=>`<option value="${x}">${sourceFlowDataClassLabel(x)} (${counts.get(x)})</option>`).join("");
  state.lineage.sourceDataClassFilter=(current==="all"||available.includes(current))?current:"all";select.value=state.lineage.sourceDataClassFilter;
}
function activeSourceFlowGraph(){
  const graph=state.lineage.sourceData?.graph||{},filter=state.lineage.sourceDataClassFilter||"all";if(filter==="all")return graph;
  const nodes=graph.nodes||[],edges=(graph.edges||[]).filter(e=>e.type!=="invisible"),byId=new Map(nodes.map(n=>[n.id,n]));
  const keep=new Set(nodes.filter(n=>n.type==="variable"&&sourceFlowNodeDataClass(n)===filter).map(n=>n.id));
  for(const edge of edges){const a=byId.get(edge.from),b=byId.get(edge.to);if((a?.type==="variable"&&keep.has(a.id)&&b)||(b?.type==="variable"&&keep.has(b.id)&&a)){keep.add(edge.from);keep.add(edge.to);}}
  let changed=true;while(changed){changed=false;for(const edge of edges){const a=byId.get(edge.from),b=byId.get(edge.to);if(!a||!b)continue;const auxiliary=n=>["gate","artifact","contract"].includes(n.type);if(keep.has(a.id)&&auxiliary(b)&&!keep.has(b.id)){keep.add(b.id);changed=true;}if(keep.has(b.id)&&auxiliary(a)&&!keep.has(a.id)){keep.add(a.id);changed=true;}}}
  return {...graph,nodes:nodes.filter(n=>keep.has(n.id)),edges:(graph.edges||[]).filter(e=>keep.has(e.from)&&keep.has(e.to))};
}
function sourceFlowDependencyRanks(graph){
  const nodes=graph.nodes||[],ids=new Set(nodes.map(n=>n.id)),edges=(graph.edges||[]).filter(e=>ids.has(e.from)&&ids.has(e.to)&&e.type!=="invisible");
  const incoming=new Map(nodes.map(n=>[n.id,[]])),outgoing=new Map(nodes.map(n=>[n.id,[]])),indegree=new Map(nodes.map(n=>[n.id,0]));
  for(const e of edges){incoming.get(e.to).push(e.from);outgoing.get(e.from).push(e.to);indegree.set(e.to,(indegree.get(e.to)||0)+1);}
  const q=nodes.filter(n=>(indegree.get(n.id)||0)===0).map(n=>n.id).sort(),rank=new Map(nodes.map(n=>[n.id,0])),visited=[];
  while(q.length){const id=q.shift();visited.push(id);for(const to of outgoing.get(id)||[]){rank.set(to,Math.max(rank.get(to)||0,(rank.get(id)||0)+1));indegree.set(to,(indegree.get(to)||0)-1);if(indegree.get(to)===0)q.push(to);}q.sort();}
  // Cycles are kept visible without inventing section layers. Place unresolved SCC members after their strongest predecessor.
  const remaining=nodes.map(n=>n.id).filter(id=>!visited.includes(id));
  for(let pass=0;pass<Math.max(1,remaining.length);pass++) for(const id of remaining){const preds=incoming.get(id)||[];rank.set(id,Math.max(rank.get(id)||0,...preds.map(p=>(rank.get(p)||0)+1)));}
  const layers=new Map();for(const n of nodes){const r=rank.get(n.id)||0;if(!layers.has(r))layers.set(r,[]);layers.get(r).push(n);}
  const ordered=[...layers.entries()].sort((a,b)=>a[0]-b[0]);
  // Crossing minimization: alternate predecessor/successor barycentric sweeps.
  // The old layout only swept downward, which can improve fan-out while making
  // downstream merge points unnecessarily tangled. Alternating sweeps converge
  // toward a stable ordering that considers both sides of every rank.
  const index=new Map();ordered.forEach(([,arr])=>arr.sort((a,b)=>String(a.label||a.id).localeCompare(String(b.label||b.id))).forEach((n,i)=>index.set(n.id,i)));
  const reorder=(arr,neighbors)=>{
    arr.sort((a,b)=>{
      const na=neighbors.get(a.id)||[],nb=neighbors.get(b.id)||[];
      const ba=na.length?na.reduce((sum,id)=>sum+(index.get(id)||0),0)/na.length:(index.get(a.id)||0);
      const bb=nb.length?nb.reduce((sum,id)=>sum+(index.get(id)||0),0)/nb.length:(index.get(b.id)||0);
      return ba-bb||String(a.label||a.id).localeCompare(String(b.label||b.id));
    });
    arr.forEach((n,i)=>index.set(n.id,i));
  };
  for(let sweep=0;sweep<6;sweep++){
    for(let li=1;li<ordered.length;li++) reorder(ordered[li][1],incoming);
    for(let li=ordered.length-2;li>=0;li--) reorder(ordered[li][1],outgoing);
  }
  return ordered;
}
function sourceFlowLayoutScaled(graph,spacingScale=1){
  const layers=sourceFlowDependencyRanks(graph),positions={},direction=state.lineage.sourceDirection||"TB",margin=Math.round(44*spacingScale);
  const gapX=Math.round(SOURCE_FLOW_GAP_X*spacingScale),gapY=Math.round(SOURCE_FLOW_GAP_Y*spacingScale),rankExtra=Math.round(24*spacingScale);
  if(direction==="LR"){
    let maxCount=1;for(const [,arr] of layers)maxCount=Math.max(maxCount,arr.length);const worldH=margin*2+maxCount*SOURCE_FLOW_CARD_H+(maxCount-1)*gapY;
    layers.forEach(([,arr],li)=>{const used=arr.length*SOURCE_FLOW_CARD_H+Math.max(0,arr.length-1)*gapY,start=margin+(worldH-margin*2-used)/2;arr.forEach((n,i)=>positions[n.id]={x:margin+li*(SOURCE_FLOW_CARD_W+gapX+Math.round(44*spacingScale)),y:start+i*(SOURCE_FLOW_CARD_H+gapY)});});
    return {positions,worldWidth:margin*2+layers.length*(SOURCE_FLOW_CARD_W+gapX+Math.round(44*spacingScale)),worldHeight:Math.max(520,worldH),spacingScale};
  }
  let maxCount=1;for(const [,arr] of layers)maxCount=Math.max(maxCount,arr.length);const worldW=margin*2+maxCount*SOURCE_FLOW_CARD_W+(maxCount-1)*gapX;
  layers.forEach(([,arr],li)=>{const used=arr.length*SOURCE_FLOW_CARD_W+Math.max(0,arr.length-1)*gapX,start=margin+(worldW-margin*2-used)/2;arr.forEach((n,i)=>positions[n.id]={x:start+i*(SOURCE_FLOW_CARD_W+gapX),y:margin+li*(SOURCE_FLOW_CARD_H+gapY+rankExtra)});});
  return {positions,worldWidth:Math.max(760,worldW),worldHeight:margin*2+layers.length*(SOURCE_FLOW_CARD_H+gapY+rankExtra),spacingScale};
}
function sourceFlowLayout(graph){return sourceFlowLayoutScaled(graph,1);}
function sourceFlowAdaptiveLayout(graph){
  const direction=state.lineage.sourceDirection||"TB",scales=[1,1.16,1.34,1.56,1.82,2.12,2.46,2.84];let best=null;
  for(const scale of scales){
    const layout=sourceFlowLayoutScaled(graph,scale),routes=sourceFlowPlanRoutes(graph,layout.positions,direction),stats=routes.stats||{overlap:0,cross:0,blocked:0,score:0};
    const quality=stats.blocked*100000000+stats.overlap*10000000+stats.cross*10000+scale*10;
    const candidate={...layout,routeStats:stats,quality};
    if(!best||quality<best.quality)best=candidate;
    if(stats.blocked===0&&stats.overlap===0)break;
  }
  return best||sourceFlowLayoutScaled(graph,1);
}
function redrawSourceFlowEdges(){
  const data=state.lineage.sourceData,graph=activeSourceFlowGraph(),svg=document.querySelector("#source-flow-edges"),vp=document.querySelector("#source-flow-viewport");if(!svg||!vp)return;
  const positions=state.lineage.sourcePositions||{},selected=state.lineage.sourceSelected,trace=sourceFlowActiveTrace(graph),legendSelection=state.lineage.sourceLegend,traceDirection=state.lineage.sourceTraceDirection;
  updateSourceFlowLegend(graph,trace);
  svg.innerHTML='<defs><marker id="source-flow-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>';
  const direction=state.lineage.sourceDirection||"TB",planned=sourceFlowPlanRoutes(graph,positions,direction);
  for(const edge of graph.edges||[]){const a=positions[edge.from],b=positions[edge.to];if(!a||!b)continue;const path=document.createElementNS("http://www.w3.org/2000/svg","path");const semantic=edge.type!=="invisible",dimmed=trace&&(!trace.visible.has(edge.from)||!trace.visible.has(edge.to));let role="";if(trace&&semantic&&!dimmed){const up=trace.upstream.has(edge.from)&&trace.upstream.has(edge.to),down=trace.downstream.has(edge.from)&&trace.downstream.has(edge.to);role=up&&!down?" upstream":down&&!up?" downstream":up&&down?" upstream downstream through-cycle":"";}const active=trace&&semantic&&!dimmed,key=`${edge.from}->${edge.to}:${edge.type||"relation"}`;const legendMatch=sourceFlowLegendMatchesEdge(edge,role,legendSelection),directionMatch=traceDirection==="upstream"?role.includes("upstream"):traceDirection==="downstream"?role.includes("downstream"):false,legendDim=(legendSelection&&legendSelection.kind==="edge"&&!legendMatch)||(traceDirection&&trace&&!directionMatch),tracePending=Boolean(traceDirection&&!trace);path.setAttribute("d",planned.get(key)||sourceFlowOrthogonalPath(a,b,direction));path.setAttribute("class",`source-flow-edge type-${String(edge.type||"relation").replace(/[^A-Za-z0-9_-]/g,"-")}${edge.type==='validation'?" validation":""}${dimmed?" dimmed":""}${active?" active":""}${role}${(legendMatch||directionMatch)?" legend-match":""}${legendDim?" legend-dim":""}${tracePending?" trace-pending":""}`);path.setAttribute("marker-end","url(#source-flow-arrow)");const title=document.createElementNS("http://www.w3.org/2000/svg","title");title.textContent=`${edge.from} → ${edge.to} · ${edge.type||"relation"}`;path.append(title);svg.append(path);}
}
function sourceFlowConnectedContext(entityId){
  const graph=state.lineage.sourceData?.graph||{},nodes=graph.nodes||[],byId=new Map(nodes.map(n=>[n.id,n])),edges=(graph.edges||[]).filter(e=>e.type!=="invisible");
  const incoming=edges.filter(e=>e.to===entityId),outgoing=edges.filter(e=>e.from===entityId);
  return {incoming:incoming.map(e=>({relation:e.type||"relation",entity:byId.get(e.from)||{id:e.from}})),outgoing:outgoing.map(e=>({relation:e.type||"relation",entity:byId.get(e.to)||{id:e.to}}))};
}
function activeLineageAssistantEntity(){
  return (state.lineage.sourceData?.graph?.nodes||[]).find(n=>n.id===state.lineage.sourceSelected)||null;
}
function activeLineageAssistantContext(entity){
  if(!entity)return {incoming:[],outgoing:[]};
  return sourceFlowConnectedContext(entity.id);
}
function sourceFlowAssistantThread(entityId,{create=true}={}){
  const id=String(entityId||"");if(!id)return null;
  if(!state.lineage.assistantThreads||typeof state.lineage.assistantThreads!=="object")state.lineage.assistantThreads={};
  if(!state.lineage.assistantThreads[id]&&create)state.lineage.assistantThreads[id]={messages:[],busy:false};
  return state.lineage.assistantThreads[id]||null;
}
function activeSourceFlowAssistantThread(){
  return sourceFlowAssistantThread(state.lineage.sourceSelected,{create:false});
}
function syncActiveLineageAssistantLegacyState(){
  const thread=activeSourceFlowAssistantThread();state.lineage.messages=thread?.messages||[];state.lineage.busy=Boolean(thread?.busy);return thread;
}
function renderSourceFlowInspector(){
  const host=document.querySelector("#lineage-selection"),messages=document.querySelector("#lineage-assistant-messages"),toolbar=document.querySelector("#lineage-assistant-toolbar"),form=document.querySelector("#lineage-assistant-form"),title=document.querySelector("#lineage-inspector-title"),subtitle=document.querySelector("#lineage-inspector-subtitle"),explain=document.querySelector("#lineage-explain"),input=document.querySelector("#lineage-assistant-input"),send=document.querySelector("#lineage-assistant-send"),unavailable=document.querySelector("#lineage-model-unavailable");if(!host)return;
  if(title)title.textContent="Source Data Flow Inspector";if(subtitle)subtitle.textContent="Double-click a tree node or open a variable passport. This authoring topology never changes Ordo execution semantics.";if(toolbar)toolbar.hidden=false;if(form)form.hidden=false;if(messages)messages.hidden=false;
  const node=(state.lineage.sourceData?.graph?.nodes||[]).find(n=>n.id===state.lineage.sourceSelected),thread=syncActiveLineageAssistantLegacyState(),threadBusy=Boolean(thread?.busy),available=modelExplanationAvailable();if(unavailable)unavailable.hidden=available;if(explain){explain.disabled=!node||!available||threadBusy;explain.textContent=threadBusy?"Explaining…":"Explain with model";}if(input)input.disabled=!node||!available||threadBusy;if(send)send.disabled=!node||!available||threadBusy;
  if(!node){host.innerHTML='Double-click an item in the dependency tree, or choose a variable passport.';if(messages)messages.innerHTML='';return;}
  const graph=state.lineage.sourceData.graph,edges=graph.edges||[],incoming=edges.filter(e=>e.to===node.id),outgoing=edges.filter(e=>e.from===node.id),meta=node.variable_metadata||node.artifact_metadata||node.gate_metadata||node.group_metadata||null;
  const refs=[node.variable_ref&&`variable_ref: ${node.variable_ref}`,node.type==="variable"&&`data_class: ${sourceFlowNodeDataClass(node)}`,node.artifact_ref&&`artifact_ref: ${node.artifact_ref}`,node.group_metadata?.id&&`group: ${node.group_metadata.id}`].filter(Boolean);
  host.innerHTML=`<div class="lineage-selection-title"><span>«${escapeHtml(sourceFlowNodeTypeLabel(node.type))}»</span><strong>${escapeHtml(node.label||node.id)}</strong></div><dl><dt>Identifier</dt><dd><code>${escapeHtml(node.id)}</code></dd><dt>Dependency rank</dt><dd>${escapeHtml(String((sourceFlowDependencyRanks(graph).findIndex(([,arr])=>arr.some(x=>x.id===node.id)))))}</dd>${refs.length?`<dt>References</dt><dd>${refs.map(x=>`<code>${escapeHtml(x)}</code>`).join("<br>")}</dd>`:""}<dt>Incoming</dt><dd>${incoming.length} relation(s)</dd><dt>Outgoing</dt><dd>${outgoing.length} relation(s)</dd></dl>${meta?`<details class="source-flow-metadata" open><summary>Canonical passport metadata</summary><pre>${escapeHtml(JSON.stringify(meta,null,2))}</pre></details>`:""}`;
  if(messages){const visible=(thread?.messages||[]).filter(m=>!m.hidden);messages.innerHTML=visible.map(m=>`<div class="lineage-assistant-message ${m.role}">${m.role==="assistant"?renderBasicMarkdown(m.content||""):escapeHtml(m.content||"").replace(/\n/g,"<br>")}</div>`).join("");messages.querySelectorAll(".lineage-assistant-message").forEach((el,i)=>{const msg=visible[i];if(msg)attachChatCopyButton(el,msg.content||"",msg.role==="user"?"right":"left");});if(threadBusy)messages.insertAdjacentHTML("beforeend",'<div class="lineage-assistant-message assistant busy">Thinking…</div>');messages.scrollTop=messages.scrollHeight;}
}
function renderSourceVariablePassports(){
  const host=document.querySelector("#source-flow-passport-groups");if(!host)return;const nodes=(activeSourceFlowGraph().nodes||[]).filter(n=>n.type==="variable"&&n.variable_metadata),groups=new Map();
  for(const n of nodes){const g=n.group_metadata||{id:"ungrouped",label:"Ungrouped variables"},id=String(g.id||"ungrouped");if(!groups.has(id))groups.set(id,{meta:g,nodes:[]});groups.get(id).nodes.push(n);}
  host.innerHTML="";for(const [id,item] of [...groups.entries()].sort((a,b)=>String(a[1].meta.label||a[0]).localeCompare(String(b[1].meta.label||b[0])))){const section=document.createElement("section");section.className="source-passport-group";section.innerHTML=`<header><strong>${escapeHtml(item.meta.label||id)}</strong><span>${item.nodes.length} variables</span>${item.meta.description?`<p>${escapeHtml(item.meta.description)}</p>`:""}</header><div class="source-passport-grid"></div>`;const grid=section.querySelector(".source-passport-grid");for(const n of item.nodes.sort((a,b)=>String(a.label||a.id).localeCompare(String(b.label||b.id)))){const m=n.variable_metadata||{},card=document.createElement("button");card.type="button";card.className="source-passport-card";card.dataset.sourceFlowId=n.id;card.innerHTML=`<strong>${escapeHtml(n.label||n.id)}</strong><span>${escapeHtml(m.type||m.data_type||"variable")} · ${escapeHtml(sourceFlowDataClassLabel(sourceFlowNodeDataClass(n)))}</span><small>${escapeHtml(m.description||m.meaning||n.variable_ref||n.id)}</small>`;card.addEventListener("click",()=>{state.lineage.sourceSelected=n.id;state.lineage.sourceFocusRoot=n.id;syncActiveLineageAssistantLegacyState();renderSourceFlowInspector();document.querySelectorAll('.source-passport-card.selected').forEach(x=>x.classList.remove('selected'));card.classList.add('selected');});grid.append(card);}host.append(section);}
  if(!groups.size)host.innerHTML='<div class="lineage-empty">No variable passports were included in this bundle.</div>';
}
function renderSourceDataFlow(){
  const data=state.lineage.sourceData,fullGraph=data?.graph||{},graph=activeSourceFlowGraph(),canvas=document.querySelector("#source-flow-canvas"),svg=document.querySelector("#source-flow-edges"),world=document.querySelector("#source-flow-world"),vp=document.querySelector("#source-flow-viewport"),empty=document.querySelector("#source-flow-empty"),pageSummary=document.querySelector("#lineage-summary"),title=document.querySelector("#source-flow-title"),subtitle=document.querySelector("#source-flow-subtitle");if(!canvas||!svg||!world||!vp)return;
  canvas.innerHTML="";svg.innerHTML="";updateSourceFlowDataClassFilter(fullGraph);const nodes=graph.nodes||[];
  if(title)title.textContent=graph.model_id||data?.bundle?.model_bundle_id||"Source Data Flow";if(subtitle)subtitle.textContent=[graph.revision||data?.bundle?.revision,data?.bundle?.path].filter(Boolean).join(" · ")||"Canonical authoring topology embedded in the playbook package.";
  if(pageSummary){const q=data?.summary||{},filtered=state.lineage.sourceDataClassFilter!=="all";pageSummary.innerHTML=`<span>${nodes.length}${filtered?` / ${q.nodes||0}`:""} objects</span><span>${(graph.edges||[]).length}${filtered?` / ${q.edges||0}`:""} relations</span><span>${(nodes.filter(n=>n.type==="gate")).length}${filtered?` / ${q.gates||0}`:""} gates</span>`;}
  if(empty){empty.hidden=nodes.length>0;empty.textContent=state.lineage.sourceError||"No canonical Data Layer / authoring data-flow projection was found in this playbook package.";}
  if(!nodes.length){state.lineage.sourceWorldWidth=Math.max(700,vp.clientWidth);state.lineage.sourceWorldHeight=420;updateSourceFlowTransform();renderSourceFlowInspector();return;}
  const auto=sourceFlowAdaptiveLayout(graph),existing=state.lineage.sourcePositions||{},next={};state.lineage.sourceWorldWidth=auto.worldWidth;state.lineage.sourceWorldHeight=auto.worldHeight;
  const trace=sourceFlowActiveTrace(graph),legendSelection=state.lineage.sourceLegend,traceDirection=state.lineage.sourceTraceDirection;updateSourceFlowLegend(graph,trace);
  for(const node of nodes){const base=auto.positions[node.id]||{x:50,y:50},pos=state.lineage.sourceLayoutMode==="free"&&existing[node.id]?existing[node.id]:base;next[node.id]={...pos};const el=document.createElement("button");el.type="button";const artifactView=sourceFlowArtifactPresentation(node),selected=state.lineage.sourceSelected===node.id,dimmed=trace&&!trace.visible.has(node.id),upstream=trace&&trace.upstream.has(node.id)&&!selected,downstream=trace&&trace.downstream.has(node.id)&&!selected,legendMatch=sourceFlowLegendMatchesNode(node,legendSelection),legendDim=legendSelection&&legendSelection.kind==="node"&&!legendMatch;el.className=`source-flow-node type-${String(node.type||"unknown").replace(/[^A-Za-z0-9_-]/g,"-")}${artifactView.className?` ${artifactView.className}`:""}${dimmed?" dimmed":""}${upstream?" source-flow-upstream":""}${downstream?" source-flow-downstream":""}${selected?" selected":""}${legendMatch?" legend-match":""}${legendDim?" legend-dim":""}`;el.dataset.sourceFlowId=node.id;el.style.left=`${pos.x}px`;el.style.top=`${pos.y}px`;const ref=node.variable_ref||node.artifact_ref||node.gate_metadata?.id||"";el.innerHTML=`<span class="source-flow-stereotype">${escapeHtml(sourceFlowNodeTypeLabel(node.type))}</span><span class="source-flow-type-icon" aria-hidden="true">${escapeHtml(sourceFlowNodeTypeIcon(node.type))}</span><strong>${escapeHtml(node.label||node.id)}</strong><span class="source-flow-node-id">${escapeHtml(node.id)}</span>${ref?`<span class="source-flow-ref">${escapeHtml(ref)}</span>`:""}${node.type==="variable"?`<span class="source-flow-data-class-tag">${escapeHtml(sourceFlowDataClassLabel(sourceFlowNodeDataClass(node)))}</span>`:""}${artifactView.badge?`<span class="source-flow-file-kind">${escapeHtml(artifactView.badge)}</span>`:""}`;
    el.addEventListener("click",ev=>{ev.stopPropagation();state.lineage.sourceSelected=node.id;if(state.lineage.sourceTraceDirection)state.lineage.sourceFocusRoot=node.id;syncActiveLineageAssistantLegacyState();renderSourceDataFlow();});
    el.addEventListener("dblclick",ev=>{ev.preventDefault();ev.stopPropagation();state.lineage.sourceSelected=node.id;state.lineage.sourceFocusRoot=node.id;syncActiveLineageAssistantLegacyState();renderSourceDataFlow();});
    el.addEventListener("pointerdown",ev=>{if(state.lineage.sourceLayoutMode!=="free"||ev.button!==0)return;ev.stopPropagation();const cur=next[node.id];state.lineage.sourceDrag={id:node.id,sx:ev.clientX,sy:ev.clientY,x:cur.x,y:cur.y,pid:ev.pointerId};el.setPointerCapture?.(ev.pointerId);el.classList.add("dragging");});
    el.addEventListener("pointermove",ev=>{const d=state.lineage.sourceDrag;if(!d||d.id!==node.id||d.pid!==ev.pointerId)return;const z=state.lineage.sourceZoom||1,nx=Math.max(10,d.x+(ev.clientX-d.sx)/z),ny=Math.max(10,d.y+(ev.clientY-d.sy)/z);next[node.id]={x:nx,y:ny};state.lineage.sourcePositions[node.id]={x:nx,y:ny};el.style.left=`${nx}px`;el.style.top=`${ny}px`;redrawSourceFlowEdges();});const end=()=>{if(state.lineage.sourceDrag?.id===node.id){state.lineage.sourceDrag=null;el.classList.remove("dragging");}};el.addEventListener("pointerup",end);el.addEventListener("pointercancel",end);canvas.append(el);}
  state.lineage.sourcePositions=next;const w=state.lineage.sourceWorldWidth,h=state.lineage.sourceWorldHeight;canvas.style.width=`${w}px`;canvas.style.height=`${h}px`;world.style.width=`${w}px`;world.style.height=`${h}px`;svg.setAttribute("width",String(w));svg.setAttribute("height",String(h));svg.setAttribute("viewBox",`0 0 ${w} ${h}`);updateSourceFlowTransform();setSourceFlowLayoutMode(state.lineage.sourceLayoutMode||"auto");setSourceFlowSubview(state.lineage.sourceSubview||"tree");document.querySelector("#source-flow-viewport")?.classList.toggle("focused-source-flow",Boolean(state.lineage.sourceFocusRoot));redrawSourceFlowEdges();renderSourceFlowInspector();
}
async function loadEmbeddedDataFlow(){
  if(!state.packageInfo?.id){state.lineage.sourceData=null;state.lineage.sourceError=null;return null;}
  if(state.lineage.sourceLoading)return state.lineage.sourceData;state.lineage.sourceLoading=true;
  try{const data=await request("/api/embedded-data-flow",{package_id:state.packageInfo.id});state.lineage.sourceData=data?.available?data:null;state.lineage.sourceError=data?.available?null:(data?.status==="invalid"?data.error:null);return data;}
  catch(error){state.lineage.sourceData=null;state.lineage.sourceError=error.message;return null;}finally{state.lineage.sourceLoading=false;}
}

function hideSourceFlowContextMenu(){const menu=document.querySelector("#source-flow-context-menu");if(menu)menu.hidden=true;}
function sourceFlowSvgPalette(type){
  const group=sourceFlowLegendNodeGroup(type);
  return ({variable:{stroke:"#7e92b8",fill:"#ffffff",accent:"#7e92b8"},transformation:{stroke:"#6d9b8e",fill:"#f7fbf9",accent:"#6d9b8e"},interaction:{stroke:"#9a8054",fill:"#fffdf8",accent:"#9a8054"},gate:{stroke:"#a66e16",fill:"#fff9e9",accent:"#a66e16"},artifact:{stroke:"#6f84a8",fill:"#fbfcff",accent:"#6f84a8"},contract:{stroke:"#2f6f5a",fill:"#f3fbf7",accent:"#2f6f5a"}})[group]||{stroke:"#738095",fill:"#ffffff",accent:"#738095"};
}
function downloadSourceFlowSvg(){
  const graph=activeSourceFlowGraph(),positions=state.lineage.sourcePositions||{};
  if(!(graph?.nodes||[]).length)return;
  const width=Math.max(700,state.lineage.sourceWorldWidth||0,...Object.values(positions).map(p=>(p?.x||0)+SOURCE_FLOW_CARD_W+40));
  const height=Math.max(500,state.lineage.sourceWorldHeight||0,...Object.values(positions).map(p=>(p?.y||0)+SOURCE_FLOW_CARD_H+40));
  const direction=state.lineage.sourceDirection||"TB",planned=sourceFlowPlanRoutes(graph,positions,direction);
  const trace=sourceFlowActiveTrace(graph),parts=[`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`,`<rect width="100%" height="100%" fill="#fbfcfe"/>`];
  for(const edge of graph.edges||[]){const a=positions[edge.from],b=positions[edge.to];if(!a||!b)continue;const key=`${edge.from}->${edge.to}:${edge.type||"relation"}`,path=planned.get(key)||sourceFlowOrthogonalPath(a,b,direction);let stroke="#8a98ad",dash="",sw=1.4;if(edge.type==="validation"){stroke="#667085";dash=' stroke-dasharray="5 4"';}if(trace){const up=trace.upstream.has(edge.from)&&trace.upstream.has(edge.to),down=trace.downstream.has(edge.from)&&trace.downstream.has(edge.to);if(up&&!down){stroke="#2d6fb7";sw=2.2;}else if(down&&!up){stroke="#258064";sw=2.2;dash=' stroke-dasharray="7 4"';}}parts.push(`<path d="${escapeXml(path)}" fill="none" stroke="${stroke}" stroke-width="${sw}"${dash}/>`);}
  for(const node of graph.nodes||[]){const pos=positions[node.id];if(!pos)continue;const pal=sourceFlowSvgPalette(node.type),label=String(node.label||node.id),type=sourceFlowNodeTypeLabel(node.type),ref=String(node.variable_ref||node.artifact_ref||node.gate_metadata?.id||"");parts.push(`<rect x="${pos.x}" y="${pos.y}" width="${SOURCE_FLOW_CARD_W}" height="${SOURCE_FLOW_CARD_H}" rx="8" fill="${pal.fill}" stroke="${pal.stroke}" stroke-width="2"/>`,`<rect x="${pos.x}" y="${pos.y}" width="${SOURCE_FLOW_CARD_W}" height="4" rx="3" fill="${pal.accent}"/>`,`<text x="${pos.x+10}" y="${pos.y+18}" font-family="Arial,sans-serif" font-size="9" font-weight="700" fill="#667085">${escapeXml(type)}</text>`);svgTextLines(label,28,2).forEach((line,i)=>parts.push(`<text x="${pos.x+10}" y="${pos.y+38+i*15}" font-family="Arial,sans-serif" font-size="12" font-weight="700" fill="#1f2937">${escapeXml(line)}</text>`));if(ref)parts.push(`<text x="${pos.x+10}" y="${pos.y+72}" font-family="Arial,sans-serif" font-size="8.5" fill="#7a8599">${escapeXml(ref.length>32?ref.slice(0,31)+'…':ref)}</text>`);}
  parts.push('</svg>');const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([parts.join('\n')],{type:'image/svg+xml;charset=utf-8'}));link.download='ordo-data-flow.svg';link.click();URL.revokeObjectURL(link.href);hideSourceFlowContextMenu();
}
function showSourceFlowContextMenu(event){
  if(!state.lineage.sourceData||state.lineage.sourceSubview==="passports")return;
  event.preventDefault();event.stopPropagation();hideCanvasContextMenu();
  const menu=document.querySelector("#source-flow-context-menu");if(!menu)return;
  document.querySelector("#source-flow-context-tb")?.classList.toggle("active",(state.lineage.sourceDirection||"TB")==="TB");
  document.querySelector("#source-flow-context-lr")?.classList.toggle("active",(state.lineage.sourceDirection||"TB")==="LR");
  menu.hidden=false;menu.style.left=`${event.clientX}px`;menu.style.top=`${event.clientY}px`;
  requestAnimationFrame(()=>{const rect=menu.getBoundingClientRect();if(rect.right>window.innerWidth-8)menu.style.left=`${Math.max(8,event.clientX-rect.width)}px`;if(rect.bottom>window.innerHeight-8)menu.style.top=`${Math.max(8,event.clientY-rect.height)}px`;});
}
function bindSourceDataFlow(){
  document.querySelector("#source-flow-data-class-filter")?.addEventListener("change",e=>{state.lineage.sourceDataClassFilter=String(e.target.value||"all");state.lineage.sourceSelected=null;state.lineage.sourceFocusRoot=null;state.lineage.sourcePositions={};clearSourceFlowLegendSelection();renderSourceDataFlow();});
  document.querySelectorAll('.source-flow-legend-item').forEach(btn=>btn.addEventListener('click',()=>{if(btn.disabled)return;setSourceFlowLegendSelection(btn.dataset.legendKind||'',btn.dataset.legendValue||'');}));
  document.querySelector("#source-flow-subview-tree")?.addEventListener("click",()=>setSourceFlowSubview("tree"));document.querySelector("#source-flow-subview-passports")?.addEventListener("click",()=>setSourceFlowSubview("passports"));document.querySelector("#source-flow-layout-auto")?.addEventListener("click",()=>{state.lineage.sourcePositions={};setSourceFlowLayoutMode("auto");renderSourceDataFlow();});document.querySelector("#source-flow-layout-free")?.addEventListener("click",()=>setSourceFlowLayoutMode("free"));document.querySelector("#source-flow-direction-tb")?.addEventListener("click",()=>setSourceFlowDirection("TB"));document.querySelector("#source-flow-direction-lr")?.addEventListener("click",()=>setSourceFlowDirection("LR"));document.querySelector("#source-flow-clear-focus")?.addEventListener("click",()=>{state.lineage.sourceSelected=null;state.lineage.sourceFocusRoot=null;clearSourceFlowLegendSelection();renderSourceDataFlow();});document.querySelector("#source-flow-zoom-out")?.addEventListener("click",()=>setSourceFlowZoom((state.lineage.sourceZoom||1)-.1));document.querySelector("#source-flow-zoom-in")?.addEventListener("click",()=>setSourceFlowZoom((state.lineage.sourceZoom||1)+.1));document.querySelector("#source-flow-zoom-reset")?.addEventListener("click",()=>setSourceFlowZoom(1));document.querySelector("#source-flow-zoom-fit")?.addEventListener("click",fitSourceFlowToViewport);const vp=document.querySelector("#source-flow-viewport");vp?.addEventListener("contextmenu",showSourceFlowContextMenu);document.querySelector("#source-flow-context-download-svg")?.addEventListener("click",downloadSourceFlowSvg);document.querySelector("#source-flow-context-fit")?.addEventListener("click",()=>{hideSourceFlowContextMenu();fitSourceFlowToViewport();});document.querySelector("#source-flow-context-auto")?.addEventListener("click",()=>{hideSourceFlowContextMenu();state.lineage.sourcePositions={};setSourceFlowLayoutMode("auto");renderSourceDataFlow();});document.querySelector("#source-flow-context-tb")?.addEventListener("click",()=>{hideSourceFlowContextMenu();setSourceFlowDirection("TB");});document.querySelector("#source-flow-context-lr")?.addEventListener("click",()=>{hideSourceFlowContextMenu();setSourceFlowDirection("LR");});vp?.addEventListener("pointerdown",e=>{if(e.button!==0||e.target.closest(".source-flow-node")||e.target.closest(".lineage-controls")||e.target.closest('.source-flow-legend-item'))return;hideSourceFlowContextMenu();state.lineage.sourcePan={x:e.clientX,y:e.clientY,left:vp.scrollLeft,top:vp.scrollTop,id:e.pointerId,moved:false};vp.setPointerCapture?.(e.pointerId);vp.classList.add("panning");});vp?.addEventListener("pointermove",e=>{const p=state.lineage.sourcePan;if(!p||p.id!==e.pointerId)return;const dx=e.clientX-p.x,dy=e.clientY-p.y;if(Math.abs(dx)>4||Math.abs(dy)>4)p.moved=true;vp.scrollLeft=p.left-dx;vp.scrollTop=p.top-dy;});const stop=e=>{const p=state.lineage.sourcePan;if(p&&p.id!==e.pointerId)return;state.lineage.sourcePan=null;vp?.classList.remove("panning");};vp?.addEventListener("pointerup",stop);vp?.addEventListener("pointercancel",()=>{state.lineage.sourcePan=null;vp?.classList.remove("panning");});
}

function lineageKindLabel(kind){ return ({analyst_input:"Analyst input",derived_state:"Derived state",transform_analyst:"Analyst interaction",transform_model:"AI transformation",transform_deterministic:"Deterministic derivation",transform_tool:"Python / tool",transform_template:"Template rendering",transform_package:"Packaging",document:"Document",artifact:"Artifact",archive:"Archive / package"})[kind] || kind || "Entity"; }
function lineageValueText(value){if(value===undefined)return"Not available in current runtime state";if(value===null)return"null";if(typeof value==="string")return value;try{return JSON.stringify(value,null,2);}catch{return String(value);}}
function lineageConnectedContext(entityId){
  const data=state.lineage.data||{},edges=(data.edges||[]).filter(e=>!e.hidden_projection),nodes=data.nodes||[],byId=new Map(nodes.map(n=>[n.id,n]));
  const incoming=edges.filter(e=>e.target===entityId),outgoing=edges.filter(e=>e.source===entityId);
  return {incoming:incoming.map(e=>({relation:e.relation,entity:byId.get(e.source)||{id:e.source}})),outgoing:outgoing.map(e=>({relation:e.relation,entity:byId.get(e.target)||{id:e.target}}))};
}
function lineageReachable(entityId,direction){return lineageMonotonicReachable(state.lineage.data||{},entityId,direction);}function updateLineageHighlight(){
  const viewport=document.querySelector("#lineage-viewport");if(!viewport)return;
  viewport.querySelectorAll(".lineage-node").forEach(el=>el.classList.toggle("selected",el.dataset.lineageId===state.lineage.selected));
}
function openLineageExecutionNode(nodeId){
  if(!nodeId || !(state.graph?.nodes||[]).some(n=>n.id===nodeId)) return;
  state.selected=nodeId;state.selectedNodes=new Set([nodeId]);showPanelTab("inspection");render();
  requestAnimationFrame(()=>{const el=canvas.querySelector(`.node[data-id="${CSS.escape(nodeId)}"]`);if(!el)return;const x=Math.max(0,el.offsetLeft-workspace.clientWidth/2+el.offsetWidth/2),y=Math.max(0,el.offsetTop-workspace.clientHeight/2+el.offsetHeight/2);workspace.scrollTo({left:x,top:y,behavior:"smooth"});});
}
function selectLineageEntity(entityId){
  if(state.lineage.selected!==entityId){state.lineage.selected=entityId;state.lineage.messages=[];state.lineage.busy=false;}
  updateLineageHighlight();renderLineageInspector();
}
function focusLineageEntity(entityId){
  state.lineage.focusRoot=entityId;
  state.lineage.selected=entityId;
  state.lineage.positions={};
  state.lineage.messages=[];state.lineage.busy=false;
  renderLineageGraph();
}
function lineageFocusedDistanceLayout(data,nodes,usable,cols,contentW,canvasEl){
  const slice=lineageFocusedSlice(data,state.lineage.focusRoot),groups=new Map(),auto={};
  for(const node of nodes){
    const d=slice.signedDistance.get(node.id);
    const distance=Number.isFinite(d)?d:0;
    if(!groups.has(distance)) groups.set(distance,[]);
    groups.get(distance).push(node);
  }
  const levels=[...groups.keys()].sort((a,b)=>a-b);
  let y=34;
  for(const distance of levels){
    const arr=groups.get(distance).slice().sort((a,b)=>String(a.label||a.id).localeCompare(String(b.label||b.id)));
    const heading=document.createElement("div");
    heading.className=`lineage-layer-heading focused-distance-layer ${distance===0?"focused-root-layer":distance<0?"focused-upstream-layer":"focused-downstream-layer"}`;
    heading.textContent=distance===0?"Selected node":distance<0?`Upstream · ${Math.abs(distance)} step${Math.abs(distance)===1?"":"s"}`:`Downstream · ${distance} step${distance===1?"":"s"}`;
    heading.style.left="34px";heading.style.top=`${y}px`;canvasEl.append(heading);y+=LINEAGE_LAYER_HEADING_H;
    const rows=Math.max(1,Math.ceil(arr.length/cols));
    arr.forEach((n,i)=>{
      const row=Math.floor(i/cols),col=i%cols,count=Math.min(cols,arr.length-row*cols),rowW=count*LINEAGE_CARD_W+Math.max(0,count-1)*LINEAGE_GAP_X,start=Math.max(34,(contentW-rowW)/2);
      auto[n.id]={x:start+col*(LINEAGE_CARD_W+LINEAGE_GAP_X),y:y+row*(LINEAGE_CARD_H+LINEAGE_GAP_Y)};
    });
    y+=rows*(LINEAGE_CARD_H+LINEAGE_GAP_Y)+LINEAGE_LAYER_GAP;
  }
  return {auto,y,slice};
}
function renderLineageGraph(){
  const data=state.lineage.data||{},canvasEl=document.querySelector("#lineage-canvas"),svg=document.querySelector("#lineage-edges"),world=document.querySelector("#lineage-world"),vp=document.querySelector("#lineage-viewport"),empty=document.querySelector("#lineage-empty"),summary=document.querySelector("#lineage-summary");
  if(!canvasEl||!svg||!world||!vp)return;
  const allNodes=data.nodes||[],visibleIds=lineageVisibleNodeIds(),nodes=allNodes.filter(n=>visibleIds.has(n.id));
  canvasEl.innerHTML="";svg.innerHTML="";
  if(summary){const q=data.summary||{},focused=Boolean(state.lineage.focusRoot),issues=lineageIssueNodes().length,filtered=state.lineage.filterMode==="issues";summary.innerHTML=`<span>${focused||filtered?`${nodes.length} / ${Number(q.entities||allNodes.length)}`:Number(q.entities||allNodes.length)} entities</span><span>${Number(q.relations||0)} relations</span><span>${Number(q.final_artifacts||0)} final artifacts</span><span class="${issues?"has-issues":""}">${issues} issues</span>`;}
  document.querySelector("#lineage-filter-all")?.classList.toggle("active",state.lineage.filterMode!=="issues");
  document.querySelector("#lineage-filter-issues")?.classList.toggle("active",state.lineage.filterMode==="issues");
  if(empty){empty.hidden=nodes.length>0;empty.textContent=state.lineage.filterMode==="issues"?"No Data Flow issues were detected in the discovered lineage.":"No data-lineage relationships were discovered in the loaded playbook.";}
  if(!nodes.length){state.lineage.worldWidth=Math.max(700,vp.clientWidth);state.lineage.worldHeight=420;updateLineageViewportTransform();renderLineageInspector();return;}

  const usable=Math.max(620,vp.clientWidth-84),cols=Math.max(2,Math.floor((usable+LINEAGE_GAP_X)/(LINEAGE_CARD_W+LINEAGE_GAP_X))),contentW=Math.max(usable,cols*LINEAGE_CARD_W+(cols-1)*LINEAGE_GAP_X),existing=state.lineage.positions||{};
  let auto={},y=34;
  if(state.lineage.focusRoot){
    const focusedLayout=lineageFocusedDistanceLayout(data,nodes,usable,cols,contentW,canvasEl);
    auto=focusedLayout.auto;y=focusedLayout.y;
  }else{
    for(let layerIndex=0;layerIndex<LINEAGE_SEMANTIC_LAYERS.length;layerIndex++){
      const layer=LINEAGE_SEMANTIC_LAYERS[layerIndex],arr=nodes.filter(n=>lineageSemanticLayer(n,data)===layerIndex).slice().sort((a,b)=>String(a.label||a.id).localeCompare(String(b.label||b.id)));
      if(!arr.length)continue;
      const heading=document.createElement("div");heading.className=`lineage-layer-heading layer-${layer.id}`;heading.textContent=layer.label;heading.style.left="34px";heading.style.top=`${y}px`;canvasEl.append(heading);y+=LINEAGE_LAYER_HEADING_H;
      const rows=Math.max(1,Math.ceil(arr.length/cols));
      arr.forEach((n,i)=>{const row=Math.floor(i/cols),col=i%cols,count=Math.min(cols,arr.length-row*cols),rowW=count*LINEAGE_CARD_W+Math.max(0,count-1)*LINEAGE_GAP_X,start=Math.max(34,(contentW-rowW)/2);auto[n.id]={x:start+col*(LINEAGE_CARD_W+LINEAGE_GAP_X),y:y+row*(LINEAGE_CARD_H+LINEAGE_GAP_Y)};});
      y+=rows*(LINEAGE_CARD_H+LINEAGE_GAP_Y)+LINEAGE_LAYER_GAP;
    }
  }
  state.lineage.worldWidth=contentW+68;state.lineage.worldHeight=Math.max(500,y+20);
  const nextPositions={};
  for(const n of nodes){
    const autoPosition=auto[n.id]||{x:34,y:34},useFree=state.lineage.layoutMode==="free"&&existing[n.id],p=useFree?existing[n.id]:autoPosition;
    nextPositions[n.id]={...p};
    const el=document.createElement("button");el.type="button";el.className=`lineage-node kind-${n.kind}`;el.dataset.lineageId=n.id;el.style.left=`${p.x}px`;el.style.top=`${p.y}px`;
    const sub=n.kind==="analyst_input"?"From analyst":n.kind==="derived_state"?`${n.source_kind||"internal"} state`:n.kind.startsWith("transform_")?`${n.execution_node_id||"producer"} · ${n.mechanism||"transformation"}`:n.artifact_path||"artifact";
    const diag=n.lineage_diagnostic?`<span class="lineage-node-diagnostic ${n.lineage_diagnostic.code==="POTENTIALLY_UNRESOLVED_USAGE"?"suspect":"unused"}" title="${escapeHtml(n.lineage_diagnostic.message||"")}">${escapeHtml(n.lineage_diagnostic.label||"Lineage note")}</span>`:"";
    el.innerHTML=`<span class="lineage-node-kind">${escapeHtml(lineageKindLabel(n.kind))}</span><strong>${escapeHtml(n.label||n.id)}</strong><span class="lineage-node-subtitle">${escapeHtml(sub)}</span>${diag}${n.final_artifact?'<span class="lineage-final-badge">Final</span>':''}`;
    el.addEventListener("click",ev=>{ev.stopPropagation();selectLineageEntity(n.id);});
    el.addEventListener("dblclick",ev=>{ev.preventDefault();ev.stopPropagation();focusLineageEntity(n.id);});
    el.addEventListener("pointerdown",ev=>{if(state.lineage.layoutMode!=="free"||ev.button!==0)return;ev.stopPropagation();const cur=nextPositions[n.id];state.lineage.drag={id:n.id,sx:ev.clientX,sy:ev.clientY,x:cur.x,y:cur.y,pid:ev.pointerId};el.setPointerCapture?.(ev.pointerId);el.classList.add("dragging");});
    el.addEventListener("pointermove",ev=>{const d=state.lineage.drag;if(!d||d.id!==n.id||d.pid!==ev.pointerId)return;ev.preventDefault();const z=state.lineage.zoom||1,nx=Math.max(8,d.x+(ev.clientX-d.sx)/z),ny=Math.max(8,d.y+(ev.clientY-d.sy)/z);nextPositions[n.id]={x:nx,y:ny};state.lineage.positions[n.id]={x:nx,y:ny};el.style.left=`${nx}px`;el.style.top=`${ny}px`;lineageRedrawEdges();});
    const stopDrag=()=>{if(state.lineage.drag?.id===n.id){state.lineage.drag=null;el.classList.remove("dragging");}};
    el.addEventListener("pointerup",stopDrag);el.addEventListener("pointercancel",stopDrag);canvasEl.append(el);
  }
  state.lineage.positions=nextPositions;
  const w=state.lineage.worldWidth,h=state.lineage.worldHeight;canvasEl.style.width=`${w}px`;canvasEl.style.height=`${h}px`;world.style.width=`${w}px`;world.style.height=`${h}px`;svg.setAttribute("width",String(w));svg.setAttribute("height",String(h));svg.setAttribute("viewBox",`0 0 ${w} ${h}`);
  updateLineageViewportTransform();setLineageLayoutMode(state.lineage.layoutMode||"auto");
  vp.classList.toggle("focused-lineage",Boolean(state.lineage.focusRoot));
  lineageRedrawEdges();updateLineageHighlight();renderLineageInspector();
  requestAnimationFrame(()=>{if(state.lineage.focusRoot)vp.scrollTo({left:0,top:0,behavior:"smooth"});});
}

async function renderDataLineage(){
  if(state.lineage.sourceLoading)return;
  await loadEmbeddedDataFlow();
  renderSourceDataFlow();
}
function renderLineageInspector(){
  renderSourceFlowInspector();
}
async function sendLineageAssistant(message,{hiddenUser=false}={}){
  const entity=activeLineageAssistantEntity(),ctx=activeLineageAssistantContext(entity),text=String(message||"").trim();if(!entity||!text||!modelExplanationAvailable())return false;
  const entityId=entity.id,thread=sourceFlowAssistantThread(entityId);if(thread.busy)return false;thread.messages.push({role:"user",content:text,hidden:hiddenUser});thread.busy=true;if(state.lineage.sourceSelected===entityId)renderLineageInspector();
  try{const data=await request("/api/data-lineage-assistant",{session_id:liveSessionId,package_id:state.packageInfo?.id||"",entity,context:{...ctx,view_mode:"source",diagnostic:entity.lineage_diagnostic||null,candidate_usage_resources:entity.candidate_usage_resources||[]},messages:thread.messages.map(m=>({role:m.role,content:m.content}))});const answer=String(data.answer_markdown||data.explanation||"").trim();if(!answer)throw new Error("The model returned an empty data-flow explanation.");thread.messages.push({role:"assistant",content:answer});return true;}catch(error){thread.messages.push({role:"assistant",content:`${lineageLocalFallback(entity)}\n\n> Model explanation unavailable: ${error.message}`});return false;}finally{thread.busy=false;if(state.lineage.sourceSelected===entityId){syncActiveLineageAssistantLegacyState();renderLineageInspector();}}
}

function bindLineageAssistant(){
  document.querySelector("#lineage-explain")?.addEventListener("click",()=>sendLineageAssistant("Explain this selected data-flow entity. Describe what it represents, how it is formed, its current value if available, all supported upstream inputs, downstream uses, and the execution nodes that produce or consume it. Do not confuse data lineage with execution order.",{hiddenUser:true}));
  document.querySelector("#lineage-clear-selection")?.addEventListener("click",()=>{state.lineage.sourceSelected=null;state.lineage.sourceFocusRoot=null;syncActiveLineageAssistantLegacyState();renderSourceDataFlow();});
  const form=document.querySelector("#lineage-assistant-form"),input=document.querySelector("#lineage-assistant-input");form?.addEventListener("submit",event=>{event.preventDefault();const value=input?.value||"";if(!String(value).trim())return;if(input)input.value="";sendLineageAssistant(value);});input?.addEventListener("keydown",event=>{if(event.key!=="Enter"||event.ctrlKey)return;event.preventDefault();if(!activeSourceFlowAssistantThread()?.busy&&String(input.value||"").trim())form?.requestSubmit();});
}

function renderHelpPage(id=activeHelpPageId) {
  const page=HELP_PAGES.find(item=>item.id===id) || HELP_PAGES[0];
  activeHelpPageId=page.id;
  const nav=document.querySelector("#help-nav"), target=document.querySelector("#help-page"), crumb=document.querySelector("#help-breadcrumb");
  if (!nav || !target) return;
  nav.innerHTML="";
  HELP_NAV_GROUPS.forEach((group,groupIndex)=>{
    if(groupIndex){const separator=document.createElement("div");separator.className="help-nav-separator";separator.setAttribute("aria-hidden","true");nav.append(separator);}
    group.forEach(itemId=>{
      const item=HELP_PAGES.find(candidate=>candidate.id===itemId);if(!item)return;
      const button=document.createElement("button"); button.type="button"; button.textContent=item.title; button.classList.toggle("active",item.id===page.id);
      button.addEventListener("click",()=>renderHelpPage(item.id)); nav.append(button);
    });
  });
  if (crumb) crumb.textContent=`Help / ${page.title}`;
  target.innerHTML=`<h1 class="help-page-title">${page.title}</h1><p class="help-page-lead">${page.lead}</p>` + page.sections.map(([title,body])=>`<section class="help-section"><h2>${title}</h2>${body}</section>`).join("");
  document.querySelector(".help-content")?.scrollTo({top:0,behavior:"instant"});
}


function modelChatAvailable(){return Boolean(state.liveConfig?.enabled&&state.liveConfig?.model);}
function modelChatFilePreviewable(file){return /\.(?:ya?ml|zip)$/i.test(String(file?.filename||""));}
function modelChatFileType(file){const n=String(file?.filename||"");if(/\.zip$/i.test(n))return"ZIP archive";if(/\.ya?ml$/i.test(n))return"YAML playbook";return artifactTypeLabel(n);}
function modelChatDownloadFile(file){if(file.download_url){const a=document.createElement("a");a.href=file.download_url;a.download=file.display_name||String(file.filename||"generated-file").split("/").pop();document.body.appendChild(a);a.click();a.remove();return;}let blob;if(file.content_base64){const raw=atob(file.content_base64),bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);blob=new Blob([bytes],{type:file.media_type||"application/octet-stream"});}else blob=new Blob([file.content_text||""],{type:file.media_type||"text/plain;charset=utf-8"});const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=file.display_name||String(file.filename||"generated-file").split("/").pop();a.click();setTimeout(()=>URL.revokeObjectURL(url),500);}
function renderModelChat(){const host=document.querySelector("#model-chat-transcript"),input=document.querySelector("#model-chat-input"),send=document.querySelector("#model-chat-send"),attachments=document.querySelector("#model-chat-attachments");if(!host)return;const rows=state.modelChat.messages.map((msg,mi)=>{const files=(msg.files||[]).map((f,fi)=>`<div class="model-chat-file-card ${modelChatFilePreviewable(f)?"previewable":""}" data-mi="${mi}" data-fi="${fi}"><div><strong>${escapeHtml(f.display_name||String(f.filename||"file").split("/").pop())}</strong><span>${escapeHtml(modelChatFileType(f))}${f.size_bytes?` · ${Number(f.size_bytes).toLocaleString()} bytes`:""}</span></div><button type="button" class="model-chat-file-download" aria-label="Download">↓</button></div>`).join("");const activities=(msg.activities||[]).map(a=>`<div class="model-chat-activity ${a.ok===false?"failed":""}"><span>${a.kind==="tool_call"?"···":"✓"}</span>${escapeHtml(a.label||"Workspace activity")}</div>`).join("");return msg.role==="user"?`<div class="model-chat-message user"><div>${escapeHtml(msg.content||"").replace(/\n/g,"<br>")}</div>${files}</div>`:`<div class="model-chat-message assistant">${activities}<div>${renderBasicMarkdown(msg.content||"")}</div>${files}</div>`;}).join("");host.innerHTML=rows||'<div class="model-chat-empty"><strong>Model Chat</strong><span>Free conversation with the configured model. This does not execute a playbook.</span></div>';host.querySelectorAll(".model-chat-message").forEach((el,i)=>{const msg=state.modelChat.messages[i];if(msg)attachChatCopyButton(el, msg.content || "", msg.role === "user" ? "right" : "left");});if(state.modelChat.busy){const live=state.modelChat.activityBuffer.map(a=>`<div class="model-chat-activity ${a.ok===false?"failed":""}"><span>${a.kind==="tool_call"?"···":"✓"}</span>${escapeHtml(a.label||"Workspace activity")}</div>`).join("");host.insertAdjacentHTML("beforeend",`<div class="model-chat-live-activity">${live}<div class="model-chat-thinking"><i></i><i></i><i></i></div></div>`);}host.querySelectorAll(".model-chat-file-card").forEach(card=>card.addEventListener("click",e=>{if(e.target.closest(".model-chat-file-download"))return;const f=state.modelChat.messages[Number(card.dataset.mi)]?.files?.[Number(card.dataset.fi)];if(f&&modelChatFilePreviewable(f))openModelChatPlaybookPreview(f);}));host.querySelectorAll(".model-chat-file-download").forEach(b=>b.addEventListener("click",e=>{e.stopPropagation();const card=b.closest(".model-chat-file-card"),f=state.modelChat.messages[Number(card.dataset.mi)]?.files?.[Number(card.dataset.fi)];if(f)modelChatDownloadFile(f);}));if(attachments)attachments.innerHTML=state.modelChat.attachments.map((a,i)=>`<span>${escapeHtml(a.filename)}<button type="button" data-remove="${i}">×</button></span>`).join("");attachments?.querySelectorAll("[data-remove]").forEach(b=>b.addEventListener("click",()=>{state.modelChat.attachments.splice(Number(b.dataset.remove),1);renderModelChat();}));if(input)input.disabled=state.modelChat.busy||!modelChatAvailable();if(send){send.disabled=!modelChatAvailable();send.dataset.mode=state.modelChat.busy?"stop":"send";send.innerHTML=state.modelChat.busy?'<span class="model-chat-stop-square"></span>':'↑';}requestAnimationFrame(()=>host.scrollTop=host.scrollHeight);renderModelChatPreview();}
function modelChatStructuredAnswer(value){
  if(!value||typeof value!=="object")return "";
  for(const key of ["answer_markdown","message","answer","content","text","response","output_text","final_response"]){
    const v=value[key];if(typeof v==="string"&&v.trim())return v.trim();
  }
  const nested=value.final;
  if(nested&&typeof nested==="object"){const found=modelChatStructuredAnswer(nested);if(found)return found;}
  for(const key of ["conversation","messages","history"]){
    const items=value[key];if(!Array.isArray(items))continue;
    for(let i=items.length-1;i>=0;i--){
      const item=items[i];if(!item||typeof item!=="object")continue;
      const role=String(item.role||"").toLowerCase();if(!["assistant","model","ai"].includes(role))continue;
      for(const k of ["content","text","message","answer","output_text"]){const v=item[k];if(typeof v==="string"&&v.trim())return v.trim();}
    }
  }
  return "";
}
function modelChatAnswerText(data){
  let answer=modelChatStructuredAnswer(data);
  if(!answer)return "";
  const trimmed=answer.trim();
  if(trimmed.startsWith("{")&&trimmed.endsWith("}")){
    try{const parsed=JSON.parse(trimmed),nested=modelChatStructuredAnswer(parsed);if(nested)return nested;}catch(_){}
  }
  return answer;
}
async function exportModelChat(debug=false){
  try{
    const data=await request("/api/model-chat-export",{
      debug:Boolean(debug),
      session_id:state.modelChat.sessionId,
      messages:state.modelChat.messages,
      attachments:state.modelChat.attachments,
      agent_trace:state.modelChat.agentTrace,
      usage_history:state.modelChat.usageHistory,
      errors:state.modelChat.errors,
      generated_files:state.modelChat.generatedFiles,
      provider_info:{
        enabled:Boolean(state.liveConfig?.enabled),
        provider:state.liveConfig?.provider||"",
        base_url:state.liveConfig?.base_url||"",
        model:state.liveConfig?.model||"",
        structured_output_mode:state.liveConfig?.structured_output_mode||"",
        semantic_fallback_policy:state.liveConfig?.semantic_fallback_policy||""
      }
    });
    let blob;
    if(data.content_base64){
      const raw=atob(data.content_base64),bytes=new Uint8Array(raw.length);
      for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
      blob=new Blob([bytes],{type:data.media_type||"application/octet-stream"});
    }else{
      blob=new Blob([String(data.content_text||"")],{type:data.media_type||"text/plain;charset=utf-8"});
    }
    const url=URL.createObjectURL(blob),a=document.createElement("a");
    a.href=url;a.download=data.filename||`model-chat-${debug?"debug.zip":"export.md"}`;
    document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }catch(error){
    state.modelChat.errors.push({timestamp:new Date().toISOString(),message:`Export failed: ${String(error?.message||error)}`});
    alert(`Model Chat export failed: ${error.message}`);
  }
}
async function waitForModelChatRun(runId){
  let seq=0;
  for(;;){
    if(!state.modelChat.busy||state.modelChat.activeRunId!==runId)throw new DOMException("Aborted","AbortError");
    const status=await request("/api/model-chat-status",{run_id:runId,after_seq:seq});
    const events=Array.isArray(status.activity_events)?status.activity_events:[];
    if(events.length){
      state.modelChat.activityBuffer.push(...events);
      seq=Number(status.last_seq||seq);
      state.modelChat.activitySeq=seq;
      renderModelChat();
    }
    if(status.finished)return status;
    await new Promise(r=>setTimeout(r,250));
  }
}
async function sendModelChat(){
  const input=document.querySelector("#model-chat-input"),text=String(input?.value||"").trim();
  if(state.modelChat.busy){
    const runId=state.modelChat.activeRunId;
    state.modelChat.busy=false;
    if(runId){try{await request("/api/model-chat-cancel",{run_id:runId});}catch(_){}}
    state.modelChat.activeRunId=null;
    renderModelChat();
    return;
  }
  if(!text&&!state.modelChat.attachments.length)return;
  if(!modelChatAvailable()){openLiveSettingsModal();return;}
  const attached=state.modelChat.attachments.map(x=>({...x}));
  state.modelChat.messages.push({role:"user",content:text,files:attached});
  state.modelChat.attachments=[];
  if(input)input.value="";
  state.modelChat.busy=true;
  state.modelChat.activityBuffer=[];
  state.modelChat.activitySeq=0;
  renderModelChat();
  try{
    const started=await request("/api/model-chat-start",{
      session_id:state.modelChat.sessionId,
      messages:state.modelChat.messages.map(m=>({role:m.role,content:m.content,files:m.files||[]})),
      attachments:attached
    });
    const runId=String(started.run_id||"");
    if(!runId)throw new Error("Model Chat did not return a run id.");
    state.modelChat.activeRunId=runId;
    const finished=await waitForModelChatRun(runId);
    if(finished.run_status==="cancelled")return;
    if(finished.run_status==="failed")throw new Error(finished.error||"Model Chat run failed.");
    const data=finished.result||{};
    if(Array.isArray(data.agent_trace))state.modelChat.agentTrace.push(...data.agent_trace.map(x=>({...x,chat_turn:state.modelChat.messages.length})));
    if(data.usage&&typeof data.usage==="object")state.modelChat.usageHistory.push({chat_turn:state.modelChat.messages.length,...data.usage});
    if(Array.isArray(data.files))state.modelChat.generatedFiles.push(...data.files.map(f=>({filename:f.filename||"",media_type:f.media_type||"",size_bytes:f.size_bytes||0,source:f.source||"model_chat"})));
    const answer=modelChatAnswerText(data);
    if(!answer)throw new Error("The Model Chat API returned no displayable answer.");
    state.modelChat.messages.push({
      role:"assistant",
      content:answer,
      files:Array.isArray(data.files)?data.files:[],
      activities:[...state.modelChat.activityBuffer]
    });
  }catch(error){
    if(error?.name!=="AbortError"){
      state.modelChat.errors.push({timestamp:new Date().toISOString(),message:String(error?.message||error)});
      state.modelChat.messages.push({role:"assistant",content:`**Model chat failed.** ${error.message}`,files:[],activities:[...state.modelChat.activityBuffer]});
    }
  }finally{
    state.modelChat.busy=false;
    state.modelChat.activeRunId=null;
    state.modelChat.activityBuffer=[];
    state.modelChat.activitySeq=0;
    renderModelChat();
    input?.focus();
  }
}

async function addModelChatAttachments(fileList){for(const file of Array.from(fileList||[]).slice(0,12)){const item={filename:file.name,media_type:file.type||"application/octet-stream",size_bytes:file.size};if(file.size<=2000000&&(/^text\//.test(file.type)||/\.(?:md|txt|json|ya?ml|py|js|ts|css|html?|xml|csv|sql|sh|toml|ini|cfg)$/i.test(file.name)))item.content_text=await file.text();else item.content_base64=bytesToBase64(new Uint8Array(await file.arrayBuffer()));state.modelChat.attachments.push(item);}renderModelChat();}
async function openModelChatPlaybookPreview(file){state.modelChat.preview={loading:true,file};renderModelChatPreview();try{const data=await request("/api/model-chat-playbook-preview",{filename:file.filename,content_text:file.content_text,content_base64:file.content_base64});state.modelChat.preview={loading:false,file,data};}catch(error){state.modelChat.preview={loading:false,file,error:error.message};}renderModelChatPreview();}
function renderModelChatPreview(){const host=document.querySelector("#model-chat-preview-body"),title=document.querySelector("#model-chat-preview-title");if(!host)return;const p=state.modelChat.preview;if(!p){host.innerHTML='<div class="model-chat-preview-empty">Select a generated Ordo YAML or ZIP file to preview its tree.</div>';if(title)title.textContent="Playbook Preview";return;}if(title)title.textContent=p.file?.filename||"Playbook Preview";if(p.loading){host.innerHTML='<div class="model-chat-preview-empty">Building tree preview…</div>';return;}if(p.error){host.innerHTML=`<div class="model-chat-preview-error">${escapeHtml(p.error)}</div>`;return;}const g=p.data?.graph||{nodes:[],edges:[]},nodes=(g.nodes||[]).filter(n=>n.element_type!=="output"),edges=(g.edges||[]).filter(e=>e.edge_type==="control_flow"),incoming=new Map(nodes.map(n=>[n.id,0]));edges.forEach(e=>incoming.set(e.target,(incoming.get(e.target)||0)+1));const roots=nodes.filter(n=>(incoming.get(n.id)||0)===0),depth=new Map(),q=roots.map(n=>[n.id,0]);while(q.length){const [id,d]=q.shift();if(depth.has(id)&&depth.get(id)<=d)continue;depth.set(id,d);edges.filter(e=>e.source===id).forEach(e=>q.push([e.target,d+1]));}nodes.forEach(n=>{if(!depth.has(n.id))depth.set(n.id,0)});const layers=new Map();nodes.forEach(n=>{const d=depth.get(n.id)||0,a=layers.get(d)||[];a.push(n);layers.set(d,a)});const W=520,R=100,NW=210,NH=60,pos=new Map();[...layers.entries()].sort((a,b)=>a[0]-b[0]).forEach(([d,list])=>list.forEach((n,i)=>pos.set(n.id,{x:Math.max(20,(W-NW)/2+(i-(list.length-1)/2)*230),y:24+d*R})));const H=Math.max(280,(Math.max(0,...depth.values())+1)*R+70),lines=edges.map(e=>{const a=pos.get(e.source),b=pos.get(e.target);return a&&b?`<path d="M ${a.x+NW/2} ${a.y+NH} C ${a.x+NW/2} ${a.y+NH+22}, ${b.x+NW/2} ${b.y-22}, ${b.x+NW/2} ${b.y}"/>`:"";}).join(""),cards=nodes.map(n=>{const x=pos.get(n.id);return `<div class="model-chat-preview-node ${n.element_type}" style="left:${x.x}px;top:${x.y}px;width:${NW}px;height:${NH}px"><strong>${escapeHtml(n.id)}</strong><span>${escapeHtml(n.label||n.answer_type||n.element_type)}</span></div>`;}).join("");host.innerHTML=`<div class="model-chat-preview-canvas" style="height:${H}px"><svg viewBox="0 0 ${W} ${H}">${lines}</svg>${cards}</div>`;}

function bindModelChat(){document.querySelector("#model-chat-export")?.addEventListener("click",()=>exportModelChat(false));document.querySelector("#model-chat-export-debug")?.addEventListener("click",()=>exportModelChat(true));document.querySelector("#model-chat-form")?.addEventListener("submit",e=>{e.preventDefault();sendModelChat();});document.querySelector("#model-chat-input")?.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey&&!e.ctrlKey){e.preventDefault();sendModelChat();}});document.querySelector("#model-chat-attach")?.addEventListener("click",()=>document.querySelector("#model-chat-file-input")?.click());document.querySelector("#model-chat-file-input")?.addEventListener("change",async e=>{await addModelChatAttachments(e.target.files);e.target.value="";});document.querySelector("#model-chat-preview-close")?.addEventListener("click",()=>{state.modelChat.preview=null;renderModelChatPreview();});}

function showPanelTab(tab) {
  const previousTab=state.panelTab;
  if(previousTab!==tab && editorMain.classList.contains("workspace-maximized")) setWorkspaceMaximized(false);
  const wasDialog=previousTab === "dialog";
  if (wasDialog && tab !== "dialog" && state.dialogPlaying) { clearDialogPlaybackTimer(); state.dialogPlaying=false; }
  state.panelTab=tab; hideNodeTooltip();
  if (["modelchat","help"].includes(tab)) { const tabs=document.querySelector("#workspace-tabs"); if(tabs) tabs.hidden=false; }
  document.querySelector("#inspection-panel").hidden=tab !== "inspection";
  document.querySelector("#validate-panel").hidden=true;
  document.querySelector("#dialog-panel").hidden=tab !== "dialog";
  document.querySelector("#replay-panel").hidden=tab !== "replay";
  document.querySelector("#run-panel").hidden=tab !== "run";
  document.querySelector("#upload-home-panel").hidden=tab !== "upload";
  document.querySelector("#model-chat-main-panel").hidden=tab !== "modelchat";
  document.querySelector("#model-chat-preview-panel").hidden=tab !== "modelchat";
  document.querySelector("#lineage-main-panel").hidden=tab !== "lineage";
  document.querySelector("#lineage-assistant-panel").hidden=tab !== "lineage";
  document.querySelector("#playbook-settings-main-panel").hidden=tab !== "settings";
  document.querySelector("#playbook-settings-assistant-panel").hidden=tab !== "settings" && !(tab === "packagefiles" && packageFilesAssistantOpen);
  document.querySelector("#package-files-main-panel").hidden=tab !== "packagefiles";
  document.querySelector("#verification-main-panel").hidden=tab !== "verification";
  document.querySelector("#verification-assistant-panel").hidden=tab !== "verification";
  document.querySelector("#help-panel").hidden=tab !== "help";
  const mode={upload:"upload",inspection:"tree",dialog:"paths",replay:"replay",run:"chat",modelchat:"modelchat",lineage:"lineage",settings:"settings",packagefiles:"packagefiles",verification:"verification",help:"help"}[tab] || "upload";
  editorMain.dataset.workspaceMode=mode; editorMain.classList.remove("side-collapsed"); if(tab!=="packagefiles")editorMain.classList.remove("package-files-chat-open"); else editorMain.classList.toggle("package-files-chat-open",packageFilesAssistantOpen); updateWorkspaceMaximizeButton();
  document.querySelectorAll("[data-workspace-tab]").forEach(button=>button.classList.toggle("active",button.dataset.workspaceTab===mode));
  if (["dialog","replay","run"].includes(previousTab) || ["dialog","replay","run"].includes(tab)) render();
  if (tab === "dialog") { populatePathBuilder(); renderDialog(); }
  if (tab === "replay") renderReplay();
  if (tab === "run") renderLiveRun();
  if (tab === "modelchat") renderModelChat();
  if (tab === "lineage") renderDataLineage();
  if (tab === "settings") { renderPlaybookSettingsSubtab(); renderPlaybookSettings(); }
  if (tab === "packagefiles") renderPackageFiles();
  if (tab === "verification") renderVerificationPage();
  if (tab === "help") renderHelpPage();
}

async function deleteDirectTransition(edge) { const source = sourceRecord(edge.source); if (!source) return alert("The selected transition is no longer available."); if (!confirm(`Delete transition ${edge.source} → ${edge.target}?`)) return; if (edge.storage === "transitions") delete source.transitions?.[edge.key]; else if (edge.storage === "transitions_list") { const list = Array.isArray(source.transitions) ? source.transitions : []; source.transitions = list.filter((item, index) => String(item?.id || item?.when || item?.outcome || `transition_${index + 1}`) !== edge.key); } else if (edge.storage === "navigation_allowed_to") { const contract = source.navigation_contract; if (contract && Array.isArray(contract.allowed_to)) contract.allowed_to = contract.allowed_to.filter(target => target !== edge.target); } else if (edge.storage === "on_answer") delete source.on_answer?.[edge.key]; else if (edge.storage === "on_answer_next") delete source.on_answer?.next; else if (edge.storage === "next") delete source.next; else if (edge.storage === "gate_route") delete source[edge.key]; else return alert("This transition cannot be removed here."); state.selectedEdge = null; hideEdgeMenu(); await refresh(state.source); }
function renderTransitionManager(record) { const manager = document.querySelector("#node-transition-manager"), list = document.querySelector("#outgoing-transition-list"); manager.hidden = !record; if (!record) return; list.innerHTML = ""; const outgoing = (state.graph.edges || []).filter(edge => edge.source === record.id); if (!outgoing.length) list.textContent = "No transitions declared for this element."; outgoing.forEach(edge => { const row = document.createElement("div"); row.className = "transition-row"; const text = document.createElement("span"); text.textContent = `${edge.key} → ${edge.target}`; const remove = document.createElement("button"); remove.type = "button"; remove.className = "danger"; remove.textContent = "Delete"; remove.addEventListener("click", () => deleteDirectTransition(edge)); row.append(text, remove); list.append(row); }); }
function templateCapableRecord(record) {
  if (!record || typeof record !== "object") return false;
  const pathPattern=/(?:^|[^A-Za-z0-9_.-])([A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)+\.(?:py|md|markdown|json|ya?ml|txt|html?|css|js|mjs|cjs|ts|tsx|jsx|xml|csv|sql|sh|toml|ini|cfg))(?:$|[^A-Za-z0-9_.-])/i;
  const walk=value=>{
    if(Array.isArray(value)) return value.some(walk);
    if(value && typeof value === "object") return Object.values(value).some(walk);
    return typeof value === "string" && !value.includes("://") && pathPattern.test(value);
  };
  return walk(record);
}
function yamlLike(value) { try { return JSON.stringify(value,null,2); } catch { return String(value ?? ""); } }
function modelExplanationAvailable() { return Boolean(state.liveConfig?.enabled && state.liveConfig?.model); }
function explanationLanguageLabel() { return state.interactionContract?.model_output_language || state.interactionContract?.locale || "playbook language"; }
function explanationKeyForSelected() { return String(state.selected || ""); }
async function requestModelExplanation(kind, payload) {
  return request("/api/explain", {
    session_id: liveSessionId,
    package_id: state.packageInfo?.id || "",
    kind,
    ...payload,
  });
}
function renderNodeExplanationTab() {
  const content=document.querySelector("#node-explanation-content"); if(!content) return;
  const key=explanationKeyForSelected();
  if(!key){ content.innerHTML='<div class="template-empty">Select a node to request an explanation.</div>'; return; }
  const cached=state.nodeExplanations[key];
  const available=modelExplanationAvailable();
  const busy=state.explanationBusy===`node:${key}`;
  content.innerHTML=`<div class="model-explanation-toolbar"><div><strong>Behavior explanation</strong><div class="hint">Generated on demand in ${escapeHtml(explanationLanguageLabel())}. It does not execute or modify the playbook.</div></div><button id="node-explain-with-model" type="button" ${(!available||busy||cached)?"disabled":""}>${busy?"Explaining…":cached?"Explained":"Explain with model"}</button></div>${available?"":'<div class="model-explanation-unavailable">Configure an LLM model to generate an explanation.</div>'}<div class="model-explanation-result">${cached?`<div class="model-explanation-meta">Model explanation</div><div class="model-explanation-text model-explanation-markdown">${renderBasicMarkdown(cached.explanation||"")}</div>`:'<div class="model-explanation-placeholder">No explanation generated yet.</div>'}</div>`;
  content.querySelector("#node-explain-with-model")?.addEventListener("click",async()=>{
    if(!modelExplanationAvailable()||busy) return;
    state.explanationBusy=`node:${key}`; renderNodeExplanationTab();
    try { const data=await requestModelExplanation("node",{node_id:key}); state.nodeExplanations[key]={explanation:data.explanation||"",model:data.model||""}; }
    catch(error){ state.nodeExplanations[key]={explanation:`Explanation could not be generated: ${error.message}`,error:true}; }
    finally { state.explanationBusy=null; renderNodeExplanationTab(); }
  });
}
function resourceExplanationKey(ref) { return String(ref?.resolved_path||ref?.path||""); }
function resourceExplainable(ref) { return Boolean(ref?.available && /\.py$/i.test(String(ref?.resolved_path||ref?.path||""))); }
async function explainResourceWithModel(ref) {
  const key=resourceExplanationKey(ref); if(!key||!resourceExplainable(ref)||!modelExplanationAvailable()) return;
  state.explanationBusy=`resource:${key}`; renderTemplateInspectorTab();
  try { const data=await requestModelExplanation("python_resource",{resource_path:key}); state.resourceExplanations[key]={explanation:data.explanation||"",model:data.model||""}; }
  catch(error){ state.resourceExplanations[key]={explanation:`Explanation could not be generated: ${error.message}`,error:true}; }
  finally { state.explanationBusy=null; renderTemplateInspectorTab(); }
}

function renderTemplateInspectorTab() {
  const data=state.templateInspectorData, content=document.querySelector("#template-inspector-content"); if (!content) return;
  if (!data) { content.innerHTML='<div class="template-empty">No package references declared for this element.</div>'; return; }
  const esc=escapeHtml, refs=(data.references||[]);
  const cards=refs.map((r,i)=>{ const rkey=resourceExplanationKey(r), rex=state.resourceExplanations[rkey], explainable=resourceExplainable(r), busy=state.explanationBusy===`resource:${rkey}`; return `<section class="template-reference-card ${r.available?"is-clickable":""}" ${r.available?`data-resource-preview-index="${i}" role="button" tabindex="0" aria-label="Preview ${esc(r.resolved_path||r.path)}"`:""}><div><strong>${esc(r.role)}</strong><span class="template-ref-status ${r.available?"ok":"missing"}">${r.available?"Resolved":"Missing"}</span></div><code>${esc(r.path)}</code>${r.resolved_path&&r.resolved_path!==r.path?`<div class="hint">Resolved as ${esc(r.resolved_path)}</div>`:""}${r.available?`<div class="template-reference-actions"><span class="template-reference-action">Preview file <span aria-hidden="true">›</span></span>${explainable?`<button type="button" class="template-resource-explain" data-resource-explain-index="${i}" ${(!modelExplanationAvailable()||busy||rex)?"disabled":""} title="${rex?"Explanation already generated":modelExplanationAvailable()?"Explain what this Python script checks":"Configure an LLM model first"}">${busy?"Explaining…":rex?"Explained":"Explain with model"}</button>`:""}</div>`:""}${rex?`<div class="resource-model-explanation"><strong>Model explanation</strong><div class="resource-model-explanation-markdown">${renderBasicMarkdown(rex.explanation||"")}</div></div>`:""}</section>`; }).join("");
  const preview=state.templateResourcePreview;
  const previewPath=String(preview?.resolved_path||preview?.path||"");
  const previewIsMarkdown=/\.(md|markdown)$/i.test(previewPath);
  const previewMode=previewIsMarkdown ? (state.templateResourcePreviewMode||"rendered") : "source";
  content.innerHTML=(cards || `<div class="template-empty">No package references declared for this element.</div>`) + `<section id="template-resource-inline-preview" class="template-resource-inline-preview" ${preview?"":"hidden"}><div class="template-resource-preview-header"><div><strong>Resource Preview</strong><span id="template-resource-preview-path"></span></div><button type="button" class="template-resource-preview-close" aria-label="Close resource preview">×</button></div>${previewIsMarkdown?`<div class="template-resource-preview-tabs" role="tablist"><button type="button" data-resource-preview-mode="rendered" class="${previewMode==="rendered"?"active":""}">Preview</button><button type="button" data-resource-preview-mode="source" class="${previewMode==="source"?"active":""}">Source</button></div>`:""}<div class="template-resource-preview-rendered" ${previewMode==="rendered"?"":"hidden"}></div><pre class="template-resource-preview-body" ${previewMode==="source"?"":"hidden"}></pre></section>`;
  if(preview){ const pathEl=content.querySelector("#template-resource-preview-path"), body=content.querySelector(".template-resource-preview-body"), rendered=content.querySelector(".template-resource-preview-rendered"); if(pathEl) pathEl.textContent=previewPath; if(body) body.textContent=preview.text||""; if(rendered && previewIsMarkdown) rendered.innerHTML=renderBasicMarkdown(preview.text||""); }
  content.querySelectorAll("[data-resource-preview-mode]").forEach(button=>button.addEventListener("click",()=>{ state.templateResourcePreviewMode=button.dataset.resourcePreviewMode; renderTemplateInspectorTab(); }));
  content.querySelectorAll("[data-resource-preview-index]").forEach(card=>{ const open=()=>{ const ref=refs[Number(card.dataset.resourcePreviewIndex)]; if(!ref?.available) return; state.templateResourcePreview=ref; state.templateResourcePreviewMode=/\.(md|markdown)$/i.test(String(ref.resolved_path||ref.path||""))?"rendered":"source"; renderTemplateInspectorTab(); requestAnimationFrame(()=>content.querySelector("#template-resource-inline-preview")?.scrollIntoView({block:"nearest",behavior:"smooth"})); }; card.addEventListener("click",event=>{ if(event.target.closest("button")) return; open(); }); card.addEventListener("keydown",event=>{ if((event.key==="Enter"||event.key===" ")&&!event.target.closest("button")){ event.preventDefault(); open(); } }); });
  content.querySelectorAll("[data-resource-explain-index]").forEach(button=>button.addEventListener("click",event=>{ event.stopPropagation(); const ref=refs[Number(button.dataset.resourceExplainIndex)]; explainResourceWithModel(ref); }));
  content.querySelector(".template-resource-preview-close")?.addEventListener("click",()=>{ state.templateResourcePreview=null; renderTemplateInspectorTab(); });
}
function renderDerivedOutputParameters(data) {
  const container=document.querySelector("#node-sections"); if(!container) return;
  const esc=escapeHtml;
  const producers=(data.producers||[]).map(p=>`<li><code>${esc(p.id)}</code>${p.action?` · ${esc(p.action)}`:""}${p.purpose?`<div class="hint">${esc(p.purpose)}</div>`:""}</li>`).join("");
  container.innerHTML=`<dl class="template-overview"><dt>Element</dt><dd><code>${esc(data.node_id)}</code></dd><dt>Type</dt><dd>output</dd><dt>Output</dt><dd><code>${esc(data.output||"Not declared")}</code></dd></dl><h3>Producer nodes</h3><ul class="template-reference-list">${producers||"<li>No producer nodes resolved.</li>"}</ul>`;
  document.querySelector("#node-transition-manager").hidden=true;
  document.querySelector("#node-fields-view .hint")?.setAttribute("hidden","");
  document.querySelector("#node-form button[type=submit]").hidden=true;
  document.querySelector("#delete-node").hidden=true;
}
async function loadTemplateInspector(record, view) {
  const selectedId=view?.id; const outputNode=["output","declared_output"].includes(view?.entity_type); if(!selectedId || !state.packageInfo?.id || (!outputNode && !templateCapableRecord(record))) return;
  const content=document.querySelector("#template-inspector-content"); if(content) content.innerHTML='<div class="template-empty">Loading package references…</div>';
  try {
    const data=await request("/api/template-inspector",{package_id:state.packageInfo.id,node_id:selectedId,source:state.source}); if(state.selected!==selectedId) return;
    state.templateInspectorData=data;
    const refTab=document.querySelector('[data-inspector-tab="references"]'); if(refTab) refTab.hidden=false;
    if(outputNode) { renderDerivedOutputParameters(data); updateYamlPreview(); }
    showInspectorTab(state.inspectorTab);
  }
  catch(error){ if(state.selected!==selectedId) return; if(content) content.innerHTML=`<div class="template-empty">${escapeHtml(error.message)}</div>`; }
}

function renderInspector() {
  const transitionPanel=document.querySelector("#transition-inspector"); if (transitionPanel) transitionPanel.hidden=true;
  state.selectedEdge=null; state.templateInspectorData=null; state.templateResourcePreview=null;
  const record=selectedRecord(), view=selectedView();
  const refTab=document.querySelector('[data-inspector-tab="references"]'); if(refTab) refTab.hidden=true;
  document.querySelector("#selection-help").hidden=Boolean(view);
  const outputInspectable=Boolean(["output","declared_output"].includes(view?.entity_type) && state.packageInfo?.id);
  const inspectable=Boolean(record && view?.collection);
  const form=document.querySelector("#node-form"); form.hidden=!(inspectable || outputInspectable);
  const manager=document.querySelector("#node-transition-manager"); if (manager) manager.hidden=true;
  const apply=document.querySelector("#node-form button[type=submit]"), del=document.querySelector("#delete-node");
  if(apply) apply.hidden=false; if(del) del.hidden=false;
  const fieldsHint=document.querySelector("#node-fields-view > .hint"); if(fieldsHint) fieldsHint.hidden=false;
  if (outputInspectable) {
    document.querySelector("#selection-help").hidden=true;
    document.querySelector("#node-summary").textContent=`${view.id} · output · ${view.path || view.label || "artifact"}`;
    document.querySelector("#node-sections").innerHTML='<div class="template-empty">Loading output information…</div>';
    state.inspectorTab = ["fields","yaml","references","explanation"].includes(state.inspectorTab) ? state.inspectorTab : "fields";
    showInspectorTab(state.inspectorTab);
    loadTemplateInspector(null,view);
    return;
  }
  if (view && !inspectable) document.querySelector("#selection-help").textContent = view.element_type === "output" ? `Declared output ${view.id}. ${view.producers?.length ? `Producer: ${view.producers.join(", ")}.` : "Producer is unresolved; no execution transition was inferred."}` : `${view.id} is an external terminal. It is shown for routing only.`;
  if (!inspectable) return;
  document.querySelector("#node-summary").textContent=`${record.id} · ${view.element_type} · ${view.answer_type || record.kind || "unspecified"}`;
  const container=document.querySelector("#node-sections"); container.innerHTML="";
  const sections=view.sections || []; const knownSectionOrder=["title", "id", "kind", "purpose", "question", "inputs", "outputs", "questions", "user_interaction", "entry_gate", "exit_gate", "on_gap", "transitions", "on_answer", "route_context", "artifact_contract", "expected_artifacts", "order", "terminal", "method", "trust_class", "condition", "on_pass", "on_fail", "severity"]; const knownSectionRank=new Map(knownSectionOrder.map((key,index)=>[key,index])); const ordered=[...sections].sort((a,b)=>{ const ar=knownSectionRank.has(a.key)?knownSectionRank.get(a.key):Number.MAX_SAFE_INTEGER; const br=knownSectionRank.has(b.key)?knownSectionRank.get(b.key):Number.MAX_SAFE_INTEGER; return ar-br; });
  ordered.forEach(section=>{ const labels=sectionLabels[section.key] || ["Additional field",section.key]; const wrapper=document.createElement("div"); wrapper.className="node-section"; const label=document.createElement("label"); label.textContent=`${labels[0]} (${labels[1]})`; const field=document.createElement("textarea"); field.dataset.sectionKey=section.key; field.dataset.originalValue=section.value_yaml; field.rows=Math.max(2,Math.min(12,section.value_yaml.split("\n").length+1)); field.value=section.value_yaml; field.spellcheck=false; field.readOnly=true; label.append(field); wrapper.append(label); container.append(wrapper); });
  updateYamlPreview();
  state.inspectorTab = ["fields","yaml","references","explanation"].includes(state.inspectorTab) ? state.inspectorTab : "fields";
  showInspectorTab(state.inspectorTab);
  if(templateCapableRecord(record) && state.packageInfo?.id) loadTemplateInspector(record,view);
}

function rerenderKeepingInspectorDraft() { const draft = Object.fromEntries([...document.querySelectorAll("[data-section-key]")].map(field => [field.dataset.sectionKey, field.value])); render(); document.querySelectorAll("[data-section-key]").forEach(field => { if (draft[field.dataset.sectionKey] !== undefined) field.value = draft[field.dataset.sectionKey]; }); updateYamlPreview(); }
function refresh(source) { state.source = source; state.selected = null; state.selectedNodes = new Set(); clearDialogPlaybackTimer(); state.dialogPath = null; state.dialogFocusId = null; state.dialogPlayMode = false; state.dialogPlaying = false; state.dialogVisibleCount = null; return request("/api/parse", { source }).then(data => { state.source = data.source; state.graph = data.graph; render(); }); }
function displayValidation(validation) {
  const container = document.querySelector("#validation");
  container.innerHTML = "";
  const summary = validation.summary || {};
  const header = document.createElement("div");
  header.className = `validation-overall ${validation.status || ""}`;
  const statusLabel = validation.status === "passed" ? "PASSED" : validation.status === "warning" ? "PASSED WITH WARNINGS" : "FAILED";
  header.innerHTML = `<strong>${statusLabel}</strong><span>${summary.checks || 0} checks · ${summary.errors || 0} errors · ${summary.warnings || 0} warnings · ${summary.info || 0} info</span>`;
  container.append(header);

  (validation.checks || []).forEach(check => {
    const block = document.createElement("section");
    block.className = `validation-check ${check.status || ""}`;
    const title = document.createElement("div");
    title.className = "validation-check-title";
    const badge = check.status === "passed" ? "PASS" : check.status === "warning" ? "WARN" : "ERROR";
    title.innerHTML = `<span class="validation-badge">${badge}</span><strong>${check.name}</strong>`;
    block.append(title);

    const summaryLine = document.createElement("p");
    summaryLine.className = "validation-check-summary";
    summaryLine.textContent = check.summary || "";
    block.append(summaryLine);

    (check.findings || []).forEach(finding => {
      const findingEl = document.createElement("div");
      findingEl.className = `validation-finding ${finding.severity || ""}`;
      const prefix = document.createElement("span");
      prefix.textContent = `${(finding.severity || "info").toUpperCase()} · ${finding.code} — `;
      findingEl.append(prefix);
      if (finding.element && (state.graph?.nodes || []).some(item => item.id === finding.element)) {
        const link = document.createElement("button");
        link.type = "button";
        link.className = "validation-element-link";
        link.textContent = finding.element;
        link.title = `Center graph on ${finding.element}`;
        link.addEventListener("click", () => focusGraphElement(finding.element));
        findingEl.append(link);
        const message = String(finding.message || "");
        const withoutLeadingId = message.startsWith(finding.element) ? message.slice(finding.element.length).trimStart() : message;
        if (withoutLeadingId) findingEl.append(document.createTextNode(` ${withoutLeadingId}`));
      } else {
        findingEl.append(document.createTextNode(String(finding.message || "")));
      }
      block.append(findingEl);
    });
    container.append(block);
  });

  if (validation.note) {
    const note = document.createElement("p");
    note.className = "hint validation-note";
    note.textContent = validation.note;
    container.append(note);
  }
}
document.querySelector("#file-input")?.addEventListener("change", async event => { const file = event.target.files[0]; if (!file) return; try { const data = await request("/api/parse", { yaml: await file.text() }); state.packageInfo = null; state.lineage.sourceData=null;state.lineage.sourceError=null;state.lineage.sourceDataClassFilter="all";state.lineage.sourceLegend=null;state.lineage.sourceTraceDirection=null;state.lineage.viewMode="source"; state.source = data.source; state.graph = data.graph; state.positions = {}; state.manualPositions = new Set(); state.collapsedNodes = new Set(); state.pendingTransitionSource = null; clearDialogPlaybackTimer(); state.dialogPath = null; state.dialogPlayMode = false; state.dialogPlaying = false; state.dialogVisibleCount = null; resetLiveRun(); render(); renderLiveRun(); } catch (error) { alert(error.message); } finally { event.target.value = ""; } });
document.querySelector("#validate").addEventListener("click", async () => { if (!state.source) return; try { const data = await request("/api/validate", { source: state.source }); displayValidation(data.validation); } catch (error) { alert(error.message); } });

async function downloadFullPlaybook() {
  if (!state.packageInfo?.id || !state.source) { alert("Load a playbook source first."); return; }
  try {
    const data = await request("/api/export-playbook", { package_id: state.packageInfo.id, source: state.source });
    const binary = atob(data.data_base64 || "");
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([bytes], { type: "application/zip" }));
    link.download = data.filename || state.packageInfo.filename || "playbook.zip";
    link.click();
    URL.revokeObjectURL(link.href);
  } catch (error) {
    alert(`Could not download full playbook: ${error.message}`);
  } finally { hideCanvasContextMenu(); }
}

async function downloadYaml() { if (!state.source) return; const data = await request("/api/export", { source: state.source }); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([data.yaml], { type: "application/x-yaml" })); link.download = "program.edited.ordo.yaml"; link.click(); URL.revokeObjectURL(link.href); hideCanvasContextMenu(); }
function escapeXml(value) { return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&apos;"}[ch])); }
function svgTextLines(value, maxChars = 30, maxLines = 4) {
  const words = String(value || "").replace(/\s+/g, " ").trim().split(" ").filter(Boolean);
  const lines = []; let line = "";
  for (const word of words) {
    const candidate = line ? `${line} ${word}` : word;
    if (candidate.length <= maxChars) line = candidate;
    else { if (line) lines.push(line); line = word; if (lines.length >= maxLines - 1) break; }
  }
  if (line && lines.length < maxLines) lines.push(line);
  if (words.join(" ").length > lines.join(" ").length && lines.length) lines[lines.length - 1] = `${lines[lines.length - 1].slice(0, Math.max(1, maxChars - 1))}…`;
  return lines;
}
function svgIdentifierLines(value, maxChars = 27, maxLines = 3) {
  const raw = String(value || "").trim();
  if (!raw) return [];
  // Keep underscores visible, but make them natural SVG wrapping points.
  const tokens = raw.match(/[^_]+_?/g) || [raw];
  const chunks = [];
  for (const token of tokens) {
    if (token.length <= maxChars) { chunks.push(token); continue; }
    for (let i = 0; i < token.length; i += maxChars) chunks.push(token.slice(i, i + maxChars));
  }
  const lines = []; let line = "";
  for (const chunk of chunks) {
    const candidate = line + chunk;
    if (!line || candidate.length <= maxChars) line = candidate;
    else { lines.push(line); line = chunk; if (lines.length >= maxLines - 1) break; }
  }
  if (line && lines.length < maxLines) lines.push(line);
  const represented = lines.join("");
  if (represented.length < raw.length && lines.length) {
    lines[lines.length - 1] = `${lines[lines.length - 1].slice(0, Math.max(1, maxChars - 1))}…`;
  }
  return lines;
}
function downloadTreeSvg() {
  if (!state.source || !state.graph) return;
  const entries = Object.entries(state.positions || {});
  const width = Math.max(1050, ...entries.map(([id, pos]) => pos.x + nodeSize(id).width + CANVAS_MARGIN));
  const height = Math.max(700, ...entries.map(([id, pos]) => pos.y + nodeHeight(id) + CANVAS_MARGIN));
  const replayEdges = new Set(replayPathEdges().map(edge => `${edge.source}\u0000${edge.target}`));
  const dialogEdges = new Set(dialogVisiblePathEdges().map(edge => `${edge.source}\u0000${edge.target}`));
  const pathNodes = new Set([...dialogVisiblePathNodes(), ...replayPathNodes()]);
  const parts = [`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`, `<rect width="100%" height="100%" fill="#f8fafc"/>`];
  resetSpaciousInternalMiniLaneCache();
  for (const edge of state.graph.edges || []) {
    const source = state.positions[edge.source], target = state.positions[edge.target]; if (!source || !target) continue;
    const geo = edgeGeometry(source, target, edge.source, edge.target);
    const active = replayEdges.has(`${edge.source}\u0000${edge.target}`) || dialogEdges.has(`${edge.source}\u0000${edge.target}`);
    const relation = edge.edge_type || edge.relation_type || 'control_flow';
    const nonControl = relation !== 'control_flow';
    parts.push(`<path d="${escapeXml(geo.path)}" fill="none" stroke="${active ? '#1f6fd1' : (nonControl ? '#a06b00' : '#7890b8')}" stroke-width="${active ? 5 : (nonControl ? 1.3 : 1.7)}"${nonControl ? ' stroke-dasharray="5 6" opacity="0.72"' : ''}/>`);
    const edgeText = relation === 'control_flow' ? (edge.key || '') : (edge.state_path || edge.artifact_path || relation);
    parts.push(`<text x="${geo.label.x}" y="${geo.label.y}" font-family="monospace" font-size="11" fill="#53657f">${escapeXml(edgeText)}</text>`);
  }
  for (const node of state.graph.nodes || []) {
    const pos = state.positions[node.id]; if (!pos) continue; const size = nodeSize(node.id);
    const isGate = node.element_type === 'gate', active = pathNodes.has(node.id);
    const stroke = active ? '#1f6fd1' : (isGate ? '#b77600' : '#6680ae'); const fill = isGate ? '#fff8e8' : (node.terminal ? '#effaf3' : '#ffffff');
    if (isGate) { const x=pos.x,y=pos.y,w=size.width,h=size.height,cut=12; parts.push(`<path d="M ${x+cut} ${y} H ${x+w-cut} L ${x+w} ${y+cut} V ${y+h-cut} L ${x+w-cut} ${y+h} H ${x+cut} L ${x} ${y+h-cut} V ${y+cut} Z" fill="${fill}" stroke="${stroke}" stroke-width="${active ? 4 : 2}"/>`); }
    else parts.push(`<rect x="${pos.x}" y="${pos.y}" width="${size.width}" height="${size.height}" rx="9" fill="${fill}" stroke="${stroke}" stroke-width="${active ? 4 : 2}"/>`);
    const svgTextX = pos.x + (isGate ? 16 : 12);
    const titleLines = svgIdentifierLines(node.id, isGate ? 25 : 27, 3);
    titleLines.forEach((line,index) => parts.push(`<text x="${svgTextX}" y="${pos.y+22+index*15}" font-family="Arial,sans-serif" font-size="12" font-weight="700" fill="#244a80">${escapeXml(line)}</text>`));
    const descriptionY = pos.y + 22 + Math.max(1, titleLines.length) * 15 + 8;
    const descriptionMaxLines = Math.max(1, Math.min(5, Math.floor((size.height - (descriptionY - pos.y) - 12) / 16)));
    svgTextLines(node.label, isGate ? 28 : 31, descriptionMaxLines).forEach((line,index) => parts.push(`<text x="${svgTextX}" y="${descriptionY+index*16}" font-family="Arial,sans-serif" font-size="12" fill="#1f2937">${escapeXml(line)}</text>`));
  }
  parts.push('</svg>');
  const blob = new Blob([parts.join('\n')], { type: 'image/svg+xml;charset=utf-8' }); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'ordo-tree.svg'; link.click(); URL.revokeObjectURL(link.href); hideCanvasContextMenu();
}
function replayMarkdown() {
  const replay=state.replayData;if(!replay)return'';const lines=[`# ${replay.run_id?`Run ${replay.run_id}`:'Canonical debug replay'}`,'',`> ${replay.chat_coverage?.statement||'Hidden model reasoning is not captured or displayed.'}`,''];const s=replay.summary||{};
  lines.push(`- Executions: ${s.executions??replay.steps?.length??0}`);if(s.total_duration_ms!=null)lines.push(`- Observed execution time: ${replayDurationText(s.total_duration_ms)}`);if(s.runtime_observable_input_tokens!=null||s.runtime_observable_output_tokens!=null)lines.push(`- Runtime-observable token equivalent: ${s.runtime_observable_input_tokens||0} input / ${s.runtime_observable_output_tokens||0} output`);if(s.exact_host_input_tokens!=null||s.exact_host_output_tokens!=null)lines.push(`- Exact host tokens: ${s.exact_host_input_tokens||0} input / ${s.exact_host_output_tokens||0} output`);lines.push(`- Process quality: ${replay.process_quality?.status||'UNAVAILABLE'}`,`- Integrity: ${replay.integrity?.status||'UNAVAILABLE'}`,`- Artifact quality: ${replay.artifact_quality?.status||'UNAVAILABLE'}`,'');
  for(const step of replay.steps||[]){lines.push(`## Execution ${step.execution_sequence||step.index}: ${step.id||'(unknown)'}`,'');const tele=step.telemetry||{};if(tele.duration_ms!=null)lines.push(`Duration: ${replayDurationText(tele.duration_ms)}`);if(tele.estimated_input_tokens!=null||tele.estimated_output_tokens!=null)lines.push(`Runtime-observable token equivalent: ${tele.estimated_input_tokens||0} input / ${tele.estimated_output_tokens||0} output`);if(tele.exact_host_input_tokens!=null||tele.exact_host_output_tokens!=null)lines.push(`Exact host tokens: ${tele.exact_host_input_tokens||0} input / ${tele.exact_host_output_tokens||0} output`);lines.push('');for(const event of step.chronology||[]){if(event.event_type==='ASSISTANT_MESSAGE')lines.push('**Assistant · verbatim**','',event.text||'','');else if(event.event_type==='ANALYST_MESSAGE')lines.push('**Analyst · verbatim**','',event.text||'','');else if(event.event_type==='MODEL_ACTION'){lines.push(`**Model action:** ${event.action_summary||event.action_type||''}`,'');if(event.changed_paths?.length)lines.push(`Changed: ${event.changed_paths.join(', ')}`,'');if(event.decision_ids?.length)lines.push(`Decisions: ${event.decision_ids.join(', ')}`,'');}else lines.push(`_${event.event_type||'event'}_`,'');}if(step.file_actions?.length)lines.push(`Files / tools: ${step.file_actions.length} observations`,'');}
  return lines.join('\n');
}

function downloadReplayMarkdown() { const text = replayMarkdown(); if (!text) return; const link=document.createElement('a'); link.href=URL.createObjectURL(new Blob([text],{type:'text/markdown;charset=utf-8'})); link.download=`${state.replayData?.run_id || 'ordo-replay'}.md`; link.click(); URL.revokeObjectURL(link.href); }
function printReplayPdf() {
  if (!state.replayData) return;
  const transcript=document.querySelector('#replay-transcript'), replayHeader=document.querySelector('#replay-header'), replayNote=document.querySelector('#replay-note');
  if (!transcript || !replayHeader || !replayNote) return;
  const win=window.open('', '_blank');
  if (!win) return alert('Allow pop-ups to print the replay as PDF.');
  const title=state.replayData.run_id ? `Run ${state.replayData.run_id}` : 'Ordo replay';
  const stylesheetHref=document.querySelector('link[rel="stylesheet"]')?.href || new URL('styles.css', window.location.href).href;
  const printOverrides=`
    html{background:#fff!important}
    body.replay-print-document{min-width:0!important;margin:0!important;background:#fff!important;color:#182235!important}
    .replay-print-shell{display:block!important;box-sizing:border-box;width:min(900px,calc(100% - 48px));max-width:900px;margin:32px auto;padding:0}
    .replay-print-shell #replay-header{margin-bottom:8px}
    .replay-print-shell #replay-transcript{padding-bottom:0}
    .replay-print-shell .replay-node-link{pointer-events:none;text-decoration:none}
    @media print{
      @page{margin:12mm}
      .replay-print-shell{display:block!important;box-sizing:border-box;width:100%!important;max-width:none!important;margin:0!important;padding:0!important}
      .replay-step,.replay-bubble,.replay-values{break-inside:auto!important;page-break-inside:auto!important}
      .replay-step-head{break-after:avoid-page;page-break-after:avoid}
      .replay-note{break-inside:auto;page-break-inside:auto}
      .replay-print-shell,.replay-print-shell *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
      .replay-print-shell .replay-bubble.analyst{background:#f1f1f1!important;border:1px solid #d6d6d6!important}
      .replay-print-shell .replay-bubble.analyst .replay-values{background:rgba(255,255,255,.72)!important}
    }`;
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeXml(title)}</title><link rel="stylesheet" href="${escapeXml(stylesheetHref)}"><style>${printOverrides}</style></head><body class="replay-print-document"><div class="replay-print-shell"><div id="replay-header">${replayHeader.innerHTML}</div><div class="replay-note">${replayNote.innerHTML}</div><div id="replay-transcript">${transcript.innerHTML}</div></div></body></html>`);
  win.document.close();
  win.focus();
  const triggerPrint=()=>setTimeout(()=>win.print(),120);
  if (win.document.readyState === 'complete') triggerPrint();
  else win.addEventListener('load',triggerPrint,{once:true});
}

function playbookUsesDirectTransitions() { return Boolean(state.source?.playbook) || (state.source?.nodes || []).some(node => Object.hasOwn(node, "transitions") || Object.hasOwn(node, "navigation_contract")); }
async function createTransition(sourceId, targetId) {
  if (!state.source || sourceId === targetId) return alert("Choose a different target node.");
  const source = sourceRecord(sourceId), target = (state.graph.nodes || []).find(item => item.id === targetId);
  if (!source || !target) return alert("Both nodes must exist.");
  if (target.element_type === "terminal" && !confirm(`Route ${sourceId} to external terminal ${targetId}?`)) return;
  if ((state.graph.nodes || []).find(item => item.id === sourceId)?.element_type === "gate") {
    const outcome = prompt("Gate route (pass or fail):", "pass");
    if (!outcome) return;
    const canonicalGate = Object.hasOwn(source, "pass_to") || Object.hasOwn(source, "fail_to");
    const key = outcome.toLowerCase() === "pass" ? (canonicalGate ? "pass_to" : "on_pass") : outcome.toLowerCase() === "fail" ? (canonicalGate ? "fail_to" : "on_fail") : null;
    if (!key) return alert("A gate route must be pass or fail.");
    if (source[key]) return alert(`${sourceId} already has an ${outcome} route. Delete or edit it first.`);
    source[key] = targetId;
    state.pendingTransitionSource = null;
    await refresh(state.source); state.selected = sourceId; state.selectedNodes = new Set([sourceId]); render(); return;
  }
  const label = prompt("Transition outcome label:", `to_${targetId}`);
  if (!label) return;
  const canonical = Array.isArray(source.transitions) || Boolean(source.navigation_contract);
  const direct = Object.hasOwn(source, "transitions") || (playbookUsesDirectTransitions() && !source.on_answer);
  if (canonical) {
    source.transitions ||= [];
    source.transitions.push({ id: label, when: `transition condition for ${label}`, to: targetId });
    source.navigation_contract ||= {};
    source.navigation_contract.allowed_to ||= [];
    if (!source.navigation_contract.allowed_to.includes(targetId)) source.navigation_contract.allowed_to.push(targetId);
    const targetRecord = sourceRecord(targetId);
    if (targetRecord) { targetRecord.navigation_contract ||= {}; targetRecord.navigation_contract.allowed_from ||= []; if (!targetRecord.navigation_contract.allowed_from.includes(sourceId)) targetRecord.navigation_contract.allowed_from.push(sourceId); }
  } else if (direct) {
    source.transitions ||= {};
    if (Object.hasOwn(source.transitions, label)) return alert(`The outcome label "${label}" already exists on ${sourceId}.`);
    source.transitions[label] = targetId;
  } else {
    source.on_answer ||= {};
    if (Object.hasOwn(source.on_answer, label)) return alert(`The outcome label "${label}" already exists on ${sourceId}.`);
    source.on_answer[label] = { next: targetId };
    const targetRecord = sourceRecord(targetId);
    if (targetRecord) { targetRecord.allowed_from ||= []; if (!targetRecord.allowed_from.includes(sourceId)) targetRecord.allowed_from.push(sourceId); }
  }
  state.pendingTransitionSource = null;
  await refresh(state.source); state.selected = sourceId; state.selectedNodes = new Set([sourceId]); render();
}
function beginTransition(sourceId) { state.pendingTransitionSource = sourceId; state.selected = sourceId; state.selectedNodes = new Set([sourceId]); state.selectedEdge = null; hideEdgeMenu(); render(); }
function handleNodeClick(nodeId, event) {
  if (!state.pendingTransitionSource) {
    const additive = Boolean(event?.ctrlKey || event?.metaKey || event?.shiftKey);
    if (!additive && state.panelTab === "dialog" && state.dialogPath?.nodes.includes(nodeId)) {
      state.selected = nodeId; state.selectedNodes = new Set([nodeId]); state.selectedEdge = null;
      updateDialogFocusVisuals(nodeId);
      scrollDialogToNode(nodeId);
      return;
    }
    return selectNode(nodeId, false);
  }
  if (state.pendingTransitionSource === nodeId) { state.pendingTransitionSource = null; return render(); }
  createTransition(state.pendingTransitionSource, nodeId);
}
async function addTransition(sourceId = state.selected || "") { if (!state.source) return; const chosenSource = prompt("Source node ID:", sourceId); const targetId = prompt("Target node ID:"); if (!chosenSource || !targetId) return; await createTransition(chosenSource, targetId); }

function removeReferencesToIds(ids) {
  const idSet = new Set(ids);
  const records = [...(state.source?.nodes || []), ...(state.source?.gates || [])];
  for (const record of records) {
    if (idSet.has(record.id)) continue;
    if (typeof record.next === "string" && idSet.has(record.next)) delete record.next;
    if (typeof record.on_pass === "string" && idSet.has(record.on_pass)) delete record.on_pass;
    if (typeof record.on_fail === "string" && idSet.has(record.on_fail)) delete record.on_fail;
    if (typeof record.pass_to === "string" && idSet.has(record.pass_to)) delete record.pass_to;
    if (typeof record.fail_to === "string" && idSet.has(record.fail_to)) delete record.fail_to;
    if (record.on_answer && typeof record.on_answer === "object") {
      for (const [key, value] of Object.entries(record.on_answer)) {
        if (typeof value === "string" && idSet.has(value)) delete record.on_answer[key];
        else if (value && typeof value === "object" && typeof value.next === "string" && idSet.has(value.next)) delete record.on_answer[key];
      }
    }
    if (Array.isArray(record.transitions)) record.transitions = record.transitions.filter(item => !(item && typeof item === "object" && idSet.has(item.to)));
    else if (record.transitions && typeof record.transitions === "object") {
      for (const [key, value] of Object.entries(record.transitions)) if (typeof value === "string" && idSet.has(value)) delete record.transitions[key];
    }
    if (Array.isArray(record.allowed_from)) record.allowed_from = record.allowed_from.filter(id => !idSet.has(id));
    if (Array.isArray(record.allowed_to)) record.allowed_to = record.allowed_to.filter(id => !idSet.has(id));
    if (record.navigation_contract && typeof record.navigation_contract === "object") {
      if (Array.isArray(record.navigation_contract.allowed_from)) record.navigation_contract.allowed_from = record.navigation_contract.allowed_from.filter(id => !idSet.has(id));
      if (Array.isArray(record.navigation_contract.allowed_to)) record.navigation_contract.allowed_to = record.navigation_contract.allowed_to.filter(id => !idSet.has(id));
    }
  }
  const entry = state.source?.graph_contract?.entry_node;
  if (entry && idSet.has(entry)) delete state.source.graph_contract.entry_node;
  const playbookEntry = state.source?.playbook?.entry_node;
  if (playbookEntry && idSet.has(playbookEntry)) delete state.source.playbook.entry_node;
}
async function deleteSelectedNodes() {
  const ids = [...state.selectedNodes].filter(id => sourceRecord(id));
  if (!ids.length) return;
  if (!confirm(`Delete ${ids.length} selected element${ids.length === 1 ? "" : "s"}? Connected transitions to or from them will also be removed.`)) return;
  removeReferencesToIds(ids);
  const idSet = new Set(ids);
  if (Array.isArray(state.source.nodes)) state.source.nodes = state.source.nodes.filter(record => !idSet.has(record.id));
  if (Array.isArray(state.source.gates)) state.source.gates = state.source.gates.filter(record => !idSet.has(record.id));
  ids.forEach(id => { delete state.positions[id]; state.manualPositions.delete(id); });
  state.selectedNodes = new Set(); state.selected = null; state.selectedEdge = null;
  hideCanvasContextMenu();
  await refresh(state.source);
}
function clearSelection() { state.selectedNodes = new Set(); state.selected = null; state.selectedEdge = null; render(); }

document.querySelector("#add-selected-transition").addEventListener("click", () => addTransition(state.selected));
form.addEventListener("submit", async event => { event.preventDefault(); if (!state.selected) return; const sections = Object.fromEntries([...document.querySelectorAll("[data-section-key]")].map(field => [field.dataset.sectionKey, field.value])); const view = selectedView(); try { const data = await request("/api/update-node-sections", { source: state.source, old_id: state.selected, collection: view?.collection, sections }); state.source = data.source; state.graph = data.graph; state.positions = {}; state.manualPositions = new Set(); state.selected = data.node_id; state.selectedNodes = new Set([data.node_id]); render(); } catch (error) { alert(error.message); } });
document.querySelector("#delete-node").addEventListener("click", async () => { if (!state.selected) return; const view = selectedView(); const connected = (state.graph.edges || []).filter(edge => edge.source === state.selected || edge.target === state.selected); if (connected.length) return alert("This element still has transitions. Update or remove those transitions before deleting it."); if (!view?.collection || !confirm(`Delete ${state.selected}?`)) return; state.source[view.collection] = state.source[view.collection].filter(record => record.id !== state.selected); state.positions = {}; state.manualPositions = new Set(); await refresh(state.source); });
document.querySelector("#delete-transition").addEventListener("click", () => { if (state.selectedEdge) deleteDirectTransition(state.selectedEdge); });
document.querySelector("#cancel-transition-mode").addEventListener("click", () => { state.pendingTransitionSource = null; render(); });
document.querySelector("#edge-delete-action").addEventListener("click", () => { if (state.selectedEdge) deleteDirectTransition(state.selectedEdge); });
document.querySelector("#edge-context-menu").addEventListener("pointerenter", () => clearTimeout(edgeMenuTimer));
document.querySelector("#edge-context-menu").addEventListener("pointerleave", scheduleEdgeMenuHide);

const marquee = document.createElement("div");
marquee.id = "selection-marquee"; marquee.hidden = true; workspace.append(marquee);
workspace.addEventListener("pointerdown", event => {
  // alpha.20.0.26 is read-only: marquee/multi-selection authoring is disabled.
  return;
  if (event.button !== 0 || state.pendingTransitionSource || event.target.closest?.(".node") || event.target.closest?.(".edge-hit") || event.target.closest?.("#node-tooltip") || event.target.closest?.("#empty-state") || event.target.closest?.("button, label, input, select, textarea, a")) return;
  hideCanvasContextMenu(); hideNodeTooltip();
  const rect = canvas.getBoundingClientRect();
  state.marqueeStart = { clientX: event.clientX, clientY: event.clientY, x: event.clientX - rect.left, y: event.clientY - rect.top, additive: Boolean(event.ctrlKey || event.metaKey || event.shiftKey) };
  marquee.hidden = false; marquee.style.left = `${state.marqueeStart.x}px`; marquee.style.top = `${state.marqueeStart.y}px`; marquee.style.width = "0px"; marquee.style.height = "0px";
  workspace.setPointerCapture?.(event.pointerId);
});
workspace.addEventListener("pointermove", event => {
  if (!state.marqueeStart) return;
  const rect = canvas.getBoundingClientRect(), x = event.clientX - rect.left, y = event.clientY - rect.top;
  const left = Math.min(state.marqueeStart.x, x), top = Math.min(state.marqueeStart.y, y), right = Math.max(state.marqueeStart.x, x), bottom = Math.max(state.marqueeStart.y, y);
  Object.assign(marquee.style, { left: `${left}px`, top: `${top}px`, width: `${right-left}px`, height: `${bottom-top}px` });
});
workspace.addEventListener("pointerup", event => {
  if (!state.marqueeStart) return;
  const rect = canvas.getBoundingClientRect(), x = event.clientX - rect.left, y = event.clientY - rect.top;
  const left = Math.min(state.marqueeStart.x, x), top = Math.min(state.marqueeStart.y, y), right = Math.max(state.marqueeStart.x, x), bottom = Math.max(state.marqueeStart.y, y);
  const moved = Math.abs(event.clientX - state.marqueeStart.clientX) + Math.abs(event.clientY - state.marqueeStart.clientY) > 6;
  const next = state.marqueeStart.additive ? new Set(state.selectedNodes) : new Set();
  if (moved) {
    for (const node of state.graph?.nodes || []) {
      const pos = state.positions[node.id]; if (!pos) continue;
      const nodeRight = pos.x + nodeSize(node.id).width, nodeBottom = pos.y + nodeHeight(node.id);
      if (pos.x < right && nodeRight > left && pos.y < bottom && nodeBottom > top) next.add(node.id);
    }
  }
  state.selectedNodes = next; state.selected = next.values().next().value || null; state.selectedEdge = null; state.marqueeStart = null; marquee.hidden = true; render();
});

workspace.addEventListener("scroll", () => {
  if (state.dialogSyncTimer) clearTimeout(state.dialogSyncTimer);
  state.dialogSyncTimer = setTimeout(syncDialogFromWorkspaceScroll, 140);
}, { passive: true });

const inspectorPanel = document.querySelector("#inspector");
inspectorPanel?.addEventListener("scroll", () => {
  if (state.panelTab !== "replay") return;
  if (state.replaySyncTimer) clearTimeout(state.replaySyncTimer);
  state.replaySyncTimer = setTimeout(syncReplayFromInspectorScroll, 120);
}, { passive: true });

workspace.addEventListener("contextmenu", showCanvasContextMenu);
document.querySelector("#canvas-add-node").addEventListener("click", () => createDisconnectedElement("node"));
document.querySelector("#canvas-add-gate").addEventListener("click", () => createDisconnectedElement("gate"));
document.querySelector("#canvas-add-materialization").addEventListener("click", () => createDisconnectedElement("materialization"));
document.querySelector("#canvas-add-terminal").addEventListener("click", () => createDisconnectedElement("terminal"));
document.querySelector("#canvas-collapse-all").addEventListener("click", () => { hideCanvasContextMenu(); setAllNodesCollapsed(true); });
document.querySelector("#canvas-expand-all").addEventListener("click", () => { hideCanvasContextMenu(); setAllNodesCollapsed(false); });
document.querySelector("#canvas-toggle-collapse").addEventListener("click", event => {
  const nodeId = event.currentTarget.dataset.nodeId;
  if (!nodeId) return;
  const collapse = !state.collapsedNodes.has(nodeId);
  hideCanvasContextMenu(); setNodeCollapsed(nodeId, collapse);
});
document.querySelector("#canvas-download-yaml").addEventListener("click", downloadYaml);
document.querySelector("#canvas-download-playbook")?.addEventListener("click", downloadFullPlaybook);
document.querySelector("#canvas-download-svg")?.addEventListener("click", downloadTreeSvg);
document.querySelector("#canvas-delete-selection").addEventListener("click", deleteSelectedNodes);
document.querySelector("#canvas-dialog-from-entry").addEventListener("click", event => { const nodeId = event.currentTarget.dataset.nodeId; if (nodeId) openEntryToNodeDialog(nodeId); });
document.querySelector("#dialog-play-toggle").addEventListener("click", () => { if (state.dialogPlayMode && state.dialogPlaying) pauseDialogPlayback(); else startDialogPlayback(!state.dialogPlayMode); });
document.querySelector("#dialog-restart").addEventListener("click", () => startDialogPlayback(true));
document.querySelector("#dialog-static").addEventListener("click", showFullDialog);
document.querySelector("#dialog-advance-mode").addEventListener("change", event => {
  const mode = ["manual", "timer"].includes(event.target.value) ? event.target.value : "manual";
  clearDialogPlaybackTimer();
  state.dialogAdvanceMode = mode;
  renderDialog();
  if (state.dialogPlaying) scheduleDialogPlayback();
});
document.querySelector("#dialog-delay").addEventListener("change", event => { state.dialogDelay = Number(event.target.value) || 2; if (state.dialogPlaying && state.dialogAdvanceMode === "timer") scheduleDialogPlayback(); });
document.querySelector("#dialog-auto-pass").addEventListener("change", event => { state.dialogAutoPassGates = !!event.target.checked; if (state.dialogPlaying) scheduleDialogPlayback(); });
document.addEventListener("pointerdown", event => { if (!event.target.closest?.("#canvas-context-menu")) hideCanvasContextMenu(); if (!event.target.closest?.("#source-flow-context-menu")) hideSourceFlowContextMenu(); });
document.addEventListener("keydown", event => { if (event.key === "Escape") { hideCanvasContextMenu(); hideSourceFlowContextMenu(); closeLiveSettingModal(); closeRecoveryClarificationDialog(); closeTokenDebugModal(); } });
document.querySelectorAll("[data-inspector-tab]").forEach(button => button.addEventListener("click", () => showInspectorTab(button.dataset.inspectorTab)));
document.querySelector("#header-model-settings")?.addEventListener("click",()=>openLiveSettingModal("connection"));
function liveDisplayText(id) {
  const record = sourceRecord(id), view = graphNodeView(id);
  if (!record) return id || "";
  const fields = view?.element_type === "gate"
    ? ["title", "purpose", "condition", "description", "summary", "question", "prompt", "instruction", "action"]
    : ["title", "question", "purpose", "description", "summary", "prompt", "instruction", "action"];
  for (const key of fields) {
    const value = record[key];
    if (typeof value === "string" && value.trim() && value.trim() !== id) return value.trim();
  }
  return view?.label || id;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
}

async function copyTextToClipboard(text) {
  const value=String(text ?? "");
  if (navigator.clipboard?.writeText) {
    try { await navigator.clipboard.writeText(value); return true; } catch (_) {}
  }
  const area=document.createElement("textarea");
  area.value=value; area.setAttribute("readonly", "");
  area.style.position="fixed"; area.style.left="-9999px"; area.style.top="0"; area.style.opacity="0";
  document.body.append(area); area.focus(); area.select();
  let copied=false;
  try { copied=Boolean(document.execCommand("copy")); } finally { area.remove(); }
  if (!copied) throw new Error("Clipboard copy is not available in this browser context.");
  return true;
}
function chatCopyButtonIcon(copied=false) {
  return copied
    ? '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m4.5 10.3 3.1 3.1 7.8-7.8"/></svg>'
    : '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="6.5" y="6.5" width="8" height="9" rx="1.5"/><path d="M5 13.5H4.5A1.5 1.5 0 0 1 3 12V4.5A1.5 1.5 0 0 1 4.5 3H11a1.5 1.5 0 0 1 1.5 1.5V5"/></svg>';
}
function attachChatCopyButton(host, text, align="left") {
  if (!host) return;
  const value=String(text ?? "");
  if (!value) return;
  host.classList.add("chat-copy-host", align === "right" ? "copy-align-right" : "copy-align-left");
  const button=document.createElement("button");
  button.type="button"; button.className="chat-message-copy"; button.title="Copy message"; button.setAttribute("aria-label", "Copy message");
  button.innerHTML=chatCopyButtonIcon(false);
  button.addEventListener("click", async event => {
    event.stopPropagation();
    try {
      await copyTextToClipboard(value);
      button.classList.add("copied"); button.title="Copied"; button.setAttribute("aria-label", "Copied"); button.innerHTML=chatCopyButtonIcon(true);
      window.setTimeout(() => { if (!button.isConnected) return; button.classList.remove("copied"); button.title="Copy message"; button.setAttribute("aria-label", "Copy message"); button.innerHTML=chatCopyButtonIcon(false); }, 1200);
    } catch (_) {
      button.classList.add("copy-failed"); button.title="Copy failed";
      window.setTimeout(() => { if (!button.isConnected) return; button.classList.remove("copy-failed"); button.title="Copy message"; }, 1600);
    }
  });
  host.append(button);
}
function safeMarkdownHref(rawHref) {
  const href = String(rawHref || "").trim();
  if (/^(https?:|mailto:)/i.test(href)) return href;
  return "";
}
function renderMarkdownInline(value) {
  const codeSpans = [];
  let raw = String(value ?? "").replace(/`([^`\n]+)`/g, (_, code) => {
    const token = `ORDOINLINECODETOKEN${codeSpans.length}ZZ`;
    codeSpans.push(`<code>${escapeHtml(code)}</code>`);
    return token;
  });
  // Keep machine IDs such as N_TRIGGER_SOURCE_BLOCK and G_TEST_COVERAGE_COMPLETE
  // literal. Markdown underscore emphasis must never eat separators from runtime IDs.
  raw = raw.replace(/\b(?:[A-Z][A-Z0-9]*_){1,}[A-Z0-9_]+\b/g, id => {
    const token = `ORDOINLINECODETOKEN${codeSpans.length}ZZ`;
    codeSpans.push(`<span class="technical-id">${escapeHtml(id)}</span>`);
    return token;
  });
  let html = escapeHtml(raw);
  html = html.replace(/\[([^\]\n]+)\]\(([^)\s]+)\)/g, (_, label, href) => {
    const safe = safeMarkdownHref(href);
    return safe ? `<a href="${escapeHtml(safe)}" target="_blank" rel="noopener noreferrer">${label}</a>` : label;
  });
  html = html.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^_\n]+)__/g, '<strong>$1</strong>');
  html = html.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  html = html.replace(/(^|[^_])_([^_\n]+)_/g, '$1<em>$2</em>');
  codeSpans.forEach((span, index) => { html = html.replace(`ORDOINLINECODETOKEN${index}ZZ`, span); });
  return html;
}
function markdownTableCells(line) {
  const trimmed = String(line || "").trim();
  if (!trimmed.includes("|")) return null;
  const body = trimmed.replace(/^\|/, "").replace(/\|$/, "");
  const cells = body.split("|").map(cell => cell.trim());
  return cells.length >= 2 ? cells : null;
}
function isMarkdownTableSeparator(line) {
  const cells = markdownTableCells(line);
  return !!cells && cells.every(cell => /^:?-{3,}:?$/.test(cell.replace(/\s+/g, "")));
}
function renderBasicMarkdown(text) {
  const source = String(text ?? "").replace(/\r\n?/g, "\n");
  const lines = source.split("\n");
  const out = [];
  let listType = null;
  const closeList = () => { if (listType) { out.push(`</${listType}>`); listType = null; } };

  for (let i = 0; i < lines.length; i += 1) {
    const rawLine = lines[i];

    // Fenced code blocks are rendered verbatim and never interpreted as Markdown/HTML.
    if (/^\s*```/.test(rawLine)) {
      closeList();
      const code = [];
      i += 1;
      while (i < lines.length && !/^\s*```/.test(lines[i])) { code.push(lines[i]); i += 1; }
      out.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
      continue;
    }

    // GitHub-flavoured Markdown table: header row followed by a separator row.
    const headerCells = markdownTableCells(rawLine);
    if (headerCells && i + 1 < lines.length && isMarkdownTableSeparator(lines[i + 1])) {
      closeList();
      const separators = markdownTableCells(lines[i + 1]);
      const aligns = separators.map(cell => {
        const clean = cell.replace(/\s+/g, "");
        if (clean.startsWith(":") && clean.endsWith(":")) return "center";
        if (clean.endsWith(":")) return "right";
        if (clean.startsWith(":")) return "left";
        return "";
      });
      const rows = [];
      i += 2;
      while (i < lines.length) {
        const row = markdownTableCells(lines[i]);
        if (!row || !lines[i].includes("|")) { i -= 1; break; }
        rows.push(row);
        i += 1;
      }
      const head = headerCells.map((cell, idx) => `<th${aligns[idx] ? ` style="text-align:${aligns[idx]}"` : ""}>${renderMarkdownInline(cell)}</th>`).join("");
      const bodyRows = rows.map(row => `<tr>${headerCells.map((_, idx) => `<td${aligns[idx] ? ` style="text-align:${aligns[idx]}"` : ""}>${renderMarkdownInline(row[idx] || "")}</td>`).join("")}</tr>`).join("");
      out.push(`<div class="md-table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${bodyRows}</tbody></table></div>`);
      continue;
    }

    const ul = rawLine.match(/^\s*[-*+]\s+(.+)$/);
    const ol = rawLine.match(/^\s*\d+[.)]\s+(.+)$/);
    if (ul || ol) {
      const type = ul ? "ul" : "ol";
      if (listType !== type) { closeList(); out.push(`<${type}>`); listType = type; }
      out.push(`<li>${renderMarkdownInline(ul ? ul[1] : ol[1])}</li>`);
      continue;
    }
    closeList();

    if (!rawLine.trim()) { out.push('<div class="md-spacer"></div>'); continue; }

    const heading = rawLine.match(/^\s*(#{1,4})\s+(.+)$/);
    if (heading) {
      const level = Math.min(4, heading[1].length);
      out.push(`<h${level}>${renderMarkdownInline(heading[2])}</h${level}>`);
      continue;
    }
    const quote = rawLine.match(/^\s*>\s?(.*)$/);
    if (quote) { out.push(`<blockquote>${renderMarkdownInline(quote[1])}</blockquote>`); continue; }
    if (/^\s*(---+|\*\*\*+)\s*$/.test(rawLine)) { out.push("<hr>"); continue; }

    out.push(`<div>${renderMarkdownInline(rawLine)}</div>`);
  }
  closeList();
  return out.join("");
}


let activeTokenDebug = null;
let activeTokenDebugTab = "summary";
function prettyJson(value) { try { return JSON.stringify(value ?? null, null, 2); } catch (_) { return String(value ?? ""); } }
function approxTokensFromChars(chars) { return Math.max(0, Math.round(Number(chars || 0) / 4)); }
function classifyExecutionStep(d) {
  const skippedIncomplete = d?.semantic_model_attempts?.some?.(a => a?.skipped_model_call === true && a?.reason === "context_incomplete")
    || (d?.input?.request_payload == null && d?.output?.api_response == null && d?.runtime?.failure_class === "context_incomplete");
  if (skippedIncomplete) return "skipped_incomplete_context";
  if (d?.runtime?.llm_call_skipped) {
    const reason=String(d?.runtime?.reason || "");
    if (reason.includes("human") || reason.includes("analyst")) return "human_or_auto_answer";
    return "deterministic";
  }
  const replay = d?.input?.request_payload?.replay === true || d?.output?.api_response?.replay === true;
  if (replay) return "replayed_model_call";
  if (d?.input?.request_payload != null || d?.output?.api_response != null) return "live_model_call";
  return "other_runtime_only";
}
function retryReasonForAttempt(a) {
  if (a?.parse_error) return "parse_error";
  const errors=a?.validation?.errors;
  if (Array.isArray(errors) && errors.length) {
    const joined=errors.map(String).join(" | ");
    if (joined.includes("check_results")) return "gate_check_results_contract";
    if (joined.includes("StatePatch") || joined.includes("operation") || joined.includes("path")) return "state_patch_contract";
    return "structured_contract";
  }
  return "unknown";
}
function assessArtifactFreshness(stateLineage, artifactLineage) {
  return artifactLineage.map(a => {
    const materialized=Number(a?.materialized_from_revision ?? -1);
    const deps=Array.isArray(a?.depends_on_paths) ? a.depends_on_paths.map(String) : [];
    const later=(stateLineage||[]).filter(s => Number(s?.revision ?? -1) > materialized);
    const relevant=deps.length ? later.filter(s => deps.some(p => String(s?.path||"")===p || String(s?.path||"").startsWith(p+".") || p.startsWith(String(s?.path||"")+"."))) : [];
    return {...a, freshness_status: relevant.length ? "stale" : (deps.length ? "fresh" : "unknown_dependencies"), stale_by_state_lineage: relevant.map(s=>({path:s.path,revision:s.revision,producer_element_id:s.producer_element_id}))};
  });
}
function buildAggregateTokenDebug() {
  const trace = Array.isArray(state.liveDebugTrace) ? state.liveDebugTrace : [];
  const classified = trace.map(d => ({d, step_class:classifyExecutionStep(d)}));
  const llmCalls = classified.filter(x => x.step_class === "live_model_call" || x.step_class === "replayed_model_call").map(x=>x.d);
  const replayedCalls = classified.filter(x => x.step_class === "replayed_model_call").map(x=>x.d);
  const liveCalls = classified.filter(x => x.step_class === "live_model_call").map(x=>x.d);
  const deterministicCalls = classified.filter(x => x.step_class === "deterministic").length;
  const skippedIncompleteContext = classified.filter(x => x.step_class === "skipped_incomplete_context").length;
  const humanOrAutoAnswers = classified.filter(x => x.step_class === "human_or_auto_answer").length;
  const otherRuntimeOnly = classified.filter(x => x.step_class === "other_runtime_only").length;
  const evidenceProfile = replayedCalls.length ? (liveCalls.length ? "mixed-replay" : "golden-replay") : "live";
  const stateLineage = trace.flatMap(d => Array.isArray(d?.runtime?.state_lineage) ? d.runtime.state_lineage : []);
  const artifactLineage = trace.flatMap(d => d?.runtime?.artifact_lineage ? [d.runtime.artifact_lineage] : []);
  const liveAttemptCounts = liveCalls.map(d => {
    const attempts=Array.isArray(d?.semantic_model_attempts) ? d.semantic_model_attempts.filter(a => a?.skipped_model_call !== true) : [];
    return attempts.length || ((d?.input?.request_payload != null || d?.output?.api_response != null) ? 1 : 0);
  }).filter(n => n > 0);
  const retryHistogram = liveAttemptCounts.reduce((acc,n) => { const k=String(n); acc[k]=(acc[k]||0)+1; return acc; }, {});
  const liveWithinTwo = liveAttemptCounts.filter(n => n <= 2).length;
  const liveExhausted = liveAttemptCounts.filter(n => n >= 3).length;
  const retryReasonHistogram={};
  for (const d of liveCalls) {
    const attempts=Array.isArray(d?.semantic_model_attempts) ? d.semantic_model_attempts.filter(a=>a?.skipped_model_call!==true) : [];
    for (const a of attempts.slice(0,-1)) { const reason=retryReasonForAttempt(a); retryReasonHistogram[reason]=(retryReasonHistogram[reason]||0)+1; }
  }
  const retryQuality = {
    model_elements: liveAttemptCounts.length,
    retry_histogram: retryHistogram,
    retry_reason_histogram: retryReasonHistogram,
    within_two_attempts_ratio: liveAttemptCounts.length ? liveWithinTwo/liveAttemptCounts.length : null,
    exhausted_retry_budget: liveExhausted,
    acceptance_thresholds: {within_two_attempts_ratio_min:0.95, exhausted_retry_budget_max:0},
    acceptance_pass: evidenceProfile === "live" && liveAttemptCounts.length > 0 && (liveWithinTwo/liveAttemptCounts.length) >= 0.95 && liveExhausted === 0,
  };
  const providerAttempts=liveAttemptCounts.reduce((a,b)=>a+b,0);
  const tokenBaselineUsage={input_tokens:0,output_tokens:0,total_tokens:0,cached_tokens:0,reasoning_tokens:0};
  for (const d of liveCalls) {
    const attempts=Array.isArray(d?.semantic_model_attempts) ? d.semantic_model_attempts.filter(a=>a?.skipped_model_call!==true && a?.usage) : [];
    const usages=attempts.length ? attempts.map(a=>a.usage) : (d?.usage ? [d.usage] : []);
    for (const u of usages) for (const k of Object.keys(tokenBaselineUsage)) tokenBaselineUsage[k]+=Number(u?.[k]||0);
  }
  const artifactFreshness=assessArtifactFreshness(stateLineage,artifactLineage);
  return {
    aggregate: true,
    evidence_profile: evidenceProfile,
    serves_gates: evidenceProfile === "live" ? ["runtime-state-regression","model-capability","token-baseline"] : ["runtime-state-regression"],
    does_not_serve: evidenceProfile === "live" ? [] : ["model-capability","token-baseline"],
    acceptance_eligible: evidenceProfile === "live",
    provenance: {
      live_calls:liveCalls.length, replayed_calls:replayedCalls.length, deterministic_calls:deterministicCalls,
      skipped_incomplete_context:skippedIncompleteContext, human_or_auto_answers:humanOrAutoAnswers, other_runtime_only:otherRuntimeOnly
    },
    provider: state.liveConfig.provider,
    base_url: state.liveConfig.base_url,
    model: state.liveConfig.model,
    provider_capability_profile: state.liveConfig.capability_profile || null,
    structured_output_mode: state.liveConfig.structured_output_mode || "auto",
    usage: { ...tokenBaselineUsage, calls: providerAttempts, semantics: "provider-attempt aggregate" },
    accounting: {logical_model_calls:llmCalls.length, live_model_elements:liveCalls.length, replayed_model_elements:replayedCalls.length, provider_attempts:providerAttempts, token_baseline_attempts:providerAttempts, per_record_usage_semantics:"last-attempt-only unless semantic_model_attempts usage is present"},
    retry_quality: retryQuality,
    run: {
      run_id: state.liveRunId,
      session_id: liveSessionId,
      package_id: state.packageInfo?.id || "",
      status: state.liveOutcome?.status || (state.liveRunning ? "running" : "idle"),
      outcome: state.liveOutcome,
      current_id: state.liveCurrentId,
      path: [...state.livePath],
      final_state: state.liveState,
      history: state.liveHistory.map(({debug, ...item}) => item),
      total_execution_steps: trace.length,
      llm_calls: llmCalls.length,
      step_class_counts: {live_model_call:liveCalls.length,replayed_model_call:replayedCalls.length,deterministic:deterministicCalls,skipped_incomplete_context:skippedIncompleteContext,human_or_auto_answer:humanOrAutoAnswers,other_runtime_only:otherRuntimeOnly},
      run_journal: {state_lineage:stateLineage, artifact_lineage:artifactLineage, artifact_freshness:artifactFreshness},
    },
    // Full per-step evidence, intentionally not reduced to token counters.
    // Each item contains provider/model, exact request input, raw/parsed output,
    // usage and runtime state/route decisions. Runtime-only steps are retained too.
    calls: trace.map((d, index) => ({ index: index + 1, step_class: classifyExecutionStep(d), ...d })),
  };
}
function tokenDebugMetric(label, value) { return `<div class="token-debug-metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`; }
function tokenDebugPre(title, value) { return `<section class="token-debug-section"><h4>${escapeHtml(title)}</h4><pre>${escapeHtml(typeof value === "string" ? value : prettyJson(value))}</pre></section>`; }
function renderTokenDebugSummary(debug) {
  const u=debug?.usage || {};
  let html='<div class="token-debug-grid">';
  html += tokenDebugMetric("Total tokens", Number(u.total_tokens || 0).toLocaleString());
  html += tokenDebugMetric("Input", Number(u.input_tokens || 0).toLocaleString());
  html += tokenDebugMetric("Output", Number(u.output_tokens || 0).toLocaleString());
  html += tokenDebugMetric("Cached input", Number(u.cached_tokens || 0).toLocaleString());
  html += tokenDebugMetric("Reasoning", Number(u.reasoning_tokens || 0).toLocaleString());
  html += tokenDebugMetric("API calls", Number(u.calls || (debug.aggregate ? debug.calls?.length : 1) || 0).toLocaleString());
  html += '</div>';
  if (debug.aggregate) {
    const rows=(debug.calls || []).map(c => `<tr><td>${c.index}</td><td>${escapeHtml(c.current_id || "")}</td><td>${escapeHtml(c.phase || "")}</td><td>${Number(c.usage?.input_tokens || 0).toLocaleString()}</td><td>${Number(c.usage?.output_tokens || 0).toLocaleString()}</td><td>${Number(c.usage?.total_tokens || 0).toLocaleString()}</td></tr>`).join('');
    return html + `<section class="token-debug-section"><h4>Calls in this Run</h4><table class="token-debug-context-table"><thead><tr><th>#</th><th>Element</th><th>Phase</th><th>Input</th><th>Output</th><th>Total</th></tr></thead><tbody>${rows}</tbody></table></section>`;
  }
  const b=debug?.context_breakdown || {};
  const sections=[['Core contract','system_chars'],['Current element','element_chars'],['Runtime state','state_chars'],['History','history_chars'],['Resources','resources_chars'],['Attachments','attachments_chars'],['Analyst clarification','analyst_override_chars']];
  const rows=sections.map(([label,key]) => { const chars=Number(b[key] || 0); return `<tr><td>${label}</td><td>${chars.toLocaleString()}</td><td>≈ ${approxTokensFromChars(chars).toLocaleString()}</td></tr>`; }).join('');
  html += `<section class="token-debug-section"><h4>Input composition</h4><table class="token-debug-context-table"><thead><tr><th>Section</th><th>Characters</th><th>Approx. tokens*</th></tr></thead><tbody>${rows}</tbody></table><p class="hint">* Section token counts are rough character-based estimates. API Input/Output/Total above are authoritative counts returned by OpenAI.</p></section>`;
  html += `<section class="token-debug-section"><h4>Step</h4><table class="token-debug-context-table"><tbody><tr><td>Execution</td><td>${escapeHtml(debug.execution_mechanism || (debug.api_style === "runtime_only" ? "runtime_only" : ""))}</td></tr><tr><td>Model</td><td>${escapeHtml(debug.model || state.liveConfig.model || "")}</td></tr><tr><td>Element</td><td>${escapeHtml(debug.current_id || "")}</td></tr><tr><td>Kind</td><td>${escapeHtml(debug.element_kind || "")}</td></tr><tr><td>Phase</td><td>${escapeHtml(debug.phase || "")}</td></tr><tr><td>Analyst clarification</td><td>${Number(b.analyst_override_chars || 0).toLocaleString()} chars</td></tr></tbody></table></section>`;
  return html;
}
function renderTokenDebugTab() {
  const body=document.querySelector('#token-debug-body'); if (!body || !activeTokenDebug) return;
  const d=activeTokenDebug;
  document.querySelectorAll('[data-token-debug-tab]').forEach(btn => btn.classList.toggle('active', btn.dataset.tokenDebugTab === activeTokenDebugTab));
  if (activeTokenDebugTab === 'summary') body.innerHTML=renderTokenDebugSummary(d);
  else if (activeTokenDebugTab === 'input') {
    if (d.aggregate) body.innerHTML=tokenDebugPre('All step inputs', (d.calls || []).map(c => ({index:c.index, current_id:c.current_id, phase:c.phase, provider:c.provider, model:c.model, input:c.input, context_breakdown:c.context_breakdown})));
    else {
      const clarification=d.input?.context?.analyst_override_context || '';
      body.innerHTML=tokenDebugPre('System / core execution contract', d.input?.system_text || '') + (clarification ? tokenDebugPre('Analyst clarification applied', clarification) : '') + tokenDebugPre('Structured execution context', d.input?.context || {}) + tokenDebugPre('Actual API request payload', d.input?.request_payload || {});
    }
  } else if (activeTokenDebugTab === 'output') {
    if (d.aggregate) body.innerHTML=tokenDebugPre('All step outputs', (d.calls || []).map(c => ({index:c.index, current_id:c.current_id, phase:c.phase, usage:c.usage, output:c.output})));
    else body.innerHTML=tokenDebugPre('Raw model text', d.output?.raw_text || '') + tokenDebugPre('Parsed structured result', d.output?.parsed_result || {}) + tokenDebugPre('Raw OpenAI API response', d.output?.api_response || {});
  } else {
    body.innerHTML=d.aggregate ? tokenDebugPre('Run + all runtime transitions/state', {run:d.run, steps:(d.calls || []).map(c => ({index:c.index, current_id:c.current_id, phase:c.phase, runtime:c.runtime}))}) : tokenDebugPre('Runtime transition/state', d.runtime || {});
  }
}
function openTokenDebugModal(debug) {
  activeTokenDebug=debug || {}; activeTokenDebugTab='summary';
  const modal=document.querySelector('#token-debug-modal'); if (!modal) return;
  const subtitle=document.querySelector('#token-debug-subtitle');
  subtitle.textContent=activeTokenDebug.aggregate ? `Run total · ${state.liveUsage.calls} API calls` : [activeTokenDebug.model, activeTokenDebug.current_id, activeTokenDebug.phase].filter(Boolean).join(' · ');
  modal.hidden=false; modal.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden'; renderTokenDebugTab();
}
function closeTokenDebugModal() { const modal=document.querySelector('#token-debug-modal'); if (!modal) return; modal.hidden=true; modal.setAttribute('aria-hidden','true'); document.body.style.overflow=''; activeTokenDebug=null; }
function tokenDebugCurrentTabText() {
  if (!activeTokenDebug) return '';
  if (activeTokenDebugTab === 'summary') return prettyJson({ model: activeTokenDebug.model, current_id: activeTokenDebug.current_id, phase: activeTokenDebug.phase, usage: activeTokenDebug.usage, context_breakdown: activeTokenDebug.context_breakdown, calls: activeTokenDebug.calls });
  if (activeTokenDebugTab === 'input') return prettyJson(activeTokenDebug.input || activeTokenDebug.calls || {});
  if (activeTokenDebugTab === 'output') return prettyJson(activeTokenDebug.output || activeTokenDebug.usage || {});
  return prettyJson(activeTokenDebug.runtime || activeTokenDebug.calls || {});
}
function downloadTokenDebugJson() {
  if (!activeTokenDebug) return;
  const blob=new Blob([prettyJson(activeTokenDebug)], {type:'application/json;charset=utf-8'}); const url=URL.createObjectURL(blob); const a=document.createElement('a');
  a.href=url; a.download=`ordo-llm-debug-${activeTokenDebug.current_id || 'run'}-${activeTokenDebug.phase || 'summary'}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 500);
}

function liveArtifactUrl(path) {
  return `/api/run-artifact?path=${encodeURIComponent(path)}&package_id=${encodeURIComponent(state.packageInfo?.id||"")}&session_id=${encodeURIComponent(liveSessionId)}&run_id=${encodeURIComponent(state.liveRunId||"")}`;
}
function isMarkdownArtifact(path) {
  return /\.(md|markdown)$/i.test(String(path||""));
}
function isPreviewableTextArtifact(path) {
  return /\.(md|markdown|json|ya?ml|txt|log|py|csv|xml|html?|css|jsx?|tsx?|sh|bash|zsh|toml|ini|cfg|conf|properties|sql)$/i.test(String(path||""));
}
function artifactPreviewMode(path) {
  return isMarkdownArtifact(path) ? "markdown" : (isPreviewableTextArtifact(path) ? "source" : null);
}
function artifactTypeLabel(path) {
  const value=String(path||"").toLowerCase();
  if (/\.zip$/i.test(value)) return "ZIP archive";
  if (/\.(json)$/i.test(value)) return "JSON file";
  if (/\.(ya?ml)$/i.test(value)) return "YAML file";
  if (/\.(txt|log)$/i.test(value)) return "Text file";
  if (/\.(py)$/i.test(value)) return "Python source";
  if (/\.(csv)$/i.test(value)) return "CSV file";
  if (/\.(xml)$/i.test(value)) return "XML file";
  if (/\.(html?)$/i.test(value)) return "HTML source";
  if (/\.(css)$/i.test(value)) return "CSS source";
  if (/\.(jsx?|tsx?)$/i.test(value)) return "Source file";
  if (/\.(sh|bash|zsh)$/i.test(value)) return "Shell script";
  if (/\.(pdf)$/i.test(value)) return "PDF document";
  const ext=(value.match(/\.([a-z0-9]+)$/i)||[])[1];
  return ext ? `${ext.toUpperCase()} file` : "File";
}
function closeArtifactPreview() {
  const panel=document.querySelector("#artifact-preview-panel");
  if (!panel) return;
  panel.hidden=true; panel.removeAttribute("data-path"); editorMain.classList.remove("artifact-preview-open");
  const body=document.querySelector("#artifact-preview-body"); if (body) body.innerHTML="";
}
async function openArtifactPreview(artifact) {
  if (!artifact?.path || !isPreviewableTextArtifact(artifact.path)) return;
  const panel=document.querySelector("#artifact-preview-panel"), body=document.querySelector("#artifact-preview-body"), title=document.querySelector("#artifact-preview-title"), subtitle=document.querySelector("#artifact-preview-subtitle"), dl=document.querySelector("#artifact-preview-download");
  if (!panel || !body || !title || !dl) return;
  // Markdown preview belongs to the right-side workspace. If the user collapsed
  // that pane earlier, opening a document must restore it automatically.
  editorMain.classList.remove("side-collapsed");
  const sideToggle=document.querySelector("#side-pane-toggle");
  if (sideToggle) sideToggle.title="Collapse side panel";
  const filename=artifact.filename || String(artifact.path).split('/').pop() || 'document.md';
  const url=liveArtifactUrl(artifact.path);
  const mode=artifactPreviewMode(artifact.path);
  title.textContent=filename; if (subtitle) subtitle.textContent=mode === "markdown" ? "Markdown preview" : artifactTypeLabel(artifact.path);
  dl.href=url; dl.setAttribute('download',filename); panel.hidden=false; panel.dataset.path=artifact.path; panel.dataset.previewMode=mode || "source"; editorMain.classList.add('artifact-preview-open');
  body.innerHTML='<div class="artifact-preview-loading">Loading preview…</div>';
  try {
    const response=await fetch(url,{cache:'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const text=await response.text();
    if (mode === "markdown") body.innerHTML=renderBasicMarkdown(text);
    else {
      let display=text;
      if (/\.json$/i.test(String(artifact.path||""))) { try { display=JSON.stringify(JSON.parse(text), null, 2); } catch(_) {} }
      body.innerHTML=`<pre class="artifact-source-preview"><code>${escapeHtml(display)}</code></pre>`;
    }
  } catch(error) { body.innerHTML=`<div class="artifact-preview-error">Could not load preview: ${escapeHtml(String(error.message||error))}</div>`; }
}

function updateLiveComposerLayout() {
  const input=document.querySelector('#live-input'), shell=document.querySelector('.live-composer-shell'), expand=document.querySelector('#live-composer-expand');
  if (!input || !shell || !expand) return;
  const style=getComputedStyle(input);
  const lineHeight=parseFloat(style.lineHeight)||22;
  input.style.height='auto';
  const contentHeight=Math.max(lineHeight, input.scrollHeight - (parseFloat(style.paddingTop)||0) - (parseFloat(style.paddingBottom)||0));
  const lineEstimate=Math.max(1, Math.ceil(contentHeight / lineHeight));
  const multiline=lineEstimate > 1 || String(input.value||'').includes('\n');
  const maxLines=state.liveComposerExpanded ? 10 : (multiline ? 3 : 1);
  const target=Math.min(input.scrollHeight, Math.ceil(lineHeight*maxLines + (parseFloat(style.paddingTop)||0) + (parseFloat(style.paddingBottom)||0)));
  input.style.height=`${Math.max(Math.ceil(lineHeight+8),target)}px`;
  input.style.overflowY=input.scrollHeight > target + 1 ? 'auto' : 'hidden';
  shell.dataset.composerMode=state.liveComposerExpanded ? 'expanded' : (multiline ? 'multiline' : 'single');
  expand.hidden=!multiline && !state.liveComposerExpanded;
  expand.textContent=state.liveComposerExpanded ? '↙' : '↗';
  expand.title=state.liveComposerExpanded ? 'Collapse composer' : 'Expand composer';
  expand.setAttribute('aria-label',expand.title);
  requestAnimationFrame(updateLiveScrollToBottomControl);
}

function appendLiveMessage(role, text, meta = "", usage = null, contextBreakdown = null, debug = null, artifact = null, attachments = []) {
  state.liveHistory.push({ role, text, meta, usage, context_breakdown: contextBreakdown, debug, artifact, attachments: Array.isArray(attachments) ? attachments : [], node_id: state.liveCurrentId });
}
function formatAttachmentSize(bytes) {
  const n=Number(bytes||0); if (n < 1024) return `${n} B`; if (n < 1024*1024) return `${(n/1024).toFixed(n<10240?1:0)} KB`; return `${(n/(1024*1024)).toFixed(1)} MB`;
}
function attachmentPublicMeta(item) { return { name:item.name, type:item.type || "application/octet-stream", size:Number(item.size||0) }; }

function humanReadableNodeLabel(target) {
  if (!target || String(target)==="stop_target") return "Stop process";
  const view = graphNodeView(target);
  const record = [...(state.source?.nodes||[]), ...(state.source?.gates||[])].find(item=>item?.id===target) || null;
  const title = String(record?.title || record?.question || view?.label || "").trim();
  if (title && title !== target) return title.replace(/\s+/g, " ").slice(0, 110);
  const cleaned=String(target).replace(/^[NG]_/, "").replace(/_/g, " ").toLowerCase();
  return cleaned ? cleaned.charAt(0).toUpperCase()+cleaned.slice(1) : String(target);
}


function isConversationalRecoveryNode(id) {
  const current=[...(state.source?.nodes||[]), ...(state.source?.gates||[])].find(item=>item?.id===id) || null;
  return !!current && (String(current.action||"").toUpperCase()==="AI.EXPLAIN_VALIDATION_FAILURE_AND_ROUTE" || String(current.id||"")==="N_VALIDATION_FAILURE_RECOVERY");
}

async function submitRecoveryConversation(currentId, text, attachments=[]) {
  const failure=latestFailedGateEvidence(currentId) || {};
  const choices=(state.liveChoiceContext?.options || []).map(o=>({target:o.target,label:o.label,value:o.value}));
  const data=await request("/api/recovery-chat", {
    session_id: liveSessionId, package_id: state.packageInfo?.id || "", source: state.source,
    evidence: failure, choices, state: state.liveState, state_revision: state.liveRevision,
    history: (state.liveHistory||[]).map(x=>({role:x.role,text:x.text,node_id:x.node_id})),
    analyst_input: text, attachments: attachments.map(attachmentPublicMeta)
  });
  if (data.state && typeof data.state === "object") state.liveState=data.state;
  if (Number.isInteger(data.state_revision)) state.liveRevision=data.state_revision;
  if (data.usage) accumulateLiveUsage(data.usage);
  if (data.debug) state.liveDebugTrace.push({current_id:currentId, element_kind:"recovery_chat", phase:"respond", ...data.debug, runtime:{state_after:state.liveState, suggested_action:data.suggested_action, recommended_recovery_target:data.recommended_recovery_target}});
  appendLiveMessage("assistant", data.assistant_message || uiText("Ready to continue diagnosis.","Ready to continue diagnosis."), uiText("recovery conversation","recovery conversation"), data.usage || null, null, data.debug || null);
  state.liveAwaitingInput=true;
  // Conversational recovery is manual by design: recorded auto-answers must not consume it.
  state.livePaused=true;
  const action=String(data.suggested_action||"stay");
  if (action === "retry_gate" && data.failed_gate) {
    appendLiveMessage("system", uiText(`Re-running ${data.failed_gate} at analyst request.`,`Re-running ${data.failed_gate} at analyst request.`), "recovery retry");
    state.liveCurrentId=String(data.failed_gate); state.livePath.push(state.liveCurrentId); state.livePendingEntryMode={target:state.liveCurrentId,mode:"retry"}; state.liveAwaitingInput=false;
    await advanceLiveUntilInput();
    return;
  }
  if (action === "go_to_target" && data.recommended_recovery_target) {
    const target=String(data.recommended_recovery_target);
    appendLiveMessage("system", uiText(`Entering manual repair mode → ${target}`,`Entering manual repair mode → ${target}`), "recovery repair");
    state.liveAnalystOverride={active:true,target,scope:"single",text:text};
    state.liveCurrentId=target; state.livePath.push(target); state.livePendingEntryMode={target,mode:"recovery"}; state.liveAwaitingInput=false;
    await advanceLiveUntilInput();
  }
}

function latestFailedGateEvidence(beforeCurrentId = "") {
  for (let i=(state.liveDebugTrace||[]).length-1; i>=0; i--) {
    const debug=state.liveDebugTrace[i];
    if (!debug || debug.current_id === beforeCurrentId) continue;
    if (debug.element_kind !== "gate") continue;
    const runtime=debug.runtime || {};
    if (runtime.selected_route_key !== "on_fail" && runtime.gate_result !== "fail") continue;
    const parsed=debug.output?.parsed_result || {};
    const gateFailure=debug.alpha20?.gate_failure || {};
    return {
      gate_id: String(gateFailure.gate_id || debug.current_id || ""),
      explanation: String(gateFailure.assistant_message || gateFailure.rationale_short || parsed.assistant_message || parsed.rationale_short || runtime.unresolved_reason || "Validation failed.").trim(),
      rationale: String(gateFailure.rationale_short || parsed.rationale_short || "").trim(),
      failed_checks: Array.isArray(gateFailure.failed_checks) ? gateFailure.failed_checks : (Array.isArray(runtime.failed_checks) ? runtime.failed_checks : (Array.isArray(parsed.failed_checks) ? parsed.failed_checks : [])),
      missing_information: Array.isArray(gateFailure.missing_information) ? gateFailure.missing_information : (Array.isArray(parsed.missing_information) ? parsed.missing_information : []),
      missing_coverage: Array.isArray(gateFailure.missing_coverage) ? gateFailure.missing_coverage : (Array.isArray(parsed.missing_coverage) ? parsed.missing_coverage : []),
      invalid_state: Array.isArray(gateFailure.invalid_state) ? gateFailure.invalid_state : (Array.isArray(parsed.invalid_state) ? parsed.invalid_state : []),
      affected_state: Array.isArray(gateFailure.affected_state) ? gateFailure.affected_state : (Array.isArray(parsed.affected_state) ? parsed.affected_state : []),
      affected_nodes: Array.isArray(gateFailure.affected_nodes) ? gateFailure.affected_nodes : (Array.isArray(runtime.affected_nodes) ? runtime.affected_nodes : (Array.isArray(parsed.affected_nodes) ? parsed.affected_nodes : [])),
      recommended_target: String(gateFailure.recommended_target || runtime.recommended_target || parsed.recommended_target || "").trim(),
      failure_class: String(gateFailure.failure_class || runtime.failure_class || parsed.failure_class || "business_stop"),
      debug: { current_id: debug.current_id, phase: debug.phase, execution_mechanism: debug.execution_mechanism, context_breakdown: debug.context_breakdown, input_context: debug.input?.context || {}, runtime: { state_before: runtime.state_before || {}, state_updates: runtime.state_updates || {}, state_after: runtime.state_after || {}, allowed_routes: runtime.allowed_routes || [], selected_route_key: runtime.selected_route_key || null, next_id: runtime.next_id || null } },
    };
  }
  return null;
}

function uiUk() { return String(state.interactionContract?.locale || "uk-UA").toLowerCase().startsWith("uk"); }
function uiText(uk,en) { return en; }
function humanGateRouteLabel(key,target) {
  if (key === "on_pass") return uiText("Approve — criterion passed","Approve — criterion passed");
  if (key === "on_fail") return uiText("Needs correction — criterion failed","Needs correction — criterion failed");
  return humanReadableNodeLabel(target);
}

function humanDecisionAnswerLabel(value, target, current) {
  const key=String(value || "");
  const answer=current?.on_answer?.[key];
  const updates=answer?.update_state && typeof answer.update_state === "object" ? answer.update_state : {};
  const preferredKeys=[
    "implementation_change_analyst_review_status",
    "implementation_change_final_status",
    "decision",
    "status",
    "outcome",
    "result"
  ];
  for (const k of preferredKeys) {
    const v=updates[k];
    if (typeof v === "string" && v.trim()) return systemNodeLabel(v);
  }
  const cleaned=key.replace(/^(impl|implementation|analyst|review|decision)_+/i,"");
  if (cleaned) return systemNodeLabel(cleaned);
  return systemNodeLabel(target);
}
function choiceTargetTooltip(target) {
  const id=String(target || "");
  const item=[...(state.source?.nodes||[]), ...(state.source?.gates||[])].find(x=>String(x?.id||"")===id);
  if (!item) return id;
  const parts=[];
  if (item.title) parts.push(String(item.title));
  if (item.purpose && String(item.purpose)!==String(item.title||"")) parts.push(String(item.purpose));
  if (item.description) parts.push(String(item.description));
  if (id) parts.push(id);
  return parts.filter(Boolean).join("\n\n");
}
function systemNodeLabel(target) {
  const id=String(target || "");
  if (!id || id === "stop_target") return "Stop process";
  return id.replace(/^[A-Z]+_/,"").replace(/_/g," ").toLowerCase().replace(/\b\w/g,c=>c.toUpperCase());
}
function formatFailedCheck(x) {
  if (typeof x === "string") return x;
  if (x && typeof x === "object") return String(x.summary || x.check_id || JSON.stringify(x));
  return String(x || "");
}

function buildLiveChoiceContext(currentId, live) {
  if (!live?.await_analyst || !Array.isArray(live.routes) || !live.routes.length) return null;
  let routes=live.routes.filter(r=>r && r.key && r.target);
  if (!routes.length) return null;
  const current=[...(state.source?.nodes||[]), ...(state.source?.gates||[])].find(item=>item?.id===currentId) || null;
  const canonicalEnumKeys=(current?.answer_type === "enum" && current?.on_answer && typeof current.on_answer === "object")
    ? new Set(Object.keys(current.on_answer).filter(k=>!["next","normalize","update_state","state_updates","analysis","transform","interpret","interpretation","bindings","outputs","result","results"].includes(k)))
    : null;
  if (canonicalEnumKeys?.size) {
    const canonicalRoutes=routes.filter(r=>canonicalEnumKeys.has(String(r.key)));
    if (canonicalRoutes.length) routes=canonicalRoutes;
  }
  const directRuntime = live.llm_call_skipped && ["declared-human-input","unmatched-human-input"].includes(live.debug?.runtime?.reason);
  const fixedDeclared = Array.isArray(current?.allowed_values) && current.allowed_values.length;
  const dynamicRecovery = String(current?.action || "").toUpperCase().includes("VALIDATION_FAILURE") || String(current?.purpose || "").toLowerCase().includes("validation");
  const humanGate = directRuntime && String(current?.trust_class || "").toLowerCase()==="human_decision";
  const ordinaryFreeText = ["free_text","text","string"].includes(String(current?.answer_type || "").toLowerCase());
  if (ordinaryFreeText && !fixedDeclared && !dynamicRecovery && !humanGate) return null;
  if (!directRuntime && !fixedDeclared && !dynamicRecovery) return null;

  const failure = dynamicRecovery ? latestFailedGateEvidence(currentId) : null;
  let recommended = failure?.recommended_target || "";
  if (!recommended && Array.isArray(failure?.affected_nodes) && failure.affected_nodes.length) {
    recommended = routes.find(r=>failure.affected_nodes.includes(r.target))?.target || "";
  }
  const enumHumanDecision = directRuntime && String(current?.type || "").toLowerCase() === "human_decision" && current?.answer_type === "enum";
  let options=routes.map(route=>({
    value:String(route.key),
    target:String(route.target),
    label:humanGate
      ? humanGateRouteLabel(String(route.key),String(route.target))
      : (enumHumanDecision ? humanDecisionAnswerLabel(String(route.key), String(route.target), current) : systemNodeLabel(route.target)),
    tooltip:choiceTargetTooltip(String(route.target)),
    recommended:String(route.target)===recommended
  }));
  // In recovery, when evidence justifies one target, make it the primary analyst action.
  // Other graph routes stay accessible only when no recommendation is grounded.
  if (dynamicRecovery && recommended) {
    const primary=options.find(o=>o.target===recommended);
    if (primary) options=[primary];
  }
  let summary=uiText("Choose one of the available actions, or type a response manually.","Choose one of the available actions, or type a response manually.");
  if (humanGate) {
    const condition=String(current?.condition || "").trim();
    summary=uiText(`Analyst decision for ${currentId}${condition?`\n\nCriterion: ${condition}`:""}\n\nApprove if it passes. Otherwise choose “Needs correction” and describe what is wrong.`, `Analyst decision for ${currentId}${condition?`\n\nCriterion: ${condition}`:""}\n\nApprove if it passes. Otherwise choose “Needs correction” and describe what is wrong.`);
  }
  if (dynamicRecovery) {
    const technical = ["technical_stop","contract_unsatisfiable_by_model"].includes(String(failure?.failure_class||""));
    const reason=failure?.explanation || uiText("The previous validation step did not pass.","The previous validation step did not pass.");
    const checks=(failure?.failed_checks||[]).map(formatFailedCheck).filter(Boolean);
    const exact=Boolean(checks.length || failure?.affected_nodes?.length || failure?.affected_state?.length || failure?.missing_coverage?.length || failure?.missing_information?.length || recommended);
    summary=technical
      ? uiText(`Technical recovery\n\nBusiness data was not rejected. Stop reason: ${reason}`,`Technical recovery\n\nBusiness data was not rejected. Stop reason: ${reason}`)
      : uiText(`Validation recovery\n\nWhy execution stopped: ${reason}`,`Validation recovery\n\nWhy execution stopped: ${reason}`);
    if (failure?.gate_id) summary += uiText(`\nFailed gate: ${failure.gate_id}`,`\nFailed gate: ${failure.gate_id}`);
    if (checks.length) summary += uiText(`\nFailed checks: ${checks.join("; ")}`,`\nFailed checks: ${checks.join("; ")}`);
    if (failure?.missing_coverage?.length) summary += uiText(`\nMissing coverage: ${failure.missing_coverage.join(", ")}`,`\nMissing coverage: ${failure.missing_coverage.join(", ")}`);
    if (failure?.missing_information?.length) summary += uiText(`\nMissing information: ${failure.missing_information.map(x=>x?.needed||x?.path||x).join(", ")}`,`\nMissing information: ${failure.missing_information.map(x=>x?.needed||x?.path||x).join(", ")}`);
    if (recommended) summary += uiText(`\nRecommended recovery point: ${systemNodeLabel(recommended)} (${recommended})`,`\nRecommended recovery point: ${systemNodeLabel(recommended)} (${recommended})`);
    else if (!exact) summary += uiText(`\nRecommended recovery point unavailable: validator evidence is not specific enough, so the editor will not guess.`,`\nRecommended recovery point unavailable: validator evidence is not specific enough, so the editor will not guess.`);
  }
  return { currentId, summary, options, recovery: dynamicRecovery, humanGate, humanGateFailure: humanGate, failure, diagnosis: state.liveRecoveryDiagnoses?.[currentId] || null };
}

async function diagnoseLiveRecovery(ctx) {
  if (!ctx?.recovery || state.liveBusy) return;
  state.liveBusy=true; renderLiveRun();
  try {
    const data=await request("/api/recovery-diagnose", { session_id: liveSessionId, evidence: ctx.failure || {}, choices: ctx.options || [] });
    const diagnosis=data.diagnosis || null;
    if (!state.liveRecoveryDiagnoses) state.liveRecoveryDiagnoses={};
    state.liveRecoveryDiagnoses[ctx.currentId]=diagnosis;
    if (data.usage) accumulateLiveUsage(data.usage);
    if (diagnosis?.recommended_recovery_target) {
      ctx.options.forEach(o=>o.recommended=(o.target===diagnosis.recommended_recovery_target));
    }
    state.liveChoiceContext=buildLiveChoiceContext(ctx.currentId,{await_analyst:true,routes:ctx.options.map(o=>({key:o.value,target:o.target})),llm_call_skipped:true,debug:{runtime:{reason:"unmatched-human-input"}}}) || ctx;
  } catch(error) { appendLiveMessage("system",`Recovery analysis error: ${error.message}`,ctx.currentId); }
  finally { state.liveBusy=false; render(); renderLiveRun(); }
}

async function rerunFailedValidation(ctx) {
  const gate=ctx?.failure?.gate_id; if (!gate || state.liveBusy) return;
  state.liveBusy=true; state.liveAwaitingInput=false; renderLiveRun();
  try {
    state.livePath.push(gate);
    const result=await executeLiveElement(gate,"","enter",[]);
    if (!result.waiting && result.nextId && !state.liveStopRequested) await advanceLiveUntilInput();
  } catch(error) { state.liveAwaitingInput=true; appendLiveMessage("system",`Validation retry error: ${error.message}`,gate); }
  finally { state.liveBusy=false; render(); renderLiveRun(); }
}



function recoveryTargetSupportsClarification(targetId) {
  const record=[...(state.source?.nodes||[]), ...(state.source?.gates||[])].find(item=>item?.id===targetId) || null;
  if (!record || targetId?.startsWith("G_")) return false;
  const action=String(record.action || "").toUpperCase();
  if (action === "DOCUMENT.GENERATE" || action.includes("DETERMINISTIC")) return false;
  const explicitHuman = Boolean(record.question || record.answer_type || (Array.isArray(record.allowed_values) && record.allowed_values.length) || action.includes("HUMAN"));
  return !explicitHuman;
}

function openRecoveryClarificationDialog(option) {
  if (!option || state.liveBusy || !state.liveAwaitingInput) return;
  state.pendingRecoveryClarification=option;
  const modal=document.querySelector("#recovery-clarification-modal");
  const subtitle=document.querySelector("#recovery-clarification-subtitle");
  const input=document.querySelector("#recovery-clarification-input");
  const chain=document.querySelector("#recovery-clarification-scope-chain");
  if (!modal || !input) return;
  if (subtitle) subtitle.textContent=`${systemNodeLabel(option.target)} (${option.target})`;
  input.value="";
  if (chain) chain.checked=true;
  modal.hidden=false; modal.setAttribute("aria-hidden","false"); document.body.style.overflow="hidden";
  setTimeout(()=>input.focus(),0);
}
function closeRecoveryClarificationDialog() {
  const modal=document.querySelector("#recovery-clarification-modal"); if (!modal) return;
  modal.hidden=true; modal.setAttribute("aria-hidden","true"); document.body.style.overflow=""; state.pendingRecoveryClarification=null;
}
async function confirmRecoveryTransition(useClarification) {
  const option=state.pendingRecoveryClarification;
  if (!option || state.liveBusy || !state.liveAwaitingInput) return;
  const input=document.querySelector("#recovery-clarification-input");
  const clean=String(input?.value || "").trim();
  if (useClarification && !clean) { input?.focus(); return; }
  if (useClarification) {
    const scope=document.querySelector('input[name="recovery-clarification-scope"]:checked')?.value || "chain";
    state.liveAnalystOverride={ target:String(option.target), text:clean, scope, active:false };
  } else state.liveAnalystOverride=null;
  closeRecoveryClarificationDialog();
  await submitLiveInput(option.value, [], option.label || option.value);
}

function renderLiveChoicePanel() {
  const panel=document.querySelector("#live-choice-panel");
  if (!panel) return;
  panel.innerHTML="";
  const ctx=state.liveChoiceContext;
  if (!ctx || !state.liveAwaitingInput || ctx.currentId !== state.liveCurrentId || !ctx.options?.length) { panel.hidden=true; return; }
  panel.hidden=false;
  const summary=document.createElement("div"); summary.className="live-choice-summary"; summary.textContent=ctx.summary || uiText("Choose an option:","Choose an option:"); panel.append(summary);
  if (ctx.recovery) {
    const diagnosis=state.liveRecoveryDiagnoses?.[ctx.currentId] || ctx.diagnosis;
    const diag=document.createElement("div"); diag.className="live-recovery-diagnosis";
    if (diagnosis) {
      const title=document.createElement("strong"); title.textContent=diagnosis.diagnosis_status === "identified" ? uiText("Model diagnosis","Model diagnosis") : uiText("Model diagnosis: evidence is insufficient","Model diagnosis: evidence is insufficient"); diag.append(title);
      const text=document.createElement("div"); text.textContent=diagnosis.analyst_explanation || diagnosis.summary || ""; diag.append(text);
      if (diagnosis.failed_checks?.length) { const x=document.createElement("div"); x.textContent=uiText(`Failed checks: ${diagnosis.failed_checks.join(", ")}`,`Failed checks: ${diagnosis.failed_checks.join(", ")}`); diag.append(x); }
      if (diagnosis.missing_evidence?.length) { const x=document.createElement("div"); x.textContent=uiText(`Missing evidence: ${diagnosis.missing_evidence.join(", ")}`,`Missing evidence: ${diagnosis.missing_evidence.join(", ")}`); diag.append(x); }
      if (diagnosis.recommended_recovery_target) { const x=document.createElement("div"); x.textContent=uiText(`Recommended: ${systemNodeLabel(diagnosis.recommended_recovery_target)} (${diagnosis.recommended_recovery_target}), confidence: ${diagnosis.recommendation_confidence}`,`Recommended: ${systemNodeLabel(diagnosis.recommended_recovery_target)} (${diagnosis.recommended_recovery_target}), confidence: ${diagnosis.recommendation_confidence}`); diag.append(x); }
    } else {
      const text=document.createElement("div"); text.textContent=uiText("If the recorded validator evidence is not specific enough, the configured model can explain what is known, what evidence is missing, and whether a recovery target can be justified.","If the recorded validator evidence is not specific enough, the configured model can explain what is known, what evidence is missing, and whether a recovery target can be justified."); diag.append(text);
    }
    const actions=document.createElement("div"); actions.className="live-recovery-actions";
    const diagnose=document.createElement("button"); diagnose.type="button"; diagnose.textContent=diagnosis?uiText("Analyze again with model","Analyze again with model"):uiText("Analyze failure with model","Analyze failure with model"); diagnose.disabled=state.liveBusy; diagnose.addEventListener("click",()=>diagnoseLiveRecovery(ctx)); actions.append(diagnose);
    if (ctx.failure?.gate_id) { const rerun=document.createElement("button"); rerun.type="button"; rerun.textContent=uiText("Re-run validation","Re-run validation"); rerun.disabled=state.liveBusy; rerun.addEventListener("click",()=>rerunFailedValidation(ctx)); actions.append(rerun); }
    diag.append(actions); panel.append(diag);
  }
  const grid=document.createElement("div"); grid.className="live-choice-grid";
  for (const option of ctx.options) {
    const button=document.createElement("button"); button.type="button"; button.className="live-choice-button"+(option.recommended?" recommended":"");
    if (option.tooltip) { button.title=option.tooltip; button.setAttribute("aria-label", `${option.label}. ${option.tooltip.replace(/\n+/g, " ")}`); }
    if (option.recommended) { const badge=document.createElement("span"); badge.className="live-choice-badge"; badge.textContent=uiText("Recommended","Recommended"); button.append(badge); }
    const label=document.createElement("span"); label.className="choice-label"; label.textContent=option.label; button.append(label);
    const id=document.createElement("span"); id.className="choice-id"; id.textContent=option.target || option.value; button.append(id);
    button.addEventListener("click", async ()=>{
      if (state.liveBusy || !state.liveAwaitingInput) return;
      if ((ctx.recovery || (ctx.humanGate && option.value === "on_fail")) && recoveryTargetSupportsClarification(option.target)) openRecoveryClarificationDialog(option);
      else await submitLiveInput(option.value, [], option.label || option.value);
    });
    grid.append(button);
  }
  panel.append(grid);
  if (ctx.humanGate) {
    const failOption=(ctx.options||[]).find(x=>x.value === "on_fail");
    if (failOption) {
      const other=document.createElement("div"); other.className="live-gate-other";
      const title=document.createElement("strong"); title.textContent=uiText("Other / clarification","Other / clarification"); other.append(title);
      const hint=document.createElement("div"); hint.className="live-gate-other-hint"; hint.textContent=uiText("If the prepared choices do not describe the issue, explain what does not satisfy the criterion. It will be passed as repair context.","If the prepared choices do not describe the issue, explain what does not satisfy the criterion. It will be passed as repair context."); other.append(hint);
      const textarea=document.createElement("textarea"); textarea.rows=4; textarea.placeholder=uiText("Describe what is wrong or missing…","Describe what is wrong or missing…"); other.append(textarea);
      const actions=document.createElement("div"); actions.className="live-gate-other-actions";
      const send=document.createElement("button"); send.type="button"; send.textContent=uiText("Submit clarification and repair","Submit clarification and repair");
      send.addEventListener("click", async ()=>{
        const clean=String(textarea.value||"").trim();
        if (!clean || state.liveBusy || !state.liveAwaitingInput) { textarea.focus(); return; }
        state.liveAnalystOverride={target:String(failOption.target||""),text:clean,scope:"chain",active:false};
        await submitLiveInput(failOption.value, [], clean);
      });
      actions.append(send); other.append(actions); panel.append(other);
    }
  }
}

function liveStateJson() { return JSON.stringify(state.liveState || {}, null, 2); }
function openLiveStateModal() {
  const modal=document.querySelector("#live-state-modal"), pre=document.querySelector("#live-state-json"), status=document.querySelector("#live-state-copy-status");
  if (!modal || !pre) return;
  pre.textContent=liveStateJson();
  if (status) status.textContent="";
  modal.hidden=false; modal.setAttribute("aria-hidden","false"); document.body.style.overflow="hidden";
}
function closeLiveStateModal() {
  const modal=document.querySelector("#live-state-modal"); if (!modal) return;
  modal.hidden=true; modal.setAttribute("aria-hidden","true"); document.body.style.overflow="";
}
async function copyLiveStateJson() {
  const text=liveStateJson(), status=document.querySelector("#live-state-copy-status");
  try {
    if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
    else { const area=document.createElement("textarea"); area.value=text; area.style.position="fixed"; area.style.opacity="0"; document.body.append(area); area.select(); document.execCommand("copy"); area.remove(); }
    if (status) status.textContent="Copied to clipboard.";
  } catch (error) { if (status) status.textContent=`Copy failed: ${error.message}`; }
}
function downloadLiveStateJson() {
  const blob=new Blob([liveStateJson()+"\n"], {type:"application/json;charset=utf-8"});
  const url=URL.createObjectURL(blob), link=document.createElement("a");
  const node=(state.liveCurrentId || "runtime").replace(/[^A-Za-z0-9._-]+/g,"_");
  link.href=url; link.download=`ordo-runtime-state-${node}.json`; document.body.append(link); link.click(); link.remove();
  setTimeout(()=>URL.revokeObjectURL(url), 0);
}

function renderLiveAttachmentQueue() {
  const wrap=document.querySelector("#live-attachments"); if (!wrap) return; wrap.innerHTML="";
  const items=state.liveAttachments || []; wrap.hidden=!items.length;
  items.forEach((item,index)=>{
    const chip=document.createElement("span"); chip.className="live-attachment-chip";
    const name=document.createElement("span"); name.className="live-attachment-chip-name"; name.textContent=item.name; name.title=item.name;
    const size=document.createElement("span"); size.className="live-attachment-chip-size"; size.textContent=formatAttachmentSize(item.size);
    const remove=document.createElement("button"); remove.type="button"; remove.className="live-attachment-remove"; remove.textContent="×"; remove.title=`Remove ${item.name}`; remove.disabled=state.liveBusy;
    remove.addEventListener("click",()=>{ state.liveAttachments.splice(index,1); renderLiveRun(); });
    chip.append(name,size,remove); wrap.append(chip);
  });
}
async function addLiveAttachments(fileList) {
  const files=[...(fileList||[])]; if (!files.length) return;
  const maxFiles=8, maxEach=10*1024*1024, maxTotal=24*1024*1024;
  if ((state.liveAttachments?.length||0)+files.length > maxFiles) throw new Error(`Attach at most ${maxFiles} files to one message.`);
  let total=(state.liveAttachments||[]).reduce((sum,x)=>sum+Number(x.size||0),0);
  for (const file of files) {
    if (file.size > maxEach) throw new Error(`${file.name} is larger than 10 MB.`); total += file.size; if (total > maxTotal) throw new Error("Total attachment size must not exceed 24 MB.");
    const bytes=new Uint8Array(await file.arrayBuffer());
    state.liveAttachments.push({ name:file.name, type:file.type || "application/octet-stream", size:file.size, data_base64:bytesToBase64(bytes) });
  }
  renderLiveRun();
}
function providerLabel(provider) {
  return provider === "mlx" ? "Local LLM" : provider === "custom" ? "OpenAI-compatible" : "OpenAI";
}
function defaultProviderBaseUrl(provider) {
  return provider === "mlx" ? "http://127.0.0.1:8080/v1" : provider === "custom" ? "http://ml03.ligazakon.net:8555/v1" : "https://api.openai.com/v1";
}
let activeLiveSetting = null;
function liveSettingLocked() { return state.liveRunning || state.liveBusy; }
function liveApiStatusText() {
  if (state.liveConfig.provider === "mlx") return "local · key not required";
  if (state.liveConfig.shared_key) return "shared server key";
  if (state.liveConfig.personal_key) return "personal session key";
  return state.liveConfig.provider === "custom" ? "optional / not configured" : "not configured";
}
function syncModelSettingsIndicator() {
  const button=document.querySelector("#header-model-settings"); if(!button)return;
  const configured=!!state.liveConfig?.enabled;
  button.classList.toggle("model-unconfigured",!configured);
  button.classList.toggle("model-configured",configured);
  button.title=configured ? `${providerLabel(state.liveConfig.provider)} · ${state.liveConfig.model || "configured"}` : "Model is not configured";
}
function closeLiveSettingModal() {
  activeLiveSetting = null;
  const modal=document.querySelector("#live-setting-modal");
  if (modal) { modal.hidden=true; modal.setAttribute("aria-hidden","true"); }
}
function liveSettingField(label, control) {
  const wrap=document.createElement("label"); wrap.className="live-setting-field";
  const title=document.createElement("span"); title.textContent=label; wrap.append(title,control); return wrap;
}
function makeLiveSettingSelect(values, current) {
  const select=document.createElement("select"); select.id="live-setting-control";
  for (const [value,label] of values) { const option=document.createElement("option"); option.value=value; option.textContent=label; select.append(option); }
  if (current != null) select.value=current; return select;
}
async function discoverLiveModels(provider, baseUrl, apiKey="", {quiet=false}={}) {
  try {
    const data=await request("/api/provider-models", {session_id:liveSessionId, provider, base_url:baseUrl, api_key:apiKey});
    return {base_url:data.base_url, models:data.models || []};
  } catch (error) { if (!quiet) alert(`Could not load provider models: ${error.message}`); return null; }
}
async function openLiveSettingModal(setting="connection") {
  if (liveSettingLocked()) { alert("Reset the current Run before changing LLM connection settings."); return; }
  activeLiveSetting="connection";
  const modal=document.querySelector("#live-setting-modal"), title=document.querySelector("#live-setting-title"), subtitle=document.querySelector("#live-setting-subtitle"), body=document.querySelector("#live-setting-body"), refresh=document.querySelector("#live-setting-refresh");
  body.innerHTML=""; title.textContent="Configure LLM connection";
  subtitle.textContent="Choose the provider first, then configure its endpoint, model and credentials.";

  const provider=document.createElement("select"); provider.id="live-provider-control";
  for (const [value,label] of [["openai","OpenAI"],["mlx","Local LLM"],["custom","OpenAI-compatible"]]) { const o=document.createElement("option"); o.value=value; o.textContent=label; provider.append(o); }
  provider.value=state.liveConfig.provider || "openai";

  const base=document.createElement("input"); base.id="live-base-url-control"; base.type="url"; base.spellcheck=false;
  const model=document.createElement("select"); model.id="live-model-control";
  const key=document.createElement("input"); key.id="live-api-key-control"; key.type="password"; key.autocomplete="off"; key.spellcheck=false;
  const keyField=liveSettingField("API key",key); keyField.id="live-api-key-field";

  const probe=document.createElement("button"); probe.type="button"; probe.id="live-capability-probe"; probe.textContent="Probe JSON schema capability";
  const probeStatus=document.createElement("div"); probeStatus.id="live-capability-probe-status"; probeStatus.className="hint";
  const probeWrap=document.createElement("div"); probeWrap.className="setting-field"; probeWrap.append(probe,probeStatus);
  const fallbackPolicy=document.createElement("select"); fallbackPolicy.id="live-semantic-fallback-policy";
  for (const [value,label] of [["automatic_safe","Automatic safe fallback"],["ask","Ask before fallback"],["disabled","Disabled"]]) { const o=document.createElement("option"); o.value=value; o.textContent=label; fallbackPolicy.append(o); }
  fallbackPolicy.value=state.liveConfig.semantic_fallback_policy || "automatic_safe";
  body.append(liveSettingField("Provider",provider), liveSettingField("Base URL",base), liveSettingField("Model",model), keyField, probeWrap, liveSettingField("Semantic fallback",fallbackPolicy));
  refresh.hidden=false; refresh.textContent="Refresh models";
  probe.addEventListener("click",async()=>{
    probe.disabled=true; probeStatus.textContent="Probing…";
    try {
      const p=provider.value; const baseUrl=p==="openai"?"https://api.openai.com/v1":(base.value.trim()||defaultProviderBaseUrl(p)); const modelName=model.value;
      if (!modelName) throw new Error("Select a model first.");
      await request("/api/live-config",{session_id:liveSessionId,provider:p,base_url:baseUrl,model:modelName,api_key:p==="openai"?(key?.value.trim()||""):""});
      const data=await request("/api/provider-capability-probe",{session_id:liveSessionId});
      state.liveConfig={...state.liveConfig,provider:p,base_url:baseUrl,model:modelName,capability_profile:data.capability_profile||null,structured_output_mode:data.structured_output_mode||"auto"};
      probeStatus.textContent=data.capability_profile?.supports_json_schema ? "Recorded: strict json_schema supported" : "Recorded: json_schema unsupported; json_object will be used";
    } catch(error) { probeStatus.textContent=`Probe failed: ${error.message}`; } finally { probe.disabled=false; }
  });

  function fillModels(models,current) {
    model.innerHTML="";
    const list=Array.isArray(models) ? models : [];
    for (const m of list) { const o=document.createElement("option"); o.value=m; o.textContent=m; model.append(o); }
    if (!list.length) { const o=document.createElement("option"); o.value=""; o.textContent="Refresh models"; model.append(o); }
    model.value=list.includes(current) ? current : (list[0] || "");
  }
  async function applyProviderUI({discover=false}={}) {
    const p=provider.value;
    if (p === "openai") {
      base.value="https://api.openai.com/v1"; base.disabled=true;
      keyField.hidden=false; key.disabled=false; key.placeholder=state.liveConfig.personal_key && state.liveConfig.provider === "openai" ? "Configured — leave blank to keep" : "Enter OpenAI API key";
      fillModels(state.liveConfig.provider === "openai" ? state.liveConfig.models : ["gpt-5.6-sol","gpt-5.6-terra","gpt-5.6-luna"], state.liveConfig.provider === "openai" ? state.liveConfig.model : "");
    } else {
      base.disabled=false;
      const same=state.liveConfig.provider === p;
      base.value=same && state.liveConfig.base_url ? state.liveConfig.base_url : defaultProviderBaseUrl(p);
      keyField.hidden=true; key.value=""; key.disabled=true;
      fillModels(same ? state.liveConfig.models : [], same ? state.liveConfig.model : "");
      if (discover) await refreshLiveSettingModels();
    }
  }
  provider.addEventListener("change",()=>applyProviderUI({discover:false}));
  await applyProviderUI({discover:false});
  modal.hidden=false; modal.setAttribute("aria-hidden","false"); provider.focus();
}
async function refreshLiveSettingModels() {
  if (activeLiveSetting !== "connection") return;
  const provider=document.querySelector("#live-provider-control"), base=document.querySelector("#live-base-url-control"), model=document.querySelector("#live-model-control"), key=document.querySelector("#live-api-key-control"), button=document.querySelector("#live-setting-refresh");
  if (!provider || !base || !model) return;
  button.disabled=true;
  try {
    const p=provider.value;
    const baseUrl=p === "openai" ? "https://api.openai.com/v1" : (base.value.trim() || defaultProviderBaseUrl(p));
    const discovered=await discoverLiveModels(p,baseUrl,p === "openai" ? (key?.value.trim() || "") : ""); if (!discovered) return;
    base.value=discovered.base_url;
    model.innerHTML=""; for (const m of discovered.models) { const o=document.createElement("option"); o.value=m; o.textContent=m; model.append(o); }
    const old=state.liveConfig.provider === p ? state.liveConfig.model : ""; model.value=discovered.models.includes(old) ? old : (discovered.models[0] || "");
  } finally { button.disabled=false; }
}
async function saveLiveSetting() {
  if (activeLiveSetting !== "connection" || liveSettingLocked()) return;
  const provider=document.querySelector("#live-provider-control"), base=document.querySelector("#live-base-url-control"), model=document.querySelector("#live-model-control"), key=document.querySelector("#live-api-key-control"), save=document.querySelector("#live-setting-save");
  if (!provider || !base || !model) return;
  save.disabled=true;
  try {
    const p=provider.value;
    const baseUrl=p === "openai" ? "https://api.openai.com/v1" : (base.value.trim() || defaultProviderBaseUrl(p));
    const modelName=model.value;
    const apiKey=p === "openai" ? (key?.value.trim() || "") : "";
    if (!modelName) { alert("Select a model. Use Refresh models if the list is empty."); return; }
    const data=await request("/api/live-config", {session_id:liveSessionId,provider:p,base_url:baseUrl,model:modelName,api_key:apiKey});
    const fallbackPolicy=document.querySelector("#live-semantic-fallback-policy")?.value || "automatic_safe";
    state.liveConfig={...state.liveConfig,...(data.live || {}),semantic_fallback_policy:fallbackPolicy}; closeLiveSettingModal(); renderLiveRun(); if (!document.querySelector("#settings-overview-modal")?.hidden) renderSettingsOverview();
  } catch (error) { alert(`Could not apply LLM connection settings: ${error.message}`); }
  finally { save.disabled=false; }
}
function scheduleLiveTreeAutoFocus() {
  if (state.panelTab !== "run" || !state.liveRunning || !state.liveCurrentId) return;
  if (state.liveTreeAutoFocusId === state.liveCurrentId) return;
  const id = state.liveCurrentId;
  state.liveTreeAutoFocusId = id;
  requestAnimationFrame(() => {
    const pos = state.positions?.[id];
    if (!pos || state.panelTab !== "run" || state.liveCurrentId !== id) return;
    workspace.scrollTo({
      left: Math.max(0, pos.x + nodeSize(id).width / 2 - workspace.clientWidth / 2),
      top: Math.max(0, pos.y + nodeHeight(id) / 2 - workspace.clientHeight / 2),
      behavior: "smooth",
    });
  });
}

function modelActivityText(id) {
  const raw=String(id || "").replace(/^[A-Z]+_/,"").replace(/_MODEL$/," ").replace(/_/g," ").trim().toLowerCase();
  const phrase=raw ? raw.replace(/\b\w/g,c=>c.toUpperCase()) : "Current Playbook Step";
  return `Working on ${phrase}…`;
}

function renderLiveRun() {
  syncModelSettingsIndicator();
  renderChatControlBar();
  const apiReady = !!state.liveConfig.enabled;
  const packageReady = !!state.packageInfo && !!state.source;
  const executeCapable = packageReady && (state.packageInfo?.capabilities?.execute !== false);
  const enabled = apiReady && executeCapable;
  const tab = document.querySelector("#run-tab");
  if (tab) {
    tab.disabled = false;
    tab.title = enabled ? "Run the loaded playbook package" : "Open Live Run readiness to see what is missing";
  }
  const readiness = document.querySelector("#live-readiness");
  if (readiness) {
    const pkg = state.packageInfo;
    readiness.innerHTML = "";
    const rows = [
      ["Playbook source", packageReady ? `✓ ${pkg.filename}` : "✕ not loaded"],
      ["Source", packageReady ? (pkg.source_name || "detected") : "—"],
      ["Runtime plan", packageReady ? (() => { const sps=pkg.semantic_plan_status || {}; return sps.valid ? (sps.generated ? "✓ compiled and verified internally" : "✓ verified precompiled plan") : "✕ unavailable (inspection-only)"; })() : "—"],
      ["Provider", providerLabel(state.liveConfig.provider)],
      ["Base URL", state.liveConfig.base_url || defaultProviderBaseUrl(state.liveConfig.provider)],
      ["Model", state.liveConfig.model ? `✓ ${state.liveConfig.model}` : "✕ not selected"],
      ["API key", liveApiStatusText()],
      ["LLM connection", "Configure provider, endpoint, model and credentials", "", "connection"],
      ["Token usage", state.liveUsage.calls ? state.liveUsage.total_tokens.toLocaleString() : "—", state.liveUsage.calls ? liveUsageTooltip(state.liveUsage, state.liveUsage.calls) : ""],
      ["Run readiness", enabled ? "READY" : "NOT READY"],
    ];
    for (const [key, value, tooltip, setting] of rows) {
      const row=document.createElement("div"); row.className="live-readiness-row"; const k=document.createElement("span"); k.textContent=key;
      let v;
      if (key === "Token usage" && state.liveUsage.calls) {
        v=document.createElement("button"); v.type="button"; v.className="token-usage-badge"; v.textContent=value; v.title="Open token usage summary";
        v.addEventListener("click", () => openTokenDebugModal(buildAggregateTokenDebug()));
      } else { v=document.createElement("strong"); v.textContent=value; if (tooltip) v.title=tooltip; }
      row.append(k,v);
      if (setting) { const action=document.createElement("button"); action.type="button"; action.className="live-setting-button"; action.textContent="Configure"; action.disabled=liveSettingLocked(); action.addEventListener("click",()=>openLiveSettingModal("connection")); row.append(action); }
      readiness.append(row);
    }
  }
  const blockers = [];
  if (!packageReady) blockers.push("playbook source is not loaded");
  if (!apiReady) blockers.push("LLM provider is not configured for this Run session");
  const note = document.querySelector("#live-disabled-note");
  note.hidden = enabled;
  note.textContent = enabled ? "" : `Run is not ready: ${blockers.join("; ")}.`;
  document.querySelector("#live-controls").hidden = false;
  document.querySelector("#live-model-badge").textContent = state.liveConfig.model ? `${providerLabel(state.liveConfig.provider)} · ${state.liveConfig.model}` : providerLabel(state.liveConfig.provider);
  const configNote = document.querySelector("#live-config-note");
  if (configNote) configNote.innerHTML = 'Configure the complete LLM connection from the single <strong>Configure</strong> button above.';
  const start = document.querySelector("#live-start"), stop = document.querySelector("#live-stop"), reset = document.querySelector("#live-reset");
  start.disabled = !enabled || state.liveStopRequested || (!!state.liveOutcome && state.liveRunning);
  start.hidden = state.liveRunning;
  start.textContent = "Start dialog";
  start.title = "Start live execution";
  const pause = document.querySelector("#live-pause");
  if (pause) {
    pause.hidden = !state.liveRunning || !!state.liveOutcome;
    pause.disabled = !state.liveRunning || !!state.liveOutcome || state.liveStopRequested;
    pause.textContent = state.livePaused ? "Resume auto" : "Pause";
    pause.title = state.livePaused
      ? "Resume recorded automatic analyst answers from the current waiting node"
      : "Pause recorded automatic analyst answers; execution still advances to the next analyst question so you can answer manually";
  }
  if (stop) {
    stop.disabled = !state.liveRunning || !!state.liveOutcome || state.liveStopRequested;
    stop.textContent = state.liveStopRequested ? "Stopping…" : "Stop";
    stop.title = state.liveBusy ? "Stop after the current element finishes" : "Stop this run and keep its history";
  }
  reset.disabled = !state.liveRunning || state.liveBusy;
  const autoButton = document.querySelector("#live-auto-answers");
  const autoNote = document.querySelector("#live-auto-answers-note");
  if (autoButton) {
    autoButton.disabled = state.liveRunning || state.liveBusy;
    autoButton.textContent = state.liveAutoAnswers?.enabled ? "Auto answers ✓" : "Auto answers";
    autoButton.title = state.liveAutoAnswers?.enabled ? "Replace the replay/evidence file used for automatic analyst answers" : "Load a replay/evidence ZIP or JSON with recorded analyst responses";
  }
  if (autoNote) autoNote.textContent = state.liveAutoAnswers?.enabled ? `${state.liveAutoAnswers.filename} · ${state.liveAutoAnswers.total} recorded answers` : "";
  const replayButton=document.querySelector("#live-guided-replay");
  const replayNote=document.querySelector("#live-guided-replay-note");
  if (replayButton) { replayButton.disabled=state.liveRunning||state.liveBusy; replayButton.textContent=state.liveGuidedReplay?.enabled ? "Replay ready ✓" : "Replay to checkpoint"; replayButton.title="Load a debug/reproduction package and replay accepted model + analyst evidence until its checkpoint"; }
  if (replayNote) replayNote.textContent=state.liveGuidedReplay?.enabled ? `${state.liveGuidedReplay.filename} · → ${state.liveGuidedReplay.checkpointId} · ${state.liveGuidedReplay.totalCalls} recorded calls` : "";
  document.querySelector("#live-empty").hidden = state.liveRunning;
  document.querySelector("#live-view").hidden = !state.liveRunning;
  if (!state.liveRunning) {
    document.querySelector("#live-empty").textContent = enabled ? "Playbook is compiled, verified and ready for execution." : !packageReady ? "Load a playbook YAML/YML or ZIP source to enable execution." : !executeCapable ? "This playbook is loaded for inspection, but execution is unavailable because runtime preparation failed." : "Playbook verified. Configure an LLM provider and model above.";
    return;
  }
  const status = document.querySelector("#live-status");
  status.classList.toggle("live-status-completed", state.liveOutcome?.status === "completed");
  status.classList.toggle("live-status-halted", state.liveOutcome?.status === "halted");
  status.hidden = !state.liveOutcome;
  if (state.liveOutcome) {
    const label = state.liveOutcome.status === "completed" ? "✓ Run completed" : "⚠ Run halted";
    const reasonLabels = {terminal:"terminal outcome reached", dead_end:"non-terminal element has no outgoing route", unresolved_target:"selected route target does not resolve", missing_route:"no route was selected", user_stop:"stopped by user"};
    status.textContent = `${label} · ${reasonLabels[state.liveOutcome.reason] || state.liveOutcome.reason || "finished"}${state.liveOutcome.nodeId ? ` · ${state.liveOutcome.nodeId}` : ""}`;
  } else { status.textContent = ""; status.hidden = true; }
  const transcript = document.querySelector("#live-transcript"); transcript.innerHTML = "";
  for (const [messageIndex, item] of state.liveHistory.entries()) {
    const block = document.createElement("div"); block.className = `live-message live-${item.role}`;
    block.innerHTML = `<div class="live-message-body"></div>${(item.meta || item.usage) ? `<small></small>` : ""}`;
    const body = block.querySelector(".live-message-body");
    const text = String(item.text || "");
    const textWrap = document.createElement("div");
    textWrap.className = "live-message-text";
    textWrap.innerHTML = renderBasicMarkdown(text);
    body.append(textWrap);

    // Long transcript messages stay fully present in history/debug, but are
    // visually collapsed to keep the run chat scannable. Analyst/auto-answer
    // messages collapse earlier because they are often large evidence blocks.
    const lineCount = (text.match(/\n/g) || []).length + 1;
    // Model/runtime answers are expanded by default. Long analyst answers are
    // collapsed so evidence dumps do not dominate the transcript.
    const shouldCollapse = item.role === "analyst" && (text.length > 520 || lineCount > 6);
    if (shouldCollapse) {
      const expanded = state.liveExpandedMessages?.has(messageIndex);
      textWrap.classList.toggle("is-collapsed", !expanded);
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "live-message-toggle";
      toggle.innerHTML = expanded ? 'Show less <span aria-hidden="true">⌃</span>' : 'Show more <span aria-hidden="true">⌄</span>';
      toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
      toggle.addEventListener("click", () => {
        if (!state.liveExpandedMessages) state.liveExpandedMessages = new Set();
        if (state.liveExpandedMessages.has(messageIndex)) state.liveExpandedMessages.delete(messageIndex);
        else state.liveExpandedMessages.add(messageIndex);
        const nowExpanded = state.liveExpandedMessages.has(messageIndex);
        textWrap.classList.toggle("is-collapsed", !nowExpanded);
        toggle.innerHTML = nowExpanded ? 'Show less <span aria-hidden="true">⌃</span>' : 'Show more <span aria-hidden="true">⌄</span>';
        toggle.setAttribute("aria-expanded", nowExpanded ? "true" : "false");
      });
      body.append(toggle);
    }
    if (Array.isArray(item.attachments) && item.attachments.length) {
      const aw=document.createElement("div"); aw.className="live-message-attachments";
      for (const file of item.attachments) { const tag=document.createElement("span"); tag.className="live-message-attachment"; tag.textContent=`📎 ${file.name} · ${formatAttachmentSize(file.size)}`; tag.title=file.type || "file"; aw.append(tag); }
      body.append(aw);
    }
    if (item.artifact?.path) {
      const artifactWrap=document.createElement("div"); artifactWrap.className="live-artifact";
      const filename=item.artifact.filename || item.artifact.path.split('/').pop() || 'artifact';
      const url=liveArtifactUrl(item.artifact.path);
      if (isPreviewableTextArtifact(item.artifact.path)) {
        const card=document.createElement('div'); card.className='live-artifact-card'; card.tabIndex=0; card.setAttribute('role','button'); card.title=`Preview ${filename}`;
        card.innerHTML=`<span class="live-artifact-card-icon" aria-hidden="true">▤</span><span class="live-artifact-card-copy"><strong></strong><small></small></span><a class="live-artifact-card-download" href="#" aria-label="Download file" title="Download"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v10m0 0 4-4m-4 4-4-4M5 19h14"/></svg></a>`;
        card.querySelector('small').textContent=artifactTypeLabel(item.artifact.path);
        card.querySelector('strong').textContent=filename;
        const openPreview=()=>openArtifactPreview(item.artifact);
        card.addEventListener('click',()=>openArtifactPreview(item.artifact));
        card.addEventListener('keydown',event=>{ if(event.key==='Enter' || event.key===' '){ event.preventDefault(); openPreview(); } });
        const dl=card.querySelector('.live-artifact-card-download'); dl.href=url; dl.setAttribute('download',filename); dl.addEventListener('click',event=>event.stopPropagation());
        artifactWrap.append(card);
      } else {
        const card=document.createElement('div'); card.className='live-artifact-card live-artifact-card-download-only'; card.setAttribute('aria-label',`${filename}, download only`);
        card.innerHTML=`<span class="live-artifact-card-icon" aria-hidden="true">▤</span><span class="live-artifact-card-copy"><strong></strong><small></small></span><a class="live-artifact-card-download" href="#" aria-label="Download file" title="Download"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v10m0 0 4-4m-4 4-4-4M5 19h14"/></svg></a>`;
        card.querySelector('strong').textContent=filename;
        card.querySelector('small').textContent=artifactTypeLabel(item.artifact.path);
        const dl=card.querySelector('.live-artifact-card-download'); dl.href=url; dl.setAttribute('download',filename);
        artifactWrap.append(card);
      }
      if (item.artifact.warning_count) { const warning=document.createElement("span"); warning.className="live-artifact-warning"; warning.textContent=`Draft with validation warnings (${item.artifact.warning_count})`; artifactWrap.append(warning); }
      body.append(artifactWrap);
    }
    if (item.meta || item.usage) {
      const meta = block.querySelector("small");
      if (item.meta) { const label=document.createElement("span"); label.textContent=item.meta; meta.append(label); }
      if (item.usage) {
        const badge=document.createElement("button"); badge.type="button"; badge.className="token-usage-badge";
        badge.textContent=`tokens ${Number(item.usage.total_tokens || 0).toLocaleString()}`;
        badge.title="Open full LLM step debug";
        badge.addEventListener("click", event => { event.stopPropagation(); openTokenDebugModal(item.debug || { usage: item.usage, context_breakdown: item.context_breakdown, current_id: item.node_id }); });
        meta.append(badge);
      }
    }
    if (item.role === "assistant" || item.role === "analyst") attachChatCopyButton(block, text, item.role === "analyst" ? "right" : "left");
    transcript.append(block);
  }
  if (state.liveBusy && state.liveCurrentId && !state.liveOutcome) {
    const activity=document.createElement("div"); activity.className="live-model-activity";
    activity.textContent=modelActivityText(state.liveCurrentId); transcript.append(activity);
  }
  const input = document.querySelector("#live-input"), send = document.querySelector("#live-send"), attach=document.querySelector("#live-attach-button"), attachInput=document.querySelector("#live-attachment-input");
  input.disabled = !state.liveRunning || !!state.liveOutcome;
  const canSend=!state.liveBusy && !!state.liveCurrentId && !!state.liveAwaitingInput && !state.liveOutcome;
  if (attachInput) attachInput.disabled=!canSend; if (attach) attach.classList.toggle("disabled",!canSend);
  if (state.liveBusy) { send.disabled=false; send.type="button"; send.classList.add("is-stop"); send.title="Stop current model step"; send.setAttribute("aria-label","Stop current model step"); send.innerHTML='<span aria-hidden="true">■</span>'; }
  else { send.type="submit"; send.classList.remove("is-stop"); send.title="Send"; send.setAttribute("aria-label","Send"); send.innerHTML='<span aria-hidden="true">↑</span>'; send.disabled=!canSend || (!input.value.trim() && !(state.liveAttachments?.length)); }
  input.placeholder = state.liveOutcome ? (state.liveOutcome.status === "completed" ? "Run completed." : "Run halted.") : "Message";
  updateLiveComposerLayout();
  document.querySelector("#live-form").classList.toggle("live-input-finished", !!state.liveOutcome);
  renderLiveChoicePanel();
  renderLiveAttachmentQueue();
  scheduleLiveTreeAutoFocus();
  scheduleLiveTranscriptScroll();
}


const LIVE_SCROLL_TO_BOTTOM_THRESHOLD_PX=100;
function liveTranscriptRemainingPx(){
  const transcript=document.querySelector("#live-transcript");
  if(!transcript) return 0;
  return Math.max(0,transcript.scrollHeight-transcript.clientHeight-transcript.scrollTop);
}
function liveTranscriptCanScrollDown(){
  const transcript=document.querySelector("#live-transcript");
  if(!transcript) return false;
  return transcript.scrollHeight>transcript.clientHeight+2 && liveTranscriptRemainingPx()>=LIVE_SCROLL_TO_BOTTOM_THRESHOLD_PX;
}
function liveModelIsWorking(){
  const button=document.querySelector("#live-send");
  const activity=document.querySelector("#live-activity");
  if(button && (button.dataset.mode==="stop" || button.getAttribute("aria-label")==="Stop" || button.classList.contains("is-stop"))) return true;
  if(activity && !activity.hidden && String(activity.textContent||"").trim()) return true;
  return Boolean(document.body.classList.contains("live-model-working"));
}
function updateLiveScrollToBottomControl(){
  const transcript=document.querySelector("#live-transcript");
  const button=document.querySelector("#live-scroll-to-bottom");
  const form=document.querySelector("#live-form");
  const view=document.querySelector("#live-view");
  if(!transcript||!button||!form||!view) return;
  const visible=liveTranscriptCanScrollDown();
  const working=visible && liveModelIsWorking();
  button.hidden=!visible;
  button.dataset.state=working?"working":"idle";
  button.title=working?"Model is working — scroll to latest message":"Scroll to latest message";
  button.setAttribute("aria-label",working?"Model is working — scroll to latest message":"Scroll to latest message");
  button.style.bottom=`${Math.max(12,form.offsetHeight+12)}px`;
}
function scrollLiveTranscriptToBottom(behavior="smooth"){
  const transcript=document.querySelector("#live-transcript");
  if(!transcript) return;
  transcript.scrollTo({top:transcript.scrollHeight,behavior});
  requestAnimationFrame(updateLiveScrollToBottomControl);
}

let liveTranscriptScrollRaf = 0;
function scrollLiveLatestAboveComposer(behavior = "smooth") {
  const transcript = document.querySelector("#live-transcript");
  const latest = transcript?.lastElementChild;
  if (!transcript || !latest) return;

  // In chat workspace the transcript itself is the vertical scroll container
  // (`#inspector` has overflow:hidden). Scroll the real owner so newly appended
  // assistant/runtime messages are brought into view automatically.
  const transcriptRect = transcript.getBoundingClientRect();
  const latestRect = latest.getBoundingClientRect();
  const gap = 12;
  const visibleTop = transcriptRect.top + gap;
  const visibleBottom = transcriptRect.bottom - gap;
  const available = Math.max(0, visibleBottom - visibleTop);
  let delta = 0;

  if (latestRect.height <= available) {
    if (latestRect.bottom > visibleBottom) delta = latestRect.bottom - visibleBottom;
    else if (latestRect.top < visibleTop) delta = latestRect.top - visibleTop;
  } else if (latestRect.top < visibleTop || latestRect.bottom > visibleBottom) {
    // For a very tall latest message, show its beginning rather than its tail.
    delta = latestRect.top - visibleTop;
  }

  if (Math.abs(delta) > 1) {
    transcript.scrollTo({ top: Math.max(0, transcript.scrollTop + delta), behavior });
  }
}

function scheduleLiveTranscriptScroll() {
  if (liveTranscriptScrollRaf) cancelAnimationFrame(liveTranscriptScrollRaf);
  liveTranscriptScrollRaf = requestAnimationFrame(() => {
    liveTranscriptScrollRaf = requestAnimationFrame(() => {
      liveTranscriptScrollRaf = 0;
      scrollLiveLatestAboveComposer("smooth");
      requestAnimationFrame(updateLiveScrollToBottomControl);
    });
  });
}

function resetLiveRun() {
  state.liveRunId = ""; state.liveRunning = false; state.livePaused = false; state.liveStopRequested = false; state.liveStepAbortController = null; state.liveInterruptedNode = null; state.liveCurrentId = null; state.liveState = {}; state.liveRevision = 0; state.liveHistory = []; state.livePath = []; state.liveBusy = false; state.liveAwaitingInput = false; state.liveOutcome = null; state.liveDebugTrace = []; state.liveUsage = { input_tokens: 0, output_tokens: 0, total_tokens: 0, cached_tokens: 0, reasoning_tokens: 0, calls: 0 }; state.liveAttachments = []; state.liveExpandedMessages = new Set(); state.liveComposerExpanded = false; state.liveChoiceContext = null; state.liveRecoveryDiagnoses = {}; state.liveAnalystOverride = null; state.pendingRecoveryClarification = null; state.liveNoProgressGateFailures = {}; state.livePendingEntryMode = null;
  if (state.liveAutoAnswers) state.liveAutoAnswers.cursors = {};
  if (state.liveGuidedReplay) { state.liveGuidedReplay.active=false; state.liveGuidedReplay.callCursor=0; state.liveGuidedReplay.answerCursors={}; }
  closeArtifactPreview();
  render(); renderLiveRun();
}
function buildLiveAutoAnswers(replay, filename = "") {
  const answersByNode = {}; let total = 0;
  for (const step of replay?.steps || []) {
    const nodeId = step?.id; if (!nodeId) continue;
    for (const interaction of step?.interactions || []) {
      const answer = typeof interaction?.analyst_response === "string" ? interaction.analyst_response.trim() : "";
      if (!answer) continue;
      (answersByNode[nodeId] ||= []).push(answer); total += 1;
    }
  }
  return { enabled: total > 0, filename, answersByNode, cursors: {}, total };
}
function nextLiveAutoAnswer(nodeId) {
  const cfg = state.liveAutoAnswers;
  if (!cfg?.enabled || !nodeId) return null;
  const answers = cfg.answersByNode?.[nodeId] || [];
  const index = Number(cfg.cursors?.[nodeId] || 0);
  if (index >= answers.length) return null;
  cfg.cursors[nodeId] = index + 1;
  return answers[index];
}
function buildGuidedReplay(replay, filename="") {
  if (replay?.kind !== "debug_reproduction" && !Array.isArray(replay?.recorded_calls)) throw new Error("The file does not contain debug reproduction evidence.");
  const calls=Array.isArray(replay.recorded_calls)?replay.recorded_calls:[];
  const answersByNode=(replay.answers_by_node && typeof replay.answers_by_node === "object") ? replay.answers_by_node : {};
  const totalAnswers=Object.values(answersByNode).reduce((n,v)=>n+(Array.isArray(v)?v.length:0),0);
  const checkpointId=String(replay.suggested_checkpoint || "").trim();
  if (!calls.length) throw new Error("No recorded runtime/model calls were found.");
  if (!checkpointId) throw new Error("No suggested checkpoint was found in the debug run.");
  return {enabled:true,active:false,filename,checkpointId,recordedCalls:calls,callCursor:0,answersByNode,answerCursors:{},totalCalls:calls.length,totalAnswers,sourceRunId:String(replay.source_run_id||""),sourceSha256:String(replay.source_sha256||""),recordedAgainst:replay.recorded_against||{}};
}
function nextGuidedReplayAnswer(nodeId) {
  const cfg=state.liveGuidedReplay;
  if (!cfg?.active) return null;
  const values=Array.isArray(cfg.answersByNode?.[nodeId])?cfg.answersByNode[nodeId]:[];
  const i=Number(cfg.answerCursors?.[nodeId]||0);
  if (i>=values.length) return null;
  cfg.answerCursors[nodeId]=i+1;
  return values[i];
}
function nextGuidedReplayCall(nodeId, phase) {
  const cfg=state.liveGuidedReplay;
  if (!cfg?.active) return null;
  for (let i=Number(cfg.callCursor||0); i<cfg.recordedCalls.length; i++) {
    const call=cfg.recordedCalls[i];
    if (String(call?.current_id||"")===String(nodeId||"") && String(call?.phase||"")===String(phase||"")) {
      cfg.callCursor=i+1;
      return call;
    }
  }
  return null;
}
function maybeExitGuidedReplayAtCheckpoint() {
  const cfg=state.liveGuidedReplay;
  if (!cfg?.active || !state.liveCurrentId || state.liveCurrentId!==cfg.checkpointId) return false;
  cfg.active=false;
  state.livePaused=true;
  appendLiveMessage("system", `Replay checkpoint reached: ${cfg.checkpointId}. Recorded model/analyst playback is now OFF; subsequent execution is live.`, "replay → live");
  return true;
}

async function startLiveRun() {
  if (!state.liveConfig.enabled || !state.packageInfo || !state.source) return;
  if (state.liveRunning) return;
  const replayWasEnabled=Boolean(state.liveGuidedReplay?.enabled);
  resetLiveRun(); state.liveRunId = crypto.randomUUID ? crypto.randomUUID() : `run-${Date.now()}-${Math.random().toString(16).slice(2)}`; state.liveRunning = true; state.livePaused = false; state.liveStopRequested = false; state.liveCurrentId = entryNodeId(); state.liveAwaitingInput = false;
  if (replayWasEnabled && state.liveGuidedReplay) { state.liveGuidedReplay.active=true; state.liveGuidedReplay.callCursor=0; state.liveGuidedReplay.answerCursors={}; }
  if (!state.liveCurrentId) { resetLiveRun(); alert("Could not determine playbook entry node."); return; }
  state.livePath = [state.liveCurrentId]; showPanelTab("run"); state.liveBusy = true; render(); renderLiveRun();
  try { await advanceLiveUntilInput(); }
  catch (error) { if (error?.name !== "AbortError") { state.liveAwaitingInput = true; appendLiveMessage("system", `Execution error: ${error.message}`, state.liveCurrentId || "entry"); } }
  finally { state.liveBusy = false; render(); renderLiveRun(); }
}
async function toggleLiveAutoPause() {
  if (!state.liveRunning || state.liveOutcome || state.liveStopRequested) return;
  state.livePaused = !state.livePaused;
  renderLiveRun();
  // Paused means manual analyst-answer mode, not a hard executor stop.
  // Resume must not re-run enter for a node that is already awaiting analyst input;
  // it consumes the recorded answer for that exact waiting node instead.
  if (!state.livePaused && !state.liveBusy && state.liveCurrentId && !state.liveOutcome) {
    state.liveBusy = true; renderLiveRun();
    try {
      if (state.liveAwaitingInput) {
        const id = state.liveCurrentId;
        const replayAnswer = nextGuidedReplayAnswer(id);
        const autoAnswer = replayAnswer || nextLiveAutoAnswer(id);
        if (!autoAnswer) return;
        appendLiveMessage("analyst", autoAnswer, `${id} · ${replayAnswer ? "recorded replay" : "auto answer"}`);
        state.liveAwaitingInput = false;
        renderLiveRun();
        const result = await executeLiveElement(id, autoAnswer, "respond");
        if (!result.waiting && result.nextId && !state.liveStopRequested) await advanceLiveUntilInput();
      } else {
        await advanceLiveUntilInput();
      }
    }
    catch (error) { state.liveAwaitingInput = true; appendLiveMessage("system", `Execution error: ${error.message}`, state.liveCurrentId || "resume"); }
    finally { state.liveBusy = false; render(); renderLiveRun(); }
  }
}

function stopLiveRun() {
  if (!state.liveRunning || state.liveOutcome) return;
  const interruptedNode = state.liveCurrentId;
  if (state.liveBusy && state.liveStepAbortController) {
    state.liveInterruptedNode = interruptedNode;
    state.liveStepAbortController.abort();
    state.liveStepAbortController = null;
    state.liveStopRequested = false;
    state.livePaused = true;
    state.liveAwaitingInput = false;
    appendLiveMessage("system", `Model step interrupted at ${interruptedNode}. No partial state was committed.`, "interrupted");
  } else {
    state.livePaused = true;
    state.liveStopRequested = false;
    appendLiveMessage("system", `Execution paused at ${interruptedNode}.`, "paused");
  }
  render(); renderLiveRun();
}

function liveElementKind(id) {
  return graphNodeView(id)?.element_type || (id?.startsWith("G_") ? "gate" : "node");
}
function liveUsageTooltip(usage, calls = 1, contextBreakdown = null) {
  if (!usage) return "";
  const input=Number(usage.input_tokens || 0), output=Number(usage.output_tokens || 0), total=Number(usage.total_tokens || (input+output));
  const lines=[`Total: ${total.toLocaleString()}`, `Input: ${input.toLocaleString()}`, `Output: ${output.toLocaleString()}`];
  lines.push(`Cached input: ${Number(usage.cached_tokens || 0).toLocaleString()}`);
  lines.push(`Reasoning: ${Number(usage.reasoning_tokens || 0).toLocaleString()}`);
  if (calls) lines.push(`API calls: ${Number(calls).toLocaleString()}`);
  if (contextBreakdown) {
    lines.push("", "Context packet (characters, diagnostic only):");
    for (const [key,label] of [["system_chars","core"],["element_chars","element"],["state_chars","state"],["history_chars","history"],["resources_chars","resources"],["attachments_chars","attachments"]]) lines.push(`${label}: ${Number(contextBreakdown[key] || 0).toLocaleString()}`);
  }
  return lines.join("\n");
}

function stableLiveJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableLiveJson).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${stableLiveJson(value[k])}`).join(",")}}`;
  return JSON.stringify(value);
}
function gateFailureFingerprint(gateId, failure) {
  const compact={
    gate_id:String(gateId||""),
    failed_checks:(failure?.failed_checks||[]).map(x=>({check_id:x?.check_id||"",summary:x?.summary||"",severity:x?.severity||null})),
    invalid_state:failure?.invalid_state||[],
    missing_information:failure?.missing_information||[],
    missing_coverage:failure?.missing_coverage||[],
    affected_state:failure?.affected_state||[]
  };
  return stableLiveJson(compact);
}
function relevantFailureStateFingerprint(failure, runtime) {
  const stateAfter=runtime?.state_after || {};
  const affected=Array.isArray(failure?.affected_state) ? failure.affected_state.map(String).filter(Boolean) : [];
  if (!affected.length) return stableLiveJson(stateAfter);
  const projection={};
  for (const rawPath of affected) {
    const parts=rawPath.split('.').filter(Boolean); let cur=stateAfter; let present=true;
    for (const part of parts) {
      if (!cur || typeof cur!=="object" || !(part in cur)) { present=false; break; }
      cur=cur[part];
    }
    projection[rawPath]=present ? cur : null;
  }
  return stableLiveJson(projection);
}
function liveNoProgressCorrectionToken() {
  const history=Array.isArray(state.liveHistory) ? state.liveHistory : [];
  for (let i=history.length-1;i>=0;i--) {
    const item=history[i] || {};
    if (item.role === "analyst") return stableLiveJson({text:String(item.text||""),meta:String(item.meta||"")});
  }
  return "";
}
function detectNoProgressGateFailure(gateId, failure, runtime, correctionToken = "") {
  if (!failure) return false;
  const token=String(correctionToken||"");
  const missing=Array.isArray(failure?.missing_coverage) ? [...new Set(failure.missing_coverage.map(String))].sort() : [];
  if (missing.length) {
    const key=`coverage::${gateId}`;
    const prior=state.liveNoProgressGateFailures?.[key];
    state.liveNoProgressGateFailures[key]={missing,correctionToken:token};
    if (!prior || !Array.isArray(prior.missing)) return false;
    if (token && token !== String(prior.correctionToken||"")) return false;
    const before=new Set(prior.missing), after=new Set(missing);
    const strictSubset=after.size < before.size && [...after].every(x=>before.has(x));
    return !strictSubset; // same correction + no coverage improvement is a real stall.
  }
  const fingerprint=gateFailureFingerprint(gateId,failure);
  const stateFingerprint=relevantFailureStateFingerprint(failure,runtime);
  const key=`${gateId}::${fingerprint}`;
  const prior=state.liveNoProgressGateFailures?.[key];
  state.liveNoProgressGateFailures[key]={stateFingerprint,correctionToken:token};
  if (!prior) return false;
  if (token && token !== String(prior.correctionToken||"")) return false;
  return prior.stateFingerprint===stateFingerprint;
}


function accumulateLiveUsage(usage, debug = null) {
  const attempts=Array.isArray(debug?.semantic_model_attempts)
    ? debug.semantic_model_attempts.filter(a => a?.skipped_model_call !== true && a?.usage && typeof a.usage === "object")
    : [];
  const sourceUsages=attempts.length ? attempts.map(a=>a.usage) : (usage ? [usage] : []);
  for (const item of sourceUsages) {
    for (const key of ["input_tokens", "output_tokens", "total_tokens", "cached_tokens", "reasoning_tokens"]) state.liveUsage[key] += Number(item?.[key] || 0);
  }
  state.liveUsage.calls += sourceUsages.length; // physical provider attempts, not logical model elements
}
function finishLiveRun(status, reason, nodeId) {
  state.liveOutcome = { status, reason, nodeId };
  state.liveCurrentId = null; state.liveAwaitingInput = false;
  const reasonText = {terminal:"Terminal outcome reached.", dead_end:"Execution halted: this non-terminal element has no outgoing route.", unresolved_target:"Execution halted: the selected transition target does not resolve in the playbook.", missing_route:"Execution halted: no valid route was selected.", user_stop:"Execution stopped by the user.", no_progress_cycle:"Execution halted: automatic recovery repeated the same gate failure without changing runtime state."}[reason] || `Execution ${status}.`;
  appendLiveMessage("system", reasonText, `${status} · ${reason || "finished"}`);
}

async function executeLiveElement(currentId, analystInput = "", phase = "enter", attachments = [], analystOverrideContext = "") {
  const controller = new AbortController();
  state.liveStepAbortController = controller;
  state.liveInterruptedNode = null;
  const replayCall = state.liveGuidedReplay?.active ? nextGuidedReplayCall(currentId, phase) : null;
  const recordedResult = replayCall && !replayCall.llm_call_skipped && replayCall.parsed_result && typeof replayCall.parsed_result === "object" ? replayCall.parsed_result : null;
  const pathIndex = Array.isArray(state.livePath) ? state.livePath.lastIndexOf(currentId) : -1;
  const pendingEntry = phase === "enter" && state.livePendingEntryMode?.target === currentId ? state.livePendingEntryMode : null;
  const previousNodeId = phase === "enter" && !pendingEntry && pathIndex > 0 ? state.livePath[pathIndex - 1] : null;
  const entryMode = phase === "enter" ? (pendingEntry?.mode || (previousNodeId ? "transition" : "root")) : null;
  if (pendingEntry) state.livePendingEntryMode = null;
  const data = await request("/api/live-step", {
    session_id: liveSessionId, run_id: state.liveRunId, package_id: state.packageInfo?.id, source: state.source, current_id: currentId,
    previous_node_id: previousNodeId, entry_mode: entryMode,
    analyst_input: analystInput, analyst_override_context: analystOverrideContext, attachments, phase, state: state.liveState, state_revision: state.liveRevision, history: state.liveHistory,
    semantic_fallback_policy: state.liveConfig.semantic_fallback_policy || "automatic_safe",
    recorded_model_result: recordedResult,
    recorded_model_provenance: recordedResult ? {source_run_id:state.liveGuidedReplay?.sourceRunId||"",source_sha256:state.liveGuidedReplay?.sourceSha256||"",recorded_against:state.liveGuidedReplay?.recordedAgainst||{}} : null
  }, {signal: controller.signal});
  if (state.liveStepAbortController === controller) state.liveStepAbortController = null;
  const live = data.live; state.liveState = live.state || state.liveState; if (Number.isInteger(live.state_revision)) state.liveRevision = live.state_revision;
  if (live.debug) state.liveDebugTrace.push(live.debug);
  if (!live.llm_call_skipped) accumulateLiveUsage(live.usage, live.debug);
  const currentKind = liveElementKind(currentId);
  let modelUsageRendered = false;
  // alpha.20: failed gates are analyst-facing evidence. Show structured failure
  // without feeding arbitrary gate prose back as canonical evidence.
  const gateFailure = live.debug?.alpha20?.gate_failure || null;
  const gateResult = live.debug?.output?.parsed_result || null;
  if (currentKind === "gate") {
    if (gateFailure) {
      const checks = Array.isArray(gateFailure.failed_checks) ? gateFailure.failed_checks : [];
      const missing = Array.isArray(gateFailure.missing_information) ? gateFailure.missing_information : [];
      const coverage = Array.isArray(gateFailure.missing_coverage) ? gateFailure.missing_coverage : [];
      const invalid = Array.isArray(gateFailure.invalid_state) ? gateFailure.invalid_state : [];
      const affected = Array.isArray(gateFailure.affected_state) ? gateFailure.affected_state : [];
      const evidence = Array.isArray(gateFailure.evidence) ? gateFailure.evidence : [];
      const lines = [`Check ${currentId}: FAIL`];
      if (checks.length) lines.push("Failed checks:", ...checks.slice(0,8).map(item => `• ${item.check_id || "check"}: ${item.summary || "failed"}`));
      if (invalid.length) lines.push("Invalid state:", ...invalid.slice(0,5).map(item => `• ${typeof item === "string" ? item : JSON.stringify(item)}`));
      if (missing.length) lines.push("Missing information:", ...missing.slice(0,5).map(item => `• ${item.path || "data"}: ${item.needed || item.why_needed || "clarification"}`));
      if (coverage.length) lines.push("Missing coverage:", ...coverage.slice(0,5).map(item => `• ${typeof item === "string" ? item : JSON.stringify(item)}`));
      if (affected.length) lines.push(`Affected state: ${affected.slice(0,8).join(", ")}`);
      if (evidence.length) lines.push(`Evidence: ${evidence.slice(0,3).map(item => typeof item === "string" ? item : JSON.stringify(item)).join("; ")}`);
      if (gateFailure.suggested_recovery_scope) lines.push(`Recommended recovery scope: ${gateFailure.suggested_recovery_scope}`);
      appendLiveMessage("assistant", lines.join("\n"), "validation gate", live.usage || null, live.context_breakdown || null, live.debug || null, null);
      modelUsageRendered = Boolean(live.usage);
      if (detectNoProgressGateFailure(currentId, gateFailure, live.debug?.runtime || {}, liveNoProgressCorrectionToken())) {
        appendLiveMessage("system", `Automatic recovery halted: ${currentId} failed again with the same failure fingerprint and unchanged runtime state. Analyst intervention is required.`, "halted · no_progress_cycle");
        finishLiveRun("halted", "no_progress_cycle", currentId);
        return { waiting: false, nextId: null, live };
      }
    } else if (["passed","pass"].includes(String(gateResult?.status || "").toLowerCase())) {
      const passedChecks = Array.isArray(gateResult?.check_results) ? gateResult.check_results.filter(x=>x?.status==="pass").length : (Array.isArray(gateResult?.passed_checks) ? gateResult.passed_checks.length : (Array.isArray(gateResult?.evidence) ? gateResult.evidence.length : null));
      const suffix = passedChecks !== null ? ` · ${passedChecks} evidence item(s)` : "";
      appendLiveMessage("assistant", `Check ${currentId}: PASS${suffix}`, "validation gate", live.usage || null, live.context_breakdown || null, live.debug || null, null);
      modelUsageRendered = Boolean(live.usage);
    }
  }
  if (live.assistant_message && currentKind !== "gate") {
    const nodeMeta = live.await_analyst ? "awaiting analyst" : (live.rationale_short ||  `processed by ${providerLabel(state.liveConfig.provider)} · ${state.liveConfig.model}`);
    const debugArtifact=live.debug?.runtime?.artifact || null;
    const artifact=debugArtifact?.path ? {
      path: debugArtifact.path,
      filename: String(debugArtifact.path).split('/').pop(),
      size: debugArtifact.size || 0,
      sha256: debugArtifact.sha256 || "",
      warning_count: Array.isArray(debugArtifact.missing_leaf_warnings) ? debugArtifact.missing_leaf_warnings.length : 0
    } : null;
    appendLiveMessage("assistant", live.assistant_message, nodeMeta, live.usage || null, live.context_breakdown || null, live.debug || null, artifact);
    modelUsageRendered = Boolean(live.usage);
  }
  // alpha.20.0.30: every paid/model execution must have a visible transcript
  // representation. Aggregate token totals must be auditable against the chat.
  // If an execution produced no ordinary assistant/gate message, render a compact
  // model-step card carrying its exact usage and full debug modal.
  if (!live.llm_call_skipped && live.usage && !modelUsageRendered) {
    const phaseLabel = String(live.debug?.runtime?.normalized_execution_result?.phase || phase || "enter");
    appendLiveMessage(
      "assistant",
      `Model execution: ${currentId} · ${phaseLabel}`,
      "model step · no analyst-facing message",
      live.usage,
      live.context_breakdown || null,
      live.debug || null,
      null
    );
    modelUsageRendered = true;
  }
  if (live.await_analyst) {
    state.liveAwaitingInput = true;
    state.liveChoiceContext = buildLiveChoiceContext(currentId, live);
    return { waiting: true, nextId: currentId, live };
  }
  state.liveChoiceContext = null;
  state.liveAwaitingInput = false;
  if (live.run_status === "completed") {
    finishLiveRun("completed", live.completion_reason || "terminal", currentId);
    return { waiting: false, nextId: null, live };
  }
  if (live.run_status === "halted") {
    finishLiveRun("halted", live.completion_reason || "missing_route", currentId);
    return { waiting: false, nextId: null, live };
  }
  if (!live.next_id) {
    finishLiveRun("halted", "missing_route", currentId);
    return { waiting: false, nextId: null, live };
  }
  const nextKind = liveElementKind(live.next_id);
  // Gate transitions are visible in alpha.20 so recovery is understandable.
  if (currentKind === "gate" || nextKind === "gate") {
    appendLiveMessage("system", `${currentId} → ${live.next_id}`, live.route_key || "gate transition");
  } else {
    appendLiveMessage("system", `${currentId} → ${live.next_id}`, live.route_key || "transition");
  }
  state.liveCurrentId = live.next_id; state.livePath.push(live.next_id);
  if (graphNodeView(live.next_id)?.terminal) {
    finishLiveRun("completed", "terminal", live.next_id);
    return { waiting: false, nextId: null, live };
  }
  return { waiting: false, nextId: live.next_id, live };
}
async function advanceLiveUntilInput() {
  let guard = 0;
  while (state.liveCurrentId && !state.liveOutcome) {
    if (state.liveStopRequested) { finishLiveRun("halted", "user_stop", state.liveCurrentId); return; }
    if (++guard > 120) throw new Error("Automatic live traversal stopped after 120 elements/responses (possible loop).");
    const id = state.liveCurrentId;
    maybeExitGuidedReplayAtCheckpoint();
    // Pause is a manual-answer override, not a hard execution stop. Always execute
    // enter so the analyst sees the next node/question. Only recorded analyst
    // auto-answers are suppressed while paused.
    render(); renderLiveRun();
    let overrideContext="";
    const override=state.liveAnalystOverride;
    if (override && (override.active || override.target === id) && liveElementKind(id) !== "gate" && recoveryTargetSupportsClarification(id)) {
      overrideContext=String(override.text || "");
      override.active=true;
      if (override.scope === "single") state.liveAnalystOverride=null;
    }
    let result = await executeLiveElement(id, "", "enter", [], overrideContext);
    if (result.waiting && state.liveAnalystOverride?.active) state.liveAnalystOverride=null;
    if (state.liveStopRequested) { finishLiveRun("halted", "user_stop", state.liveCurrentId || id); return; }
    while (result.waiting && state.liveCurrentId === id && !state.liveOutcome) {
      if (state.liveStopRequested) { finishLiveRun("halted", "user_stop", state.liveCurrentId || id); return; }
      if (isConversationalRecoveryNode(id)) { state.livePaused = true; renderLiveRun(); return; }
      if (state.livePaused) return;
      const replayAnswer = nextGuidedReplayAnswer(id);
      const autoAnswer = replayAnswer || nextLiveAutoAnswer(id);
      if (!autoAnswer) return;
      appendLiveMessage("analyst", autoAnswer, `${id} · ${replayAnswer ? "recorded replay" : "auto answer"}`);
      state.liveAwaitingInput = false;
      renderLiveRun();
      if (++guard > 120) throw new Error("Automatic live traversal stopped after 120 elements/responses (possible loop).");
      result = await executeLiveElement(id, autoAnswer, "respond");
      if (state.liveStopRequested) { finishLiveRun("halted", "user_stop", state.liveCurrentId || id); return; }
    }
    if (!result.nextId || state.liveOutcome || state.liveStopRequested) return;
  }
}
async function submitLiveInput(text, attachments = [], displayText = null) {
  if (!state.liveCurrentId || state.liveBusy || !state.liveAwaitingInput) return;
  const currentId = state.liveCurrentId; const publicAttachments=attachments.map(attachmentPublicMeta); appendLiveMessage("analyst", displayText || text, currentId, null, null, null, null, publicAttachments); state.liveBusy = true; state.liveAwaitingInput = false; renderLiveRun();
  try {
    if (isConversationalRecoveryNode(currentId)) {
      await submitRecoveryConversation(currentId, text, attachments);
    } else {
      const result = await executeLiveElement(currentId, text, "respond", attachments);
      if (!result.waiting && result.nextId && !state.liveStopRequested) await advanceLiveUntilInput();
    }
  } catch (error) {
    if (error?.name !== "AbortError") {
      state.liveAwaitingInput = true;
      appendLiveMessage("system", `Execution error: ${error.message}`, state.liveCurrentId || currentId);
    }
  }
  finally { state.liveBusy = false; render(); renderLiveRun(); }
}
async function loadRuntimeConfig() {
  try {
    const response = await fetch(`/api/runtime-config?session_id=${encodeURIComponent(liveSessionId)}`, { cache: "no-store" }); const data = await response.json();
    state.liveConfig = data.live || { enabled: false, provider: "openai", base_url: "https://api.openai.com/v1", model: "gpt-5.6-terra", shared_key: false, personal_key: false, models: ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"] };
    state.gitlab.root=String(data.startup?.gitlab_root || "");
    const rootInput=document.querySelector("#gitlab-root-input"); if(rootInput && state.gitlab.root) rootInput.value=state.gitlab.root;
  } catch (_) { state.liveConfig = { enabled: false, provider: "openai", base_url: "https://api.openai.com/v1", model: "gpt-5.6-terra", shared_key: false, personal_key: false, models: ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"] }; }
  renderLiveRun(); syncModelSettingsIndicator();
  if(state.gitlab.root) loadGitLabCatalog({forceOpen:true});
}
document.querySelector("#live-setting-save")?.addEventListener("click", saveLiveSetting);
document.querySelector("#live-setting-refresh")?.addEventListener("click", refreshLiveSettingModels);
document.querySelectorAll("[data-live-setting-close]").forEach(el => el.addEventListener("click", closeLiveSettingModal));
document.querySelector("#live-setting-close")?.addEventListener("click", closeLiveSettingModal);
document.querySelector("#live-start").addEventListener("click", startLiveRun);
document.querySelector("#live-pause")?.addEventListener("click", toggleLiveAutoPause);
document.querySelector("#live-stop")?.addEventListener("click", stopLiveRun);
document.querySelector("#live-send")?.addEventListener("click", event => { if (state.liveBusy) { event.preventDefault(); stopLiveRun(); } });
document.querySelector("#live-reset").addEventListener("click", resetLiveRun);
document.querySelector("#live-auto-answers")?.addEventListener("click", () => {
  if (state.liveRunning || state.liveBusy) return;
  document.querySelector("#live-auto-answers-file")?.click();
});
document.querySelector("#live-auto-answers-file")?.addEventListener("change", async event => {
  const file = event.target.files?.[0]; if (!file) return;
  const note = document.querySelector("#live-auto-answers-note");
  if (note) note.textContent = `Loading ${file.name}…`;
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    const data = await request("/api/replay-package", { filename: file.name, data_base64: bytesToBase64(bytes) });
    const auto = buildLiveAutoAnswers(data.replay, file.name);
    if (!auto.total) throw new Error("This replay/evidence file does not contain recorded analyst responses that can be safely auto-submitted.");
    state.liveAutoAnswers = auto;
    renderLiveRun();
    renderSettingsOverview();
  } catch (error) {
    state.liveAutoAnswers = { enabled: false, filename: "", answersByNode: {}, cursors: {}, total: 0 };
    renderLiveRun(); alert(`Could not load auto answers: ${error.message}`);
  } finally { event.target.value = ""; }
});
document.querySelector("#live-guided-replay")?.addEventListener("click",()=>{
  if (state.liveRunning||state.liveBusy) return;
  document.querySelector("#live-guided-replay-file")?.click();
});
document.querySelector("#live-guided-replay-file")?.addEventListener("change",async event=>{
  const file=event.target.files?.[0]; if(!file) return;
  const note=document.querySelector("#live-guided-replay-note"); if(note) note.textContent=`Loading ${file.name}…`;
  try {
    const bytes=new Uint8Array(await file.arrayBuffer());
    const data=await request("/api/replay-package",{filename:file.name,data_base64:bytesToBase64(bytes)});
    state.liveGuidedReplay=buildGuidedReplay(data.replay,file.name);
    renderLiveRun();
    renderSettingsOverview();
  } catch(error) {
    state.liveGuidedReplay={enabled:false,active:false,filename:"",checkpointId:"",recordedCalls:[],callCursor:0,answersByNode:{},answerCursors:{},totalCalls:0,totalAnswers:0};
    renderLiveRun(); alert(`Could not load guided replay: ${error.message}`);
  } finally { event.target.value=""; }
});
document.querySelector("#live-state-button")?.addEventListener("click", openLiveStateModal);
document.querySelector("#live-state-close")?.addEventListener("click", closeLiveStateModal);
document.querySelectorAll("[data-live-state-close]").forEach(el => el.addEventListener("click", closeLiveStateModal));
document.querySelector("#live-state-copy")?.addEventListener("click", copyLiveStateJson);
document.querySelector("#live-state-download")?.addEventListener("click", downloadLiveStateJson);
document.querySelector("#live-attachment-input")?.addEventListener("change", async event => {
  try { await addLiveAttachments(event.target.files); } catch (error) { alert(`Could not attach files: ${error.message}`); } finally { event.target.value=""; }
});
document.querySelector("#live-input")?.addEventListener("input",()=>{ renderLiveRun(); requestAnimationFrame(updateLiveComposerLayout); });
document.querySelector("#live-composer-expand")?.addEventListener("click",()=>{ state.liveComposerExpanded=!state.liveComposerExpanded; updateLiveComposerLayout(); document.querySelector("#live-input")?.focus(); });
document.querySelector("#artifact-preview-close")?.addEventListener("click",closeArtifactPreview);
document.querySelector("#live-form").addEventListener("submit", async event => { event.preventDefault(); if (state.liveBusy) return; const input = document.querySelector("#live-input"); const text = input.value.trim(); const attachments=[...(state.liveAttachments||[])]; if (!text && !attachments.length) return; input.value = ""; state.liveAttachments=[]; renderLiveRun(); await submitLiveInput(text, attachments); });
document.querySelector("#live-input").addEventListener("keydown", event => {
  if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
  event.preventDefault();
  if (state.liveBusy || event.target.disabled || document.querySelector("#live-send")?.disabled) return;
  document.querySelector("#live-form").requestSubmit();
});

function setPlaybookPreparation(progress, status, stages=[], error="") {
  const overlay=document.querySelector("#playbook-preparation-overlay"); if (!overlay) return;
  overlay.hidden=false;
  const bar=document.querySelector("#playbook-preparation-progress-bar"); if (bar) bar.style.width=`${Math.max(0,Math.min(100,progress))}%`;
  const st=document.querySelector("#playbook-preparation-status"); if (st) st.textContent=status;
  const box=document.querySelector("#playbook-preparation-stages"); if (box) { box.innerHTML=""; for (const row of stages||[]) { const el=document.createElement("div"); el.className=`playbook-preparation-stage ${String(row.status||"").toLowerCase()}`; el.textContent=`${row.status==="PASS"?"✓":row.status==="FAIL"?"×":"•"} ${String(row.id||"").replaceAll("_"," ")}`; box.append(el); } }
  const err=document.querySelector("#playbook-preparation-error"); if (err) { err.hidden=!error; err.textContent=error||""; }
}
let currentPlaybookPreparationDiagnostics=null;
function playbookDiagnosticFallbackFromText(payload,all){
  const diagnostics=[];
  const seen=new Set();
  const unreachable=all.find(x=>x.toLowerCase().includes("not fully reachable"))||"";
  if(unreachable){
    const match=unreachable.match(/missing=\[([^\]]*)\]/);
    const missing=match?match[1].split(",").map(x=>x.trim().replace(/^['\"]|['\"]$/g,"")).filter(Boolean):[];
    diagnostics.push({severity:"error",code:"GRAPH_NOT_FULLY_REACHABLE",title:"Graph is not fully reachable",message:missing.length?`${missing.length} element(s) cannot be reached from the playbook entry point: ${missing.join(", ")}.`:unreachable,unreachable:missing,expected:"Every executable element must be reachable from the declared entry node through valid control-flow routes.",remediation:"Connect every unreachable executable element to an intended branch, or remove it if it should not be executable."});
    seen.add("GRAPH_NOT_FULLY_REACHABLE");
  }
  for(const line of all){
    if(!line.includes("NONTERMINAL_WITHOUT_ROUTE")) continue;
    const m=line.match(/\b(?:N|G|D|END)_[A-Z0-9_]+\b/); const eid=m?.[0]||null;
    const key=`NONTERMINAL_WITHOUT_ROUTE:${eid||line}`; if(seen.has(key)) continue; seen.add(key);
    diagnostics.push({severity:"error",code:"NONTERMINAL_WITHOUT_ROUTE",title:"Non-terminal element has no outgoing route",message:eid?`${eid} is non-terminal but has no valid outgoing route.`:line,element_id:eid,expected:"Every non-terminal node or gate must route to another element or an allowed external terminal target.",remediation:"Add the intended outgoing transition, or make the element terminal if it should end execution."});
  }
  for(const line of all){
    if(line.includes("NONTERMINAL_WITHOUT_ROUTE")||line.toLowerCase().includes("not fully reachable")||line.startsWith("compiler issue GRAPH_NOT_FULLY_REACHABLE")) continue;
    diagnostics.push({severity:"error",code:"VALIDATION_ERROR",title:"Validation issue",message:line,expected:"The compiled runtime plan must satisfy this validator invariant.",remediation:"Inspect the affected source and correct the reported invariant."});
  }
  return diagnostics;
}
function parsePlaybookPreparationFailure(message="") {
  const raw=String(message||"").trim();
  let payload=null;
  const brace=raw.indexOf("{");
  if (brace>=0) { try { payload=JSON.parse(raw.slice(brace)); } catch (_) {} }
  const structural=Array.isArray(payload?.structural_errors)?payload.structural_errors:[];
  const semantic=Array.isArray(payload?.semantic_errors)?payload.semantic_errors:[];
  const all=[...structural,...semantic].map(String).filter(Boolean);
  const diagnostics=Array.isArray(payload?.diagnostics)&&payload.diagnostics.length?payload.diagnostics:playbookDiagnosticFallbackFromText(payload,all);
  const affected=[...new Set(diagnostics.flatMap(d=>[d.element_id,...(Array.isArray(d.unreachable)?d.unreachable:[])].filter(Boolean)))];
  const headline="The playbook could not be started because the compiler or runtime-plan validator found blocking issues.";
  const bullets=[];
  const unreachable=diagnostics.find(d=>d.code==="GRAPH_NOT_FULLY_REACHABLE");
  const noRoute=diagnostics.filter(d=>d.code==="NONTERMINAL_WITHOUT_ROUTE");
  if(unreachable){ const ids=unreachable.unreachable||[]; bullets.push(ids.length?`${ids.length} unreachable element(s): ${ids.join(", ")}.`:unreachable.message); }
  if(noRoute.length){ bullets.push(`${noRoute.length} non-terminal element${noRoute.length===1?" has":"s have"} no outgoing route: ${noRoute.map(d=>d.element_id||"unknown element").join(", ")}.`); }
  const remaining=diagnostics.length-(unreachable?1:0)-noRoute.length;
  if(remaining>0) bullets.push(`${remaining} additional blocking diagnostic${remaining===1?" was":"s were"} reported.`);
  if(!bullets.length) bullets.push("The compiler returned a blocking error before execution could start.");
  const action="Review each diagnostic below. Fix blocking ERROR items first, then upload the playbook again. Source locations are best-effort and are shown when the compiler can resolve them.";
  return {raw,payload,diagnostics,headline,bullets,affected,action};
}
function renderPreparationDiagnosticCard(diag,index,technical=false){
  const card=document.createElement("article"); card.className=`playbook-preparation-diagnostic ${String(diag.severity||"error").toLowerCase()}`;
  const head=document.createElement("div"); head.className="playbook-preparation-diagnostic-head";
  const title=document.createElement("strong"); title.textContent=`${index+1}. ${diag.title||String(diag.code||"Diagnostic").replaceAll("_"," ")}`;
  const code=document.createElement("code"); code.textContent=diag.code||"DIAGNOSTIC"; head.append(title,code); card.append(head);
  if(diag.message){ const p=document.createElement("p"); p.className="diagnostic-message"; p.textContent=diag.message; card.append(p); }
  const meta=[];
  if(diag.element_id) meta.push(["Affected element",diag.element_id]);
  if(diag.element_kind) meta.push(["Element type",diag.element_kind]);
  const loc=diag.source_location||{}; if(loc.file) meta.push(["Source",`${loc.file}${loc.line?`:${loc.line}${loc.column?`:${loc.column}`:""}`:" (location not resolved)"}`]);
  if(diag.path) meta.push(["Path",diag.path]);
  if(Array.isArray(diag.current_routes)) meta.push(["Current routes",diag.current_routes.length?diag.current_routes.map(r=>`${r.label||"route"} → ${r.target||"?"}`).join("; "):"None"]);
  if(Array.isArray(diag.unreachable)&&diag.unreachable.length) meta.push(["Unreachable",diag.unreachable.join(", ")]);
  if(meta.length){ const dl=document.createElement("dl"); dl.className="diagnostic-meta"; for(const [k,v] of meta){ const dt=document.createElement("dt"); dt.textContent=k; const dd=document.createElement("dd"); dd.textContent=String(v); dl.append(dt,dd); } card.append(dl); }
  if(diag.expected){ const row=document.createElement("div"); row.className="diagnostic-rule"; row.innerHTML=`<strong>Expected rule</strong><span>${escapeHtml(diag.expected)}</span>`; card.append(row); }
  if(diag.remediation){ const row=document.createElement("div"); row.className="diagnostic-remediation"; row.innerHTML=`<strong>How to fix</strong><span>${escapeHtml(diag.remediation)}</span>`; card.append(row); }
  if(technical&&diag.compiler_issue){ const raw=document.createElement("details"); raw.className="diagnostic-compiler-issue"; const sum=document.createElement("summary"); sum.textContent="Compiler issue object"; const pre=document.createElement("pre"); pre.textContent=JSON.stringify(diag.compiler_issue,null,2); raw.append(sum,pre); card.append(raw); }
  return card;
}
function showPlaybookPreparationTab(tab="human") {
  const selected=tab==="technical"?"technical":"human";
  document.querySelectorAll("[data-playbook-preparation-tab]").forEach(button=>{
    const active=button.dataset.playbookPreparationTab===selected;
    button.classList.toggle("active",active);
    button.setAttribute("aria-selected",active?"true":"false");
  });
  document.querySelectorAll("[data-playbook-preparation-panel]").forEach(panel=>{
    panel.hidden=panel.dataset.playbookPreparationPanel!==selected;
  });
  const body=document.querySelector("#playbook-preparation-body"); if(body) body.scrollTop=0;
}
function renderPlaybookPreparationFailure(message) {
  const info=parsePlaybookPreparationFailure(message); currentPlaybookPreparationDiagnostics={schema:"ordo.editor.playbook_preparation_diagnostics.v1",generated_at:new Date().toISOString(),editor_version:"0.2.0-alpha.20.0.106-dev",playbook_file:document.querySelector("#playbook-preparation-file")?.textContent||null,...info};
  const summary=document.querySelector("#playbook-preparation-summary");
  if (summary) {
    summary.hidden=false; summary.innerHTML="";
    const lead=document.createElement("p"); lead.className="playbook-preparation-human-lead"; lead.textContent=info.headline; summary.append(lead);
    const label=document.createElement("div"); label.className="playbook-preparation-human-label"; label.textContent="What was found — blocking issues"; summary.append(label);
    const ul=document.createElement("ul"); ul.className="playbook-preparation-human-list"; for(const item of info.bullets){ const li=document.createElement("li"); li.textContent=item; ul.append(li); } summary.append(ul);
    const list=document.createElement("div"); list.className="playbook-preparation-diagnostic-list human"; info.diagnostics.forEach((d,i)=>list.append(renderPreparationDiagnosticCard(d,i,false))); summary.append(list);
    const actionLabel=document.createElement("div"); actionLabel.className="playbook-preparation-human-label"; actionLabel.textContent="What to do"; summary.append(actionLabel);
    const action=document.createElement("p"); action.className="playbook-preparation-human-action"; action.textContent=info.action; summary.append(action);
  }
  const tabs=document.querySelector("#playbook-preparation-tabs"); if(tabs) tabs.hidden=false;
  const diagnostics=document.querySelector("#playbook-preparation-diagnostics"); if(diagnostics){ diagnostics.innerHTML=""; info.diagnostics.forEach((d,i)=>diagnostics.append(renderPreparationDiagnosticCard(d,i,true))); }
  const err=document.querySelector("#playbook-preparation-error"); if(err){ err.hidden=!info.raw; err.textContent=info.payload?JSON.stringify(info.payload,null,2):info.raw; }
  showPlaybookPreparationTab("human");
}
function downloadPlaybookPreparationDiagnostics(){
  if(!currentPlaybookPreparationDiagnostics) return;
  const file=(currentPlaybookPreparationDiagnostics.playbook_file||"playbook").replace(/\.[^.]+$/,"").replace(/[^A-Za-z0-9._-]+/g,"_");
  const blob=new Blob([JSON.stringify(currentPlaybookPreparationDiagnostics,null,2)],{type:"application/json;charset=utf-8"});
  const url=URL.createObjectURL(blob); const a=document.createElement("a"); a.href=url; a.download=`${file}_compilation_diagnostics.json`; document.body.append(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),500);
}

function closePlaybookPreparation() { const overlay=document.querySelector("#playbook-preparation-overlay"); if (overlay) overlay.hidden=true; }
function beginPlaybookPreparation(filename) {
  currentPlaybookPreparationDiagnostics=null;
  const overlay=document.querySelector("#playbook-preparation-overlay"); if (overlay) overlay.hidden=false;
  const f=document.querySelector("#playbook-preparation-file"); if (f) f.textContent=filename;
  const title=document.querySelector("#playbook-preparation-title"); if (title) title.textContent="Preparing Playbook";
  const close=document.querySelector("#playbook-preparation-close"); if (close) close.hidden=true;
  const summary=document.querySelector("#playbook-preparation-summary"); if (summary) { summary.hidden=true; summary.innerHTML=""; }
  const technical=document.querySelector("#playbook-preparation-technical"); if (technical) technical.hidden=true;
  const tabs=document.querySelector("#playbook-preparation-tabs"); if(tabs) tabs.hidden=true;
  const body=document.querySelector("#playbook-preparation-body"); if(body) body.scrollTop=0;
  setPlaybookPreparation(18,"Loading source…",[{id:"load_source",status:"RUNNING"}]);
  requestAnimationFrame(()=>setPlaybookPreparation(58,"Compiling and validating runtime plan…",[{id:"load_source",status:"PASS"},{id:"compile_runtime_plan",status:"RUNNING"}]));
}
function finishPlaybookPreparation(pkg) {
  const report=pkg?.preparation_report||{};
  const stages=report.stages||[{id:"load_source",status:"PASS"},{id:"verify_runtime_plan",status:"PASS"}];
  setPlaybookPreparation(100,"Playbook verified. Ready to execute.",stages);
  setTimeout(()=>{ const overlay=document.querySelector("#playbook-preparation-overlay"); if (overlay) overlay.hidden=true; },450);
}
function finishDegradedPlaybookPreparation(pkg) {
  const report=pkg?.preparation_report||{}, diagnostics=Array.isArray(pkg?.load_diagnostics)?pkg.load_diagnostics:[];
  const stages=report.stages||[{id:"load_source",status:"PASS"},{id:"compile_runtime_plan",status:"FAIL"}];
  const title=document.querySelector("#playbook-preparation-title"); if(title)title.textContent="Playbook loaded with warnings";
  const close=document.querySelector("#playbook-preparation-close"); if(close)close.hidden=false;
  setPlaybookPreparation(100,"Inspection is available; unavailable capabilities are disabled.",stages);
  const summary=document.querySelector("#playbook-preparation-summary");
  if(summary){
    summary.hidden=false; summary.innerHTML="";
    const lead=document.createElement("p");lead.className="playbook-preparation-human-lead";lead.textContent="The package was loaded for inspection, but one or more executable/runtime preparation steps failed.";summary.append(lead);
    const label=document.createElement("div");label.className="playbook-preparation-human-label";label.textContent="Warnings";summary.append(label);
    const ul=document.createElement("ul");ul.className="playbook-preparation-human-list";
    for(const item of diagnostics){const li=document.createElement("li");li.textContent=String(item?.message||item?.code||"Preparation warning");ul.append(li);} if(!diagnostics.length){const li=document.createElement("li");li.textContent="Executable runtime capability is unavailable.";ul.append(li);} summary.append(ul);
    const action=document.createElement("p");action.className="playbook-preparation-human-action";action.textContent="You can continue inspecting the source, tree, Data Flow, settings, package files, and applicable verification checks. Disabled tabs require capabilities that were not prepared successfully.";summary.append(action);
    const button=document.createElement("button");button.type="button";button.className="primary";button.textContent="Continue in Editor";button.addEventListener("click",closePlaybookPreparation);summary.append(button);
  }
  const tabs=document.querySelector("#playbook-preparation-tabs");if(tabs)tabs.hidden=true;
}
function failPlaybookPreparation(message) {
  const title=document.querySelector("#playbook-preparation-title"); if (title) title.textContent="Playbook could not be started";
  const close=document.querySelector("#playbook-preparation-close"); if (close) close.hidden=false;
  setPlaybookPreparation(100,"Compilation or validation failed.",[],"");
  renderPlaybookPreparationFailure(message);
}
document.addEventListener("click",event=>{
  const close=event.target?.closest?.("#playbook-preparation-close");
  if(close){ event.preventDefault(); event.stopPropagation(); closePlaybookPreparation(); return; }
  const download=event.target?.closest?.("#playbook-preparation-download-diagnostics");
  if(download){ event.preventDefault(); event.stopPropagation(); downloadPlaybookPreparationDiagnostics(); return; }
  const tab=event.target?.closest?.("[data-playbook-preparation-tab]");
  if(tab){ event.preventDefault(); showPlaybookPreparationTab(tab.dataset.playbookPreparationTab); return; }
  if(event.target?.id==="playbook-preparation-overlay") closePlaybookPreparation();
});
document.addEventListener("keydown",event=>{ if (event.key==="Escape" && !document.querySelector("#playbook-preparation-overlay")?.hidden) closePlaybookPreparation(); });

function applyLoadedPlaybookPackage(pkg) {
  state.lineage.sourceData=null; state.lineage.sourceError=null; state.lineage.sourceDataClassFilter="all"; state.lineage.sourceLegend=null; state.lineage.sourceTraceDirection=null; state.lineage.sourceSelected=null; state.lineage.sourceFocusRoot=null; state.lineage.sourcePositions={}; state.lineage.assistantThreads={}; state.lineage.messages=[]; state.lineage.busy=false; state.lineage.viewMode="source";
  state.packageInfo={id:pkg.id,filename:pkg.filename,source_name:pkg.source_name,entry_node:pkg.entry_node,file_count:pkg.file_count,text_resource_count:pkg.text_resource_count,compiled_plan_status:pkg.compiled_plan_status||null,semantic_plan_status:pkg.semantic_plan_status||null,preparation_report:pkg.preparation_report||null,input_kind:pkg.input_kind||null,interaction_contract:pkg.interaction_contract||null,load_status:pkg.load_status||"ready",load_diagnostics:Array.isArray(pkg.load_diagnostics)?pkg.load_diagnostics:[],capabilities:pkg.capabilities||{},graph_error:pkg.graph_error||null};
  state.interactionContract=pkg.interaction_contract||state.interactionContract;
  stopVerificationPolling(); state.verification.runId=""; state.verification.running=false; state.verification.progress=0; state.verification.summary=null; state.verification.lastResult=null; state.verification.checks=state.verification.catalog.map(x=>({...x,status:"PENDING",message:"Waiting"}));
  state.source=pkg.source; state.graph=pkg.graph||{nodes:[],edges:[]}; state.positions={}; state.manualPositions=new Set(); state.collapsedNodes=new Set(); state.pendingTransitionSource=null;
  clearDialogPlaybackTimer(); state.dialogPath=null; state.dialogPlayMode=false; state.dialogPlaying=false; state.dialogVisibleCount=null; resetLiveRun(); render(); renderLiveRun();
  if((pkg.load_status||"ready")==="degraded") { showPanelTab((pkg.capabilities||{}).show_tree?"inspection":"packagefiles"); finishDegradedPlaybookPreparation(pkg); }
  else { finishPlaybookPreparation(pkg); showPanelTab("run"); }
}
async function loadPlaybookFromGitLab(path,filename) {
  const root=String(document.querySelector("#gitlab-root-input")?.value || state.gitlab.root || "").trim();
  if(!root)return;
  beginPlaybookPreparation(filename || path.split("/").pop() || "GitLab playbook");
  try { const data=await request("/api/gitlab-playbook-load",{root_url:root,path}); applyLoadedPlaybookPackage(data.package); }
  catch(error){ failPlaybookPreparation(error.message); }
}
function gitLabRootUrl() { return String(document.querySelector("#gitlab-root-input")?.value || state.gitlab.root || "").trim(); }
function downloadGitLabArchive(path) {
  const root=gitLabRootUrl(); if(!root||!path)return;
  const href=`/api/gitlab-archive?root_url=${encodeURIComponent(root)}&path=${encodeURIComponent(path)}`;
  const a=document.createElement("a");a.href=href;a.download=String(path).split("/").pop()||"playbook.zip";document.body.append(a);a.click();a.remove();
}
function closeGitLabReadme() {
  const modal=document.querySelector("#gitlab-readme-modal");if(!modal)return;modal.hidden=true;modal.setAttribute("aria-hidden","true");
}
async function openGitLabReadme(readme,directoryName="") {
  const root=gitLabRootUrl(),modal=document.querySelector("#gitlab-readme-modal"),title=document.querySelector("#gitlab-readme-title"),pathHost=document.querySelector("#gitlab-readme-path"),body=document.querySelector("#gitlab-readme-body");
  if(!root||!readme?.path||!modal||!body)return;
  title.textContent=directoryName?`${directoryName} · README.md`:"README.md";pathHost.textContent=readme.path;body.innerHTML='<div class="hint">Loading README…</div>';modal.hidden=false;modal.setAttribute("aria-hidden","false");
  try { const data=await request("/api/gitlab-readme",{root_url:root,path:readme.path});body.innerHTML=renderBasicMarkdown(data.content||""); }
  catch(error){body.innerHTML=`<div class="error">${escapeHtml(error.message)}</div>`;}
}
function syncGitLabDirectoryReadmeButton(box,node) {
  const summary=box.querySelector(":scope > .gitlab-directory-summary"); if(!summary)return;
  summary.querySelector(".gitlab-readme-button")?.remove();
  if(!node.readme)return;
  const readme=document.createElement("button");readme.type="button";readme.className="gitlab-readme-button";readme.textContent="README";readme.title=`Open ${node.readme.filename||"README.md"}`;
  readme.addEventListener("click",event=>{event.preventDefault();event.stopPropagation();openGitLabReadme(node.readme,node.name||"");});summary.append(readme);
}
function populateGitLabDirectoryBody(body,node,depth) {
  body.innerHTML="";
  for(const archive of node.archives||[]){
    const row=document.createElement("div");row.className="gitlab-archive-row";
    const label=document.createElement("span");label.className="gitlab-archive-name";label.textContent=archive.filename;label.title=archive.path;row.append(label);
    const load=document.createElement("button");load.type="button";load.className="gitlab-archive-action";load.textContent="Load";load.addEventListener("click",()=>loadPlaybookFromGitLab(archive.path,archive.filename));row.append(load);
    const download=document.createElement("button");download.type="button";download.className="gitlab-archive-action";download.textContent="Download";download.addEventListener("click",()=>downloadGitLabArchive(archive.path));row.append(download);
    body.append(row);
  }
  for(const child of node.children||[])body.append(renderGitLabDirectory(child,depth+1));
  if(!(node.archives||[]).length && !(node.children||[]).length){const empty=document.createElement("div");empty.className="gitlab-directory-empty hint";empty.textContent="No ZIP archives or subdirectories.";body.append(empty);}
}
async function loadGitLabDirectoryNode(node,box,body,depth) {
  if(node.loaded||node.loading)return;
  const cached=state.gitlab.loadedDirectories?.[node.path];
  if(cached){Object.assign(node,cached,{loaded:true,loading:false});syncGitLabDirectoryReadmeButton(box,node);populateGitLabDirectoryBody(body,node,depth);return;}
  node.loading=true;box.classList.add("loading");body.innerHTML='<div class="gitlab-directory-loading" role="status"><span class="gitlab-loading-spinner" aria-hidden="true"></span><span>Loading…</span></div>';
  try {
    const data=await request("/api/gitlab-directory",{root_url:gitLabRootUrl(),path:node.path});
    const loaded=data.directory||{};Object.assign(node,loaded,{loaded:true,loading:false});
    state.gitlab.loadedDirectories[node.path]={...loaded,loaded:true,loading:false};
    syncGitLabDirectoryReadmeButton(box,node);populateGitLabDirectoryBody(body,node,depth);
  } catch(error) {
    node.loading=false;body.innerHTML=`<div class="error">${escapeHtml(error.message)}</div>`;
  } finally {box.classList.remove("loading");}
}
function renderGitLabDirectory(node,depth=0) {
  const box=document.createElement("details");box.className="gitlab-directory";box.dataset.depth=String(depth);
  const summary=document.createElement("summary");summary.className="gitlab-directory-summary";
  const name=document.createElement("span");name.className="gitlab-directory-summary-name";name.textContent=node.name||node.path||"directory";summary.append(name);box.append(summary);
  const body=document.createElement("div");body.className="gitlab-directory-body";box.append(body);
  syncGitLabDirectoryReadmeButton(box,node);
  if(node.loaded)populateGitLabDirectoryBody(body,node,depth);
  box.addEventListener("toggle",()=>{if(box.open&&!node.loaded)loadGitLabDirectoryNode(node,box,body,depth);});
  return box;
}
function renderGitLabCatalog() {
  const host=document.querySelector("#gitlab-playbook-list"),status=document.querySelector("#gitlab-status"); if(!host)return; host.innerHTML="";
  if(state.gitlab.loading){if(status)status.textContent="Reading first GitLab directory level…";return;}
  if(state.gitlab.error){if(status)status.textContent=state.gitlab.error;return;}
  const root=state.gitlab.catalog?.root||null, rows=state.gitlab.catalog?.directories || root?.children || [];
  if(status)status.textContent=rows.length?`${rows.length} top-level director${rows.length===1?"y":"ies"} found. Open a directory to load its contents.`:"No subdirectories found under this root.";
  if(root?.archives?.length){const rootFiles=document.createElement("div");rootFiles.className="gitlab-root-archives";populateGitLabDirectoryBody(rootFiles,{archives:root.archives,children:[]},-1);host.append(rootFiles);}
  for(const node of rows)host.append(renderGitLabDirectory(node,0));
}
async function loadGitLabCatalog({forceOpen=false}={}) {
  const panel=document.querySelector("#gitlab-browser-panel"),input=document.querySelector("#gitlab-root-input"); if(forceOpen&&panel)panel.hidden=false;
  const root=String(input?.value || state.gitlab.root || "").trim(); if(!root){if(panel)panel.hidden=false;if(input)input.focus();return;}
  state.gitlab.root=root; state.gitlab.loading=true; state.gitlab.error=""; state.gitlab.loadedDirectories={}; renderGitLabCatalog();
  try { state.gitlab.catalog=await request("/api/gitlab-playbooks",{root_url:root}); }
  catch(error){state.gitlab.catalog=null;state.gitlab.error=`Could not read GitLab: ${error.message}`;}
  finally {state.gitlab.loading=false;renderGitLabCatalog();}
}
document.querySelector("#package-file-input")?.addEventListener("change", async event => {
  const file=event.target.files?.[0]; if(!file)return; beginPlaybookPreparation(file.name);
  try { const bytes=new Uint8Array(await file.arrayBuffer()); const data=await request("/api/playbook-package",{filename:file.name,data_base64:bytesToBase64(bytes)}); applyLoadedPlaybookPackage(data.package); }
  catch(error){failPlaybookPreparation(error.message);} finally {event.target.value="";}
});
document.querySelector("#gitlab-playbook-browser")?.addEventListener("click",()=>{const panel=document.querySelector("#gitlab-browser-panel");if(panel)panel.hidden=!panel.hidden;if(panel&&!panel.hidden){const input=document.querySelector("#gitlab-root-input");if(input&&!input.value&&state.gitlab.root)input.value=state.gitlab.root;if(input?.value)loadGitLabCatalog();else input?.focus();}});
document.querySelector("#gitlab-refresh")?.addEventListener("click",()=>loadGitLabCatalog({forceOpen:true}));
document.querySelector("#gitlab-root-input")?.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();loadGitLabCatalog({forceOpen:true});}});
document.querySelectorAll("[data-gitlab-readme-close]").forEach(el=>el.addEventListener("click",closeGitLabReadme));
document.addEventListener("keydown",event=>{if(event.key==="Escape"&&!document.querySelector("#gitlab-readme-modal")?.hidden)closeGitLabReadme();});
const openYamlButton = document.querySelector("#canvas-open-yaml"); if (openYamlButton) openYamlButton.addEventListener("click", () => { hideCanvasContextMenu(); document.querySelector("#file-input")?.click(); });
const openPackageButton = document.querySelector("#canvas-open-package"); if (openPackageButton) openPackageButton.addEventListener("click", () => { hideCanvasContextMenu(); document.querySelector("#package-file-input").click(); });

document.querySelector("#replay-file-input").addEventListener("change", async event => {
  const file = event.target.files?.[0]; if (!file) return;
  const name = document.querySelector("#replay-file-name"); if (name) name.textContent = `Loading ${file.name}…`;
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    const data = await request("/api/replay-package", { filename: file.name, data_base64: bytesToBase64(bytes) });
    state.replayData = data.replay; state.replayFocusId = null;
    if (name) name.textContent = file.name;
    showPanelTab("replay"); renderReplay();
  } catch (error) {
    if (name) name.textContent = file.name;
    alert(`Could not load replay package: ${error.message}`);
  } finally { event.target.value = ""; }
});
document.querySelector("#replay-download-md").addEventListener("click", downloadReplayMarkdown);
document.querySelector("#replay-print-pdf").addEventListener("click", printReplayPdf);
document.querySelectorAll("[data-token-debug-tab]").forEach(button => button.addEventListener("click", () => { activeTokenDebugTab=button.dataset.tokenDebugTab; renderTokenDebugTab(); }));

document.querySelectorAll("[data-recovery-clarification-close]").forEach(el => el.addEventListener("click", closeRecoveryClarificationDialog));
document.querySelector("#recovery-clarification-without")?.addEventListener("click",()=>confirmRecoveryTransition(false));
document.querySelector("#recovery-clarification-apply")?.addEventListener("click",()=>confirmRecoveryTransition(true));
document.querySelectorAll("[data-token-debug-close]").forEach(button => button.addEventListener("click", closeTokenDebugModal));
document.querySelector("#token-debug-close")?.addEventListener("click", closeTokenDebugModal);
document.querySelector("#token-debug-copy")?.addEventListener("click", async () => { try { await navigator.clipboard.writeText(tokenDebugCurrentTabText()); } catch (_) {} });
document.querySelector("#token-debug-download")?.addEventListener("click", downloadTokenDebugJson);
document.addEventListener("keydown", event => {
  if (event.key !== "Escape") return;
  if (!document.querySelector("#live-state-modal")?.hidden) { closeLiveStateModal(); return; }
  if (!document.querySelector("#token-debug-modal")?.hidden) closeTokenDebugModal();
});


function verificationStatusLabel(status) { return String(status || "PENDING").toUpperCase(); }
function verificationSkippedLabel(item) {
  if (verificationStatusLabel(item?.status)!=="SKIPPED") return "";
  if (item?.skip_label) return String(item.skip_label);
  const text=`${item?.message||""} ${item?.description||""}`.toLowerCase();
  if (text.includes("runtime state") || text.includes("journey evidence") || text.includes("intake evidence")) return "Needs runtime evidence";
  if (text.includes("gate_id") || text.includes("gate-specific")) return "Needs selected gate";
  if (text.includes("bindings")) return "Needs bindings context";
  if (text.includes("tree-module") || text.includes("tree module")) return "Needs tree-module context";
  if (text.includes("template")) return "Needs template context";
  if (text.includes("release") && text.includes("not applicable")) return "Release-only";
  if (text.includes("portable authoring bundle") || text.includes("toolkit")) return "Toolkit-only";
  if (text.includes("safe one-click")) return "Not in safe one-click";
  if (text.includes("not applicable")) return "Not applicable";
  return "Needs additional context";
}
function verificationDisplayRows(rows) {
  if(state.verification.running || !state.verification.lastResult?.finished) return rows;
  const rank={ERROR:0,FAIL:1,SKIPPED:2,RUNNING:3,PENDING:4,PASS:5};
  return [...rows].sort((a,b)=>{
    const sa=verificationStatusLabel(a.status), sb=verificationStatusLabel(b.status);
    const d=(rank[sa]??4)-(rank[sb]??4);
    return d || Number(a.index||0)-Number(b.index||0);
  });
}
function verificationExplanationKey(item){ return `${state.verification.runId||"run"}:${item.id||item.title||"check"}`; }
async function explainVerificationCheck(item){
  if(!modelExplanationAvailable()) return;
  const key=verificationExplanationKey(item); if(state.verification.explanationBusy===key) return;
  state.verification.explanationBusy=key; renderVerificationPage();
  try{
    const data=await requestModelExplanation("verification_check",{
      verification_check:{id:item.id||null,title:item.title||null,category:item.group||null,description:item.description||"",status:verificationStatusLabel(item.status),message:item.message||"",output:item.output||"",evidence_summary:item.evidence_summary||"",evidence:Array.isArray(item.evidence)?item.evidence:[],exit_code:item.exit_code??null,duration_ms:item.duration_ms??null}
    });
    state.verification.explanations[key]={explanation:data.explanation||"",classification:data.classification||"inconclusive",classification_normalized_from:data.classification_normalized_from||null,model:data.model||null,provider:data.provider||null,locale:data.locale||null,language:data.language||null,usage:data.usage||null,generated_at:new Date().toISOString()};
  }catch(error){ state.verification.explanations[key]={explanation:`Explanation failed: ${error.message}`,error:true}; }
  finally{ state.verification.explanationBusy=null; renderVerificationPage(); }
}

function verificationCheckPayload(item){
  return {
    id:item.id||null,title:item.title||null,category:item.group||null,
    description:item.description||"",status:verificationStatusLabel(item.status),
    skip_kind:item.skip_kind||null,skip_label:item.skip_label||null,
    message:item.message||"",output:item.output||"",
    evidence_summary:item.evidence_summary||"",
    evidence:Array.isArray(item.evidence)?item.evidence:[],
    exit_code:item.exit_code??null,duration_ms:item.duration_ms??null
  };
}
function renderVerificationAssistant(){
  const panel=document.querySelector("#verification-assistant-panel");
  if(!panel || panel.hidden) return;
  const context=document.querySelector("#verification-assistant-context");
  const messages=document.querySelector("#verification-assistant-messages");
  const unavailable=document.querySelector("#verification-assistant-unavailable");
  const input=document.querySelector("#verification-assistant-input");
  const send=document.querySelector("#verification-assistant-send");
  const clear=document.querySelector("#verification-assistant-clear");
  const available=modelExplanationAvailable();
  if(unavailable) unavailable.hidden=available;
  if(input) input.disabled=!available || state.verification.assistantBusy || !state.verification.assistantCheck;
  if(send) send.disabled=!available || state.verification.assistantBusy || !state.verification.assistantCheck;
  if(clear) clear.disabled=state.verification.assistantBusy || (!state.verification.assistantCheck && !state.verification.assistantMessages.length);
  const item=state.verification.assistantCheck;
  if(context){
    if(!item) context.innerHTML='Select <strong>Discuss in chat</strong> on a non-PASS verification.';
    else {
      const status=verificationStatusLabel(item.status);
      const reason=status==="SKIPPED" ? verificationSkippedLabel(item) : status;
      context.innerHTML=`<strong>${escapeHtml(item.title||item.id||"Verification")}</strong><span>${escapeHtml(reason)}</span><p>${escapeHtml(item.message||item.description||"")}</p>`;
    }
  }
  if(messages){
    const visibleVerificationMessages=state.verification.assistantMessages.filter(msg=>!msg.hidden);messages.innerHTML=visibleVerificationMessages.map(msg=>`<div class="verification-assistant-message ${msg.role==="user"?"user":"assistant"}">${msg.role==="assistant"?renderBasicMarkdown(msg.content||""):escapeHtml(msg.content||"").replace(/\n/g,"<br>")}</div>`).join("");
    messages.querySelectorAll(".verification-assistant-message").forEach((el,i)=>{const msg=visibleVerificationMessages[i];if(msg)attachChatCopyButton(el, msg.content || "", msg.role === "user" ? "right" : "left");});
    if(state.verification.assistantBusy) messages.insertAdjacentHTML("beforeend",'<div class="verification-assistant-message assistant busy">Thinking…</div>');
    messages.scrollTop=messages.scrollHeight;
  }
}
async function openVerificationDiscussion(item){
  if(!item || verificationStatusLabel(item.status)==="PASS") return;
  const current=state.verification.assistantCheck;
  const changed=!current || current.id!==item.id;
  if(changed){
    state.verification.assistantCheck=item;
    state.verification.assistantMessages=[];
  }
  renderVerificationAssistant();
  if(changed && modelExplanationAvailable()){
    await sendVerificationDiscussion(
      "Explain this verification result immediately. Tell me what happened, why it has this status, whether it points to a playbook problem or to missing context/tooling, and what I should do next.",
      {hiddenUser:true}
    );
  }
  document.querySelector("#verification-assistant-input")?.focus();
}
async function sendVerificationDiscussion(message,options={}){
  const item=state.verification.assistantCheck;
  const text=String(message||"").trim();
  if(!item || !text || state.verification.assistantBusy || !modelExplanationAvailable()) return false;
  state.verification.assistantMessages.push({role:"user",content:text,hidden:Boolean(options.hiddenUser)});
  state.verification.assistantBusy=true; renderVerificationAssistant();
  try{
    const data=await request("/api/verification-assistant",{
      session_id:liveSessionId,
      package_id:state.packageInfo?.id||"",
      verification_check:verificationCheckPayload(item),
      messages:state.verification.assistantMessages.map(m=>({role:m.role,content:m.content}))
    });
    const answer=String(data.answer_markdown||data.explanation||"").trim();
    if(!answer) throw new Error("The model returned an empty verification-assistant response.");
    state.verification.assistantMessages.push({role:"assistant",content:answer});
    return true;
  }catch(error){
    state.verification.assistantMessages.push({role:"assistant",content:`**Discussion failed.** ${error.message}`});
    return false;
  }finally{
    state.verification.assistantBusy=false; renderVerificationAssistant();
  }
}
function bindVerificationAssistant(){
  const form=document.querySelector("#verification-assistant-form");
  const input=document.querySelector("#verification-assistant-input");
  form?.addEventListener("submit",event=>{
    event.preventDefault();
    const value=input?.value||"";
    if(!String(value).trim()) return;
    if(input) input.value="";
    sendVerificationDiscussion(value);
  });
  input?.addEventListener("keydown",event=>{
    if(event.key!=="Enter") return;
    if(event.ctrlKey) return; // Ctrl+Enter keeps the textarea default: insert a new line.
    event.preventDefault();
    if(!state.verification.assistantBusy && String(input.value||"").trim()) form?.requestSubmit();
  });
  document.querySelector("#verification-assistant-clear")?.addEventListener("click",()=>{
    state.verification.assistantCheck=null;
    state.verification.assistantMessages=[];
    renderVerificationAssistant();
  });
}

function renderVerificationPage() {
  const list=document.querySelector("#verification-list"); if(!list) return;
  const rawRows=state.verification.checks.length ? state.verification.checks : state.verification.catalog.map(item=>({...item,status:"PENDING",message:"Waiting"}));
  const rows=verificationDisplayRows(rawRows);
  list.innerHTML="";
  rows.forEach(item=>{
    const row=document.createElement("div"); row.className="verification-row";
    const main=document.createElement("div"); main.className="verification-row-main";
    const title=document.createElement("div"); title.className="verification-row-title";
    const name=document.createElement("span"); name.textContent=item.title || item.id;
    const group=document.createElement("span"); group.className="verification-row-group"; group.textContent=item.group || "verification";
    title.append(name,group);
    const desc=document.createElement("div"); desc.className="verification-row-description"; desc.textContent=item.description || "";
    const msg=document.createElement("div"); msg.className="verification-row-message"; msg.textContent=item.message || "";
    main.append(title,desc,msg);
    if(item.evidence_summary){
      const evidenceSummary=document.createElement("div"); evidenceSummary.className="verification-evidence-summary";
      evidenceSummary.textContent=item.evidence_summary; main.append(evidenceSummary);
    }
    if(Array.isArray(item.evidence)&&item.evidence.length){
      const details=document.createElement("details"); details.className="verification-evidence";
      const sum=document.createElement("summary"); sum.textContent=`Evidence ${item.evidence.length}`;
      details.append(sum);
      item.evidence.forEach(ev=>{
        const card=document.createElement("div"); card.className="verification-evidence-item";
        const head=document.createElement("div"); head.className="verification-evidence-head";
        head.innerHTML=`<strong>${escapeHtml(ev.path||ev.name||"report")}</strong><span>${Number(ev.size_bytes||0)} bytes</span>`;
        card.append(head);
        if(ev.content_json!==undefined){
          const pre=document.createElement("pre"); pre.textContent=JSON.stringify(ev.content_json,null,2); card.append(pre);
        }else if(ev.content_text){
          const pre=document.createElement("pre"); pre.textContent=String(ev.content_text); card.append(pre);
        }
        details.append(card);
      });
      main.append(details);
    }
    const status=verificationStatusLabel(item.status);
    if(["FAIL","ERROR","SKIPPED"].includes(status)){
      const key=verificationExplanationKey(item), cached=state.verification.explanations[key], busy=state.verification.explanationBusy===key;
      const tools=document.createElement("div"); tools.className="verification-row-tools";
      const explain=document.createElement("button"); explain.type="button"; explain.className="verification-explain-button";
      explain.disabled=!modelExplanationAvailable() || busy || Boolean(cached && !cached.error);
      explain.textContent=busy?"Explaining…":cached&&!cached.error?"Explained":"Explain with model";
      explain.title=modelExplanationAvailable()?"Ask the configured model to explain this verification result without changing the playbook.":"Configure a model to explain this verification result.";
      explain.addEventListener("click",()=>explainVerificationCheck(item)); tools.append(explain);
      const discuss=document.createElement("button"); discuss.type="button"; discuss.className="verification-discuss-button";
      discuss.disabled=!modelExplanationAvailable();
      discuss.textContent="Discuss in chat";
      discuss.title=modelExplanationAvailable()?"Open this verification in the Verification Assistant.":"Configure a model to discuss this verification.";
      discuss.addEventListener("click",()=>openVerificationDiscussion(item));
      tools.append(discuss); main.append(tools);
      if(cached){ const box=document.createElement("div"); box.className=`verification-explanation${cached.error?" error":""}`; const head=document.createElement("div"); head.className="verification-explanation-title"; head.textContent=cached.classification?`Explanation · ${cached.classification.replaceAll("_"," ")}`:"Explanation"; const body=document.createElement("div"); body.className="verification-explanation-markdown"; body.innerHTML=renderBasicMarkdown(cached.explanation||""); box.append(head,body); main.append(box); }
    }
    if(item.output){ const details=document.createElement("details"); details.className="verification-output-details"; const s=document.createElement("summary"); s.textContent="Output"; const pre=document.createElement("pre"); pre.textContent=item.output; details.append(s,pre); main.append(details); }
    const badge=document.createElement("div"); badge.className=`verification-status ${status}`; badge.textContent=status==="SKIPPED" ? verificationSkippedLabel(item) : status;
    if(status==="SKIPPED") badge.title="This verification was not run because its required context is not available for the current verification run.";
    row.append(main,badge); list.append(row);
  });
  const pct=Math.max(0,Math.min(100,Number(state.verification.progress)||0));
  const bar=document.querySelector("#verification-progress-bar"); if(bar) bar.style.width=`${pct}%`;
  const count=document.querySelector("#verification-progress-count"); if(count){ const done=rows.filter(x=>["PASS","FAIL","ERROR","SKIPPED"].includes(verificationStatusLabel(x.status))).length; count.textContent=`${done} / ${rows.length}`; }
  renderVerificationAssistant();
  const label=document.querySelector("#verification-progress-label");
  if(label) label.textContent=state.verification.running ? `Verification running · ${pct}%` : (state.verification.summary ? `Verification ${state.verification.summary.FAIL||state.verification.summary.ERROR ? "completed with failures" : "completed"}` : "Ready to verify");
  const summary=document.querySelector("#verification-summary");
  if(summary && state.verification.summary){ const s=state.verification.summary; summary.textContent=`PASS ${s.PASS||0} · FAIL ${s.FAIL||0} · ERROR ${s.ERROR||0} · SKIPPED ${s.SKIPPED||0}`; }
  const run=document.querySelector("#verification-run-all"); if(run){ run.disabled=state.verification.running || !state.packageInfo?.id; run.textContent=state.verification.running ? "Running…" : "Run all verifications"; }
  const exp=document.querySelector("#verification-export-json"); if(exp){ exp.disabled=!state.verification.lastResult || state.verification.running; }
}
async function loadVerificationCatalog() {
  try { const data=await request("/api/verification-catalog",{}); state.verification.catalog=data.catalog||[]; if(!state.verification.checks.length) state.verification.checks=state.verification.catalog.map(x=>({...x,status:"PENDING",message:"Waiting"})); renderVerificationPage(); }
  catch(error){ console.error(error); }
}
function stopVerificationPolling(){ if(state.verification.pollTimer) clearTimeout(state.verification.pollTimer); state.verification.pollTimer=null; }
async function pollVerificationRun(){
  if(!state.verification.runId) return;
  try{
    const data=await request("/api/verification-status",{run_id:state.verification.runId}); const v=data.verification||{};
    state.verification.checks=v.checks||[]; state.verification.progress=v.progress_percent||0; state.verification.summary=v.summary||null; state.verification.running=!v.finished; state.verification.lastResult=v;
    renderVerificationPage();
    if(!v.finished) state.verification.pollTimer=setTimeout(pollVerificationRun,450); else stopVerificationPolling();
  }catch(error){ state.verification.running=false; stopVerificationPolling(); alert(`Verification status failed: ${error.message}`); renderVerificationPage(); }
}
function exportVerificationResultsJson(){
  const v=state.verification.lastResult;
  if(!v) return;
  const packageMeta=state.packageInfo || {};
  const sourceMeta=state.source || {};
  const payload={
    schema_version:"ordo.editor.verification_results.v2",
    exported_at:new Date().toISOString(),
    editor_version:"0.2.0-alpha.20.0.96-dev",
    run_id:v.run_id || state.verification.runId || null,
    package:{
      id:packageMeta.id || null,
      filename:packageMeta.filename || packageMeta.name || null,
      source_name:packageMeta.source_name || sourceMeta.__source_name || null,
      playbook_id:sourceMeta.playbook_id || sourceMeta.id || null,
      playbook_version:sourceMeta.version || null
    },
    status:v.status || (v.finished ? "FINISHED" : "RUNNING"),
    finished:Boolean(v.finished),
    completed:Number(v.completed || 0),
    total:Number(v.total || (v.checks||[]).length || 0),
    progress_percent:Number(v.progress_percent || 0),
    summary:v.summary || {},
    checks:(v.checks || []).map(item=>({
      id:item.id || null,
      title:item.title || null,
      category:item.group || null,
      description:item.description || "",
      descriptor_file:item.descriptor_file || null,
      status:verificationStatusLabel(item.status),
      skip_kind:item.skip_kind || null,
      skip_label:item.skip_label || (verificationStatusLabel(item.status)==="SKIPPED" ? verificationSkippedLabel(item) : null),
      message:item.message || "",
      index:item.index ?? null,
      total:item.total ?? null,
      duration_ms:item.duration_ms ?? null,
      exit_code:item.exit_code ?? null,
      output:item.output || "",
      evidence_summary:item.evidence_summary || "",
      evidence:Array.isArray(item.evidence)?item.evidence:[],
      model_explanation:(()=>{ const cached=state.verification.explanations[verificationExplanationKey(item)]; return cached && !cached.error ? {explanation:cached.explanation||"",classification:cached.classification||"inconclusive",classification_normalized_from:cached.classification_normalized_from||null,model:cached.model||null,provider:cached.provider||null,locale:cached.locale||null,language:cached.language||null,usage:cached.usage||null,generated_at:cached.generated_at||null} : null; })()
    }))
  };
  const blob=new Blob([JSON.stringify(payload,null,2)+"\n"],{type:"application/json;charset=utf-8"});
  const url=URL.createObjectURL(blob); const a=document.createElement("a");
  const safe=(packageMeta.filename || packageMeta.name || sourceMeta.playbook_id || "playbook").replace(/[^A-Za-z0-9._-]+/g,"_").replace(/\.(zip|ya?ml|json)$/i,"");
  a.href=url; a.download=`${safe}_verification_results.json`; document.body.append(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),0);
}

async function runAllVerifications(){
  if(!state.packageInfo?.id || state.verification.running) return;
  stopVerificationPolling(); state.verification.running=true; state.verification.progress=0; state.verification.summary=null; state.verification.lastResult=null;
  state.verification.checks=state.verification.catalog.map(x=>({...x,status:"PENDING",message:"Waiting"})); renderVerificationPage();
  try{ const data=await request("/api/verification-start",{package_id:state.packageInfo.id}); state.verification.runId=data.run_id; pollVerificationRun(); }
  catch(error){ state.verification.running=false; alert(`Verification could not start: ${error.message}`); renderVerificationPage(); }
}

function workspacePrimarySelector(mode) {
  return {
    upload:"#upload-home-panel",
    tree:"#workspace",
    paths:"#workspace",
    replay:"#inspector",
    chat:"#inspector",
    modelchat:"#model-chat-main-panel",
    lineage:"#lineage-main-panel",
    settings:"#playbook-settings-main-panel",
    verification:"#verification-main-panel",
    help:"#inspector"
  }[mode] || "#workspace";
}
function updateWorkspaceMaximizeButton() {
  const button=document.querySelector("#workspace-maximize-toggle"); if(!button)return;
  const mode=editorMain.dataset.workspaceMode||"upload", maximized=editorMain.classList.contains("workspace-maximized");
  button.hidden=mode==="upload";
  button.textContent=maximized?"↙":"⛶";
  button.title=maximized?"Restore workspace":"Expand workspace";
  button.setAttribute("aria-label",button.title);
  button.setAttribute("aria-pressed",maximized?"true":"false");
}
function refreshWorkspaceAfterShellChange() {
  const mode=editorMain.dataset.workspaceMode||"upload";
  requestAnimationFrame(()=>{
    if(mode==="lineage"){
      if(state.lineage.viewMode==="source"&&state.lineage.sourceData?.available)renderSourceDataFlow();
      else if(state.lineage.data)renderLineageGraph();
    } else if(["tree","paths"].includes(mode)&&state.source) { rerenderKeepingInspectorDraft(); }
  });
}
function setWorkspaceMaximized(enabled) {
  const active=Boolean(enabled), mode=editorMain.dataset.workspaceMode||"upload";
  editorMain.querySelectorAll(":scope > .workspace-maximized-target").forEach(el=>el.classList.remove("workspace-maximized-target"));
  if(active){
    const target=document.querySelector(workspacePrimarySelector(mode));
    if(!target)return;
    target.classList.add("workspace-maximized-target");
  }
  editorMain.classList.toggle("workspace-maximized",active);
  document.body.classList.toggle("workspace-maximized",active);
  updateWorkspaceMaximizeButton();
  refreshWorkspaceAfterShellChange();
}
function toggleWorkspaceMaximized() { setWorkspaceMaximized(!editorMain.classList.contains("workspace-maximized")); }

function updateWorkspaceShell() {
  const loaded=!!state.source;
  editorMain.classList.toggle("source-empty", !loaded);
  const tabs=document.querySelector("#workspace-tabs"), toggle=document.querySelector("#side-pane-toggle");
  if (tabs) tabs.hidden=false;
  if (toggle) toggle.hidden=!loaded && !["modelchat","help"].includes(state.panelTab);
  document.querySelectorAll("[data-workspace-tab]").forEach(button=>{
    const mode=button.dataset.workspaceTab;button.hidden=false;
    const caps=state.packageInfo?.capabilities||{};
    const capability={tree:"show_tree",lineage:"show_data_flow",settings:"playbook_settings",verification:"verification",packagefiles:"package_files",paths:"show_path",chat:"execute",replay:"replay"}[mode];
    const baseDisabled=!loaded && !["upload","modelchat","help"].includes(mode);
    const capabilityDisabled=loaded&&capability&&caps[capability]===false;
    button.disabled=baseDisabled||capabilityDisabled;
    if(capabilityDisabled)button.title=`Unavailable for this loaded playbook: ${capability.replaceAll("_"," ")} capability was not prepared successfully.`;
  });
  if (!loaded && !["upload","modelchat","help"].includes(state.panelTab)) {
    state.panelTab="upload";
    editorMain.dataset.workspaceMode="upload";
    return;
  }
  const activeMode={upload:"upload",inspection:"tree",dialog:"paths",replay:"replay",run:"chat",modelchat:"modelchat",lineage:"lineage",settings:"settings",packagefiles:"packagefiles",verification:"verification",help:"help"}[state.panelTab] || "upload";
  editorMain.dataset.workspaceMode=activeMode;
  updateWorkspaceMaximizeButton();
}
function workspacePanelForMode(mode) { return {upload:"upload",tree:"inspection",paths:"dialog",replay:"replay",chat:"run",modelchat:"modelchat",lineage:"lineage",settings:"settings",packagefiles:"packagefiles",verification:"verification",help:"help"}[mode] || "upload"; }
function showWorkspaceTab(mode) {
  if (!state.source && !["upload","modelchat","help"].includes(mode)) return;
  const caps=state.packageInfo?.capabilities||{}, capability={tree:"show_tree",lineage:"show_data_flow",settings:"playbook_settings",verification:"verification",packagefiles:"package_files",paths:"show_path",chat:"execute",replay:"replay"}[mode];
  if(capability&&caps[capability]===false)return;
  showPanelTab(workspacePanelForMode(mode));
}
function populatePathBuilder() {
  const start=document.querySelector("#dialog-start-node"), end=document.querySelector("#dialog-end-node"); if (!start || !end || !state.graph) return;
  const previousStart=start.value || entryNodeId(); const previousEnd=end.value;
  const rows=(state.graph.nodes||[]).map(n=>({id:n.id,label:n.label||n.id}));
  const fill=(select,current)=>{ select.innerHTML=""; for (const row of rows) { const o=document.createElement("option"); o.value=row.id; o.textContent=`${row.id} — ${row.label}`; select.append(o); } if (rows.some(r=>r.id===current)) select.value=current; };
  fill(start,previousStart); fill(end,previousEnd || rows.at(-1)?.id || "");
}
function syncPathBuilder(startId,endId) { populatePathBuilder(); const a=document.querySelector("#dialog-start-node"), b=document.querySelector("#dialog-end-node"); if (a && startId) a.value=startId; if (b && endId) b.value=endId; }
function buildSelectedDialogPath() { const start=document.querySelector("#dialog-start-node")?.value, end=document.querySelector("#dialog-end-node")?.value; if (!start || !end) return; const path=shortestDialogPath(start,end); openDialogPath(path,`${start} → ${end}`,end); syncPathBuilder(start,end); }
function settingsOverviewValue(value, fallback="Not configured") { return value ? String(value) : fallback; }
function renderSettingsOverview() {
  const body=document.querySelector("#settings-overview-body"); if (!body) return;
  const sourceLabel=state.packageInfo?.filename || (state.source ? "YAML source loaded" : "Not loaded");
  const modelLabel=state.liveConfig?.model ? `${providerLabel(state.liveConfig.provider)} · ${state.liveConfig.model}` : "Not configured";
  const modelDetail=state.liveConfig?.model ? (state.liveConfig.base_url || defaultProviderBaseUrl(state.liveConfig.provider)) : "Configure provider, endpoint, model and credentials";
  const answers=state.liveAutoAnswers?.enabled ? `${state.liveAutoAnswers.filename} · ${state.liveAutoAnswers.total} recorded answers` : "Not loaded";
  const replay=state.liveGuidedReplay?.enabled ? `${state.liveGuidedReplay.filename} · checkpoint ${state.liveGuidedReplay.checkpointId}` : "Not loaded";
  body.innerHTML=`
    <section class="settings-overview-section"><h3>Source / Playbook</h3><div class="settings-overview-row"><div><strong>${escapeHtml(sourceLabel)}</strong><div class="hint">Current YAML or playbook package used by the workspace.</div></div><div class="settings-overview-actions"><button type="button" data-settings-action="yaml">Load YAML</button><button type="button" data-settings-action="playbook">Load Playbook ZIP</button></div></div></section>
    <section class="settings-overview-section"><h3>Model</h3><div class="settings-overview-row"><div><strong>${escapeHtml(modelLabel)}</strong><div class="hint">${escapeHtml(modelDetail)}</div></div><div class="settings-overview-actions"><button type="button" data-settings-action="model">Configure model</button></div></div></section>
    <section class="settings-overview-section"><h3>Auto Answers</h3><div class="settings-overview-row"><div><strong>${escapeHtml(answers)}</strong><div class="hint">Recorded analyst answers used for automatic responses.</div></div><div class="settings-overview-actions"><button type="button" data-settings-action="answers">${state.liveAutoAnswers?.enabled ? "Change file" : "Load file"}</button></div></div></section>
    <section class="settings-overview-section"><h3>Replay to Checkpoint</h3><div class="settings-overview-row"><div><strong>${escapeHtml(replay)}</strong><div class="hint">Recorded model/analyst evidence replayed before switching back to live execution.</div></div><div class="settings-overview-actions"><button type="button" data-settings-action="checkpoint">${state.liveGuidedReplay?.enabled ? "Change file" : "Load file"}</button></div></div></section>`;
  body.querySelector('[data-settings-action="yaml"]').onclick=()=>document.querySelector("#file-input")?.click();
  body.querySelector('[data-settings-action="playbook"]').onclick=()=>document.querySelector("#package-file-input")?.click();
  body.querySelector('[data-settings-action="answers"]').onclick=()=>document.querySelector("#live-auto-answers-file")?.click();
  body.querySelector('[data-settings-action="checkpoint"]').onclick=()=>document.querySelector("#live-guided-replay-file")?.click();
  body.querySelector('[data-settings-action="model"]').onclick=()=>openLiveSettingModal("connection");
}
function openUnifiedSettings() {
  if (liveSettingLocked()) { alert("Reset the current Run before changing chat settings."); return; }
  const modal=document.querySelector("#settings-overview-modal"); renderSettingsOverview(); modal.hidden=false; modal.setAttribute("aria-hidden","false");
}
function closeUnifiedSettings() { const modal=document.querySelector("#settings-overview-modal"); if (modal) { modal.hidden=true; modal.setAttribute("aria-hidden","true"); } }
function renderChatControlBar() {
  const start=document.querySelector("#chat-start-proxy"), step=document.querySelector("#chat-current-step"), settings=document.querySelector("#chat-settings"), tokenUsage=document.querySelector("#chat-token-usage"), stop=document.querySelector("#chat-stop-proxy"), reset=document.querySelector("#chat-reset-proxy"), stateButton=document.querySelector("#chat-state-proxy"), pauseButton=document.querySelector("#chat-pause-proxy"), autoButton=document.querySelector("#chat-auto-answers-proxy"); if (!start) return;
  const configured=!!state.source && !!state.packageInfo && state.packageInfo?.capabilities?.execute!==false && !!state.liveConfig.enabled;
  start.hidden=!!state.liveRunning; start.disabled=!configured; start.textContent="Execute Playbook"; start.title=configured?"Execute the loaded playbook":"Load a playbook and configure a model in Settings";
  step.hidden=!state.liveRunning; step.textContent=state.liveOutcome ? (state.liveOutcome.status === "completed" ? "Run completed" : `Run halted · ${state.liveOutcome.reason||""}`) : (state.liveCurrentId ? `${state.liveCurrentId}${state.livePaused ? " · paused":""}` : "Starting…");
  settings.hidden=false;

  if (stateButton) { stateButton.hidden=!state.liveRunning; stateButton.disabled=!state.liveRunning; }
  if (pauseButton) { pauseButton.hidden=!state.liveRunning || !!state.liveOutcome; pauseButton.disabled=!state.liveRunning || !!state.liveOutcome || state.liveBusy; pauseButton.textContent=state.livePaused ? "Resume Auto" : "Pause"; }
  if (autoButton) { autoButton.disabled=state.liveRunning || state.liveBusy; autoButton.textContent=state.liveAutoAnswers?.enabled ? "Auto Answers ✓" : "Auto Answers"; }
  if (tokenUsage) {
    const hasUsage=Number(state.liveUsage?.calls || 0) > 0;
    tokenUsage.hidden=!state.liveRunning && !state.liveOutcome;
    tokenUsage.disabled=!hasUsage;
    tokenUsage.textContent=hasUsage ? `${Number(state.liveUsage.total_tokens || 0).toLocaleString()} tokens` : "0 tokens";
    tokenUsage.title=hasUsage ? liveUsageTooltip(state.liveUsage, state.liveUsage.calls) : "Token usage will appear after the first model call";
  }
  stop.hidden=!state.liveRunning || !!state.liveOutcome || !state.liveBusy; reset.hidden=!state.liveRunning; stop.disabled=false; stop.textContent="Stop"; reset.disabled=state.liveBusy;
}


function setTreeLayoutDensity(mode, options = {}) {
  const next = ["compact", "normal", "spacious"].includes(mode) ? mode : "normal";
  state.treeLayoutDensity = next;
  document.querySelector("#tree-layout-compact")?.classList.toggle("active", next === "compact");
  document.querySelector("#tree-layout-normal")?.classList.toggle("active", next === "normal");
  document.querySelector("#tree-layout-spacious")?.classList.toggle("active", next === "spacious");
  document.querySelector("#tree-layout-controls")?.setAttribute("data-density", next);
  if (options.rerender !== false && state.source) rerenderKeepingInspectorDraft();
}
function reflowTreeLayout() {
  state.positions = {};
  state.manualPositions = new Set();
  if (state.source) rerenderKeepingInspectorDraft();
}

let treeZoom = 1;
function applyTreeZoom() {
  const c=document.querySelector("#canvas"), e=document.querySelector("#edges");
  if (!c || !e) return;
  c.style.transform=`scale(${treeZoom})`; c.style.transformOrigin="0 0";
  e.style.transform=`scale(${treeZoom})`; e.style.transformOrigin="0 0";
  document.querySelector("#tree-zoom-reset").textContent=`${Math.round(treeZoom*100)}%`;
}
function changeTreeZoom(delta) { treeZoom=Math.max(.4,Math.min(2,Math.round((treeZoom+delta)*10)/10)); applyTreeZoom(); }
function resetTreeZoom() { treeZoom=1; applyTreeZoom(); }

document.querySelectorAll("[data-workspace-tab]").forEach(button=>button.addEventListener("click",()=>showWorkspaceTab(button.dataset.workspaceTab)));
document.querySelector("#verification-run-all")?.addEventListener("click",runAllVerifications);
document.querySelector("#verification-export-json")?.addEventListener("click",exportVerificationResultsJson);
document.querySelector("#tree-layout-compact")?.addEventListener("click",()=>setTreeLayoutDensity("compact"));
document.querySelector("#tree-layout-normal")?.addEventListener("click",()=>setTreeLayoutDensity("normal"));
document.querySelector("#tree-layout-spacious")?.addEventListener("click",()=>setTreeLayoutDensity("spacious"));
document.querySelector("#tree-layout-reflow")?.addEventListener("click",reflowTreeLayout);
document.querySelector("#tree-zoom-in")?.addEventListener("click",()=>changeTreeZoom(.1));
document.querySelector("#tree-zoom-out")?.addEventListener("click",()=>changeTreeZoom(-.1));
document.querySelector("#tree-zoom-reset")?.addEventListener("click",resetTreeZoom);
setTreeLayoutDensity(state.treeLayoutDensity, { rerender: false });
document.querySelector("#side-pane-toggle")?.addEventListener("click",()=>{ editorMain.classList.toggle("side-collapsed"); const b=document.querySelector("#side-pane-toggle"),collapsed=editorMain.classList.contains("side-collapsed"); if(b){b.title=collapsed?"Expand side panel":"Collapse side panel";b.setAttribute("aria-label",b.title);b.setAttribute("aria-expanded",collapsed?"false":"true");} refreshWorkspaceAfterShellChange(); });
document.querySelector("#workspace-maximize-toggle")?.addEventListener("click",toggleWorkspaceMaximized);
document.addEventListener("keydown",event=>{if(event.key==="Escape"&&editorMain.classList.contains("workspace-maximized")){event.preventDefault();setWorkspaceMaximized(false);}});
document.querySelector("#dialog-build-path")?.addEventListener("click",buildSelectedDialogPath);
document.querySelector("#chat-settings")?.addEventListener("click",openUnifiedSettings);
document.querySelector("#chat-token-usage")?.addEventListener("click",()=>{ if (state.liveUsage?.calls) openTokenDebugModal(buildAggregateTokenDebug()); });
document.querySelectorAll("[data-settings-overview-close]").forEach(el=>el.addEventListener("click",closeUnifiedSettings));
document.querySelector("#settings-overview-close")?.addEventListener("click",closeUnifiedSettings);
document.querySelector("#chat-start-proxy")?.addEventListener("click",()=>document.querySelector("#live-start")?.click());
document.querySelector("#chat-stop-proxy")?.addEventListener("click",stopLiveRun);
document.querySelector("#chat-state-proxy")?.addEventListener("click",()=>document.querySelector("#live-state-button")?.click());
document.querySelector("#chat-pause-proxy")?.addEventListener("click",toggleLiveAutoPause);
document.querySelector("#chat-auto-answers-proxy")?.addEventListener("click",()=>document.querySelector("#live-auto-answers-file")?.click());
document.querySelector("#chat-reset-proxy")?.addEventListener("click",()=>document.querySelector("#live-reset")?.click());

document.querySelectorAll("[data-panel-tab]").forEach(button => button.addEventListener("click", () => showPanelTab(button.dataset.panelTab)));
loadRuntimeConfig();
showPanelTab(state.panelTab);
loadVerificationCatalog();
inspectorResizer.addEventListener("pointerdown", event => { const startWidth = editorMain.getBoundingClientRect().right - event.clientX; const startX = event.clientX; inspectorResizer.setPointerCapture(event.pointerId); const move = moveEvent => { const width = Math.max(300, Math.min(window.innerWidth * 0.65, startWidth + startX - moveEvent.clientX)); editorMain.style.setProperty("--side-width", `${width}px`); }; const end = () => { inspectorResizer.removeEventListener("pointermove", move); inspectorResizer.removeEventListener("pointerup", end); if (state.source) rerenderKeepingInspectorDraft(); }; inspectorResizer.addEventListener("pointermove", move); inspectorResizer.addEventListener("pointerup", end); });
window.addEventListener("resize", () => { if (state.source) rerenderKeepingInspectorDraft(); });
render();

updateWorkspaceShell();

// R3 settings assistant binding
bindPlaybookSettingsSubtabs();
bindPackageFiles();
bindSettingsAssistant();
bindVerificationAssistant();
bindModelChat();
bindLineageAssistant();
bindLineageInteractions();
bindSourceDataFlow();
document.querySelector("#live-transcript")?.addEventListener("scroll",updateLiveScrollToBottomControl,{passive:true});
document.querySelector("#live-scroll-to-bottom")?.addEventListener("click",()=>scrollLiveTranscriptToBottom("smooth"));
const liveScrollStateObserver=new MutationObserver(()=>updateLiveScrollToBottomControl());
const liveActivityNode=document.querySelector("#live-activity");
const liveSendNode=document.querySelector("#live-send");
const liveTranscriptNode=document.querySelector("#live-transcript");
if(liveActivityNode) liveScrollStateObserver.observe(liveActivityNode,{subtree:true,childList:true,characterData:true,attributes:true});
if(liveSendNode) liveScrollStateObserver.observe(liveSendNode,{attributes:true,attributeFilter:["class","data-mode","aria-label","disabled"]});
if(liveTranscriptNode) liveScrollStateObserver.observe(liveTranscriptNode,{subtree:true,childList:true});
