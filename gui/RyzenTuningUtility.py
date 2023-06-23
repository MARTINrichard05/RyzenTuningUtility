import sys
from multiprocessing.connection import Client, Listener
from random import randbytes
from threading import Thread
from time import sleep
import json

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

key = sys.argv[1]
user = sys.argv[2]

workingDir = "/home/"+user+"/.var/app/com.nyaker.RyzenTuningUtility/gui"

local_key = randbytes(256)  # this is the key that will be used to authenticate the connection between gui and handler
local_address = ('localhost', 6006)

connAddress = ('localhost', 6000)  # privilidged daemon

unsecure_address = ('localhost', 6001)
unsecure_key = bytes('open/close', 'ascii')

cpuparams = {"tempEdit": False, "temp": 75,
                          "avgPEdit": False, "avgpower": 10,
                          "pkPEdit": False, "pkpower": 13,
                          }




class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(600, 250)
        self.set_title("RyzenTuningUtility")
        app = self.get_application()
        sm = app.get_style_manager()
        ## sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

        self.MainBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.SlidersBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.header = Gtk.HeaderBar()

        self.set_titlebar(self.header)

        self.MainBox.set_spacing(10)
        self.MainBox.set_hexpand(False)
        self.SlidersBox.set_hexpand(True)

        self.ExitButton = Gtk.Button(label="KILL DAEMON")
        self.ExitButton.connect('clicked', self.Exit)
        
        self.initTemp()

        self.initavgPower()

        self.initpkPower()

        self.initPresets()

        self.set_child(self.MainBox)
        self.header.pack_start(self.ExitButton)
        self.MainBox.append(self.SlidersBox)

    def readcfg(self):
        with open(workingDir + '/presets.json') as json_file:
            self.presets = json.load(json_file)

    def writecfg(self):
        with open(workingDir + '/presets.json', 'w') as fp:
            json.dump(self.presets, fp)

    def initPresets(self):
        try:
            self.readcfg()
        except:
            self.presets = {}
            self.writecfg()

        self.presetBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.presetBox.set_hexpand(False)
        #self.presetList = Gtk.ListStore()
        #self.presetList.append(["test", "1"])
        #self.presetList.append(["test", "2"])

        #self.presetBox.append(self.presetList)
        self.MainBox.append(self.presetBox)



    def initTemp(self):
        global cpuparams
        self.tempbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.tempbox.set_margin_bottom(15)

        self.templabel = Gtk.Label(label="Max Temperature : "+str(cpuparams['temp'])+"C | enabled : " +str(cpuparams['tempEdit']))
        self.templabel.set_margin_top(5)

        self.tempReset = Gtk.Button(label="Reset")
        self.tempReset.connect('clicked', self.tempReset_clicked)
        self.tempReset.set_size_request(10,20)

        self.TempSlider = Gtk.Scale()
        self.TempSlider.set_digits(0)  # Number of decimal places to use
        self.TempSlider.set_range(60, 95)
        self.TempSlider.set_draw_value(False)  # Show a label with current value
        self.TempSlider.set_value(cpuparams['temp'])  # Sets the current value/position
        self.TempSlider.connect('value-changed', self.tempSlider_changed)
        self.TempSlider.set_hexpand(True) #

        self.SlidersBox.append(self.templabel)
        self.tempbox.append(self.tempReset)
        self.tempbox.append(self.TempSlider)
        self.SlidersBox.append(self.tempbox)

    def initavgPower(self):
        self.avgbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.avgbox.set_margin_bottom(15)

        self.avgPlabel = Gtk.Label(label="Max Avg Power : " +str(cpuparams['avgpower'])+"W | enabled : " +str(cpuparams['avgPEdit']))
        self.avgPlabel.set_margin_top(5)

        self.avgPowerReset = Gtk.Button(label="Reset")
        self.avgPowerReset.connect('clicked', self.avgPReset_clicked)

        self.avgPSlider = Gtk.Scale()
        self.avgPSlider.set_digits(0)  # Number of decimal places to use
        self.avgPSlider.set_range(6, 30)
        self.avgPSlider.set_draw_value(False)  # Show a label with current value
        self.avgPSlider.set_value(cpuparams['avgpower'])  # Sets the current value/position
        self.avgPSlider.connect('value-changed', self.avgPslider_changed)
        self.avgPSlider.set_hexpand(True)  #

        self.SlidersBox.append(self.avgPlabel)
        self.avgbox.append(self.avgPowerReset)
        self.avgbox.append(self.avgPSlider)
        self.SlidersBox.append(self.avgbox)

    def initpkPower(self):
        self.pkbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.pkbox.set_margin_bottom(15)

        self.pkPlabel = Gtk.Label(label="Max Peak Power : " + str(cpuparams['pkpower']) + "W | enabled : " + str(cpuparams['pkPEdit']))
        self.pkPlabel.set_margin_top(5)

        self.pkPowerReset = Gtk.Button(label="Reset")
        self.pkPowerReset.connect('clicked', self.pkPReset_clicked)

        self.pkPSlider = Gtk.Scale()
        self.pkPSlider.set_digits(0)  # Number of decimal places to use
        self.pkPSlider.set_range(8, 33)
        self.pkPSlider.set_draw_value(False)  # Show a label with current value
        self.pkPSlider.set_value(cpuparams['pkpower'])  # Sets the current value/position
        self.pkPSlider.connect('value-changed', self.pkPslider_changed)
        self.pkPSlider.set_hexpand(True)  #

        self.SlidersBox.append(self.pkPlabel)
        self.pkbox.append(self.pkPowerReset)
        self.pkbox.append(self.pkPSlider)
        self.SlidersBox.append(self.pkbox)


    def tempReset_clicked(self, button):
        conn = Client(local_address, authkey=local_key)
        conn.send(["TEMP", 0])
        conn.close()
        sleep(0.01)
        self.templabel.set_label("Max Temperature : " + str(cpuparams['temp']) + "C | enabled : " + str(cpuparams['tempEdit']))
    def avgPReset_clicked(self, button):
        conn = Client(local_address, authkey=local_key)
        conn.send(["AVGPOWER", 0])
        conn.close()
        sleep(0.01)
        self.templabel.set_label("Max Avg Power : " +str(cpuparams['avgpower'])+"W | enabled : " +str(cpuparams['avgPEdit']))
    def pkPReset_clicked(self, button):
        conn = Client(local_address, authkey=local_key)
        conn.send(["PKPOWER", 0])
        conn.close()
        sleep(0.01)
        self.templabel.set_label("Max Peak Power : " + str(cpuparams['pkpower']) + "W | enabled : " + str(cpuparams['pkPEdit']))

    def tempSlider_changed(self, slider):
        slidervalue = int(slider.get_value())
        self.templabel.set_label("Max Temperature : " + str(slidervalue))
        conn = Client(local_address, authkey=local_key)
        conn.send(["TEMP", slidervalue])
        conn.close()
        sleep(0.01)
        self.templabel.set_label("Max Temperature : " + str(cpuparams['temp']) + "C | enabled : " + str(cpuparams['tempEdit']))

    def avgPslider_changed(self, slider):
        slidervalue = int(slider.get_value())
        self.avgPlabel.set_label("Max Avg Power : " + str(slidervalue))
        conn = Client(local_address, authkey=local_key)
        conn.send(["AVGPOWER", slidervalue])
        conn.close()
        sleep(0.01)
        self.templabel.set_label("Max Avg Power : " + str(cpuparams['avgpower']) + "W | enabled : " + str(cpuparams['avgPEdit']))

    def pkPslider_changed(self, slider):
        slidervalue = int(slider.get_value())
        self.avgPlabel.set_label("Max Peak Power : " + str(slidervalue))
        conn = Client(local_address, authkey=local_key)
        conn.send(["PKPOWER", slidervalue])
        conn.close()
        sleep(0.01)
        self.templabel.set_label("Max Peak Power : " + str(cpuparams['pkpower']) + "W | enabled : " + str(cpuparams['pkPEdit']))


    def Exit(self, button):
        conn = Client(local_address, authkey=local_key)
        conn.send("EXIT")
        conn.close()


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.win = None

    def on_activate(self, app):
        if not self.win:
            self.win = MainWindow(application=app)
        self.win.present()


