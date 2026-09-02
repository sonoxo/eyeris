# EYERIS // RVIA Agentic Knowledge Bridge

EYERIS multimodal and visual-intelligence workflows inherit the canonical `rvia-agentic-core-v1` knowledge profile maintained in `sonoxo/gpt-doug-llm`.

Canonical profile:
`https://github.com/sonoxo/gpt-doug-llm/blob/main/safety-shield/agents/knowledge/rvia-agentic-core.json`

## EYERIS-specific extension

```text
SENSOR / APP EVENT
  → local preprocessing
  → semantic target / observation
  → minimum required context
  → model reasoning when needed
  → explicit semantic action request
  → SHADOW GLASS policy
  → bounded app/AIP action
  → validation
  → GLASS ONION audit
```

EYERIS keeps raw gaze/biometric-adjacent interaction data local and ephemeral where possible. Agents should reason over semantic targets, observations and authorized app state instead of retaining raw sensor histories by default.

Every new EYERIS agent or adapter must declare its sensor inputs, semantic outputs, allowed tools/actions, data class, retention, confirmation requirements, evals and rollback behavior.

Canonical agent builder:
`https://github.com/sonoxo/gpt-doug-llm/blob/main/safety-shield/agents/agentic_builder.py`
