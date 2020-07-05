import PySimpleGUIWx as sg
import datetime as dt
import configparser
import subprocess
import time
import sys
import os

Config = configparser.ConfigParser()
Config.read('Config.ini')
sg.theme('DarkTanBlue')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Radio('Sleep', "SLEEP", default=True),sg.Radio('Shutdown', "SHUTDOWN")],
            [sg.Text('How many minutes before action starts?'), sg.InputText()],
            [sg.Button('Start'), sg.Button('Cancel')]]

class Timer:
    def __init__(self):
        self.default_sleep_standby = Config.get('Settings', 'default_sleep_standby')
        self.check_standby = Config.get('Settings', 'check_standby')
        self.min_left = 'UNSET'
        self.actiom = ''
        self.delay = ''



    @staticmethod
    def get_standby_time():
        # Gets Active Power scheme
        current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
        # Gets Current Scheme Sleep Standby time.
        output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
        output.split(' ')[1][:-4]
        string = 'Current AC Power Setting Index:'
        cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
        return int(int(cur_standby_time, 16) / 60)


    def Timed_shutdown_sleep(self):
        if self.use_config == 1:
            self.def_standby = get_standby_time()
        else:
            self.def_standby = self.default_sleep_standby
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
        last_run = dt.datetime.now()
        timer = delay * 60
        if delay > self.def_standby:
            subprocess.call(f"powercfg -change -standby-timeout-ac {timer + 5}")
        while timer > 0:
            if dt.datetime.now() - last_run >= dt.timedelta(minutes=1.1):
                subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
                sys.exit()
            min_left = int(timer / 60)
            if min_left == 1:
                min_plur = 'Minute'
            else:
                min_plur = 'Minutes'
            time.sleep(1)
            timer -= 1
            last_run = dt.datetime.now()
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
        if self.action == 1: # Sleep
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            time.sleep(10)
            sys.exit()
        elif self.action == 2: # Shutdown
            os.system("shutdown /s /t 1")

if __name__ == '__main__':
    App = Timer()
    window = sg.Window('Timed Shutdown and Sleep', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        if event == sg.WIN_CLOSED or event == 'Start':
            self.Timed_shutdown_sleep(values[0])

    window.close()