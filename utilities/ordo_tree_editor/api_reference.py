from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import yaml

ROOT=Path(__file__).resolve().parent

TAGS=[
 {"name":"Source & Graph","description":"Parse, validate, edit and export Ordo source documents."},
 {"name":"Packages & Replay","description":"Load/export playbook packages, replay packages and GitLab-hosted archives."},
 {"name":"Runtime & Providers","description":"Configure providers, inspect runtime configuration, execute one runtime step and retrieve run artifacts."},
 {"name":"Execute Playbook","description":"Server-managed Execute Playbook runs for autonomous agents: start, advance, inspect state/transcript/debug, submit analyst input and stop."},
 {"name":"Model Chat","description":"Free Model Chat execution, polling, cancellation, export, preview and workspace files."},
 {"name":"Inspection","description":"Templates, tree modules, playbook settings, data lineage and embedded source data-flow."},
 {"name":"Assistants & Recovery","description":"Read-only model-assisted explanations, settings/data-flow assistance and recovery helpers."},
 {"name":"Verification","description":"Verification catalog, execution, polling and verification assistant."},
]

def obj(props:dict[str,Any]|None=None, required:list[str]|None=None, desc:str|None=None, additional:bool=True):
    s={"type":"object","properties":props or {},"additionalProperties":additional}
    if required:s["required"]=required
    if desc:s["description"]=desc
    return s

def p(t="string",desc="",**kw):
    d={"type":t}
    if desc:d["description"]=desc
    d.update(kw);return d

SOURCE=p("object","Parsed Ordo source mapping.",additionalProperties=True)
MESSAGES=p("array","Conversation messages; each item normally contains role/content and may contain files.",items={"type":"object","additionalProperties":True})
ATTACHMENTS=p("array","Attachment descriptors accepted by the browser/runtime transport.",items={"type":"object","additionalProperties":True})

OPS:dict[tuple[str,str],dict[str,Any]]={}
def add(method,path,tag,summary,props=None,required=None,description="",query=None,response=None,body=True):
    op={"tags":[tag],"summary":summary,"operationId":method.lower()+path.replace('/api/','').replace('/','_').replace('-','_'),"description":description or summary,
        "responses":{"200":{"description":"Successful response","content":{"application/json":{"schema":response or {"$ref":"#/components/schemas/ApiResponse"}}}},"400":{"$ref":"#/components/responses/BadRequest"},"404":{"$ref":"#/components/responses/NotFound"}}}
    if query:
        op["parameters"]=[{"name":name,"in":"query","required":bool(spec.pop("required",False)),"schema":spec,"description":spec.get("description","")} for name,spec in [(n,dict(v)) for n,v in query.items()]]
    if body:
        op["requestBody"]={"required":True,"content":{"application/json":{"schema":obj(props,required)}}}
    OPS[(method.lower(),path)]=op

# Source & Graph
add('POST','/api/parse','Source & Graph','Parse an Ordo source',{'yaml':p('string','YAML text. Use either yaml or source.'),'source':SOURCE},description='Parses YAML or accepts a source mapping and returns the normalized source plus graph projection.')
add('POST','/api/validate','Source & Graph','Validate an Ordo source',{'yaml':p('string','YAML text. Use either yaml or source.'),'source':SOURCE},description='Runs Editor source validation and returns validation diagnostics.')
add('POST','/api/export','Source & Graph','Serialize source as YAML',{'source':SOURCE},['source'])
add('POST','/api/update-node','Source & Graph','Replace one node or gate',{'source':SOURCE,'old_id':p(desc='Current node/gate id.'),'collection':p(desc='nodes or gates.',enum=['nodes','gates']),'node_yaml':p(desc='Replacement record as YAML text.')},['source','old_id','node_yaml'])
add('POST','/api/update-node-sections','Source & Graph','Update record sections',{'source':SOURCE,'old_id':p(desc='Current node/gate id.'),'collection':p(desc='nodes or gates.',enum=['nodes','gates']),'sections':p('object','Section-key to YAML-text mapping.',additionalProperties={'type':'string'})},['source','old_id','sections'])

