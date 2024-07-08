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


