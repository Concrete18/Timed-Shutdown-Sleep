from win10toast import ToastNotifier
import PySimpleGUIWx as sg
from time import sleep
import datetime as dt
import tkinter as Tk
import subprocess
import threading
import json
import os


class Timer:


    def __init__(self):
        '''
        Sets default settings from config.json.
        '''
        # var init
        self.title = 'Timed Shutdown and Sleep'
        self.last_run = dt.datetime.now()
        self.timer = 0
        self.cancel = 0
        self.action = ''
        self.timer_active = 0
        self.keep_tray = 0
        self.icon = 'Images\Power.ico'
        # config init
        with open('config.json') as json_file:
            data = json.load(json_file)
        self.enable_minimize = data['config']['enable_minimize']
        self.toast_notif = data['config']['toast_notification']
        self.notif_dur = data['config']['notification_duration']
        use_default_standby = data['config']['use_default_standby']
        config_standby_time = data['config']['default_sleep_standby']
        try:
            self.toaster = ToastNotifier()
        except:
            self.toast_notif = 0
        # standy mode setup
        if use_default_standby == 1:
            self.standby_time = config_standby_time
        else:
            self.get_standby_time()


    def open_window(self):
        # defaults for background and fonts
        Background = 'White'
        BoldBaseFont = "Arial Bold"
        BaseFont = "Arial"

        app_width, app_height = 395, 190
        self.master = Tk.Tk()
        width = int((self.master.winfo_screenwidth()-app_width)/2)
        height = int((self.master.winfo_screenheight()-app_height)/2)

        self.master.geometry(f'{app_width}x{app_height}+{width}+{height}')
        self.master.title(self.title)
        self.master.iconbitmap(self.icon)
        self.master.configure(bg=Background)
        self.master.resizable(width=False, height=False)
        self.master.wm_protocol("WM_DELETE_WINDOW", self.close_protocol)

        self.Title_Frame = Tk.Frame(self.master, bg=Background)
        self.Title_Frame.grid(columnspan=4, padx=(20, 20), pady=(5, 10))

        # self.Title = Tk.Label(self.Title_Frame, text=self.title, font=(BoldBaseFont, 20), bg=Background)
        # self.Title.grid(column=0, row=0)

        self.instruction = Tk.Label(self.Title_Frame, text='Enter time in minutes then click desired action',
            font=(BoldBaseFont, 12), bg=Background, anchor='center')
        self.instruction.grid(columnspan=3, row=1, pady=(10,0))

        pad_x = 14
        pad_y = 10
        self.Sleep_Button = Tk.Button(self.master, text=f'Sleep', font=(BaseFont, 12), width=10,
            command=lambda: self.timed_shutdown_sleep('Sleep'))
        self.Sleep_Button.grid(column=0, row=3, padx=pad_x, pady=pad_y)

        self.Timer_Entry = Tk.Spinbox(self.master, from_=1, to=1000, width=9, bd=2, font=(BaseFont, 13),
            justify='center', bg='grey95')
        self.Timer_Entry.grid(column=1, row=3, padx=pad_x, pady=pad_y)

        self.Shutdown_Button = Tk.Button(self.master, text=f'Shutdown', font=(BaseFont, 12), width=10,
            command=lambda: self.timed_shutdown_sleep('Shutdown'))
        self.Shutdown_Button.grid(column=2, row=3, padx=pad_x, pady=pad_y)

        self.Timer_Frame = Tk.Frame(self.master, bg=Background)
        self.Timer_Frame.grid(columnspan=3, row=4, padx=(20, 20), pady=(5, 10))

        self.Timer_Display = Tk.Label(self.Timer_Frame, text='Time Left: Waiting to start', font=(BoldBaseFont, 12),
            bg=Background)
        self.Timer_Display.grid(columnspan=4, row=0)

        self.Cancel_Button = Tk.Button(self.Timer_Frame, text=f'Cancel', font=(BaseFont, 12), width=10,
            command=self.cancel_timer, state='disabled')
        self.Cancel_Button.grid(columnspan=4, row=1, pady=(10, 6))

        self.master.mainloop()


    def minimize_to_tray(self):
        '''
        TODO set up minimize to tray
        destroys hides interface and opens up a loop for a tray icon.
        '''
        print('Minimized')
        # hides window
        self.master.withdraw()
        # sets up tray
        self.Tray = sg.SystemTray(
            menu=['menu',['Exit']],
            filename=self.icon,
            tooltip=self.title)
        # starts tray loop
        self.keep_tray = 1
        while self.keep_tray:
            event = self.Tray.Read()
            print(event)
            if event == '__ACTIVATED__' or self.keep_tray == 0:
                break
            elif event == 'Exit':
                exit()
        # shows window again after tray loop is exited
        self.Tray.Close()
        print('Tray closed')
        self.master.deiconify()
        print('WIndow unhidden')


    def close_protocol(self):
        '''
        Sets standy time to current default using cmd call and then destroys main window.
        '''
        if self.timer_active and self.enable_minimize  == 1:
            # TODO ask to minimize or just close
            self.minimize_to_tray()
        else:
            subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
            print(f'Stanbdy reset to {self.standby_time}')
            self.master.destroy()


    def get_standby_time(self):
        '''
        Gets Current Scheme Sleep Standby time using cmd output.
        '''
        current_scheme = str(subprocess.check_output([f"powercfg", "/getactivescheme"])).split(' ')[3]
        output = str(subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"]))
        output.split(' ')[1][:-4]
        string = 'Current AC Power Setting Index:'
        cur_standby_time = output.partition(str(string))[2].split(' ')[1][:-4]
        self.standby_time = int(int(cur_standby_time, 16) / 60)
        print(f'Current Stanby Time: {self.standby_time}')


    def timed_shutdown_sleep(self, event):
        '''
        Sleeps or shuts down PC in the specified time frame.

        Arguments:

        action -- sleep or shutdown determines what happens when the timer expires
        '''
        self.action = event
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
        delay = int(self.Timer_Entry.get())
        self.Sleep_Button.config(state='disabled')
        self.Shutdown_Button.config(state='disabled')
        self.Cancel_Button.config(state='normal')
        self.timer = delay * 60
        if int(delay) > self.standby_time:
            subprocess.call(f"powercfg -change -standby-timeout-ac {self.timer + 5}")
        thread = threading.Thread(target=self.time_tracker, daemon=True)
        thread.start()


    def timer_end_warning(self):
        '''
        TODO update docstring
        Shows a Windows Toast Notification when the timer is close to ending.
        Notification duration and popup time set in config.
        '''
        notif_msg = f'{self.timer} seconds till {self.action}.'
        if self.toast_notif:
            self.toaster.show_toast(
                title=self.title,
                msg=notif_msg,
                icon_path=self.icon,
                duration=self.notif_dur,
                threaded=True)
        else:
            sg.ShowMessage(self.title, message=notif_msg, filename=self.icon, messageicon=None, time=10000)


    def time_tracker(self):
        '''
        Tracks time left with a new thread and runs the entered action when it reaches 0.
        '''
        self.cancel = 0
        self.last_run = dt.datetime.now()
        self.timer_active = 1
        while self.timer > 0:
            print(self.timer)
            # runs toast notification at specific time remaining
            if self.timer == self.notif_dur:
                self.timer_end_warning()
            # detects cancel button being pressed
            if self.cancel == 1:
                self.cancel_timer()
                break
            # detects computer went to sleep during timer
            if dt.datetime.now() - self.last_run >= dt.timedelta(seconds=20):
                print('Sleep Detected')
                self.cancel_timer()
                break
            self.last_run = dt.datetime.now()  # sets last second increment for sleep detection
            if self.keep_tray:
                min_left = int(self.timer / 60)
                sec_left = "{0:0=2d}".format(int(self.timer % 60))
                self.Timer_Display.config(text=f'Time Left till {self.action}: {min_left}:{sec_left}')
            sleep(1)
            self.timer -= 1
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
        if self.cancel == 0:
            if self.keep_tray:
                self.Timer_Display.config(text=f'Time Left till {self.action}: 0:00')
            if self.action == 'Sleep':
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                sleep(10)
                quit()
            elif self.action == 'Shutdown':
                os.system("shutdown /s /t 1")


    def cancel_timer(self):
        '''
        Resets timer to unset and reconfigures buttons and labels to default state.
        Sets computer standby to original settings or default setting.
        '''
        subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
        self.cancel = 1
        self.timer_active = 0
        self.Sleep_Button.config(state='normal')
        self.Shutdown_Button.config(state='normal')
        self.Cancel_Button.config(state='disabled')
        self.Timer_Display.config(text='Time Left: Waiting to start')


if __name__ == "__main__":
    App = Timer()
    App.open_window()
