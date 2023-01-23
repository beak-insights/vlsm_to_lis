# Hl7DB to Senaite

### create a mysql/mariadb user if not exist 
create databse `create database db_name;`

create user in mysql: `create user 'username'@'%' identified with mysql_native_password by '<password>';` and then 
`GRANT ALL PRIVILEGES ON db_name.* TO 'username'@'%';`

create user in mariadb `grant all privileges on databse_name.* TO 'username'@'%' identified by '<password>';` 

finally `fush privileges`


make sure you have installed `python 3.9.5 or higher`

run `pip install -r requirements.txt`

## Scheduling Automatic executin os the script

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
From the root of this package just run the command `python win_setup.py`. This action will automatically reboot the PC in 3s. After logon check the logs.

It will setup the 2 required auto start scripts. The first script with name `run_interface.cmd` will be 
created in the same root directory of the project. The second script will be created in the windows startup folder with name `hl7_silencer.vbs`. 
The purpose of `run_interface.cmd` file is to run the program however it opens a cmd terminal window by default which can be closed by the users. The `hl7_silencer.vbs` file executes the `run_interface.cmd` in the bg *(as a process daemon)*

Another option is to setup Windows Scheduler but it has not been tried and tested on this package. Research on it