class CoreHandler:
    def __init__(self):
        self.running = True
        self.isgui = False


        self.connectionThread = Thread(target=self.connection)
        self.serverThread = Thread(target=self.server)
        self.localServerThread = Thread(target=self.localServer)  # initing some threads that are gonna run continuously

    def initGuiThread(self):  # isolate it into a function so any other code can run it (unsecure server)
        self.guithread = Thread(target=self.startGui)
        self.guithread.start()

    def startGui(self):
        self.isgui = True
        self.guiapp = MyApp(application_id="com.nyaker.RyzenTuningUtility")
        self.guiapp.run()
        self.isgui = False

    def run(self):
        self.connectionThread.start()  # init connection to the priviledged daemon

        self.serverThread.start()  # server for unsecure connection to the start process
        self.localServerThread.start()  # server for secure connection to the gui

        self.initGuiThread()

        self.localServerThread.join()
        self.serverThread.join()
        self.connectionThread.join()

    def server(self):  # connection to the start process (unsecure)
        sleep(0.2)

        listener = Listener(unsecure_address, authkey=unsecure_key)
        while self.running:
            if self.isgui == False:
                try:
                    conn = listener.accept()
                    while self.running:
                        while conn.poll():
                            msg = conn.recv()

                            if msg == "EXIT":
                                conn.close()
                                # self.exit()
                                break
                            elif msg == "OPEN":
                                self.initGuiThread()
                                break
                        if self.running == False:
                            break

                except:
                    pass
            else:
                sleep(0.1)

    def localServer(self):  # connection to the gui (secure)
        global cpuparams
        listener = Listener(local_address, authkey=local_key)
        while self.running:
            try:
                conn = listener.accept()
                while self.running:
                    msg = conn.recv()
                    if msg == "EXIT":
                        self.conn.send("EXIT")
                        conn.close()
                        self.running = False
                        break
                    elif msg[0] == "TEMP":
                        if int(msg[1]) == 0:
                            cpuparams["tempEdit"] = False
                        else :
                            cpuparams["temp"] = int(msg[1])
                            cpuparams["tempEdit"] = True
                    elif msg[0] == "AVGPOWER":
                        if int(msg[1]) == 0:
                            cpuparams["avgPEdit"] = False
                        else:
                            cpuparams["avgpower"] = int(msg[1])
                            cpuparams["avgPEdit"] = True
                    elif msg[0] == "PKPOWER":
                        if int(msg[1]) == 0:
                            cpuparams["pkPEdit"] = False
                        else :
                            cpuparams["pkpower"] = int(msg[1])
                            cpuparams["pkPEdit"] = True
            except:
                pass

    def connection(self):  # connection to the daemon (secure)
        global cpuparams
        while self.running:
            try:
                self.conn = Client(connAddress, authkey=bytes(key, 'ascii'))
                while self.running:
                    if cpuparams["tempEdit"] == True:
                        self.conn.send(["ryzenadj", "temp", cpuparams["temp"]])
                        sleep(0.2)
                    if cpuparams["avgPEdit"] == True:
                        self.conn.send(["ryzenadj", "avgpower", cpuparams["avgpower"] * 1000])
                        sleep(0.2)
                    if cpuparams["pkPEdit"] == True:
                        self.conn.send(["ryzenadj", "pkpower", cpuparams["pkpower"] * 1000])
                        sleep(0.2)
                    sleep(2)
            except:
                sleep(0.1)


# app = MyApp(application_id="com.example.GtkApplication")
# app.run()
app = CoreHandler()
app.run()

print('-----FrontEnd Stopped------')
