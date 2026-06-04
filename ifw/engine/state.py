from __future__ import annotations

from .state_lookup import EngineLookupStateMixin
from .state_player import EnginePlayerStateMixin
from .state_progress import EngineProgressStateMixin
from .state_rooms import EngineRoomStateMixin


class EngineStateMixin(
    EngineProgressStateMixin,
    EngineLookupStateMixin,
    EngineRoomStateMixin,
    EnginePlayerStateMixin,
):
    """Compatibility mixin that composes the engine's state helpers."""
