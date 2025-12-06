#!/bin/bash
#sed -i '/FILESYSTEMS=/c\FILESYSTEMS="vfat ext2 ext3 ext4 hfsplus ntfs fuseblk vfat"' /etc/usbmount/usbmount.conf

ROOT_UID=0   # Root has $UID 0.

update=$1

if [ "$UID" -eq "$ROOT_UID" ]
then
   echo "OK"
else
    echo "Run with sudo!"
    echo "sudo ./install.sh"
    exit 0
fi

echo "Hurray, you are root! Let's do this.."
cat <<'EOF'
 ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄    ▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄ 
█       █       █  █  █ █       █       █       █   █
█   ▄▄▄▄█   ▄   █   █▄█ █▄▄▄▄   █   ▄   █    ▄  █   █
█  █  ▄▄█  █ █  █       █▄▄▄▄█  █  █ █  █   █▄█ █   █
█  █ █  █  █▄█  █  ▄    █ ▄▄▄▄▄▄█  █▄█  █    ▄▄▄█   █
█  █▄▄█ █       █ █ █   █ █▄▄▄▄▄█       █   █   █   █
█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄█  █▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄█   █▄▄▄█
EOF
sleep 1

if grep -q -F '#gonzopi-rpi-configuration-1.0' /boot/config.txt
then
echo "screen drivers found! remove them in /boot/config.txt"
else
echo "Select screen driver to be installed"
select screen in hyperpixel4 ugeek-hdtft hdmi-screen
do
echo $screen
break
done
fi
echo "setting up system for filmmaking flow..."
echo "if something goes wrong please submit bug to https://github.com/rbckman/gonzopi"
sleep 2
version="$(lsb_release -c -s)"
if [ "$version" = "buster" ]
then
    echo "Debian Buster found"
else
    echo "Debian Stretch found"
fi
echo "Installing all dependencies..."

apt-get update
apt-get upgrade -y
if [ "$version" = "buster" ]
then
    apt-get -y install git python3-pip python-configparser ffmpeg mediainfo gpac omxplayer sox cpufrequtils apache2 libapache2-mod-wsgi-py3 libdbus-glib-1-dev dbus libdbus-1-dev usbmount python3-numpy python3-pil python3-smbus python3-shortuuid wiringpi make gcc cmake pmount python3-ifaddr python3-pygame python3-serial libmediainfo-dev python3-pymediainfo f2fs-tools
else
    apt-get -y install git python3-pip python-configparser libav-tools mediainfo gpac omxplayer sox cpufrequtils apache2 libapache2-mod-wsgi-py3 libdbus-glib-1-dev dbus libdbus-1-dev usbmount python3-numpy python3-pil python3-smbus python3-shortuuid wiringpi make gcc cmake python3-ifaddr python3-pygame python3-serial f2fs-tools
fi
usermod -a -G dialout pi

echo "upgrading pip..."
pip3 install --upgrade pip

echo "installing python-omxplayer-wrapper..."
pip3 install omxplayer-wrapper
echo "installing blessed..."
pip3 install blessed
echo "installing secrets..."
pip3 install secrets
pip3 install numpy
pip3 install RPi.GPIO
echo "installing picamerax with lens shading correction..."
#sudo pip3 --no-cache-dir install https://github.com/chrisruk/picamera/archive/hq-camera-new-framerates.zip --upgrade
pip3 install --upgrade picamerax
echo "installing web.py for the gonzopi webserver..."
pip3 install web.py==0.61

