# Timed Shutdown/Sleep

Set timer to shutdown or sleep after a specific minute timer expires.

Built for windows only.

![Image of Home Control Interface](https://raw.githubusercontent.com/Concrete18/Timed-Shutdown-Sleep/master/Images/Screenshot.png)

## Requirements

Only required if notification is turned on in config

```pip
win10toast==0.9
```

## Features

* Allows whole numbers and decimals for minute entry.
* Detects current sleep standby time.
* If current PC sleep standby is shorter than the set timer, then it will make it long enough and change it back before initiating the action. (Closing the script before it finishes will leave the standby time on the new setting.)
* Detects if PC went to sleep before timer went off so it can cancel. This prevents any action from taking place after waking the PC up.
* Shows a notification when the selected action is close to starting.

## TODO

* Minimize to tray icon
