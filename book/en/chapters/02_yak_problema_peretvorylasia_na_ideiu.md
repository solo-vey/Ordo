# How a Problem Became an Idea: Why Prompts Were Not Enough

![Nebu — thinking](../assets/mascots/64x64/Nebu_thinking_64x64.png)

The idea of Ordo did not appear all at once. At first, it might have seemed that we had simply decided to create a new language for describing processes. But an honest look at the path shows something else: the language did not arise from a desire to invent another format. It arose from a sequence of practical problems.

At the very beginning was a technological shift. The emergence of modern AI models opened an extremely attractive possibility: embedding artificial intelligence into real company processes and accelerating people's work. This was especially relevant to roles in which much of the work consists of analysis, structuring, writing, task creation, documentation, requirements alignment, and keeping processes synchronized.

One such example was the work of an analyst in a software company. An analyst performs a great deal of complex but partly repetitive work: understanding a request, clarifying details, formalizing requirements, creating tasks, preparing documentation, checking logic, keeping track of open questions, and synchronizing changes with the team. The human remains the mind of the process, but a substantial amount of routine formalization could, in theory, be delegated to an AI model.

The initial idea looked simple:

```text
there is a problem: analysts work slowly;
there is a new technology: AI models;
therefore, we can try to accelerate analysts with AI.
```

At that stage, the solution seemed obvious: write high-quality prompts and instructions. Those instructions could describe a standard analyst workflow: which questions to ask, what to check, how to format the result, when to return for clarification, and how to create documents or tasks.

The role of AI in this model was clear: the model performs the routine part of the work, while the analyst controls meaning, makes decisions, and confirms the result. Figuratively speaking, the analyst remains the head and AI becomes the hands.

But after many attempts, another problem became visible. AI really can help. It writes well, reformulates well, structures text, proposes alternatives, and produces drafts. Yet the more complex the process becomes, the worse an ordinary textual instruction performs.

When an instruction is short, the model can still keep track of it. But when a process contains many branches, conditions, backward transitions, exceptions, intermediate decisions, and checks, behavior becomes unstable. If the user distracts the model with an additional question, asks to return to a previous step, or changes a detail, the model may lose track of where it is. It starts skipping important parts, mixing stages, forgetting open questions, or behaving as if the process were already complete when it is not.

We tried to solve this problem with longer and more detailed instructions. It did not help. On the contrary, instructions grew to hundreds of kilobytes. They accumulated more rules, clarifications, exceptions, and special cases. Yet the more text there was, the harder it became for the model to execute the process consistently.

At some point, it became clear that the problem was not only prompt quality. The problem was the form of the instruction itself.

Human language is highly flexible. That is one of its strengths, but for an executable process it is also a weakness. The same action can be described in dozens of different ways. For example, a simple function that adds two numbers can be explained like this:

```text
Return the sum of two numbers.
Add the first argument to the second.
The result must be a number equal to the sum of the supplied parameters.
The function must take two values and return their addition.
```

All of these sentences mean approximately the same thing. For a human, that is normal. But in a complex process, this freedom creates a problem: the text must be interpreted every time. And when the process is large, interpretation begins to drift.

AI models often work better with code precisely because code has a stricter form. There is less room for ambiguity. A function, condition, variable, call, or return value has a concrete structure. A model can still make mistakes in code, but the format itself forces it to stay within certain rules.

That led to the key idea: perhaps processes for AI should not be described only in human language. Perhaps they need an intermediate form—more technical, structured, and stable, while still understandable to a person.

Not a full programming language in the classical sense. And not merely a long prompt. Rather, a process description language in which we can explicitly say:

```text
here is the intent;
here is the contract;
here is the state;
here is the question;
here are the possible branches;
here are the transition conditions;
here are the checks;
here is the result;
here is the template;
here is the point where human confirmation is required.
```

This is how the idea of Ordo gradually emerged.

Its roots were not in a desire to make work more complicated. Quite the opposite: the goal was to reduce chaos. We wanted to preserve natural human reasoning while giving the AI model enough explicit structure not to lose its way in long processes.

The path to Ordo can therefore be described as a chain:

```text
AI technological breakthrough
→ desire to accelerate analysts' work
→ attempt to describe processes through prompts
→ discovery of instability in long textual instructions
→ realization that a more formal form is needed
→ idea of a governed process language
```

This is how Ordo began to take shape as a practical language for AI processes. Its purpose is not to replace the human or turn every kind of work into code. Its purpose is to make a complex process explicit enough for a person to control it and for an AI model to execute it consistently.

In this sense, Ordo did not arise as an abstract language. It arose as a response to a very specific problem: ordinary prompts work well for short tasks, but long governed processes require more form, memory, boundaries, and discipline.

Ordo became an attempt to give those processes a form.
