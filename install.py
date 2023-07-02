from subprocess import check_output, call
import os
import sys

version = 2
user = check_output(['whoami']).decode('utf-8')[:-1]
WorkingDirectory = os.getcwd()

path = "/home/" + user + "/.var/app/com.nyaker.RyzenTuningUtility"
desktopPath = "/home/" + user + "/.local/share/applications"
corefilelist = [("daemon/ryzenadj/libryzenadj.so", "/daemon/ryzenadj"), ("daemon/ryzenadj/ryzenadj", "/daemon/ryzenadj"), ("daemon/RyzenTuningDaemon.py", "/daemon"),
                ("gui/RyzenTuningUtility.py", "/gui"), ("start.py", "")]
configfileslist = [("daemon/config.py", "/daemon")]
installMode = "None"


def selectrepair():
    global installMode
    print('complete repair (including config files)(DATA LOSS RISK) : c \nbasic repair : b')
    choice = input('>>> ')
    if choice == "c":
        print("complete Repair, Config Data will be lost ! \nAre you sure ? (y/n)")
        if input(">>> ") == "y":
            installMode = "repairC"
        else:
            selectrepair()
    elif choice == "b":
        print("Basic repair, your config data is safe")
        installMode = "repairB"



def install_desktopShortcut():
    call(("cp", "-f", "etc/RyzenTuningController.desktop", desktopPath))
    print("\n======= desktop files copied into " + desktopPath + " =======\n")


def install_icon():
    call(("pkexec", "cp", "-f", WorkingDirectory + "/etc/com.nyaker.RyzenTuningUtility.svg", "/usr/share/icons/hicolor/scalable/apps"))
    print("\n======= Icon copied into " + "/usr/share/icons/hicolor/scalable/apps" + " =======\n")


def install_libs():
    print("\n======= installing libs =======")
    call(("python",'-m','pip', "install", "PyGObject"))
    call(("python",'-m','pip', "install", "PyGObject"))


def install_Core_Files():
    i = 0
    print("\n======= installing core files =======")
    for file in corefilelist:
        if file[1] == '':
            pass
        else:
            call(("mkdir", "-p", path + file[1]))
        call(("cp", "-f", "-r", file[0], path + file[1]))
        i += 1
        print((i / len(corefilelist)) * 100, "%.")
    print("\n======= core files copied into " + path + " =======\n")


def install_Configs(mode):
    if mode == 'force':
        arg = "-f"
    elif mode == 'normal':
        arg = "-n"
    elif mode == 'update':
        print("\n======= updating config==========\n")
        print("========= not implemented =========\n")
    for file in configfileslist:
        if file[1] == '':
            pass
        else:
            call(("mkdir", "-p", path + file[1]))
        call(("cp", "-f", "-r", file[0], path + file[1]))
        print("==== copied " + file[0] + " to " + path + file[1] + "\n")
    print("\n======= config files copied into " + path + " =======\n")


if os.path.exists("/usr/bin/python"):
    print("=============== python bindings are ok, installing ===============\n")
    python = "python"
elif os.path.exists("/usr/bin/python3"):
    print("== using python3 executable (big chance that you are running a debian based system), it should work ==\n")
    python = "python3"
else:
    print("=============== python not found ===============")
    print("Your distro is not currently supported, you can still try to modify the script, please report the problem into the github")
    exit(1)

isdir = call(("mkdir", path))
try:
    arg = sys.argv[1]
    if arg == 'update':
        installMode = 'update'

except:
    if isdir == 0:
        print('\n======= folder created =======\n')
        installMode = "normal"
    elif isdir == 1:
        print('\n======= folder already exist =======\n')
        if os.path.exists(path + "/start.py"):
            print('\n======= detected start.py file, detecting version =======\n')
            currentversion = int(check_output([python, path + "/start.py", "version"]).decode('utf-8'))
            if int(currentversion) == version:
                selectrepair()
            else:
                installMode = "update"
                print('====== update from v' + str(currentversion) + ' to v' + str(version) + ' ======')
        else:
            installMode = "normal"

if installMode == "normal":
    install_Core_Files()
    install_Configs()
    install_icon()
    install_desktopShortcut()
    install_libs()
elif installMode == "update":
    install_Core_Files()
    install_desktopShortcut()
elif installMode == "repairC":
    install_Core_Files()
    install_Configs()
    install_icon()
    install_desktopShortcut()
    install_libs()
elif installMode == "repairB":
    install_Core_Files()
    install_desktopShortcut()
    #install_icon()

print("\n======= done =======")
