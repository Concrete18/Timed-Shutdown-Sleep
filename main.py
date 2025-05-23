# standard library
import tkinter as tk
from tkinter import ttk
import datetime as dt
import os, json, threading, time

# local imports
from library.windows import *


class Timer:
    def __init__(self) -> None:
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.config = self.load_config()
        self.debug = self.config["settings"]["debug"]

        self.title = "Timed Shutdown and Sleep"
        self.unset_text = "Waiting to Start\nSet Delay and Action"
        self.wait_time = 0
        self.cancel = 0
        self.action = ""
        self.default_standby_time = self.get_default_standby_time()
        if self.debug:
            print(self.default_standby_time)
        self.main = tk.Tk()

    def load_config(self) -> dict:
        config_path = os.path.join(self.script_dir, "config.json")
        with open(config_path) as f:
            return json.load(f)

    def get_default_standby_time(self) -> int:
        """
        Gets gets the default standby time before sleep from the config.
        """
        cfg = self.config["standby"]
        if cfg["use_default_standby"]:
            return (
                cfg["default_sleep_standby_battery"]
                if using_battery()
                else cfg["default_sleep_standby_outlet"]
            )

        minutes = get_current_standby_time()
        max_time = self.config["standby"]["max_standby_time_in_min"]
        return min(minutes, max_time) if max_time > 0 else minutes

    def open_interface(self) -> None:
        self.main.title(self.title)
        # self.main.resizable(False, False)
        self.main.iconbitmap(os.path.join(self.script_dir, "Images", "Default.ico"))
        self.main.configure(bg="white")
        self.main.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_gui()
        self.main.mainloop()

    def build_gui(self) -> None:
        padding_x, padding_y = 8, 1
        base_font = ("Segoe UI", 11)
        bold_font = ("Segoe UI", 11, "bold")
        background = "white"

        # Apply ttk theme and styling
        style = ttk.Style(self.main)
        style.theme_use("clam")  # Use 'clam', 'alt', or 'default'

        style.configure(
            "Header.TLabel",
            font=bold_font,
            background=background,
            padding=5,
        )
        style.configure("TLabel", font=base_font, background=background)
        style.configure("TButton", font=base_font)
        style.configure("TSpinbox", font=base_font)

        self.main.configure(bg=background)

        # Center window
        app_width, app_height = 376, 220
        screen_w = self.main.winfo_screenwidth()
        screen_h = self.main.winfo_screenheight()
        pos_x = int((screen_w - app_width) / 2)
        pos_y = int((screen_h - app_height) / 2)
        self.main.geometry(f"{app_width}x{app_height}+{pos_x}+{pos_y}")
        self.main.title("Sleep/Shutdown Timer")

        # Title and info
        title_frame = ttk.Frame(self.main)
        title_frame.grid(columnspan=3, padx=20, pady=(5, 5))

        standby_info = f"Current Standby Time: {self.default_standby_time} minutes."
        instructions = "Enter time in minutes then click desired action"
        info_text = f"{standby_info}\n{instructions}"

        info_label = ttk.Label(
            title_frame,
            text=info_text,
            style="Header.TLabel",
            anchor="center",
            justify="center",
        )
        info_label.grid(columnspan=3, row=0)

        # Buttons and entry
        self.timer_value = tk.StringVar(value="30")
        self.sleep_button = ttk.Button(
            self.main,
            text="Sleep",
            command=lambda: self.start_timer("Sleep"),
        )
        self.sleep_button.grid(column=0, row=1, padx=padding_x, pady=padding_y)

        self.timer_entry = ttk.Spinbox(
            self.main,
            textvariable=self.timer_value,
            from_=1,
            to=1000,
            width=10,
            justify="center",
            wrap=True,
        )
        self.timer_entry.grid(column=1, row=1, padx=padding_x, pady=padding_y)

        self.shutdown_button = ttk.Button(
            self.main,
            text="Shutdown",
            command=lambda: self.start_timer("Shutdown"),
        )
        self.shutdown_button.grid(column=2, row=1, padx=padding_x, pady=padding_y)

        # Timer display and cancel
        timer_frame = ttk.Frame(self.main)
        timer_frame.grid(columnspan=3, row=2, padx=20, pady=(5, 10))

        self.Timer_Display = ttk.Label(
            timer_frame,
            text=self.unset_text,
            style="Header.TLabel",
            anchor="center",
            justify="center",
        )
        self.Timer_Display.grid(columnspan=3, row=0)

        cancel_frame = ttk.Frame(self.main)
        cancel_frame.grid(column=0, row=3, columnspan=3)

        self.cancel_button = ttk.Button(
            cancel_frame,
            text="Cancel",
            command=self.cancel_timer,
            state="disabled",
        )
        self.cancel_button.grid()

    def start_timer(self, action):
        self.action = action
        delay = float(self.timer_value.get())
        self.wait_time = delay * 60
        if delay > self.default_standby_time:
            temp_standby = int(delay + 5)
            set_standby_time(temp_standby)
        self.disable_buttons()
        timer_thread = threading.Thread(
            target=self.time_tracker,
            name=f"Timed {action}",
            args=[action],
            daemon=True,
        )
        timer_thread.start()

    @staticmethod
    def get_time_from_seconds(seconds):
        """
        Gets the time in string format from the seconds since epoch.

        Output Example: 08:00 PM
        """
        datetime = dt.datetime.fromtimestamp(seconds)
        return datetime.strftime("%I:%M %p").replace(" 0", " ")

    def set_timer_display(self, active_data: dict = {}) -> None:
        if active_data:
            action = active_data.get("action", "Unknown")
            mins, secs = active_data.get("mins_secs", (None, None))
            end_time = active_data.get("end_time")
            time_left_str = f"{mins:.0f}:{secs:02.0f}"
            text = f"Time Left till {action}: {time_left_str}\nAction Time: {end_time}"
        else:
            text = self.unset_text
        self.Timer_Display.config(text=text)

    def time_tracker(self, action) -> None:
        self.cancel = 0
        start_seconds = time.time()
        end_seconds = start_seconds + self.wait_time
        end_time = self.get_time_from_seconds(end_seconds)

        last_check = time.time()
        if self.debug:
            print(f"\nStarting test for {action}")
            print(f"Wait Time: {self.wait_time:,.0f} Seconds")
            print(f"Start Time: {start_seconds:02.0f}")
            print(f"End Time:   {end_seconds:02.0f}\n")
        while True:
            cur_time = time.time()
            if cur_time - last_check > 20:
                # cancels due to the OS likely going to sleep
                self.cancel_timer()
                return
            last_check = cur_time
            time_left = end_seconds - last_check
            if self.debug:
                print(f"{time_left:,.0f} Seconds Left        ", end="\r", flush=True)
            if time_left < 0:
                self.cancel_timer()
                break
            active_data = {
                "action": action,
                "mins_secs": (divmod(time_left, 60)),
                "end_time": end_time,
            }
            self.set_timer_display(active_data)

            time.sleep(1)
            if self.cancel:
                self.cancel_timer()
                return
        if self.debug:
            print(f"Activating {action}")
        else:
            set_standby_time(self.default_standby_time)
            perform_action(action)

    def cancel_timer(self) -> None:
        """
        Cancels the timer and resets standby time.
        """
        set_standby_time(self.default_standby_time)
        self.cancel = 1
        self.wait_time = 0
        self.enable_buttons()
        self.set_timer_display()

    def disable_buttons(self) -> None:
        """
        Disables all Sleep and Shutdown buttons but enables cancel button.
        """
        self.sleep_button.config(state="disabled")
        self.shutdown_button.config(state="disabled")
        self.cancel_button.config(state="normal")

    def enable_buttons(self) -> None:
        """
        Disables Cancel button but enables Sleep and Shutdown buttons.
        """
        self.sleep_button.config(state="normal")
        self.shutdown_button.config(state="normal")
        self.cancel_button.config(state="disabled")

    def on_close(self) -> None:
        """
        Cancels timer and shuts down interface.
        """
        if self.wait_time > 0:
            set_standby_time(self.default_standby_time)
            if self.debug:
                print(f"Set standby to default: {self.default_standby_time} minutes")
        self.main.destroy()


if __name__ == "__main__":
    Timer().open_interface()
