#!/bin/sh

#### Basic config for python env
sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y
sudo apt install -y python3-dev python3-pip python3-setuptools python3-wheel git 
python -m venv --system-site-packages ~/.env
. ~/.env/bin/activate



#### VIM
sudo apt install -y vim
sudo find /etc/vim/vimrc -exec sed -i 's/^"syntax on/syntax on/g' '{}' \;



#### BLUETOOTH
sudo apt install -y python3-dbus 
python -m venv --system-site-packages ~/.env
pip install bluedot



#### PIRATE
sudo sed -i "s/^dtparam=audio=on/#dtparam=audio=on/g" /boot/firmware/config.txt
sudo bash -c 'cat >> /boot/firmware/config.txt' <<EOF
dtoverlay=hifiberry-dac
gpio=25=op,dh
EOF
sudo apt remove -y python3-rpi.gpio && sudo apt autoremove -y
sudo apt install -y python3-lgpio libopenblas-dev libopenjp2-7
python -m venv --system-site-packages ~/.env
pip install numpy pillow spidev st7789 rpi-lgpio
git clone https://github.com/pimoroni/pirate-audio
python pirate-audio/examples/rainbow.py
python pirate-audio/examples/buttons.py
speaker-test -c2 -twav -l2



#### NEOCLOCK
pip install rpi_ws281x adafruit-circuitpython-neopixel
pip install --force-reinstall adafruit-blinka
git clone https://github.com/nigeljohnson73/neoclock.git
sudo sed -i "s/^exit 0//g" /etc/rc.local
sudo bash -c 'cat >> /etc/rc.local' <<EOF
/home/pi/neoclock/clock.sh >/tmp/clock.log 2>&1 &
exit 0
EOF
