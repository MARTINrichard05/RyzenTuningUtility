import sys
from multiprocessing.connection import Client, Listener
from random import randbytes
from threading import Thread
from time import sleep
import json
from random import randint
import copy

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib

key = sys.argv[1]
user = sys.argv[2]
verbose = int(sys.argv[3])

print("Verbose mode :", verbose)

workingDir = "/home/" + user + "/.var/app/com.nyaker.RyzenTuningUtility/gui"

local_key = randbytes(256)  # this is the key that will be used to authenticate the connection between gui and handler
local_address = ('localhost', 6006)

connAddress = ('localhost', 6000)  # privileged daemon

unsecure_address = ('localhost', 6001)
unsecure_key = bytes('open/close', 'ascii')

params = {"settings": {"temp_enabled": False, "max_temp": 80, "skin_temp_enabled": False, "max_skin_temp": 45,
                       "avg_power_enabled": False, "max_avg_power": 15, "peak_power_enabled": False,
                       "max_peak_power": 20,
                       "mode": "manual"}, "updated": False,
          "limits": {"temp": 90, "avg_power": 500, "peak_power": 1000, "skin_temp": 90}}

def logg(msg,cat):
    '''cat 0 : full running log, cat 1 : info, 2 : warning, 3 : error, 4 : debug'''
    if verbose != "0":
        if cat == 0:
            print(str(msg))
        if cat > 0 and cat < 5:
            cats = ["INFO", "WARNING", "ERROR", "DEBUG"]
            if cat >= verbose:
                print("["+cats[cat-1]+"] : "+str(msg))

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):

        logg("Starting GUI, INIT",1)
        self.conn = None
        self.hamburger = None
        self.Phamburger = None
        self.popover = None
        self.menu = None
        self.presets = None
        self.ui_elements = {}

        while True:
            try:
                a = params['stats']
                break
            except:
                pass
            sleep(0.1)

        super().__init__(*args, **kwargs)

        self.running = True
        self.prename = ""
        self.Pmenu = True
        self.actions = True
        self.first = True

        self.set_default_size(600, 250)
        self.set_title("RyzenTuningUtility")
        self.connect("close-request", self.closewin)
        # app = self.get_application()
        # sm = app.get_style_manager()
        # # sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

        self.MainBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.SlidersBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.header = Gtk.HeaderBar()

        self.set_titlebar(self.header)

        self.MainBox.set_spacing(10)
        self.MainBox.set_hexpand(False)
        self.SlidersBox.set_hexpand(True)

        self.ExitButton = Gtk.Button(label="KILL DAEMON")
        self.ExitButton.connect('clicked', self.Exit)

        self.inittemp()

        self.initstemp()

        self.initavgpower()

        self.initpkpower()

        self.initpresets()

        self.set_child(self.MainBox)
        self.header.pack_start(self.ExitButton)
        self.MainBox.append(self.SlidersBox)
        logg("gui init almost done",0)

        connthread = Thread(target=self.conn_f)
        connthread.start()
        logg("Connection thread started",0)
        self.timeout_id = GLib.timeout_add(30, self.refresh)
        logg("gui init finished",1)

    def closewin(self, arg):
        logg("Closing Window",1)
        GLib.source_remove(self.timeout_id)
        self.running = False

    def conn_f(self):
        logg("Starting connection thread",1)
        self.conn = Client(local_address, authkey=local_key)
        logg("Connection thread started",0)
        while self.running:
            sleep(0.3)
        self.conn.close()
        logg("Connection thread stopped",0)

    def refresh(self):
        logg("Refreshing",0)
        global params
        if params["updated"]:
            settings = [("temp_enabled", "max_temp", "temp"), ("skin_temp_enabled", "max_skin_temp", "skin_temp"),
                        ("avg_power_enabled", "max_avg_power", "avg_power"),
                        ("peak_power_enabled", "max_peak_power", "peak_power")]

            for setting_enabled, setting_max, stat in settings:
                if params['settings'][setting_enabled]:
                    self.ui_elements[setting_max]['disablebutton'].set_label('Disable')
                    self.ui_elements[setting_max]['bar01'].set_value(1)
                else:
                    self.ui_elements[setting_max]['disablebutton'].set_label('Enable')
                    self.ui_elements[setting_max]['bar01'].set_value(0)

                if self.ui_elements[setting_max]['bar'].get_allocated_width() != 0 and self.ui_elements[setting_max][
                    'bar'].get_allocated_height() != 0:
                    self.ui_elements[setting_max]['bar'].set_max_value(params['stats'][setting_max])
                    self.ui_elements[setting_max]['bar'].set_value(params['stats'][stat])

                if params['settings'][setting_max] != int(self.ui_elements[setting_max]['slider'].get_value()):
                    self.ui_elements[setting_max]['slider'].set_value(params['settings'][stat])

            params['updated'] = False
        else:
            pass
        if self.running:
            return True
        else:
            return False

    def readcfg(self):
        logg("Reading presets",1)
        with open(workingDir + '/presets.json') as json_file:
            self.presets = json.load(json_file)

    def writecfg(self):
        logg("Writing presets",1)
        with open(workingDir + '/presets.json', 'w') as fp:
            json.dump(self.presets, fp)

    def reloadpmenu(self):
        logg("Reloading preset menu",1)
        if self.Pmenu:
            del self.Pmenu
            logg("Preset menu deleted",0)
        if self.actions:
            del self.actions
            logg("Actions deleted",0)

        self.Pmenu = Gio.Menu.new()
        self.actions = []
        for i in self.presets:
            self.actions.append(
                [Gio.Menu.new(), Gio.SimpleAction.new(i + "Enable", None), Gio.SimpleAction.new(i + "Save", None),
                 Gio.SimpleAction.new(i + "Rename", None),
                 Gio.SimpleAction.new(i + "Delete", None)])

            buff = ["Enable", "Save", "Rename", "Delete"]
            for j in range(1, len(buff) + 1):
                self.actions[len(self.actions) - 1][j].connect("activate", self.presetchanged, (i, buff[j - 1]))
                self.add_action(self.actions[len(self.actions) - 1][j])
            for j in buff:
                self.actions[len(self.actions) - 1][0].append(j, "win." + i + j)
            self.Pmenu.append_submenu(i, self.actions[len(self.actions) - 1][0])

        if not self.first:
            self.menu.remove(1)
            self.menu.append_submenu("Presets", self.Pmenu)
        else:
            self.first = False
        logg("Preset menu reloaded",1)
    def initpresets(self):
        logg("Initing presets",1)
        try:
            self.readcfg()
        except:
            self.presets = {}
            self.writecfg()


        new_preset = Gio.SimpleAction.new("new_preset", None)
        new_preset.connect("activate", self.new_preset)
        self.add_action(new_preset)

        self.menu = Gio.Menu.new()
        self.menu.append("new preset", "win.new_preset")


        self.popover = Gtk.PopoverMenu()
        self.popover.set_menu_model(self.menu)


        self.Phamburger = Gtk.MenuButton()
        self.Phamburger.set_icon_name("open-menu-symbolic")
        self.reloadpmenu()
        self.menu.append_submenu("Presets", self.Pmenu)

        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")  # Give it a nice icon

        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)
        logg("Presets inited",1)

    def select_pname(self):
        """asks the user to rename the preset"""
        logg("Selecting preset name",0)
        entry = Gtk.Entry()
        entry.connect("activate", self.rename_preset)  # when the user presses enter
        self.MainBox.append(entry)  # add the entry to the window

    def rename_preset(self, entry):
        """when the user presses enter, rename the preset"""
        logg("Renaming preset",0)
        newkey = entry.get_text()
        if ' ' in newkey:
            newkey = newkey.replace(' ', '_')
        self.MainBox.remove(entry)

        if newkey != self.prename[0]:
            self.presets[newkey] = self.presets[self.prename]
            del self.presets[self.prename]
            self.MainBox.remove(entry)
            self.writecfg()
            self.reloadpmenu()

    def new_preset(self, action, param):
        """creates a new preset with the current settings"""
        logg("Creating new preset",1)
        self.prename = str(randint(0, 99999))
        self.presets[self.prename] = copy.deepcopy(params['settings'])
        self.select_pname()  # ask the user to rename the preset
        pass

    def presetchanged(self, action, param, preset_name):
        """handles action with presets, enable, save, rename, delete"""
        logg("Preset changing",1)
        global params
        preset, action = preset_name[0], preset_name[1]
        if action == "Enable":
            logg("Enabling preset",1)
            if preset in self.presets:
                for i in self.presets[preset]:  # safe and ensure compatibility with older config files
                    params['settings'][i] = self.presets[preset][i]
                params['updated'] = True
            else:
                logg("Preset not found",2)

        elif action == "Save":
            logg("Saving preset",1)
            if preset in self.presets:
                if params['settings']["mode"] == "manual":
                    self.presets[preset] = copy.deepcopy(params['settings'])
                    self.writecfg()
                    self.reloadpmenu()
            else:
                logg("Preset not found",2)

        elif action == "Rename":
            logg("Renaming preset",1)
            if preset in self.presets:
                self.prename = preset
                self.select_pname()
            else:
                logg("Preset not found",2)

        elif action == "Delete":
            logg("Deleting preset",1)
            if preset in self.presets:
                del self.presets[preset]
                self.writecfg()
                self.reloadpmenu()
            else:
                logg("Preset not found",2)

    def initslider(self, label_text, slider_range, slider_value, reset_callback, slider_callback, key_text):
        logg("Initing slider :"+str(label_text),1)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        adj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        frame = Gtk.Frame()
        frame.set_margin_top(15)
        frame.set_margin_end(10)
        frame.set_child(box)
        plabel = Gtk.Label()
        plabel.set_margin_top(10)
        plabel.set_label(label_text)

        bar = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        bar.set_min_value(0)
        bar.set_max_value(100)

        bar01 = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        bar01.set_min_value(0)
        bar01.set_max_value(1)

        disablebutton = Gtk.Button(label="Disable")
        disablebutton.connect('clicked', reset_callback)

        slider = Gtk.Scale()
        slider.set_digits(0)  # Number of decimal places to use
        slider.set_range(*slider_range)
        slider.set_draw_value(True)  # Show a label with current value
        slider.set_value(slider_value)  # Sets the current value/position
        slider.connect('value-changed', slider_callback)
        slider.set_hexpand(True)  #

        adj.append(disablebutton)
        adj.append(slider)
        box.append(bar)
        box.append(plabel)
        box.append(adj)
        box.append(bar01)
        self.SlidersBox.append(frame)

        # Store the UI elements in the self.ui_elements dictionary
        self.ui_elements[key_text] = {
            'box': box,
            'adj': adj,
            'frame': frame,
            'plabel': plabel,
            'bar': bar,
            'bar01': bar01,
            'disablebutton': disablebutton,
            'slider': slider
        }
        logg("Slider inited :"+str(self.ui_elements[key_text]),0)

    def inittemp(self):
        logg("Initing temp",1)
        global params
        self.initslider("Maximum temperature", (55, 97), params['settings']['max_temp'], self.tempReset_clicked,
                        self.tempSlider_changed, "max_temp")

    def initstemp(self):
        logg("Initing skin temp",1)
        global params
        self.initslider("Maximum Skin Temperature", (40, params['limits']['skin_temp']),
                        params['settings']['max_skin_temp'], self.stempReset_clicked, self.stempSlider_changed,
                        "max_skin_temp")

    def initavgpower(self):
        logg("Initing avg power",1)
        self.initslider('Average Power Limit', (7, 60), params['settings']['max_avg_power'], self.avgPReset_clicked,
                        self.avgPslider_changed, "max_avg_power")

    def initpkpower(self):
        logg("Initing peak power",1)
        self.initslider('Peak Power Limit', (9, 70), params['settings']['max_peak_power'], self.pkPReset_clicked,
                        self.pkPslider_changed, "max_peak_power")

    def tempReset_clicked(self, button):
        logg("Temp reset clicked",1)
        if params['settings']['temp_enabled']:
            self.conn.send(["max_temp", 0])
        else:
            self.conn.send(["max_temp", 1])
        sleep(0.01)

    def stempReset_clicked(self, button):
        logg("Skin temp reset clicked",1)
        if params['settings']['skin_temp_enabled']:
            self.conn.send(["max_skin_temp", 0])
        else:
            self.conn.send(["max_skin_temp", 1])
        sleep(0.01)

    def avgPReset_clicked(self, button):
        logg("Avg power reset clicked",1)
        if params['settings']["avg_power_enabled"]:
            self.conn.send(["max_avg_power", 0])
        else:
            self.conn.send(["max_avg_power", 1])
        sleep(0.01)

    def pkPReset_clicked(self, button):
        logg("Peak power reset clicked",1)
        if params['settings']["peak_power_enabled"]:
            self.conn.send(["max_peak_power", 0])
        else:
            self.conn.send(["max_peak_power", 1])
        sleep(0.01)

    def tempSlider_changed(self, slider):
        logg("Temp slider changed",0)
        slidervalue = int(slider.get_value())
        # self.templabel.set_label("Max Temperature : " + str(slidervalue))
        self.conn.send(["max_temp", slidervalue])
        sleep(0.01)
        # self.templabel.set_label("Max Temperature : " + str(params['settings']['max_temp']) + "C | enabled : " +
        # str(params['settings']['temp_enabled']))

    def avgPslider_changed(self, slider):
        logg("Avg power slider changed",0)
        slidervalue = int(slider.get_value())
        # self.avgPlabel.set_label("Max Avg Power : " + str(slidervalue))
        self.conn.send(["max_avg_power", slidervalue])
        sleep(0.01)
        # self.avgPlabel.set_label("Max Avg Power : " + str(params['settings']['max_avg_power']) + "W | enabled : " +
        # str(params['settings']['avg_power_enabled']))

    def pkPslider_changed(self, slider):
        logg("Peak power slider changed",0)
        slidervalue = int(slider.get_value())
        # self.pkPlabel.set_label("Max Peak Power : " + str(slidervalue))
        self.conn.send(["max_peak_power", slidervalue])
        sleep(0.01)
        # self.pkPlabel.set_label("Max Peak Power : " + str(params['settings']['max_peak_power']) + "W | enabled : "
        # + str(params['settings']['peak_power_enabled']))

    def stempSlider_changed(self, slider):
        logg("Skin temp slider changed",0)
        slidervalue = int(slider.get_value())
        # self.stemplabel.set_label("Max Skin Temperature : " + str(slidervalue))
        self.conn.send(["max_skin_temp", slidervalue])
        sleep(0.01)
        # self.stemplabel.set_label("Max Skin Temperature : " + str(params['settings']['max_skin_temp']) + "C |
        # enabled : " + str(params['settings']['skin_temp_enabled']))

    def Exit(self, button):
        logg("Killing Daemon",1)
        self.running = False
        self.conn.send("EXIT")
        self.conn.close()


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.win = None

    def on_activate(self, app):
        logg("App activated",1)
        if not self.win:
            logg("Creating window",0)
            self.win = MainWindow(application=app)
        logg("Presenting window",0)
        self.win.present()
        logg("Window presented",1)