if [ "$screen" = "ugeek-hdtft" ]
then
echo "installing ugeek screen drivers"
echo "Gonzopi configuration seems to be in order in /boot/config.txt"
echo "Adding to /boot/config.txt"
cat <<'EOF' >> /boot/config.txt
#-----GonzoPi configuration starts here-------
#gonzopi-rpi-configuration-ugeek-1.0
#Rpi-hd-tft
dtoverlay=dpi18
overscan_left=0
overscan_right=0
overscan_top=0
overscan_bottom=0
framebuffer_width=800
framebuffer_height=480
enable_dpi_lcd=1
display_default_lcd=1
dpi_group=2
dpi_mode=87
dpi_output_format=0x6f015
hdmi_timings=480 0 16 16 24 800 0 4 2 2 0 0 0 60 0 32000000 6
dtoverlay=pi3-disable-bt-overlay
dtoverlay=i2c-gpio,i2c_gpio_scl=24,i2c_gpio_sda=23framebuffer_height=480
display_rotate=3 
start_x=1
gpu_mem=256
disable_splash=1
force_turbo=1
boot_delay=1
dtparam=i2c_arm=on
# dtparam=sd_overclock=90
# Disable the ACT LED.
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off
# Disable the PWR LED.
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=off

#--------GonzoPi configuration end here---------
EOF
elif [ "$screen" = "hyperpixel4" ]
then
apt-get -y install curl
echo "installing hyperpixel4 screen drivers"
curl -sSL get.pimoroni.com/hyperpixel4-legacy | bash
cat <<'EOF' >> /etc/udev/rules.d/98-hyperpixel4-calibration.rules
ATTRS{name}=="Goodix Capacitive TouchScreen", ENV{LIBINPUT_CALIBRATION_MATRIX}="0 1 0 -1 0 1"
EOF
echo "GonzoPi configuration seems to be in order in /boot/config.txt"
echo "Adding to /boot/config.txt"
cat <<'EOF' >> /boot/config.txt
#-----GonzoPi configuration starts here-------

[edid=HDMI-A-2]
hdmi_enable=1
max_framebuffers=2
disable_overscan=1
hdmi_force_hotplug:1=1
hdmi_group=:1=1
hdmi_mode:1=82
hdmi_blanking=1

[all]
#dtoverlay=vc4-fkms-v3d

#gonzopi-rpi-configuration-hyperpixel-1.0
#hyperpixel
#enable_dpi_lcd=1
#display_lcd_rotate=1
start_x=1
gpu_mem=512
disable_splash=1
force_turbo=1
boot_delay=1
# dtparam=sd_overclock=90
# Disable the ACT LED.
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off
# Disable the PWR LED.
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=off
#hdmi_force_hotplug=1
#hdmi_group=1
#hdmi_mode=16
#hdmi_port=2
#hdmi_blanking=1

#[edid=Ras-LCD Panel]
dtoverlay=hyperpixel4
#display_auto_detect=0
#display_default_lcd=0
framebuffer_width=800
framebuffer_height=480
overscan_left=0
overscan_right=0
overscan_top=0
overscan_bottom=0
enable_dpi_lcd=1
display_default_lcd=1
display_rotate=1
dpi_group=2
hdmi_group=3
dpi_mode=87
dpi_output_format=0x7f216
hdmi_timings=480 0 10 16 59 800 0 15 113 15 0 0 0 60 0 32000000 6
#hdmi_force_hotplug:1=1
#hdmi_group:1=2
#hdmi_mode:1=10

#--------GonzoPi configuration end here---------
EOF
elif [ "$screen" = "hdmi-screen" ]
then
echo "configuring hdmi screen"
echo "GonzoPi configuration seems to be in order in /boot/config.txt"
echo "Adding to /boot/config.txt"
cat <<'EOF' >> /boot/config.txt
#-----GonzoPi configuration starts here-------
#gonzopi-rpi-configuration-hdmi-screen
start_x=1
gpu_mem=256
disable_splash=1
force_turbo=1
boot_delay=1
# dtparam=sd_overclock=90
# Disable the ACT LED.
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off
# Disable the PWR LED.
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=off
framebuffer_width=800
framebuffer_height=480
#hdmi_force_hotplug=1
hdmi_group=1
hdmi_mode=3
#--------GonzoPi configuration end here---------
EOF
else
echo "screen driver already there, to change it remove gonzopi config in /boot/config.txt"
fi

echo "Change hostname to gonzopi"
cat <<'EOF' > /etc/hostname
gonzopi
EOF

cat <<'EOF' > /etc/hosts
127.0.0.1	localhost
::1		localhost ip6-localhost ip6-loopback
ff02::1		ip6-allnodes
ff02::2		ip6-allrouters

