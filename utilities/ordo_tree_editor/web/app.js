const state = { source: null, graph: null, positions: {}, manualPositions: new Set(), selected: null, selectedEdge: null, pendingTransitionSource: null, inspectorTab: "fields", templates: {} };
const canvas = document.querySelector("#canvas"), edges = document.querySelector("#edges");
const empty = document.querySelector("#empty-state"), form = document.querySelector("#node-form");
const workspace = document.querySelector("#workspace"), editorMain = document.querySelector("main"), inspectorResizer = document.querySelector("#inspector-resizer");
const directFileOpen = location.protocol === "file:";
if (directFileOpen) {
  document.querySelector("#launch-warning").hidden = false;
  document.querySelector("header").hidden = true;
  document.querySelector("main").hidden = true;
}

async function request(path, payload) {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  const data = await response.json(); if (!response.ok) throw new Error(data.error || "Request failed."); return data;
}
function uniqueId(base) { const ids = new Set((state.graph?.nodes || []).map(item => item.id)); let id = base, number = 1; while (ids.has(id)) id = `${base}_${number++}`; return id; }
function sourceRecord(id) { return [...(state.source?.nodes || []), ...(state.source?.gates || [])].find(record => record.id === id); }
function selectedRecord() { return sourceRecord(state.selected); }
function selectedView() { return (state.graph?.nodes || []).find(item => item.id === state.selected); }
const NODE_WIDTH = 205, NODE_HEIGHT = 88, HORIZONTAL_GAP = 55, VERTICAL_GAP = 70, CANVAS_MARGIN = 42;
function entryNodeId() { return state.source?.graph_contract?.entry_node || state.source?.playbook?.entry_node || state.graph?.nodes?.find(item => item.element_type === "node")?.id; }
function automaticPositions() {
  const nodes = state.graph?.nodes || [], edges = state.graph?.edges || [];
  const ids = new Set(nodes.map(node => node.id)), outgoing = new Map(nodes.map(node => [node.id, []]));
  edges.forEach(edge => { if (ids.has(edge.source) && ids.has(edge.target)) outgoing.get(edge.source).push(edge.target); });
  const entry = entryNodeId(), levels = new Map(), queue = [];
  if (entry && ids.has(entry)) { levels.set(entry, 0); queue.push(entry); }
  for (let cursor = 0; cursor < queue.length; cursor += 1) {
    const source = queue[cursor], nextLevel = levels.get(source) + 1;
    (outgoing.get(source) || []).forEach(target => { if (!levels.has(target)) { levels.set(target, nextLevel); queue.push(target); } });
  }
  let finalLevel = Math.max(0, ...levels.values());
  nodes.forEach(node => { if (!levels.has(node.id)) levels.set(node.id, ++finalLevel); });
  const groups = new Map();
  nodes.forEach(node => { const level = levels.get(node.id); if (!groups.has(level)) groups.set(level, []); groups.get(level).push(node.id); });
  const widestGroup = Math.max(1, ...[...groups.values()].map(group => group.length));
  const contentWidth = widestGroup * NODE_WIDTH + (widestGroup - 1) * HORIZONTAL_GAP;
  const canvasWidth = Math.max(1050, workspace.clientWidth, contentWidth + CANVAS_MARGIN * 2);
  const positions = {};
  [...groups.keys()].sort((a, b) => a - b).forEach(level => {
    const group = groups.get(level), groupWidth = group.length * NODE_WIDTH + (group.length - 1) * HORIZONTAL_GAP;
    const startX = Math.max(CANVAS_MARGIN, (canvasWidth - groupWidth) / 2);
    group.forEach((id, index) => { positions[id] = { x: startX + index * (NODE_WIDTH + HORIZONTAL_GAP), y: CANVAS_MARGIN + level * (NODE_HEIGHT + VERTICAL_GAP) }; });
  });
  return positions;
}
function positionFor(id) { return state.positions[id]; }
function resizeCanvas() {
  const positions = Object.values(state.positions);
  const width = Math.max(1050, ...positions.map(pos => pos.x + NODE_WIDTH + CANVAS_MARGIN));
  const height = Math.max(700, ...positions.map(pos => pos.y + NODE_HEIGHT + CANVAS_MARGIN));
  canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
  edges.setAttribute("width", String(width)); edges.setAttribute("height", String(height)); edges.setAttribute("viewBox", `0 0 ${width} ${height}`);
}
function renderTransitionMode() {
  const banner = document.querySelector("#transition-mode"), text = document.querySelector("#transition-mode-text");
  const source = state.pendingTransitionSource;
  banner.hidden = !source;
  if (source) text.textContent = `Select the target node for a transition from ${source}.`;
}
function render() {
  canvas.innerHTML = ""; edges.innerHTML = '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#6680ae"/></marker></defs>';
  if (!state.source) { empty.hidden = false; return; } empty.hidden = true;
  const automatic = automaticPositions();
  (state.graph.nodes || []).forEach(node => {
    const pos = state.manualPositions.has(node.id) ? positionFor(node.id) : automatic[node.id]; state.positions[node.id] = pos;
    const element = document.createElement("article"); element.className = `node ${node.element_type || "node"} ${node.terminal ? "terminal" : ""} ${state.selected === node.id ? "selected" : ""} ${state.pendingTransitionSource === node.id ? "transition-source" : ""}`;
    element.style.left = `${pos.x}px`; element.style.top = `${pos.y}px`; element.dataset.id = node.id;
    element.innerHTML = `<div class="node-id"></div><div class="node-label"></div><div class="node-type"></div><div class="node-toolbar"><button type="button">Add transition</button></div>`;
    element.querySelector(".node-id").textContent = node.element_type === "gate" ? `◆ ${node.id}` : node.id;
    element.querySelector(".node-label").textContent = node.label;
    element.querySelector(".node-type").textContent = node.answer_type;
    const addButton = element.querySelector(".node-toolbar button");
    if (node.element_type === "terminal") addButton.hidden = true;
    addButton.addEventListener("pointerdown", event => event.stopPropagation());
    addButton.addEventListener("click", event => { event.stopPropagation(); beginTransition(node.id); });
    element.addEventListener("click", () => handleNodeClick(node.id)); makeDraggable(element); canvas.append(element);
  });
  resizeCanvas(); renderTransitionMode(); requestAnimationFrame(drawEdges); renderInspector();
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
function drawEdges() { state.graph.edges.forEach(edge => { const a = state.positions[edge.source], b = state.positions[edge.target]; if (!a || !b) return; const attributes = { x1: a.x + NODE_WIDTH / 2, y1: a.y + NODE_HEIGHT, x2: b.x + NODE_WIDTH / 2, y2: b.y }; const hit = document.createElementNS("http://www.w3.org/2000/svg", "line"); hit.classList.add("edge-hit"); Object.entries(attributes).forEach(([key, value]) => hit.setAttribute(key, String(value))); hit.addEventListener("pointerenter", event => showEdgeMenu(edge, event)); hit.addEventListener("pointermove", event => showEdgeMenu(edge, event)); hit.addEventListener("pointerleave", scheduleEdgeMenuHide); hit.addEventListener("click", event => { event.stopPropagation(); selectTransition(edge); }); edges.append(hit); const line = document.createElementNS("http://www.w3.org/2000/svg", "line"); line.classList.add("edge-line"); if (edge.storage === "gate_route") line.classList.add("gate-route"); Object.entries(attributes).forEach(([key, value]) => line.setAttribute(key, String(value))); edges.append(line); const label = document.createElementNS("http://www.w3.org/2000/svg", "text"); label.classList.add("edge-label"); label.setAttribute("x", String((attributes.x1 + attributes.x2) / 2 + 5)); label.setAttribute("y", String((attributes.y1 + attributes.y2) / 2 - 5)); label.textContent = edge.key; edges.append(label); }); }
function makeDraggable(element) { let start; element.addEventListener("pointerdown", event => { if (event.button !== 0 || state.pendingTransitionSource) return; const current = state.positions[element.dataset.id]; start = { pointerX: event.clientX, pointerY: event.clientY, nodeX: current.x, nodeY: current.y }; element.setPointerCapture(event.pointerId); }); element.addEventListener("pointermove", event => { if (!start) return; state.manualPositions.add(element.dataset.id); state.positions[element.dataset.id] = { x: Math.max(0, start.nodeX + event.clientX - start.pointerX), y: Math.max(0, start.nodeY + event.clientY - start.pointerY) }; element.style.left = `${state.positions[element.dataset.id].x}px`; element.style.top = `${state.positions[element.dataset.id].y}px`; resizeCanvas(); edges.innerHTML = '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#6680ae"/></marker></defs>'; drawEdges(); }); element.addEventListener("pointerup", () => { start = null; }); }
function selectNode(id) { state.selected = id; state.selectedEdge = null; hideEdgeMenu(); render(); }
function selectTransition(edge) { state.selectedEdge = edge; renderInspector(); }
const sectionLabels = {
  id: ["ID", "id"], kind: ["Node type", "kind"], purpose: ["Purpose", "purpose"], question: ["Question", "question"],
  inputs: ["Input parameters", "inputs"], outputs: ["Output parameters", "outputs"], questions: ["Analyst questions", "questions"],
  user_interaction: ["Analyst interaction", "user_interaction"], entry_gate: ["Entry gate", "entry_gate"], exit_gate: ["Exit gate", "exit_gate"],
  on_gap: ["Gap handling", "on_gap"], transitions: ["Transitions", "transitions"], on_answer: ["Answer transitions", "on_answer"],
  route_context: ["Route context", "route_context"], artifact_contract: ["Artifact contract", "artifact_contract"],
  expected_artifacts: ["Expected artifacts", "expected_artifacts"], order: ["Order", "order"], terminal: ["Terminal node", "terminal"],
  method: ["Evaluation method", "method"], trust_class: ["Trust class", "trust_class"], condition: ["Gate condition", "condition"],
  on_pass: ["On pass", "on_pass"], on_fail: ["On fail", "on_fail"], severity: ["Failure severity", "severity"],
};
function yamlBlock(key, value) { const content = value.trim() || "null"; const lines = content.split("\n"); return lines.length === 1 ? `${key}: ${lines[0]}` : `${key}:\n${lines.map(line => `  ${line}`).join("\n")}`; }
function updateYamlPreview() { const preview = document.querySelector("#node-yaml-preview"); preview.innerHTML = ""; document.querySelectorAll("[data-section-key]").forEach(field => { const block = document.createElement("span"); block.textContent = `${yamlBlock(field.dataset.sectionKey, field.value)}\n`; if (field.value !== field.dataset.originalValue) block.className = "yaml-change"; preview.append(block); }); }
function showInspectorTab(tab) { state.inspectorTab = tab; document.querySelector("#node-fields-view").hidden = tab !== "fields"; document.querySelector("#node-yaml-view").hidden = tab !== "yaml"; document.querySelectorAll("[data-inspector-tab]").forEach(button => button.classList.toggle("active", button.dataset.inspectorTab === tab)); if (tab === "yaml") updateYamlPreview(); }
async function deleteDirectTransition(edge) { const source = sourceRecord(edge.source); if (!source) return alert("The selected transition is no longer available."); if (!confirm(`Delete transition ${edge.source} → ${edge.target}?`)) return; if (edge.storage === "transitions") delete source.transitions?.[edge.key]; else if (edge.storage === "on_answer") delete source.on_answer?.[edge.key]; else if (edge.storage === "on_answer_next") delete source.on_answer?.next; else if (edge.storage === "next") delete source.next; else if (edge.storage === "gate_route") delete source[edge.key]; else return alert("This transition cannot be removed here."); state.selectedEdge = null; hideEdgeMenu(); await refresh(state.source); }
function renderTransitionManager(record) { const manager = document.querySelector("#node-transition-manager"), list = document.querySelector("#outgoing-transition-list"); manager.hidden = !record; if (!record) return; list.innerHTML = ""; const outgoing = (state.graph.edges || []).filter(edge => edge.source === record.id); if (!outgoing.length) list.textContent = "No transitions declared for this element."; outgoing.forEach(edge => { const row = document.createElement("div"); row.className = "transition-row"; const text = document.createElement("span"); text.textContent = `${edge.key} → ${edge.target}`; const remove = document.createElement("button"); remove.type = "button"; remove.className = "danger"; remove.textContent = "Delete"; remove.addEventListener("click", () => deleteDirectTransition(edge)); row.append(text, remove); list.append(row); }); }
function renderInspector() { const transitionPanel = document.querySelector("#transition-inspector"); transitionPanel.hidden = !state.selectedEdge; if (state.selectedEdge) { const edge = state.selectedEdge; document.querySelector("#transition-summary").textContent = `${edge.source} → ${edge.target} (${edge.key})`; document.querySelector("#delete-transition").hidden = !sourceRecord(edge.source); document.querySelector("#transition-note").textContent = "Delete removes this route from the source node or gate."; } const record = selectedRecord(), view = selectedView(); const editable = Boolean(record && view?.collection); document.querySelector("#selection-help").hidden = Boolean(view); form.hidden = !editable; renderTransitionManager(editable ? record : null); if (view && !editable) document.querySelector("#selection-help").textContent = `${view.id} is an external terminal/output. It is shown for routing, but is not an editable node or gate.`; if (!editable) return; document.querySelector("#node-summary").textContent = `${record.id} · ${view.element_type} · ${view.answer_type || record.kind || "unspecified"}`; const container = document.querySelector("#node-sections"); container.innerHTML = ""; const sections = view.sections || []; const ordered = [...sections].sort((a, b) => (sectionLabels[a.key] ? 0 : 1) - (sectionLabels[b.key] ? 0 : 1)); ordered.forEach(section => { const labels = sectionLabels[section.key] || ["Additional field", section.key]; const wrapper = document.createElement("div"); wrapper.className = "node-section"; const label = document.createElement("label"); label.textContent = `${labels[0]} (${labels[1]})`; const field = document.createElement("textarea"); field.dataset.sectionKey = section.key; field.dataset.originalValue = section.value_yaml; field.rows = Math.max(2, Math.min(12, section.value_yaml.split("\n").length + 1)); field.value = section.value_yaml; field.spellcheck = false; field.addEventListener("input", updateYamlPreview); label.append(field); wrapper.append(label); container.append(wrapper); }); showInspectorTab(state.inspectorTab); }
function rerenderKeepingInspectorDraft() { const draft = Object.fromEntries([...document.querySelectorAll("[data-section-key]")].map(field => [field.dataset.sectionKey, field.value])); render(); document.querySelectorAll("[data-section-key]").forEach(field => { if (draft[field.dataset.sectionKey] !== undefined) field.value = draft[field.dataset.sectionKey]; }); updateYamlPreview(); }
function refresh(source) { state.source = source; state.selected = null; return request("/api/parse", { source }).then(data => { state.source = data.source; state.graph = data.graph; render(); }); }
function displayValidation(validation) { const container = document.querySelector("#validation"); const issues = validation.issues || []; container.innerHTML = validation.status === "passed" ? '<p class="ok">Validation passed.</p>' : ""; issues.slice(0, 30).forEach(issue => { const el = document.createElement("div"); el.className = `issue ${issue.severity || ""}`; el.textContent = `${issue.validator}: ${issue.code} — ${issue.message}`; container.append(el); }); if (issues.length > 30) container.insertAdjacentHTML("beforeend", `<p class="hint">${issues.length - 30} additional findings are available through the CLI report.</p>`); }
document.querySelector("#file-input").addEventListener("change", async event => { const file = event.target.files[0]; if (!file) return; try { const data = await request("/api/parse", { yaml: await file.text() }); state.source = data.source; state.graph = data.graph; state.positions = {}; state.manualPositions = new Set(); state.pendingTransitionSource = null; render(); } catch (error) { alert(error.message); } });
document.querySelector("#validate").addEventListener("click", async () => { if (!state.source) return; try { const data = await request("/api/validate", { source: state.source }); displayValidation(data.validation); } catch (error) { alert(error.message); } });
document.querySelector("#download").addEventListener("click", async () => { if (!state.source) return; const data = await request("/api/export", { source: state.source }); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([data.yaml], { type: "application/x-yaml" })); link.download = "program.edited.ordo.yaml"; link.click(); URL.revokeObjectURL(link.href); });
document.querySelectorAll("[data-template]").forEach(button => button.addEventListener("click", async () => { if (!state.source) return alert("Open a YAML file first."); const templateName = button.dataset.template; if (templateName === "gate") { const gate = { id: uniqueId("G_NEW_GATE"), method: "mechanical", trust_class: "deterministic", condition: "Describe the condition this gate evaluates.", on_pass: "N_NEXT", on_fail: "STOP_VALIDATION_FAILED" }; if (!Array.isArray(state.source.gates)) state.source.gates = []; state.source.gates.push(gate); await refresh(state.source); selectNode(gate.id); return; } const template = structuredClone(state.templates[templateName]); template.id = uniqueId(template.id); if (!Array.isArray(state.source.nodes)) state.source.nodes = []; state.source.nodes.push(template); await refresh(state.source); selectNode(template.id); }));
function playbookUsesDirectTransitions() { return Boolean(state.source?.playbook) || (state.source?.nodes || []).some(node => Object.hasOwn(node, "transitions")); }
async function createTransition(sourceId, targetId) {
  if (!state.source || sourceId === targetId) return alert("Choose a different target node.");
  const source = sourceRecord(sourceId), target = (state.graph.nodes || []).find(item => item.id === targetId);
  if (!source || !target) return alert("Both nodes must exist.");
  if (target.element_type === "terminal" && !confirm(`Route ${sourceId} to external terminal ${targetId}?`)) return;
  if ((state.graph.nodes || []).find(item => item.id === sourceId)?.element_type === "gate") {
    const outcome = prompt("Gate route (pass or fail):", "pass");
    if (!outcome) return;
    const key = outcome.toLowerCase() === "pass" ? "on_pass" : outcome.toLowerCase() === "fail" ? "on_fail" : null;
    if (!key) return alert("A gate route must be pass or fail.");
    if (source[key]) return alert(`${sourceId} already has an ${outcome} route. Delete or edit it first.`);
    source[key] = targetId;
    state.pendingTransitionSource = null;
    await refresh(state.source); state.selected = sourceId; render(); return;
  }
  const label = prompt("Transition outcome label:", `to_${targetId}`);
  if (!label) return;
  const direct = Object.hasOwn(source, "transitions") || (playbookUsesDirectTransitions() && !source.on_answer);
  if (direct) {
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
  await refresh(state.source); state.selected = sourceId; render();
}
function beginTransition(sourceId) { state.pendingTransitionSource = sourceId; state.selected = sourceId; state.selectedEdge = null; hideEdgeMenu(); render(); }
function handleNodeClick(nodeId) { if (!state.pendingTransitionSource) return selectNode(nodeId); if (state.pendingTransitionSource === nodeId) { state.pendingTransitionSource = null; return render(); } createTransition(state.pendingTransitionSource, nodeId); }
async function addTransition(sourceId = state.selected || "") { if (!state.source) return; const chosenSource = prompt("Source node ID:", sourceId); const targetId = prompt("Target node ID:"); if (!chosenSource || !targetId) return; await createTransition(chosenSource, targetId); }
document.querySelector("#add-transition").addEventListener("click", () => addTransition());
document.querySelector("#add-selected-transition").addEventListener("click", () => addTransition(state.selected));
form.addEventListener("submit", async event => { event.preventDefault(); if (!state.selected) return; const sections = Object.fromEntries([...document.querySelectorAll("[data-section-key]")].map(field => [field.dataset.sectionKey, field.value])); const view = selectedView(); try { const data = await request("/api/update-node-sections", { source: state.source, old_id: state.selected, collection: view?.collection, sections }); state.source = data.source; state.graph = data.graph; state.positions = {}; state.manualPositions = new Set(); state.selected = data.node_id; render(); } catch (error) { alert(error.message); } });
document.querySelector("#delete-node").addEventListener("click", async () => { if (!state.selected) return; const view = selectedView(); const connected = (state.graph.edges || []).filter(edge => edge.source === state.selected || edge.target === state.selected); if (connected.length) return alert("This element still has transitions. Update or remove those transitions before deleting it."); if (!view?.collection || !confirm(`Delete ${state.selected}?`)) return; state.source[view.collection] = state.source[view.collection].filter(record => record.id !== state.selected); state.positions = {}; state.manualPositions = new Set(); await refresh(state.source); });
document.querySelector("#delete-transition").addEventListener("click", () => { if (state.selectedEdge) deleteDirectTransition(state.selectedEdge); });
document.querySelector("#cancel-transition-mode").addEventListener("click", () => { state.pendingTransitionSource = null; render(); });
document.querySelector("#edge-delete-action").addEventListener("click", () => { if (state.selectedEdge) deleteDirectTransition(state.selectedEdge); });
document.querySelector("#edge-context-menu").addEventListener("pointerenter", () => clearTimeout(edgeMenuTimer));
document.querySelector("#edge-context-menu").addEventListener("pointerleave", scheduleEdgeMenuHide);
document.querySelectorAll("[data-inspector-tab]").forEach(button => button.addEventListener("click", () => showInspectorTab(button.dataset.inspectorTab)));
inspectorResizer.addEventListener("pointerdown", event => { const startWidth = editorMain.getBoundingClientRect().right - event.clientX; const startX = event.clientX; inspectorResizer.setPointerCapture(event.pointerId); const move = moveEvent => { const width = Math.max(320, Math.min(window.innerWidth * 0.65, startWidth + startX - moveEvent.clientX)); editorMain.style.setProperty("--inspector-width", `${width}px`); }; const end = () => { inspectorResizer.removeEventListener("pointermove", move); inspectorResizer.removeEventListener("pointerup", end); if (state.source) rerenderKeepingInspectorDraft(); }; inspectorResizer.addEventListener("pointermove", move); inspectorResizer.addEventListener("pointerup", end); });
window.addEventListener("resize", () => { if (state.source) rerenderKeepingInspectorDraft(); });
if (!directFileOpen) Promise.all([fetch("/api/node-templates").then(r => r.json()), fetch("/api/tree-modules").then(r => r.json())]).then(([templates, modules]) => { state.templates = templates.templates; document.querySelector("#module-list").innerHTML = (modules.library.templates || []).map(item => `<p><strong>${item.id}</strong><br><span class="hint">${item.purpose}</span></p>`).join(""); }).catch(error => { document.querySelector("#module-list").textContent = `Local service unavailable: ${error.message}`; });
