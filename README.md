# Timed Shutdown/Sleep

Set timer to shutdown or sleep after a specific minute timer expires.

![Image of Home Control Interface](https://i.imgur.com/5QFclhr.png)

## Features

* Allows whole numbers and decimals for minute entry.
* Detects current sleep standby time.
* If current PC sleep standby is shorter than the set timer, then it will make it long enough and change it back before initiating the action. (Closing the script before it finishes will leave the standby time on the new setting.)
* Detects if PC went to sleep before timer went off so it can cancel. This prevents any action from taking place after waking the PC up.

## To Do

* Warning or bring to focus if timer is close to finishing.
