# Timed Shutdown/Sleep

Set timer to shutdown or sleep after a specific amount of minutes.

Built for windows (Tested on Windows 10 only).

![Image of Home Control Interface](https://raw.githubusercontent.com/Concrete18/Timed-Shutdown-Sleep/main/Images/Screenshot.png)

## Features

- Can detects current sleep standby time and knows if the device is plugged in or not.
- If current PC sleep standby is shorter than the set timer, then it will make it long enough and change it back before initiating the action.
- Detects if PC went to sleep before timer went off so it can cancel. This prevents any action from taking place after waking the PC up.

## Limitations

- Force closing the script before it finishes may leave the standby time on the temp setting that is needed to not sleep early.

## Quick Start

<!-- ### Install Dependencies

```
pip install -r requirements.txt
``` -->

### Config

Create a config.json file with the following inside. Change any values that you want.

```json
{
  "settings": {
    "debug": 0
  },
  "standby": {
    "default_sleep_standby_outlet": 60,
    "default_sleep_standby_battery": 5,
    "use_default_standby": 0,
    "max_standby_time_in_min": 120
  }
}
```
