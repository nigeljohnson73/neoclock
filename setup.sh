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

echo "## Install rc.local hooks" | tee -a $logfile
sudo cat /etc/rc.local | grep -v 'exit 0' | grep -v '/webroot/' | sudo tee /etc/rc.local.tmp >/dev/null
sudo rm /etc/rc.local
sudo mv /etc/rc.local.tmp /etc/rc.local
sudo bash -c 'cat >> /etc/rc.local' <<EOF
su -l pi -c /hone/pi/neoclock/clock.sh >/tmp/clock.log 2>&1 &
exit 0
EOF
sudo chmod 755 /etc/rc.local
