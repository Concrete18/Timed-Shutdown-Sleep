import datetime as dt
import subprocess
import time
import sys
import os


def get_standby_time():
    # Gets Active Power scheme
    current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
    # Gets Current Scheme Sleep Standby time.
    output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
    output.split(' ')[1][:-4]
    string = 'Current AC Power Setting Index:'
    cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
    return int(int(cur_standby_time, 16) / 60)


def Timed_shutdown_sleep():
    def_standbuy = get_standby_time()
    subprocess.call(f"powercfg -change -standby-timeout-ac {def_standbuy}")
    print('Shutdown/Sleep Timer\n')
    last_run = dt.datetime.now()
    power = {1:'sleep', 2:'shutdown'}
    action = int(input('What do you want to do?\n1-Sleep  2-Shutdown\n'))
    response = float(input(f'\nHow long till you want your PC to {power[action]} in minutes.\n'))
    timer = response * 60
    print('')
    if response > def_standbuy:
        subprocess.call(f"powercfg -change -standby-timeout-ac {timer + 5}")
        print(f'Default Standby Time is {def_standbuy} minutes.\n\
            Standy Timer was changed so do not close manually so it goes back to default.\n')
    while timer > 0:
        if dt.datetime.now() - last_run >= dt.timedelta(minutes=1.1):
            response = input('Sleep Detected: Press Enter to close or type r to restart.')
            if response == 'r':
                Timed_shutdown_sleep()
            else:
                subprocess.call(f"powercfg -change -standby-timeout-ac {def_standbuy}")
                sys.exit()
        min_left = int(timer / 60)
        if min_left == 1:
            min_plur = 'Minute'
        else:
            min_plur = 'Minutes'
        print(f'System will {power[action]} in {min_left} {min_plur} and {int(timer % 60)} Seconds.        ', end='\r')
        time.sleep(1)
        timer -= 1
        last_run = dt.datetime.now()
    print('Timer Finished')
    subprocess.call(f"powercfg -change -standby-timeout-ac {def_standbuy}")
    print(f'\n{power[action].capitalize()} Initiated')
    if action == 1: # Sleep
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        time.sleep(10)
        sys.exit()
    elif action == 2: # Shutdown
        os.system("shutdown /s /t 1")
    input()


Timed_shutdown_sleep()
