from subprocess import call, check_output
from sys import argv
import os

WorkingDirectory = argv[1]
path = argv[2]

user = check_output(['whoami']).decode('utf-8')[:-1]
print("\n=-=-=-=-=-=-=-= Running Admin installer as "+user+" =-=-=-=-=-=-=-=\n")


daemonfiles = [("/daemon/RyzenTuningDaemon.py", "/daemon"), ("/daemon/ryzenadj/ryzenadj", "/daemon/ryzenadj"), ("/daemon/ryzenadj/libryzenadj.so", "/daemon/ryzenadj")]

i = 0
print("\n======= installing Protected files =======")
for file in daemonfiles:
    if file[1] == '':
        pass
    else:
        call(("mkdir", "-p", path + file[1]))
    call(("cp", "-f", "-r", WorkingDirectory+ file[0], path + file[1]))
    i += 1
    print((i / len(daemonfiles)) * 100, "%.")
print("\n======= protected files copied into " + path + " =======\n")

call(("cp", "-f", WorkingDirectory + "/etc/com.nyaker.RyzenTuningUtility.svg", "/usr/share/icons/hicolor/scalable/apps"))
print("\n======= Icon copied into " + "/usr/share/icons/hicolor/scalable/apps" + " =======\n")