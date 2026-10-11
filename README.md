# AqualinkD API for Home Assistant

A HACS-compatible custom integration that polls a local
[AqualinkD](https://github.com/aqualinkd/AqualinkD) controller and exposes its
pool status and equipment in Home Assistant.

## Features

- UI configuration; no YAML required
- Local polling of `/api/devices` and `/api/status`
- Pool, spa, air, pH, ORP, salt, pump, and source-freshness sensors
- Read-only equipment status binary sensors
- Optional equipment switches
- Optional pool and spa heater climate entities
- Optional salt-generator and freeze-protection setpoint controls
- Home Assistant diagnostics and one controller device grouping all entities

## Entities

The exact entities depend on the devices returned by AqualinkD.

| Platform | Examples | Control required |
|---|---|---|
| Sensor | Air/pool/spa temperature, pH, ORP, salt PPM, SWG output, pump RPM/watts/GPM | No |
| Sensor | Panel, chemistry, and salt-generator data age | No |
| Binary sensor | Controller ready and equipment on/off status | No |
| Switch | Pumps, spa mode, lights, auxiliaries, blower, boost | Yes |
| Climate | Pool heater and spa heater | Yes |
| Number | Salt-generator output and freeze-protection setpoint | Yes |

Equipment controls are **disabled by default**. Enabling them creates entities
that can operate physical pumps, lights, heaters, auxiliaries, and other
equipment exposed by AqualinkD.

## HACS installation

1. In HACS, open **Integrations**.
2. Select the menu and choose **Custom repositories**.
3. Add `https://github.com/wcarty/aqualinkd_api` as an **Integration**.
4. Install **AqualinkD API**.
5. Restart Home Assistant.
6. Go to **Settings > Devices & services > Add integration** and select
   **AqualinkD API**.

For the standard AqualinkD installation, use the controller IP address, port
`80`, and scheme `http`.

## Configuration

| Setting | Default | Description |
|---|---:|---|
| Host | required | AqualinkD IP address or hostname |
| Port | `80` | AqualinkD HTTP port |
| Scheme | `http` | `http` or `https` |
| Polling interval | `10` seconds | Allowed range: 5-300 seconds |
| Verify SSL | off | Verify certificates for HTTPS |
| Enable controls | off | Add command-capable entities |

Polling interval and equipment controls can be changed from the integration's
**Configure** dialog.

## Safety

Home Assistant commands are sent directly to AqualinkD and can operate physical
pool equipment. Review and disable any entities that should not be manually
controlled, especially chemical-dosing auxiliaries. The integration does not
optimistically change entity state: after a command, it polls AqualinkD and
shows the state reported by the controller.

Chemical-dosing switch entities are created disabled in the entity registry.
They should remain disabled unless the dosing hardware and independent safety
interlocks have been reviewed.

## Troubleshooting

### Cannot connect during setup

Open `http://<aqualinkd-host>/api/status` and
`http://<aqualinkd-host>/api/devices` in a browser. Both endpoints must return
JSON. The standard AqualinkD port is `80`; change it only if the daemon was
configured to listen elsewhere.

### Entities become unavailable

Home Assistant marks coordinator entities unavailable when either required API
endpoint fails. Check the AqualinkD service, controller network connection, and
Home Assistant logs rather than relying on stale values.

### Controls are missing

Open **Settings > Devices & services > AqualinkD API > Configure**, enable
equipment controls, and submit. The integration reloads and adds switches,
climates, and number entities.

### HACS does not show the integration

Verify that the repository was added as an **Integration**, not a dashboard or
theme. If an older repository view is cached, reload HACS and check for the
latest GitHub release.

## Development

```bash
python -m pip install -r dev-requirements.txt
ruff check .
pytest -q
```

## License

GPL-3.0. See [LICENSE](LICENSE).
