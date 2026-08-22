#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,sys
R=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); pol=json.loads((R/'source/data-layer-first-hard-architecture-policy.json').read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ups={x:sha(R/x) for x in pol['canonical_upstream_files']}; ints={x:sha(R/x) for x in pol.get('derived_intermediate_files',[]) if (R/x).exists()}; downs={x:sha(R/x) for x in pol['downstream_projection_files']}
manifest={'schema_version':'1.1','manifest_id':'VIBE_DATA_LAYER_PROJECTION_LINEAGE_V1','generator':'materialize_data_layer_projection_lineage.py','authoring_source_of_truth':'data_layer','upstream_hashes':ups,'intermediate_hashes':ints,'downstream_hashes':downs,'upstream_bundle_sha256':hashlib.sha256(json.dumps(ups,sort_keys=True).encode()).hexdigest(),'intermediate_bundle_sha256':hashlib.sha256(json.dumps(ints,sort_keys=True).encode()).hexdigest(),'status':'CURRENT_AT_MATERIALIZATION'}
p=R/'authoring/projection_generation_manifest.json'; p.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':'PASS','manifest':str(p),'upstream_count':len(ups),'intermediate_count':len(ints),'downstream_count':len(downs)},indent=2))
