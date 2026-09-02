# ZYRA EYERIS // Multimodal Intent Control

![EYERIS multimodal loop](./assets/eyeris-multimodal-loop.svg)

## Goal

EYERIS should feel like a native extension of the application, not a shaky webcam mouse.

The interaction model is:

```text
LOOK at a semantic target
        ↓
SPEAK an intent or make a simple gesture
        ↓
EYERIS resolves the target against app state
        ↓
SHADOW GLASS checks the requested capability
        ↓
GLASS ONION records the decision path
        ↓
THE APP executes a bounded semantic action
```

## Why this is different from a gaze-controlled cursor

A cursor asks: **what pixel are the eyes pointing at?**

EYERIS asks: **which meaningful app object is the user looking at, and what do they want to do with it?**

That difference matters because eyes naturally make saccades and micro-movements. Driving a cursor directly from raw gaze produces visible jitter and forces the user to stare unnaturally. EYERIS instead smooths gaze enough to select a semantic target and then lets voice or gesture disambiguate the action.

## Current implemented core

`src/eyeris/multimodal.py` now implements:

- normalized gaze samples;
- low-pass gaze smoothing;
- semantic target registration;
- target hit testing plus bounded nearest-target recovery;
- target priority for overlapping UI regions;
- voice intent → registered action resolution;
- pinch/tap/nod → select/open/confirm resolution;
- head-shake → cancel resolution;
- high-impact action confirmation flags;
- audit records that omit raw gaze coordinates.

Tests live in `tests/test_multimodal.py`.

## Target registration model

Host applications should expose meaningful interaction surfaces to EYERIS.

Example:

```python
from eyeris.multimodal import SemanticTarget, TargetBounds

SemanticTarget(
    target_id="ticket-42",
    label="Pump maintenance ticket",
    bounds=TargetBounds(0.10, 0.10, 0.40, 0.30),
    actions=("open", "select", "update", "submit"),
    priority=1,
)
```

This means EYERIS does not need to infer every operation from pixels or DOM structure. The application tells EYERIS what a target *is* and which actions are legal.

## Interaction examples

### Gaze + voice

```text
User looks at Equipment row 7
User says: "open this"
EYERIS resolves:
  target = equipment-row-7
  action = open
  modalities = gaze + voice
```

### Gaze + gesture

```text
User looks at a dashboard card
User pinches
EYERIS resolves:
  target = dashboard-card
  action = select
```

### Elevated-impact action

```text
User looks at a release control
User says: "submit this"
EYERIS resolves the action
SHADOW GLASS marks it confirmation-required
No automatic external side effect occurs until the approval gate passes
```

## Intended ZYRA architecture

```text
CAMERA / EYE LANDMARKS
        ↓
LOCAL GAZE ESTIMATOR
        ↓
EPHEMERAL GAZE SAMPLE
        ↓
EYERIS GAZE SMOOTHER
        ↓
SEMANTIC TARGET REGISTRY ← host app state / route / UI capabilities
        ↓
FOCUSED TARGET
        ↓
VOICE / GESTURE INTENT
        ↓
MULTIMODAL INTENT ENGINE
        ↓
SHADOW GLASS
        ↓
GLASS ONION
        ↓
APP-NATIVE ACTION / AIP ACTION / ZYRA TOOL
```

## Privacy architecture

Raw eye-position streams can reveal highly sensitive behavioral information. EYERIS therefore uses a local-first privacy posture:

1. Process raw camera/eye landmarks locally whenever possible.
2. Convert raw gaze into a short-lived normalized point.
3. Resolve the point into a semantic target.
4. Audit the target/action/modality decision, not raw eye coordinates.
5. Do not create biometric identity profiles.
6. Do not persist gaze history by default.
7. External models receive semantic context only when SHADOW GLASS egress policy permits it.

This extends the existing repository rule that EYERIS is non-identifying.

## Smoothness targets

For an interaction that feels closer to the reference design than a mouse emulator, optimize for:

- camera/gaze sampling at a stable interactive rate;
- local gaze smoothing with minimal lag;
- large semantic hit regions instead of pixel-perfect targeting;
- target hysteresis so focus does not bounce between adjacent controls;
- visual target highlighting immediately after focus resolves;
- voice/gesture fusion rather than dwell-click as the primary activation method;
- app-native actions for common operations;
- LLM reasoning only for genuinely ambiguous or multi-step intents.

## Next implementation layers

### Layer 1 — browser/web SDK

Expose a lightweight React/TypeScript adapter that registers visible components and app-native actions with EYERIS.

### Layer 2 — camera gaze estimator

Add a local landmark/gaze provider behind a replaceable adapter interface. The semantic engine must remain independent of any one camera/model vendor.

### Layer 3 — multimodal runtime

Fuse:

- gaze target;
- speech transcript;
- pinch/hand gesture;
- optional nod/shake;
- current application route/state;
- approved ZYRA / AIP tools.

### Layer 4 — accessibility calibration

Per-user calibration should tune smoothing, target expansion, dwell fallback, dominant-eye handling, head-pose tolerance, and modality preferences without creating identity recognition profiles.

### Layer 5 — AIP / Foundry action bridge

Semantic commands can map to governed Ontology Actions only after SHADOW GLASS verifies data scope, identity, tool authority, and confirmation requirements.

## Design invariant

> **Gaze provides context. Voice and gesture provide intent. App-native tools provide reliable execution. Policy provides authority.**

That is the target experience for ZYRA EYERIS.
