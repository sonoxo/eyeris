# ZYRA EYERIS — Real-World Solutions

EYERIS is designed around one interaction principle:

> **Gaze supplies context. Voice or gesture supplies intent. App state supplies meaning. Policy decides authority.**

This is intentionally different from using eye tracking as a continuously moving mouse cursor.

## System loop

```text
SENSOR / APP INPUT
      ↓
LOCAL GAZE ADAPTER
      ↓
SEMANTIC TARGET REGISTRY
      ↓
VOICE / GESTURE INTENT
      ↓
EYERIS RUNTIME
      ↓
SHADOW GLASS POLICY GATE
      ↓
GLASS ONION OBSERVABILITY
      ↓
APP-NATIVE ACTION ADAPTER
      ↓
VALIDATION + AUDIT RECEIPT
```

## What is implemented now

| Layer | Repository implementation | Status |
|---|---|---|
| Semantic gaze targeting | `src/eyeris/multimodal.py` | Implemented |
| Gaze smoothing | `GazeSmoother` | Implemented |
| App target registry | `TargetRegistry` | Implemented |
| Gaze + voice + gesture fusion | `MultimodalIntentEngine` | Implemented |
| High-impact confirmation flag | `SemanticCommand.requires_confirmation` | Implemented |
| Runtime orchestration | `src/eyeris/runtime.py` | Implemented |
| Conservative fallback policy | `DefaultPolicyGate` | Implemented for local/demo use |
| Deterministic demo action adapter | `InMemoryActionAdapter` | Implemented |
| Runtime tests | `tests/test_runtime.py` | Implemented |
| Interactive motion demo | `demo/index.html` | Implemented |
| Camera/eye-tracker adapter | hardware/platform-specific | Next integration |
| Production speech adapter | OS/browser/device-specific | Next integration |
| Production gesture adapter | vision/device-specific | Next integration |
| SHADOW GLASS remote policy service | ecosystem integration | Next integration |
| Foundry/AIP action adapters | enrollment-specific | Next integration |

## 1. Accessibility and computer control

### Problem

Traditional eye-mouse control can feel unstable because natural eye motion becomes cursor movement. Heavy smoothing reduces wobble but increases latency.

### EYERIS solution

The eye does not need to hold a pointer on an exact pixel. EYERIS resolves gaze against semantic targets already known by the app.

```text
LOOK at "Messages"
      ↓
EYERIS resolves targetId=messages
      ↓
SAY "open this"
      ↓
Action=open
      ↓
Policy allows read/navigation
      ↓
App opens Messages
```

### Implementation

Apps register target bounds, labels, actions and priorities through `SemanticTarget`. A hardware gaze adapter only needs to produce normalized gaze samples. The rest of the interaction remains device-independent.

## 2. Maintenance and readiness

### Problem

Technicians may need both hands available while inspecting equipment, reading diagnostics, or moving between work steps.

### EYERIS solution

A technician can look at a machine, card, diagram, or workflow panel and ask for the relevant state without reaching for a mouse.

```text
LOOK → Hydraulic Pump A
SAY  → "show history"
EYERIS → open maintenance history

LOOK → Work order control
SAY  → "create ticket"
EYERIS → proposal created
CONFIRM → required before material write if policy says so
```

### Implementation path

1. Asset UI registers semantic targets.
2. Asset IDs map to Ontology or maintenance-system objects.
3. Voice resolves an allowed action.
4. SHADOW GLASS evaluates user identity, mission scope, environment and action impact.
5. Action adapter calls the approved maintenance API or AIP Action.
6. Receipt records the target, action, policy state and execution result.

## 3. Defensive cybersecurity

### Problem

Analysts work across dense alert queues where speed matters, but containment actions can have material consequences.

### EYERIS solution

```text
LOOK → endpoint alert
SAY  → "explain this"
RESULT → read-only context and evidence

LOOK → same alert
SAY  → "isolate endpoint"
RESULT → confirmation required
CONFIRM → policy-gated EDR action
```

### Implementation path

Use a read-only analysis action for explanation. Register containment/remediation operations as elevated actions requiring confirmation and explicit authorization. External-model data egress remains governed by the SHADOW GLASS model/data policy layer.

## 4. Intelligence briefing and field decision support

### Problem

Operators need concise, source-linked information without losing provenance or confidence while navigating multiple panels.

### EYERIS solution

The Black House provides evidence and analytic context; EYERIS provides a hands-free interaction layer.

```text
LOOK → confidence badge
ASK  → "why is this high confidence?"
AGENT → retrieve supporting evidence
POLICY → verify allowed data/model boundary
UI → show source-linked explanation
```

The interaction layer does not create new authority over sensitive data. It uses the access rights and data handling rules of the configured environment.

## 5. Logistics and operations coordination

Operators can use gaze to select routes, assets, tasks, or supply objects while voice supplies the requested operation.

Examples:

- look at a delayed shipment → “show blockers”;
- look at a route → “show alternate route”;
- look at an asset → “show readiness”;
- look at a task → “assign to my queue” (policy-gated write);
- look at an alert → “acknowledge” (confirmation policy configurable).

## Privacy model

EYERIS distinguishes **ephemeral interaction telemetry** from **retained audit evidence**.

Raw gaze coordinates are used locally to resolve a target but are intentionally omitted from `SemanticCommand.audit_record()` and `EyerisRuntime` audit receipts. Production deployments should follow the same rule unless a separately documented use case requires retention.

Recommended defaults:

```text
RAW CAMERA FRAMES       → local / ephemeral
RAW GAZE COORDINATES    → local / ephemeral
VOICE AUDIO             → local / ephemeral when possible
TRANSCRIBED INTENT      → retain only if required
SEMANTIC TARGET ID      → auditable
REQUESTED ACTION        → auditable
POLICY DECISION         → auditable
EXECUTION RECEIPT       → auditable
```

## Production adapter contract

A real deployment should provide four adapter categories:

```text
GazeAdapter
  device sample → NormalizedPoint + confidence

VoiceAdapter
  speech / switch input → intent text or command token

GestureAdapter
  pinch / nod / switch / tap → gesture token

ActionAdapter
  SemanticCommand → authorized platform action → ActionReceipt
```

The core runtime remains independent of a specific camera, speech engine, gesture model or enterprise backend.

## Running the motion demo

The demo is a self-contained static page:

```bash
python -m http.server 8000 --directory demo
```

Then open `http://localhost:8000`.

The demo intentionally simulates sensor inputs. It does not request camera or microphone permission and therefore can be reviewed safely from a cloned repository.

## Deployment sequence

```text
1. Run tests
2. Select hardware input adapters
3. Calibrate gaze locally
4. Register semantic app targets
5. Connect speech / gesture input
6. Connect SHADOW GLASS policy decision point
7. Connect app / Foundry / AIP action adapter
8. Add negative tests + accessibility testing
9. Validate audit / rollback behavior
10. Deploy only to the authorized environment
```

## Safety and authority boundary

EYERIS can support accessibility, maintenance, logistics, defensive cyber, briefing, training, inspection, rescue, medical support and other bounded workflows. The repository does not itself authorize autonomous weapon release, target selection, unrestricted offensive cyber operations, classified processing, or access to systems/data that the configured operator is not authorized to use.