class CoreHandler:
    def __init__(self):
        self.conn = None
        self.guiapp = None
        self.guithread = None
        self.running = True
        self.isgui = False
        global params

        self.connectionThread = Thread(target=self.connection)
        self.serverThread = Thread(target=self.server)
        self.localServerThread = Thread(target=self.localServer)  # initing some threads that are going to run
        # continuously
        logg('Frontend init finished',1)

    def initGuiThread(self):  # isolate it into a function so any other code can run it (unsecure server)
        logg("-----FrontEnd GUI Starting------",1)
        self.guithread = Thread(target=self.startGui)
        self.guithread.start()

    def startGui(self):
        logg("-----FrontEnd GUI Starting------",1)
        self.isgui = True
        self.guiapp = MyApp(application_id="com.nyaker.RyzenTuningUtility")
        self.guiapp.run()
        self.guiapp.quit()
        self.isgui = False
        logg('-----FrontEnd GUI Stopped------',1)

    def run(self):
        logg("-----FrontEnd Starting------",1)
        self.connectionThread.start()  # init connection to the priviledged daemon

        self.serverThread.start()  # server for unsecure connection to the start process
        self.localServerThread.start()  # server for secure connection to the gui

        sleep(0.01)
        self.initGuiThread()

        self.localServerThread.join()
        self.serverThread.join()
        self.connectionThread.join()

    def server(self):  # connection to the start process (unsecure)
        logg("-----FrontEnd Unsecure Server Starting------",1)
        sleep(0.2)

        listener = Listener(unsecure_address, authkey=unsecure_key)
        while self.running:
            if not self.isgui:

                logg("Open for wake request",1)
                try:
                    conn = listener.accept()
                    while self.running:
                        while conn.poll():
                            msg = conn.recv()

                            if msg == "EXIT":
                                conn.close()
                                self.conn.close()
                                logg("-----Gui Thread Stopping-----",1)
                                # self.exit()
                                break
                            elif msg == "OPEN":
                                logg("REQUESTED OPEN",0)
                                self.initGuiThread()
                                logg("-----Gui Thread Launching-----",1)
                                break
                        if not self.running:
                            break

                except Exception as e:
                    logg("Error in unsecure server",3)
                    logg(e,3)
                    pass
            else:
                logg("Gui is running : " + str(self.isgui),0)
                sleep(0.1)

    def localServer(self):  # connection to the gui (secure)
        global params
        listener = Listener(local_address, authkey=local_key)
        while self.running:
            try:
                logg("Local GUI server open",0)
                conn = listener.accept()
                logg("Local GUI server open and connected",1)
                while self.running:
                    msg = conn.recv()
                    if msg == "EXIT":
                        logg("Local GUI server closing EXIT received",1)
                        self.conn.send("EXIT")
                        self.conn.close()
                        conn.close()
                        self.running = False
                        break
                    elif msg[0] == "max_temp":
                        if int(msg[1]) == 0:
                            params['settings']["temp_enabled"] = False
                        elif int(msg[1]) == 1:
                            params['settings']["temp_enabled"] = True
                        else:
                            params['settings']["max_temp"] = int(msg[1])
                            # params['settings']["temp_enabled"] = True
                    elif msg[0] == "max_avg_power":
                        if int(msg[1]) == 0:
                            params['settings']["avg_power_enabled"] = False
                        elif int(msg[1]) == 1:
                            params['settings']["avg_power_enabled"] = True
                        else:
                            params['settings']["max_avg_power"] = int(msg[1])
                            # params['settings']["avg_power_enabled"] = True
                    elif msg[0] == "max_peak_power":
                        if int(msg[1]) == 0:
                            params['settings']["peak_power_enabled"] = False
                        elif int(msg[1]) == 1:
                            params['settings']["peak_power_enabled"] = True
                        else:
                            params['settings']["max_peak_power"] = int(msg[1])
                            # params['settings']["peak_power_enabled"] = True
                    elif msg[0] == "max_skin_temp":
                        if int(msg[1]) == 0:
                            params['settings']["skin_temp_enabled"] = False
                        elif int(msg[1]) == 1:
                            params['settings']["skin_temp_enabled"] = True
                        else:
                            params['settings']["max_skin_temp"] = int(msg[1])
            except Exception as e:
                logg("Error in local GUI server",3)
                logg(e,3)

    def connection(self):  # connection to the daemon (secure)
        global params

        while self.running:
            try:
                self.conn = Client(connAddress, authkey=bytes(key, 'ascii'))
                self.conn.send(['get', 'all'])
                params['stats'] = self.conn.recv()
                i = 0
                j = 0
                oldparams = copy.deepcopy(params['settings'])

                while self.running:
                    if self.isgui and not params["updated"]:
                        self.conn.send(['get', 'all'])
                        params['stats'] = self.conn.recv()
                        params["updated"] = True

                    elif not self.isgui:
                        if j >= 15:
                            j = 0
                            self.conn.send(['get', 'all'])
                            params['stats'] = self.conn.recv()
                            params["updated"] = True
                        else:
                            j += 1

                    if i >= 15:
                        i = 0
                        if params['settings']["temp_enabled"]:
                            if int(params['settings']["max_temp"]) != int(oldparams["max_temp"]):
                                # print("user changed temp")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_temp", params['settings']["max_temp"]])
                                sleep(0.01)

                            elif int(params['settings']["max_temp"]) != int(params['stats']["max_temp"]):
                                # print("target temp limit not equal to current limit")
                                sleep(0.1)
                                self.conn.send(["set", "max_temp", params['settings']["max_temp"]])
                                sleep(0.01)

                        if params['settings']["avg_power_enabled"]:
                            if int(params['settings']["max_avg_power"]) != int(oldparams["max_avg_power"]):
                                # print("user changed avg power")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_avg_power", params['settings']["max_avg_power"]])
                                sleep(0.01)
                            elif int(params['settings']["max_avg_power"]) != int(params['stats']["max_avg_power"]):
                                # print("target avg power limit not equal to current limit")
                                sleep(0.1)
                                self.conn.send(["set", "max_avg_power", params['settings']["max_avg_power"] * 1000])
                                sleep(0.01)

                        if params['settings']["peak_power_enabled"]:
                            if int(params['settings']["max_peak_power"]) != int(oldparams["max_peak_power"]):
                                # print("user changed peak power")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_peak_power", params['settings']["max_peak_power"]])
                                sleep(0.01)
                            elif int(params['settings']["max_peak_power"]) != int(params['stats']["max_peak_power"]):
                                # print("target peak power limit not equal to current limit")
                                sleep(0.1)
                                self.conn.send(["set", "max_peak_power", params['settings']["max_peak_power"] * 1000])
                                sleep(0.01)

                        if params['settings']["skin_temp_enabled"]:
                            if int(params['settings']["max_skin_temp"]) != int(oldparams["max_skin_temp"]):
                                # print("user changed skin temp")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_skin_temp", params['settings']["max_skin_temp"]])
                                sleep(0.01)
                            elif int(params['settings']["max_skin_temp"]) != int(params['stats']["max_skin_temp"]):
                                sleep(0.1)
                                self.conn.send(["set", "max_skin_temp", params['settings']["max_skin_temp"]])
                                sleep(0.01)

                    i += 1
                    sleep(0.02)
            except :
                sleep(0.02)


# app = MyApp(application_id="com.example.GtkApplication")
# app.run()
app = CoreHandler()
app.run()

logg('-----FrontEnd Stopped------',1)
