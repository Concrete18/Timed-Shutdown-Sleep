import tkinter as Tk
from functools import partial
from tkinter import ttk
import datetime as dt
import configparser
import subprocess
from functools import partial
import time
import sys
import os

Config = configparser.ConfigParser()
Config.read('Config.ini')

def create_window():
    default_sleep_standby = Config.get('Settings', 'default_sleep_standby')
    check_standby = Config.get('Settings', 'check_standby')
    min_left = 'UNSET'


    def get_standby_time():
        # Gets Active Power scheme
        current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
        # Gets Current Scheme Sleep Standby time.
        output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
        output.split(' ')[1][:-4]
        string = 'Current AC Power Setting Index:'
        cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
        return int(int(cur_standby_time, 16) / 60)


    def Timed_shutdown_sleep(delay, action):
        if check_standby == 1:
            def_standby = get_standby_time()
        else:
            def_standby = default_sleep_standby
        subprocess.call(f"powercfg -change -standby-timeout-ac {def_standby}")
        last_run = dt.datetime.now()
        print(f'Delay is set to "{delay}"')
        print(f'Action is set to "{action}"')
        timer = int(delay) * 60
        if delay > def_standby:
            subprocess.call(f"powercfg -change -standby-timeout-ac {timer + 5}")
        while timer > 0:
            if dt.datetime.now() - last_run >= dt.timedelta(minutes=1.1):
                subprocess.call(f"powercfg -change -standby-timeout-ac {def_standby}")
                sys.exit()
            min_left = int(timer / 60)
            if min_left == 1:
                min_plur = 'Minute'
            else:
                min_plur = 'Minutes'
            time.sleep(1)
            timer -= 1
            last_run = dt.datetime.now()
        subprocess.call(f"powercfg -change -standby-timeout-ac {def_standby}")
        if action == 1: # Sleep
            print('Sleep')
            # os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            # time.sleep(10)
            # sys.exit()
        elif action == 2: # Shutdown
            print('Shutdown')
            # os.system("shutdown /s /t 1")


    # Defaults for Background and fonts
    Background = 'White'
    BoldBaseFont = "Arial Bold"
    BaseFont = "Arial"
    FontColor = "Black"

    Timed_GUI = Tk.Tk()
    Timed_GUI.title("Timed Shutdown and Sleep")
    Timed_GUI.iconbitmap('Power.ico')
    Timed_GUI.configure(bg=Background)
    Timed_GUI.resizable(width=False, height=False)

    Title_Frame = Tk.Frame(Timed_GUI, bg=Background)
    Title_Frame.grid(columnspan=4, padx=(20, 20), pady=(5, 10))

    Title = Tk.Label(Title_Frame, text='Timed Shutdown and Sleep', font=(BoldBaseFont, 20), bg=Background)
    Title.grid(column=0, row=0)

    Question = Tk.Label(Title_Frame, text='Enter Time in minutes before action starts.', font=(BoldBaseFont, 12), bg=Background)
    Question.grid(columnspan=4, row=1)

    Timer_Entry = Tk.Entry(Timed_GUI, width=10, bd=2, font=(BaseFont, 13), justify='center', bg='grey95')
    Timer_Entry.grid(columnspan=4, row=2)

    Sleep_Button = Tk.Button(Timed_GUI, text=f'Sleep Computer', font=(BaseFont, 11), width=20, command=partial(Timed_shutdown_sleep, Timer_Entry.get(), 1))
    Sleep_Button.grid(column=1, row=3, pady=(10, 10))

    Shutdown_Button = Tk.Button(Timed_GUI, text=f'Shutdown Computer', font=(BaseFont, 11), width=20, command=partial(Timed_shutdown_sleep, Timer_Entry.get(), 2))
    Shutdown_Button.grid(column=2, row=3, pady=(10, 10))

    Timed_GUI.mainloop()

if __name__ == '__main__':
    create_window()
