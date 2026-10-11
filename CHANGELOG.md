# Changelog

## 1.0.1

- Rebuilt GitHub Actions validation as separate Python and HACS workflows.
- Replaced legacy development documentation with the current test, architecture,
  safety, and release process.

## 1.0.0

- Added HACS repository metadata and branding.
- Added UI configuration and options.
- Added local polling of `/api/devices` and `/api/status`.
- Added pool, spa, chemistry, salt, temperature, pump, and freshness sensors.
- Added read-only equipment status entities.
- Added opt-in switches, heater climates, salt-generator output, and
  freeze-protection setpoint controls.
- Disabled chemical-dosing switches by default in the entity registry.
