# Introduction: The Core Idea of Ordo

![Nebu — idea](../assets/mascots/64x64/Nebu_idea_64x64.png)

The core idea of Ordo is that a complex instruction for an AI model should not be merely text. It should be an executable contract.

An ordinary prompt often describes the desired result. Ordo describes the path to that result: what must be established, which decisions may be made, where execution must stop, which checks must be passed, what counts as a completed result, and how execution should be explained.

The basic Ordo formula looks like this:

```text
intent → contract → context → state → path → steps → gates → result → handoff
```

This formula matters because it changes the entire approach to working with a model. We no longer simply ask the model to “do it well.” We define the process within which the model must operate.

Ordo does not try to turn an AI model into an ordinary deterministic program. The model remains a semantic executor: it understands text, generalizes, formulates, compares, and proposes. But Ordo defines the boundaries of that freedom.

In short:

```text
Ordo is a language for governed execution of instructions by AI models.
```

Or, even more simply:

```text
Ordo turns human intent into a process that a model can execute, validate, explain, and improve.
```

## M30 Clarification: Ordo as a Process Rail

The current core idea of Ordo is that it is neither a CLI-first runtime nor a rigid wizard. Ordo gives AI a Process Rail: a supporting structure that holds state, route, gates, backward transitions, and results while leaving the AI as an active, reasoning executor.

```text
AI reasons and communicates.
The Process Rail holds the process.
Semantic JSON IR preserves the machine-readable form of the rail.
The CLI validates deterministic parts.
```