127.0.1.1	gonzopi
EOF

echo "consoleblank=0 logo.nologo loglevel=0"
echo "may be put at the end of line in this file /boot/cmdline.txt"
sleep 4

echo "Make USB soundcard default"
echo "writing to /etc/modprobe.d/alsa-base.conf"
if [ "$version" = "buster" ]
then
echo "Debian Buster Alsa config"
cat <<'EOF' > /etc/modprobe.d/alsa-base.conf
#set index value
options snd-usb-audio index=0
options snd_bcm2835 index=1
#reorder
options snd slots=snd_usb_audio, snd_bcm2835
EOF
else
echo "Debian Stretch Alsa config"
cat <<'EOF' > /etc/modprobe.d/alsa-base.conf
#set index value
options snd_usb_audio index=0
options snd_bcm2835 index=1
#reorder
options snd slots=snd_usb_audio, snd_bcm2835
EOF
fi

echo "Automatically boot to GonzoPi"
echo "creating a gonzopi.service file"
cat <<'EOF' > /etc/systemd/system/gonzopi.service
[Unit]
Description=gonzopi
After=getty.target
Conflicts=getty@tty1.service
DefaultDependencies=false

[Service]
Type=simple
RemainAfterExit=yes
ExecStart=/usr/bin/python3 /home/pi/gonzopi/gonzopi.py default
User=pi
Restart=on-failure
StandardInput=tty-force
StandardOutput=inherit
StandardError=inherit
TTYPath=/dev/tty1
TTYReset=yes
TTYVHangup=yes
Nice=-20
CPUSchedulingPolicy=rr
CPUSchedulingPriority=99

[Install]
WantedBy=local-fs.target
EOF

#dont kill process if user log out or in

cat <<'EOF' >> /etc/systemd/logind.conf
KillUserProcesses=no
EOF


#thanx systemd for making me search for years to make this all workd like a normal programd.
loginctl enable-linger
loginctl enable-linger pi

chmod +x /home/pi/gonzopi/gonzopi.py
systemctl enable gonzopi.service
systemctl daemon-reload
echo "systemd configuration done!"

echo "Installing gonzopi apache server configuration"
cp extras/gonzopi.conf /etc/apache2/sites-available/
#ln -s -t /var/www/ /home/pi/gonzopi/srv/
a2dissite 000-default.conf
a2ensite gonzopi.conf
echo "configure srv path to /home/pi/gonzopi/srv"

cat <<'EOF' >> /etc/apache2/apache2.conf
<Directory /home/pi/gonzopi/srv>
	Options Indexes FollowSymLinks
	AllowOverride None
	Require all granted
</Directory>
EOF
cat <<'EOF' >> /dev/shm/apache2.conf
<Directory /dev/shm/srv>
	Options Indexes FollowSymLinks
	AllowOverride None
	Require all granted
</Directory>
EOF
systemctl reload apache2

echo 'Dont do sync while copying to usb drives, does increase speed alöt!'
sed -i '/MOUNTOPTIONS=/c\MOUNTOPTIONS="noexec,nodev,noatime,nodiratime"' /etc/usbmount/usbmount.conf

echo "Adding harddrive tools..."
cat <<'EOF'
All this hard work to figure out how to keep NTFS mounted was done by F. Untermoser
https://raspberrypi.stackexchange.com/questions/41959/automount-various-usb-stick-file-systems-on-jessie-lite
Thanks alot!

while we are at it :)
To all the amazing FOSS people out there big big props and
  _____  ______  _____ _____  ______ _____ _______ _ 
 |  __ \|  ____|/ ____|  __ \|  ____/ ____|__   __| |
 | |__) | |__  | (___ | |__) | |__ | |       | |  | |
 |  _  /|  __|  \___ \|  ___/|  __|| |       | |  | |
 | | \ \| |____ ____) | |    | |___| |____   | |  |_|
 |_|  \_\______|_____/|_|    |______\_____|  |_|  (_)

