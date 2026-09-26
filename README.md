# X20 LAN Hook

Custom integration for Home Assistant/HACS focused on Xiaomi/Dreame X20 Max telemetry exposed by the official `xiaomi_home` integration.

## Goal

Expose, with local-push latency whenever the LAN payload makes it possible:

- active/current map;
- current room/segment;
- room mapping;
- raw MIoT properties useful for reverse engineering the model.

The project intentionally separates the Home Assistant entity layer from the protocol discovery layer because the exact MIoT payload used by the X20 Max for map and room state still needs to be confirmed on real hardware.

## Installation with HACS

1. HACS → Integrations → three-dot menu → Custom repositories.
2. Add `https://github.com/dCypherNx/x20-lan-hook` as an Integration.
3. Install **X20 LAN Hook**.
4. Restart Home Assistant.
5. Settings → Devices & services → Add integration → **X20 LAN Hook**.

During protocol discovery you may leave the DID empty. For normal use, configure the X20 Max DID so the hook ignores unrelated Xiaomi devices.

## Entities

- `sensor.x20_current_map` — map name/id when discovered.
- `sensor.x20_current_room` — room name/id when discovered.
- `sensor.x20_miot_properties` — count of MIoT property pairs observed; attributes contain the latest raw values keyed as `siid.piid`.

## Current discovery strategy

The hook observes all `properties_changed` packets received locally by Xiaomi Home rather than assuming one hard-coded MIoT pair.

Structured JSON-looking values are inspected for common map/room fields such as:

- `map_id`, `map_uid`;
- `rooms`, `room_information`;
- `current_room_id`, `room_id`, `segment_id`, `robot_segment`.

This is deliberately heuristic. The X20 Max mapping will be promoted to an explicit decoder once captures from real cleaning runs identify the authoritative fields.

## Debug capture

Enable **Registrar payloads MIoT no log de depuração** in the integration setup and set the logger to debug:

```yaml
logger:
  logs:
    custom_components.x20_lan_hook: debug
```

Then run controlled tests:

1. robot idle at dock;
2. start cleaning one known room;
3. cross into another room;
4. pause/resume;
5. switch floor/map if applicable;
6. return to dock.

The useful evidence is the sequence of `did / siid / piid / value` changes correlated with those transitions.

## Architecture note

The integration currently hooks the private `MIoTLan.__message_handler` method in `xiaomi_home`. That remains a compatibility risk and is intentionally isolated in `__init__.py`.

## License

MIT.
