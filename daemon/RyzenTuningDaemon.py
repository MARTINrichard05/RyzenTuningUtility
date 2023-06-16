from multiprocessing.connection import Listener
import subprocess

import sys
import time

workingDir = "/home/richou/.var/app/com.nyaker.RyzenTuningUtility/daemon"

key = sys.argv[1]

address = ('localhost', 6000)

listener = Listener(address, authkey=bytes(key, 'ascii'))

def decompose_and_set(msg):
    for i in range(len(msg)):
        if msg[i] == "ryzenadj":
            pass
        elif msg[i] == "temp":
            i += 1
            if msg[i] < 60:
                pass
            elif msg[i] > 95:
                pass
            else:
                subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-f", str(msg[i])])
        elif msg[i] == "avgpower":
            i += 1
            if msg[i] < 6000:
                pass
            elif msg[i] > 30000:
                pass
            else:
                subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-a", str(msg[i])])
                subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-c", str(msg[i])])
        elif msg[i] == "pkpower":
            i += 1
            subprocess.call([workingDir + '/ryzenadj/ryzenadj', "-b", str(msg[i])])


def main_loop():
    conn = listener.accept()
    running = True
    while running:
        while conn.poll():
            msg = conn.recv()
            if msg == "EXIT":
                running = False
            elif msg[0] == "ryzenadj":
                decompose_and_set(msg)
            elif msg == "TEST":
                cmdout = subprocess.run([workingDir + '/ryzenadj/ryzenadj', '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
                conn.send(cmdout)

            # Other code can go here
        #print("server running !")
        time.sleep(0.1)

main_loop()
print("------Daemon Stopped----")