EOF
apt-get -y install ntfs-3g exfat-fuse
#sed -i -e 's/MountFlags=slave/MountFlags=shared/g' /lib/systemd/system/systemd-udevd.service
#sed -i '/FS_MOUNTOPTIONS=/c\FS_MOUNTOPTIONS="-fstype=ntfs-3g,nls=utf8,umask=007,gid=46 -fstype=fuseblk,nls=utf8,umask=007,gid=46 -fstype=vfat,gid=1000,uid=1000,umask=007"' /etc/usbmount/usbmount.conf
#sed -i '/FILESYSTEMS=/c\FILESYSTEMS="vfat ext2 ext3 ext4 hfsplus ntfs fuseblk vfat"' /etc/usbmount/usbmount.conf

cat <<'EOF' >> /etc/usbmount/usbmount.conf
FS_MOUNTOPTIONS="-fstype=ntfs-3g,nls=utf8,umask=007,gid=46 -fstype=fuseblk,nls=utf8,umask=007,gid=46 -fstype=vfat,gid=1000,uid=1000,umask=007"
FILESYSTEMS="vfat ext2 ext3 ext4 hfsplus ntfs fuseblk vfat"
EOF

cat <<'EOF' > /etc/udev/rules.d/usbmount.rules
KERNEL=="sd*", DRIVERS=="sbp2",         ACTION=="add",  PROGRAM="/bin/systemd-escape -p --template=usbmount@.service $env{DEVNAME}", ENV{SYSTEMD_WANTS}+="%c"
KERNEL=="sd*", SUBSYSTEMS=="usb",       ACTION=="add",  PROGRAM="/bin/systemd-escape -p --template=usbmount@.service $env{DEVNAME}", ENV{SYSTEMD_WANTS}+="%c"
KERNEL=="ub*", SUBSYSTEMS=="usb",       ACTION=="add",  PROGRAM="/bin/systemd-escape -p --template=usbmount@.service $env{DEVNAME}", ENV{SYSTEMD_WANTS}+="%c"
KERNEL=="sd*",                          ACTION=="remove",       RUN+="/usr/share/usbmount/usbmount remove"
KERNEL=="ub*",                          ACTION=="remove",       RUN+="/usr/share/usbmount/usbmount remove"
EOF

cat <<'EOF' > /etc/systemd/system/usbmount@.service
[Unit]
BindTo=%i.device
After=%i.device

[Service]
Type=oneshot
TimeoutStartSec=0
Environment=DEVNAME=%I
ExecStart=/usr/share/usbmount/usbmount add
RemainAfterExit=yes
EOF

echo "Adding hacking tools..."
apt-get -y install vim htop screen nmap
cp extras/.vimrc /root/.vimrc
cp extras/.vimrc /home/pi/.vimrc

echo "Installing youtube upload mod..."
pip3 install pyshorteners
pip3 install google-api-python-client==1.7.3 oauth2client==4.1.2 progressbar2==3.38.0 httplib2==0.15.0

cd mods
./install-youtube-upload.sh
cd ..

echo "Setting up network configuration to use wicd program..."
echo "it works nicer from the terminal than raspberry pi default"
apt-get -y purge dhcpcd5 plymouth
apt-get -y install wicd wicd-curses

echo "Removing unnecessary programs from startup..."
systemctl disable lightdm.service --force
systemctl disable graphical.target --force
systemctl disable plymouth.service --force
systemctl disable bluetooth.service 
systemctl disable hciuart.service 

echo "Configure wifi region settings to FI, finland"
echo "You can change settings in extras/wifiset.sh file"
cp extras/wifiset.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable wifiset.service

echo "HURRAY! WE ARE"
cat <<'EOF'
  _____   ____  _   _ ______ _ 
 |  __ \ / __ \| \ | |  ____| |
 | |  | | |  | |  \| | |__  | |
 | |  | | |  | | . ` |  __| | |
 | |__| | |__| | |\  | |____|_|
 |_____/ \____/|_| \_|______(_)
                               
EOF
sleep 2
echo "Rebooting into up-to-date GonzoPi..."
sleep 2
reboot
