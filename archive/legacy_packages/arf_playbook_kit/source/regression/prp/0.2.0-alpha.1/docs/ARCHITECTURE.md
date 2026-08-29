# Architecture

PRP is the orchestration playbook.
PRH is the embedded execution and evaluation module.

ARF authoring process
→ creates or updates an applied playbook
→ invokes PRP at a regression checkpoint
→ PRP invokes PRH evaluators
→ optional external chat/API execution
→ results return to PRP
→ PRP issues separated verdicts and improvement instructions.

The original authoring chat remains the controlling session because it knows the change intent and prior version lineage. Separate chats are evidence-producing workers, not the final promotion authority.
