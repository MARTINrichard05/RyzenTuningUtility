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

params = {"tempEdit": False, "temp": 75,
                          "avgPEdit": False, "avgpower": 10,
                          "pkPEdit": False, "pkpower": 13,
          }





class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.running = True


        self.set_default_size(600, 250)
        self.set_title("RyzenTuningUtility")
        self.connect("close-request", self.closewin)
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

        connThread = Thread(target=self.connF)
        connThread.start()

    def closewin(self,arg):
        self.running = False

    def connF(self):
        self.conn = Client(local_address, authkey=local_key)
        while self.running:
            self.refresh()
            sleep(0.1)
        self.conn.close()

    def refresh(self):
        global params

        if params['tempEdit']: # refreshing temp bar
            self.disableTemp.set_label('Disable')
            self.tempbar.set_value(1)
            if params['temp'] != int(self.tempbar.get_value()):
                self.TempSlider.set_value(params['temp'])
        else:
            self.disableTemp.set_label('Enable')
            self.tempbar.set_value(0)

        if params["avgPEdit"]:
            self.DisableAvgPower.set_label('Disable')
            self.avgbar.set_value(1)
            if params['avgpower'] != int(self.avgbar.get_value()):
                self.avgPSlider.set_value(params['avgpower'])
        else:
            self.DisableAvgPower.set_label('Enable')
            self.avgbar.set_value(0)

        if params["pkPEdit"]:
            self.DisablePkPower.set_label('Disable')
            self.pkbar.set_value(1)
            if params['pkpower'] != int(self.pkbar.get_value()):
                self.pkPSlider.set_value(params['pkpower'])
        else:
            self.DisablePkPower.set_label('Enable')
            self.pkbar.set_value(0)

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
        global params
        self.tempbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.tempadj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.tempframe = Gtk.Frame()
        self.tempframe.set_margin_top(15)
        self.tempframe.set_margin_end(10)
        self.tempframe.set_child(self.tempbox)
        self.templabel = Gtk.Label()
        self.templabel.set_margin_top(10)
        self.templabel.set_label("Maximum temperature")

        self.tempbar = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.tempbar.set_min_value(0)
        self.tempbar.set_max_value(1)

        #self.templabel = Gtk.Label(label="Max Temperature : "+str(params['temp'])+"C | enabled : " +str(params['tempEdit']))
        #self.templabel.set_margin_top(5)

        self.disableTemp = Gtk.Button(label="Disable")
        self.disableTemp.connect('clicked', self.tempReset_clicked)

        self.TempSlider = Gtk.Scale()
        self.TempSlider.set_digits(0)  # Number of decimal places to use
        self.TempSlider.set_range(60, 95)
        self.TempSlider.set_draw_value(True)  # Show a label with current value
        self.TempSlider.set_value(params['temp'])  # Sets the current value/position
        self.TempSlider.connect('value-changed', self.tempSlider_changed)
        self.TempSlider.set_hexpand(True) #

        self.tempadj.append(self.disableTemp)
        self.tempadj.append(self.TempSlider)
        self.tempbox.append(self.tempbar)
        self.tempbox.append(self.templabel)
        self.tempbox.append(self.tempadj)
        self.SlidersBox.append(self.tempframe)

    def initavgPower(self):
        self.avgbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.avgedit = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.avgframe = Gtk.Frame()
        self.avgframe.set_margin_top(15)
        self.avgframe.set_margin_end(10)
        self.avgframe.set_child(self.avgbox)
        self.avgplabel = Gtk.Label()
        self.avgplabel.set_margin_top(10)
        self.avgplabel.set_label('Average Power Limit')

        self.avgbar = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.avgbar.set_min_value(0)
        self.avgbar.set_max_value(1)

        self.DisableAvgPower = Gtk.Button(label="Disable")
        self.DisableAvgPower.connect('clicked', self.avgPReset_clicked)

        self.avgPSlider = Gtk.Scale()
        self.avgPSlider.set_digits(0)  # Number of decimal places to use
        self.avgPSlider.set_range(6, 30)
        self.avgPSlider.set_draw_value(True)  # Show a label with current value
        self.avgPSlider.set_value(params['avgpower'])  # Sets the current value/position
        self.avgPSlider.connect('value-changed', self.avgPslider_changed)
        self.avgPSlider.set_hexpand(True)  #

        self.avgbox.append(self.avgbar)
        self.avgbox.append(self.avgplabel)
        self.avgedit.append(self.DisableAvgPower)
        self.avgedit.append(self.avgPSlider)
        self.avgbox.append(self.avgedit)
        self.SlidersBox.append(self.avgframe)

    def initpkPower(self):
        self.pkbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.pkedit = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.pkframe = Gtk.Frame()
        self.pkframe.set_margin_top(15)
        self.pkframe.set_margin_bottom(15)
        self.pkframe.set_margin_end(10)
        self.pkframe.set_child(self.pkbox)
        self.pkplabel = Gtk.Label()
        self.pkplabel.set_margin_top(10)
        self.pkplabel.set_label('Peak Power Limit')


        self.pkbar = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.pkbar.set_min_value(0)
        self.pkbar.set_max_value(1)

        self.DisablePkPower = Gtk.Button(label="Disable")
        self.DisablePkPower.connect('clicked', self.pkPReset_clicked)

        self.pkPSlider = Gtk.Scale()
        self.pkPSlider.set_digits(0)  # Number of decimal places to use
        self.pkPSlider.set_range(8, 33)
        self.pkPSlider.set_draw_value(True)  # Show a label with current value
        self.pkPSlider.set_value(params['pkpower'])  # Sets the current value/position
        self.pkPSlider.connect('value-changed', self.pkPslider_changed)
        self.pkPSlider.set_hexpand(True)  #

        self.pkbox.append(self.pkbar)
        self.pkbox.append(self.pkplabel)
        self.pkedit.append(self.DisablePkPower)
        self.pkedit.append(self.pkPSlider)
        self.pkbox.append(self.pkedit)
        self.SlidersBox.append(self.pkframe)


    def tempReset_clicked(self, button):
        if params['tempEdit']:
            self.conn.send(["TEMP", 0])
        else:
            self.conn.send(["TEMP", 1])
        sleep(0.01)
    def avgPReset_clicked(self, button):
        if params["avgPEdit"]:
            self.conn.send(["AVGPOWER", 0])
        else:
            self.conn.send(["AVGPOWER", 1])
        sleep(0.01)
    def pkPReset_clicked(self, button):
        if params["pkPEdit"]:
            self.conn.send(["PKPOWER", 0])
        else:
            self.conn.send(["PKPOWER", 1])
        sleep(0.01)

    def tempSlider_changed(self, slider):
        slidervalue = int(slider.get_value())
        #self.templabel.set_label("Max Temperature : " + str(slidervalue))
        self.conn.send(["TEMP", slidervalue])
        sleep(0.01)
        #self.templabel.set_label("Max Temperature : " + str(params['temp']) + "C | enabled : " + str(params['tempEdit']))

    def avgPslider_changed(self, slider):
        slidervalue = int(slider.get_value())
        #self.avgPlabel.set_label("Max Avg Power : " + str(slidervalue))
        self.conn.send(["AVGPOWER", slidervalue])
        sleep(0.01)
        #self.avgPlabel.set_label("Max Avg Power : " + str(params['avgpower']) + "W | enabled : " + str(params['avgPEdit']))

    def pkPslider_changed(self, slider):
        slidervalue = int(slider.get_value())
        #self.pkPlabel.set_label("Max Peak Power : " + str(slidervalue))
        self.conn.send(["PKPOWER", slidervalue])
        sleep(0.01)
        #self.pkPlabel.set_label("Max Peak Power : " + str(params['pkpower']) + "W | enabled : " + str(params['pkPEdit']))


    def Exit(self, button):
        self.running = False
        self.conn.send("EXIT")
        self.conn.close()


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
        global params
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
                            params["tempEdit"] = False
                        elif int(msg[1]) == 1:
                            params["tempEdit"] = True
                        else :
                            params["temp"] = int(msg[1])
                            #params["tempEdit"] = True
                    elif msg[0] == "AVGPOWER":
                        if int(msg[1]) == 0:
                            params["avgPEdit"] = False
                        elif int(msg[1]) == 1:
                            params["avgPEdit"] = True
                        else:
                            params["avgpower"] = int(msg[1])
                            #params["avgPEdit"] = True
                    elif msg[0] == "PKPOWER":
                        if int(msg[1]) == 0:
                            params["pkPEdit"] = False
                        elif int(msg[1]) == 1:
                            params["pkPEdit"] = True
                        else :
                            params["pkpower"] = int(msg[1])
                            #params["pkPEdit"] = True
            except:
                pass

    def connection(self):  # connection to the daemon (secure)
        global params
        while self.running:
            try:
                self.conn = Client(connAddress, authkey=bytes(key, 'ascii'))
                while self.running:
                    if params["tempEdit"] == True:
                        self.conn.send(["ryzenadj", "temp", params["temp"]])
                        sleep(0.2)
                    if params["avgPEdit"] == True:
                        self.conn.send(["ryzenadj", "avgpower", params["avgpower"] * 1000])
                        sleep(0.2)
                    if params["pkPEdit"] == True:
                        self.conn.send(["ryzenadj", "pkpower", params["pkpower"] * 1000])
                        sleep(0.2)
                    sleep(2)
            except:
                sleep(0.1)


# app = MyApp(application_id="com.example.GtkApplication")
# app.run()
app = CoreHandler()
app.run()

print('-----FrontEnd Stopped------')
