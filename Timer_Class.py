import json
import subprocess
import threading
import time
import sys
import os
import datetime as dt

class Timer:
    def __init__(self):
        '''Sets default settings from config.json.'''
        with open('settings.json') as json_file:
            data = json.load(json_file)
        self.default_sleep_standby = data['config']['check_standby']
        self.check_standby = data['config']['default_sleep_standby']
        if self.check_standby == 1:
            self.check_standby = int(Get_Standby_Time())
        else:
            self.check_standby = int(self.default_sleep_standby)
        self.cancel = 0


def Get_Standby_Time():
    '''Gets Active Power scheme.'''
    current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
    # Gets Current Scheme Sleep Standby time.
    output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
    output.split(' ')[1][:-4]
    string = 'Current AC Power Setting Index:'
    cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
    return int(int(cur_standby_time, 16) / 60)


def Timed_shutdown_sleep(self, action, Sleep_Button, Shutdown_Button, Cancel_Button):
    '''Sleeps or shuts down PC in the specified time frame.

    Arguments:

    action -- sleep or shutdown determines what occurs at timers end
    '''
    subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
    delay = int(Timer_Entry.get())
    Sleep_Button.config(state='disabled')
    Shutdown_Button.config(state='disabled')
    Cancel_Button.config(state='normal')
    timer = delay * 60
    if int(delay) > self.def_standby:
        subprocess.call(f"powercfg -change -standby-timeout-ac {timer + 5}")
    thread = threading.Thread(target=Time_Tracker, args=(timer, action, self.def_standby), daemon=True)
    thread.start()


def Time_Tracker(self, timer, action, def_standby):
    '''ph

    Arguments:

    timer -- time til countdown ends

    action -- sleep or shutdown determines what occurs at timers end

    def_standby -- default standby sleep timer
    '''
    cancel = 0
    last_run = dt.datetime.now()
    while timer > 0:
        print(dt.datetime.now() - last_run)
        if dt.datetime.now() - last_run >= dt.timedelta(seconds=10):
            print('Sleep Detected')
            Cancel_Func()
            cancel = 1
            break
        last_run = dt.datetime.now()
        min_left = int(timer / 60)
        sec_left = "{0:0=2d}".format(int(timer % 60))
        Timer_Display.config(text=f'Time Left: {min_left}:{sec_left}')
        time.sleep(1)
        timer -= 1
        print(cancel)
    subprocess.call(f"powercfg -change -standby-timeout-ac {def_standby}")
    if cancel == 0:
        if action == 'Sleep': # Sleep
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            time.sleep(10)
            sys.exit()
            print('Canceled')
        elif action == 'Shutdown': # Shutdown
            os.system("shutdown /s /t 1")


def Cancel_Func(self):
    '''Resets timer and defaults the PC standby sleep timer.'''
    subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
    cancel = 1
    Sleep_Button.config(state='normal')
    Shutdown_Button.config(state='normal')
    Cancel_Button.config(state='disabled')
    Timer_Display.config(text='Time Left: Waiting to start')