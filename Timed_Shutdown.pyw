from functools import partial
import datetime as dt
import tkinter as Tk
import configparser
import subprocess
import threading
import time
import sys
import os

Config = configparser.ConfigParser()
Config.read('Config.ini')

def create_window():
    default_sleep_standby = Config.get('Settings', 'default_sleep_standby')
    check_standby = Config.get('Settings', 'check_standby')
    if check_standby == 1:
        def_standby = int(get_standby_time())
    else:
        def_standby = int(default_sleep_standby)


    def get_standby_time():
        # Gets Active Power scheme
        current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
        # Gets Current Scheme Sleep Standby time.
        output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
        output.split(' ')[1][:-4]
        string = 'Current AC Power Setting Index:'
        cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
        return int(int(cur_standby_time, 16) / 60)


    def Timed_shutdown_sleep(action):
        subprocess.call(f"powercfg -change -standby-timeout-ac {def_standby}")
        # last_run = dt.datetime.now()
        delay = int(Timer_Entry.get())
        Sleep_Button.config(state='disabled')
        Shutdown_Button.config(state='disabled')
        Cancel_Button.config(state='normal')
        timer = delay * 60
        if int(delay) > def_standby:
            subprocess.call(f"powercfg -change -standby-timeout-ac {timer + 5}")
        thread = threading.Thread(target=Time_Loop, args=(timer, action, def_standby), daemon=True)
        thread.start()


    def Time_Loop(timer, action, def_standby):
        last_run = dt.datetime.now()
        while timer > 0:
            print(dt.datetime.now() - last_run)
            if dt.datetime.now() - last_run >= dt.timedelta(seconds=10):
                print('Sleep Detected')
                Sleep_Button.config(state='normal')
                Shutdown_Button.config(state='normal')
                Cancel_Button.config(state='disabled')
                # Cancel_Func()
                break
            last_run = dt.datetime.now()
            min_left = int(timer / 60)
            sec_left = "{0:0=2d}".format(int(timer % 60))
            Timer_Display.config(text=f'Time Left: {min_left}:{sec_left}')
            time.sleep(1)
            timer -= 1
        subprocess.call(f"powercfg -change -standby-timeout-ac {def_standby}")
        if action == 'Sleep': # Sleep
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            time.sleep(10)
            sys.exit()
        elif action == 'Shutdown': # Shutdown
            os.system("shutdown /s /t 1")


    def Cancel_Func():
        subprocess.call(f"powercfg -change -standby-timeout-ac {def_standby}")
        # Sleep_Button.config(state='normal')
        # Shutdown_Button.config(state='normal')
        # Cancel_Button.config(state='disabled')
        sys.exit()


    # Defaults for Background and fonts
    Background = 'White'
    BoldBaseFont = "Arial Bold"
    BaseFont = "Arial"

    Main_GUI = Tk.Tk()
    Main_GUI.title("Timed Shutdown and Sleep")
    Main_GUI.iconbitmap('Power.ico')
    Main_GUI.configure(bg=Background)
    Main_GUI.resizable(width=False, height=False)

    Title_Frame = Tk.Frame(Main_GUI, bg=Background)
    Title_Frame.grid(columnspan=4, padx=(20, 20), pady=(5, 10))

    Title = Tk.Label(Title_Frame, text='Timed Shutdown and Sleep', font=(BoldBaseFont, 20), bg=Background)
    Title.grid(column=0, row=0)

    Question = Tk.Label(Title_Frame, text='Enter Time in minutes before action starts.', font=(BoldBaseFont, 12), bg=Background)
    Question.grid(columnspan=4, row=1)

    Timer_Entry = Tk.Spinbox(Main_GUI, from_=1, to=1000, width=6, bd=2, font=(BaseFont, 13), justify='center', bg='grey95')
    Timer_Entry.grid(columnspan=4, row=2)

    Sleep_Button = Tk.Button(Main_GUI, text=f'Sleep Computer', font=(BaseFont, 11), width=20, command=partial(Timed_shutdown_sleep, 'Sleep'))
    Sleep_Button.grid(column=1, row=3, pady=(10, 10))

    Shutdown_Button = Tk.Button(Main_GUI, text=f'Shutdown Computer', font=(BaseFont, 11), width=20, command=partial(Timed_shutdown_sleep, 'Shutdown'))
    Shutdown_Button.grid(column=2, row=3, pady=(10, 10))

    Timer_Frame = Tk.Frame(Main_GUI, bg=Background)
    Timer_Frame.grid(columnspan=4, row=4, padx=(20, 20), pady=(5, 10))

    Timer_Display = Tk.Label(Timer_Frame, text='Time Left: Waiting to start', font=(BoldBaseFont, 12), bg=Background)
    Timer_Display.grid(columnspan=4, row=0)

    Cancel_Button = Tk.Button(Timer_Frame, text=f'Cancel Action', font=(BaseFont, 11), width=20, command=Cancel_Func, state='disabled')
    Cancel_Button.grid(columnspan=4, row=1, pady=(10, 1))

    Main_GUI.mainloop()

if __name__ == '__main__':
    create_window()
