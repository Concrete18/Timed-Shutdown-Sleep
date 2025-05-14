# standard library
import psutil, subprocess, os


def using_battery() -> bool:
    """
    Returns True if computer is using battery.
    """
    battery = psutil.sensors_battery()
    return battery is not None and not battery.power_plugged


def get_active_power_scheme() -> str:
    """
    Gets the active power scheme's GUID in Windows.
    Tested in Win 10 only.
    """
    scheme_output = subprocess.check_output(["powercfg", "/getactivescheme"])
    return scheme_output.decode().split(" ")[3].strip()


def get_current_standby_time() -> int:
    """
    Gets the PC's current standby time before it goes to sleep.
    """
    scheme_guid = get_active_power_scheme()
    output = subprocess.check_output(
        ["powercfg", "/q", scheme_guid, "SUB_SLEEP"]
    ).decode()
    key = (
        "Current DC Power Setting Index:"
        if using_battery()
        else "Current AC Power Setting Index:"
    )
    standby_raw = output.partition(key)[2].split()[0]
    return int(int(standby_raw, 16) / 60)


def set_standby_time(standby_time: int) -> None:
    """
    Sets standby time before sleep.
    """
    arg = "-standby-timeout-dc" if using_battery() else "-standby-timeout-ac"
    subprocess.call(["powercfg", "-change", arg, str(standby_time)])


def perform_action(action) -> None:
    """
    Performs given action.
    """
    match action:
        case "Sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        case "Shutdown":
            os.system("shutdown /s /t 1")
        case _:
            print(f"{action} Not Found")
