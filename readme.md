# Hl7DB to Senaite

### create a mysql user if not exist 
`create user 'username'@'%' identified with mysql_native_password by '<password>';`

make sure you have installed `python 3.9.5 or higher`

run `pip install -r requirements.txt`

### linux setup crontab
## option 1
if you want to use cron specific time scheduler the set `LINUX_USING_CRON_TIME_SCHEDULER = True` and

command `crontab -e` and add to the bottom of the file `*/10 * * * * /usr/bin/python path/to/script/folder`

reboot and check logs

## option 2
If you want the script to manage the schecule the set `LINUX_USING_CRON_TIME_SCHEDULER = False`  and

command `crontab -e` and add to the bottom of the file `@reboot /usr/bin/python path/to/script/folder`

reboot and check logs


### windows setup
Somewhere here `C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

add a file with name 'hl7_interface.cmd' with this content `python path\to\your\script\folder`

reboot and check logs