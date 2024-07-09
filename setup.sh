#/bin/sh

sudo apt update -y
sudo apt full-upgrade -y
sudo apt autoremove -y
sudo apt install -y python3-dev python3-pip python3-setuptools python3-wheel git

python -m venv ~/.env

. ~/.env/bin/activate

pip install rpi_ws281x adafruit-circuitpython-neopixel
python3 -m pip install --force-reinstall adafruit-blinka

git clone https://github.com/nigeljohnson73/neoclock.git

sudo cat /etc/rc.local | grep -v 'exit 0' | grep -v 'clock.sh'
sudo rm /etc/rc.local
sudo mv /etc/rc.local.tmp /etc/rc.local
sudo bash -c 'cat >> /etc/rc.local' <<EOF
# su -l pi -c /hone/pi/neoclock/clock.sh >/tmp/clock.log 2>&1 &
/home/pi/neoclock/clock.sh >/tmp/clock.log 2>&1 &
exit 0
EOF
sudo chmod 755 /etc/rc.local

# Want syntax highlighting? VIM is the answer
#sudo apt install -y vim
#sudo find /etc/vim/vimrc -exec sed -i 's/^"syntax on/syntax on/g' '{}' \;

######################################
# Stuff here is patched together for the pirate audio hat since the documetation is crap
#sudo apt remove python3-rpi.gpio
#sudo apt install -y python3-dev python3-pip python3-setuptools python3-lgpio python3-wheel git libopenblas-dev
#python -m venv --system-site-packages ~/.env
#pip install numpy pillow spidev st7789
#sudo raspi-config nonint do_spi 0
# Do some DT overlay stuff: https://shop.pimoroni.com/products/pirate-audio-mini-speaker?variant=31189753692243
# sudo reboot
#git clone https://github.com/pimoroni/pirate-audio
