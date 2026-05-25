# AqualinkD API Integration for Home Assistant

A custom Home Assistant integration designed to connect locally to the [AqualinkD](https://github.com/aqualinkd/AqualinkD) daemon. It communicates directly with the AqualinkD REST API (v2.0/3.x) to provide high-speed, local control of your Jandy AquaLink pool system.

## ✨ Features

* **Smart Device Discovery**: Scans multiple AqualinkD endpoints (`/api/devices`, `/status.json`, etc.) and automatically merges the data to ensure all equipment is found, even if named inconsistently by the API.
* **Climate Control**: Pool and Spa Heaters are presented as native Home Assistant `Climate` circular gauges, allowing you to easily view current temperatures and adjust setpoints.
* **Interactive Sliders**: Salt Water Generator (SWG) percentage and Variable Speed Pump (VSP) RPM setpoints are exposed as interactive slider entities.
* **Filtered Telemetry**: Pump data (RPM, Watts, GPM) is intelligently monitored. If a pump is turned off, the telemetry drops cleanly to `0` instead of showing as "Unavailable".
* **Dashboard Cleanup**: Automatically intercepts and hides unused Expansion Board (`Aux_B*`), Virtual (`Aux_V*`), and Extra Sensor (`Aux_S*`) circuits so your Home Assistant device list stays perfectly clean.
* **API v2.0 Standard**: Uses modern, reliable `PUT` REST commands (`/api/device/set`) to guarantee your equipment turns on and off instantly without "Bad Request" errors.
* **Live Configuration**: Change your API polling interval (down to 2 seconds) and stale timeouts directly from the Home Assistant UI without restarting.

---

## ⚙️ How It Works

Unlike standard MQTT setups, this integration relies entirely on local HTTP polling to the AqualinkD web server. 

1. **The Coordinator**: Every few seconds (configurable), the `DataUpdateCoordinator` makes parallel requests to the AqualinkD hardware.
2. **Flattening & Merging**: Because AqualinkD structures its data differently depending on the endpoint (e.g., nested `leds` arrays vs flat `devices` lists), the integration "flattens" everything into a single master list. It cross-references devices by their Hardware ID (e.g., `Aux_3`) to ensure your friendly names (e.g., `Spill Over`) are preserved.
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

1. In Home Assistant, go to **Settings > Devices & Services**.
2. Click the **+ Add Integration** button in the bottom right corner.
3. Search for **AqualinkD API**.
4. Enter your configuration details:
    * **IP Address or Hostname**: The IP address of your Raspberry Pi / device running AqualinkD (e.g., `10.38.3.194`).
    * **Port**: Usually `80` (or `8080`).
    * **Polling Interval**: How often to fetch new data. `5` seconds is recommended for fast response times.
5. Click **Submit**.

### Renaming Entities (Aux_1, Aux_2)
By default, the integration uses the labels provided by AqualinkD. If you see a generic switch like `Aux_3`, you do **not** need to edit code.
Simply click the switch in Home Assistant, hit the **Gear Icon**, and type in your preferred name (e.g., "Spillover"). Home Assistant will remember this forever!

### Advanced Options
To change how often the integration polls for data after it has been installed:
1. Go to **Settings > Devices & Services > AqualinkD API**.
2. Click the **Configure** button.
3. Adjust the sliders for the polling interval or timeouts, and click Submit. Changes take effect instantly.
