from time import sleep
import datetime as dt
import tkinter as Tk
import subprocess
import threading
import json
import sys
import os


class Timer:

    def __init__(self, master):
        '''Sets default settings from config.json.'''
        self.master = master
        self.last_run = dt.datetime.now()
        self.timer = 0
        self.cancel = 0
        self.action = ''
        with open('config.json') as json_file:
            data = json.load(json_file)
        if data['config']['use_default_standby'] == 1:
            self.standby_time = data['config']['default_sleep_standby']
        else:
            self.Set_Standby_Time()


        # Defaults for Background and fonts
        Background = 'White'
        BoldBaseFont = "Arial Bold"
        BaseFont = "Arial"

        app_width, app_height = 415, 237
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

        self.Sleep_Button = Tk.Button(self.master, text=f'Sleep', font=(BaseFont, 12), width=10,
            command=lambda: self.Timed_shutdown_sleep('Sleep'))
        self.Sleep_Button.grid(column=1, row=3, pady=(10, 10))

        self.Shutdown_Button = Tk.Button(self.master, text=f'Shutdown', font=(BaseFont, 12), width=10,
            command=lambda: self.Timed_shutdown_sleep('Shutdown'))
        self.Shutdown_Button.grid(column=2, row=3, pady=(10, 10))

        self.Timer_Frame = Tk.Frame(self.master, bg=Background)
        self.Timer_Frame.grid(columnspan=4, row=4, padx=(20, 20), pady=(5, 10))

        self.Timer_Display = Tk.Label(self.Timer_Frame, text='Time Left: Waiting to start', font=(BoldBaseFont, 12),
            bg=Background)
        self.Timer_Display.grid(columnspan=4, row=0)

        self.Cancel_Button = Tk.Button(self.Timer_Frame, text=f'Cancel', font=(BaseFont, 12), width=10,
            command=self.Cancel_Timer, state='disabled')
        self.Cancel_Button.grid(columnspan=4, row=1, pady=(10, 1))


    def Set_Standby_Time(self):
        '''Gets Current Scheme Sleep Standby time using cmd a command output.'''
        current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
        output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
        output.split(' ')[1][:-4]
        string = 'Current AC Power Setting Index:'
        cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
        self.standby_time = int(int(cur_standby_time, 16) / 60)


    def Timed_shutdown_sleep(self, action):
        '''Sleeps or shuts down PC in the specified time frame.

        Arguments:

        action -- sleep or shutdown determines what happens when the timer expires
        '''
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
        delay = int(self.Timer_Entry.get())
        self.Sleep_Button.config(state='disabled')
        self.Shutdown_Button.config(state='disabled')
        self.Cancel_Button.config(state='normal')
        self.timer = delay * 60
        if int(delay) > self.standby_time:
            subprocess.call(f"powercfg -change -standby-timeout-ac {self.timer + 5}")
        thread = threading.Thread(target=self.Time_Tracker, args=(action,), daemon=True)
        thread.start()


    def Time_Tracker(self, action):
        '''Tracks time left with a new thread and runs the entered action when it reaches 0.'''
        self.cancel = 0
        self.last_run = dt.datetime.now()
        while self.timer > 0:
            # detects cancel button being pressed
            if self.cancel == 1:
                self.Cancel_Timer()
                break
            # detects computer went to sleep during timer
            if dt.datetime.now() - self.last_run >= dt.timedelta(seconds=20):
                print('Sleep Detected')
                self.Cancel_Timer()
                break
            self.last_run = dt.datetime.now()  # sets last second increment for sleep detection
            min_left = int(self.timer / 60)
            sec_left = "{0:0=2d}".format(int(self.timer % 60))
            self.Timer_Display.config(text=f'Time Left till {action}: {min_left}:{sec_left}')
            sleep(1)
            self.timer -= 1
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
        if self.cancel == 0:
            self.Timer_Display.config(text=f'Time Left till {action}: 0:00')
            if action == 'Sleep':
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                sleep(10)
                sys.exit()
            elif action == 'Shutdown':
                os.system("shutdown /s /t 1")


    def Cancel_Timer(self):
        '''Resets timer to unset and reconfigures buttons and labels to default state.
        Also sets computer standby to original settings'''
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
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
