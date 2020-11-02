import tkinter as Tk
from Timer_Class import Timer

# Defaults for Background and fonts
Background = 'White'
BoldBaseFont = "Arial Bold"
BaseFont = "Arial"

Main_GUI = Tk.Tk()
app_width = 425
app_height = 273
width = int((Main_GUI.winfo_screenwidth()-app_width)/2)
height = int((Main_GUI.winfo_screenheight()-app_height)/2)
Main_GUI.geometry(f'{app_width}x{app_height}+{width}+{height}')
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
