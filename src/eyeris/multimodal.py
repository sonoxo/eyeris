from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from time import monotonic
from typing import Iterable


@dataclass(frozen=True)
class NormalizedPoint:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.x <= 1.0 or not 0.0 <= self.y <= 1.0:
            raise ValueError("NormalizedPoint coordinates must be between 0 and 1")


@dataclass(frozen=True)
class GazeSample:
    point: NormalizedPoint
    confidence: float = 1.0
    observed_at: float = field(default_factory=monotonic)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("gaze confidence must be between 0 and 1")


@dataclass(frozen=True)
class TargetBounds:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def __post_init__(self) -> None:
        values = (self.x_min, self.y_min, self.x_max, self.y_max)
        if any(value < 0.0 or value > 1.0 for value in values):
            raise ValueError("target bounds must be normalized between 0 and 1")
        if self.x_min > self.x_max or self.y_min > self.y_max:
            raise ValueError("target bound minimums must be <= maximums")

    def contains(self, point: NormalizedPoint) -> bool:
        return self.x_min <= point.x <= self.x_max and self.y_min <= point.y <= self.y_max

    @property
    def center(self) -> NormalizedPoint:
        return NormalizedPoint((self.x_min + self.x_max) / 2.0, (self.y_min + self.y_max) / 2.0)

    @property
    def area(self) -> float:
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)


@dataclass(frozen=True)
class SemanticTarget:
    target_id: str
    label: str
    bounds: TargetBounds
    actions: tuple[str, ...]
    route: str | None = None
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id is required")
        if not self.actions:
            raise ValueError("at least one semantic action is required")


@dataclass(frozen=True)
class SemanticCommand:
    target_id: str
    action: str
    modalities: tuple[str, ...]
    confidence: float
    requires_confirmation: bool = False

    def audit_record(self) -> dict[str, object]:
        # Raw gaze coordinates are intentionally excluded from audit output.
        return {
            "targetId": self.target_id,
            "action": self.action,
            "modalities": list(self.modalities),
            "confidence": round(self.confidence, 4),
            "requiresConfirmation": self.requires_confirmation,
        }


class GazeSmoother:
    """Low-pass gaze filter designed for semantic target selection, not cursor driving."""

    def __init__(self, alpha: float = 0.35, minimum_confidence: float = 0.35) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self.minimum_confidence = minimum_confidence
        self._point: NormalizedPoint | None = None

    def update(self, sample: GazeSample) -> NormalizedPoint | None:
        if sample.confidence < self.minimum_confidence:
            return self._point
        if self._point is None:
            self._point = sample.point
            return self._point
        self._point = NormalizedPoint(
            self.alpha * sample.point.x + (1.0 - self.alpha) * self._point.x,
            self.alpha * sample.point.y + (1.0 - self.alpha) * self._point.y,
        )
        return self._point


class TargetRegistry:
    def __init__(self, targets: Iterable[SemanticTarget] = ()) -> None:
        self._targets: dict[str, SemanticTarget] = {target.target_id: target for target in targets}

    def register(self, target: SemanticTarget) -> None:
        self._targets[target.target_id] = target

    def remove(self, target_id: str) -> None:
        self._targets.pop(target_id, None)

    def resolve(self, point: NormalizedPoint, nearest_radius: float = 0.08) -> SemanticTarget | None:
        hits = [target for target in self._targets.values() if target.bounds.contains(point)]
        if hits:
            # Prefer app-declared priority, then the smallest target under gaze.
            return sorted(hits, key=lambda target: (-target.priority, target.bounds.area))[0]

        nearest: tuple[float, SemanticTarget] | None = None
        for target in self._targets.values():
            center = target.bounds.center
            distance = hypot(point.x - center.x, point.y - center.y)
            if distance <= nearest_radius and (nearest is None or distance < nearest[0]):
                nearest = (distance, target)
        return nearest[1] if nearest else None


_ACTION_TERMS: dict[str, tuple[str, ...]] = {
    "open": ("open", "show", "view"),
    "select": ("select", "choose", "pick", "this"),
    "navigate": ("navigate", "go", "switch"),
    "create": ("create", "new", "add"),
    "update": ("update", "edit", "change"),
    "submit": ("submit", "send", "save"),
    "confirm": ("confirm", "yes", "approve"),
    "cancel": ("cancel", "no", "stop"),
}

_HIGH_IMPACT_ACTIONS = {"delete", "publish", "deploy", "approve", "submit", "send", "release"}


class MultimodalIntentEngine:
    """Fuse gaze, voice and simple gestures into app-native semantic commands.

    EYERIS uses gaze as context, not as a continuously moving mouse pointer. The
    currently gazed semantic target is combined with voice/gesture intent, then
    resolved against the target's explicitly registered actions.
    """

    def __init__(self, registry: TargetRegistry | None = None, smoother: GazeSmoother | None = None) -> None:
        self.registry = registry or TargetRegistry()
        self.smoother = smoother or GazeSmoother()
        self.focused_target: SemanticTarget | None = None

    def observe_gaze(self, sample: GazeSample) -> SemanticTarget | None:
        point = self.smoother.update(sample)
        if point is not None:
            self.focused_target = self.registry.resolve(point)
        return self.focused_target

    def _resolve_action(self, target: SemanticTarget, voice_text: str | None, gesture: str | None) -> str | None:
        allowed = {action.lower(): action for action in target.actions}

        if voice_text:
            text = voice_text.strip().lower()
            for canonical, terms in _ACTION_TERMS.items():
                if canonical in allowed and any(term in text for term in terms):
                    return allowed[canonical]
            for action_key, original in allowed.items():
                if action_key in text:
                    return original

        gesture_key = (gesture or "").strip().lower()
        if gesture_key in {"pinch", "tap", "nod"}:
            for preferred in ("select", "open", "confirm"):
                if preferred in allowed:
                    return allowed[preferred]
        if gesture_key in {"shake", "head_shake"} and "cancel" in allowed:
            return allowed["cancel"]
        return None

    def command(self, *, voice_text: str | None = None, gesture: str | None = None) -> SemanticCommand | None:
        target = self.focused_target
        if target is None:
            return None
        action = self._resolve_action(target, voice_text, gesture)
        if action is None:
            return None

        modalities = ["gaze"]
        if voice_text:
            modalities.append("voice")
        if gesture:
            modalities.append("gesture")

        confidence = min(1.0, 0.55 + 0.15 * (len(modalities) - 1) + 0.1 * max(target.priority, 0))
        requires_confirmation = action.lower() in _HIGH_IMPACT_ACTIONS
        return SemanticCommand(
            target_id=target.target_id,
            action=action,
            modalities=tuple(modalities),
            confidence=confidence,
            requires_confirmation=requires_confirmation,
        )
