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

workingDir = "/home/" + user + "/.var/app/com.nyaker.RyzenTuningUtility/gui"

local_key = randbytes(256)  # this is the key that will be used to authenticate the connection between gui and handler
local_address = ('localhost', 6006)

connAddress = ('localhost', 6000)  # privilidged daemon

unsecure_address = ('localhost', 6001)
unsecure_key = bytes('open/close', 'ascii')

params = {"settings": {"temp_enabled": False, "max_temp": 80, "skin_temp_enabled": False, "max_skin_temp": 45,
                       "avg_power_enabled": False, "max_avg_power": 15, "peak_power_enabled": False,
                       "max_peak_power": 20,
                       "mode": "manual"}, "updated": False,
          "limits": {"temp": 90, "avg_power": 500, "peak_power": 1000, "skin_temp": 90}}


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):

        self.conn = None
        self.pkPSlider = None
        self.DisablePkPower = None
        self.pk01 = None
        self.pkbar = None
        self.pkplabel = None
        self.pkframe = None
        self.pkedit = None
        self.pkbox = None

        self.avgPSlider = None
        self.DisableAvgPower = None
        self.avg01 = None
        self.avgbar = None
        self.avgplabel = None
        self.avgframe = None
        self.avgedit = None
        self.avgbox = None

        self.TempSlider = None
        self.disableTemp = None
        self.temp01 = None
        self.tempbar = None
        self.templabel = None
        self.tempframe = None
        self.tempadj = None
        self.tempbox = None

        self.stempSlider = None
        self.disablestemp = None
        self.stemp01 = None
        self.stempbar = None
        self.stemplabel = None
        self.stempframe = None
        self.stempadj = None
        self.stembox = None

        self.hamburger = None
        self.Phamburger = None
        self.popover = None
        self.menu = None
        self.presets = None

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

        self.initSTemp()

        self.initavgPower()

        self.initpkPower()

        self.initPresets()

        self.set_child(self.MainBox)
        self.header.pack_start(self.ExitButton)
        self.MainBox.append(self.SlidersBox)

        connThread = Thread(target=self.connF)
        connThread.start()
        GLib.timeout_add(30, self.refresh)

    def closewin(self, arg):
        self.running = False

    def connF(self):
        self.conn = Client(local_address, authkey=local_key)
        while self.running:
            sleep(0.1)
        self.conn.close()

    def refresh(self):
        global params
        if params["updated"]:

            if params['settings']['temp_enabled']:  # refreshing max_temp bar
                self.disableTemp.set_label('Disable')
                self.temp01.set_value(1)

            else:
                self.disableTemp.set_label('Enable')
                self.temp01.set_value(0)

            if self.tempbar.get_allocated_width() != 0 and self.tempbar.get_allocated_height() != 0:
                self.tempbar.set_max_value(params['stats']['max_temp'])
                self.tempbar.set_value(params['stats']['temp'])

            # sleep(0.01)

            if params['settings']['max_temp'] != int(self.TempSlider.get_value()):
                self.TempSlider.set_value(params['settings']['max_temp'])

            if params['settings']["avg_power_enabled"]:
                self.DisableAvgPower.set_label('Disable')
                self.avg01.set_value(1)
            else:
                self.DisableAvgPower.set_label('Enable')
                self.avg01.set_value(0)

            if self.pkbar.get_allocated_width() != 0 and self.pkbar.get_allocated_height() != 0:
                self.avgbar.set_max_value(params['stats']['max_avg_power'])
                self.avgbar.set_value(params['stats']['avg_power'])

            # sleep(0.01)

            if params['settings']['max_avg_power'] != int(self.avgPSlider.get_value()):
                self.avgPSlider.set_value(params['settings']['max_avg_power'])

            if params['settings']["peak_power_enabled"]:
                self.DisablePkPower.set_label('Disable')
                self.pk01.set_value(1)
            else:
                self.DisablePkPower.set_label('Enable')
                self.pk01.set_value(0)

            if self.pkbar.get_allocated_width() != 0 and self.pkbar.get_allocated_height() != 0:
                self.pkbar.set_max_value(params['stats']['max_peak_power'])
                self.pkbar.set_value(params['stats']['peak_power'])

            # sleep(0.01)

            if params['settings']['max_peak_power'] != int(self.pkPSlider.get_value()):
                self.pkPSlider.set_value(params['settings']['max_peak_power'])

            if params['settings']['skin_temp_enabled']:  # refreshing max_temp bar
                self.disablestemp.set_label('Disable')
                self.stemp01.set_value(1)

            else:
                self.disablestemp.set_label('Enable')
                self.stemp01.set_value(0)

            if self.stempbar.get_allocated_width() != 0 and self.stempbar.get_allocated_height() != 0:
                self.stempbar.set_max_value(params['stats']['max_skin_temp'])
                self.stempbar.set_value(params['stats']['skin_temp'])

            # sleep(0.01)

            if params['settings']['max_skin_temp'] != int(self.sTempSlider.get_value()):
                self.sTempSlider.set_value(params['settings']['max_skin_temp'])

            params['updated'] = False
        else:
            pass
        if self.running:
            return True
        else:
            return False

    def readcfg(self):
        with open(workingDir + '/presets.json') as json_file:
            self.presets = json.load(json_file)

    def writecfg(self):
        with open(workingDir + '/presets.json', 'w') as fp:
            json.dump(self.presets, fp)

    def reloadPmenu(self):
        if self.Pmenu:
            del self.Pmenu
        if self.actions:
            del self.actions
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

    def initPresets(self):
        try:
            self.readcfg()
        except:
            self.presets = {}
            self.writecfg()

        # Here the action is being added to the window, but you could add it to the
        # application or an "ActionGroup"

        # Create a new menu, containing that action

        NewPreset = Gio.SimpleAction.new("new_preset", None)
        NewPreset.connect("activate", self.new_preset)
        self.add_action(NewPreset)  # Here the action is being added to the window, but you could add it to the
        # application or an "ActionGroup"

        # Create a new menu, containing that action
        self.menu = Gio.Menu.new()
        self.menu.append("new preset", "win.new_preset")
        # action to the application

        # Create a popover
        self.popover = Gtk.PopoverMenu()  # Create a new popover menu
        self.popover.set_menu_model(self.menu)

        # Create a menu button
        self.Phamburger = Gtk.MenuButton()  # Create a new
        self.Phamburger.set_icon_name("open-menu-symbolic")
        self.reloadPmenu()
        self.menu.append_submenu("Presets", self.Pmenu)

        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")  # Give it a nice icon

        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)

    def select_pname(self):
        entry = Gtk.Entry()
        entry.connect("activate", self.on_entry_activated)
        self.MainBox.append(entry)

    def on_entry_activated(self, entry):
        newkey = entry.get_text()
        if ' ' in newkey:
            newkey = newkey.replace(' ', '_')
        self.MainBox.remove(entry)
        if newkey != self.prename[0]:
            self.presets[newkey] = self.presets[self.prename]
            del self.presets[self.prename]
            self.MainBox.remove(entry)
            self.writecfg()
            self.reloadPmenu()

    def new_preset(self, action, param):
        self.prename = str(randint(0, 99999))
        self.presets[self.prename] = copy.deepcopy(params['settings'])
        self.select_pname()
        pass

    def presetchanged(self, action, param, preset_name):
        global params
        if preset_name[1] == "Enable":
            if preset_name[0] in self.presets:
                params['settings'] = copy.deepcopy(self.presets[preset_name[0]])
        elif preset_name[1] == "Save":
            if preset_name[0] in self.presets:
                if params['settings']["mode"] == "manual":
                    self.presets[preset_name[0]] = copy.deepcopy(params['settings'])
                    self.writecfg()
                    self.reloadPmenu()
        elif preset_name[1] == "Rename":
            if preset_name[0] in self.presets:
                self.prename = preset_name[0]
                self.select_pname()
        elif preset_name[1] == "Delete":
            if preset_name[0] in self.presets:
                del self.presets[preset_name[0]]
                self.writecfg()
                self.reloadPmenu()

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
        self.tempbar.set_max_value(100)

        self.temp01 = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.temp01.set_min_value(0)
        self.temp01.set_max_value(1)

        # self.templabel = Gtk.Label(label="Max Temperature : "+str(params['settings']['max_temp'])+"C | enabled : " +str(params['settings']['temp_enabled']))
        # self.templabel.set_margin_top(5)

        self.disableTemp = Gtk.Button(label="Disable")
        self.disableTemp.connect('clicked', self.tempReset_clicked)

        self.TempSlider = Gtk.Scale()
        self.TempSlider.set_digits(0)  # Number of decimal places to use
        self.TempSlider.set_range(55, 97)
        self.TempSlider.set_draw_value(True)  # Show a label with current value
        self.TempSlider.set_value(params['settings']['max_temp'])  # Sets the current value/position
        self.TempSlider.connect('value-changed', self.tempSlider_changed)
        self.TempSlider.set_hexpand(True)  #

        self.tempadj.append(self.disableTemp)
        self.tempadj.append(self.TempSlider)
        self.tempbox.append(self.tempbar)
        self.tempbox.append(self.templabel)
        self.tempbox.append(self.tempadj)
        self.tempbox.append(self.temp01)
        self.SlidersBox.append(self.tempframe)

    def initSTemp(self):
        global params
        self.stempbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.stempadj = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.stempframe = Gtk.Frame()
        self.stempframe.set_margin_top(15)
        self.stempframe.set_margin_end(10)
        self.stempframe.set_child(self.stempbox)
        self.stemplabel = Gtk.Label()
        self.stemplabel.set_margin_top(10)
        self.stemplabel.set_label("Maximum Skin Temperature")

        self.stempbar = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.stempbar.set_min_value(0)
        self.stempbar.set_max_value(100)

        self.stemp01 = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.stemp01.set_min_value(0)
        self.stemp01.set_max_value(1)

        # self.templabel = Gtk.Label(label="Max Temperature : "+str(params['settings']['max_temp'])+"C | enabled : " +str(params['settings']['temp_enabled']))
        # self.templabel.set_margin_top(5)

        self.disablestemp = Gtk.Button(label="Disable")
        self.disablestemp.connect('clicked', self.stempReset_clicked)

        self.sTempSlider = Gtk.Scale()
        self.sTempSlider.set_digits(0)  # Number of decimal places to use
        self.sTempSlider.set_range(40, params['limits']['skin_temp'])
        self.sTempSlider.set_draw_value(True)  # Show a label with current value
        self.sTempSlider.set_value(params['settings']['max_skin_temp'])  # Sets the current value/position
        self.sTempSlider.connect('value-changed', self.stempSlider_changed)
        self.sTempSlider.set_hexpand(True)  #

        self.stempadj.append(self.disablestemp)
        self.stempadj.append(self.sTempSlider)
        self.stempbox.append(self.stempbar)
        self.stempbox.append(self.stemplabel)
        self.stempbox.append(self.stempadj)
        self.stempbox.append(self.stemp01)
        self.SlidersBox.append(self.stempframe)

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
        self.avgbar.set_max_value(params['settings']['max_avg_power'])

        self.avg01 = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.avg01.set_min_value(0)
        self.avg01.set_max_value(1)

        self.DisableAvgPower = Gtk.Button(label="Disable")
        self.DisableAvgPower.connect('clicked', self.avgPReset_clicked)

        self.avgPSlider = Gtk.Scale()
        self.avgPSlider.set_digits(0)  # Number of decimal places to use
        self.avgPSlider.set_range(7, 60)
        self.avgPSlider.set_draw_value(True)  # Show a label with current value
        self.avgPSlider.set_value(params['settings']['max_avg_power'])  # Sets the current value/position
        self.avgPSlider.connect('value-changed', self.avgPslider_changed)
        self.avgPSlider.set_hexpand(True)  #

        self.avgbox.append(self.avgbar)
        self.avgbox.append(self.avgplabel)
        self.avgedit.append(self.DisableAvgPower)
        self.avgedit.append(self.avgPSlider)
        self.avgbox.append(self.avgedit)
        self.avgbox.append(self.avg01)
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
        self.pkbar.set_max_value(params['settings']['max_peak_power'])

        self.pk01 = Gtk.LevelBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.pk01.set_min_value(0)
        self.pk01.set_max_value(1)

        self.DisablePkPower = Gtk.Button(label="Disable")
        self.DisablePkPower.connect('clicked', self.pkPReset_clicked)

        self.pkPSlider = Gtk.Scale()
        self.pkPSlider.set_digits(0)  # Number of decimal places to use
        self.pkPSlider.set_range(9, 70)
        self.pkPSlider.set_draw_value(True)  # Show a label with current value
        self.pkPSlider.set_value(params['settings']['max_peak_power'])  # Sets the current value/position
        self.pkPSlider.connect('value-changed', self.pkPslider_changed)
        self.pkPSlider.set_hexpand(True)  #

        self.pkbox.append(self.pkbar)
        self.pkbox.append(self.pkplabel)
        self.pkedit.append(self.DisablePkPower)
        self.pkedit.append(self.pkPSlider)
        self.pkbox.append(self.pkedit)
        self.pkbox.append(self.pk01)
        self.SlidersBox.append(self.pkframe)

    def tempReset_clicked(self, button):
        if params['settings']['temp_enabled']:
            self.conn.send(["max_temp", 0])
        else:
            self.conn.send(["max_temp", 1])
        sleep(0.01)

    def stempReset_clicked(self, button):
        if params['settings']['skin_temp_enabled']:
            self.conn.send(["max_skin_temp", 0])
        else:
            self.conn.send(["max_skin_temp", 1])
        sleep(0.01)

    def avgPReset_clicked(self, button):
        if params['settings']["avg_power_enabled"]:
            self.conn.send(["max_avg_power", 0])
        else:
            self.conn.send(["max_avg_power", 1])
        sleep(0.01)

    def pkPReset_clicked(self, button):
        if params['settings']["peak_power_enabled"]:
            self.conn.send(["max_peak_power", 0])
        else:
            self.conn.send(["max_peak_power", 1])
        sleep(0.01)

    def tempSlider_changed(self, slider):
        slidervalue = int(slider.get_value())
        # self.templabel.set_label("Max Temperature : " + str(slidervalue))
        self.conn.send(["max_temp", slidervalue])
        sleep(0.01)
        # self.templabel.set_label("Max Temperature : " + str(params['settings']['max_temp']) + "C | enabled : " + str(params['settings']['temp_enabled']))

    def avgPslider_changed(self, slider):
        slidervalue = int(slider.get_value())
        # self.avgPlabel.set_label("Max Avg Power : " + str(slidervalue))
        self.conn.send(["max_avg_power", slidervalue])
        sleep(0.01)
        # self.avgPlabel.set_label("Max Avg Power : " + str(params['settings']['max_avg_power']) + "W | enabled : " + str(params['settings']['avg_power_enabled']))

    def pkPslider_changed(self, slider):
        slidervalue = int(slider.get_value())
        # self.pkPlabel.set_label("Max Peak Power : " + str(slidervalue))
        self.conn.send(["max_peak_power", slidervalue])
        sleep(0.01)
        # self.pkPlabel.set_label("Max Peak Power : " + str(params['settings']['max_peak_power']) + "W | enabled : " + str(params['settings']['peak_power_enabled']))

    def stempSlider_changed(self, slider):
        slidervalue = int(slider.get_value())
        # self.stemplabel.set_label("Max Skin Temperature : " + str(slidervalue))
        self.conn.send(["max_skin_temp", slidervalue])
        sleep(0.01)
        # self.stemplabel.set_label("Max Skin Temperature : " + str(params['settings']['max_skin_temp']) + "C | enabled : " + str(params['settings']['skin_temp_enabled']))

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
        self.conn = None
        self.guiapp = None
        self.guithread = None
        self.running = True
        self.isgui = False
        global params

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

        sleep(0.1)
        self.initGuiThread()

        self.localServerThread.join()
        self.serverThread.join()
        self.connectionThread.join()

    def server(self):  # connection to the start process (unsecure)
        sleep(0.2)

        listener = Listener(unsecure_address, authkey=unsecure_key)
        while self.running:
            if not self.isgui:
                try:
                    conn = listener.accept()
                    while self.running:
                        while conn.poll():
                            msg = conn.recv()

                            if msg == "EXIT":
                                conn.close()
                                self.conn.close()
                                # self.exit()
                                break
                            elif msg == "OPEN":
                                self.initGuiThread()
                                break
                        if not self.running:
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
                print(e)

    def connection(self):  # connection to the daemon (secure)
        global params
        coretemp_cnt = 0  # if any of theses values goes above 3, we consider that the cpu cannot go higher
        avgpower_cnt = 0
        peakpower_cnt = 0
        skin_temp_cnt = 0

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
                        if params['settings']["temp_enabled"] == True:
                            if int(params['settings']["max_temp"]) != int(oldparams["max_temp"]):
                                #print("user changed temp")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_temp", params['settings']["max_temp"]])
                                sleep(0.01)
                            elif int(params['settings']["max_temp"]) != int(params['stats']["max_temp"]):
                                #print("target temp limit not equal to current limit")
                                coretemp_cnt += 1
                                sleep(0.5)
                                self.conn.send(["set", "max_temp", params['settings']["max_temp"]])
                                sleep(0.01)
                            # if self.conn.recv() == "EXIT":
                            #    self.running = False
                            #    exit(0)
                        if params['settings']["avg_power_enabled"] == True:
                            if int(params['settings']["max_avg_power"]) != int(oldparams["max_avg_power"]):
                                #print("user changed avg power")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_avg_power", params['settings']["max_avg_power"]])
                                sleep(0.01)
                            elif int(params['settings']["max_avg_power"]) != int(params['stats']["max_avg_power"]):
                                #print("target avg power limit not equal to current limit")
                                avgpower_cnt += 1
                                sleep(0.5)
                                self.conn.send(["set", "max_avg_power", params['settings']["max_avg_power"] * 1000])
                                sleep(0.01)
                        if params['settings']["peak_power_enabled"] == True:
                            if int(params['settings']["max_peak_power"]) != int(oldparams["max_peak_power"]):
                                #print("user changed peak power")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_peak_power", params['settings']["max_peak_power"]])
                                sleep(0.01)
                            elif int(params['settings']["max_peak_power"]) != int(params['stats']["max_peak_power"]):
                                #print("target peak power limit not equal to current limit")
                                peakpower_cnt += 1
                                sleep(0.5)
                                self.conn.send(["set", "max_peak_power", params['settings']["max_peak_power"] * 1000])
                                sleep(0.01)
                        if params['settings']["skin_temp_enabled"] == True:
                            if int(params['settings']["max_skin_temp"]) != int(oldparams["max_skin_temp"]):
                                #print("user changed skin temp")
                                oldparams = copy.deepcopy(params['settings'])
                                self.conn.send(["set", "max_skin_temp", params['settings']["max_skin_temp"]])
                                sleep(0.01)
                            elif int(params['settings']["max_skin_temp"]) != int(params['stats']["max_skin_temp"]):
                                #print("target skin temp limit not equal to current limit")
                                #print("target : " + str(params['settings']["max_skin_temp"]) + " current : " + str(
                                #    #params['stats']["max_skin_temp"]))
                                skin_temp_cnt += 1
                                sleep(0.5)
                                self.conn.send(["set", "max_skin_temp", params['settings']["max_skin_temp"]])
                                sleep(0.01)

                    i += 1
                    sleep(0.01)
            except Exception as e:
                print(e)
                sleep(0.1)


# app = MyApp(application_id="com.example.GtkApplication")
# app.run()
app = CoreHandler()
app.run()

print('-----FrontEnd Stopped------')
