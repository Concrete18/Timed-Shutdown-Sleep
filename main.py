# standard library
import tkinter as tk
import datetime as dt
import os, json, threading, subprocess, time

# local imports
from library.windows import *


class Timer:
    def __init__(self) -> None:
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.config = self.load_config()
        self.debug = self.config["settings"]["debug"]

        self.title = "Timed Shutdown and Sleep"
        self.wait_time = 0
        self.cancel = 0
        self.action = ""
        self.standby_time = self.init_standby_time()
        self.main = None

    def load_config(self) -> dict:
        config_path = os.path.join(self.script_dir, "config.json")
        with open(config_path) as f:
            return json.load(f)

    def init_standby_time(self) -> int:
        cfg = self.config["standby"]
        if cfg["use_default_standby"]:
            return (
                cfg["default_sleep_standby_battery"]
                if self.using_battery()
                else cfg["default_sleep_standby_outlet"]
            )

        minutes = get_current_standby_time()
        max_time = self.config["standby"]["max_standby_time_in_min"]
        return min(minutes, max_time) if max_time > 0 else minutes

    def open_interface(self) -> None:
        self.main = tk.Tk()
        self.main.title(self.title)
        self.main.resizable(False, False)
        self.main.iconbitmap(os.path.join(self.script_dir, "Images", "Default.ico"))
        self.main.configure(bg="white")
        self.main.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_gui()
        self.main.mainloop()

    def build_gui(self) -> None:
        padding_x, padding_y = 14, 10
        # TODO change to a new font
        background = "white"
        base_font = ("Arial", 12)
        bold_font = ("Arial Bold", 12)

        # Center window
        app_width, app_height = 395, 200
        screen_w = self.main.winfo_screenwidth()
        screen_h = self.main.winfo_screenheight()
        pos_x = int((screen_w - app_width) / 2)
        pos_y = int((screen_h - app_height) / 2)
        self.main.geometry(f"{app_width}x{app_height}+{pos_x}+{pos_y}")

        # Title and info
        title_frame = tk.Frame(self.main, bg=background)
        title_frame.grid(columnspan=4, padx=20, pady=(5, 10))

        standby_info = f"Current Standby Time: {self.standby_time} minutes."
        instructions = "Enter time in minutes then click desired action"
        info_text = f"{standby_info}\n{instructions}"

        info_label = tk.Label(
            title_frame, text=info_text, font=bold_font, bg=background, anchor="center"
        )
        info_label.grid(columnspan=3, row=0, pady=(10, 0))

        # Buttons and entry
        self.timer_value = tk.StringVar(value="30")
        self.sleep_button = tk.Button(
            self.main,
            text="Sleep",
            font=base_font,
            width=10,
            command=lambda: self.start_timer("Sleep"),
        )
        self.sleep_button.grid(column=0, row=1, padx=padding_x, pady=padding_y)

        self.timer_entry = tk.Spinbox(
            self.main,
            textvariable=self.timer_value,
            from_=1,
            to=1000,
            width=9,
            bd=2,
            font=("Arial", 13),
            justify="center",
            bg="grey95",
        )
        self.timer_entry.grid(column=1, row=1, padx=padding_x, pady=padding_y)

        self.shutdown_button = tk.Button(
            self.main,
            text="Shutdown",
            font=base_font,
            width=10,
            command=lambda: self.start_timer("Shutdown"),
        )
        self.shutdown_button.grid(column=2, row=1, padx=padding_x, pady=padding_y)

        # Timer display and cancel
        timer_frame = tk.Frame(self.main, bg=background)
        timer_frame.grid(columnspan=3, row=2, padx=20, pady=(5, 10))

        self.Timer_Display = tk.Label(
            timer_frame,
            text="Time Left: Waiting to start",
            font=bold_font,
            bg=background,
        )
        self.Timer_Display.grid(columnspan=3, row=0)

        self.cancel_button = tk.Button(
            timer_frame,
            text=f"Cancel",
            font=(base_font, 12),
            width=10,
            command=self.cancel_timer,
            state="disabled",
        )
        self.cancel_button.grid(columnspan=4, row=1, pady=(10, 6))

    def start_timer(self, action):
        self.action = action
        delay = float(self.timer_value.get())
        self.wait_time = delay * 60
        if delay > self.standby_time:
            temp_standby = str(int(delay + 5))
            command = ["powercfg", "-change", "-standby-timeout-ac", temp_standby]
            subprocess.call(command)
        self.disable_buttons()
        timer_thread = threading.Thread(
            target=self.time_tracker,
            name=f"Timed {action}",
            args=[action],
            daemon=True,
        )
        timer_thread.start()

    def time_tracker(self, action) -> None:
        self.cancel = 0
        start_time = time.time()
        end_time = start_time + self.wait_time
        last_check = time.time()
        if self.debug:
            print(f"\nStarting test for {action}")
            print(f"wait time: {self.wait_time}")
            print(f"start time: {start_time}")
            print(f"end time:   {end_time}\n")

        while True:
            cur_time = time.time()
            if cur_time - last_check > 20:
                # cancels due to the OS likely going to sleep
                self.cancel_timer()
                return
            last_check = cur_time
            time_left = end_time - last_check
            print(f"{time_left:.0f}")
            if time_left < 0:
                self.cancel_timer()
                break
            mins, secs = divmod(time_left, 60)
            time_left_str = f"{mins:.0f}:{secs:02.0f}"
            self.Timer_Display.config(text=f"Time Left till {action}: {time_left_str}")

            time.sleep(1)
            if self.cancel:
                self.cancel_timer()
                return
        if self.debug:
            print(f"Would perform: {action}")
        else:
            perform_action(action, self.standby_time)

    def cancel_timer(self) -> None:
        reset_standby_time(self.standby_time)
        self.cancel = 1
        self.wait_time = 0
        self.enable_buttons()
        self.Timer_Display.config(text="Time Left: Waiting to start")

    def disable_buttons(self) -> None:
        self.sleep_button.config(state="disabled")
        self.shutdown_button.config(state="disabled")
        self.cancel_button.config(state="normal")

    def enable_buttons(self) -> None:
        self.sleep_button.config(state="normal")
        self.shutdown_button.config(state="normal")
        self.cancel_button.config(state="disabled")

    def on_close(self) -> None:
        if self.wait_time > 0:
            reset_standby_time(self.standby_time)
        self.main.destroy()


if __name__ == "__main__":
    Timer().open_interface()
