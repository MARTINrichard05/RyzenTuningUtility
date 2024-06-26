from multiprocessing.connection import Listener
import subprocess

import sys
import time

key = sys.argv[1]
user = sys.argv[2]

if sys.argv[3] == "1":
    verbose = True
else:
    verbose = False

print("Verbose mode :", verbose)

workingDir = "/home/"+user+"/.var/app/com.nyaker.RyzenTuningUtility/daemon"

address = ('localhost', 6000)

listener = Listener(address, authkey=bytes(key, 'ascii'))

backupvals = {}
timeout = 0.02
cmdout_buffer = []

def logg(msg,cat):
    '''cat 0 : full running log, cat 1 : info, 2 : warning, 3 : error, 4 : debug'''
    if verbose != "0":
        if cat == 0:
            print(str(msg))
        if cat > 0 and cat < 5:
            cats = ["INFO", "WARNING", "ERROR", "DEBUG"]
            if cat >= verbose:
                print("["+cats[cat-1]+"] : "+str(msg))

def getraw(value):
    # if we have read this value
    global cmdout_buffer
    cmdout = None

    rawoutput = None

    if cmdout_buffer != []:
        if time.time() - cmdout_buffer[1] < timeout:
            cmdout = cmdout_buffer[0]

    if cmdout is None:
        try:
            cmdout = subprocess.check_output([workingDir+'/ryzenadj/ryzenadj', '-i']).decode('utf-8').split('\n')
            cmdout_buffer = [cmdout, time.time()]
        except:
            return backupvals[value]

    for line in cmdout:
        if value in line:
            rawoutput = (line.split(" "))

    if rawoutput is None:
        return 1

    for i in range(len(rawoutput)-1):
        if rawoutput[i] == "":
            pass
        else:
            try:
                backupvals[value] = float(rawoutput[i])
                return float(rawoutput[i])
            except :
                pass
def getVal(value):


    if value == "all":
        return {"temp" : float(getraw("THM VALUE CORE")),
                "max_temp": int(getraw("THM LIMIT CORE")),
                "avg_power": float(getraw("PPT VALUE SLOW")),
                "max_avg_power": int(getraw("PPT LIMIT SLOW")),
                "peak_power": float(getraw("PPT VALUE FAST")),
                "max_peak_power": int(getraw("PPT LIMIT FAST")),
                "max_skin_temp": float(getraw("STT LIMIT APU")),
                "skin_temp": float(getraw("STT VALUE APU")),
                }

    elif value == "temp":
        return getraw("THM VALUE CORE")
    elif value == "max_temp":
        return getraw("THM LIMIT CORE")
    elif value == "avg_power":
        return getraw("PPT VALUE SLOW")
    elif value == "max_avg_power":
        return getraw("PPT LIMIT SLOW")
    elif value == "peak_power":
        return getraw("PPT LIMIT FAST")
    elif value == "max_peak_power":
        return getraw("PPT LIMIT FAST")
    elif value == "skin_temp_limit":
        return getraw("STT LIMIT APU")
    elif value == "skin_temp":
        return getraw("STT VALUE APU")
    else:
        return None

def decompose_and_set(msg):
    for i in range(len(msg)):
        if msg[i] == "set":
            pass
        elif msg[i] == "max_temp":
            i += 1
            if type(msg[i]) == int:
                if msg[i] < 55:
                    pass
                elif msg[i] > 95:
                    pass
                else:
                    try:
                        subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-f", str(msg[i])], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    except:
                        pass
        elif msg[i] == "max_avg_power":
            i += 1
            if type(msg[i]) == int:
                if msg[i] < 6000:
                    pass
                elif msg[i] > 60000:
                    pass
                else:
                    try:
                        subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-a", str(msg[i])], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                        subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-c", str(msg[i])], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    except:
                        pass
        elif msg[i] == "max_peak_power":
            i += 1
            if type(msg[i]) == int:
                try:
                    subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-b", str(msg[i])], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                except:
                    pass
        elif msg[i] == "max_skin_temp":
            i += 1
            if type(msg[i]) == int:
                if msg[i] < 55:
                    pass
                elif msg[i] > 95:
                    pass
                else:
                    try:
                        subprocess.call([workingDir + '/ryzenadj/ryzenadj', "--apu-skin-temp="+str(msg[i])], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    except:
                        pass


def main_loop():
    conn = listener.accept()
    running = True
    while running:
        try :
            while conn.poll():
                msg = conn.recv()
                if msg == "EXIT":
                    running = False
                elif msg[0] == "set":
                    decompose_and_set(msg)
                elif msg[0] == "get":
                    conn.send(getVal(msg[1]))
                elif msg == "TEST":
                    cmdout = subprocess.run([workingDir + '/ryzenadj/ryzenadj', '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
                    conn.send(cmdout)

                # Other code can go here
            time.sleep(0.05)
        except :
            logg("Daemon error", 3)
            running = False

main_loop()
logg("Daemon closed", 1)
