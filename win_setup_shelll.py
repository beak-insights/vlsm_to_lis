import os
from config import BASE_DIR
from helpers import is_windows


user_path = os.path.expanduser('~')
sartup_path = os.path.join(
    user_path, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

sartup_file = os.path.join(BASE_DIR, "run_interface.cmd")
silencer_file = os.path.join(sartup_path, "hl7_silencer.vbs")


def init():
    # create the startup file
    with open(sartup_file, "w+") as out_file:
        out_file.write(f"python {BASE_DIR}")

    # create another file to run the startup script in bg
    with open(silencer_file, "w+") as silencer:
        the_shell = f"""
        Set WshShell = CreateObject("WScript.Shell")
        WshShell.Run Chr(34) & "{sartup_file}" & Chr(34), 0
        Set WshShell = Nothing
        """
        silencer.write(the_shell)

    # reboot windows machine
    # os.system("shutdown /r /t 1")  # os.system("shutdown -t 0 -r -f")


if __name__ == '__main__':
    if is_windows():
        init()
    else:
        print("This setup file is meant for Windows os only!")

# ddnt work
# xxx = """
# Set onShell = CreateObject ("Wscript.Shell")
# Dim strArgs
# strArgs = "cmd /c {}
# onShell.Run strArgs, 0, false
# """
