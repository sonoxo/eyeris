from eyeris.multimodal import (
    GazeSample,
    MultimodalIntentEngine,
    NormalizedPoint,
    SemanticTarget,
    TargetBounds,
    TargetRegistry,
)
from eyeris.runtime import EyerisRuntime, InteractionFrame, InMemoryActionAdapter


def _runtime() -> EyerisRuntime:
    registry = TargetRegistry(
        [
            SemanticTarget(
                target_id="maintenance-card",
                label="Hydraulic Pump A",
                bounds=TargetBounds(0.1, 0.1, 0.45, 0.45),
                actions=("open", "create"),
                priority=1,
            ),
            SemanticTarget(
                target_id="incident-alert",
                label="Security Alert",
                bounds=TargetBounds(0.55, 0.1, 0.9, 0.45),
                actions=("open", "submit"),
                priority=1,
            ),
        ]
    )
    adapter = InMemoryActionAdapter({("maintenance-card", "open"): "Opened maintenance history"})
    return EyerisRuntime(MultimodalIntentEngine(registry=registry), action_adapter=adapter)


def test_gaze_plus_voice_executes_bounded_action() -> None:
    runtime = _runtime()
    result = runtime.process(
        InteractionFrame(
            gaze=GazeSample(NormalizedPoint(0.25, 0.25), confidence=0.95),
            voice_text="open this",
            context={"environment": "LOCAL_DEMO"},
        )
    )
    assert result.stage == "EXECUTED"
    assert result.receipt is not None
    assert result.receipt.message == "Opened maintenance history"
    assert "x" not in str(result.audit).lower()


def test_high_impact_action_requires_confirmation() -> None:
    runtime = _runtime()
    runtime.process(
        InteractionFrame(
            gaze=GazeSample(NormalizedPoint(0.70, 0.25), confidence=0.95),
            voice_text="submit this",
        )
    )
    result = runtime.process(InteractionFrame(voice_text="submit this"))
    assert result.stage == "CONFIRMATION_REQUIRED"
    assert result.command is not None
    assert result.command.requires_confirmation is True


def test_restricted_environment_is_blocked() -> None:
    runtime = _runtime()
    result = runtime.process(
        InteractionFrame(
            gaze=GazeSample(NormalizedPoint(0.25, 0.25), confidence=0.95),
            voice_text="open this",
            context={"environment": "RESTRICTED"},
        )
    )
    assert result.stage == "BLOCKED"
    assert result.policy is not None
    assert result.policy.state == "RED"
