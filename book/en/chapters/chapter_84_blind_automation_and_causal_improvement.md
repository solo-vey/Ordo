# Chapter 84 — Blind Automation and Causal Playbook Improvement

A useful playbook test should not quietly teach the model the answer. In a blind run, the execution model receives the instruction package, a controlled Driver, and only the scenario facts that the current interaction is allowed to reveal. Expected scores, reference answers, prior run outcomes, and developer conclusions remain outside the model context.

Ordo supports two patterns. A step-bound Driver follows a real canonical sequence and discloses facts by stable step. A semantic-adaptive Driver lets the model choose the question order while classifying each question into neutral intents and returning only the minimal relevant facts. The second pattern is important for all-in-one or historically accumulated instructions: forcing them into invented hidden steps would test the Driver's script rather than the instructions themselves.

Completion is not quality. The Driver can prove that protocol gates were reached, but an independent evaluator must separately inspect process execution and the generated documents. A document may be structurally complete and still be generic, contradictory, or unusable.

The strongest improvement practice begins after a weak blind run. Instead of guessing why a document was poor, developers ask the same execution model for a narrow causal reconstruction: which node, prompt, template, contract, facts, and gates produced one problematic element? The answer is evidence about the model's reported execution path, not unquestionable truth. It must be checked against traces and package files.

Then the narrowest responsible component is changed, a new blind package is built, and the playbook is rerun in a clean context. The two runs become regression evidence. This turns playbook improvement from broad prompt rewriting into a controlled engineering loop.
