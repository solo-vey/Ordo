const fs=require('fs');
const js=fs.readFileSync('web/app.js','utf8');
function must(v,m){if(!v)throw new Error(m)}
for(const token of [
  'function finishDegradedPlaybookPreparation(pkg)',
  'Playbook loaded with warnings',
  'Inspection is available; unavailable capabilities are disabled.',
  'capabilities:pkg.capabilities||{}',
  'state.graph=pkg.graph||{nodes:[],edges:[]}',
  'capability={tree:"show_tree",lineage:"show_data_flow",settings:"playbook_settings",verification:"verification",packagefiles:"package_files",paths:"show_path",chat:"execute",replay:"replay"}',
  'state.packageInfo?.capabilities?.execute !== false',
  'This playbook is loaded for inspection, but execution is unavailable because runtime preparation failed.'
]) must(js.includes(token),`missing degraded-load UI contract: ${token}`);
console.log('PASS degraded playbook loading UI regression');