# Packages & Replay
add('POST','/api/playbook-package','Packages & Replay','Load a playbook ZIP package',{'filename':p(desc='Original ZIP filename.'),'data_base64':p(desc='Base64-encoded ZIP bytes.')},['filename','data_base64'])
add('POST','/api/export-playbook','Packages & Replay','Export edited playbook package',{'package_id':p(desc='Loaded package id.'),'source':SOURCE},['package_id','source'])
add('POST','/api/replay-package','Packages & Replay','Load a canonical debug handoff ZIP',{'filename':p(desc='Canonical debug handoff ZIP filename.'),'data_base64':p(desc='Base64-encoded replay bytes.')},['filename','data_base64'])
add('POST','/api/gitlab-playbooks','Packages & Replay','List the first directory level from the configured GitLab tree',{'root_url':p(desc='GitLab repository tree URL. Optional when server startup configured a default root.')})
add('POST','/api/gitlab-directory','Packages & Replay','Lazy-load one GitLab directory level',{'root_url':p(desc='GitLab repository tree URL.'),'path':p(desc='Directory path under the configured GitLab root.')},['path'])
add('POST','/api/gitlab-playbook-load','Packages & Replay','Load a GitLab playbook archive',{'root_url':p(desc='GitLab repository tree URL.'),'path':p(desc='Archive path returned by gitlab-playbooks.')},['path'])
add('POST','/api/gitlab-readme','Packages & Replay','Read a GitLab directory README',{'root_url':p(desc='GitLab repository tree URL.'),'path':p(desc='README.md path returned by gitlab-playbooks.')},['path'])
add('GET','/api/gitlab-archive','Packages & Replay','Download an original GitLab ZIP archive',query={'root_url':p(desc='GitLab repository tree URL.',required=True),'path':p(desc='ZIP path returned by gitlab-playbooks.',required=True)},body=False,response={'type':'string','format':'binary'})

# Runtime & Providers
add('GET','/api/runtime-config','Runtime & Providers','Read effective runtime configuration',query={'session_id':p(desc='Optional browser session id.')},body=False)
add('GET','/api/node-templates','Inspection','List built-in node templates',body=False)
add('GET','/api/tree-modules','Inspection','Read tree module library',body=False)
add('POST','/api/provider-models','Runtime & Providers','List provider models',{'session_id':p(desc='Browser session id.'),'provider':p(desc='Provider id.',enum=['openai','mlx','custom']),'base_url':p(desc='MLX/custom provider base URL.'),'api_key':p(desc='Personal provider key when applicable.')},['provider'])
add('POST','/api/live-config','Runtime & Providers','Configure live provider session',{'session_id':p(desc='Browser session id.'),'provider':p(desc='Provider id.',enum=['openai','mlx','custom']),'base_url':p(desc='MLX/custom provider base URL.'),'model':p(desc='Selected model id.'),'api_key':p(desc='Personal OpenAI key when no shared key exists.'),'structured_output_mode':p(desc='Structured-output mode.',enum=['auto','strict_json_schema','json_object'])},['session_id','provider','model'])
add('POST','/api/provider-capability-probe','Runtime & Providers','Probe provider structured-output capability',{'session_id':p(desc='Configured browser session id.')},['session_id'])
add('POST','/api/live-step','Runtime & Providers','Execute one live playbook step',{
 'package_id':p(desc='Loaded package id.'),'session_id':p(desc='Configured browser session id.'),'run_id':p(desc='Runtime run id.'),'source':SOURCE,'state':p('object','Current canonical runtime state.',additionalProperties=True),'state_revision':p('integer','Current state revision.',minimum=0),'current_id':p(desc='Current node/gate id.'),'phase':p(desc='enter or respond.',enum=['enter','respond']),'history':p('array','Prior runtime interaction history.',items={'type':'object','additionalProperties':True}),'analyst_input':p(desc='Analyst response for respond phase.'),'analyst_override_context':p(desc='Optional analyst override context.'),'attachments':ATTACHMENTS,'previous_node_id':p(desc='Previous element for transition provenance.'),'entry_mode':p(desc='Runtime entry mode.')},['package_id','source','state','current_id'])
add('GET','/api/run-artifact','Runtime & Providers','Download a runtime artifact',query={'path':p(desc='Relative path inside runtime workspace.',required=True),'package_id':p(desc='Package id.'),'session_id':p(desc='Session id.'),'run_id':p(desc='Run id.')},body=False,response={'type':'string','format':'binary'})

