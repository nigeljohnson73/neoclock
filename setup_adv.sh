#!/bin/sh

# Get the board up to date
sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y

# Enable the SPI interface
sudo raspi-config nonint do_spi 0

# Install the core packages we need
sudo apt install -y python3-dev python3-pip python3-setuptools python3-wheel libopenblas-dev git vim python3-dbus bluez-tools libopenblas-dev libopenjp2-7 fonts-dejavu

# Bookwoom screwed rpi.gpio edge detection, so put in a new version that is a drop in replacement
# But probably doesn't do edge detection - go figure
sudo apt remove -y python3-rpi.gpio && sudo apt autoremove -y
sudo apt install -y python3-lgpio

# With all the above packages (Some installed to bypass stuff that PIP stuffs up) create a virtual 
# python environment based on core packages we have already
python -m venv --system-site-packages ~/.env
. ~/.env/bin/activate

# Now install all the bits that PIP doesn't screw
pip install bluedot numpy pillow spidev st7789 rpi-lgpio rpi_ws281x adafruit-circuitpython-neopixel
pip install --force-reinstall adafruit-blinka

# Go get all the software
git clone https://github.com/nigeljohnson73/neoclock.git

# Install the audio handler in case we have the Pirate Hat
sudo sed -i "s/^dtparam=audio=on/dtparam=audio=off/g" /boot/firmware/config.txt
sudo bash -c 'cat >> /boot/firmware/config.txt' <<EOF
dtoverlay=hifiberry-dac
gpio=25=op,dh
EOF

# Start up a Bluetooth agent that lets PINs work properly and then our stuff
sudo sed -i "s/^exit 0//g" /etc/rc.local
sudo bash -c 'cat >> /etc/rc.local' <<EOF
sudo bt-agent --capability=DisplayOnly -p /home/pi/neoclock/btpins &
/home/pi/neoclock/clock_adv.sh >/tmp/clock.log 2>&1 &
exit 0
EOF