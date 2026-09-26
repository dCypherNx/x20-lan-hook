from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class PropertyValue:
    siid: int
    piid: int
    value: Any
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class X20Runtime:
    device_did: str | None = None
    debug_capture: bool = False
    properties: dict[tuple[int, int], PropertyValue] = field(default_factory=dict)
    current_map_id: str | int | None = None
    current_map_name: str | None = None
    current_room_id: str | int | None = None
    current_room_name: str | None = None
    rooms: dict[str, str] = field(default_factory=dict)

    def accepts(self, did: str) -> bool:
        return self.device_did in (None, "", did)

    def update_property(self, siid: int, piid: int, value: Any) -> None:
        self.properties[(siid, piid)] = PropertyValue(siid=siid, piid=piid, value=value)