# Execute Playbook — high-level server-managed orchestration over the same /api/live-step runtime boundary
add('POST','/api/execute-run-start','Execute Playbook','Create an Execute Playbook run',{'package_id':p(desc='Loaded playbook package id.'),'session_id':p(desc='Configured provider session id.'),'auto_answers_replay_id':p(desc='Optional replay_id returned by /api/replay-package.'),'advance':p('boolean','Immediately advance until analyst input, terminal, halt or error.'),'max_steps':p('integer','Maximum runtime phases when advance=true.',minimum=1,maximum=1000),'semantic_fallback_policy':p(desc='Runtime semantic fallback policy.')},['package_id'],description='Creates server-managed execution state. Unlike /api/live-step, the caller does not need to resend current state/history on every request.')
add('POST','/api/execute-run-step','Execute Playbook','Execute one managed runtime phase',{'run_id':p(desc='Execute run id.'),'analyst_input':p(desc='Optional analyst input. When omitted at a waiting node, the next loaded Auto Answer is consumed if available.'),'attachments':ATTACHMENTS},['run_id'],description='Executes exactly one enter/respond runtime phase and persists state, revision, path, transcript and debug evidence server-side.')
add('POST','/api/execute-run-advance','Execute Playbook','Advance until the next control boundary',{'run_id':p(desc='Execute run id.'),'max_steps':p('integer','Maximum runtime phases before fail-closed stop.',minimum=1,maximum=1000)},['run_id'],description='Automatically advances through deterministic/model steps and consumes loaded Auto Answers until analyst input is missing, terminal/halt/error occurs, or max_steps is reached.')
add('POST','/api/execute-run-input','Execute Playbook','Submit analyst input and optionally continue',{'run_id':p(desc='Execute run id.'),'analyst_input':p(desc='Analyst response for the current waiting node.'),'attachments':ATTACHMENTS,'advance':p('boolean','Continue automatically after accepting the input; defaults to true.'),'max_steps':p('integer','Maximum follow-on runtime phases.',minimum=1,maximum=1000)},['run_id','analyst_input'])
add('POST','/api/execute-run-stop','Execute Playbook','Stop a managed run',{'run_id':p(desc='Execute run id.')},['run_id'])
add('GET','/api/execute-run-status','Execute Playbook','Read current run state and transcript',query={'run_id':p(desc='Execute run id.',required=True)},body=False,description='Returns current element, canonical runtime state, state revision, path, transcript, outcome/error, artifact registry and debug download link.')
add('GET','/api/execute-run-debug','Execute Playbook','Download complete run debug snapshot',query={'run_id':p(desc='Execute run id.',required=True)},body=False,description='Returns state, history, transcript, full debug trace, error traceback, artifact registry and Auto Answer cursors. Intended for automated post-failure analysis.')

# Model Chat
add('POST','/api/model-chat','Model Chat','Run Model Chat synchronously',{'session_id':p(desc='Workspace/session id.'),'messages':MESSAGES,'attachments':ATTACHMENTS},['session_id','messages'])
add('POST','/api/model-chat-start','Model Chat','Start asynchronous Model Chat run',{'session_id':p(desc='Workspace/session id.'),'messages':MESSAGES,'attachments':ATTACHMENTS},['session_id','messages'],description='Starts the same Model Chat workflow as /api/model-chat in a background thread and returns run_id.')
add('POST','/api/model-chat-status','Model Chat','Poll asynchronous Model Chat run',{'run_id':p(desc='Run id returned by model-chat-start.'),'after_seq':p('integer','Only activity events with seq greater than this value are returned.',minimum=0)},['run_id'])
add('POST','/api/model-chat-cancel','Model Chat','Cancel asynchronous Model Chat run',{'run_id':p(desc='Run id returned by model-chat-start.')},['run_id'])
add('POST','/api/model-chat-export','Model Chat','Export Model Chat conversation/debug package',{'session_id':p(desc='Session id.'),'debug':p('boolean','false => Markdown export; true => diagnostic ZIP.'),'messages':MESSAGES,'attachments':ATTACHMENTS,'agent_trace':p('array',items={'type':'object','additionalProperties':True}),'usage_history':p('array',items={'type':'object','additionalProperties':True}),'errors':p('array',items={}), 'generated_files':p('array',items={'type':'object','additionalProperties':True}),'provider_info':p('object',additionalProperties=True)},['session_id','messages'])
add('POST','/api/model-chat-playbook-preview','Model Chat','Preview generated YAML or ZIP playbook',{'filename':p(desc='Displayed file name.'),'content_text':p(desc='YAML text for YAML preview.'),'content_base64':p(desc='Base64 ZIP bytes for ZIP preview.')},['filename'])
add('GET','/api/model-chat-workspace-file','Model Chat','Download a Model Chat workspace file',query={'session_id':p(desc='Workspace/session id.',required=True),'path':p(desc='Relative workspace path.',required=True)},body=False,response={'type':'string','format':'binary'})

# Inspection
add('POST','/api/template-inspector','Inspection','Inspect a node template/materialization contract',{'package_id':p(desc='Loaded package id.'),'node_id':p(desc='Node id.'),'source':SOURCE},['package_id','node_id','source'])
add('POST','/api/playbook-settings','Inspection','Read language-defined playbook settings',{'package_id':p(desc='Loaded package id; active package used when omitted.')})
add('POST','/api/package-files','Inspection','List package files or preview one package file',{'package_id':p(desc='Loaded package id; active package used when omitted.'),'mode':p(desc='list or read.',enum=['list','read']),'path':p(desc='Package-relative file path for read mode.')})
add('GET','/api/package-file-download','Inspection','Download one original file from the loaded package',query={'package_id':p(desc='Loaded package id.'),'path':p(desc='Package-relative file path.',required=True)},body=False,response={'type':'string','format':'binary'})
add('POST','/api/data-lineage','Inspection','Build reconstructed logical data lineage',{'package_id':p(desc='Loaded package id.'),'source':SOURCE,'runtime_state':p('object','Optional current runtime state for values.',additionalProperties=True)})
add('POST','/api/embedded-data-flow','Inspection','Read canonical authoring data flow',{'package_id':p(desc='Loaded package id.')},['package_id'])

