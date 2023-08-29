# HASS-Solarman
HomeAssistant App for Solarman inverters

# Application
The App uses [AppDaemon](https://appdaemon.readthedocs.io/en/latest/) to run Python code.
The App fetches data from Solarman web UI using Selenium.
Your Solarman inverter page must be accessible from your Home Assistant instance (i.e., be in the same network).
Inverter data is exposed by `solarman.*` entities.

# Installation
1. Have HomeAssistant with AppDaemon Add-On installed
2. Using file editor of your choice navigate to `/config/appdaemon/apps/` directory
3. Open `apps.yaml` and add the following code:
```
solarman:
  module: solarman
  class: Solarman
  plugin: HASS
  hass_namespace: hass
  ip: ""
  user: ""
  password: ""
```
4. Insert IP of your Solarman instance and login credentials (defaults are admin/admin)
