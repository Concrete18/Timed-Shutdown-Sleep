import datetime as dt
import tkinter as Tk
import subprocess
import threading
import time
import json
import sys
import os


class Timer:

    def __init__(self, master):
        '''Sets default settings from config.json.'''
        self.master = master
        with open('config.json') as json_file:
            data = json.load(json_file)
        self.default_sleep_standby = data['config']['default_sleep_standby']
        self.use_def_standby = data['config']['use_def_standby']
        if self.use_def_standby == 1:
            self.def_standby = int(self.Get_Standby_Time())
        else:
            self.def_standby = int(self.default_sleep_standby)
        self.last_run = dt.datetime.now()
        self.timer = 0
        self.cancel = 0
        self.action = ''


        # Defaults for Background and fonts
        Background = 'White'
        BoldBaseFont = "Arial Bold"
        BaseFont = "Arial"

        app_width = 425
        app_height = 240
        width = int((self.master.winfo_screenwidth()-app_width)/2)
        height = int((self.master.winfo_screenheight()-app_height)/2)

        self.master.geometry(f'{app_width}x{app_height}+{width}+{height}')
        self.master.title("Timed Shutdown and Sleep")
        self.master.iconbitmap('Power.ico')
        self.master.configure(bg=Background)
        self.master.resizable(width=False, height=False)

        self.Title_Frame = Tk.Frame(self.master, bg=Background)
        self.Title_Frame.grid(columnspan=4, padx=(20, 20), pady=(5, 10))

        self.Title = Tk.Label(self.Title_Frame, text='Timed Shutdown and Sleep', font=(BoldBaseFont, 20), bg=Background)
        self.Title.grid(column=0, row=0)

        self.Question = Tk.Label(self.Title_Frame, text='Enter Time in minutes before action starts.',
            font=(BoldBaseFont, 12), bg=Background)
        self.Question.grid(columnspan=4, row=1)

        self.Timer_Entry = Tk.Spinbox(self.master, from_=1, to=1000, width=6, bd=2, font=(BaseFont, 13),
            justify='center', bg='grey95')
        self.Timer_Entry.grid(columnspan=4, row=2)

        self.Sleep_Button = Tk.Button(self.master, text=f'Sleep Computer', font=(BaseFont, 11), width=20,
            command=lambda: self.Timed_shutdown_sleep('Sleep'))
        self.Sleep_Button.grid(column=1, row=3, pady=(10, 10))

        self.Shutdown_Button = Tk.Button(self.master, text=f'Shutdown Computer', font=(BaseFont, 11), width=20,
            command=lambda: self.Timed_shutdown_sleep('Shutdown'))
        self.Shutdown_Button.grid(column=2, row=3, pady=(10, 10))

        self.Timer_Frame = Tk.Frame(self.master, bg=Background)
        self.Timer_Frame.grid(columnspan=4, row=4, padx=(20, 20), pady=(5, 10))

        self.Timer_Display = Tk.Label(self.Timer_Frame, text='Time Left: Waiting to start', font=(BoldBaseFont, 12),
            bg=Background)
        self.Timer_Display.grid(columnspan=4, row=0)

        self.Cancel_Button = Tk.Button(self.Timer_Frame, text=f'Cancel Action', font=(BaseFont, 11), width=20,
            command=self.Cancel_Func, state='disabled')
        self.Cancel_Button.grid(columnspan=4, row=1, pady=(10, 1))


    def Get_Standby_Time():
        '''Gets Active Power scheme.'''
        current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
        # Gets Current Scheme Sleep Standby time.
        output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
        output.split(' ')[1][:-4]
        string = 'Current AC Power Setting Index:'
        cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
        return int(int(cur_standby_time, 16) / 60)


    def Timed_shutdown_sleep(self, action):
        '''Sleeps or shuts down PC in the specified time frame.

        Arguments:

        action -- sleep or shutdown determines what occurs at timers end

        Sleep_Button, Shutdown_Button, Cancel_Button -- button objects that get state changes.
        '''
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
        delay = int(self.Timer_Entry.get())
        self.Sleep_Button.config(state='disabled')
        self.Shutdown_Button.config(state='disabled')
        self.Cancel_Button.config(state='normal')
        self.timer = delay * 60
        if int(delay) > self.def_standby:
            subprocess.call(f"powercfg -change -standby-timeout-ac {self.timer + 5}")
        thread = threading.Thread(target=self.Time_Tracker, daemon=True)
        thread.start()


    def Time_Tracker(self):
        '''Tracks time left and runs actions d

        Arguments:

        timer -- time til countdown ends

        action -- set to sleep or shutdown to determine what occurs at timers end

        def_standby -- default standby sleep timer
        '''
        self.cancel = 0
        self.last_run = dt.datetime.now()
        while self.timer > 0:
            print(dt.datetime.now() - self.last_run)
            if dt.datetime.now() - self.last_run >= dt.timedelta(seconds=10):
                print('Sleep Detected')
                self.Cancel_Func()
                self.cancel = 1
                break
            self.last_run = dt.datetime.now()
            min_left = int(self.timer / 60)
            sec_left = "{0:0=2d}".format(int(self.timer % 60))
            self.Timer_Display.config(text=f'Time Left: {min_left}:{sec_left}')
            time.sleep(1)
            self.timer -= 1
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
        if self.cancel == 0:
            if self.action == 'Sleep':
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                time.sleep(10)
                sys.exit()
            elif self.action == 'Shutdown':
                os.system("shutdown /s /t 1")


    def Cancel_Func(self):
        '''Resets timer and defaults the PC standby sleep timer.'''
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.def_standby}")
        self.cancel = 1
        self.Sleep_Button.config(state='normal')
        self.Shutdown_Button.config(state='normal')
        self.Cancel_Button.config(state='disabled')
        self.Timer_Display.config(text='Time Left: Waiting to start')


def Main():
    Main_GUI = Tk.Tk()
    App = Timer(Main_GUI)
    Main_GUI.mainloop()


if __name__ == "__main__":
    Main()
