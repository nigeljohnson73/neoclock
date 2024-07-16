import socket
import subprocess
import os
import json
import datetime
import neopixel
import board
from bluedot.btcomm import BluetoothServer, BluetoothAdapter
from _app.NjButton import NjButton
from _app.PirateDisplay import PirateDisplay
from _app.EinkDisplay import EinkDisplay
from _app.JoypadDisplay import JoypadDisplay
from _app.WeatherApi import WeatherApi

config_fn = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.json')
print(f"Config: '{config_fn}'")

###########################################################################################
# Neopixel gear
num_pixels = 60  # Can run on 24 neopixel rings
bri = 255  # Max brightness
toff = -26  # This is one pixel past 5 oclock (to allow for soldering)
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)


###########################################################################################
# Stuff we should probably put somewhere else
bt_adapter = None
bt_server = None

package = "None"
weather_api_key = ""
weather_api_location = ""
weather_api = None
weather_api_choice = -1

buttons = []
display = None


###########################################################################################
# Works out the correct IP address on the local network
def getIpAddress():
    """
    Idea from https://stackoverflow.com/a/28950776/3057377
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    # Doesn’t even have to be reachable.
    s.connect_ex(("10.254.254.254", 1))
    ip = s.getsockname()[0]
    ip = "127.0.0.1" if ip == "0.0.0.0" else ip
    s.close()
    return ip


###########################################################################################
# Setup WIFI connection file (hopefully - currently untested)
def writeWpa(ssid, psk, country="GB", exec=False):
    # Ongoing from https://github.com/raspberrypi/bookworm-feedback/issues/72#issuecomment-1874654829
    data = 'echo -e "[connection]\nid=wifi1\nuuid=ac4a8bf2-afcd-4bd4-bdb4-456d5a92c520\ntype=wifi\n[wifi]\nmode=infrastructure\nssid={ssid}\nhidden=false\n[ipv4]\nmethod=auto\n[ipv6]\naddr-gen-mode=default\nmethod=auto\n[proxy]\n[wifi-security]\nkey-mgmt=wpa-psk\npsk={psk}">wifi1.nmconnection ; mv wifi1.nmconnection /etc/NetworkManager/system-connections/ ; chmod 0600 /etc/NetworkManager/system-connections/*.nmconnection ; raspi-config nonint do_wifi_country "{country}"'
    data = data.replace("{ssid}", ssid).replace(
        "{psk}", psk).replace("{country}", country)
    os.system(data)


###########################################################################################
# Set a NEOPIXEL to a value, with relativity in the arr(ay)
def setPixel(n, mult, arr):
    for i in arr:
        # Scale pixels to expected 60
        sp = int(((toff + n + i[0]) % 60) * (num_pixels / 60))
        lb = round(i[1])
        pixels[sp] = (
            max(0, min(255, pixels[sp][0] + lb*mult[0])),
            max(0, min(255, pixels[sp][1] + lb*mult[1])),
            max(0, min(255, pixels[sp][2] + lb*mult[2])),
        )


###########################################################################################
# Write out the current config
def writeConfig():
    global config_fn, package, weather_api_key, weather_api_location
    data = {
        "package": package,
        "weather_api_key": weather_api_key,
        "weather_api_location": weather_api_location,
    }
    with open(config_fn, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=True)

    pass


###########################################################################################
# Bleutooth connection handling malary: TODO: move this soemwhere else
def bt_handleData(data):
    global bt_server
    global weather_api, weather_api_key, weather_api_location, weather_api_choice

    bits = data.strip().split("::")
    print(f"data: '{bits}'")
    if bits[0] == "pong":
        bt_server.send("pong\n")
    elif bits[0] == "time":
        bt_server.send("OK\n")
        subprocess.call(['sudo', 'date', '-s', bits[1]], shell=False)
    elif bits[0] == "wifi":
        bt_server.send("OK-REBOOT\n")
        writeWpa(ssid=bits[2], psk=bits[3], country=bits[1], exec=True)
    elif bits[0] == "ip":
        ip = getIpAddress()
        bt_server.send(f"{ip}\n")
    elif bits[0] == "wapi-l":
        bt_server.send("OK\n")
        weather_api_location = bits[1]
        if weather_api:
            weather_api.stop()
        weather_api = None
        writeConfig()
        weather_api_choice = -1;
        pageOnce("config")
    elif bits[0] == "wapi-k":
        bt_server.send("OK\n")
        weather_api_key = bits[1]
        if weather_api:
            weather_api.stop()
        weather_api = None
        writeConfig()
        weather_api_choice = -1;
        pageOnce("config")
    else:
        bt_server.send(f"NO\n")


def bt_handleConnect():
    global bt_adapter
    print(f"bluetooth connect")
    devices = bt_adapter.paired_devices
    for d in devices:
        print(f"    connect: '{d}'")
    bt_server.send("wapi-k::KEY - Weather API key\n")
    bt_server.send("wapi-l::LOC - Weather API location\n")
    bt_server.send("ip - shows the network IP\n")
    bt_server.send("time::YYYY-MM-DD HH:II:SS - Set time\n")
    bt_server.send("wifi::CC::SSID::PSK - Set WiFi config\n")
    if display:
        display.btConnected(True)


def bt_handleDisconnect():
    global bt_adapter, bt_server
    print(f"bluetooth disconnect")
    if display:
        display.btConnected(False)


###########################################################################################
# handle button pressing for now. TODO: move this somewhere else
def nextLocation(label):
    global weather_api, weather_api_key, weather_api_location, weather_api_choice
    print(f"{label} pressed")

    weather_api = None
    choices = []
    bits = weather_api_location.strip().split(",")
    for i in bits:
        if len(i.strip()):
            print (f"    Adding location choice '{i}'")
            choices.append(i)
    if len(choices):
        weather_api_choice = weather_api_choice + 1
        if weather_api_choice >= len(choices):
                weather_api_choice = 0
        print (f"    Choice '{choices[weather_api_choice]}'")
        weather_api = WeatherApi(weather_api_key, choices[weather_api_choice])


def buttonPressed(label):
    print(f"{label} pressed")


def buttonReleased(label):
    print(f"{label} released")


###########################################################################################
# Set up the application
def setup():
    global config_fn
    global display, buttons, package, bt_adapter, bt_server
    global weather_api, weather_api_key, weather_api_location

    # try loading the config
    try:
        with open(config_fn, 'r') as f:
            data = json.load(f)
            package = data["package"]
            weather_api_key = data["weather_api_key"]
            weather_api_location = data["weather_api_location"]
    except:
        print("No config loaded")

    # If we have a known package, set that up
    if package == "InkyR":
        display = EinkDisplay(multicolor=True)
    elif package == "Inky":
        display = EinkDisplay()
    elif package == "Pirate":
        display = PirateDisplay()
        buttons = [NjButton(board.D5, func_press=nextLocation, label="A"),
                   NjButton(board.D6, func_press=buttonPressed, label="B"),
                   NjButton(board.D16, func_press=buttonPressed, label="X"),
                   NjButton(board.D24, func_press=buttonPressed, label="Y"),
                   ]
    elif package == "Joypad":
        display = JoypadDisplay()
        buttons = [NjButton(board.D21, func_press=buttonPressed, label="KEY1"),
                   NjButton(board.D20, func_press=buttonPressed, label="KEY2"),
                   NjButton(board.D16, func_press=nextLocation, label="KEY3"),
                   NjButton(board.D6, func_press=buttonPressed,  label="UP"),
                   NjButton(board.D19, func_press=buttonPressed, label="DN"),
                   NjButton(board.D5, func_press=buttonPressed,  label="LT"),
                   NjButton(board.D26, func_press=buttonPressed, label="RT"),
                   NjButton(board.D13, func_press=buttonPressed, label="CT"),
                   ]

    print("Enabling Bluetooth agent")
    bt_adapter = BluetoothAdapter()
    bt_adapter.allow_pairing(timeout=None)

    print("Creating Bluetooth server")
    bt_server = BluetoothServer(
        power_up_device=True,
        when_client_connects=bt_handleConnect,
        when_client_disconnects=bt_handleDisconnect,
        data_received_callback=bt_handleData,
    )

    nextLocation("setup")
    #print("Creating WeatherApi service")
    #weather_api = WeatherApi(weather_api_key, weather_api_location)


def buttonLoop():
    for b in buttons:
        b.loop()


def loop():
    global display
    t = datetime.datetime.now().time()
    s = t.second
    m = t.minute
    h = int(((t.hour % 12)+m/60+s/3600) * 5)  # Allow for sweep within the hour

    pixels.fill((0, 0, 0))
    setPixel(h, (1, 0, 0), [[-1, bri/12], [0, bri], [1, bri/12]])
    setPixel(m, (0, 1, 0), [[0, bri]])
    setPixel(s, (0, 0, 1), [[-2, bri/23], [-1, bri/10], [0, bri/5]])
    pixels.show()

    buttonLoop()
    if display:
        display.loop()


###########################################################################################
# And the main attraction
last_s = 999
setup()
try:
    while True:
        loop()

        t = datetime.datetime.now().time()
        if last_s != t.second:
            last_s = t.second
            print(f"time: {t.hour:02d}:{t.minute:02d}:{t.second:02d}")


except KeyboardInterrupt:
    print("Exiting nicely")
    display = None
    weather_api = None
