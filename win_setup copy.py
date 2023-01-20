import os
from config import BASE_DIR
from helpers import is_windows


user_path = os.path.expanduser('~')
sartup_path = os.path.join(
    user_path, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

sartup_file = os.path.join(sartup_path, "hl7_senaite.bat")


def init():
    with open(sartup_file, "w+") as out_file:
        out_file.write(f"python {BASE_DIR}")

    # reboot windows machine
    os.system("shutdown /r /t 1")  # os.system("shutdown -t 0 -r -f")


if __name__ == '__main__':
    if is_windows():
        init()
    else:
        print("This setup file is meant for Windows os only!")
