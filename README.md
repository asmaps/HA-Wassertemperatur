# Wassertemperatur (Home Assistant Custom Integration)

Track the water temperature (°C) of a lake from https://www.wassertemperatur.org/ as a sensor in Home Assistant.

This repository provides a HACS-installable custom integration. During setup, you select the lake by providing its page URL from wassertemperatur.org.

## Features
- One sensor per configured lake with the current water temperature in °C
- Config Flow (UI) setup
- Options flow to change the lake later
- Data update every 30 minutes (configurable by editing const.py)

## Installation (via HACS)
1. In Home Assistant, install HACS if you haven’t already: https://hacs.xyz/
2. In HACS → Integrations, open the three-dot menu → Custom repositories.
3. Add this repository URL, select category "Integration", and click Add.
4. Find "Wassertemperatur" in HACS → Integrations and click Install.
5. Restart Home Assistant when prompted.

## Configuration
1. Go to Settings → Devices & Services → Add Integration.
2. Search for "Wassertemperatur".
3. Paste the full lake URL from https://www.wassertemperatur.org/ for the lake you want to track.
   - Example: https://www.wassertemperatur.org/deutschland/nordrhein-westfalen/baldeneysee/
4. The integration validates the URL by fetching the page and parsing the current temperature.
5. After adding, you’ll get a sensor entity showing the temperature in °C.

You can change the lake later from the integration’s Options.

## Notes
- This integration fetches public HTML pages and parses the temperature value displayed. If the page layout changes, parsing may break. Please open an issue/PR if parsing fails for a specific lake.
- Update interval defaults to 30 minutes. If you need a different interval, you can adjust `DEFAULT_UPDATE_INTERVAL_MINUTES` in `custom_components/wassertemperatur/const.py`.

## Attribution
Data provided by https://www.wassertemperatur.org/.

## Manual Installation (alternative)
Copy the `custom_components/wassertemperatur` folder into your Home Assistant `config/custom_components` directory, restart Home Assistant, and add the integration via the UI.

## Development
- Domain: `wassertemperatur`
- Files:
  - `__init__.py`: sets up the DataUpdateCoordinator and forwards to the sensor platform.
  - `api.py`: lightweight async client fetching and parsing temperature and lake name.
  - `sensor.py`: exposes the temperature as a sensor entity.
  - `config_flow.py`: handles setup and options (URL-based selection).
  - `const.py`: constants and defaults.
  - `translations/` and `strings.json`: UI strings and error messages.

## License
MIT (or your preferred license)
