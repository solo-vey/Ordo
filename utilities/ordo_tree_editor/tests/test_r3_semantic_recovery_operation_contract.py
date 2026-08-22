
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_opcontract",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

variants=[{
 "type":"object","required":["op","path","value","basis","reason"],
 "properties":{
   "op":{"type":"string","enum":["set","replace"]},
   "path":{"type":"string"},
   "value":{},
   "basis":{"type":"string","enum":["derived","generated"]},
   "reason":{"type":"string"},
 }
}]
s=m._operation_contract_summary(variants)
assert s["required_fields"]==["basis","op","path","reason","value"]
assert s["allowed_op_values"]==["replace","set"]
assert s["allowed_basis_values"]==["derived","generated"]
print("PASS operation contract summary is dynamically derived")
