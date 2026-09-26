from __future__ import annotations

import json
from typing import Any

from .runtime import X20Runtime


MAP_KEYS = ("map_id", "map_uid", "mapId", "mapUid")
MAP_NAME_KEYS = ("map_name", "mapName", "name")
ROOM_LIST_KEYS = ("rooms", "room_info", "room_information", "roomInformation")
CURRENT_ROOM_KEYS = ("current_room", "current_room_id", "room_id", "segment_id", "robot_segment")


def _jsonish(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped or stripped[0] not in "[{":
        return value

    try:
        return json.loads(stripped)
    except (TypeError, ValueError, json.JSONDecodeError):
        return value


def _first(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _learn_rooms(runtime: X20Runtime, payload: Any) -> None:
    payload = _jsonish(payload)
    if isinstance(payload, dict):
        rooms = _first(payload, ROOM_LIST_KEYS)
        if rooms is not None:
            _learn_rooms(runtime, rooms)

        map_id = _first(payload, MAP_KEYS)
        if map_id is not None:
            runtime.current_map_id = map_id

        if runtime.current_map_name is None:
            map_name = _first(payload, MAP_NAME_KEYS)
            if isinstance(map_name, str) and map_name:
                runtime.current_map_name = map_name

        current_room = _first(payload, CURRENT_ROOM_KEYS)
        if current_room is not None and not isinstance(current_room, (dict, list)):
            runtime.current_room_id = current_room
            runtime.current_room_name = runtime.rooms.get(str(current_room))

        room_id = payload.get("id")
        room_name = payload.get("name")
        if room_id is not None and isinstance(room_name, str) and room_name:
            runtime.rooms[str(room_id)] = room_name

        for value in payload.values():
            if isinstance(value, (dict, list)):
                _learn_rooms(runtime, value)

    elif isinstance(payload, list):
        for item in payload:
            _learn_rooms(runtime, item)


def ingest(runtime: X20Runtime, siid: int, piid: int, value: Any) -> None:
    runtime.update_property(siid, piid, value)
    _learn_rooms(runtime, value)
