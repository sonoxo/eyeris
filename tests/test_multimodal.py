from eyeris.multimodal import (
    GazeSample,
    MultimodalIntentEngine,
    NormalizedPoint,
    SemanticTarget,
    TargetBounds,
    TargetRegistry,
)


def _engine() -> MultimodalIntentEngine:
    registry = TargetRegistry(
        [
            SemanticTarget(
                target_id="ticket-42",
                label="Pump maintenance ticket",
                bounds=TargetBounds(0.10, 0.10, 0.40, 0.30),
                actions=("open", "select", "update", "submit"),
                priority=1,
            ),
            SemanticTarget(
                target_id="nav-equipment",
                label="Equipment navigation",
                bounds=TargetBounds(0.70, 0.05, 0.95, 0.20),
                actions=("navigate", "open"),
            ),
        ]
    )
    return MultimodalIntentEngine(registry=registry)


def test_gaze_plus_voice_resolves_app_native_action() -> None:
    engine = _engine()
    focused = engine.observe_gaze(GazeSample(NormalizedPoint(0.20, 0.20), confidence=0.95))
    assert focused is not None
    assert focused.target_id == "ticket-42"

    command = engine.command(voice_text="open this")
    assert command is not None
    assert command.target_id == "ticket-42"
    assert command.action == "open"
    assert command.modalities == ("gaze", "voice")
    assert command.requires_confirmation is False


def test_gaze_plus_pinch_can_select_without_voice() -> None:
    engine = _engine()
    engine.observe_gaze(GazeSample(NormalizedPoint(0.20, 0.20)))
    command = engine.command(gesture="pinch")
    assert command is not None
    assert command.action == "select"
    assert command.modalities == ("gaze", "gesture")


def test_high_impact_action_requires_confirmation() -> None:
    engine = _engine()
    engine.observe_gaze(GazeSample(NormalizedPoint(0.20, 0.20)))
    command = engine.command(voice_text="submit this")
    assert command is not None
    assert command.action == "submit"
    assert command.requires_confirmation is True


def test_raw_gaze_coordinates_are_not_written_to_audit_record() -> None:
    engine = _engine()
    engine.observe_gaze(GazeSample(NormalizedPoint(0.20, 0.20)))
    command = engine.command(voice_text="open this")
    assert command is not None
    audit = command.audit_record()
    assert "x" not in audit
    assert "y" not in audit
    assert audit["targetId"] == "ticket-42"


def test_low_confidence_gaze_does_not_replace_existing_focus() -> None:
    engine = _engine()
    engine.observe_gaze(GazeSample(NormalizedPoint(0.20, 0.20), confidence=0.95))
    focused = engine.observe_gaze(GazeSample(NormalizedPoint(0.80, 0.10), confidence=0.05))
    assert focused is not None
    assert focused.target_id == "ticket-42"
