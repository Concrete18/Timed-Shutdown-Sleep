import datetime as dt
import atexit
import time
import os

print('Shutdown/Sleep Timer\n')


def exit_handler():
    print('  My application is ending!')


def timed_Shutdown_Sleep():
    last_run = dt.datetime.now()
    power = {1:'sleep', 2:'shutdown'}
    action = int(input('What do you want to do?\n1-Sleep  2-Shutdown\n'))
    timer = float(input(f'\nHow long till you want your PC to {power[action]} in minutes..\n')) * 60 # Turns the minutes entered into seconds.
    print('')
    while timer > 0:
        if dt.datetime.now() - last_run >= dt.timedelta(minutes=1.1):
            quit()
        min_left = int(timer / 60)
        if min_left == 1:
            min_plur = 'Minute'
        else:
            min_plur = 'Minutes'
        print(f'System will {power[action]} in {min_left} {min_plur} and {int(timer % 60)} Seconds.       ', end='\r')
        time.sleep(1)
        timer -= 1
        last_run = dt.datetime.now()
    print('Timer Finished                                                     ')
    if action == 1: # Sleep
        # os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        print('\nShutdown Initiated')
    elif action == 2: # Shutdown
        # os.system("shutdown /s /t 1")
        print('\nSleep Initiated')
    input()

timed_Shutdown_Sleep()

atexit.register(exit_handler)
