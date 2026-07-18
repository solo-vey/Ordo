# APF consumer role model

## Roles

- human_operator
- next_apf_model
- playbook_authoring_model
- language_package_model
- runtime_validation_model
- documentation_model

## next_apf_model

May:
- modify APF package
- create next APF patch
- update APF process docs

Must:
- use latest confirmed closure baseline
- activate rc.8 confirmation gates for process-changing patches
- preserve APF scope boundary

Must not:
- modify Ordo language package
- claim runtime evidence without external proof

## playbook_authoring_model

May:
- use APF package to create concrete playbook packages
- follow APF process rails

Must not:
- mutate APF baseline unless explicitly assigned APF patch work
- change language package

## language_package_model

May:
- read APF contracts as consumer requirements
- implement language/tooling support separately

Must not:
- treat APF package as language source-of-truth
- write language changes back into APF as if they were APF patches

## runtime_validation_model

May:
- consume APF evidence contracts
- run external validation outside APF if assigned

Must not:
- mark APF package runtime-ready without required external evidence

## documentation_model

May:
- rewrite or improve docs inside assigned documentation scope

Must:
- preserve current baseline, scope boundary, and confirmed decisions
