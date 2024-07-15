import socket
import subprocess
import os
from bluedot.btcomm import BluetoothServer, BluetoothAdapter
import json
import board
import digitalio
import time
import datetime
import neopixel
from _app.NjButton import NjButton
from _app.PirateDisplay import PirateDisplay
from _app.EinkDisplay import EinkDisplay
from _app.JoyDisplay import JoyDisplay
from _app.WeatherApi import WeatherApi

config_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
print(f"Config: '{config_fn}'")

#################
## Neopixel gear
num_pixels = 60 # Can run on 24 neopixel rings
bri = 255  # Max brightness
toff = -26 # This is one pixel past 5 oclock (to allow for soldering)
pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)

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



##########################
# Setup WIFI connection
def writeWpa(ssid, psk, country="GB", exec=False):
    # Ongoing from https://github.com/raspberrypi/bookworm-feedback/issues/72#issuecomment-1874654829
    data='echo -e "[connection]\nid=wifi1\nuuid=ac4a8bf2-afcd-4bd4-bdb4-456d5a92c520\ntype=wifi\n[wifi]\nmode=infrastructure\nssid={ssid}\nhidden=false\n[ipv4]\nmethod=auto\n[ipv6]\naddr-gen-mode=default\nmethod=auto\n[proxy]\n[wifi-security]\nkey-mgmt=wpa-psk\npsk={psk}">wifi1.nmconnection ; mv wifi1.nmconnection /etc/NetworkManager/system-connections/ ; chmod 0600 /etc/NetworkManager/system-connections/*.nmconnection ; raspi-config nonint do_wifi_country "{country}"'
    data = data.replace("{ssid}", ssid).replace("{psk}", psk).replace("{country}", country)
    os.system(data)

def buttonPressed(label):
    print(f"{label} pressed")
    pass

def buttonReleased(label):
    print(f"{label} released")
    pass

bt_adapter = None
bt_server = None

package="None"
weather_api_key=""
weather_api_location =""
weather_api = None

buttons = []
display = None

def setPixel(n, mult, arr):
    for i in arr:
        #Scale pixels to expected 60
        sp = int(((toff + n + i[0]) % 60) * (num_pixels / 60))
        lb = round(i[1])
        pixels[sp]=(
            max(0, min(255, pixels[sp][0] + lb*mult[0])),
            max(0, min(255, pixels[sp][1] + lb*mult[1])),
            max(0, min(255, pixels[sp][2] + lb*mult[2])),
        )

def writeConfig():
    global config_fn, package, weather_api_key, weather_api_location
    data = {
            "package":package,
            "weather_api_key":weather_api_key,
            "weather_api_location":weather_api_location,
           }
    with open(config_fn, 'w') as f:
     json.dump(data, f, sort_keys = True, indent = 4, ensure_ascii = True)

    pass

def bt_handleData(data):
    global bt_server
    global weather_api, weather_api_key, weather_api_location

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
        ip=getIpAddress()
        bt_server.send(f"{ip}\n")
    elif bits[0] == "wapi_l":
        bt_server.send("OK\n")
        weather_api_location = bits[1]
        if weather_api:
            weather_api.stop()
        writeConfig()
        weather_api = WeatherApi(weather_api_key, weather_api_location)
    elif bits[0] == "wapi_k":
        bt_server.send("OK\n")
        weather_api_key = bits[1]
        if weather_api:
            weather_api.stop()
        writeConfig()
        weather_api = WeatherApi(weather_api_key, weather_api_location)
    else:
        bt_server.send(f"NO\n")


def bt_handleConnect():
    global bt_adapter
    print(f"bluetooth connect")
    devices = bt_adapter.paired_devices
    for d in devices:
        print(f"    connect: '{d}'")
    bt_server.send("wapi_k::KEY - Weather API key\n")
    bt_server.send("wapi_l::LOC - Weather API location\n")
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

def setup():
    global config_fn
    global display, buttons, package, bt_adapter, bt_server
    global weather_api, weather_api_key, weather_api_location

    try:
        with open(config_fn, 'r') as f:
            data = json.load(f)
            package = data["package"]
            weather_api_key = data["weather_api_key"]
            weather_api_location = data["weather_api_location"]
    except:
        print("No config loaded")

    if package == "InkyR":
        display = EinkDisplay(multicolor=True)
    elif package == "Inky":
        display = EinkDisplay()
    elif package == "Pirate":
        display = PirateDisplay()
        buttons = [ NjButton(board.D5, func_press=buttonPressed, func_release=buttonReleased, label="A"),
                    NjButton(board.D6, func_press=buttonPressed, label="B"),
                    NjButton(board.D16, func_press=buttonPressed, label="X"),
                    NjButton(board.D24, func_press=buttonPressed, label="Y"),
                ]
    elif package == "Joy":
        display = JoyDisplay()
        buttons = [ NjButton(board.D21,func_press=buttonPressed, label="KEY1"),
                    NjButton(board.D20,func_press=buttonPressed, label="KEY2"),
                    NjButton(board.D16,func_press=buttonPressed, label="KEY3"),
                    NjButton(board.D6,func_press=buttonPressed,  label="UP"),
                    NjButton(board.D19,func_press=buttonPressed, label="DOWN"),
                    NjButton(board.D5,func_press=buttonPressed,  label="LEFT"),
                    NjButton(board.D26,func_press=buttonPressed, label="RIGHT"),
                    NjButton(board.D13,func_press=buttonPressed, label="CENTER"),
                ]

    print("Enabling Bluetooth pairing")
    bt_adapter = BluetoothAdapter()
    bt_adapter.allow_pairing(timeout=None)
    print("Creating Bluetooth server")
    # BluetoothServer(data_received_callback, auto_start=True, device='hci0', port=1, encoding='utf-8', power_up_device=False, when_client_connects=None, when_client_disconnects=None)
    bt_server = BluetoothServer(
            power_up_device=True, 
            when_client_connects=bt_handleConnect, 
            when_client_disconnects=bt_handleDisconnect,
            data_received_callback=bt_handleData, 
            )
    print("Creating WeatherApi service")
    weather_api = WeatherApi(weather_api_key, weather_api_location)

def buttonLoop():
    for b in buttons:
        b.loop()

def loop():
    global display
    t = datetime.datetime.now().time()
    s = t.second
    m = t.minute
    h = int(((t.hour%12)+m/60+s/3600) * 5) # Allow for sweep within the hour

    pixels.fill((0,0,0))
    setPixel(h, (1,0,0), [[-1,bri/12], [0,bri], [1, bri/12]])
    setPixel(m, (0,1,0), [[0,bri]])
    setPixel(s, (0,0,1), [[-2,bri/23], [-1, bri/10], [0, bri/5]])
    pixels.show()

    buttonLoop()
    if display:
        display.loop();

last_s = 999
setup();
try:
    while True:
        loop()

        t = datetime.datetime.now().time()
        if last_s != t.second:
            last_s = t.second
            if display:
                print(f"time: {t.hour:02d}:{t.minute:02d}:{t.second:02d}, btcon: {display.btConnected()}")
            else:
                print(f"time: {t.hour:02d}:{t.minute:02d}:{t.second:02d}")
        #time.sleep(0.01)

except KeyboardInterrupt:
    print("Closing down")
    if display:
        display.__del__()
    if weather_api:
        weather_api.__del__()
