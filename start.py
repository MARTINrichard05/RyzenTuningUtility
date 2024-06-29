#!/usr/bin/python
import sys
from subprocess import check_output, call
from multiprocessing import Process
from multiprocessing.connection import Client, Listener
import os
import random

version = 13
testMode = False
user = check_output(['whoami']).decode('utf-8')[:-1]
path = "/home/"+user+"/.var/app/com.nyaker.RyzenTuningUtility"
key = random.randint(0,999999999999999999)
connAddress = ('localhost', 6001)
address = ('localhost', 6000)


def start(verbose):
    try :
        conn = Client(connAddress, authkey=bytes('open/close', 'ascii'))
        conn.send('OPEN')
        conn.close()
    except :

        if user == 'root':
            print('do not run as root please, passwd will be asked next')
        else :
            daemon_proc = Process(target=startDaemon, args=(verbose,))
            gui_proc = Process(target=startGui, args=(verbose,))
            daemon_proc.start()
            gui_proc.start()
            daemon_proc.join()
            gui_proc.join()
def startDaemon(verbose):
    if testMode:
        code = call((python, path + '/daemon/RyzenTuningDaemon.py', str(key), user, verbose))
    else:
        code = call(('pkexec', python, path + '/daemon/RyzenTuningDaemon.py', str(key), user, verbose))
        if code == 126:
            call(('zenity', '--error', '--text', 'PLEASE RESTART OR CLOSE RYZEN TUNING UTILITY (KILL DAEMON)'))
            listener = Listener(address, authkey=bytes(str(key), 'ascii'))
            conn = listener.accept()
            running = True
            while running:
                while conn.poll():
                    msg = conn.recv()
                    if msg == "EXIT":
                        running = False
                    else:
                        conn.send("EXIT")

def startGui(verbose):
    call((python, path + '/gui/RyzenTuningUtility.py', str(key), user, verbose))

if os.path.exists("/usr/bin/python"):
    python = "python"
elif os.path.exists("/usr/bin/python3"):
    python = "python3"
else:
    print("=============== python not found ===============")
    print("Your distro is not currently supported, you can still try to modify the script, please report the problem in github")
    exit(1)

try :
    arg = sys.argv[1]
    if arg == "version":
        print(version)
    elif arg == "test":
        print("Entering Test Mode")
        testMode = True
        start("0")
    elif arg == "log":

        try:
            subarg = int(sys.argv[2])
        except:
            print("Invalid argument")
        else:
            if subarg in range(1, 4):
                start(str(subarg))

    else :
        print(sys.argv)
except Exception as e:
    print(e)
    start("0")



