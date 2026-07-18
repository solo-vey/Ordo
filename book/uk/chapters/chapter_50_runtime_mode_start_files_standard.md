# Розділ 50. Runtime Mode start files standard

Після M55 детальні runtime-правила більше не треба щоразу вставляти у великий prompt.

Кожен runtime-ready Ordo package має два стартові файли:

```text
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
```

`START_HERE_RUNTIME_MODE.md` містить повний протокол: як читати `ordo.yml`, як перевіряти source/IR, як працювати з `run_state`, як не вести guided intake “з памʼяті”, як фіксувати CLI status, як не обходити gates і як запускати artifact validation.

`START_PROMPT_RUNTIME_MODE.md` є мінімальним: він лише каже AI прочитати `START_HERE_RUNTIME_MODE.md` і почати runtime loading protocol.

Source-of-truth лишається таким:

```text
ordo.yml = manifest / entrypoint
source/program.ordo.yaml = editable source of truth
compiled/program.ir.json = runtime source for guided execution
run_state.json = current execution state
generated artifacts = rendered output
```

PDF книги не перегенеровується на цьому кроці.