# Assistants & Recovery
add('POST','/api/explain','Assistants & Recovery','Explain a selected Editor entity with the configured model',{'session_id':p(desc='Configured model session.'),'package_id':p(desc='Loaded package id.'),'kind':p(desc='Explanation kind.'),'node_id':p(desc='Selected node id.'),'collection':p(desc='nodes/gates where applicable.'),'source':SOURCE,'runtime_state':p('object',additionalProperties=True),'verification_check':p('object',additionalProperties=True)},['session_id'])
add('POST','/api/data-lineage-assistant','Assistants & Recovery','Ask the Data Flow assistant',{'session_id':p(desc='Configured model session.'),'package_id':p(desc='Loaded package id.'),'entity':p('object','Selected lineage entity.',additionalProperties=True),'context':p('object','Connected lineage context.',additionalProperties=True),'messages':MESSAGES},['session_id','entity'])
add('POST','/api/playbook-settings-assistant','Assistants & Recovery','Ask the Playbook Settings assistant',{'session_id':p(desc='Configured model session.'),'package_id':p(desc='Loaded package id.'),'mode':p(desc='Assistant mode.'),'message':p(desc='Current user message.'),'messages':MESSAGES,'resource_path':p(desc='Selected package file path when mode=resource_chat.')},['session_id','package_id','message'])
add('POST','/api/recovery-diagnose','Assistants & Recovery','Diagnose a runtime recovery situation',{'evidence':p('object','Failure/runtime evidence.',additionalProperties=True),'choices':p('array','Available recovery choices.',items={'type':'object','additionalProperties':True})},['evidence'])
add('POST','/api/recovery-chat','Assistants & Recovery','Continue conversational recovery',{'session_id':p(desc='Configured model session.'),'evidence':p('object',additionalProperties=True),'choices':p('array',items={'type':'object','additionalProperties':True}),'history':p('array',items={'type':'object','additionalProperties':True}),'state':p('object',additionalProperties=True),'state_revision':p('integer',minimum=0),'analyst_input':p(desc='Analyst recovery message.')},['session_id','evidence'])

# Verification
add('POST','/api/verification-catalog','Verification','List verification checks',{})
add('POST','/api/verification-start','Verification','Start package verification',{'package_id':p(desc='Loaded package id.')},['package_id'])
add('POST','/api/verification-status','Verification','Poll package verification',{'run_id':p(desc='Verification run id.')},['run_id'])
add('POST','/api/verification-assistant','Verification','Ask the verification assistant',{'session_id':p(desc='Configured model session.'),'package_id':p(desc='Loaded package id.'),'verification_check':p('object','Selected verification check and evidence.',additionalProperties=True),'messages':MESSAGES},['session_id','verification_check'])


def build_spec()->dict[str,Any]:
    paths:dict[str,Any]={}
    for (method,path),op in OPS.items(): paths.setdefault(path,{})[method]=op
    return {
      "openapi":"3.1.0",
      "info":{"title":"Ordo Tree Editor Local REST API","version":"0.2.0-alpha.20.0.217-dev","description":"HTTP API used by the local Ordo Tree Editor web UI. The server binds to 127.0.0.1 by default. This reference documents the current implementation; it does not make the API a remote/public service or a canonical Ordo language contract."},
      "servers":[{"url":"http://127.0.0.1:8765","description":"Default local Editor server"}],
      "tags":TAGS,
      "paths":paths,
      "components":{"schemas":{"ApiResponse":{"type":"object","required":["status"],"properties":{"status":{"type":"string","examples":["passed","failed"]}},"additionalProperties":True},"ErrorResponse":{"type":"object","required":["status","error"],"properties":{"status":{"const":"failed"},"error":{"type":"string"}},"additionalProperties":True}},"responses":{"BadRequest":{"description":"Invalid request or contract violation","content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}}},"NotFound":{"description":"Unknown endpoint/resource/run","content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}}}}}
    }

def write_specs(root:Path|None=None)->None:
    root=root or ROOT/'web'/'api-docs'; root.mkdir(parents=True,exist_ok=True)
    spec=build_spec()
    (root/'openapi.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
    rendered=yaml.safe_dump(spec,allow_unicode=True,sort_keys=False,width=120)
    (root/'openapi.yaml').write_text(rendered,encoding='utf-8')
    (root/'swagger.yaml').write_text(rendered,encoding='utf-8')

if __name__=='__main__': write_specs()
