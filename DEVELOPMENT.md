# Development

## Requirements

- Python 3.12 or newer
- Docker for validation against the current Home Assistant container
- An AqualinkD controller for optional live read-only API checks

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r dev-requirements.txt
```

## Validation

Run all repository checks before opening a pull request:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
python -m compileall -q custom_components/aqualinkd_api
```

The test suite is intentionally lightweight. It validates value conversion,
device normalization, and command URL construction without requiring a running
Home Assistant instance or sending commands to pool equipment.

## Home Assistant import validation

The integration can be imported with the official Home Assistant image:

```bash
docker build -t aqualinkd-api-validation -f - . <<'EOF'
FROM ghcr.io/home-assistant/home-assistant:stable
COPY custom_components /config/custom_components
EOF

docker run --rm --entrypoint python aqualinkd-api-validation -c \
  "import sys; sys.path.insert(0, '/config/custom_components'); import aqualinkd_api"
```

## Architecture

- `api.py` performs HTTP requests and validates endpoint response shapes.
- `coordinator.py` polls `/api/devices` and `/api/status` once per interval.
- `sensor.py` exposes numeric telemetry and source-age diagnostics.
- `binary_sensor.py` exposes read-only controller and equipment state.
- `switch.py`, `climate.py`, and `number.py` provide opt-in controls.
- `config_flow.py` owns UI setup and options.

The coordinator treats `/api/devices` as the authoritative equipment inventory.
`config.json` is intentionally not read because it contains web presentation
settings rather than authoritative controller state.

## Safety requirements

- Never send equipment commands from tests.
- Keep controls disabled by default.
- Chemical-dosing controls must be disabled by default in the entity registry.
- Do not optimistically update states after commands; refresh from AqualinkD.
- API failures must produce unavailable entities, not cached success-shaped data.

## Release process

1. Update the integration version in `manifest.json`.
2. Update `CHANGELOG.md`.
3. Run all local validation.
4. Push the commit and confirm both **Validate** and **HACS** workflows pass.
5. Create a GitHub release tag matching the manifest version, prefixed with `v`.
