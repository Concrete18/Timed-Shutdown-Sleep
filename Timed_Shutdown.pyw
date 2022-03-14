import tkinter as Tk
import PySimpleGUIWx as sg
from time import sleep
import datetime as dt
import os, json, threading, subprocess, psutil


class Timer:

    # sets script directory in case current working directory is different
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # var init
    debug_testing = 0  # for skipping shutdown and sleep
    title = "Timed Shutdown and Sleep"
    last_run = dt.datetime.now()
    timer = 0
    cancel = 0
    action = ""
    keep_tray = 0

    def __init__(self):
        """
        Sets default settings from config.json.
        """
        # config init
        with open("config.json") as json_file:
            data = json.load(json_file)
        # settings
        self.enable_minimize = data["settings"]["enable_minimize"]
        self.debug = data["settings"]["debug"]
        # notification
        self.toast_notif = data["notification"]["toast_notification"]
        self.notif_threshold = data["notification"]["notification_threshold"]
        # standby
        use_default_standby = data["standby"]["use_default_standby"]
        config_standby_outlet = data["standby"]["default_sleep_standby_outlet"]
        config_standby_battery = data["standby"]["default_sleep_standby_battery"]
        self.max_standby_time = data["standby"]["max_standby_time_in_min"]
        if use_default_standby:
            if self.check_for_battery_use():
                self.standby_time = config_standby_battery
            else:
                self.standby_time = config_standby_outlet
        else:
            self.standby_time = self.get_standby_time()

    def open_window(self):
        """
        Opens the tkinter window.
        """
        # defaults for background and fonts
        Background = "White"
        BoldBaseFont = "Arial Bold"
        BaseFont = "Arial"

        self.master = Tk.Tk()
        # window size
        app_width, app_height = 395, 200
        width = int((self.master.winfo_screenwidth() - app_width) / 2)
        height = int((self.master.winfo_screenheight() - app_height) / 2)
        self.master.geometry(f"+{width}+{height}")
        # self.master.geometry(f'{app_width}x{app_height}+{width}+{height}')
        self.master.resizable(width=False, height=False)
        # other
        self.master.title(self.title)
        self.master.iconbitmap("Images\Default.ico")
        self.master.configure(bg=Background)
        self.master.wm_protocol("WM_DELETE_WINDOW", self.close_protocol)

        self.Title_Frame = Tk.Frame(self.master, bg=Background)
        self.Title_Frame.grid(columnspan=4, padx=(20, 20), pady=(5, 10))

        self.current_standby_info = (
            f"Current Standby Time: {self.standby_time} minutes."
        )
        self.instruction = "Enter time in minutes then click desired action"
        self.info_label = Tk.Label(
            self.Title_Frame,
            text=f"{self.current_standby_info}\n{self.instruction}",
            font=(BoldBaseFont, 12),
            bg=Background,
            anchor="center",
        )
        self.info_label.grid(columnspan=3, row=1, pady=(10, 0))

        pad_x, pad_y = 14, 10
        self.Sleep_Button = Tk.Button(
            self.master,
            text=f"Sleep",
            font=(BaseFont, 12),
            width=10,
            command=lambda: self.timed_shutdown_sleep("Sleep"),
        )
        self.Sleep_Button.grid(column=0, row=3, padx=pad_x, pady=pad_y)

        self.timer_value = Tk.StringVar(self.master)
        self.timer_value.set(30)

        self.Timer_Entry = Tk.Spinbox(
            self.master,
            textvariable=self.timer_value,
            from_=1,
            to=1000,
            width=9,
            bd=2,
            font=(BaseFont, 13),
            justify="center",
            bg="grey95",
        )
        self.Timer_Entry.grid(column=1, row=3, padx=pad_x, pady=pad_y)

        self.Shutdown_Button = Tk.Button(
            self.master,
            text=f"Shutdown",
            font=(BaseFont, 12),
            width=10,
            command=lambda: self.timed_shutdown_sleep("Shutdown"),
        )
        self.Shutdown_Button.grid(column=2, row=3, padx=pad_x, pady=pad_y)

        self.Timer_Frame = Tk.Frame(self.master, bg=Background)
        self.Timer_Frame.grid(columnspan=3, row=4, padx=(20, 20), pady=(5, 10))

        self.Timer_Display = Tk.Label(
            self.Timer_Frame,
            text="Time Left: Waiting to start",
            font=(BoldBaseFont, 12),
            bg=Background,
        )
        self.Timer_Display.grid(columnspan=4, row=0)

        self.Cancel_Button = Tk.Button(
            self.Timer_Frame,
            text=f"Cancel",
            font=(BaseFont, 12),
            width=10,
            command=self.cancel_timer,
            state="disabled",
        )
        self.Cancel_Button.grid(columnspan=4, row=1, pady=(10, 6))

        self.master.mainloop()

    def minimize_to_tray(self):
        """
        hides interface and opens up a loop for a tray icon.
        """
        if self.debug:
            print("Minimized")
        # hides window
        self.master.withdraw()
        # sets up tray
        icon = f"Images\{self.action}.ico"
        self.Tray = sg.SystemTray(
            menu=["menu", ["Exit"]], filename=icon, tooltip=self.title
        )
        # starts tray loop
        self.keep_tray = 1
        while self.keep_tray:
            event = self.Tray.Read()
            if self.debug:
                print(event)
            if event == "__ACTIVATED__" or self.keep_tray == 0:
                break
            elif event == "Exit":
                self.reset_standby_time()
                self.master.destroy()
                exit()
        # shows window again after tray loop is exited
        self.Tray.Close()
        if self.debug:
            print("Tray closed")
        self.master.deiconify()
        self.keep_tray = 0
        if self.debug:
            print("Window unhidden")

    @staticmethod
    def plugged_in():
        """
        Determines if the computer us currently plugged in or not. Returns True if it is plugged in and False if not.
        """
        battery = psutil.sensors_battery()
        if battery is None:
            return True
        else:
            return battery.power_plugged

    def get_standby_time(self):
        """
        Gets Current Scheme Sleep Standby time using cmd output.
        """
        # gets current power current_scheme
        current_scheme = str(
            subprocess.check_output([f"powercfg", "/getactivescheme"])
        ).split(" ")[3]
        # finds output of powercfg command using current_scheme
        output = str(
            subprocess.check_output([f"powercfg", "/q", current_scheme, "SUB_SLEEP"])
        )
        # determines if what standby time to use
        self.plugged_in = self.plugged_in()
        # sets which Power Setting to check based on power state
        if self.plugged_in:
            string = "Current AC Power Setting Index:"
        else:
            string = "Current DC Power Setting Index:"
        # converts output from hexidecimal into decimal
        cur_standby_time = int(output.partition(str(string))[2].split(" ")[1][:10], 16)
        # sets standby_time to minutes from cur_standby_time
        standby_time = int(cur_standby_time / 60)
        # sets standby_timeto max ammount if max_standby_time greater then 0
        if self.max_standby_time > 0 and standby_time > self.max_standby_time:
            standby_time = self.max_standby_time
        print(f"Current Standby Time: {standby_time}")
        if self.plugged_in:
            print("Device is plugged in.")
        else:
            print("Battery is used.")
        return standby_time

    def reset_standby_time(self):
        """
        Resets standby time to previous or default value.
        """
        if self.plugged_in:
            subprocess.call(f"powercfg -change -standby-timeout-ac {self.standby_time}")
            print(f"Set Plugged in sleep standby to {self.standby_time}.")
        else:
            subprocess.call(f"powercfg -change -standby-timeout-dc {self.standby_time}")
            print(f"Set on battery sleep standby to {self.standby_time}.")

    def timed_shutdown_sleep(self, event):
        """
        Sleeps or shuts down PC in the specified time frame.

        Arguments:

        event -- sleep or shutdown determines what happens when the timer expires
        """
        self.action = event
        delay = float(self.timer_value.get())
        self.Sleep_Button.config(state="disabled")
        self.Shutdown_Button.config(state="disabled")
        self.Cancel_Button.config(state="normal")
        self.timer = delay * 60
        if delay > self.standby_time:
            subprocess.call(f"powercfg -change -standby-timeout-ac {delay + 5}")
        threading.Thread(target=self.time_tracker, daemon=True).start()

    def timer_end_warning(self):
        """
        Creates a Windows Notification when the timer is close to ending.
        Notification duration and popup time set in config.
        """
        if self.keep_tray:
            if self.debug:
                print("Showing tray balloon")
            notif_msg = f"{self.timer} seconds till {self.action}."
            notif_miliseconds = self.notif_threshold * 1000
            self.Tray.ShowMessage(self.title, notif_msg, time=notif_miliseconds)

    def run_action(self):
        """
        Runs the selected action.
        """
        if self.cancel == 0:  # last moment check to see if cancel was pressed
            self.reset_standby_time()
            if not self.keep_tray:
                self.Timer_Display.config(text=f"Time Left till {self.action}: 0:00")
            if self.action == "Sleep":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif self.action == "Shutdown":
                os.system("shutdown /s /t 1")
            else:
                print("No Action was selected.")

    def time_tracker(self):
        """
        Tracks time left with a new thread and runs the entered action when it reaches 0.
        """
        self.cancel = 0
        self.last_run = dt.datetime.now()
        while self.timer > 0:
            # runs toast notification at specific time remaining
            if self.timer == self.notif_threshold:
                self.timer_end_warning()
            # detects if computer went to sleep during timer
            if dt.datetime.now() - self.last_run >= dt.timedelta(seconds=20):
                print("Sleep Detected")
                self.cancel_timer()
                break
            self.last_run = (
                dt.datetime.now()
            )  # sets last second increment for sleep detection
            min_left = int(self.timer / 60)
            sec_left = "{0:0=2d}".format(int(self.timer % 60))
            info_text = f"Time Left till {self.action}: {min_left}:{sec_left}"
            if self.keep_tray:
                self.Tray.update(tooltip=self.title + "\n" + info_text)
            else:
                self.Timer_Display.config(text=info_text)
            sleep(1)
            # detects cancel button press
            if self.cancel == 1:
                # TODO check if cancel_timer is needed here
                break
            self.timer -= 1
        if (
            self.debug_testing
        ):  # if debug_testing is True, skips actual final action for testin
            print(f"Computer {self.action}")
            if self.keep_tray:
                self.Tray.Close()
            exit()
        else:
            self.run_action()

    def cancel_timer(self):
        """
        Resets timer to unset and reconfigures buttons and labels to default state.
        Sets computer standby to original settings or default setting.
        """
        self.reset_standby_time()
        # sets loop ending variables
        self.cancel = 1
        self.timer = 0
        # sets button states for canceled state
        self.Sleep_Button.config(state="normal")
        self.Shutdown_Button.config(state="normal")
        self.Cancel_Button.config(state="disabled")
        self.Timer_Display.config(text="Time Left: Waiting to start")

    def close_protocol(self):
        """
        Sets standby time to current default using cmd call and then destroys main window.
        If enable_minimize is 1 then it will minimize to tray instead and only hide the main window.
        """
        if self.timer > 0 and self.enable_minimize:
            self.minimize_to_tray()
        elif self.timer > 0:
            self.reset_standby_time()
        else:
            self.master.destroy()


if __name__ == "__main__":
    Timer().open_window()
