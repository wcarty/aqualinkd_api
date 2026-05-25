# AqualinkD API Integration for Home Assistant

A custom Home Assistant integration designed to connect locally to the [AqualinkD](https://github.com/aqualinkd/AqualinkD) daemon. It communicates directly with the AqualinkD REST API (v2.0/3.x) to monitor and control Pentair pool equipment.

## ✨ Features

* **Smart Device Discovery**: Scans multiple AqualinkD endpoints (`/api/devices`, `/status.json`, etc.) and automatically merges the data to ensure all equipment is found, even if named inconsistently across endpoints.
* **Climate Control**: Pool and Spa Heaters are presented as native Home Assistant `Climate` entities, allowing you to easily view current temperatures and adjust setpoints.
* **Interactive Sliders**: Salt Water Generator (SWG) percentage and Variable Speed Pump (VSP) RPM setpoints are exposed as interactive slider entities.
* **Filtered Telemetry**: Pump data (RPM, Watts, GPM) is intelligently monitored. If a pump is turned off, the telemetry drops cleanly to `0` instead of showing as "Unavailable".
* **Dashboard Cleanup**: Automatically intercepts and hides unused Expansion Board (`Aux_B*`), Virtual (`Aux_V*`), and Extra Sensor (`Aux_S*`) circuits so your Home Assistant device list stays clean.
* **API v2.0 Standard**: Uses modern, reliable `PUT` REST commands (`/api/device/set`) to guarantee your equipment turns on and off instantly without "Bad Request" errors.
* **Live Configuration**: Change your API polling interval (down to 2 seconds) and stale timeouts directly from the Home Assistant UI without restarting.

---

## ⚙️ How It Works

Unlike standard MQTT setups, this integration relies entirely on local HTTP polling to the AqualinkD web server.

1. **The Coordinator**: Every few seconds (configurable), the `DataUpdateCoordinator` makes parallel requests to the AqualinkD hardware.
2. **Flattening & Merging**: Because AqualinkD structures its data differently depending on the endpoint (e.g., nested `leds` arrays vs flat `devices` lists), the integration "flattens" everything into a unified device registry.
3. **Entity Routing**:
    * `Switch`: Standard relays (Filter Pump, Pool Light, Blower).
    * `Climate`: `setpoint_thermo` types (Heaters).
    * `Number`: `setpoint_swg` and Pump RPMs.
    * `Sensor`: Read-only metrics (Temperatures, Salinity, pH).

---

## 📥 Installation Instructions

### Option 1: Manual Installation

1. Ensure you have a `custom_components` folder inside your Home Assistant `/config` directory.
2. Copy the entire `aqualinkd_api` folder into `/config/custom_components/`.
    * Your file path should look like this: `/config/custom_components/aqualinkd_api/manifest.json`
3. Restart Home Assistant completely.

### Option 2: HACS (If added to GitHub)

1. Open HACS in Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add the URL of your GitHub repository and select **Integration** as the category.
4. Click **Download** on the AqualinkD API integration.
5. Restart Home Assistant.

---

## 🛠️ Setup & Configuration

### Initial Setup

1. In Home Assistant, go to **Settings > Devices & Services**.
2. Click the **+ Add Integration** button in the bottom right corner.
3. Search for **AqualinkD API**.
4. Enter your configuration details:
    * **Host**: The IP address or hostname of your device running AqualinkD (e.g., `192.168.1.100`).
    * **Port**: The port number for the AqualinkD API (default: `8080`).
    * **Scheme**: HTTP scheme to use (`http` or `https`, default: `http`).
    * **Poll Interval**: How often to fetch new data in seconds (default: `5`, minimum: `2`).
5. Click **Submit**.

### Configuration Options

After adding the integration, you can configure additional options:

#### Required Options
- **Host**: IP address or hostname of the AqualinkD server

#### Optional Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| **Port** | Integer | `8080` | API server port |
| **Scheme** | String | `http` | Use `http` or `https` |
| **Poll Interval** | Integer | `5` | Polling interval in seconds (minimum: 2) |
| **Verify SSL** | Boolean | `False` | Verify SSL certificates (only for HTTPS) |
| **Filter Pump Zeros** | Boolean | `True` | Filter pump telemetry when pump is off |
| **Zero Grace Period** | Integer | `60` | Grace period (seconds) before filtering pump zeros |
| **Stale Timeout** | Integer | `300` | Data considered stale after this many seconds |
| **Create Raw Sensors** | Boolean | `False` | Create raw JSON sensor entities for debugging |

### Reconfiguring After Installation

To change configuration options after the integration is installed:

1. Go to **Settings > Devices & Services**.
2. Find **AqualinkD API** in the list.
3. Click the **⋮** (three dots) menu and select **Reconfigure**.
4. Adjust your settings and click **Submit**. Changes take effect immediately without requiring a restart.

### Renaming Entities (Aux_1, Aux_2, etc.)

By default, the integration uses the labels provided by AqualinkD. If you see a generic switch like `Aux_3`, you do **not** need to edit code.

Simply follow these steps in Home Assistant:

1. Click on the entity in your dashboard or device list.
2. Click the **⚙️ Gear Icon** in the top right corner.
3. Edit the **Entity Name** to your preferred label (e.g., "Spillover", "Fountain").
4. Click **Update**. Home Assistant will remember this name even after restarts.

---

## 📊 Supported Entity Types

### Climate (Heater Control)
* Pool Heater setpoint
* Spa Heater setpoint

### Switches (Relay Control)
* Filter Pump
* Pool Light
* Spa Light
* Blower
* Aux circuits

### Number (Adjustable Setpoints)
* SWG percentage (0-100%)
* Variable Speed Pump RPM

### Sensors (Read-Only Telemetry)
* Water Temperature (Pool, Spa)
* Air Temperature
* Salt Level (ppm)
* pH Level
* ORP Level
* Pump RPM
* Pump Watts
* Pump GPM
* System Status

### Binary Sensors
* Equipment status states

---

## 🔍 Troubleshooting

### Integration won't add
* **Check connectivity**: Verify the AqualinkD host/IP is reachable and the correct port is used.
* **Firewall**: Ensure Home Assistant can access the AqualinkD port (usually `8080`).
* **Credentials**: If using HTTPS with self-signed certificates, ensure `Verify SSL` is disabled.

### Entities showing as "Unavailable"
* **Polling interval**: Try increasing the polling interval if your network is slow.
* **Stale timeout**: Increase the stale timeout value if data updates are infrequent.
* **Data filtering**: Check if `Create Raw Sensors` is enabled for debugging raw responses.

### Pump telemetry always showing 0
* **Zero filtering**: Disable `Filter Pump Zeros` in configuration if the pump is legitimately running.
* **Grace period**: Adjust `Zero Grace Period` if filtering is triggering too aggressively.

### Changes to setpoints don't take effect
* **API version**: Ensure your AqualinkD version supports `/api/device/set` endpoint (v2.0+).
* **Permissions**: Check that the AqualinkD daemon has proper permissions to control devices.

### Performance issues
* **Polling too frequent**: Avoid setting poll interval below `2` seconds.
* **Raw sensors**: Disable `Create Raw Sensors` if not needed for debugging.
* **Network latency**: Check for network connectivity issues to the AqualinkD host.

---

## 🔧 Advanced Configuration

### Using HTTPS

To use HTTPS with your AqualinkD server:

1. Set **Scheme** to `https`
2. Set **Port** to `443` (or your custom HTTPS port)
3. If using self-signed certificates, keep **Verify SSL** disabled

### Debugging with Raw Sensors

Enable **Create Raw Sensors** to generate sensor entities containing raw API responses:

* `sensor.aqualinkd_api_raw_devices` - Raw `/api/devices` response
* `sensor.aqualinkd_api_raw_status` - Raw `/status.json` response

These are useful for troubleshooting device discovery or unexpected entity behavior.

---

## 📝 Supported Platforms

- `sensor` - Read-only telemetry and state sensors
- `binary_sensor` - Binary state sensors
- `switch` - Controllable relay switches
- `number` - Numeric setpoint controls
- `climate` - Climate entities for heater control

---

## 🐛 Known Limitations

* Requires local network access to AqualinkD (no cloud support)
* Depends on AqualinkD daemon being running and accessible
* Some advanced AqualinkD features may not be exposed as Home Assistant entities
* Renaming entities only affects Home Assistant display; device names in AqualinkD remain unchanged

---

## 📞 Support & Issues

If you encounter issues:

1. **Enable debug logging**: Add this to your `configuration.yaml`:
   ```yaml
   logger:
     logs:
       custom_components.aqualinkd_api: debug
   ```

2. **Check logs**: Go to **Settings > System > Logs** and look for `aqualinkd_api` entries.

3. **Gather information**:
   * Home Assistant version
   * AqualinkD version and API endpoint
   * Network setup (local IP, port, etc.)
   * Error messages from logs

4. **Create an issue**: Include the above information when reporting problems on GitHub.

---

## 📄 License

This integration is licensed under the GNU General Public License v3.0.

## 🤝 Contributing

Contributions are welcome! Please ensure documentation is updated with any new features or configuration options.
