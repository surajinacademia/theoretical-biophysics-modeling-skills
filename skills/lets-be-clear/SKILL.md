---
name: lets-be-clear
description: >-
  Restate a user's request clearly and ask for confirmation before acting. Use
  when the user invokes this skill or checks whether the agent understood them,
  with phrases such as "let's be clear," "am I clear?", "do you get me?", or a
  semantic equivalent, or when schematic-designer explicitly delegates its
  figure-brief confirmation. Do not trigger from ambiguity alone or from an
  ordinary retrieval or definition request.
metadata: 
  short-description: Restate a request and confirm it before action
---

# Let's Be Clear

For a delegated `schematic-designer` brief, reuse an explicitly confirmed matching
brief from the current session and return control without a second confirmation.
Otherwise apply the steps below to that brief before figure work starts. This
delegation does not activate other skills or broaden the requested deliverables.

1. Restate the user's goal, requested action, scope, constraints, and desired
   result in plain language. Preserve exact quotations and identifiers. Do not
   add requirements or permissions.
2. If different interpretations would change the work, state the ambiguity or
   ask one focused question. Keep the restatement concise.
3. Ask the user to confirm. Before confirmation, do not start the underlying
   request, including searching, editing, running commands, calling tools,
   delegating, or external communication.
4. If the user corrects the request and explicitly authorizes that corrected
   request in the same reply, accept the confirmation and proceed within that
   scope. Ask again only when the correction or what the user authorized remains
   unclear, or when the user has not confirmed the corrected request.

If explicit invocation has no current or relevant prior request, ask what the
user wants restated.
