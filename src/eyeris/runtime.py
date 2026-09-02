from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol

from .multimodal import GazeSample, MultimodalIntentEngine, SemanticCommand


@dataclass(frozen=True)
class InteractionFrame:
    """One bounded multimodal interaction frame.

    Raw gaze data may be used to resolve the current semantic target but is not
    copied into the audit receipt. Voice and gesture inputs are treated as
    ephemeral intent signals unless the caller explicitly retains them.
    """

    gaze: GazeSample | None = None
    voice_text: str | None = None
    gesture: str | None = None
    confirmation: bool = False
    context: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    state: str
    reason: str


@dataclass(frozen=True)
class ActionReceipt:
    ok: bool
    target_id: str
    action: str
    message: str
    details: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class InteractionResult:
    stage: str
    focused_target_id: str | None = None
    command: SemanticCommand | None = None
    policy: PolicyDecision | None = None
    receipt: ActionReceipt | None = None
    audit: Mapping[str, object] = field(default_factory=dict)


class PolicyGate(Protocol):
    def evaluate(self, command: SemanticCommand, context: Mapping[str, str]) -> PolicyDecision:
        ...


class ActionAdapter(Protocol):
    def execute(self, command: SemanticCommand, context: Mapping[str, str]) -> ActionReceipt:
        ...


class DefaultPolicyGate:
    """Conservative local policy used for demos and unclassified app control.

    Production deployments should replace this with the configured SHADOW GLASS
    policy service / Rego decision point. High-impact actions never execute from
    this fallback gate without an explicit confirmation frame.
    """

    def evaluate(self, command: SemanticCommand, context: Mapping[str, str]) -> PolicyDecision:
        environment = context.get("environment", "LOCAL_DEMO").upper()
        if environment in {"CLASSIFIED", "RESTRICTED", "UNKNOWN_REMOTE"}:
            return PolicyDecision(False, "RED", f"environment {environment} is not approved by the local fallback gate")
        if command.confidence < 0.60:
            return PolicyDecision(False, "AMBER", "semantic command confidence is below the execution threshold")
        return PolicyDecision(True, "GREEN", "bounded semantic action is eligible for execution")


class InMemoryActionAdapter:
    """Deterministic adapter for demos/tests.

    It performs no operating-system mutation. Registered actions are resolved to
    human-readable receipts so the same orchestration path can be exercised
    safely before a platform-specific adapter is connected.
    """

    def __init__(self, responses: Mapping[tuple[str, str], str] | None = None) -> None:
        self.responses = dict(responses or {})

    def execute(self, command: SemanticCommand, context: Mapping[str, str]) -> ActionReceipt:
        message = self.responses.get(
            (command.target_id, command.action),
            f"Executed {command.action} on {command.target_id}",
        )
        return ActionReceipt(
            ok=True,
            target_id=command.target_id,
            action=command.action,
            message=message,
            details={"adapter": "IN_MEMORY", "environment": context.get("environment", "LOCAL_DEMO")},
        )


class EyerisRuntime:
    """Orchestrates gaze + voice/gesture into a policy-gated app-native action."""

    def __init__(
        self,
        engine: MultimodalIntentEngine,
        *,
        policy_gate: PolicyGate | None = None,
        action_adapter: ActionAdapter | None = None,
    ) -> None:
        self.engine = engine
        self.policy_gate = policy_gate or DefaultPolicyGate()
        self.action_adapter = action_adapter or InMemoryActionAdapter()

    def process(self, frame: InteractionFrame) -> InteractionResult:
        if frame.gaze is not None:
            target = self.engine.observe_gaze(frame.gaze)
        else:
            target = self.engine.focused_target

        focused_target_id = target.target_id if target else None
        command = self.engine.command(voice_text=frame.voice_text, gesture=frame.gesture)
        if command is None:
            return InteractionResult(
                stage="FOCUS" if target else "IDLE",
                focused_target_id=focused_target_id,
                audit={"stage": "FOCUS" if target else "IDLE", "targetId": focused_target_id},
            )

        policy = self.policy_gate.evaluate(command, frame.context)
        audit: dict[str, object] = {
            "stage": "POLICY",
            **command.audit_record(),
            "policyState": policy.state,
            "policyReason": policy.reason,
        }

        if not policy.allowed:
            return InteractionResult(
                stage="BLOCKED",
                focused_target_id=focused_target_id,
                command=command,
                policy=policy,
                audit=audit,
            )

        if command.requires_confirmation and not frame.confirmation:
            audit["stage"] = "CONFIRMATION_REQUIRED"
            return InteractionResult(
                stage="CONFIRMATION_REQUIRED",
                focused_target_id=focused_target_id,
                command=command,
                policy=policy,
                audit=audit,
            )

        receipt = self.action_adapter.execute(command, frame.context)
        audit.update(
            {
                "stage": "EXECUTED" if receipt.ok else "FAILED",
                "receipt": {
                    "ok": receipt.ok,
                    "targetId": receipt.target_id,
                    "action": receipt.action,
                    "message": receipt.message,
                    "details": dict(receipt.details),
                },
            }
        )
        return InteractionResult(
            stage="EXECUTED" if receipt.ok else "FAILED",
            focused_target_id=focused_target_id,
            command=command,
            policy=policy,
            receipt=receipt,
            audit=audit,
        )
