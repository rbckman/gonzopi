#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://gonzopi.org

cameramode=True
try:
    import picamerax as picamera
except:
    cameramode=False
import numpy as np
import string
import os
import time
import datetime
import multiprocessing as mp
from subprocess import call
from subprocess import Popen
omxplayermode=True
try:
    from omxplayer import OMXPlayer
except:
    omxplayermode=False
from multiprocessing import Process, Queue
import subprocess
import sys
import pickle
rpimode=True
try:
    import RPi.GPIO as GPIO
except:
    rpimode=False
from PIL import Image
import socket
import configparser
import shortuuid
if rpimode == True:
    import smbus
import ifaddr
import web
# Check for slider support
import serial
import serial.tools.list_ports
from pymediainfo import MediaInfo
# Get a list of all serial ports
slidecommander = ''
slideports = serial.tools.list_ports.comports()
# Print the available ports
if not slideports:
    print("No serial ports found.")
else:
    print("Available serial ports:")
    for p in slideports:
        print(f"{p.device} - {p.description}")
        if p.description.strip() == "FT232R USB UART":
            slidecommander = p.device
            print('Future Technology Found!')

#import shlex
from blessed import Terminal

# bless the code!
term = Terminal()

#DEBIAN VERSION
pipe = subprocess.check_output('lsb_release -c -s', shell=True)
debianversion = pipe.decode().strip()
print('running debian ' + debianversion)

if rpimode:
    #CHECK RASPBERRY PI VERSION
    pipe = subprocess.check_output('cat /sys/firmware/devicetree/base/model', shell=True)
    raspberrypiversion = pipe.decode().strip()
    print('on ' + raspberrypiversion)

    #give permissions to GPIO
    os.system('sudo chown root.gpio /dev/gpiomem')
    os.system('sudo chmod g+rw /dev/gpiomem')

    #give permissions to RAM
    os.system('sudo chown -R pi /dev/shm')

    #make cpu freq performance
    os.system('sudo cpufreq-set -g performance')

    #set IO
    os.system('sudo echo 20 | sudo tee /proc/sys/vm/dirty_background_ratio')
    os.system('sudo echo 40 | sudo tee /proc/sys/vm/dirty_ratio')

    #I2CBUTTONS
    probei2c = 0
    while probei2c < 3:
        try:
            if debianversion == "stretch":
                os.system('sudo modprobe i2c-dev')
                bus = smbus.SMBus(3) # Rev 2 Pi uses 1
            else:
                if 'Raspberry Pi 4 Model B' in raspberrypiversion:
                    os.system('sudo modprobe i2c-dev')
                    bus = smbus.SMBus(22) # Rev 2 Pi uses 1
                else:
                    os.system('sudo modprobe i2c-dev')
                    bus = smbus.SMBus(11) # Rev 2 Pi uses 1
            DEVICE = 0x20 # Device address (A0-A2)
            IODIRB = 0x0d # Pin pullups B-side
            IODIRA = 0x00 # Pin pullups A-side 0x0c
            IODIRApullup = 0x0c # Pin pullups A-side 0x0c
            GPIOB  = 0x13 # Register B-side for inputs
            GPIOA  = 0x12 # Register A-side for inputs
            OLATA  = 0x14 # Register for outputs
            bus.write_byte_data(DEVICE,IODIRB,0xFF) # set all gpiob to input
            bus.write_byte_data(DEVICE,IODIRApullup,0xF3) # set two pullup inputs and two outputs 
            bus.write_byte_data(DEVICE,IODIRA,0xF3) # set two inputs and two outputs 
            bus.write_byte_data(DEVICE,OLATA,0x4)
            print("yes, found em i2c buttons!")
            i2cbuttons = True
            break
        except:
            print("could not find i2c buttons!! running in keyboard only mode")
            print("trying again...")
            i2cbuttons = False
            probei2c += 1
            time.sleep(1)
            bus=''
else:
    i2cbuttons = False

#MAIN
def main():
    global headphoneslevel, miclevel, gonzopifolder, screen, loadfilmsettings, plughw, channels, filmfolder, scene, showmenu, rendermenu, quality, profilelevel, i2cbuttons, menudone, soundrate, soundformat, process, serverstate, que, port, recording, onlysound, camera_model, lens, fps_selection, fps_selected, fps, db, selected, cammode, newfilmname, camera_recording, abc, showhelp, camera, overlay, overlay2, recordwithports, crossfade, blendmodes, blendselect, udp_ip, udp_port, bitrate, pan, tilt, move, speed, slidereader,slide,smooth, muxing, film_fps, film_reso, film_fps_options, film_reso_options
    # Get path of the current dir, then use it as working directory:
    rundir = os.path.dirname(__file__)
    if rundir != '':
        os.chdir(rundir)
    #filmfolder = "/home/pi/Videos/"
    #picfolder = "/home/pi/Pictures/"
    gonzopifolder = os.getcwd()

    #MENUS
    if slidecommander:
        standardmenu = 'DSK:', 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'FPS:', 'Q:', 'BRIGHT:', 'CONT:', 'SAT:', 'VFX:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'BLEND:', 'MODE:', 'SHUTDOWN', 'SRV:', 'SEARCH:', 'WIFI:', 'UPDATE', 'UPLOAD', 'LOAD', 'NEW', 'TITLE', 'LIVE:', 'MUX:', 'HDMI:', 'SLIDE:'
    else:
        standardmenu = 'DSK:', 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'FPS:', 'Q:', 'BRIGHT:', 'CONT:', 'SAT:', 'VFX:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'BLEND:', 'MODE:', 'SHUTDOWN', 'SRV:', 'SEARCH:', 'WIFI:', 'UPDATE', 'UPLOAD', 'LOAD', 'NEW', 'TITLE', 'LIVE:', 'MUX:', 'HDMI:'
    gonzopictrlmenu = 'DSK:', 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'FPS:', 'Q:', 'BRIGHT:', 'CONT:', 'SAT:', 'VFX:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'BLEND:', 'MODE:', 'SHUTDOWN', 'SRV:', 'SEARCH:', 'WIFI:', 'CAMERA:', 'Add CAMERA', 'New FILM', 'New SCENE', 'Sync SCENE'
    #gonzopictrlmenu = "BACK","CAMERA:", "Add CAMERA","New FILM","","New SCENE","Sync SCENE","Snapshot"
    emptymenu='','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''
    menu = standardmenu
    hide_menu_time=4
    showmenutime = time.time()+6
    oldmenu=''
    showgonzopictrl = False
    recordwithports = False
    pressagain = ''
    #STANDARD VALUES (some of these may not be needed, should do some clean up)
    abc = '_','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0'
    numbers_only = ' ','0','1','2','3','4','5','6','7','8','9'
    keydelay = 0.0555
    selectedaction = 0
    selected = 0
    awb = 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
    awbx = 0
    udp_ip = ''
    udp_port = ''
    awb_lock = 'no'
    effects = 'none', 'negative', 'solarize', 'denoise', 'colorpoint', 'colorswap', 'posterise', 'blur', 'film'
    effectselected = 0
    blendmodes = 'screen', 'average', 'darken', 'lighten', 'burn', 'multiply'
    blendselect=0
    blending=False
    fade='in'
    fadelength=3
    hdmi='off'
    cammode = 'film'
    camera_model=''
    slidemode=False
    fps_selected=8
    fps_selection=[]
    film_reso_options='1920x1080','1920x816'
    film_fps_options=[24,25,30]
    film_reso_selected=0
    film_fps_selected=1
    film_reso=film_reso_options[film_reso_selected]
    film_fps=int(film_fps_options[film_fps_selected])
    fps=int(film_fps)
    if 'Raspberry Pi 4 Model B' in raspberrypiversion:
        quality = 20
        bitrate = 8888888
    if 'Raspberry Pi 3 Model B' in raspberrypiversion:
        quality = 20
        bitrate = 1111111
    profilelevel='4.2'
    headphoneslevel = 40
    miclevel = 50
    soundformat = 'S16_LE'
    soundrate = '48000'
    recording = False
    retake = False
    playdubonrec = False
    playdubrecord = False
    playdubrecfile = ''
    lastmenu = ''
    menudone = ''
    rendermenu = True
    showmenu = 1
    showmenu_settings = True
    showhelp = False
    oldchecksync = 0
    overlay = None
    overlay2 = None
    underlay = None
    reclength = 0
    t = 0
    rectime = ''
    scene = 1
    shot = 1
    take = 1
    pic = 1
    speed = 10
    pan = 0
    tilt = 0
    move = 0
    slidereader = None
    smooth = 100
    slide=1
    onlysound=False
    filmname = 'reel_001'
    newfilmname = ''
    beeps = 0
    beepcountdown = 0
    beeping = False
    backlight = True
    lastbeep = time.time()
    flip = 'yes'
    between = 30
    duration = 0.2
    dsk = 0
    lenses = os.listdir('lenses/')
    lens = lenses[0]
    buttontime = time.time()
    pressed = ''
    buttonpressed = False
    holdbutton = ''
    updatethumb = False
    loadfilmsettings = True
    oldsettings = ''
    comp = 0
    yanked = ''
    copying = ''
    shots_selected=[]
    scenes_selected=[]
    films_selected=[]
    moving = False
    stream = ''
    live = 'no'
    rec_process = ''
    peakshot = ''
    peaktake = ''
    plughw = 0 #default audio device
    channels = 1 #default mono
    #SAVE SETTINGS FREQUENCY IN SECS
    pausetime = time.time()
    savesettingsevery = 5
    #TARINA VERSION
    f = open(gonzopifolder + '/VERSION')
    gonzopiversion = f.readline().strip()
    gonzopivername = f.readline().strip()
    print('Gonzo Pi '+gonzopiversion+ ' '+gonzopivername)
    db=''
    synclist=[]
    muxing=False
    mux='no'
    camera = ''
    gputemp = ''
    cputemp = ''
    newbitrate = ''

    #SYSTEM CONFIGS (turn off hdmi)
    #run_command('tvservice -o')
    #Kernel page cache optimization for sd card
    if rpimode:
        run_command('sudo ' + gonzopifolder + '/extras/sdcardhack.sh')
        #Make screen shut off work and run full brightness
        run_command('gpio -g mode 19 pwm ')
        run_command('gpio -g pwm 19 1023')

    filmfolder = os.path.expanduser('~')+'/gonzopifilms/'

    if os.path.isdir(filmfolder) == False:
        os.makedirs(filmfolder)

    #STORAGE DRIVES
    storagedrives=[['sd',filmfolder]]

    #CHECK IF FILMING TO USB STORAGE
    #if os.path.exists('/dev/sda1') == False:
    #    os.system('sudo pumount /media/usb0')
    #    os.system('sudo umount -l /media/usb0')
    #if os.path.exists('/dev/sda2') == False:
    #    os.system('sudo pumount /media/usb1')
    #    os.system('sudo umount -l /media/usb1')
    filmfolderusb=usbfilmfolder(dsk)
    if filmfolderusb:
        filmfolder=filmfolderusb
        storagedrives.append(['usb0',filmfolder])
        dsk=1
        loadfilmsettings == True
        if os.path.isdir(filmfolder) == False:
            os.makedirs(filmfolder)
 
    #COUNT DISKSPACE
    disk = os.statvfs(filmfolder)
    diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'

    #LOAD FILM AND SCENE SETTINGS
    try:
        filmname = getfilms(filmfolder)[0][0]
    except:
        filmname = filmname 
        if os.path.isdir(filmfolder+filmname) == False:
            os.makedirs(filmfolder+filmname)

    #Load settings
    try:
        filmsettings = loadsettings(filmfolder, filmname)
        quality = filmsettings[18]
        bitrate=filmsettings[30]
        logger.warning('quality and bitrate: '+str(quality)+' '+str(bitrate)+' loaded')
        time.sleep(0.2)
    except:
        logger.warning('could not load bitrate')

    if rpimode:
        #FIRE UP CAMERA
        camera = startcamera(camera)
        #START INTERFACE
        startinterface()
    else:
        camera=None

    #GET FILMFOLDER AND CAMERA VERSION
    camera_model, camera_revision , originalfilmfolder = getconfig(camera)

    #THUMBNAILCHECKER
    oldscene = scene
    oldshot = shot
    oldtake = take

   #TURN ON WIFI AND TARINA SERVER
    serverstate = 'on'
    wifistate = 'on'
    if os.path.isdir(gonzopifolder+'/srv/sessions') == False:
        os.makedirs(gonzopifolder+'/srv/sessions')
    os.system('sudo chown -R www-data '+gonzopifolder+'/srv/sessions')
    os.system('sudo ln -sf /dev/shm/srv/menu.html '+gonzopifolder+'/srv/static/menu.html')
    os.system('sudo mkdir /dev/shm/srv')
    os.system('sudo chown -R www-data /dev/shm/srv')
    os.system('sudo chown -R www-data '+gonzopifolder+'/srv/static/')
    #serverstate = gonzopiserver(False)
    #TO_BE_OR_NOT_TO_BE 
    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
    filename = 'take' + str(take).zfill(3)
    picturename = 'take' + str(take).zfill(3)
    recordable = not os.path.isfile(foldername + filename + '.mp4') and not os.path.isfile(foldername + filename + '.h264') and not os.path.isfile(foldername + picturename + '.jpeg')

    #CLEAN
    #clean('',filmfolder)

    #--------------Gonzopi Controller over socket ports --------#

    #TARINACTRL
    camerasconnected=''
    sleep=0.2
    cameras = []
    camerasoff =[]
    camselected=0
    newselected=0 
    mastersound=None
    camera_recording=None
    pingip=0
    searchforcameras='off'
    #NETWORKS
    networks=[]
    network=''
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        print("IPs of network adapter " + adapter.nice_name)
        for ip in adapter.ips:
            if ':' not in ip.ip[0] and '127.0.0.1' != ip.ip:
                print(ip.ip)
                networks=[ip.ip]
    if networks != []:
        network=networks[0]
        if network not in cameras and network != '':
            cameras=[]
            cameras.append(network)

    port = 55555
    que = Queue()
    process = Process(target=listenforclients, args=("0.0.0.0", port, que))
    process.start()
    nextstatus = ''

    serverstate_old='off'
    wifistate_old='off'


    if rpimode:
        #--------------Rpi MAIN LOOP---------------#
        while True:
            pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
            if pressagain != '':
                pressed = pressagain
                pressagain = ''
            #event = screen.getch()
            if wifistate != wifistate_old:
                if wifistate == 'on':
                    run_command('sudo iwconfig wlan0 txpower auto')
                elif wifistate == 'off':
                    run_command('sudo iwconfig wlan0 txpower off')
                wifistate_old = wifistate
            if serverstate != serverstate_old:
                if serverstate == 'on':
                    gonzopiserver(True)
                elif serverstate == 'off':
                    gonzopiserver(False)
                serverstate_old=serverstate
            if recording == False:
                #SHUTDOWN
                if pressed == 'middle' and menu[selected] == 'SHUTDOWN':
                    writemessage('Hold on shutting down...')
                    time.sleep(1)
                    run_command('sudo shutdown -h now')
                #MODE
                elif pressed == 'changemode':
                    if cammode == 'film':
                        cammode = 'picture'
                        vumetermessage('changing to picture mode')
                    elif cammode == 'picture':
                        cammode = 'film'
                        vumetermessage('changing to film mode')
                    camera = stopcamera(camera, rec_process)
                    camera = startcamera(camera)
                    loadfilmsettings = True
                #PICTURE
                elif pressed == 'picture':
                    if os.path.isdir(foldername) == False:
                        os.makedirs(foldername)
                    picture = foldername +'picture' + str(take).zfill(3) + '.jpeg'
                    run_command('touch ' + foldername + '.placeholder')
                    print('taking picture')
                    camera.capture(picture,format="jpeg",use_video_port=True) 
                #PEAKING
                elif pressed == 'peak' and recordable == True:
                    if shot > 1:
                        peakshot = shot - 1
                        peaktake = counttakes(filmname, filmfolder, scene, peakshot)
                    p_imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(peakshot).zfill(3) + '/take' + str(peaktake).zfill(3) + '.jpeg'
                    overlay = displayimage(camera, p_imagename, overlay, 3)
                    while holdbutton == 'peak':
                        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
                        vumetermessage('peaking ' + str(peakshot))
                        time.sleep(0.03)
                    overlay = removeimage(camera, overlay)
                #SHOWHELP
                elif pressed == 'showhelp':
                    vumetermessage('Button layout')
                    if showhelp == False:
                        overlay2 = removeimage(camera, overlay2)
                        overlay2 = displayimage(camera, gonzopifolder+'/extras/buttons.png', overlay, 4)
                        showhelp = True
                    elif showhelp == True:
                        overlay2 = removeimage(camera, overlay2)
                        updatethumb =  True
                        showhelp = False
                    #while holdbutton == 'showhelp' or pressed == 'H':
                    #    pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
                    #    vumetermessage('Button layout')
                    #    time.sleep(0.03)
                #TIMELAPSE
                elif pressed == 'middle' and menu[selected] == 'TIMELAPSE':
                    overlay = removeimage(camera, overlay)
                    takes = counttakes(filmname, filmfolder, scene, shot)
                    if takes > 0:
                        shot = countshots(filmname, filmfolder, scene) + 1
                        take = 1
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    renderedfilename, between, duration = timelapse(beeps,camera,filmname,foldername,filename,between,duration,backlight)
                    if renderedfilename != '':
                        #render thumbnail
                        #writemessage('creating thumbnail')
                        #run_command('avconv -i ' + foldername + filename  + '.mp4 -frames 1 -vf scale=800:460 ' + foldername + filename + '.jpeg')
                        updatethumb =  True
                #VIEW SCENE
                elif pressed == 'view' and menu[selected] == 'SLIDE:':
                    send_serial_port(slidecommander,';'+str(slide))
                    slide += 1
                elif pressed == 'remove' and menu[selected] == 'SLIDE:':
                    send_serial_port(slidecommander,'<')
                elif pressed == 'view' and menu[selected] == 'SCENE:':
                    writemessage('Loading scene...')
                    organize(filmfolder, filmname)
                    filmfiles = shotfiles(filmfolder, filmname, scene)
                    vumetermessage('press middlebutton to cancel')
                    if len(filmfiles) > 0:
                        removeimage(camera, overlay)
                        camera = stopcamera_preview(camera)
                        #Check if rendered video exist
                        #renderfilename, newaudiomix = renderscene(filmfolder, filmname, scene)
                        renderfilename = renderfilm(filmfolder, filmname, comp, scene)
                        #writemessage('Render done!')
                        if renderfilename != '':
                            remove_shots = playdub(filmname,renderfilename, 'film',take)
                            #fastedit (maybe deploy sometime)
                            #if remove_shots != []:
                            #    for i in remove_shots:
                            #        remove(filmfolder, filmname, scene, i, take, 'shot')
                            #    organize(filmfolder, filmname)
                            #    updatethumb = True
                            #    #loadfilmsettings = True
                            #    time.sleep(0.5)
                            #else:
                            #    print('nothing to remove')
                        camera = startcamera_preview(camera)
                        #loadfilmsettings = True
                    else:
                        vumetermessage("There's absolutely nothing in this scene! hit rec!")
                    updatethumb=True
                    rendermenu = True
                #VIEW FILM
                elif pressed == 'view' and menu[selected] == 'FILM:':
                    writemessage('Loading film...')
                    organize(filmfolder, filmname)
                    filmfiles = viewfilm(filmfolder, filmname)
                    vumetermessage('press middlebutton to cancel')
                    if len(filmfiles) > 0:
                        removeimage(camera, overlay)
                        camera = stopcamera_preview(camera)
                        #removeimage(camera, overlay)
                        renderfilename = renderfilm(filmfolder, filmname, comp, 0)
                        #camera = stopcamera(camera, rec_process)
                        if renderfilename != '':
                            remove_shots = playdub(filmname,renderfilename, 'film',take)
                        #overlay = displayimage(camera, imagename, overlay, 3)
                        camera = startcamera_preview(camera)
                        loadfilmsettings = True
                    else:
                        vumetermessage('wow, shoot first! there is zero, nada, zip footage to watch now... just hit rec!')
                    updatethumb=True
                    rendermenu = True
                #VIEW SHOT OR TAKE
                elif pressed == 'view':
                    takes = counttakes(filmname, filmfolder, scene, shot)
                    if take == takes+1:
                        take = takes
                    if takes > 0:
                        vumetermessage('press middlebutton to cancel')
                        writemessage('Loading clip...')
                        removeimage(camera, overlay)
                        camera = stopcamera_preview(camera)
                        organize(filmfolder, filmname)
                        foldername = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                        filename = 'take' + str(take).zfill(3)
                        #compileshot(foldername + filename,filmfolder,filmname)
                        renderfilename, newaudiomix = rendershot(filmfolder, filmname, foldername+filename, scene, shot)
                        if renderfilename == foldername+filename:
                            trim, split_list = playdub(filmname,foldername + filename, 'shot',take)
                            if split_list != []:
                                print(split_list)
                                #time.sleep(5)
                                split_list_save(foldername, split_list)
                                writemessage('Splits saved! press view to see them.')
                            else:
                                if trim[0] == 'beginning' or trim[0] == 'end':
                                    writemessage('Cutting clip...')
                                    videotrimsave(foldername, trim[0], trim[1], filename)
                                elif trim[0] >= trim[1]:
                                    trim = [trim[0],0]
                                elif trim[0] != 0 and trim[1] != 0:
                                    writemessage('Cutting clip...')
                                    videotrimsave(foldername, 'end', trim[1], filename)
                                    videotrimsave(foldername, 'beginning', trim[0], filename)
                                elif trim[0] == 0 and trim[1] != 0:
                                    writemessage('Cutting clip...')
                                    videotrimsave(foldername, 'end', trim[1], filename)
                                if trim[0] != 0 and trim[1] == 0:
                                    writemessage('Cutting clip...')
                                    videotrimsave(foldername, 'beginning', trim[0], filename)
                            imagename = foldername + filename + '.jpeg'
                            camera = startcamera_preview(camera)
                            #loadfilmsettings = True
                            overlay = displayimage(camera, imagename, overlay, 3)
                        else:
                            #vumetermessage('nothing here! hit rec!')
                            playdub(filmname, renderfilename, 'shot',take)
                            take = counttakes(filmname, filmfolder, scene, shot)
                        rendermenu = True
                        updatethumb=True
                    else:
                        shot = shots
                        takes = counttakes(filmname, filmfolder, scene, shot)
                        take=takes
                    rendermenu = True
                    updatethumb=True
                #BLEND
                elif pressed == 'middle' and menu[selected] == 'BLEND:' and recordable == False:
                    videolength=0
                    blenddir = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/blend/'
                    filename=yanked
                    #compileshot(scenedir+'blend/'+blendmodes[blendselect]+'.h264',filmfolder,filmname)
                    if filename[-7:-3] == 'shot':
                        takename = gettake(filename)
                        if '.h264' in takename:
                            filename=filename+'/'+takename[:-5]
                        if '.mp4' in takename:
                            filename=filename+'/'+takename[:-4]
                        compileshot(filename,filmfolder,filmname)
                    elif filename[-8:-3] == 'scene':
                        filename=filename+'/scene'
                    else:
                        filename=filename+'/'+filmname
                    #pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
                    #videolength = pipe.decode().strip()
                    videolength=get_video_length(filename+'.mp4')
                    videolength=(int(videolength)/1000)
                    os.makedirs(blenddir,exist_ok=True)
                    #videotrim(blenddir,filename,'end', videolength)
                    os.system('cp '+filename+'.mp4 '+blenddir+blendmodes[blendselect]+'.mp4')
                    rendermenu = True
                    vumetermessage('blend done.')
                #CROSSFADE
                elif pressed == 'middle' and menu[selected] == 'CROSSFADE:':
                    folder = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    vumetermessage('New crossfade made!')
                    crossfadesave(folder,crossfade,filename)     
                elif pressed == 'middle' and menu[selected] == 'SHOT:':
                    folder = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    if folder in shots_selected:
                        shots_selected.remove(folder)
                        shots_sel = ''
                        vumetermessage(str(len(shots_selected))+' shots selected')
                    else:
                        shots_selected.append(folder)
                        shots_sel = '*'
                        vumetermessage(str(len(shots_selected))+' shots selected')
                    os.system('rm /dev/shm/videos_selected')
                    f = open('/dev/shm/videos_selected', 'w')
                    for i in shots_selected:
                        f.write(i+'\n')
                    f.close()
                elif pressed == 'middle' and menu[selected] == 'SCENE:':
                    folder = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/'
                    if folder in scenes_selected:
                        scenes_selected.remove(folder)
                        scenes_sel = ''
                        vumetermessage(str(len(scenes_selected))+' scenes selected')
                    else:
                        scenes_selected.append(folder)
                        scenes_sel = '*'
                        vumetermessage(str(len(scenes_selected))+' scenes selected')
                elif pressed == 'middle' and menu[selected] == 'FILM:':
                    folder = filmfolder + filmname + '/'
                    if folder in films_selected:
                        films_selected.remove(folder)
                        vumetermessage(str(len(films_selected))+' films selected')
                    else:
                        films_selected.append(folder)
                        vumetermessage(str(len(films_selected))+' films selected')
                #DUB SHOT
                elif pressed == 'dub' and menu[selected] == 'SHOT:' and recordable == False:
                    newdub, yanked = clipsettings(filmfolder, filmname, scene, shot, take, plughw,yanked)
                    take = counttakes(filmname, filmfolder, scene, shot)
                    if newdub:
                        camera = stopcamera_preview(camera)
                        #save original sound
                        dubfolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/dub/'
                        saveoriginal = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take'+str(take).zfill(3)+'.wav'
                        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, shot)
                        foldername = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                        filename = 'take' + str(take).zfill(3)
                        if dubfiles==[]:
                            print('no dubs, copying original sound to original')
                            #os.system('cp '+saveoriginal+' '+dubfolder+'original.wav')
                            #audio_origins = (os.path.realpath(saveoriginal+'.wav'))[:-5]
                            videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                            tot = int(videos_totalt.videos)
                            audio_origins=datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                            os.system('cp '+saveoriginal+' '+filmfolder+'.videos/'+audio_origins+'.wav')
                            os.system('ln -sfr '+filmfolder+'.videos/'+audio_origins+'.wav '+dubfolder+'original.wav')
                            time.sleep(0.2)
                        renderfilename, newaudiomix = rendershot(filmfolder, filmname, foldername+filename, scene, shot)
                        playdub(filmname,renderfilename, 'dub',take)
                        #run_command('sox -V0 -G /dev/shm/dub.wav -c 2 ' + newdub)
                        #add audio/video start delay sync
                        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                        tot = int(videos_totalt.videos)
                        audio_origins=datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                        run_command('sox -V0 -G '+filmfolder+'.tmp/dub.wav -c 2 '+filmfolder+'.videos/'+audio_origins+'.wav trim 0.013')
                        os.system('ln -sfr '+filmfolder+'.videos/'+audio_origins+'.wav '+newdub)
                        #audiosync, videolength, audiolength = audiotrim(renderfilename, 'end', newdub)
                        vumetermessage('new shot dubbing made!')
                        #rerender audio
                        #run_command('rm '+filmfolder+'.tmp/dub.wav')
                        os.system('rm ' + filmfolder + filmname + '/.audiohash')
                        camera = startcamera_preview(camera)
                        #loadfilmsettings = True
                        time.sleep(1)
                    else:
                        vumetermessage('see ya around!')
                    rendermenu = True
                #DUB SCENE
                elif pressed == 'dub' and menu[selected] == 'SCENE:':
                    newdub, yanked = clipsettings(filmfolder, filmname, scene, 0, take, plughw,yanked)
                    if newdub:
                        camera = stopcamera_preview(camera)
                        renderfilename, newaudiomix = renderscene(filmfolder, filmname, scene)
                        playdub(filmname,renderfilename, 'dub',take)
                        #run_command('sox -V0 -G /dev/shm/dub.wav -c 2 ' + newdub)
                        #add audio/video start delay sync 
                        dubfolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/dub/'
                        os.makedirs(dubfolder,exist_ok=True)
                        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                        tot = int(videos_totalt.videos)

                        audio_origins=datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                        run_command('sox -V0 -G '+filmfolder+'.tmp/dub.wav -c 2 '+filmfolder+'.videos/'+audio_origins+'.wav trim 0.013')
                        os.system('ln -sfr '+filmfolder+'.videos/'+audio_origins+'.wav '+newdub)
                        run_command('rm '+filmfolder+'.tmp/dub.wav')
                        #audiosync, videolength, audiolength = audiotrim(renderfilename, 'end', newdub)
                        vumetermessage('new scene dubbing made!')
                        #rerender audio
                        os.system('rm ' + filmfolder + filmname + '/.audiohash')
                        camera = startcamera_preview(camera)
                        #loadfilmsettings = True
                        time.sleep(1)
                    else:
                        vumetermessage('see ya around!')
                    rendermenu = True
                #DUB FILM
                elif pressed == 'dub' and menu[selected] == 'FILM:':
                    newdub, yanked = clipsettings(filmfolder, filmname, 0, 0, take, plughw,yanked)
                    if newdub:
                        camera = stopcamera_preview(camera)
                        renderfilename = renderfilm(filmfolder, filmname, comp, 0)
                        playdub(filmname,renderfilename, 'dub',take)
                        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                        tot = int(videos_totalt.videos)
                        audio_origins=datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                        run_command('sox -V0 -G '+filmfolder+'.tmp/dub.wav -c 2 '+filmfolder+'.videos/'+audio_origins+'.wav trim 0.013')
                        os.system('ln -sfr '+filmfolder+'.videos/'+audio_origins+'.wav '+newdub)
                        run_command('rm '+filmfolder+'.tmp/dub.wav')
                        vumetermessage('new film dubbing made!')
                        camera = startcamera_preview(camera)
                        #loadfilmsettings = True
                        time.sleep(1)
                    else:
                        vumetermessage('see ya around!')
                    rendermenu = True
                #BACKUP
                elif pressed == 'middle' and menu[selected] == 'BACKUP':
                    copytousb(filmfolder)
                    rendermenu = True
                #UPLOAD
                elif pressed == 'middle' and menu[selected] == 'UPLOAD':
                    if webz_on() == True:
                        filmfiles = viewfilm(filmfolder, filmname)
                        if len(filmfiles) > 0:
                            renderfilename = renderfilm(filmfolder, filmname, comp, 0)
                            cmd = uploadfilm(renderfilename, filmname)
                            if cmd != None:
                                camera = stopinterface(camera)
                                camera = stopcamera(camera, 'rec_process')
                                try:
                                    run_command(cmd)
                                except:
                                    logger.warning('uploadfilm bugging')
                                startinterface()
                                camera = startcamera(camera)
                                #loadfilmsettings = True
                                loadfilmsettings = True
                            selectedaction = 0
                    rendermenu = True
                #LOAD FILM
                elif pressed == 'middle' and menu[selected] == 'LOAD':
                    camera, filmname = loadfilm(filmname, filmfolder, camera, overlay)
                    allfilm = getfilms(filmfolder)
                    for i in allfilm:
                        if i[0] == newfilmname:
                            filmname_exist=True
                    if filmname != newfilmname and filmname_exist==False:
                        filmname = newfilmname
                        os.makedirs(filmfolder + filmname)
                        vumetermessage('Good luck with your film ' + filmname + '!')
                        #make a filmhash
                        print('making filmhash...')
                        filmhash = shortuuid.uuid()
                        with open(filmfolder + filmname + '/.filmhash', 'w') as f:
                            f.write(filmhash)
                        updatethumb = True
                        rendermenu = True
                        scene = 1
                        shot = 1
                        take = 1
                        #selectedaction = 0
                        newfilmname = ''
                    else:
                        filmname = newfilmname
                        newfilmname = ''
                        vumetermessage('film already exist!')
                        logger.info('film already exist!')
                        print(term.clear)
                    updatethumb = True
                    loadfilmsettings = True
                    rendermenu = True
                #UPDATE
                elif pressed == 'middle' and menu[selected] == 'UPDATE':
                    if webz_on() == True:
                        camera = stopinterface(camera)
                        camera = stopcamera(camera, 'rec_process')
                        gonzopiversion, gonzopivername = update(gonzopiversion, gonzopivername)
                        startinterface()
                        camera = startcamera(camera)
                        loadfilmsettings = True
                        selectedaction = 0
                    rendermenu = True
                #WIFI
                elif pressed == 'middle' and menu[selected] == 'WIFI:':
                    camera = stopinterface(camera)
                    camera = stopcamera(camera, 'rec_process')
                    run_command('wicd-curses')
                    startinterface()
                    camera = startcamera(camera)
                    loadfilmsettings = True
                    rendermenu = True
                #NEW FILM
                elif pressed == 'middle' and menu[selected] == 'NEW' or filmname == '' or pressed == 'new_film':
                    filmname_exist=False
                    if newfilmname == '':
                        newfilmname = nameyourfilm(filmfolder, filmname, abc, True)
                    allfilm = getfilms(filmfolder)
                    for i in allfilm:
                        if i[0] == newfilmname:
                            filmname_exist=True
                    if filmname != newfilmname and filmname_exist==False:
                        filmname = newfilmname
                        os.makedirs(filmfolder + filmname)
                        vumetermessage('Good luck with your film ' + filmname + '!')
                        #make a filmhash
                        print('making filmhash...')
                        filmhash = shortuuid.uuid()
                        with open(filmfolder + filmname + '/.filmhash', 'w') as f:
                            f.write(filmhash)
                        updatethumb = True
                        rendermenu = True
                        scene = 1
                        shot = 1
                        take = 1
                        #selectedaction = 0
                        newfilmname = ''
                        #film_reso, film_fps = film_settings()
                        #stop()
                        #camera = stopcamera_preview(camera)
                        #camera = startcamera_preview(camera)
                        #loadfilmsettings = True
                    else:
                        print(term.clear)
                        filmname = newfilmname
                        newfilmname = ''
                #EDIT FILM NAME
                elif pressed == 'middle' and menu[selected] == 'TITLE' or filmname == '':
                    newfilmname = nameyourfilm(filmfolder, filmname, abc, False)
                    if filmname != newfilmname:
                        os.system('mv ' + filmfolder + filmname + ' ' + filmfolder + newfilmname)
                        os.system('mv ' + filmfolder + newfilmname + '/'+filmname+'.mp4 ' + filmfolder + newfilmname+'/'+newfilmname+'.mp4')
                        os.system('mv ' + filmfolder + newfilmname + '/'+filmname+'.wav ' + filmfolder + newfilmname+'/'+newfilmname+'.wav')
                        os.system('mv ' + filmfolder + newfilmname + '/'+filmname+'.info ' + filmfolder + newfilmname+'/'+newfilmname+'.info')
                        filmname = newfilmname
                        db = get_film_files(filmname,filmfolder,db)
                        vumetermessage('Film title changed to ' + filmname + '!')
                    else:
                        vumetermessage('')
                    rendermenu = True

                #PASTE MANY SCENES
                elif pressed == 'copy' and menu[selected] == 'SCENE:' and scenes_selected != [] or pressed == 'move' and menu[selected] == 'SCENE:' and scenes_selected != []:
                    landingscene=scene-1
                    for yanked in reversed(scenes_selected):
                        vumetermessage('Pasting scene, please wait...')
                        paste = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_yanked'
                        os.system('cp -r ' + yanked + ' ' + paste)
                        if pressed == 'move':
                            os.system('touch ' + yanked + '/.remove')
                        add_organize(filmfolder, filmname)
                        yanked = ''
                    scenes_selected = []
                    organize(filmfolder, filmname)
                    organize(filmfolder, filmname)
                    updatethumb = True
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    if scene > scenes:
                        scene = scenes
                    if shot > shots:
                        shot = shots
                    vumetermessage('All scenes pasted!')
                    yanked = ''
                    scene=landingscene
                #PASTE MANY SHOTS
                elif pressed == 'copy' and menu[selected] == 'SHOT:' and shots_selected != []  or pressed == 'move' and menu[selected] == 'SHOT:' and shots_selected != []:
                    landingshot=shot-1
                    for yanked in reversed(shots_selected):
                        take = counttakes(filmname, filmfolder, scene, shot)
                        if shot == 0:
                            shot=1
                        vumetermessage('Pasting shot, please wait...')
                        paste = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_yanked' 
                        try:
                            os.makedirs(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3))
                        except:
                            pass
                        os.system('cp -r ' + yanked + ' ' + paste)
                        if pressed == 'move':
                            os.system('touch ' + yanked + '/.remove')
                        add_organize(filmfolder, filmname)
                        yanked = ''
                    os.system('rm /dev/shm/videos_selected')
                    shots_selected = []
                    organize(filmfolder, filmname)
                    organize(filmfolder, filmname)
                    updatethumb = True
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    if scene > scenes:
                        scene = scenes
                    if shot > shots:
                        shot = shots
                    vumetermessage('All shots pasted!')
                    yanked = ''
                    shot=landingshot
                #(YANK) COPY FILM
                elif pressed == 'copy' and menu[selected] == 'FILM:':
                    copying = 'film'
                    yanked = filmfolder + filmname
                    pastefilmname = filmname
                    vumetermessage('Film ' + filmname + ' copied! (I)nsert button to place it...')
                #(YANK) COPY TAKE
                elif pressed == 'copy' and menu[selected] == 'TAKE:' and recordable == False:
                    copying = 'take'
                    yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)+'/take' + str(take).zfill(3)
                    vumetermessage('Take ' + str(take) + ' copied! (I)nsert button to place it...')
                #(YANK) COPY SHOT
                elif pressed == 'copy' and menu[selected] == 'SHOT:':
                    copying = 'shot'
                    yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                    vumetermessage('Shot ' + str(shot) + ' copied! (I)nsert button to place it...')
                #(YANK) COPY SCENE
                elif pressed == 'copy' and menu[selected] == 'SCENE:':
                    copying = 'scene'
                    yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                    vumetermessage('Scene ' + str(scene) + ' copied! (I)nsert button to place it...')
                #(CUT) MOVE TAKE
                elif pressed == 'move' and menu[selected] == 'TAKE:' and recordable == False:
                    copying = 'take'
                    moving = True
                    yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)+'/take' + str(take).zfill(3)
                    vumetermessage('Moving shot ' + str(shot) + ' (I)nsert button to place it...')
                #(CUT) MOVE SHOT
                elif pressed == 'move' and menu[selected] == 'SHOT:':
                    copying='shot'
                    moving = True
                    yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                    vumetermessage('Moving shot ' + str(shot) + ' (I)nsert button to place it...')
                #(CUT) MOVE SCENE
                elif pressed == 'move' and menu[selected] == 'SCENE:':
                    copying='scene'
                    moving = True
                    yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                    vumetermessage('Moving scene ' + str(scene) + ' (I)nsert button to place it...')

                #PASTE SHOT and PASTE SCENE
                elif pressed == 'insert' and yanked:
                    if copying == 'take' and menu[selected] == 'TAKE:':
                        take = counttakes(filmname, filmfolder, scene, shot)
                        if shot == 0:
                            shot=1
                        take=take+1
                        vumetermessage('Pasting take, please wait...')
                        paste = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3)
                        try:
                            os.makedirs(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot'+ str(shot).zfill(3))
                        except:
                            pass
                        os.system('cp ' + yanked + '.mp4 ' + paste + '.mp4')
                        os.system('cp ' + yanked + '.info ' + paste + '.info')
                        os.system('cp ' + yanked + '.nofaststart ' + paste + '.nofaststart')
                        os.system('cp ' + yanked + '.jpeg ' + paste + '.jpeg')
                        os.system('cp ' + yanked + '.h264 ' + paste + '.h264')
                        os.system('cp ' + yanked + '.wav ' + paste + '.wav')
                        paste = ''
                        if moving == True:
                            os.system('rm -r ' + yanked + '*')
                    elif copying == 'shot' and menu[selected] == 'SHOT:':
                        take = counttakes(filmname, filmfolder, scene, shot)
                        if shot == 0:
                            shot=1
                        vumetermessage('Pasting shot, please wait...')
                        paste = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_yanked' 
                        try:
                            os.makedirs(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3))
                        except:
                            pass
                        os.system('cp -r ' + yanked + ' ' + paste)
                        if moving == True:
                            os.system('rm -r ' + yanked+'/*')
                            #Remove hidden placeholder
                            #os.system('rm ' + yanked + '/.placeholder')
                    elif copying == 'scene' and menu[selected]=='SCENE:':
                        vumetermessage('Pasting scene, please wait...')
                        paste = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_yanked'
                        os.system('cp -r ' + yanked + ' ' + paste)
                        if moving == True:
                            os.system('rm -r ' + yanked+'/*')
                            #Remove hidden placeholder
                            os.system('rm ' + yanked + '/.placeholder')
                        try:
                            run_command('rsync -avr --update --progress --files-from='+yanked+'/.origin_videos --no-relative / ' +filmfolder+'.videos/')
                        except:
                            logger.info('no origin videos')
                    elif copying == 'film' and menu[selected]=='FILM:':
                        vumetermessage('Pasting film, please wait...')
                        paste = filmfolder+pastefilmname
                        os.system('cp -r ' + yanked + ' ' + paste)
                        try:
                            run_command('rsync -avr --update --progress --files-from='+yanked+'/.origin_videos --no-relative / ' +filmfolder+'.videos/')
                        except:
                            logger.info('no origin videos')
                        #if moving == True:
                            #os.system('rm -r ' + yanked)
                            #Remove hidden placeholder
                            #os.system('rm ' + yanked + '/.placeholder')
                    add_organize(filmfolder, filmname)
                    organize(filmfolder, filmname)
                    organize(filmfolder, filmname)
                    updatethumb = True
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    if scene > scenes:
                        scene = scenes
                    if shot > shots:
                        shot = shots
                    yanked = ''
                    copying = ''
                    moving = False
                    vumetermessage('Pasted!')
                    time.sleep(1)
                #INSERT SHOT
                elif pressed == 'insert' and menu[selected] != 'SCENE:' and yanked == '':
                    insertshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_insert'
                    try:
                        os.makedirs(insertshot)
                        run_command('touch ' + insertshot + '/.placeholder')
                    except:
                        print('is there already prob')
                    add_organize(filmfolder, filmname)
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    #vumetermessage('Shot ' + str(shot) + ' inserted')
                    updatethumb = True
                    time.sleep(1)
                #INSERT SHOT TO LAST SHOT
                elif pressed == 'insert_shot':
                    logger.info('inserting shot')
                    shot = countshots(filmname, filmfolder, scene)
                    shot=shot+1
                    insertshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_insert'
                    try:
                        os.makedirs(insertshot)
                        run_command('touch ' + insertshot + '/.placeholder')
                    except:
                        print('is there already prob')
                    add_organize(filmfolder, filmname)
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    #vumetermessage('Shot ' + str(shot) + ' inserted')
                    updatethumb = True
                #INSERT TAKE
                elif pressed == 'insert_take':
                    logger.info('inserting take')
                    insertshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                    try:
                        os.makedirs(insertshot)
                        run_command('touch ' + insertshot + '/.placeholder')
                    except:
                        print('is there already prob')
                    add_organize(filmfolder, filmname)
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    #vumetermessage('Take ' + str(shot) + ' inserted')
                    updatethumb = True
                    #time.sleep(1)
                #INSERT SCENE
                elif pressed == 'insert' and menu[selected] == 'SCENE:':
                    insertscene = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_insert'
                    logger.info("inserting scene")
                    try:
                        insertplaceholder = insertscene+'/.placeholder'
                        os.makedirs(insertplaceholder)
                        run_command('touch ' + insertscene + '/.placeholder')
                    except:
                        print('something scetchy!')
                    organize(filmfolder, filmname)
                    add_organize(filmfolder, filmname)
                    updatethumb = True
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    vumetermessage('Scene ' + str(scene) + ' inserted')
                    time.sleep(1)
                #NEW SCENE
                elif pressed == 'new_scene':
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    vumetermessage('got new scene')
                    scene=scenes+1
                    shot=1
                    take=1
                #DEVELOP
                elif event == 'D':
                    try:
                        camera = stopinterface(camera)
                        camera = stopcamera(camera, 'rec_process')
                        code.interact(local=locals())
                        startinterface()
                        camera = startcamera(camera)
                        loadfilmsetings = True
                    except:
                        writemessage('hmm.. couldnt enter developer mode')
                #TURN OFF SCREEN
                elif pressed == 'screen':
                    if backlight == False:
                        # requires wiringpi installed
                        run_command('gpio -g pwm 19 1023')
                        backlight = True
                        camera.start_preview()
                    elif backlight == True:
                        run_command('gpio -g pwm 19 0')
                        backlight = False
                        camera.stop_preview()
                elif pressed == 'showmenu':
                    if showmenu == 1:
                        # requires wiringpi installed
                        showmenu = 0
                        showmenu_settings = False
                    elif showmenu == 0:
                        showmenu = 1
                        showmenu_settings = True
                #DSK
                elif pressed == 'middle' and menu[selected] == 'DSK:':
                    print("usb filmfolder")
                    vumetermessage('checking usb mount...')
                    filmfolderusb=usbfilmfolder(dsk)
                    if filmfolderusb:
                        filmfolder=filmfolderusb
                        if dsk < 1:
                            storagedrives.append(['usb0',filmfolder])
                            dsk=1
                            loadfilmsettings = True
                        elif dsk > 0:
                            storagedrives.append(['usb1',filmfolder])
                            dsk=2
                            loadfilmsettings = True
                    else:
                        #camera_model, camera_revision, filmfolder = getconfig(camera)
                        if os.path.isdir(filmfolder) == False:
                            os.makedirs(filmfolder)
                    #COUNT DISKSPACE
                    #sudo mkfs -t ext4 /dev/sdb1
                    disk = os.statvfs(filmfolder)
                    diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
                    #LOAD FILM AND SCENE SETTINGS
                    try:
                        filmname = getfilms(filmfolder)[0][0]
                    except:
                        filmname = 'onthefloor' 
                    try:
                        filmname_back = getfilms(filmfolder)[0][1]
                    except:
                        filmname_back = 'onthefloor' 
                    if os.path.isdir(filmfolder) == False:
                        os.makedirs(filmfolder)
                    #loadfilmsettings = True
                    updatethumb = True
                    rendermenu = True
                    #cleanupdisk(filmname,filmfolder)
                    serverstate = gonzopiserver(False)
                    serverstate = gonzopiserver(True)
                #REMOVE DELETE
                #dsk
                elif pressed == 'remove' and menu[selected] == 'DSK:':
                    if dsk != 0:
                        print("usb filmfolder")
                        os.system('sudo pumount /media/usb'+str(dsk))
                        os.system('sudo umount -l /media/usb'+str(dsk))
                        try:
                            del storagedrives[dsk]
                        except:
                            pass
                        dsk=0
                        time.sleep(1)
                #take
                elif pressed == 'remove' and menu[selected] == 'TAKE:':
                    u = remove(filmfolder, filmname, scene, shot, take, 'take')
                    if u != False:
                        organize(filmfolder, filmname)
                        scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                        take = counttakes(filmname, filmfolder, scene, shot)
                        updatethumb = True
                        rendermenu = True
                        #loadfilmsettings = True
                        time.sleep(0.2)
                #shot
                elif pressed == 'remove' and menu[selected] == 'SHOT:':
                    u = remove(filmfolder, filmname, scene, shot, take, 'shot')
                    if u != False:
                        organize(filmfolder, filmname)
                        scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                        take = counttakes(filmname, filmfolder, scene, shot)
                        updatethumb = True
                        rendermenu = True
                        #loadfilmsettings = True
                        time.sleep(0.2)
                #scene
                elif pressed == 'remove' and menu[selected] == 'SCENE:' or pressed=='remove_now':
                    u = remove(filmfolder, filmname, scene, shot, take, 'scene')
                    if u != False:
                        organize(filmfolder, filmname)
                        scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                        shot = countshots(filmname, filmfolder, scene)
                        take = counttakes(filmname, filmfolder, scene, shot)
                        updatethumb = True
                        rendermenu = True
                        #loadfilmsettings = True
                        time.sleep(0.2)
                #film
                elif pressed == 'remove' and menu[selected] == 'FILM:':
                    u = remove(filmfolder, filmname, scene, shot, take, 'film')
                    if u != False:
                        try:
                            filmname = getfilms(filmfolder)[0][0]
                        except:
                            filmname = 'reel_001'
                            if os.path.isdir(filmfolder+filmname) == False:
                                os.makedirs(filmfolder+filmname)
                        else:
                            scene, shot, take = countlast(filmname, filmfolder)
                            loadfilmsettings = True
                            updatethumb = True
                            rendermenu = True
                        time.sleep(0.2)
                elif pressed == 'remove' and menu[selected] == 'CAMERA:':
                    if camselected != 0:
                        cameras.pop(camselected)
                        newselected=0
                elif pressed == 'remove' and menu[selected] == 'LIVE:':
                    udp_ip = ''
                    udp_port = ''
                    vumetermessage("udp ip address removed")
                    time.sleep(1)
                elif pressed == 'middle' and menu[selected] == 'Add CAMERA':
                    if networks != []:
                        newcamera = newcamera_ip(numbers_only, network)
                        if newcamera != '':
                            if newcamera not in cameras and newcamera not in networks:
                                sendtocamera(newcamera,port,'NEWFILM:'+filmname)
                                time.sleep(0.2)
                                sendtocamera(newcamera,port,'Q:'+str(quality))
                                time.sleep(0.2)
                                sendtocamera(newcamera,port,'SHOT:'+str(shot))
                                time.sleep(0.2)
                                sendtocamera(newcamera,port,'SCENE:'+str(scene))
                                time.sleep(0.2)
                                sendtocamera(newcamera,port,'MAKEPLACEHOLDERS:'+str(scenes)+'|'+str(shots))
                                cameras.append(newcamera)
                                rendermenu = True
                                #newselected=newselected+1
                                camera_recording=None
                                vumetermessage("New camera! "+newcamera)
                    else:
                        vumetermessage('No network!')
                elif 'SYNCIP:' in pressed:
                    msg = pressed.split(':')[1]
                    syncfolder=msg.split('|')[1]
                    ip = msg.split('|')[0]
                    synctime= ip.split(';')[1]
                    ip = ip.split(';')[0]
                    vumetermessage('SYNCING!')
                    time.sleep(int(synctime))
                    camera = stopinterface(camera)
                    camera = stopcamera(camera, 'rec_process')
                    video_files=shotfiles(filmfolder, filmname, scene)
                    for i in video_files:
                        compileshot(i,filmfolder,filmname)
                        logger.info('SYNCING:'+i)
                    organize(filmfolder, filmname)
                    if not os.path.isfile('/home/pi/.ssh/id_rsa'):
                        run_command('ssh-keygen')
                    run_command('ssh-copy-id pi@'+ip)
                    try:
                        run_command('rsync -avr --update --progress --files-from='+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/.origin_videos --no-relative / pi@'+ip+':'+syncfolder+'.videos/')
                    except:
                        logger.info('no origin videos')
                    #run_command('scp -r '+filmfolder+filmname+'/'+'scene'+str(scene).zfill(3)+' pi@'+ip+':'+filmfolder+filmname+'/')
                    received=False
                    while received != True:
                        received = sendtocamera(ip,port,'SYNCDONE:'+cameras[0]+'|'+filmfolder)
                        time.sleep(1)
                        logger.info('sending syncdone again...')
                    startinterface()
                    camera = startcamera(camera)
                    loadfilmsettings = True
                    rendermenu = True
                elif 'SYNCDONE:' in pressed:
                    msg = pressed.split(':')[1]
                    syncfolder=msg.split('|')[1]
                    ip = msg.split('|')[0]
                    sendtocamera(ip,port,'GOTSYNC:'+cameras[0]+'|'+filmfolder)
                    synclist.append(ip)
                    print(synclist)
                    #time.sleep(3)
                    if len(synclist) == len(cameras)-1:
                        for ip in synclist:
                            camera = stopinterface(camera)
                            camera = stopcamera(camera, 'rec_process')
                            logger.info('SYNCING from ip:'+ip)
                            run_command('ssh-copy-id pi@'+ip)
                            try:
                                run_command('rsync -avr --update --progress pi@'+ip+':'+syncfolder+filmname+'/scene'+str(scene).zfill(3)+'/ '+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/')
                            except:
                                logger.info('no files')
                            try:
                                with open(filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/.origin_videos', 'r') as f:
                                    if f:
                                        scene_origin_files = [line.rstrip() for line in f]
                            except:
                                logger.info('no files')
                            #a=0
                            #for i in cameras:
                            #    if a != 0:
                            #        run_command('rsync -avr --update --progress '+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/ pi@'+i+':'+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/')
                            #        time.sleep(3)
                            #    a=a+1
                            startinterface()
                            camera = startcamera(camera)
                            loadfilmsettings = True
                            rendermenu = True
                            vumetermessage('SYNC DONE!')
                elif 'RETAKE' in pressed:
                    pressed="retake"
                elif 'RETAKE:' in pressed:
                    shot=pressed.split(':')[1]
                    shot=int(shot)
                    retake = True
                    pressed="retake_now"
                elif 'SCENE:' in pressed:
                    scene=pressed.split(':')[1]
                    scene=int(scene)
                    shot = countshots(filmname, filmfolder, scene)
                    take = counttakes(filmname, filmfolder, scene, shot)
                elif 'SHOT:' in pressed:
                    shot=pressed.split(':')[1]
                    shot=int(shot)
                    take = counttakes(filmname, filmfolder, scene, shot)
                elif 'SHOTSCENES:' in pressed:
                    sceneshot=pressed.split(':')[1]
                    scene=sceneshot.split('|')[0].split('#')[0]
                    scene=int(scene)
                    shot=sceneshot.split('|')[1].split('#')[0]
                    shot=int(shot)
                    filmname = sceneshot.split('|')[1].split('#')[1]
                    take = counttakes(filmname, filmfolder, scene, shot)
                elif 'REMOVE:' in pressed:
                    scene=pressed.split(':')[1]
                    scene=int(scene)
                    shot = countshots(filmname, filmfolder, scene)
                    take = counttakes(filmname, filmfolder, scene, shot)
                    pressagain='remove_now'
                elif 'Q:' in pressed:
                    qual=pressed.split(':')[1]
                    quality=int(qual)
                    vumetermessage('Quality changed to '+str(quality))
                elif 'CAMERA:' in pressed:
                    newselected_maybe=int(pressed.split(':')[1])
                    if len(cameras) > newselected_maybe:
                        newselected=newselected_maybe
                elif 'MAKEPLACEHOLDERS:' in pressed:
                    scenesshots=pressed.split(':')[1]
                    pscene=int(scenesshots.split('|')[0])
                    pshots=int(scenesshots.split('|')[1])
                    #to not throw away empty shots, make placeholders
                    for i in range(pshots):
                        placeholders=filmfolder + filmname + '/scene' +  str(pscene).zfill(3) + '/shot' + str(i+1).zfill(3)
                        try:
                            os.makedirs(placeholders)
                        except:
                            logger.info('scene or shot already there!')
                        run_command('touch ' + placeholders + '/.placeholder')
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take) 
                    rendermenu = True
                    vumetermessage('CONNECTED TO MASTER TARINA!')
            #SHOWTARINACTRL
            if recordwithports: 
                if pressed == 'middle' and menu[selected] == "New FILM":
                    newfilmname = nameyourfilm(filmfolder, filmname, abc, True)
                    a=0
                    for i in cameras:
                        if i not in camerasoff:
                            sendtocamera(i,port,'NEWFILM:'+newfilmname)
                        a=a+1
                elif pressed == "retake":
                    a=0
                    for i in cameras:
                        if i not in camerasoff:
                            if a == camselected:
                                if camera_recording == a:
                                    if a==0:
                                        if recording == True:
                                            pressed="retake_now"
                                            retake = True
                                            camera_recording=None
                                    else:
                                        sendtocamera(i,port,'STOPRETAKE')
                                    camera_recording=None
                                else:
                                    if a==0:
                                        if recording == False:
                                            pressed="retake_now"
                                            retake = True
                                            camera_recording=0
                                    else:
                                        sendtocamera(i,port,'RETAKE:'+str(shot))
                                        camera_recording=camselected
                            else:
                                if a==0:
                                    pressagain='insert_take'
                                else:
                                    sendtocamera(i,port,'TAKEPLACEHOLDER')
                            a=a+1
                elif pressed == "middle" and menu[selected]=="Sync SCENE":
                    n=1
                    for i in cameras:
                        if i != cameras[0]:
                            vumetermessage('Hold on syncing!')
                            sendtocamera(i,port,'SYNCIP:'+cameras[0]+';'+str(n)+'|'+filmfolder)
                            synclist=[]
                            n=n+1
                            #time.sleep(1)
                elif pressed == "middle" and menu[selected]=='New SCENE':
                    a=0
                    for i in cameras:
                        if i not in camerasoff:
                            if a==0:
                                pressagain="new_scene"
                            else:
                                sendtocamera(i,port,'NEWSCENE')
                        a=a+1
                elif pressed == "record" and camera_recording != None:
                    if camera_recording == 0:
                        if recording == True:
                            pressed='record_now'
                    else:
                        sendtocamera(cameras[camera_recording],port,'STOP')
                    camera_recording=None
                elif pressed == "record" and camera_recording == None:
                    a=0
                    for i in cameras:
                        if i not in camerasoff:
                            if a == camselected:
                                if camselected==0:
                                    pressed='record_now'
                                else:
                                    sendtocamera(i,port,'REC')
                                camera_recording=camselected
                            else:
                                if a==0:
                                    pressagain='insert_shot'
                                else:
                                    sendtocamera(i,port,'PLACEHOLDER')
                            a=a+1
                elif pressed == "remove" and menu[selected]=='SCENE:':
                    a=0
                    for i in cameras:
                        if a!=0:
                            sendtocamera(i,port,'REMOVE:'+str(scene))
                        a=a+1
                elif pressed == "up" and menu[selected]=='SCENE:':
                    a=0
                    for i in cameras:
                        if a!=0:
                            sendtocamera(i,port,'SCENE:'+str(scene+1))
                        a=a+1
                elif pressed == "down" and menu[selected]=='SCENE:':
                    a=0
                    for i in cameras:
                        if a!=0:
                            sendtocamera(i,port,'SCENE:'+str(scene-1))
                        a=a+1
                elif pressed == "up" and menu[selected]=='SHOT:':
                    a=0
                    for i in cameras:
                        if a!=0:
                            sendtocamera(i,port,'SHOT:'+str(shot+1))
                        a=a+1
                elif pressed == "down" and menu[selected]=='SHOT:':
                    a=0
                    for i in cameras:
                        if a!=0:
                            sendtocamera(i,port,'SHOT:'+str(shot-1))
                        a=a+1
                elif pressed == "up" and menu[selected]=='Q:':
                    a=0
                    for i in cameras:
                        if a!=0:
                            sendtocamera(i,port,'Q:'+str(quality+1))
                        a=a+1
                elif pressed == "down" and menu[selected]=='Q:':
                    a=0
                    for i in cameras:
                        if a!=0:
                            sendtocamera(i,port,'Q:'+str(quality-1))
                        a=a+1
                elif event == "0":
                    newselected = 0
                elif event == "1":
                    if len(cameras) > 0:
                        newselected = 0
                elif event == "2":
                    if len(cameras) > 1:
                        newselected = 1
                elif event == "3":
                    if len(cameras) > 2:
                        newselected = 2
                elif event == "4":
                    if len(cameras) > 3:
                        newselected = 3
                elif event == "5":
                    if len(cameras) > 4:
                        newselected = 4
                elif event == "6":
                    if len(cameras) > 5:
                        newselected = 5
                elif event == "7":
                    if len(cameras) > 6:
                        newselected = 6
                elif event == "8":
                    if len(cameras) > 7:
                        newselected = 7
                elif event == "9":
                    if len(cameras) > 8:
                        newselected = 8
                elif event == "-":
                    if cameras[camselected] not in camerasoff:
                        camerasoff.append(cameras[camselected])
                elif event == "+":
                    if cameras[camselected] in camerasoff:
                        camerasoff.remove(cameras[camselected])
                elif camselected != newselected:
                    if camera_recording != None:
                        #change camera
                        a=0
                        for c in cameras:
                            if c not in camerasoff:
                                if a == camselected:
                                    if a == 0:
                                        #pressed='record_now'
                                        #pressagain='insert_shot'
                                        delayedstop=c
                                    else:
                                        #sendtocamera(c,port,'STOP')
                                        #time.sleep(sleep)
                                        #sendtocamera(c,port,'PLACEHOLDER')
                                        delayedstop=c
                                elif a == newselected:
                                    if a == 0:
                                        if recording == False:
                                            pressed='record_now'
                                    else:
                                        sendtocamera(c,port,'REC')
                                    camera_recording=newselected
                                else:
                                    if a == 0:
                                        pressagain='insert_shot'
                                    else:
                                        sendtocamera(c,port,'PLACEHOLDER')
                                    #time.sleep(2)
                                a=a+1
                        if delayedstop:
                            time.sleep(0.05)
                            if delayedstop==cameras[0]:
                                if recording == True:
                                    pressed='record_now'
                                pressagain='insert_shot'
                            else:
                                sendtocamera(delayedstop,port,'STOP')
                                time.sleep(sleep)
                                sendtocamera(delayedstop,port,'PLACEHOLDER')
                    camselected=newselected
                    rendermenu = True
                    #vumetermessage('filming with '+camera_model +' ip:'+ network + ' '+camerasconnected+' camselected:'+str(camselected))
                    if len(cameras) > 0:
                        if camera_recording:
                            vumetermessage('filming with '+camera_model +' ip:'+ cameras[camselected] + ' '+camerasconnected+' camselected:'+str(camselected+1)+' rec:'+str(camera_recording+1))
                        else:
                            vumetermessage('filming with '+camera_model +' ip:'+ cameras[camselected] + ' '+camerasconnected+' camselected:'+str(camselected+1)+' rec:'+str(camera_recording))
                    else:
                        vumetermessage('filming with '+camera_model +' ip:'+ network)

            #RECORD AND PAUSE
            if beepcountdown > 1:
                if time.time() - lastbeep  > 1:
                    beep(bus)
                    beepcountdown -= 1
                    lastbeep = time.time()
                    logger.info('beepcountdown: ' + str(beepcountdown))
                    vumetermessage('Filming in ' + str(beepcountdown) + ' seconds, press record again to cancel       ')
            elif beepcountdown > 0:
                if time.time() - float(lastbeep) > 0.1:
                    beep(bus)
                    vumetermessage('Get ready!!')
                if time.time() - lastbeep > 1:
                    longbeep(bus)
                    beepcountdown = 0
                    if recordwithports == True:
                        if retake == True:
                            pressed = 'retake_now'
                            retake = False
                        else:
                            pressed = 'record_now'
                    else:
                        pressed = 'retake_now'
                    print('exhausted from all beepings')
            elif 'CAMERA:' in pressed:
                newselected_maybe=int(pressed.split(':')[1])
                if len(cameras) > newselected_maybe:
                    newselected=newselected_maybe
            if pressed == 'record' and recordwithports==False or pressed == 'record_now' or pressed == 'retake_now' or pressed == 'retake' and recordwithports==False or reclength != 0 and t > reclength:
                overlay = removeimage(camera, overlay)
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                filename = 'take' + str(take).zfill(3)
                picturename = 'picture' + str(take).zfill(3)
                recordable = not os.path.isfile(foldername + filename + '.mp4') and not os.path.isfile(foldername + filename + '.h264') and not os.path.isfile(foldername + picturename + '.jpeg')
                if recording == False and recordable == True or recording == False and pressed == 'record_now' or recording == False and pressed == 'retake_now':
                    #calculate ratio
                    syncratio=0.9998
                    if int(round(fps)) != int(film_fps):
                        syncratio=24.989/fps-((1.0-syncratio)/24.989*fps)
                        #syncratio=24.989/fps-((1.0-syncratio)/24.989*fps)
                        #syncratio=25/fps
                    #print('fuuuuuuuuuuu: '+str(syncratio))
                    #time.sleep(5)
                    #check if dub and play it
                    if playdubrecord == True:
                        playdubrecfile=filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)+'/dub/dub001.wav'
                    if os.path.exists(playdubrecfile) == True and playdubonrec == False and playdubrecord == True:
                        writemessage('Loading scene...')
                        organize(filmfolder, filmname)
                        filmfiles = shotfiles(filmfolder, filmname, scene)
                        vumetermessage('press middlebutton to cancel')
                        playonrec_start = 0
                        if len(filmfiles) > 0:
                            renderfilm(filmfolder, filmname, comp, scene)
                        try:
                            playerAudio = OMXPlayer(playdubrecfile, args=['--adev','alsa:hw:'+str(plughw), '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer2', pause=True)
                            playdubonrec = True
                        except:
                            writemessage('something wrong with play dub on rec audio player')
                            playdubonrec = False
                        playdubonrec_start=get_video_length(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)+'/scene.mp4')/1000
                        dublength=get_video_length(playdubrecfile)
                        #if playonrec_start > dublength:
                        #    playdubonrec = False
                        #else:
                        #    playdubonrec = True
                    #camera_recording=0 
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take) 
                    if pressed == "record":
                        if takes > 0:
                            shot = shots+1
                            take = 1
                            takes=1
                            shots=shots+1
                        else:
                            take = 1
                            takes=1
                    elif pressed == "retake" and takes > 0:
                        takes = counttakes(filmname, filmfolder, scene, shot)
                        take = takes+1
                        takes=take
                    elif pressed == "retake" and takes == 0:
                        if shot > 1:
                            shot = shot - 1
                        takes = counttakes(filmname, filmfolder, scene, shot)
                        take = takes+1
                        takes=take
                        #take=1
                        #takes=1
                    elif pressed == 'record_now':
                        shot=shots+1
                        take=1
                        takes=1
                        shots=shots+1
                    elif pressed == 'retake_now':
                        takes = counttakes(filmname, filmfolder, scene, shot)
                        take = takes + 1
                        takes=take
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    if beeps > 0 and beeping == False:
                        beeping = True
                        beepcountdown = beeps
                    elif beepcountdown == 0:
                        beeping = False
                        if os.path.isdir(foldername) == False:
                            os.makedirs(foldername)
                        if cammode == 'film':
                            #if recandslide here
                            if slidecommander:
                                send_serial_port(slidecommander,';'+str(slide))
                            videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                            tot = int(videos_totalt.videos)
                            video_origins=datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                            try:
                                db.insert('videos', tid=datetime.datetime.now(), filename=filmfolder+'.videos/'+video_origins+'.mp4', foldername=foldername, filmname=filmname, scene=scene, shot=shot, take=take, audiolength=0, videolength=0)
                            except:
                                db=correct_database(filmname,filmfolder,db)
                                db.insert('videos', tid=datetime.datetime.now(), filename=filmfolder+'.videos/'+video_origins+'.mp4', foldername=foldername, filmname=filmname, scene=scene, shot=shot, take=take, audiolength=0, videolength=0)
                            #check if there's a dub and no
                            if playdubonrec == True:
                                if playdubonrec_start > 3:
                                    playerAudio.play()
                                    playerAudio.set_position(playdubonrec_start - 3)
                                    vumetermessage('Geat Ready in 3...')
                                    time.sleep(1)
                                    vumetermessage('Geat Ready in 2...')
                                    time.sleep(1)
                                    vumetermessage('Geat Ready in 1...')
                                    time.sleep(0.5)
                                    vumetermessage('Go!')
                                    time.sleep(0.5)
                                else:
                                    playerAudio.play()
                                    playerAudio.set_position(playdubonrec_start)
                            #os.system(gonzopifolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:' + str(plughw) + ' -f '+soundformat+' -c ' + str(channels) + ' -r '+soundrate+' -vv '+filmfolder+ '.videos/'+video_origins+'.wav &')
                            #START RECORDING AUDIO AND FINETUNE IT FOR PICAMERA CLOCK

                            os.system(gonzopifolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:' + str(plughw) + ' -f '+soundformat+' -c ' + str(channels) + ' -r '+soundrate+' -vv - | sox -t raw -r '+soundrate+' -c '+str(channels)+' -b 16 -e signed - -t wav '+filmfolder+ '.videos/'+video_origins+'.wav speed '+str(syncratio)+' &') #magic number is 0.9998, if sound lags behind reduce with 0.0001 or even finer
                            sound_start = time.time()
                            if onlysound != True:
                                #camera.start_recording(filmfolder+ '.videos/'+video_origins+'.h264', format='h264', bitrate = bitrate, level=profilelevel, quality=quality, intra_period=1)
                                rec_process, camera=startrecording(camera, filmfolder+ '.videos/'+video_origins+'.mp4',bitrate, quality, profilelevel, reclength)
                                starttime = time.time()
                                soundlag=sound_start-starttime

                            os.system('ln -sfr '+filmfolder+'.videos/'+video_origins+'.mp4 '+foldername+filename+'.mp4')
                            os.system('ln -sfr '+filmfolder+'.videos/'+video_origins+'.wav '+foldername+filename+'.wav')
                            recording = True
                            showmenu = 0
                            with open(foldername+filename+'.nofaststart', 'w') as f:
                                f.write(str(int((time.time() - starttime)*1000)))
                        if cammode == 'picture':
                            #picdate=datetime.datetime.now().strftime('%Y%d%m')
                            picture = foldername +'picture' + str(take).zfill(3) + '.jpeg'
                            print('taking picture')
                            camera.capture(picture,format="jpeg",use_video_port=True) 
                            #run_command('touch ' + foldername + 'take' + str(take).zfill(3) + '.mp4')
                            basewidth = 800
                            img = Image.open(picture)
                            wpercent = (basewidth/float(img.size[0]))
                            hsize = int((float(img.size[1])*float(wpercent)))
                            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                            img.save(foldername+'take'+str(take).zfill(3) + '.jpeg')
                            basewidth = 80
                            wpercent = (basewidth/float(img.size[0]))
                            hsize = int((float(img.size[1])*float(wpercent)))
                            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                            img.save(foldername+'take'+str(take).zfill(3) + '_thumb.jpeg')
                            vumetermessage('Great Pic taken!!')
                            updatethumb = True
                    elif beepcountdown > 0 and beeping == True:
                        beeping = False
                        beepcountdown = 0
                        vumetermessage('Filming was canceled!!')
                elif recording == True and float(time.time() - starttime) > 0.2:
                    #print(term.clear+term.home)
                    disk = os.statvfs(filmfolder)
                    diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
                    recording = False
                    if showmenu_settings == True:
                        showmenu = 1
                    if onlysound != True:
                        #camera.stop_recording()
                        recprocess, camera = stoprecording(camera, rec_process,bitrate, quality, profilelevel)
                    os.system('pkill arecord')
                    try:
                        db.update('videos', where='filename="'+filmfolder+'.videos/'+video_origins+'.mp4"', soundlag=soundlag, videolength=float(time.time() - starttime), faststart=False)
                    except:
                        db = correct_database(filmname,filmfolder,db)
                        db.update('videos', where='filename="'+filmfolder+'.videos/'+video_origins+'.mp4"', soundlag=soundlag, videolength=float(time.time() - starttime), faststart=False)
                    #time.sleep(0.005) #get audio at least 0.1 longer
                    #camera.capture(foldername + filename + '.jpeg', resize=(800,341))
                    #if slidecommander:
                    #send_serial_port(slidecommander,'<')
                    if onlysound != True:
                        try:
                            #camera.capture(foldername + filename + '.jpeg', resize=(800,340), use_video_port=True)
                            if film_reso == '1920x1080':
                                camera.capture(foldername + filename + '.jpeg', resize=(800,450), use_video_port=True)
                            elif film_reso == '1920x816':
                                camera.capture(foldername + filename + '.jpeg', resize=(800,340), use_video_port=True)
                            basewidth = 80
                            img = Image.open(foldername + filename + '.jpeg')
                            wpercent = (basewidth/float(img.size[0]))
                            hsize = int((float(img.size[1])*float(wpercent)))
                            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                            img.save(foldername+filename + '_thumb.jpeg')
                            updatethumb = True
                        except:
                            logger.warning('something wrong with camera jpeg capture')
                    if playdubonrec == True:
                        playerAudio.pause()
                        playerAudio.quit()
                        playdubonrec=False
                    #delayerr = audiotrim(foldername,filename)
                    onlysound = False
                    if beeps > 0:
                        if bus:
                            buzz(300)
                        else:
                            run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep.wav')
                    #if int(round(fps)) != int(film_fps):
                    #    compileshot(foldername + filename,filmfolder,filmname)
                    #os.system('cp /dev/shm/' + filename + '.wav ' + foldername + filename + '.wav')
                    if beeps > 0:
                        if bus:
                            buzz(150)
                        else:
                            run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep.wav')
                    t = 0
                    rectime = ''
                    vumetermessage('Gonzo Pi v.' + gonzopiversion[:-1] + ' ' + gonzopivername[:-1])
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    if shot == shots and pressed == 'record':
                        shot=shots+1
                        take=1
                        takes=0
                    elif pressed == 'retake':
                        take=takes+1
                        #updatethumb = True
                        #camera_recording=0
                #if not in last shot or take then go to it
                if pressed == 'record' and recordable == False:
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    shot=shots+1
                    take=1
                    takes=0
                    #take = takes
                    #takes = counttakes(filmname, filmfolder, scene, shot)
                if pressed == 'retake' and recordable == False:
                    #scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    #take = takes
                    #takes = counttakes(filmname, filmfolder, scene, shot)
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    take = takes + 1
            #ENTER (auto shutter, iso, awb on/off)
            elif pressed == 'middle' and menu[selected] == 'SHUTTER:':
                if camera.shutter_speed == 0:
                    camera.shutter_speed = camera.exposure_speed
                else:
                    camera.shutter_speed = 0
            elif pressed == 'middle' and menu[selected] == 'ISO:':
                if camera.iso == 0:
                    camera.iso = 100
                else:
                    camera.iso = 0
            elif pressed == 'middle' and menu[selected] == 'RED:':
                if camera.awb_mode == 'auto':
                    camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]))
                    camera.awb_mode = 'off'
                else:
                    camera.awb_mode = 'auto'
            elif pressed == 'middle' and menu[selected] == 'BLUE:':
                if camera.awb_mode == 'auto':
                    camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]))
                    camera.awb_mode = 'off'
                else:
                    camera.awb_mode = 'auto'
            elif pressed == 'middle' and menu[selected] == 'BEEP:':
                beeps = 0
            elif pressed == 'middle' and menu[selected] == 'LENGTH:':
                reclength = 0
            elif pressed == 'middle' and menu[selected] == 'LIVE:':
                if stream == '':
                    if udp_ip == '':
                        udp_ip, udp_port = newudp_ip(numbers_only, network)
                        rendermenu = True
                    stream = startstream(camera, stream, plughw, channels,network,udp_ip,udp_port,bitrate)
                    if stream == '':
                        vumetermessage('something wrong with streaming')
                    else:
                        live = 'yes'
                else:
                    stream = stopstream(camera, stream)
                    live = 'no'
            elif pressed == 'middle' and menu[selected] == 'SLIDE:':
                slide_menu(slidecommander)
                rendermenu = True
            elif pressed == 'middle' and menu[selected] == 'BRIGHT:':
                camera.brightness = 50
            elif pressed == 'middle' and menu[selected] == 'CONT:':
                if yanked == '':
                    camera.contrast = 0
                else:
                    videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                    tot = int(videos_totalt.videos)
                    video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                    newtake = nexttakefilename(filmname, filmfolder, scene, shot)
                    #why didnt i do this earlier cuz copy paste & that works too
                    vumetermessage('applying effect...')
                    run_command('ffmpeg -i '+yanked+'.mp4 -vf "eq=contrast='+str(1.0+(int(camera.contrast)/100))+'" -c:v copy -c:a copy -y '+encoder()+video_origins+'.mp4')
                    os.system('ln -sfr '+filmfolder+'.videos/'+video_origins+'.mp4 '+newtake+'.mp4')
                    vumetermessage('done!')
                    yanked=''
                    scenes, shots, takes = countlast(filmname, filmfolder)
                    take=takes
            elif pressed == 'middle' and menu[selected] == 'SAT:':
                camera.saturation = 0
            elif pressed == 'middle' and menu[selected] == 'MIC:':
                miclevel  = 70
            elif pressed == 'middle' and menu[selected] == 'PHONES:':
                headphoneslevel = 70
            elif pressed == 'middle' and menu[selected] == 'SRV:':
                if showgonzopictrl == False:
                    menu=gonzopictrlmenu
                    #selected=0
                    showgonzopictrl = True
                else:
                    menu=standardmenu
                    showgonzopictrl=False
            elif pressed == 'middle' and menu[selected] == 'Q:':
                bitrate = get_bitrate(numbers_only, bitrate)
                newbitrate = int(bitrate*1000)
                bitrate = int(bitrate*1000)
                camera = stopcamera(camera, rec_process)
                camera = startcamera(camera)
                vumetermessage('Bitrate set to ' + str(int(newbitrate/1000))+ ' kbits/s')
                time.sleep(2)
                #print('saving settings')
                loadfilmsettings = True
                rendermenu = True
            elif pressed == 'middle' and menu[selected] == 'VFX:':
                if effects[effectselected] == 'colorpoint':
                    vfx_colorpoint()
                if effects[effectselected] == 'solarize':
                    vfx_solarize()

            #UP
            elif pressed == 'up':
                if menu[selected] == 'FILM:':
                    camera, newfilmname = loadfilm(filmname, filmfolder, camera, overlay)
                    allfilm = getfilms(filmfolder)
                    filmname_exist=False
                    for i in allfilm:
                        if i[0] == newfilmname:
                            filmname_exist=True
                    if filmname != newfilmname and filmname_exist==False:
                        filmname = newfilmname
                        os.makedirs(filmfolder + filmname)
                        vumetermessage('Good luck with your film ' + filmname + '!')
                        #make a filmhash
                        print('making filmhash...')
                        filmhash = shortuuid.uuid()
                        with open(filmfolder + filmname + '/.filmhash', 'w') as f:
                            f.write(filmhash)
                        updatethumb = True
                        rendermenu = True
                        scene = 1
                        shot = 1
                        take = 1
                        #selectedaction = 0
                        newfilmname = ''
                    else:
                        filmname = newfilmname
                        newfilmname = ''
                        vumetermessage('film already exist!')
                        logger.info('film already exist!')
                        print(term.clear)
                        updatethumb = True
                        rendermenu = True
                        loadfilmsettings = True
                elif menu[selected] == 'BRIGHT:':
                    camera.brightness = min(camera.brightness + 1, 99)
                elif menu[selected] == 'CONT:':
                    camera.contrast = min(camera.contrast + 1, 99)
                elif menu[selected] == 'SAT:':
                    camera.saturation = min(camera.saturation + 1, 99)
                elif menu[selected] == 'VFX:':
                    if effectselected < len(effects) - 1:
                        effectselected += 1
                        camera.image_effect = effects[effectselected]
                    else:
                        effectselected = 0
                        camera.image_effect = effects[effectselected]
                elif menu[selected] == 'BLEND:':
                    if blendselect < len(blendmodes) - 1:
                        blendselect += 1
                    else:
                        blendselect=0
                elif menu[selected] == 'SHUTTER:':
                    if camera.shutter_speed == 0:
                        camera.shutter_speed = camera.exposure_speed
                    if camera.shutter_speed < 5000:
                        camera.shutter_speed = min(camera.shutter_speed + 50, 50000)
                    else:
                        camera.shutter_speed = min(camera.shutter_speed + 200, 50000)
                elif menu[selected] == 'ISO:':
                    camera.iso = min(camera.iso + 100, 1600)
                elif menu[selected] == 'BEEP:':
                    beeps = beeps + 1
                elif menu[selected] == 'FLIP:':
                    if flip == 'yes':
                        camera.hflip = False
                        camera.vflip = False
                        flip = 'no'
                        time.sleep(0.2)
                    else:
                        camera.hflip = True
                        camera.vflip = True
                        flip = 'yes'
                        time.sleep(0.2)
                elif menu[selected] == 'HDMI:':
                    if hdmi == 'on':
                        hdmi = 'off'
                        os.system("sudo sed -i '/\[edid=Ras-LCD Panel\]/c\#\[edid=Ras-LCD Panel\]' /boot/config.txt")
                        os.system("sudo sed -i '/\#\[edid=HDMI-A-2\]/c\[edid=HDMI-A-2\]' /boot/config.txt")
                        time.sleep(0.2)
                    else:
                        hdmi = 'on'
                        os.system("sudo sed -i '/\#\[edid=Ras-LCD Panel\]/c\[edid=Ras-LCD Panel\]' /boot/config.txt")
                        os.system("sudo sed -i '/\[edid=HDMI-A-2\]/c\#\[edid=HDMI-A-2\]' /boot/config.txt")
                        time.sleep(0.2)
                elif menu[selected] == 'LENGTH:':
                    if reclength < 1:
                        reclength = reclength + 0.2
                    else:
                        reclength = int(reclength + 1)
                    time.sleep(0.1)
                elif menu[selected] == 'MIC:':
                    if miclevel < 100:
                        miclevel = miclevel + 2
                        run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
                elif menu[selected] == 'PHONES:':
                    if headphoneslevel < 100:
                        headphoneslevel = headphoneslevel + 2
                        run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
                elif menu[selected] == 'SCENE:' and recording == False:
                    if scene <= scenes:
                        scene += 1
                        #shot = countshots(filmname, filmfolder, scene)
                        shot = 1
                    else:
                        scene = 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                    #scene, shots, takes = browse2(filmname, filmfolder, scene, shot, take, 0, 1)
                    #shot = 1
                elif menu[selected] == 'SHOT:' and recording == False:
                    if shot <= shots:
                        shot += 1
                    else:
                        shot=1
                    take = counttakes(filmname, filmfolder, scene, shot)
                    #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, 1)
                    #takes = take
                elif menu[selected] == 'TAKE:' and recording == False:
                    if take <= takes:
                        take += 1
                    else:
                        take=0
                    #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, 1)
                elif menu[selected] == 'RED:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[0]) < 7.98:
                        camera.awb_gains = (round(camera.awb_gains[0],2) + 0.02, round(camera.awb_gains[1],2))
                elif menu[selected] == 'BLUE:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[1]) < 7.98:
                        camera.awb_gains = (round(camera.awb_gains[0],2), round(camera.awb_gains[1],2) + 0.02)
                elif menu[selected] == 'SRV:':
                    if serverstate == 'on':
                        try:
                            os.makedirs(gonzopifolder+'/srv/sessions')
                            os.system('chown www-data '+gonzopifolder+'/srv/sessions')
                        except:
                            print('srv folder exist')
                        serverstate = 'false'
                        serverstate = gonzopiserver(False)
                    elif serverstate == 'off':
                        serverstate = 'on'
                        serverstate = gonzopiserver(True)
                elif menu[selected] == 'WIFI:':
                    if wifistate == 'on':
                        run_command('sudo iwconfig wlan0 txpower off')
                        wifistate = 'off'
                    elif wifistate == 'off':
                        run_command('sudo iwconfig wlan0 txpower auto')
                        wifistate = 'on'
                elif menu[selected] == 'SEARCH:':
                    if searchforcameras == 'on':
                        searchforcameras = 'off'
                    elif searchforcameras == 'off':
                        searchforcameras = 'on'
                elif menu[selected] == 'MODE:':
                    if cammode == 'film':
                        cammode = 'picture'
                        vumetermessage('changing to picture mode')
                    elif cammode == 'picture':
                        cammode = 'film'
                        vumetermessage('changing to film mode')
                    camera = stopcamera(camera, rec_process)
                    camera = startcamera(camera)
                    loadfilmsettings = True
                    flushbutton()
                elif menu[selected] == 'LENS:':
                    s = 0
                    for a in lenses:
                        if a == lens:
                            selectlens = s
                        s += 1
                    if selectlens < len(lenses) - 1:
                        selectlens += 1
                    lens = os.listdir('lenses/')[selectlens]
                    #npzfile = np.load('lenses/' + lens)
                    #lensshade = npzfile['lens_shading_table']
                    table = read_table('lenses/' + lens)
                    camera.lens_shading_table = table
                elif menu[selected] == 'COMP:':
                    if comp < 1:
                        comp += 1
                elif menu[selected] == 'HW:':
                    if plughw < len(getaudiocards())-1:
                        plughw += 1
                    vumetermessage(getaudiocards()[plughw])
                elif menu[selected] == 'CH:':
                    if channels == 1:
                        channels = 2
                elif menu[selected] == 'FPS:':
                    if fps_selected < len(fps_selection)-1:
                        fps_selected+=1
                        fps=fps_selection[fps_selected]
                        camera = stopcamera_preview(camera)
                        camera.framerate = fps 
                        camera = startcamera_preview(camera)
                elif menu[selected] == 'Q:':
                    if quality < 39:
                        quality += 1
                elif menu[selected] == 'CAMERA:':
                    if camselected < len(cameras)-1:
                        newselected = camselected+1
                        logger.info('camera selected:'+str(camselected))
                elif menu[selected] == 'SLIDE:':
                    if slidecommander:
                        #send_serial_port(slidecommander,'>')
                        slide += 1
                elif menu[selected] == 'DSK:':
                    if dsk+1 < len(storagedrives):
                        dsk += 1
                        filmfolder = storagedrives[dsk][1]
                        loadfilmsettings = True
                        #COUNT DISKSPACE
                        disk = os.statvfs(filmfolder)
                        diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
                        #LOAD FILM AND SCENE SETTINGS
                        try:
                            filmname = getfilms(filmfolder)[0][0]
                        except:
                            filmname = filmname 
                        try:
                            filmname_back = getfilms(filmfolder)[0][1]
                        except:
                            filmname_back = filmname
                        if serverstate == 'on':
                            gonzopiserver(False)
                            gonzopiserver(True)
                elif menu[selected] == 'MUX:':
                    if muxing == False:
                        muxing=True
                        mux='yes'
                    else:
                        muxing=False
                        mux='no'

            #LEFT
            elif pressed == 'left':
                if selected > 0:
                    selected = selected - 1
                else:
                    selected = len(menu) - 1
                if selected == 5:
                    selected = 4
            #DOWN
            elif pressed == 'down':
                if menu[selected] == 'FILM:':
                    camera, newfilmname = loadfilm(filmname, filmfolder, camera, overlay)
                    allfilm = getfilms(filmfolder)
                    filmname_exist=False
                    for i in allfilm:
                        if i[0] == newfilmname:
                            filmname_exist=True
                    if filmname != newfilmname and filmname_exist==False:
                        filmname = newfilmname
                        os.makedirs(filmfolder + filmname)
                        vumetermessage('Good luck with your film ' + filmname + '!')
                        #make a filmhash
                        print('making filmhash...')
                        filmhash = shortuuid.uuid()
                        with open(filmfolder + filmname + '/.filmhash', 'w') as f:
                            f.write(filmhash)
                        updatethumb = True
                        rendermenu = True
                        scene = 1
                        shot = 1
                        take = 1
                        #selectedaction = 0
                        newfilmname = ''
                    else:
                        filmname = newfilmname
                        newfilmname = ''
                        vumetermessage('film already exist!')
                        logger.info('film already exist!')
                        print(term.clear)
                        updatethumb = True
                        rendermenu = True
                        loadfilmsettings = True
                elif menu[selected] == 'BRIGHT:':
                    camera.brightness = max(camera.brightness - 1, 0)
                elif menu[selected] == 'CONT:':
                    camera.contrast = max(camera.contrast - 1, -100)
                elif menu[selected] == 'SAT:':
                    camera.saturation = max(camera.saturation - 1, -100)
                elif menu[selected] == 'VFX:':
                    if effectselected > 0:
                        effectselected -= 1
                        camera.image_effect = effects[effectselected]
                    else:
                        effectselected = len(effects)-1
                        camera.image_effect = effects[effectselected]
                elif menu[selected] == 'BLEND:':
                    if blendselect > 0:
                        blendselect -= 1
                    else:
                        blendselect = len(blendmodes)-1
                elif menu[selected] == 'SHUTTER:':
                    if camera.shutter_speed == 0:
                        camera.shutter_speed = camera.exposure_speed
                    if camera.shutter_speed < 5000:
                        camera.shutter_speed = max(camera.shutter_speed - 50, 20)
                    else:
                        camera.shutter_speed = max(camera.shutter_speed - 200, 200)
                elif menu[selected] == 'ISO:':
                    camera.iso = max(camera.iso - 100, 100)
                elif menu[selected] == 'BEEP:':
                    if beeps > 0:
                        beeps = beeps - 1
                elif menu[selected] == 'HDMI:':
                    if hdmi == 'on':
                        hdmi = 'off'
                        os.system("sudo sed -i '/\[edid=Ras-LCD Panel\]/c\#\[edid=Ras-LCD Panel\]' /boot/config.txt")
                        os.system("sudo sed -i '/\#\[edid=HDMI-A-2\]/c\[edid=HDMI-A-2\]' /boot/config.txt")
                        time.sleep(0.2)
                    else:
                        hdmi = 'on'
                        os.system("sudo sed -i '/\#\[edid=Ras-LCD Panel\]/c\[edid=Ras-LCD Panel\]' /boot/config.txt")
                        os.system("sudo sed -i '/\[edid=HDMI-A-2\]/c\#\[edid=HDMI-A-2\]' /boot/config.txt")
                        time.sleep(0.2)
                elif menu[selected] == 'FLIP:':
                    if flip == 'yes':
                        camera.hflip = False
                        camera.vflip = False
                        flip = 'no'
                        time.sleep(0.2)
                    else:
                        camera.hflip = True
                        camera.vflip = True
                        flip = 'yes'
                        time.sleep(0.2)
                elif menu[selected] == 'LENGTH:':
                    if reclength > 1:
                        reclength = int(reclength - 1)
                        time.sleep(0.1)
                    elif reclength > 0.3:
                        reclength = reclength - 0.2
                        time.sleep(0.1)
                    else:
                        reclength = 0
                elif menu[selected] == 'MIC:':
                    if miclevel > 0:
                        miclevel = miclevel - 2
                        run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
                elif menu[selected] == 'PHONES:':
                    if headphoneslevel > 0:
                        headphoneslevel = headphoneslevel - 2
                        run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
                elif menu[selected] == 'SCENE:' and recording == False:
                    if scene > 1:
                        scene -= 1
                        #shot = countshots(filmname, filmfolder, scene)
                    else:
                        scene = countscenes(filmfolder, filmname)
                    shot=1
                    take = counttakes(filmname, filmfolder, scene, shot)
                    #scene, shots, take = browse2(filmname, filmfolder, scene, shot, take, 0, -1)
                    #takes = take
                    #shot = 1
                elif menu[selected] == 'SHOT:' and recording == False:
                    if shot > 1:
                        shot -= 1
                    else:
                        shot = countshots(filmname, filmfolder, scene)
                    take = counttakes(filmname, filmfolder, scene, shot)
                    #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, -1)
                    #takes = take
                elif menu[selected] == 'TAKE:' and recording == False:
                    if take > 1:
                        take -= 1
                    else:
                        take = counttakes(filmname,filmfolder,scene,shot)
                    #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, -1)
                elif menu[selected] == 'RED:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[0]) > 0.02:
                        camera.awb_gains = (round(camera.awb_gains[0],2) - 0.02, round(camera.awb_gains[1],2))
                elif menu[selected] == 'BLUE:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[1]) > 0.02:
                        camera.awb_gains = (round(camera.awb_gains[0],2), round(camera.awb_gains[1],2) - 0.02)
                elif menu[selected] == 'SRV:':
                    if serverstate == 'on':
                        try:
                            os.makedirs(gonzopifolder+'/srv/sessions')
                            os.system('chown www-data '+gonzopifolder+'/srv/sessions')
                        except:
                            print('srv folder exist')
                        serverstate = gonzopiserver(False)
                    elif serverstate == 'off':
                        serverstate = gonzopiserver(True)
                elif menu[selected] == 'WIFI:':
                    if wifistate == 'on':
                        run_command('sudo iwconfig wlan0 txpower off')
                        wifistate = 'off'
                    elif wifistate == 'off':
                        run_command('sudo iwconfig wlan0 txpower auto')
                        wifistate = 'on'
                elif menu[selected] == 'SEARCH:':
                    if searchforcameras == 'on':
                        searchforcameras = 'off'
                    elif searchforcameras == 'off':
                        seaarchforcameras = 'on'
                elif menu[selected] == 'MODE:':
                    if cammode == 'film':
                        cammode = 'picture'
                        vumetermessage('changing to picture mode')
                    elif cammode == 'picture':
                        cammode = 'film'
                        vumetermessage('changing to film mode')
                    camera = stopcamera(camera, rec_process)
                    camera = startcamera(camera)
                    loadfilmsettings = True
                    flushbutton()
                elif menu[selected] == 'LENS:':
                    s = 0
                    for a in lenses:
                        if a == lens:
                            selectlens = s
                        s += 1
                    if selectlens > 0:
                        selectlens -= 1
                    lens = os.listdir('lenses/')[selectlens]
                    #npzfile = np.load('lenses/' + lens)
                    #lensshade = npzfile['lens_shading_table']
                    table = read_table('lenses/' + lens)
                    camera.lens_shading_table = table
                elif menu[selected] == 'DUB:':
                    if round(dub[0],1) == 1.0 and round(dub[1],1) > 0.0:
                        dub[1] -= 0.1
                    if round(dub[1],1) == 1.0 and round(dub[0],1) < 1.0:
                        dub[0] += 0.1
                elif menu[selected] == 'COMP:':
                    if comp > 0:
                        comp -= 1
                elif menu[selected] == 'HW:':
                    if plughw > 0:
                        plughw -= 1
                    vumetermessage(getaudiocards()[plughw])
                elif menu[selected] == 'CH:':
                    if channels == 2:
                        channels = 1
                elif menu[selected] == 'FPS:':
                    if fps_selected > 0:
                        fps_selected-=1
                        fps=fps_selection[fps_selected]
                        camera = stopcamera_preview(camera)
                        camera.framerate = fps 
                        camera = startcamera_preview(camera)
                elif menu[selected] == 'Q:':
                    if quality > 10:
                        quality -= 1
                elif menu[selected] == 'CAMERA:':
                    if camselected > 0:
                        newselected = camselected-1
                        logger.info('camera selected:'+str(camselected))
                elif menu[selected] == 'SLIDE:':
                    if slidecommander and slide > 1:
                        slide -= 1
                        #send_serial_port(slidecommander,'<')
                elif menu[selected] == 'DSK:':
                    if dsk > 0:
                        dsk -= 1
                        filmfolder = storagedrives[dsk][1]
                        loadfilmsettings = True
                        #COUNT DISKSPACE
                        disk = os.statvfs(filmfolder)
                        diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
                        #LOAD FILM AND SCENE SETTINGS
                        try:
                            filmname = getfilms(filmfolder)[0][0]
                        except:
                            filmname = filmname 
                        try:
                            filmname_back = getfilms(filmfolder)[0][1]
                        except:
                            filmname_back = filmname 
                        if serverstate == 'on':
                            gonzopiserver(False)
                            gonzopiserver(True)
                elif menu[selected] == 'MUX:':
                    if muxing == False:
                        muxing=True
                        mux='yes'
                    else:
                        muxing=False
                        mux='no'

            #RIGHT
            elif pressed == 'right':
                if selected < len(menu) - 1:
                    selected = selected + 1
                else:
                    selected = 0
                if selected == 5: #jump over recording time
                    selected = 6
            #Start Recording Time
            if recording == True:
                t = time.time() - starttime
                rectime = time.strftime("%H:%M:%S", time.gmtime(t))
            #Load settings
            if loadfilmsettings == True:
                db = get_film_files(filmname,filmfolder,db)
                try:
                    filmsettings = loadsettings(filmfolder, filmname)
                    camera.brightness = filmsettings[2]
                    camera.contrast = filmsettings[3]
                    camera.saturation = filmsettings[4]
                    camera.shutter_speed = filmsettings[5]
                    camera.iso = filmsettings[6]
                    camera.awb_mode = filmsettings[7]
                    camera.awb_gains = filmsettings[8]
                    awb_lock = filmsettings[9]
                    miclevel = filmsettings[10]
                    headphoneslevel = filmsettings[11]
                    beeps = filmsettings[12]
                    flip = filmsettings[13]
                    comp = filmsettings[14]
                    between = filmsettings[15]
                    duration = filmsettings[16]
                    showmenu_settings = filmsettings[17]
                    quality = filmsettings[18]
                    #wifistate = filmsettings[19]
                    #serverstate=filmsettings[20]
                    plughw=filmsettings[21]
                    channels=filmsettings[22]
                    #cammode=filmsettings[23]
                    scene=filmsettings[24]
                    shot=filmsettings[25]
                    take=filmsettings[26]
                    cameras=filmsettings[27]
                    udp_ip=filmsettings[28]
                    udp_port=filmsettings[29]
                    if newbitrate == '':
                        bitrate=filmsettings[30]
                        newbitrate = ''
                    pan=filmsettings[31]
                    tilt=filmsettings[32]
                    move=filmsettings[33]
                    speed=filmsettings[34]
                    slide=filmsettings[35]
                    film_fps=filmsettings[36]
                    film_reso=filmsettings[37]
                    logger.info('film settings loaded & applied')
                    time.sleep(0.2)
                except:
                    logger.warning('could not load film settings')
                #if rpimode:
                #    #FIRE UP CAMERA
                #    if camera != None:
                #        camera.stop_preview()
                #        camera.close()
                #    camera = startcamera(lens,fps)
                #    #START INTERFACE
                #else:
                #    camera=None
                if flip == "yes":
                    camera.vflip = True
                    camera.hflip = True
                run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
                run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
                #check if audiocard there other default to 0
                if int(plughw) > len(getaudiocards()):
                    plughw = 0
                    channels = 1
                    vumetermessage(getaudiocards()[plughw])
                print(filmfolder)
                print(filmname)
                check_film = True
                if check_film == True:
                    origin_videos=organize(filmfolder, filmname)
                    print('ORIGIN')
                    print(origin_videos)
                    print('total of videos: '+str(len(origin_videos)))
                    with open(filmfolder+filmname+'/.origin_videos', 'w') as outfile:
                        outfile.write('\n'.join(str(i) for i in origin_videos))
                    if not os.path.isdir(filmfolder+'.videos/'):
                        os.makedirs(filmfolder+'.videos/')
                    allfiles = os.listdir(filmfolder+'.videos/')
                    print(allfiles)
                    print('alll')
                    for origin in origin_videos:
                        if origin in allfiles:
                            try:
                                #os.remove(origin)
                                print('ORIGIN VIDEO FOLDER NOT IN SYNC' + origin)
                                time.sleep(5)
                            except:
                                print('not exist')
                                time.sleep(5)
                    #organize(filmfolder,'onthefloor')
                    #if origin_videos != []:
                    #    if origin_videos[0] != '':
                    #        reso_w, reso_h = check_reso(origin_videos[0])
                    #        reso_check=str(reso_w)+'x'+str(reso_h)
                    #        fps_check = check_fps(origin_videos[0])
                    #        if reso_check != film_reso:
                    #            vumetermessage('wrong film project resolution')
                    #            #waitforanykey()
                    #        if str(fps_check) != str(film_fps):
                    #            vumetermessage('wrong film project framerate')
                    #            #waitforanykey()
                    add_organize(filmfolder, filmname)
                scenes, shots, takes = countlast(filmname, filmfolder)
                loadfilmsettings = False
                rendermenu = True
                updatethumb =  True
            if scene == 0:
                scene = 1
            if take == 0:
                take = 1
            if shot == 0:
                shot = 1
            # If menu at SCENE show first shot thumbnail off that scene
            if menu[selected] == 'FILM:' and lastmenu != menu[selected] and recordable == False:
                updatethumb = True
            if menu[selected] == 'SCENE:' and lastmenu != menu[selected] and recordable == False:
                updatethumb = True
            if menu[selected] == 'SHOT:' and lastmenu != menu[selected] and recordable == False:
                updatethumb = True
            if menu[selected] == 'TAKE:' and lastmenu != menu[selected] and recordable == False:
                updatethumb = True
            #Check if scene, shot, or take changed and update thumbnail
            if oldscene != scene or oldshot != shot or oldtake != take or updatethumb == True:
                if recording == False:
                    #logger.info('film:' + filmname + ' scene:' + str(scene) + '/' + str(scenes) + ' shot:' + str(shot) + '/' + str(shots) + ' take:' + str(take) + '/' + str(takes))
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    scenename = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/'
                    if foldername in shots_selected:
                        shots_sel = '*'
                    else:
                        shots_sel = ''
                    if scenename in scenes_selected:
                        scenes_sel = '*'
                    else:
                        scenes_sel = ''
                    if filmname in films_selected:
                        films_sel = '*'
                    else:
                        films_sel = ''
                    filename = 'take' + str(take).zfill(3)
                    picturename = 'picture' + str(take).zfill(3)
                    recordable = not os.path.isfile(foldername + filename + '.mp4') and not os.path.isfile(foldername + filename + '.h264') and not os.path.isfile(foldername + picturename + '.jpeg')
                    overlay = removeimage(camera, overlay)
                    if recordable:
                        vumetermessage('filming with '+camera_model+' ip:'+ network + ' '+camerasconnected)
                        #vumetermessage(str(round(film_fps)) + ' '+ str(round(fps)))
                    if menu[selected] == 'SCENE:' and recordable == False: # display first shot of scene if browsing scenes
                        p = counttakes(filmname, filmfolder, scene, 1)
                        imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                        try:
                            videosize=countsize(filmfolder + filmname + '/scene' + str(scene).zfill(3)+'/scene.mp4')
                            if videosize == 0:
                                vumetermessage('scene not rendered')
                            else:
                                vumetermessage('videosize: '+str(round(videosize/1000,2))+' Mb')
                        except:
                            vumetermessage('not rendered')
                    #elif menu[selected] == 'FILM:' and recordable == True:
                    #    scene, shot, take = countlast(filmname,filmfolder)
                    #    shot += 1
                    elif menu[selected] == 'FILM:' and recordable == False: # display first shot of film
                        p = counttakes(filmname, filmfolder, 1, 1)
                        imagename = filmfolder + filmname + '/scene' + str(1).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                        try:
                            videosize=countsize(filmfolder + filmname + '/' + filmname+'.mp4')
                            if videosize == 0:
                                vumetermessage('film not rendered')
                            else:
                                vumetermessage('videosize: '+str(round(videosize/1000,2))+' Mb')
                        except:
                            vumetermessage('not rendered')
                    imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3) + '.jpeg'
                    if menu[selected]=='SHOT:' and recordable == False or menu[selected]=='TAKE:' and recordable==False:
                        try:
                            videosize=countsize(foldername + filename + '.mp4')
                            vumetermessage('length: '+get_video_length_str(foldername+filename+'.mp4')+' size: '+str(round(videosize/1000,2))+' Mb')
                        except:
                            videosize=countsize(foldername + filename + '.h264')
                            vumetermessage('videosize: '+str(round(videosize/1000,2))+' Mb')
                    overlay = displayimage(camera, imagename, overlay, 3)
                    oldscene = scene
                    oldshot = shot
                    oldtake = take
                    updatethumb = False
                    scenes = countscenes(filmfolder, filmname)
                    shots = countshots(filmname, filmfolder, scene)
                    takes = counttakes(filmname, filmfolder, scene, shot)
            #If auto dont show value show auto (impovement here to show different colors in gui, yes!!?)
            if camera.iso == 0:
                cameraiso = 'auto'
            else:
                cameraiso = str(camera.iso)
            if camera.shutter_speed == 0:
                camerashutter = 'auto'
            else:
                camerashutter = str(camera.exposure_speed).zfill(5)
            if camera.awb_mode == 'auto':
                camerared = 'auto'
                camerablue = 'auto'
            else:
                camerared = str(float(camera.awb_gains[0]))[:4]
                camerablue = str(float(camera.awb_gains[1]))[:4]
            if time.time() - showmenutime > hide_menu_time: 
                #showmenutime = time.time()
                showmenu=0
                showmenu_settings = False
                rendermenu=True
            #Check if menu is changed and save settings / sec
            if buttonpressed == True or recording == True or rendermenu == True:
                if buttonpressed == True and recording == False and not pressed == 'record' and not pressed == 'retake':
                    showmenu=1
                    showmenutime = time.time()
                lastmenu = menu[selected]
                if showgonzopictrl == False:
                    menu = standardmenu
                    settings = storagedrives[dsk][0]+' '+diskleft, filmname+films_sel, str(scene)+scenes_sel+ '/' + str(scenes), str(shot)+shots_sel+ '/' + str(shots), str(take) + '/' + str(takes), rectime, camerashutter, cameraiso, camerared, camerablue, str(round(camera.framerate)), str(quality), str(camera.brightness), str(camera.contrast), str(camera.saturation), effects[effectselected], str(flip), str(beeps), str(round(reclength,2)), str(plughw), str(channels), str(miclevel), str(headphoneslevel), str(comp), '',blendmodes[blendselect], cammode, '', serverstate, searchforcameras, wifistate, '', '', '', '', '', live, mux, hdmi, str(slide)
                else:
                    #gonzopictrlmenu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'FPS:', 'Q:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'BLEND:', 'FADE:', 'L:', 'MODE:', 'DSK:', 'SHUTDOWN', 'SRV:', 'SEARCH:', 'WIFI:', 'CAMERA:', 'Add CAMERA', 'New FILM', 'Sync FILM', 'Sync SCENE'
                    menu = gonzopictrlmenu
                    #settings = '',str(camselected),'','',rectime,'','','','','','','','','',''
                    settings = storagedrives[dsk][0]+' '+diskleft, filmname, str(scene) + scenes_sel+ '/' + str(scenes), str(shot) + shots_sel+ '/' + str(shots), str(take) + '/' + str(takes), rectime, camerashutter, cameraiso, camerared, camerablue, str(round(camera.framerate)), str(quality), str(camera.brightness), str(camera.contrast), str(camera.saturation), effects[effectselected], str(flip), str(beeps), str(reclength), str(plughw), str(channels), str(miclevel), str(headphoneslevel), str(comp), '',blendmodes[blendselect], cammode, '', serverstate, searchforcameras, wifistate, str(camselected+1), '', '', '', '', '', '', ''
                #Rerender menu if picamera settings change
                #if settings != oldsettings or selected != oldselected:
                oldmenu=writemenu(menu,settings,selected,'',showmenu,oldmenu)
                rendermenu = False
                #save settings if menu has been updated and x seconds passed
                if recording == False:
                    #if time.time() - pausetime > savesettingsevery: 
                    if oldsettings != settings:
                        settings_to_save = [filmfolder, filmname, camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, comp, between, duration, showmenu_settings, quality,wifistate,serverstate,plughw,channels,cammode,scene,shot,take,cameras,udp_ip,udp_port,bitrate, pan, tilt, move, speed, slide, film_fps, film_reso]
                        #print('saving settings')
                        savesettings(settings_to_save, filmname, filmfolder)
                    if time.time() - pausetime > savesettingsevery: 
                        pausetime = time.time()
                        #CPU AND GPU TEMP
                        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                            cputemp = 'cpu: '+str(int(f.read()) / 1000)+'°C'
                        # GPU/SoC temp
                        result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
                        gputemp = 'gpu: '+ str(float(result.stdout.split('=')[1].split("'")[0])) + '°C'
                        #NETWORKS
                        networks=[]
                        network=''
                        adapters = ifaddr.get_adapters()
                        for adapter in adapters:
                            print("IPs of network adapter " + adapter.nice_name)
                            for ip in adapter.ips:
                                if ':' not in ip.ip[0] and '127.0.0.1' != ip.ip:
                                    print(ip.ip)
                                    networks=[ip.ip]
                        if networks != []:
                            network=networks[0]
                            if network not in cameras and network != '':
                                cameras=[]
                                cameras.append(network)
                        else:
                            network='not connected'
                        if len(cameras) > 1:
                            camerasconnected='connected '+str(len(cameras)-1)
                            recordwithports=True
                            if camera_recording:
                                vumetermessage('filming with '+camera_model +' ip:'+ cameras[camselected] + ' '+camerasconnected+' camselected:'+str(camselected+1)+' rec:'+str(camera_recording+1))
                            else:
                                vumetermessage('filming with '+camera_model +' ip:'+ cameras[camselected] + ' '+camerasconnected+' camselected:'+str(camselected+1)+' rec:'+str(camera_recording))
                        else:
                            camerasconnected=''
                            recordwithports=False
                            if searchforcameras == 'on':
                                camerasconnected='searching '+str(pingip)
                            if menu[selected] != 'SHOT:' and menu[selected] != 'SCENE:' and menu[selected] != 'FILM:' and menu[selected] != 'TAKE:':
                                vumetermessage('filming with '+camera_model +' ip:'+ network + ' '+camerasconnected +' '+cputemp+' '+gputemp)
                        disk = os.statvfs(filmfolder)
                        diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
                        #checksync = int(disk.f_bavail * disk.f_frsize / 1024 / 1024 )
                        #if checksync == oldchecksync:
                        #    rectime = str(checksync)+'Mb/s'
                        #elif checksync - oldchecksync > 1000:
                        #    rectime = 'SYNCING.. '
                        #oldchecksync = checksync
                        #print(term.yellow+'filming with '+camera_model +' ip:'+ network
                        print(camselected,camera_recording,cameras)
                #writemessage(pressed)
                oldsettings = settings
                oldselected = selected
            #PING TARINAS
            if searchforcameras == 'on':
                if camera_recording == None:
                    if pingip < 256:
                        pingip+=1
                    else:
                        pingip=0
                        #searchforcameras='off'
                    newcamera=pingtocamera(network[:-3]+str(pingip),port,'PING')
                    if newcamera != '':
                        if newcamera not in cameras and newcamera not in networks:
                            cameras.append(newcamera)
                            vumetermessage("Found camera! "+newcamera)
                    print('-~-')
                    print('pinging ip: '+network[:-3]+str(pingip))
                else:
                    searchforcameras = 'off'
            time.sleep(keydelay)

#--------------Logger-----------------------

class logger():
    def info(info):
        print(term.yellow(info))
    def warning(warning):
        print('Warning: ' + warning)

#-------------get film db files---

def get_film_files(filmname,filmfolder,db):
    if not os.path.isdir(filmfolder+'.videos/'):
        os.makedirs(filmfolder+'.videos/')
    if not os.path.isdir(filmfolder+'.tmp/'):
        os.makedirs(filmfolder+'.tmp/')
    filmdb = filmfolder+'.videos/gonzopi.db'
    db = web.database(dbn='sqlite', db=filmdb)
    try:
        videodb=db.select('videos')
        return db
    except:
        db.query("CREATE TABLE videos (id integer PRIMARY KEY, tid DATETIME, filename TEXT, foldername TEXT, filmname TEXT, scene INT, shot INT, take INT, audiolength FLOAT, videolength FLOAT,soundlag FLOAT, audiosync FLOAT, faststart BOOL);")
    videodb=db.select('videos')
    return db

#---------remove and get correct database------

def correct_database(filmname,filmfolder,db):
    if not os.path.isdir(filmfolder+'.videos/'):
        os.makedirs(filmfolder+'.videos/')
    filmdb = filmfolder+'.videos/gonzopi.db'
    #run_command('rm '+filmdb)
    db = web.database(dbn='sqlite', db=filmdb)
    db.query("CREATE TABLE videos (id integer PRIMARY KEY, tid DATETIME, filename TEXT, foldername TEXT, filmname TEXT, scene INT, shot INT, take INT, audiolength FLOAT, videolength FLOAT,soundlag FLOAT, audiosync FLOAT, faststart BOOL);")
    videodb=db.select('videos')
    return db

#--------------Save settings-----------------

def savesettings(settings, filmname, filmfolder):
    #db.insert('videos', tid=datetime.datetime.now())
    try:
        with open(filmfolder + filmname + "/settings.p", "wb") as f:
            pickle.dump(settings, f)
            #logger.info("settings saved")
    except:
        logger.warning("could not save settings")
        #logger.warning(e)
    return

#--------------Load film settings--------------

def loadsettings(filmfolder, filmname):
    try:
        settings = pickle.load(open(filmfolder + filmname + "/settings.p", "rb"))
        logger.info("settings loaded")
        return settings
    except:
        logger.info("couldnt load settings")
        return ''


##---------------Connection----------------------------------------------
def pingtocamera(host, port, data):
    print("Sending to "+host+" on port "+str(port)+" DATA:"+data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.05)
    newcamera=''
    try:
        while True:
            s.connect((host, port))
            s.send(str.encode(data))
            newcamera=host
            print("Sent to server..")
            break
    except:
        print('did not connect')
    s.close()
    return newcamera

##---------------Send to server----------------------------------------------

def sendtocamera(host, port, data):
    print("Sending to "+host+" on port "+str(port)+" DATA:"+data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        while True:
            s.connect((host, port))
            s.send(str.encode(data))
            print("Sent to server..")
            break
        return True
    except:
        print('did not connect')
        return False
    s.close()

##---------------Send to server----------------------------------------------

def sendtoserver(host, port, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        while True:
            print('sending data to '+host+':'+str(port))
            s.connect((host, port))
            s.send(str.encode(data))
            s.close()
            break
    except:
        print('sometin rong')

##--------------Listen for Clients-----------------------

def listenforclients(host, port, q):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    #s.settimeout(0.1)
    try:
        print("listening on port "+str(port))
        s.listen(5)
        c, addr = s.accept()
        while True:
                data = c.recv(1024).decode()
                if not data:
                    print("no data")
                    break
                else:
                    if addr:
                        #print(addr[0],' sending back')
                        #sendtoserver(addr[0],port,'rebounce'+data)
                        nextstatus = data
                        print("got data:"+nextstatus)
                        c.close()
                        q.put(nextstatus+'*'+addr[0])
                        break
    except:
        print("somthin wrong")
        q.put('')

#--------------Write the menu layer to dispmanx--------------

def writemenu(menu,settings,selected,header,showmenu,oldmenu):
    menudone = ''
    menudoneprint = ''
    menudone += str(selected) + '\n'
    menudone += str(showmenu) + '\n'
    menudone += header + '\n'
    n = 0
    for i, s in zip(menu, settings):
        menudone += i + s + '\n'
        if n == selected:
            menudoneprint += term.black_on_darkkhaki(i+s) + ' | ' 
        else:
            menudoneprint += i + ' ' + s + ' | '
        n += 1
    spaces = len(menudone) - 500
    menudone += spaces * ' '
    if oldmenu != menudone and len(menudone) > 4:
        print(term.clear+term.home)
        if showmenu == 0:
            print(term.red+menudoneprint)
        else:
            print(menudoneprint)
        #menudone += 'EOF'
        f = open('/dev/shm/interface', 'w')
        f.write(menudone)
        f.close()
        return oldmenu

#------------Write to screen----------------

def writemessage(message):
    menudone = ""
    menudone += '420' + '\n'
    menudone += message + '\n'
    #menudone += 'EOF'
    #clear = 500
    #clear = clear - len(message)
    f = open('/dev/shm/interface', 'w')
    f.write(menudone)
    f.close()

#------------Write to vumeter (last line)-----

def vumetermessage(message):
    clear = 72
    clear = clear - len(message)
    f = open('/dev/shm/vumeter', 'w')
    f.write(message + clear * ' ')
    f.close()
    logger.info(message)

#------------Count file size-----

def countvideosize(filename):
    size = 0
    if type(filename) is list:
        size = 0
        for i in filename[:]:
            size = size + os.stat(i + '.mp4').st_size
    if type(filename) is str:
        size = os.stat(filename + '.mp4').st_size
    return size/1024

def countsize(filename):
    size = 0
    if type(filename) is str:
        try:
            size = os.stat(filename).st_size
        except:
            return 0
    else:
        return 0
    return size/1024

#------------Count scenes, takes and shots-----

def countlast(filmname, filmfolder): 
    scenes = 0
    shots = 0
    takes = 0
    try:
        allfiles = os.listdir(filmfolder + filmname)
    except:
        allfiles = []
        scenes = 0
    for a in allfiles:
        if 'scene' in a:
            scenes = scenes + 1
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scenes).zfill(3))
    except:
        allfiles = []
        shots = 0
    for a in allfiles:
        if 'shot' in a:
            shots = shots + 1
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scenes).zfill(3) + '/shot' + str(shots).zfill(3))
    except:
        allfiles = []
        takes = 0
    for a in allfiles:
        if '.mp4' in a or '.h264' in a or '.jpeg' and 'picture' in a:
            takes = takes + 1
    return scenes, shots, takes

#------------Count scenes--------

def countscenes(filmfolder, filmname):
    scenes = 0
    try:
        allfiles = os.listdir(filmfolder + filmname)
    except:
        allfiles = []
        scenes = 0
    for a in allfiles:
        if 'scene' in a:
            scenes = scenes + 1
    return scenes

#------------Count shots--------

def countshots(filmname, filmfolder, scene):
    shots = 0
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scene).zfill(3))
    except:
        allfiles = []
        shots = 0
    for a in allfiles:
        if 'shot' in a or '.jpeg' and 'picture' in a:
            shots = shots + 1
    return shots

#------------Count takes--------

def counttakes(filmname, filmfolder, scene, shot):
    takes = 0
    doubles = ''
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
    except:
        allfiles = []
        return takes
    for a in allfiles:
        if 'take' in a:
            if '.mp4' in a or '.h264' in a or '.jpeg' and 'picture' in a:
                if not doubles.replace('.h264', '.mp4') == a:
                    takes = takes + 1
                doubles = a
    return takes

def counttakes2(folder):
    takes = 0
    doubles = ''
    try:
        allfiles = os.listdir(folder)
    except:
        allfiles = []
        return takes
    for a in allfiles:
        if 'take' in a:
            if '.mp4' in a or '.h264' in a or '.jpeg' and 'picture' in a:
                if not doubles.replace('.h264', '.mp4') == a:
                    takes = takes + 1
                doubles = a
    return takes

def gettake(folder):
    takes = 0
    doubles = ''
    try:
        allfiles = os.listdir(folder)
    except:
        allfiles = []
        return takes
    for a in allfiles:
        if 'take' in a:
            if '.mp4' in a or '.h264' in a or '.jpeg' and 'picture' in a:
                if not doubles.replace('.h264', '.mp4') == a:
                    takes = takes + 1
                    filename=a
                doubles = a
    return filename

#------------Count last take name --------

def nexttakefilename(filmname, filmfolder, scene, shot):
    takes = 0
    doubles = ''
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
    except:
        allfiles = []
        return takes
    for a in allfiles:
        if 'take' in a:
            if '.mp4' in a or '.h264' in a or '.jpeg' and 'picture' in a:
                if not doubles.replace('.h264', '.mp4') == a:
                    takes = takes + 1
                doubles = a
    return filmfolder+filmname+'/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3)+'/take'+str(takes+1).zfill(3)

def counttakes2(folder):
    takes = 0
    doubles = ''
    try:
        allfiles = os.listdir(folder)
    except:
        allfiles = []
        return takes
    for a in allfiles:
        if 'take' in a:
            if '.mp4' in a or '.h264' in a or '.jpeg' and 'picture' in a:
                if not doubles.replace('.h264', '.mp4') == a:
                    takes = takes + 1
                doubles = a
    return takes

#-----------Count videos on floor-----

def countonfloor(filmname, filmfolder):
    print('dsad')

#----------Camera effect menus------

def vfx_colorpoint():
    global camera
    oldmenu=''
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    header = 'Choose colorpoint'
    menu =  'BACK','GREEN','RED/YELLOW','BLUE','PURPLE'
    while True:
        settings = '','','','',''
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
            else:
                selected = 0
            selected == 0
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
            else:
                selected = len(settings) - 1
        elif pressed == 'middle' and menu[selected] == 'GREEN':
            camera.image_effect_params = 0
        elif pressed == 'middle' and menu[selected] == 'RED/YELLOW':
            camera.image_effect_params = 1
        elif pressed == 'middle' and menu[selected] == 'BLUE':
            camera.image_effect_params = 2
        elif pressed == 'middle' and menu[selected] == 'PURPLE':
            camera.image_effect_params = 3
        elif pressed == 'middle' and menu[selected] == 'BACK':
            return
        time.sleep(keydelay)

def vfx_solarize():
    global camera
    oldmenu=''
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    strenght = 0
    r=0
    g=0
    b=0
    header = 'Choose solarize'
    menu =  'BACK','STRENGHT:','R:','G:','B:'
    while True:
        settings = '',str(strenght),str(r),str(g),str(b)
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
            else:
                selected = 0
            selected == 0
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
            else:
                selected = len(settings) - 1
        elif pressed == 'up' and menu[selected] =='STRENGHT:':
            if strenght < 128:
                strenght += 1
        elif pressed == 'down' and menu[selected] =='STRENGHT:':
            if strenght > 0:
                strenght -= 1
        elif pressed == 'up' and menu[selected] =='R:':
            if r < 128:
                r += 1
        elif pressed == 'down' and menu[selected] =='R:':
            if r > 0:
                r -= 1
        elif pressed == 'up' and menu[selected] =='G:':
            if g < 128:
                g += 1
        elif pressed == 'down' and menu[selected] =='G:':
            if g > 0:
                g -= 1
        elif pressed == 'up' and menu[selected] =='B:':
            if b < 128:
                b += 1
        elif pressed == 'down' and menu[selected] =='B:':
            if b > 0:
                b -= 1
        elif pressed == 'middle' and menu[selected] != 'BACK':
            camera.image_effect_params = r,g,b,strenght
        elif pressed == 'middle' and menu[selected] == 'BACK':
            return
        time.sleep(keydelay)

def film_settings():
    global film_fps_options, film_reso_options, film_fps_selected, film_fps, film_reso, fps
    oldmenu=''
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 1
    film_reso_selected=0
    film_fps_selected=1
    header = 'Film settings'
    menu =  'OK','FPS:','RESOLUTION:'
    while True:
        settings = '',str(film_fps_options[film_fps_selected]),film_reso_options[film_reso_selected]
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
            else:
                selected = 0
            selected == 0
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
            else:
                selected = len(settings) - 1
        elif pressed == 'up' and menu[selected] =='FPS:':
            if film_fps_selected < len(film_fps_options)-1:
                film_fps_selected += 1
                film_fps=int(film_fps_options[film_fps_selected])
            else:
                film_fps_selected == len(film_fps_options)-1
        elif pressed == 'down' and menu[selected] =='FPS:':
            if film_fps_selected > 0:
                film_fps_selected -= 1
                film_fps=int(film_fps_options[film_fps_selected])
        elif pressed == 'up' and menu[selected] =='RESOLUTION:':
            if film_reso_selected < len(film_reso_options)-1:
                film_reso_selected += 1
                film_reso=film_reso_options[film_reso_selected]
        elif pressed == 'down' and menu[selected] =='RESOLUTION:':
            if film_reso_selected > 0:
                film_reso_selected -= 1
                film_reso=film_reso_options[film_reso_selected]
        elif pressed == 'middle' and menu[selected]=='OK':
            return film_reso, film_fps
        time.sleep(keydelay)
 

#------------Run Command-------------

def run_command(command_line):
    #command_line_args = shlex.split(command_line)
    logger.info('Running: "' + command_line + '"')
    try:
        p = subprocess.Popen(command_line, shell=True).wait()
        # process_output is now a string, not a file,
        # you may want to do:
    except (OSError, CalledProcessError) as exception:
        logger.warning('Exception occured: ' + str(exception))
        logger.warning('Process failed')
        return False
    else:
        # no exception was raised
        logger.info('Process finished')
    return True

#-------------Display bakg-------------------

def displaybakg(camera, filename, underlay, layer):
    # Load the arbitrarily sized image
    img = Image.open(filename)
    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGB', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    underlay = camera.add_overlay(pad.tobytes(), size=img.size)
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    underlay.alpha = 255
    underlay.layer = layer

#-------------Display jpeg-------------------

def displayimage(camera, filename, overlay, layer):
    # Load the arbitrarily sized image
    try:
        img = Image.open(filename)
    except:
        #writemessage('Seems like an empty shot. Hit record!')
        overlay = removeimage(camera, overlay)
        return overlay
    camera.stop_preview()
    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGB', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    overlay = camera.add_overlay(pad.tobytes(), size=img.size)
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    overlay.alpha = 255
    overlay.layer = layer
    return overlay

def removeimage(camera, overlay):
    if overlay:
        try:
            camera.remove_overlay(overlay)
            overlay = None
            camera.start_preview()
        except:
            pass
        return overlay


#-------------Browse------------------

def browse(filmname, filmfolder, scene, shot, take):
    scenes = countscenes(filmfolder, filmname)
    shots = countshots(filmname, filmfolder, scene)
    takes = counttakes(filmname, filmfolder, scene, shot)
    return scenes, shots, takes

#-------------Browse2.0------------------

def browse2(filmname, filmfolder, scene, shot, take, n, b):
    scenes = countscenes(filmfolder, filmname)
    shots = countshots(filmname, filmfolder, scene)
    takes = counttakes(filmname, filmfolder, scene, shot)
    #writemessage(str(scene) + ' < ' + str(scenes))
    #time.sleep(4)
    selected = n
    if selected == 0 and b == 1:
        if scene < scenes + 1: #remove this if u want to select any scene
            scene = scene + 1
            shot = countshots(filmname, filmfolder, scene)
            take = counttakes(filmname, filmfolder, scene, shot)
            #if take == 0:
                #shot = shot - 1
                #take = counttakes(filmname, filmfolder, scene, shot - 1)
    elif selected == 1 and b == 1:
        if shot < shots + 1: #remove this if u want to select any shot
            shot = shot + 1 
            take = counttakes(filmname, filmfolder, scene, shot)
    elif selected == 2 and b == 1:
        if take < takes + 1:
            take = take + 1 
    elif selected == 0 and b == -1:
        if scene > 1:
            scene = scene - 1
            shot = countshots(filmname, filmfolder, scene)
            take = counttakes(filmname, filmfolder, scene, shot)
            #if take == 0:
            #    shot = shot - 1
            #    take = counttakes(filmname, filmfolder, scene, shot - 1)
    elif selected == 1 and b == -1:
        if shot > 1:
            shot = shot - 1
            take = counttakes(filmname, filmfolder, scene, shot)
    elif selected == 2 and b == -1:
        if take > 1:
            take = take - 1 
    return scene, shot, take

#-------------Update------------------

def update(gonzopiversion, gonzopivername):
    logger.info('Current version ' + gonzopiversion[:-1] + ' ' + gonzopivername[:-1])
    time.sleep(2)
    logger.info('Checking for updates...')
    try:
        run_command('wget -N https://raw.githubusercontent.com/rbckman/gonzopi/master/VERSION -P /tmp/')
    except:
        logger.info('Sorry buddy, no internet connection')
        time.sleep(2)
        return gonzopiversion, gonzopivername
    try:
        f = open('/tmp/VERSION')
        versionnumber = f.readline()
        versionname = f.readline()
    except:
        logger.info('hmm.. something wrong with the update')
    if round(float(gonzopiversion),3) < round(float(versionnumber),3):
        logger.info('New version found ' + versionnumber[:-1] + ' ' + versionname[:-1])
        time.sleep(4)
        logger.info('Updating...')
        run_command('git -C ' + gonzopifolder + ' pull')
        #run_command('sudo ' + gonzopifolder + '/install.sh')
        logger.info('Update done, will now reboot Gonzopi')
        waitforanykey()
        logger.info('Hold on rebooting Gonzopi...')
        run_command('sudo reboot')
    logger.info('Version is up-to-date!')
    return gonzopiversion, gonzopivername

#-------------Get films---------------

def getfilms(filmfolder):
    #get a list of films, in order of settings.p file last modified
    films_sorted = []
    films = next(os.walk(filmfolder))[1]
    if films == []:
        return
    for i in films:
        if not '.videos' in i:
            if os.path.isfile(filmfolder + i + '/' + 'settings.p') == True:
                lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
                films_sorted.append((i,lastupdate))
            else:
                films_sorted.append((i,0))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[1], reverse=True)
    logger.info('*-- Films --*')
    for p in films_sorted:
        logger.info(p[0])
    return films_sorted

#-------------Load gonzopi config---------------

def getconfig(camera):
    oldmenu=''
    filmfolder=''
    if camera != None:
        version = camera.revision
    else:
        version = 'none'
    home = os.path.expanduser('~')
    configfile = home + '/.gonzopi/config.ini'
    configdir = os.path.dirname(configfile)
    if not os.path.isdir(configdir):
        os.makedirs(configdir)
    config = configparser.ConfigParser()
    if config.read(configfile):
        try:
            camera_model = config['SENSOR']['model']
        except:
            logger.info("couldnt read config")
        try:
            camera_revision = config['SENSOR']['revision']
        except:
            logger.info("couldnt read config")
        try:
            filmfolder = config['USER']['filmfolder']
            return camera_model, camera_revision, filmfolder+'/'
        except:
            logger.info("couldnt read config")
    if version == 'none':
        config['SENSOR'] = {}
        config['SENSOR']['model'] = version
        config['SENSOR']['revision'] = 'none'
        with open(configfile, 'w') as f:
            config.write(f)
        camera_model = version
        camera_revision = 'none'
    elif version == 'imx219':
        config['SENSOR'] = {}
        config['SENSOR']['model'] = version
        config['SENSOR']['revision'] = 'standard'
        with open(configfile, 'w') as f:
            config.write(f)
        camera_model = version
        camera_revision = 'standard'
    elif version == 'imx477':
        config['SENSOR'] = {}
        config['SENSOR']['model'] = version
        config['SENSOR']['revision'] = 'hq-camera'
        camera_model = version
        camera_revision = 'hq-camera'
        with open(configfile, 'w') as f:
            config.write(f)
    else:
        pressed = ''
        buttonpressed = ''
        buttontime = time.time()
        holdbutton = ''
        selected = 0
        header = 'What revision of ' + version + ' sensor are you using?'
        menu = 'rev.C', 'rev.D', 'hq-camera'
        while True:
            settings = '', '', ''
            oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
            pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
            if pressed == 'right':
                if selected < (len(settings) - 1):
                    selected = selected + 1
            elif pressed == 'left':
                if selected > 0:
                    selected = selected - 1
            elif pressed == 'middle':
                camera_model = version
                camera_revision = menu[selected]
                config['SENSOR'] = {}
                config['SENSOR']['model'] = camera_model
                config['SENSOR']['revision'] = camera_revision
                with open(configfile, 'w') as f:
                    config.write(f)
            time.sleep(0.02)

    return version, camera_revision, home+'/gonzopifilms/'
    #if filmfolder != '':
    #    return version, camera_revision, filmfolder+'/'
    #else:
    #    filmfolder = namesomething('Your film folder: ', home+'/Videos')
    #    config['USER'] = {}
    #    config['USER']['filmfolder'] = filmfolder
    #    with open(configfile, 'w') as f:
    #        config.write(f)
    #    return camera_model, camera_revision, filmfolder+'/'

#-------------Calc folder size with du-----------

def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du','-sh', path]).split()[0].decode('utf-8')


#------------Clean up----------------

def cleanupdisk(filmname, filmfolder):
    alloriginfiles=[]
    films = getfilms(filmfolder)
    for f in films:
        alloriginfiles.extend(organize(filmfolder,f[0]))
    print(alloriginfiles)
    filesinfolder = next(os.walk(filmfolder+'.videos/'))[2]
    filesfolder=[]
    for i in filesinfolder:
        filesfolder.append(filmfolder+'.videos/'+i)
    print(filesfolder)
    for i in alloriginfiles:
        if i in filesfolder:
            print("YES, found link to origin")
        else:
            print("NOPE, no link to origin")
            print(i)
            time.sleep(2)
            #os.system('rm ' + i)
    #for i in filesfolder:
    #    if i in alloriginfiles:
    #        print("YES, found link to origin")
    #    else:
    #        print("NOPE, no link to origin")
    #        print(i)
    #        os.system('rm ' + i)

#-------------Load film---------------

def loadfilm(filmname, filmfolder, camera, overlay):
    global film_fps_options, film_reso_options, film_fps_selected, film_reso_selected, film_fps, film_reso, lens, fps
    writemessage('Loading films...')
    oldmenu=''
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    films = getfilms(filmfolder)
    #filmsize=[]
    #for f in films:
    #    filmsize.append(du(filmfolder+f[0]))
    filmstotal = len(films[1:])
    selectedfilm = 0
    selected = 0
    header = 'Up and down to select and load film'
    menu = 'FILM:', 'BACK', 'NEW FILM'
    while True:
        settings = films[selectedfilm][0], '', ''
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        vumetermessage('date: '+time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(films[selectedfilm][1])))
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'down':
            if selectedfilm < filmstotal:
                selectedfilm = selectedfilm + 1
                p = counttakes(films[selectedfilm][0], filmfolder, 1, 1)
                overlay = removeimage(camera, overlay)
                imagename = filmfolder + films[selectedfilm][0] + '/scene' + str(1).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                overlay = displayimage(camera, imagename, overlay, 3)
        elif pressed == 'up':
            if selectedfilm > 0:
                selectedfilm = selectedfilm - 1
                p = counttakes(films[selectedfilm][0], filmfolder, 1, 1)
                overlay = removeimage(camera, overlay)
                imagename = filmfolder + films[selectedfilm][0] + '/scene' + str(1).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                overlay = displayimage(camera, imagename, overlay, 3)
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and menu[selected] == 'FILM:':
            overlay = removeimage(camera, overlay)
            filmname = films[selectedfilm][0]
            return camera, filmname
        elif pressed == 'middle' and menu[selected] == 'BACK':
            overlay = removeimage(camera, overlay)
            writemessage('Returning')
            return camera, filmname
        elif pressed == 'middle' and menu[selected] == 'NEW FILM':
            overlay = removeimage(camera, overlay)
            newfilm=nameyourfilm(filmfolder, filmname, abc, True)
            #film_reso, film_fps = film_settings()
            #camera.stop_preview()
            #camera.close()
            #camera = startcamera(lens,fps)
            writemessage('Great Scott! a new film, May the Force Be With You!')
            time.sleep(2)
            return camera, newfilm
        time.sleep(0.02)

def slide_menu(slidecommander):
    global pan, tilt, move, speed, slidereader, smooth
    if not slidereader:
        slidereader = Popen(['python3', gonzopifolder+'/extras/slidereader.py'])
        #slidereader = subprocess.check_output(['python3',gonzopifolder+'/extras/slidereader.py'], shell=True)
        #slidereader = pipe.decode().strip()
        #vumetermessage(slidereader)
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    header = 'Future Tech Slide Commander'
    menu =  'BACK','SPEED:', 'SMOOTH:', 'PAN:', 'TILT:', 'MOVE:', 'ADD', '<', '>', 'SAVE', 'RESET', 'STATUS'
    oldmenu=''
    while True:
        settings = '',str(speed), str(smooth), str(pan), str(tilt), str(move), '', '', '' , '', '', ''
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'down' and menu[selected] == 'SPEED:':
            if speed > 10:
                speed -= 10
        elif pressed == 'remove' and menu[selected] =='SPEED:':
            speed += 1
        elif pressed == 'view' and menu[selected] =='SPEED:':
            speed -= 1
        elif pressed == 'up' and menu[selected] =='SPEED:':
            speed += 10
        elif pressed == 'down' and menu[selected] =='SPEED:':
            speed -= 10
        elif pressed == 'record' and menu[selected] =='SPEED:':
            speed += 100
        elif pressed == 'retake' and menu[selected] =='SPEED:':
            speed -= 100
        elif pressed == 'down' and menu[selected] == 'SMOOTH:':
            if smooth > 10:
                smooth -= 10
        elif pressed == 'remove' and menu[selected] =='SMOOTH:':
            smooth += 1
        elif pressed == 'view' and menu[selected] =='SMOOTH:':
            smooth -= 1
        elif pressed == 'up' and menu[selected] =='SMOOTH:':
            smooth += 10
        elif pressed == 'down' and menu[selected] =='SMOOTH:':
            smooth -= 10
        elif pressed == 'record' and menu[selected] =='SMOOTH:':
            smooth += 100
        elif pressed == 'retake' and menu[selected] =='SMOOTH:':
            smooth -= 100
        elif pressed == 'up' and menu[selected] =='PAN:':
            pan += 10
        elif pressed == 'down' and menu[selected] =='PAN:':
            pan -= 10
        elif pressed == 'view' and menu[selected] =='PAN:':
            pan -= 1
        elif pressed == 'remove' and menu[selected] =='PAN:':
            pan += 1
        elif pressed == 'retake' and menu[selected] =='PAN:':
            pan -= 100
        elif pressed == 'record' and menu[selected] =='PAN:':
            pan += 100
        elif pressed == 'view' and menu[selected] =='TILT:':
            tilt += 1
        elif pressed == 'remove' and menu[selected] =='TILT:':
            tilt -= 1
        elif pressed == 'up' and menu[selected] =='TILT:':
            tilt += 10
        elif pressed == 'down' and menu[selected] =='TILT:':
            tilt -= 10
        elif pressed == 'retake' and menu[selected] =='TILT:':
            tilt -= 100
        elif pressed == 'record' and menu[selected] =='TILT:':
            tilt += 100
        elif pressed == 'remove' and menu[selected] =='MOVE:':
            move += 1
        elif pressed == 'view' and menu[selected] =='MOVE:':
            move -= 1
        elif pressed == 'up' and menu[selected] =='MOVE:':
            move += 10
        elif pressed == 'down' and menu[selected] =='MOVE:':
            move -= 10
        elif pressed == 'record' and menu[selected] =='MOVE:':
            move += 100
        elif pressed == 'retake' and menu[selected] =='MOVE:':
            move -= 100
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
            else:
                selected = 0
            selected == 0
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
            else:
                selected = len(settings)-1
        elif pressed == 'middle' and menu[selected] == 'PAN:':
            send_serial_port(slidecommander,'p'+str(pan))
        elif pressed == 'middle' and menu[selected] == 'TILT:':
            send_serial_port(slidecommander,'t'+str(tilt))
        elif pressed == 'middle' and menu[selected] == 'MOVE:':
            send_serial_port(slidecommander,'x'+str(move))
        elif pressed == 'middle' and menu[selected] == 'ADD':
            send_serial_port(slidecommander,'#')
        elif pressed == 'record' and menu[selected] == 'ADD':
            return
        elif pressed == 'middle' and menu[selected] == '<':
            send_serial_port(slidecommander,'<')
        elif pressed == 'middle' and menu[selected] == '>':
            send_serial_port(slidecommander,'>')
        elif pressed == 'middle' and menu[selected] == 'SPEED:':
            send_serial_port(slidecommander,'s'+str(speed))
            time.sleep(0.3)
            send_serial_port(slidecommander,'S'+str(speed))
            time.sleep(0.3)
            send_serial_port(slidecommander,'X'+str(speed))
        elif pressed == 'middle' and menu[selected] == 'SMOOTH:':
            send_serial_port(slidecommander,'q'+str(smooth))
            time.sleep(0.3)
            send_serial_port(slidecommander,'Q'+str(smooth))
            time.sleep(0.3)
            send_serial_port(slidecommander,'w'+str(smooth))
        elif pressed == 'middle' and menu[selected] == 'BACK':
            writemessage('Returning')
            return
        elif pressed == 'remove' and menu[selected] == 'ADD':
            send_serial_port(slidecommander,'C')
        elif pressed == 'retake' and menu[selected] == 'ADD':
            send_serial_port(slidecommander,'E')
        elif pressed == 'view' and menu[selected] == 'ADD':
            #send_serial_port(slidecommander,'d'+str(speed))
            send_serial_port(slidecommander,'D'+str(speed))
        elif pressed == 'middle' and menu[selected] == 'STATUS':
            send_serial_port(slidecommander,'R')
        elif pressed == 'middle' and menu[selected] == 'SAVE':
            send_serial_port(slidecommander,'U')
        elif pressed == 'middle' and menu[selected] == 'RESET':
            os.system('pkill -9 slidereader.py')
            if slidereader.poll():
                slidereader.kill()
                slidereader = Popen(['python3', gonzopifolder+'/extras/slidereader.py'])
            time.sleep(1)
            pan = 0
            tilt = 0
            move = 0
        time.sleep(keydelay)


### send to SERIAL PORT

def send_serial_port(serial_port,msg):
    baud_rate = 57600       # Set the baud rate according to your device
    # Create a serial connection
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"Connected to {serial_port} at {baud_rate} baud.")
    except serial.SerialException as e:
        print(f"Error: {e}")
        exit()
    # Write data to the serial port
    data_to_send = msg  # Add a newline if needed
    try:
        ser.write(data_to_send.encode('utf-8'))  # Encode the string to bytes
        print(f"Sent: {data_to_send.strip()}")
    except Exception as e:
        print(f"Error while sending data: {e}")

#---------Name anything really-----------

def namesomething(what, readymadeinput):
    global abc
    anything = readymadeinput
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abcx = 0
    helpmessage = 'Up, Down (select characters) Right (next). Middle (done)'
    cursor = '_'
    blinking = True
    pausetime = time.time()
    while True:
        message = what + anything
        print(term.clear+term.home)
        print(message+cursor)
        writemessage(message + cursor)
        vumetermessage(helpmessage)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if event == ' ':
            event = '_'
        if pressed == 'down':
            pausetime = time.time()
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
        elif pressed == 'up':
            pausetime = time.time()
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
        elif pressed == 'right':
            pausetime = time.time()
            if len(anything) < 30:
                anything = anything + abc[abcx]
                cursor = abc[abcx]
            else:
                helpmessage = 'Yo, maximum characters reached bro!'
        elif pressed == 'left' or pressed == 'remove':
            pausetime = time.time()
            if len(anything) > 0:
                anything = anything[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if len(anything) > 0:
                if abc[abcx] != '_':
                    anything = anything + abc[abcx]
                return anything
        elif event in abc:
            pausetime = time.time()
            anything = anything + event
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(keydelay)


#-------------New film----------------

def nameyourfilm(filmfolder, filmname, abc, newfilm):
    filmcount=len(getfilms(filmfolder))
    oldfilmname = filmname
    filmname = 'reel_'+str(filmcount+1).zfill(3)
    #if newfilm == True:
    #    filmname = ''
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abcx = 0
    helpmessage = 'Left (remove), Up, Down (select characters) Right (next). Middle (done), Retake (Cancel)'
    vumetermessage('Press enter if you want to leave it untitled')
    cursor = '_'
    blinking = True
    pausetime = time.time()
    while True:
        if newfilm == True:
            message = 'New film name: ' + filmname
        else:
            message = 'Edit film name: ' + filmname
        print(term.clear+term.home)
        print(message+cursor)
        print(helpmessage)
        writemessage(message + cursor)
        vumetermessage(helpmessage)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if event == ' ':
            event = '_'
        if pressed == 'down':
            pausetime = time.time()
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
        elif pressed == 'up':
            pausetime = time.time()
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
        elif pressed == 'right':
            pausetime = time.time()
            if len(filmname) < 30:
                filmname = filmname + abc[abcx]
                cursor = abc[abcx]
            else:
                helpmessage = 'Yo, maximum characters reached bro!'
        elif pressed == 'left' or pressed == 'remove':
            pausetime = time.time()
            if len(filmname) > 0:
                filmname = filmname[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if filmname == '':
                filmname='untitledfilm'
            if len(filmname) > 0:
                if abc[abcx] != '_':
                    filmname = filmname + abc[abcx]
                try:
                    if filmname == oldfilmname:
                        return oldfilmname
                    elif filmname in getfilms(filmfolder)[0]:
                        helpmessage = 'this filmname is already taken! make a sequel!'
                        filmname = filmname+'2'
                    elif '_archive' in filmname:
                        helpmessage = 'the filmname cant be named as an archive.'
                    elif filmname not in getfilms(filmfolder)[0]:
                        logger.info("New film " + filmname)
                        return filmname
                except:
                    logger.info("New film " + filmname)
                    return filmname
        elif pressed == 'retake':
            return oldfilmname
        elif event in abc:
            pausetime = time.time()
            filmname = filmname + event
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(keydelay)


#-------------set bitrate----------------

def get_bitrate(abc, bitrate):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abcx = 0
    helpmessage = 'Up, Down (select bitrate) Right (next). Middle (done), Retake (Cancel)'
    cursor = '_'
    blinking = True
    pausetime = time.time()
    bitrate=int(bitrate/1000)
    menuinput=str(bitrate)
    while True:
        message = 'New bitrate ' + menuinput 
        endmessage = ' kbits/s'
        print(term.clear+term.home)
        print(message+cursor)
        writemessage(message + cursor + endmessage)
        vumetermessage(helpmessage)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if event == ' ':
            event = '_'
        if pressed == 'up':
            pausetime = time.time()
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
            else:
                abcx = 0
                cursor = abc[abcx]
        elif pressed == 'down':
            pausetime = time.time()
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
            else:
                abcx = len(abc) - 1
                cursor = abc[abcx]
        elif pressed == 'right' and abcx != 0:
            pausetime = time.time()
            if len(menuinput) < 7:
                menuinput = menuinput + abc[abcx]
                cursor = abc[abcx]
            else:
                helpmessage = 'Yo, maximum bitrate reached bro!'
        elif pressed == 'left' or pressed == 'remove':
            pausetime = time.time()
            if len(menuinput) > 0:
                menuinput = menuinput[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if abc[abcx] != ' ' or menuinput != '':
                menuinput = menuinput + abc[abcx]
                if int(menuinput) < 65001:
                    logger.info("New bitrate!")
                    bitrate = int(menuinput)
                    return bitrate
                    break
                else:
                    helpmessage = 'in the range of bitrate 1-65000'
        elif pressed == 'retake':
            return '' 
        elif event in abc:
            pausetime = time.time()
            menuinput = menuinput + event
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(keydelay)


#-------------New udp Stream host----------------

def newudp_ip(abc, network):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abcx = 0
    helpmessage = 'Up, Down (select characters) Right (next). Middle (done), Retake (Cancel)'
    cursor = '_'
    blinking = True
    pausetime = time.time()
    ip_network = network.split('.')[:-1]
    ip_network = '.'.join(ip_network)+'.'
    ip = ''
    port=8000
    while True:
        message = 'Host ip and port: ' + ip_network + ip
        print(term.clear+term.home)
        print(message+cursor)
        writemessage(message + cursor)
        vumetermessage(helpmessage)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if event == ' ':
            event = '_'
        if pressed == 'down':
            pausetime = time.time()
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
        elif pressed == 'up':
            pausetime = time.time()
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
        elif pressed == 'right':
            pausetime = time.time()
            if len(ip) < 2:
                ip = ip + abc[abcx]
                cursor = abc[abcx]
            else:
                helpmessage = 'Yo, maximum ip reached bro!'
        elif pressed == 'left' or pressed == 'remove':
            pausetime = time.time()
            if len(ip) > 0:
                ip = ip[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if abc[abcx] != ' ' or ip != '':
                ip = ip + abc[abcx]
                if int(ip) < 256:
                    logger.info("New host " + ip_network+ip)
                    newhost = (ip_network+ip).strip()
                    break
                else:
                    helpmessage = 'in the range of ips 1-256'
        elif pressed == 'retake':
            return '' 
        elif event in abc:
            pausetime = time.time()
            ip = ip + event
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(keydelay)
    ip='800'
    abcx=1
    while True:
        message = 'Host ip and port: ' + newhost + ': ' + ip
        print(term.clear+term.home)
        print(message+cursor)
        writemessage(message + cursor)
        vumetermessage(helpmessage)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if event == ' ':
            event = '_'
        if pressed == 'down':
            pausetime = time.time()
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
        elif pressed == 'up':
            pausetime = time.time()
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
        elif pressed == 'right':
            pausetime = time.time()
            if len(ip) < 4:
                ip = ip + abc[abcx]
                cursor = abc[abcx]
            else:
                helpmessage = 'Yo, maximum ip reached bro!'
        elif pressed == 'left' or pressed == 'remove':
            pausetime = time.time()
            if len(ip) > 0:
                ip = ip[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if abc[abcx] != ' ' or ip != '':
                ip = ip + abc[abcx]
                if int(ip) < 8256:
                    logger.info("New port " +ip)
                    return newhost, (ip).strip()
                else:
                    helpmessage = 'in the range of ips 1-256'
        elif pressed == 'retake':
            return '' 
        elif event in abc:
            pausetime = time.time()
            ip = ip + event
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(keydelay)

#-------------New camera----------------

def newcamera_ip(abc, network):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abcx = 0
    helpmessage = 'Up, Down (select characters) Right (next). Middle (done), Retake (Cancel)'
    cursor = '_'
    blinking = True
    pausetime = time.time()
    ip_network = network.split('.')[:-1]
    ip_network = '.'.join(ip_network)+'.'
    ip = ''
    while True:
        message = 'Camera ip: ' + ip_network + ip
        print(term.clear+term.home)
        print(message+cursor)
        writemessage(message + cursor)
        vumetermessage(helpmessage)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if event == ' ':
            event = '_'
        if pressed == 'down':
            pausetime = time.time()
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
        elif pressed == 'up':
            pausetime = time.time()
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
        elif pressed == 'right':
            pausetime = time.time()
            if len(ip) < 2:
                ip = ip + abc[abcx]
                cursor = abc[abcx]
            else:
                helpmessage = 'Yo, maximum ip reached bro!'
        elif pressed == 'left' or pressed == 'remove':
            pausetime = time.time()
            if len(ip) > 0:
                ip = ip[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if abc[abcx] != ' ' or ip != '':
                ip = ip + abc[abcx]
                if int(ip) < 256:
                    logger.info("New camera " + ip_network+ip)
                    return (ip_network+ip).strip()
                else:
                    helpmessage = 'in the range of ips 1-256'
        elif pressed == 'retake':
            return '' 
        elif event in abc:
            pausetime = time.time()
            ip = ip + event
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(keydelay)

#------------Timelapse--------------------------

def timelapse(beeps,camera,filmname,foldername,filename,between,duration,backlight):
    global fps, soundrate, channels, bitrate, muxing, db, quality
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    sound = False
    selected = 0
    header = 'Adjust delay in seconds between videos'
    menu = 'DELAY:', 'DURATION:', 'SOUND:', 'START', 'BACK'
    oldmenu=''
    while True:
        settings = str(round(between,2)), str(round(duration,2)), str(sound), '', ''
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        seconds = (3600 / between) * duration
        vumetermessage('1 h timelapse filming equals ' + str(round(seconds,2)) + ' second clip   ')
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'up' and menu[selected] == 'DELAY:':
            between = between + 1
        elif pressed == 'down' and menu[selected] == 'DELAY:':
            if between > 1:
                between = between - 1
        if pressed == 'up' and menu[selected] == 'SOUND:':
            sound = True
        elif pressed == 'down' and menu[selected] == 'SOUND:':
            sound = False
        elif pressed == 'up' and menu[selected] == 'DURATION:':
            duration = duration + 0.1
        elif pressed == 'down' and menu[selected] == 'DURATION:':
            if duration > 0.3:
                duration = duration - 0.1
        elif pressed == 'up' or pressed == 'down' and menu[selected] == 'SOUND:':
            if sound == False:
                sound == True
            if sound == True:
                sound == False
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle':
            if menu[selected] == 'START':
                if os.path.isdir(foldername+'timelapse') == False:
                    os.makedirs(foldername + 'timelapse')
                time.sleep(0.02)
                writemessage('Recording timelapse, middlebutton to stop')
                n = 1
                recording = False
                starttime = time.time()
                t = 0
                files = []
                while True:
                    t = time.time() - starttime
                    pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
                    vumetermessage('Timelapse length is now ' + str(round(n * duration,2)) + ' second clip   ')
                    if recording == False and t > between:
                        if beeps > 0:
                            if bus:
                                buzz(150)
                            else:
                                run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep.wav')
                        #camera.start_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', quality=26, bitrate=5000000)
                        #camera.start_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', quality=quality, level=profilelevel, intra_period=5)
                        if bitrate > 1000:
                            camera.split_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)
                        else:
                            camera.split_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', level=profilelevel, intra_period=5, quality = quality)
                        if sound == True:
                            os.system(gonzopifolder+'/alsa-utils-1.1.3/aplay/arecord -D hw:'+str(plughw)+' -f '+soundformat+' -c '+str(channels)+' -r '+soundrate+' -vv '+foldername+'timelapse/'+filename+'_'+str(n).zfill(3)+'.wav &')
                        files.append(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3))
                        starttime = time.time()
                        recording = True
                        n = n + 1
                        t = 0
                    if recording == True:
                        writemessage('Recording timelapse ' + str(n) + ' ' + 'time:' + str(round(t,2)))
                    if recording == False:
                        writemessage('Between timelapse ' + str(n) + ' ' + 'time:' + str(round(t,2)))
                    if t > duration and recording == True:
                        if sound == True:
                            os.system('pkill arecord')
                        #camera.stop_recording()
                        if bitrate > 1000:
                            camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
                        else:
                            camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, quality = quality)   # back to hot standby
                        recording = False
                        starttime = time.time()
                        t = 0
                    if pressed == 'screen':
                        if backlight == False:
                            # requires wiringpi installed
                            run_command('gpio -g pwm 19 1023')
                            backlight = True
                        elif backlight == True:
                            run_command('gpio -g pwm 19 0')
                            backlight = False
                    elif pressed == 'middle' and n > 1:
                        if recording == True:
                            os.system('pkill arecord')
                            #camera.stop_recording()
                            if bitrate > 1000:
                                camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
                            else:
                                camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, quality = quality)   # back to hot standby
                        #create thumbnail
                        try:
                            if film_reso == '1920x1080':
                                camera.capture(foldername + filename + '.jpeg', resize=(800,450), use_video_port=True)
                            elif film_reso == '1920x816':
                                camera.capture(foldername + filename + '.jpeg', resize=(800,340), use_video_port=True)
                        except:
                            logger.warning('something wrong with camera jpeg capture')
                        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                        tot = int(videos_totalt.videos)
                        video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                        writemessage('Compiling timelapse')
                        logger.info('Hold on, rendering ' + str(len(files)) + ' scenes')
                        #RENDER VIDEO
                        print('Rendering videofiles')
                        writemessage('Hold on, rendering timelapse with ' + str(len(files)) + ' files')
                        videosize = 0
                        rendersize = 0
                        scenedir=foldername
                        filename = foldername + filename
                        n = 1
                        videomerge = ['ffmpeg']
                        videomerge.append('-f')
                        videomerge.append('concat')
                        videomerge.append('-safe')
                        videomerge.append('0')
                        run_command('rm '+scenedir+'.renderlist')
                        for f in files[:-1]:
                            compileshot(f+'.h264',filmfolder,filmname)
                            videosize = videosize + countsize(f + '.mp4')
                            #videomerge.append(f + '.mp4')
                            with open(scenedir + '.renderlist', 'a') as l:
                                l.write("file '"+str(f)+".mp4'\n")
                        videomerge.append('-i')
                        videomerge.append(scenedir+'.renderlist')
                        videomerge.append('-c:v')
                        videomerge.append('copy')
                        videomerge.append('-movflags')
                        videomerge.append('+faststart')
                        videomerge.append(video_origins + '.mp4')
                        videomerge.append('-y')
                        #videomerge.append(filename + '.h264')
                        #videomerge.append(filename + '.h264')
                        #call(videomerge, shell=True) #how to insert somekind of estimated time while it does this?
                        p = Popen(videomerge)
                        #show progress
                        while p.poll() is None:
                            time.sleep(0.1)
                            try:
                                rendersize = countsize(filename + '.mp4')
                            except:
                                continue
                            writemessage('video rendering ' + str(int(rendersize)) + ' of ' + str(int(videosize)) + ' kb done')
                        run_command('rm '+scenedir+'.renderlist')
                        print('Video rendered!')
                        os.system('ln -sfr '+video_origins+'.mp4 '+filename+'.mp4')
                        ##RENDER AUDIO
                        writemessage('Rendering sound')
                        audiomerge = ['sox']
                        #if render > 2:
                        #    audiomerge.append(filename + '.wav')
                        for f in files[:-1]:
                            audiomerge.append(f + '.wav')
                        audiomerge.append(filename + '.wav')
                        call(audiomerge, shell=False)
                        ##MAKE AUDIO SILENCE
                        #if sound == False:
                        #    audiosilence(foldername+filename)
                        #cleanup
                        #os.system('rm -r ' + foldername + 'timelapse')
                        vumetermessage('timelapse done! ;)')
                        return filename, between, duration
                    time.sleep(keydelay)
            if menu[selected] == 'BACK':
                vumetermessage('ok!')
                return '', between, duration
        time.sleep(keydelay)

#------------Remove-----------------------

def remove(filmfolder, filmname, scene, shot, take, sceneshotortake):
    flushbutton()
    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
    filename = 'take' + str(take).zfill(3)
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    time.sleep(0.1)
    header = 'Are you sure you want to remove ' + sceneshotortake + '?'
    menu = '', '', ''
    settings = 'NO', 'ARCHIVE', 'YES'
    selected = 0
    otf_scene = countscenes(filmfolder, filmname+'_archive')
    otf_scene += 1
    otf_shot = countshots(filmname+'_archive' , filmfolder, otf_scene)
    otf_shot += 1
    otf_take = counttakes(filmname+'_archive', filmfolder, otf_scene, otf_shot)
    otf_take += 1
    oldmenu=''
    starttime=time.time()
    while True:
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'remove' and time.time()-starttime > 1:
            return
        elif pressed == 'middle':
            if selected == 2:
                if sceneshotortake == 'take':
                    os.system('rm ' + foldername + filename + '.h264')
                    os.system('rm ' + foldername + filename + '.mp4')
                    os.system('rm ' + foldername + filename + '.info')
                    os.system('rm ' + foldername + filename + '.wav')
                    os.system('rm ' + foldername + filename + '.jpeg')
                    os.system('rm ' + foldername + filename + '_thumb.jpeg')
                    return
                elif sceneshotortake == 'shot' and shot > 0:
                    os.system('rm -r ' + foldername)
                    return
                elif sceneshotortake == 'scene':
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                    os.system('rm -r ' + foldername)
                    scene = countscenes(filmfolder, filmname)
                    shot=1
                    take=1
                    return
                elif sceneshotortake == 'film':
                    origin_videos=[]
                    v=organize(filmfolder, filmname)
                    if v == '':
                        return
                    origin_videos.extend(v)
                    for i in origin_videos:
                        print('remove video: '+i)
                        try:
                            os.remove(i)
                        except:
                            pass
                        #time.sleep(3)
                    foldername = filmfolder + filmname
                    os.system('rm -r ' + foldername)
                    return
            if selected == 1:
                if '_archive' in filmname:
                    if sceneshotortake == 'take':
                        os.system('rm ' + foldername + filename + '.h264')
                        os.system('rm ' + foldername + filename + '.mp4')
                        os.system('rm ' + foldername + filename + '.info')
                        os.system('rm ' + foldername + filename + '.wav')
                        os.system('rm ' + foldername + filename + '.jpeg')
                        os.system('rm ' + foldername + filename + '_thumb.jpeg')
                        return
                    elif sceneshotortake == 'shot' and shot > 0:
                        os.system('rm -r ' + foldername)
                        return
                    elif sceneshotortake == 'scene':
                        foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                        os.system('rm -r ' + foldername)
                        scene = countscenes(filmfolder, filmname)
                        shot=1
                        take=1
                        return
                    elif sceneshotortake == 'film':
                        origin_videos=[]
                        v=organize(filmfolder, filmname)
                        if v == '':
                            return
                        origin_videos.extend(v)
                        for i in origin_videos:
                            print('remove video: '+i)
                            try:
                                os.remove(i)
                            except:
                                pass
                            #time.sleep(3)
                        foldername = filmfolder + filmname
                        os.system('rm -r ' + foldername)
                        return
                else:
                    if sceneshotortake == 'take':
                        writemessage('Throwing take in archive' + str(take))
                        #onthefloor = filmfolder + filmname + '_archive/' + 'scene' + str(otf_scene).zfill(3) + '/shot' + str(otf_shot).zfill(3) + '/take' + str(otf_take).zfill(3) 
                        onthefloor = filmfolder + filmname + '_archive/' + 'scene' + str(otf_scene).zfill(3) + '/shot' + str(otf_shot).zfill(3) + '/'
                        if os.path.isdir(onthefloor) == False:
                            os.makedirs(onthefloor)
                        os.system('cp ' + foldername + filename + '.h264 ' + onthefloor + '')
                        os.system('cp ' + foldername + filename + '.mp4 ' + onthefloor + '')
                        os.system('cp ' + foldername + filename + '.info ' + onthefloor + '')
                        os.system('cp ' + foldername + filename + '.wav ' + onthefloor + '')
                        os.system('cp ' + foldername + filename + '.jpeg ' + onthefloor + '')
                        os.system('cp ' + foldername + filename + '_thumb.jpeg ' + onthefloor + '')
                        os.system('rm ' + foldername + filename + '.h264 ')
                        os.system('rm ' + foldername + filename + '.mp4 ')
                        os.system('rm ' + foldername + filename + '.info ')
                        os.system('rm ' + foldername + filename + '.wav ')
                        os.system('rm ' + foldername + filename + '.jpeg ')
                        os.system('rm ' + foldername + filename + '_thumb.jpeg ')
                        os.system('cp -r '+filmfolder + filmname + "/settings.p "+filmfolder + filmname + '_archive/settings.p')
                        take = take - 1
                        if take == 0:
                            take = 1
                    elif sceneshotortake == 'shot' and shot > 0:
                        writemessage('Throwing shot in archive' + str(shot))
                        onthefloor = filmfolder + filmname + '_archive/' + 'scene' + str(otf_scene).zfill(3) + '/shot' + str(otf_shot).zfill(3)+'/'
                        os.makedirs(onthefloor,exist_ok=True)
                        os.system('cp -r '+foldername+'* '+onthefloor)
                        os.system('cp -r '+filmfolder + filmname + "/settings.p "+filmfolder + filmname + '_archive/settings.p')
                        os.system('rm -r '+foldername)
                        take = counttakes(filmname, filmfolder, scene, shot)
                    elif sceneshotortake == 'scene':
                        onthefloor = filmfolder + filmname + '_archive/' + 'scene' + str(otf_scene).zfill(3)
                        os.makedirs(onthefloor)
                        writemessage('Throwing clips in the archive ' + str(scene))
                        foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                        os.system('cp ' + foldername + '/* ' + onthefloor+'/' )
                        os.system('cp -r '+filmfolder + filmname + "/settings.p "+filmfolder + filmname + '_archive/settings.p')
                        os.system('rm -r ' + foldername)
                        scene = countscenes(filmfolder, filmname)
                        shot = 1
                        take = 1
                    elif sceneshotortake == 'film':
                        origin_videos=[]
                        v=organize(filmfolder, filmname)
                        if v == '':
                            return
                        origin_videos.extend(v)
                        for i in origin_videos:
                            print('remove video: '+i)
                            try:
                                os.remove(i)
                            except:
                                pass
                            #time.sleep(3)
                        foldername = filmfolder + filmname
                        os.system('rm -r ' + foldername)
                        return
                    organize(filmfolder, filmname + '_archive')
                return
            elif selected == 0:
                return False
        time.sleep(0.02)

#--------CLEAN---------

def clean(filmname, filmfolder):
    if filmname == '':
        films = getfilms(filmfolder)
    else:
        films.append(filmname)
    videos_to_remove=[]
    origin_videos=[]
    for f in films:
        v=organize(filmfolder, f[0])
        origin_videos.extend(v)
        print(filmfolder)
        print(f[0])
        print(origin_videos)
        #time.sleep(5)
    print('ORIGIN')
    print(origin_videos)
    print('alll')
    allfiles = os.listdir(filmfolder+'.videos/')
    print(allfiles)
    print('all videos: '+ str(len(allfiles)))
    remove_videos=[]
    for video in allfiles:
        if any(filmfolder+'.videos/'+video in x for x in origin_videos):
            #os.remove(origin)
            print('REMOVE ORIGIN VIDEO NOT IN SYNC ' + video)
        else:
            #os.remove(origin)
            if video != 'gonzopi.db':
                remove_videos.append(filmfolder+'.videos/'+video)
            print('ORIGIN VIDEO IN SYNC' + video)
    #print(remove_videos)
    print('all videos: '+ str(len(allfiles)))
    print('origin videos: '+ str(len(origin_videos)))
    print('to be removed: '+ str(len(remove_videos)))
    for i in remove_videos:
        os.remove(i)
    #with open(filmfolder+'.videos/.remove_videos', 'w') as outfile:
    #    outfile.write('\n'.join(str(i) for i in remove_videos))
    #time.sleep(10)

#------------Remove and Organize----------------

def organize(filmfolder, filmname):
    global fps, db
    origin_files=[]
    #remove scenes with .remove
    scenes = next(os.walk(filmfolder + filmname))[1]
    for i in scenes:
        scenefiles = next(os.walk(filmfolder + filmname+'/'+i))[2]
        for s in scenefiles:
            if '.remove' in s:
                logger.info('removing scene')
                os.system('rm -r ' + filmfolder + filmname + '/' + i)
    scenes = next(os.walk(filmfolder + filmname))[1]
    for i in scenes:
        if 'scene' not in i:
            scenes.remove(i)
    # Takes
    for i in sorted(scenes):
        origin_scene_files=[]
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        for p in shots:
            if 'shot' not in p:
                shots.remove(p)
        for p in sorted(shots):
            takes=[]
            takefiles = next(os.walk(filmfolder + filmname + '/' + i + '/' + p))[2]
            for t in takefiles:
                if '.remove' in t:
                    logger.info('removing shot')
                    os.system('rm -r ' + filmfolder + filmname + '/' + i + '/' + p)
                if 'take' in t:
                    takes.append(t)
            if len(takes) == 0:
                logger.info('no takes in this shot, removing shot if no placeholder')
                if not os.path.isfile(filmfolder + filmname + '/' + i + '/' + p + '/.placeholder'):
                    os.system('rm -r ' + filmfolder + filmname + '/' + i + '/' + p)

            organized_nr = 1
            print(i)
            print(p)
            print(sorted(takes))
            #time.sleep(2)
            for s in sorted(takes):
                if 'take' in s:
                    if '.mp4' in s or '.h264' in s:
                        unorganized_nr = int(s[4:7])
                        takename = filmfolder + filmname + '/' + i + '/' + p + '/take' + str(unorganized_nr).zfill(3)
                        if '.mp4' in s:
                            origin=os.path.realpath(takename+'.mp4')
                            if origin != os.path.abspath(takename+'.mp4'):
                                print('appending: '+origin)
                                origin_files.append(origin)
                                origin_scene_files.append(origin)
                                if os.path.isfile(takename+'.h264'):
                                    print('oh no boubles found!')
                            else:
                                videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                                tot = int(videos_totalt.videos)
                                video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
                                print('no sublink for video, create it here')
                                os.system('mv '+takename+'.mp4 '+video_origins+'.mp4')
                                os.system('ln -sfr '+video_origins+'.mp4 '+takename+'.mp4')
                                #time.sleep(1)
                        origin_audio=os.path.realpath(takename+'.wav')
                        if origin_audio != os.path.abspath(takename+'.wav'):
                            print('appending: '+origin_audio)
                            origin_files.append(origin_audio)
                            origin_scene_files.append(origin_audio)
                        else:
                            print('no sublink for sound, create it here')
                            #time.sleep(1)
                            origin=os.path.realpath(takename+'.mp4')
                            os.system('mv '+takename+'.wav '+origin[:-4]+'.wav')
                            os.system('ln -sfr '+origin[:-4]+'.wav '+takename+'.wav')
                        if '.h264' in s:
                            origin=os.path.realpath(takename+'.h264')
                            if origin != os.path.abspath(takename+'.h264'):
                                origin_files.append(origin)
                                origin_scene_files.append(origin)
                        if organized_nr == unorganized_nr:
                            #print('correct')
                            pass
                        if organized_nr != unorganized_nr:
                            print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                            print(s)
                            #time.sleep(3)
                            mv = 'mv ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(unorganized_nr).zfill(3)
                            run_command(mv + '.mp4 ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.mp4')
                            run_command(mv + '.info ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.info')
                            run_command(mv + '.nofaststart ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.nofaststart')
                            run_command(mv + '.h264 ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.h264')
                            run_command(mv + '.wav ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.wav')
                            run_command(mv + '.jpeg ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.jpeg')
                            run_command(mv + '_thumb.jpeg ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '_thumb.jpeg')
                        #check if same video has both h246 and mp4 and render and remove h264
                        for t in sorted(takes):
                            if t.replace('.mp4','') == s.replace('.h264','') or s.replace('.mp4','') == t.replace('.h264',''):
                                logger.info('Found both mp4 and h264 of same video!')
                                logger.info(t)
                                logger.info(s)
                                #time.sleep(5)
                                compileshot(takename,filmfolder,filmname)
                                organized_nr -= 1
                        organized_nr += 1
        origin_files.extend(origin_scene_files)
        with open(filmfolder+filmname+'/'+i+'/.origin_videos', 'w') as outfile:
            outfile.write('\n'.join(str(i) for i in origin_scene_files))

    # Shots
    for i in sorted(scenes):
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        if len(shots) == 0:
            logger.info('no shots in this scene, removing scene..')
            os.system('rm -r ' + filmfolder + filmname + '/' + i)
        organized_nr = 1
        for p in sorted(shots):
            if 'insert' in p:
                #add_organize(filmfolder, filmname)
                pass
            elif 'shot' in p:
                #print(p)
                if '_yanked' in p:
                    unorganized_nr = int(p[4:-7])
                else:
                    unorganized_nr = int(p[-3:])
                if organized_nr == unorganized_nr:
                    #print('correct')
                    pass
                if organized_nr != unorganized_nr:
                    #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                    os.system('mv ' + filmfolder + filmname + '/' + i + '/shot' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
                organized_nr += 1

    # Scenes
    organized_nr = 1
    for i in sorted(scenes):
        if 'insert' in i:
            #add_organize(filmfolder, filmname)
            pass
        elif 'scene' in i:
            #print(i)
            if '_yanked' in i:
                unorganized_nr = int(i[5:-7])
            else:
                unorganized_nr = int(i[-3:])
            if organized_nr == unorganized_nr:
                #print('correct')
                pass
            if organized_nr != unorganized_nr:
                #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                os.system('mv ' + filmfolder + filmname + '/scene' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
            organized_nr += 1

    logger.info('Organizer done! Everything is tidy')
    return origin_files


#------------Add and Organize----------------

def add_organize(filmfolder, filmname):
    scenes = next(os.walk(filmfolder + filmname))[1]
    for i in scenes:
        if 'scene' not in i:
            scenes.remove(i)
    # Shots
    for i in sorted(scenes):
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        for c in shots:
            if 'shot' not in c:
                shots.remove(c)
        organized_nr = len(shots)
        for p in sorted(shots, reverse=True):
            if '_yanked' in p:
                print(p)
                #time.sleep(5)
                os.system('mv -n ' + filmfolder + filmname + '/' + i + '/' + p + ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
            #if _insert in last shot
            elif organized_nr==len(shots) and '_insert' in p:
                os.system('mv -n ' + filmfolder + filmname + '/' + i + '/' +p+ ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
            elif '_insert' in p:
                os.system('mv -n ' + filmfolder + filmname + '/' + i + '/' +p+ ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
                #run_command('touch ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3) + '/.placeholder')
            elif 'shot' in p:
                #print(p)
                unorganized_nr = int(p[-3:])
                if organized_nr == unorganized_nr:
                    #print('correct')
                    pass
                if organized_nr != unorganized_nr:
                    #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                    os.system('mv -n ' + filmfolder + filmname + '/' + i + '/shot' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3)) 
            organized_nr -= 1

    # Scenes
    organized_nr = len(scenes)
    for i in sorted(scenes, reverse=True):
        #print(i)
        if '_yanked' in i:
            os.system('mv -n ' + filmfolder + filmname + '/'+i+' '+ filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
        elif organized_nr==len(scenes) and '_insert' in i:
            os.system('mv -n ' + filmfolder + filmname + '/'+i+' '+ filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
        elif '_insert' in i:
            #print(p)
            os.system('mv -n ' + filmfolder + filmname + '/' +i+' '+ filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
            run_command('touch ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3) + '/.placeholder')
        elif 'scene' in i:
            #print(i)
            unorganized_nr = int(i[-3:])
            if organized_nr == unorganized_nr:
                #print('correct')
                pass
            if organized_nr != unorganized_nr:
                #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                os.system('mv -n ' + filmfolder + filmname + '/scene' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
        organized_nr -= 1
    return

#------------Organize and move dubs----------------

def organizedubs(foldername):
    dubs = next(os.walk(foldername))[2]
    print(dubs)
    time.sleep(3)
    for c in dubs:
        if 'dub' not in c:
            dubs.remove(c)
    organized_nr = len(dubs)
    for p in sorted(dubs, reverse=True):
        print(p)
        time.sleep(3)
        if '_insert' in p:
            os.system('mv -n ' + foldername + 'dub' + str(organized_nr).zfill(3) + '_insert.wav ' + foldername + 'dub' + str(organized_nr).zfill(3)+'.wav')
        elif 'dub' in p:
            print(p)
            time.sleep(3)
            unorganized_nr = int(p[5:-4])
            if organized_nr == unorganized_nr:
                print('correct')
                time.sleep(3)
                pass
            if organized_nr != unorganized_nr:
                print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                time.sleep(3)
                os.system('mv -n ' + foldername + 'dub' + str(unorganized_nr).zfill(3) + '.wav ' + foldername + 'dub' + str(organized_nr).zfill(3)+'.wav') 
        organized_nr -= 1

#-------------Stretch Audio--------------

def stretchaudio(filename,fps):
    global film_fps,filmfolder
    fps_rounded=round(fps)
    if int(fps_rounded) != int(film_fps):
        #pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
        #videolength = pipe.decode().strip()
        videolength=get_video_length(filename+'.mp4')
        try:
            #pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + filename + '.wav', shell=True)
            #audiolength = pipe.decode().strip()
            audiolength = get_audio_length(filename+'.wav')
        except:
            audiosilence(filename)
            audiolength=videolength
        #if there is no audio length
        logger.info('audio is:' + str(audiolength))
        ratio = int(audiolength)/int(videolength)
        print(str(ratio))
        #run_command('cp '+filename+'.wav '+filename+'_temp.wav')
        run_command('ffmpeg -y -i ' + filename + '.wav -filter:a atempo="'+str(ratio) + '" ' + filmfolder + '.tmp/'+filename+'.wav')
        run_command('cp '+filmfolder+'.tmp/'+filename+'.wav '+filename+'.wav')
        os.remove(filmfolder+'.tmp/'+filename+'.wav')
    #time.sleep(5)
    return

#---------#ffmpeg settings------------

def encoder():
    global bitrate
    return '-c:v h264_omx -profile:v high -level:v 4.2 -preset slow -bsf:v h264_metadata=level=4.2 -g 1 -b:v '+str(bitrate)+' -c:a copy '
    #return '-c:v copy -c:a copy '

def has_audio_track(file_path):
    try:
        # Parse the media file
        media_info = MediaInfo.parse(file_path)
        
        # Check for audio tracks
        for track in media_info.tracks:
            if track.track_type == "Audio":
                return True
        return False

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def check_fps(file_path):
    try:
        # Parse the media file
        media_info = MediaInfo.parse(file_path)
        
        # Check for audio tracks
        for track in media_info.tracks:
            if track.track_type == "Video":
                return track.frame_rate
        return None
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def check_reso(file_path):
    try:
        # Parse the media file
        media_info = MediaInfo.parse(file_path)
        
        # Check for audio tracks
        for track in media_info.tracks:
            if track.track_type == "Video":
                return track.width, track.height
        return None
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def is_audio_stereo(file_path):
    try:
        # Parse the media file
        media_info = MediaInfo.parse(file_path)
        
        # Check for audio tracks
        for track in media_info.tracks:
            if track.track_type == "Audio":
                if track.channel_s == 1:
                    return False
                if track.channel_s == 2:
                    return True
        return None
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def get_video_length_str(filepath):
    video_origins = (os.path.realpath(filepath))
    try:
        if os.path.isfile(filepath[:-3]+'nofaststart') == True:
            with open(filepath[:-3]+'nofaststart', 'r') as f:
                duration_ms = f.readline().strip()
                print('duration in ms: ' + str(duration_ms))
            return str(datetime.timedelta(seconds=round(int(duration_ms)/1000)))
    except:
        pass
    try:
        if os.path.isfile(filepath[:-3]+'info') == True:
            with open(filepath[:-3]+'info', 'r') as f:
                duration_ms = f.readline().strip()
                print('duration in ms: ' + str(duration_ms))
            return str(datetime.timedelta(seconds=round(int(duration_ms)/1000)))
    except:
        pass
    #try:
        #video_db=db.select('videos', where='filename="'+video_origins+'"')[0]
        #return str(datetime.timedelta(seconds=round(video_db.videolength)))
    #except:
    #    pass
    # Parse the file
    try:
        media_info = MediaInfo.parse(filepath)
    except:
        return
    # Find the video track (usually the first video track)
    for track in media_info.tracks:
        if track.track_type == "Video":
            # Duration is in milliseconds, convert to seconds
            duration_ms = track.duration
            if duration_ms is None:
                return None  # No duration found
            db.update('videos', where='filename="'+video_origins+'"', videolength=duration_ms/1000)
            with open(filepath[:-3] + 'info', 'w') as f:
                f.write(str(duration_ms))
            return str(datetime.timedelta(seconds=round(duration_ms/1000)))
            #return int(duration_ms)
    return None  # No video track found

def get_video_length(filepath):
    global db
    video_origins = (os.path.realpath(filepath))
    try:
        media_info = MediaInfo.parse(filepath)
    except:
        return
    # Find the video track (usually the first video track)
    for track in media_info.tracks:
        if track.track_type == "Video":
            # Duration is in milliseconds, convert to seconds
            duration_ms = track.duration
            if duration_ms is None:
                return 0  # No duration found
            db.update('videos', where='filename="'+video_origins+'"', videolength=duration_ms/1000)
            with open(filepath[:-3] + 'info', 'w') as f:
                f.write(str(duration_ms))
            return int(duration_ms)
            #return int(duration_ms)
    return 0  # No video track found


def get_audio_length(filepath):
    # Parse the file
    media_info = MediaInfo.parse(filepath)
    # Find the video track (usually the first video track)
    for track in media_info.tracks:
        if track.track_type == "Audio":
            # Duration is in milliseconds, convert to seconds
            duration_ms = track.duration
            if duration_ms is None:
                return None  # No duration found
            return int(duration_ms)
    return None  # No video track found

#-------------Compile Shot--------------

def compileshot(filename,filmfolder,filmname):
    global fps, soundrate, channels, bitrate, muxing, db, film_fps
    videolength=0
    audiolength=0 
    #Check if file already converted
    if '.h264' in filename:
        filename=filename.replace('.h264','')
    if '.mp4' in filename:
        filename=filename.replace('.mp4','')
    if os.path.isfile(filename + '.h264'):
        logger.info('Video not converted!')
        writemessage('Converting to playable video')
        #remove old mp4 if corrupted like if an unpredicted shutdown in middle of converting
        video_origins = (os.path.realpath(filename+'.h264'))[:-5]
        os.system('rm ' + filename + '.mp4')
        os.system('rm ' + video_origins + '.mp4')
        print(filename+'.mp4 removed!')
        #run_command('ffmpeg -fps 25 -add ' + video_origins + '.h264 ' + video_origins + '.mp4')
        #run_command('ffmpeg -fps 25 -add ' + video_origins + '.h264 ' + video_origins + '.mp4')
        #run_command('ffmpeg -i ' + video_origins + '.h264 -c:v h264_omx -profile:v high -level:v 4.2 -preset slower -bsf:v h264_metadata=level=4.2 -g 1 -b:v '+str(bitrate)+' '+ video_origins + '.mp4')
        #run_command('ffmpeg -fflags +genpts -r 25 -i ' + video_origins + '.h264 '+encoder()+ video_origins + '.mp4')
        ffmpeg_cmd = ['ffmpeg','-i', video_origins+'.h264', '-fflags', '+genpts+igndts', '-c:v', 'copy', '-movflags', 'frag_keyframe+empty_moov', '-level:v', '4.2', '-g', '1', '-r', str(film_fps), '-f', 'mp4', video_origins+'.mp4', '-loglevel','debug', '-y']
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd)
        stdout, stderr = ffmpeg_process.communicate()
        #os.system('ln -sfr '+video_origins+'.mp4 '+filename+'.mp4')
        print(filename+'.h264 converted to mp4')
    video_origins = (os.path.realpath(filename+'.mp4'))[:-4]
    vumetermessage('checking video audio length...')
    videolength = get_video_length(filename+'.mp4')
    print('videolength:'+str(videolength))
    if not os.path.isfile(filename + '.wav'):
        vumetermessage('creating audio track...')
        audiosilence(filename)
        try:
            db.update('videos', where='filename="'+video_origins+'.mp4"', videolength=videolength/1000)
        except:
            db = correct_database(filmname,filmfolder,db)
            db.update('videos', where='filename="'+video_origins+'.mp4"', videolength=videolength/1000)
    #add audio/video start delay sync
    try:
        audiolength = get_audio_length(filename+'.wav')
    except:
        audiolength=videolength
        #if there is no audio length
        vumetermessage('creating audio track...')
        audiosilence(filename)
    #fps_rounded=round(fps)
    #if int(fps) != int(film_fps):
    #    vumetermessage('stretching audio...')
    #    stretchaudio(filename,fps)
    if int(audiolength) != int(videolength):
        vumetermessage('trimming audio to video...')
        audiosync, videolength, audiolength = audiotrim(filename, 'end','')
        try:
            db.update('videos', where='filename="'+video_origins+'.mp4"', audiolength=audiolength/1000, audiosync=audiosync)
        except:
            db = correct_database(filmname,filmfolder,db)
            db.update('videos', where='filename="'+video_origins+'.mp4"', audiolength=audiolength/1000, audiosync=audiosync)
    #one more if stereo check!
    stereo = is_audio_stereo(filename+'.wav')
    if stereo == False:
        run_command('sox -V0 -b 16 '+filename+'.wav -c 2 '+filmfolder+'.tmp/temp.wav')
        run_command('mv '+filmfolder+'.tmp/temp.wav '+ filename + '.wav')
        os.system('rm '+filmfolder+'.tmp/temp.wav')
    logger.info('audio is:' + str(audiolength))
    #mux=False
    ifaudio = get_audio_length(filename+'.mp4')
    if muxing == True and ifaudio == None :
        #muxing mp3 layer to mp4 file
        #count estimated audio filesize with a bitrate of 320 kb/s
        audiosize = countsize(filename + '.wav') * 0.453
        p = Popen(['ffmpeg', '-y', '-i', filename + '.wav', '-acodec', 'libmp3lame', '-ac', '2', '-b:a', '320k', filename + '.mp3'])
        while p.poll() is None:
            time.sleep(0.2)
            try:
                rendersize = countsize(filename + '.mp3')
            except:
                continue
            writemessage('audio rendering ' + str(int(rendersize)) + ' of ' + str(int(audiosize)) + ' kb done')
        ##MERGE AUDIO & VIDEO
        writemessage('Merging audio & video')
        #os.remove(renderfilename + '.mp4') 
        call(['MP4Box', '-rem', '2',  video_origins + '.mp4'], shell=False)
        call(['MP4Box', '-fps', str(film_fps), '-add', video_origins + '.mp4', '-add', filename + '.mp3', '-new', video_origins + '_tmp.mp4'], shell=False)
        os.system('cp -f ' + video_origins + '_tmp.mp4 ' + video_origins + '.mp4')
        os.remove(video_origins + '_tmp.mp4')
        os.remove(filename + '.mp3')
    #origin=os.path.realpath(filename+'.mp4')
    os.system('rm ' + video_origins + '.h264')
    #os.system('rm ' + filename + '.h264')
    #os.system('ln -sfr '+video_origins+'.mp4 '+filename+'.mp4')
    logger.info('compile done!')
    #run_command('omxplayer --layer 3 ' + filmfolder + '/.rendered/' + filename + '.mp4 &')
    #time.sleep(0.8)
    #run_command('aplay ' + foldername + filename + '.wav')
    return

#-------------Get shot files--------------

def shotfiles(filmfolder, filmname, scene):
    files = []
    shots = countshots(filmname,filmfolder,scene)
    print("shots"+str(shots))
    shot = 1
    for i in range(shots):
        takes = counttakes(filmname,filmfolder,scene,shot)
        if takes > 0:
            folder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
            filename = 'take' + str(takes).zfill(3)
            files.append(folder + filename)
            print(folder+filename)
        shot = shot + 1
    #writemessage(str(len(shotfiles)))
    #time.sleep(2)
    return files

#--------Show JPEG as progress when rendering

#---------------Render Video------------------

def rendervideo(filmfolder, filmname, scene, filmfiles, filename, renderinfo):
    videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
    rendered_video = filmfolder+'.rendered/'+filmname+'_scene' + str(scene).zfill(3)
    os.makedirs(filmfolder+'.rendered',exist_ok=True)
    tot = int(videos_totalt.videos)
    #video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
    if scene == 0:
        scenedir = filmfolder + filmname + '/'
    if len(filmfiles) < 1:
        writemessage('Nothing here!')
        time.sleep(2)
        return None
    print('Rendering videofiles')
    writemessage('Hold on, rendering ' + renderinfo + ' with ' + str(len(filmfiles)) + ' files')
    videosize = 0
    rendersize = 0
    #videomerge = ['MP4Box']
    #videomerge.append('-force-cat')
    #for f in filmfiles[:]:
    #    videosize = videosize + countsize(f + '.mp4')
    #    videomerge.append('-cat')
    #    videomerge.append(f + '.mp4#video')
    #videomerge.append('-new')
    #videomerge.append(filename + '.mp4')
    videomerge = ['ffmpeg']
    videomerge.append('-f')
    videomerge.append('concat')
    videomerge.append('-safe')
    videomerge.append('0')
    run_command('rm '+scenedir+'.renderlist')
    for f in filmfiles[:]:
        videosize = videosize + countsize(f + '.mp4')
        #videomerge.append(f + '.mp4')
        with open(scenedir + '.renderlist', 'a') as l:
            l.write("file '"+str(f)+".mp4'\n")
    videomerge.append('-i')
    videomerge.append(scenedir+'.renderlist')
    videomerge.append('-an')
    videomerge.append('-c:v')
    videomerge.append('copy')
    videomerge.append('-movflags')
    videomerge.append('+faststart')
    videomerge.append(rendered_video+'.mp4')
    videomerge.append('-y')
    #videomerge.append(filename + '.h264')
    #videomerge.append(filename + '.h264')
    #call(videomerge, shell=True) #how to insert somekind of estimated time while it does this?
    p = Popen(videomerge)
    #show progress
    while p.poll() is None:
        time.sleep(0.1)
        try:
            rendersize = countsize(rendered_video+'.mp4')
        except:
            continue
        writemessage('video rendering ' + str(int(rendersize)) + ' of ' + str(int(videosize)) + ' kb done')
    print('Video rendered!')
    os.system('ln -sfr '+rendered_video+'.mp4 '+filename+'.mp4')
    run_command('rm '+scenedir+'.renderlist')
    return

#---------------Render Audio----------------

def renderaudio(filmfolder, filmname, scene, audiofiles, filename, dubfiles, dubmix):
    #if len(audiofiles) < 1:
    #    writemessage('Nothing here!')
    #    time.sleep(2)
    #    return None
    #
    #check if shot or take and put them in .rendered folder
    if audiofiles == filename:
        rendered_audio=filename
    else:
        rendered_audio = filmfolder+'.rendered/'+filmname+'_scene' + str(scene).zfill(3)
        os.makedirs(filmfolder+'.rendered',exist_ok=True)
    print('Rendering audiofiles')
    ##PASTE AUDIO TOGETHER
    writemessage('Hold on, rendering audio...')
    audiomerge = ['sox']
    #if render > 2:
    #    audiomerge.append(filename + '.wav')
    if isinstance(audiofiles, list):
        for f in audiofiles:
            audiomerge.append(f + '.wav')
        audiomerge.append(rendered_audio + '.wav')
        call(audiomerge, shell=False)
    else:
        #if rendering scene with one shot
        if audiofiles[0] != filename:
            os.system('cp '+audiofiles[0]+'.wav '+rendered_audio+'.wav')
    os.system('ln -sfr '+rendered_audio+'.wav '+filename+'.wav')
    #DUBBING
    p = 1
    #pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
    #videolength = pipe.decode().strip()
    try:
        videolength = get_video_length(filename+'.mp4')
    except:
        videolength = 0
    try:
        audiolength = get_audio_length(filename+'.wav')
    except:
        audiosilence(filename)
        audiolength = get_audio_length(filename+'.wav')
    if audiolength == None:
        audiosilence(filename)
        audiolength = get_audio_length(filename+'.wav')
    if videolength != 0 and videolength != None:
        if audiolength > videolength:
            audiotrim(filename, 'end','')
    if audiolength < videolength:
        print('FUUUUUUUUUUUU')
        #time.sleep(5)
    for i, d in zip(dubmix, dubfiles):
        writemessage('Dub ' + str(p) + ' audio found lets mix...')
        #first trimit!
        #audiotrim(filename, 'end', d)
        try:
            #pipe = subprocess.check_output('soxi -D ' + d, shell=True)
            #dubaudiolength = pipe.decode()
            dubaudiolength=get_audio_length(d)
            if dubaudiolength != videolength:
                print('dub wrong length!')
                #time.sleep(5)
        except:
            pass
        #print(d)
        #print(filename)
        #time.sleep(3)
        os.system('cp ' + filename + '.wav ' + filename + '_tmp.wav')
        #Fade and make stereo
        run_command('sox -V0 -b 16 -G ' + d + ' -c 2 '+filmfolder+'.tmp/fade.wav fade ' + str(round(i[2],1)) + ' 0 ' + str(round(i[3],1)))
        run_command('sox -V0 -b 16 -G -m -v ' + str(round(i[0],1)) + ' '+filmfolder+'.tmp/fade.wav -v ' + str(round(i[1],1)) + ' ' + filename + '_tmp.wav -c 2 ' + rendered_audio + '.wav trim 0 ' + str(videolength))
        os.system('ln -sfr '+rendered_audio+'.wav '+filename+'.wav')
        try:
            os.remove(filename + '_tmp.wav')
            os.remove(''+filmfolder+'.tmp/fade.wav')
        except:
            pass
        print('Dub mix ' + str(p) + ' done!')
        p += 1
    try:
        videolength = get_video_length(filename+'.mp4')
    except:
        videolength = 0
    try:
        audiolength = get_audio_length(filename+'.wav')
    except:
        audiosilence(filename)
        audiolength = get_audio_length(filename+'.wav')
    if int(audiolength) != int(videolength):
        vumetermessage('trimming audio to video...')
        audiosync, videolength, audiolength = audiotrim(filename, 'end','')
    return

#-------------Fast Edit-----------------
def fastedit(filmfolder, filmname, filmfiles, scene):
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
    totlength = 0
    try:
        os.remove(scenedir + '.fastedit')
    except:
        print('no fastedit file')
    #for f in filmfiles:
        #pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + f + '.mp4', shell=True)
        #videolength = pipe.decode().strip()
        #totlength = int(videolength) + totlength
        #print('writing shot lengths for fastedit mode')
        #with open(scenedir + '.fastedit', 'a') as f:
        #    f.write(str(totlength)+'\n')


def check_faststart(file_path):
    try:
        # Load the media file
        media_info = MediaInfo.parse(file_path)
        
        # Check if the file is MP4
        for track in media_info.tracks:
            if track.track_type == "General":
                if track.format.lower() not in ["mpeg-4", "mp4"]:
                    print(f"Error: '{file_path}' is not an MP4 file.")
                # Check for IsStreamable field
                is_streamable = track.to_data().get("is_streamable", "").lower()
                if is_streamable == "yes":
                    print(f"Faststart is enabled for '{file_path}' (IsStreamable: Yes).")
                elif is_streamable == "no":
                    print(f"Faststart is NOT enabled for '{file_path}' (IsStreamable: No).")
                
                # Fallback: Check MOOV atom position (if IsStreamable is not explicitly set)
                # MediaInfo doesn't always provide direct MOOV position, so we infer from file structure
                if "moov" in track.to_data().get("other_file_format", "").lower():
                    print(f"Faststart is likely enabled for '{file_path}' (MOOV atom detected).")
                    return True
                else:
                    print(f"Faststart is NOT enabled for '{file_path}' (MOOV atom not at start).")
                    return False
                return
        
        print(f"Error: No general track found in '{file_path}'.")
    
    except Exception as e:
        print(f"Error analyzing '{file_path}': {str(e)}")


#-------------Get scene files--------------

def scenefiles(filmfolder, filmname):
    files = []
    scenes = countscenes(filmfolder,filmname)
    scene = 1
    while scene <= scenes:
        folder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/'
        filename = 'scene'
        files.append(folder + filename)
        scene = scene + 1
    #writemessage(str(len(shotfiles)))
    #time.sleep(2)
    return files

#-------------Render Shot-------------

def rendershot(filmfolder, filmname, renderfilename, scene, shot):
    global fps, take, rendermenu, updatethumb, bitrate, muxing, db, film_fps
    if os.path.exists(renderfilename + '.mp4') == False:
        print('no file')
        return
    #This function checks and calls rendervideo & renderaudio if something has changed in the film
    #Video
    vumetermessage('render shot '+renderfilename)
    video_origins = (os.path.realpath(renderfilename+'.mp4'))[:-4]
    def render(q, filmfolder, filmname, renderfilename, scene, shot):
        global fps, take, rendermenu, updatethumb, bitrate, muxing, db
        video_origins = (os.path.realpath(renderfilename+'.mp4'))[:-4]
        videohash = ''
        oldvideohash = ''
        scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
        #return if no file
        # Video Hash
        #if os.path.isfile(renderfilename + '.h264') == True:
        #new logic here (check for video length if takes more than a second asume no faststart)
        video_db=db.select('videos', where='filename="'+video_origins+'.mp4"')
        faststart=True
        try:
            if video_db[0].faststart == 0:
                faststart=False
                print('faststart is not, making video faststart ready')
                time.sleep(3)
        except:
            faststart = True
            print('video faststart ready!')
            pass
        #if faststart == False:
        if os.path.isfile(renderfilename+'.nofaststart') == True:
            faststart=False
        #if check_faststart(renderfilename+'.mp4') == False:
        #if os.path.isfile(renderfilename+'.nofaststart') == True:
        if faststart == False:
            tmp=filmfolder+'.tmp/'+filmname+'_'+str(scene).zfill(3)+'_'+str(shot).zfill(3)+'.mp4'
            vumetermessage('found new clip compiling...')
            #os.system('mv ' + video_origins + '.mp4 ' + video_origins + '_tmp.mp4')
            call(['ffmpeg', '-i', video_origins + '.mp4', '-r', str(film_fps), '-fflags', '+genpts+igndts', '-vsync', '1', '-c:v', 'copy', '-movflags', '+faststart', tmp, '-y'], shell=False)
            os.system('cp ' + tmp + ' ' + video_origins + '.mp4')
            run_command('rm '+tmp)
            try:
                db.update('videos', where='filename="'+video_origins+'.mp4"', faststart=True)
            except:
                db = correct_database(filmname,filmfolder,db)
                db.update('videos', where='filename="'+video_origins+'.mp4"', faststart=True)
            print('trimming audio standard gap from start 0.013s')
            vumetermessage('trimming and syncing audio...')
            audio_origins = (os.path.realpath(renderfilename+'.wav'))[:-4]
            audiolength = get_audio_length(audio_origins+'.wav')
            videolength = get_video_length(video_origins+'.mp4')
            print('fuuuuuu:'+str(audiolength)+' '+str(videolength))
            #time.sleep(3)
            #if audiolength > videolength: 
            run_command('sox -V0 -b 16 '+audio_origins+'.wav -c 2 '+filmfolder+'.tmp/temp.wav trim 0.013')
            #run_command('ffmpeg -i '+filmfolder+'.tmp/temp.wav -filter:a atempo=1.00033703703703703706 '+filmfolder+'.tmp/temp2.wav')
            #run_command('ffmpeg -i '+filmfolder+'.tmp/temp.wav -t '+str(round(videolength/1000, 3))+' -filter:a "rubberband=tempo=0.9995" '+filmfolder+'.tmp/temp2.wav')
            run_command('mv '+filmfolder+'.tmp/temp.wav '+ audio_origins+'.wav')
            os.system('rm '+filmfolder+'.tmp/temp.wav')
            #os.system('rm '+filmfolder+'.tmp/temp2.wav')
            audiolength = get_audio_length(audio_origins+'.wav')
            videolength = get_video_length(video_origins+'.mp4')
            print('fuuuuuu:'+str(audiolength)+' '+str(videolength))
            #time.sleep(3)
            compileshot(renderfilename,filmfolder,filmname)
            run_command('rm '+renderfilename+'.nofaststart')
            audiohash = str(int(countsize(renderfilename + '.wav')))
            with open(scenedir + '.audiohash', 'w') as f:
                f.write(audiohash)
        if os.path.isfile(renderfilename + '.mp4') == True:
            videohash = videohash + str(int(countsize(renderfilename + '.mp4')))
            print('Videohash of shot is: ' + videohash)
            #time.sleep(3)
            #if something shutdown in middle of process
            #elif os.path.isfile(renderfilename + '_tmp.mp4') == True:
            #    os.system('cp ' + renderfilename + '_tmp.mp4 ' + renderfilename + '.mp4')
        else:
            vumetermessage('Nothing here to play hit record')
            status='',''
            q.put(status)
        #if os.path.isfile(renderfilename + '.h264') and os.path.isfile(renderfilename + '.mp4'):
        #    os.system('rm ' + renderfilename + '.h264 ')
        # Check if video corrupt
        renderfix = False
        if not os.path.isfile(renderfilename + '.wav'):
            vumetermessage('creating audio track...')
            audiosilence(renderfilename)
            renderfix = True
        if os.path.isfile(renderfilename + '.jpeg') == False: 
            run_command('ffmpeg -sseof -1 -i ' + renderfilename + '.mp4 -update 1 -q:v 1 -vf scale=800:450 ' + renderfilename + '.jpeg')
            run_command('ffmpeg -sseof -1 -i ' + renderfilename + '.mp4 -update 1 -q:v 1 -vf scale=80:45 ' + renderfilename + '_thumb.jpeg')
        #try:
        #    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + renderfilename + '.mp4', shell=True)
        #    videolength = pipe.decode().strip()
        #except:
        #    videolength = ''
        #print('Shot length ' + videolength)
        #if videolength == '':
        #    print('Okey, shot file not found or is corrupted')
        #    # For backwards compatibility remove old rendered scene files
        #    # run_command('rm ' + renderfilename + '*')
        #    status='',''
        #    q.put(status)

        #EDITS AND FX
        trimfile = ''
        if os.path.isfile(scenedir+'.split') == True:
            settings = pickle.load(open(scenedir + ".split", "rb"))
            split_list = settings
            logger.info("settings loaded")
            nr=1
            for i in split_list:
                if nr == 1:
                    #make first split as a new take in the original shot
                    newshotdir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                    newtakename = 'take' + str(counttakes2(newshotdir)).zfill(3)
                    if i[0][0] < i[0][1]:
                        videotrim(filmfolder,scenedir,i[1],'both', i[0][0],i[0][1],'take')
                    #newtakename = 'take' + str(1).zfill(3)
                elif nr > 1:
                    #then make new shots
                    newshotdir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot-1).zfill(3) + '_insert/'
                    newtakename = 'take' + str(1).zfill(3)
                    try:
                        os.makedirs(newshotdir)
                    except:
                        print('is there already prob')
                    if i[0][0] < i[0][1]:
                        videotrim(filmfolder,scenedir,i[1],'both', i[0][0],i[0][1],newshotdir+newtakename)
                    add_organize(filmfolder, filmname)
                organize(filmfolder, filmname)
                organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,1)
                #vumetermessage('Shot ' + str(shot) + ' inserted')
                updatethumb = True
                time.sleep(1)
                nr=nr+1
                shot=shot+1
            os.remove(scenedir+'.split')
            take=counttakes2(scenedir)
            updatethumb=True
            rendermenu = True
            newaudiomix = True
            renderfilename = scenedir+'take' + str(counttakes2(scenedir)).zfill(3)
        elif os.path.isfile(scenedir+'.beginning') == True and os.path.isfile(scenedir+'.end') == True:
            settings = pickle.load(open(scenedir + ".beginning", "rb"))
            s, trimfile = settings
            logger.info("settings loaded")
            trimfile = 'take' + str(counttakes2(scenedir)).zfill(3)
            renderfilename=scenedir+trimfile
            settings = pickle.load(open(scenedir + ".end", "rb"))
            t, trimfile = settings
            logger.info("settings loaded")
            videotrim(filmfolder,scenedir,trimfile,'both', s,t,'take')
            os.remove(scenedir+'.beginning')
            os.remove(scenedir+'.end')
            take=counttakes2(scenedir)
            updatethumb=True
            rendermenu = True
            newaudiomix = True
            renderfilename = scenedir+'take' + str(counttakes2(scenedir)).zfill(3)
        elif os.path.isfile(scenedir+'.beginning') == True:
            settings = pickle.load(open(scenedir + ".beginning", "rb"))
            s, trimfile = settings
            logger.info("settings loaded")
            videotrim(filmfolder,scenedir,trimfile,'beginning', s, 0,'take')
            os.remove(scenedir+'.beginning')
            newaudiomix = True
            take=counttakes2(scenedir)
            updatethumb=True
            rendermenu = True
            trimfile = 'take' + str(counttakes2(scenedir)).zfill(3)
            renderfilename=scenedir+trimfile
        elif os.path.isfile(scenedir+'.end') == True:
            settings = pickle.load(open(scenedir + ".end", "rb"))
            if trimfile == '':
                s, trimfile = settings
            else:
                p, trimfileoriginal = settings
                s=p-s
            logger.info("settings loaded")
            videotrim(filmfolder,scenedir,trimfile,'end', s, 0,'take')
            os.remove(scenedir+'.end')
            take=counttakes2(scenedir)
            updatethumb=True
            rendermenu = True
            newaudiomix = True
            renderfilename = scenedir+'take' + str(counttakes2(scenedir)).zfill(3)
        ###---------TITLES----------
        if os.path.isfile(scenedir+'title/title001.png') == True:
            videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
            tot = int(videos_totalt.videos)
            video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
            #compileshot(scenedir+'blend/'+blendmodes[blendselect]+'.h264',filmfolder,filmname)
            run_command('ffmpeg -y -i '+renderfilename+'.mp4 -i '+scenedir+'title/title001.png '+encoder()+'-filter_complex "[0:v][1:v]overlay=0:0:enable=\'between(t,2,8)\'[v]" -map "[v]" -map 0:a? '+filmfolder+'.tmp/title.mp4')
            screen_filename = scenedir+'take' + str(counttakes2(scenedir)+1).zfill(3)
            run_command('cp ' + renderfilename + '.wav ' + screen_filename + '.wav')
            #make a new sublink
            run_command('cp '+filmfolder+'.tmp/title.mp4 '+video_origins+'.mp4')
            os.system('ln -sfr '+video_origins+'.mp4 '+screen_filename+'.mp4')
            run_command('rm '+filmfolder+'.tmp/title.mp4')
            run_command('rm -r title/title001.png')
            run_command('ffmpeg -y -sseof -1 -i ' + screen_filename + '.mp4 -update 1 -q:v 1 -vf scale=800:450 ' + screen_filename + '.jpeg')
            #ffmpeg -i blendtest.mp4 -i blendtest3.mp4 -filter_complex "blend=screen" output2.mp4
            newaudiomix = True
            take=counttakes2(scenedir)
            renderfilename = scenedir+'take' + str(counttakes2(scenedir)).zfill(3)
            updatethumb=True
            rendermenu = True
            newaudiomix = True
        ###---------BLEND----------
        if os.path.isfile(scenedir+'blend/'+blendmodes[blendselect]+'.mp4') == True:
            videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
            tot = int(videos_totalt.videos)
            video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
            #compileshot(scenedir+'blend/'+blendmodes[blendselect]+'.h264',filmfolder,filmname)
            call(['MP4Box', '-rem', '2', scenedir+'blend/'+blendmodes[blendselect] + '.mp4'], shell=False)
            run_command('ffmpeg -y -i '+renderfilename+'.mp4 -i '+scenedir+'blend/'+blendmodes[blendselect]+'.mp4 '+encoder()+'-filter_complex "blend='+blendmodes[blendselect]+'" -an '+filmfolder+'.tmp/blend.mp4')
            #run_command('ffmpeg -y -i '+renderfilename+'.mp4 -i '+scenedir+'blend/'+blendmodes[blendselect]+'.mp4 '+encoder()+'-filter_complex "[0:v][1:v]blend=all_mode='+blendmodes[blendselect]+':all_opacity=0.5[v]" -map "[v]" -an '+filmfolder+'.tmp/blend.mp4')
            screen_filename = scenedir+'take' + str(counttakes2(scenedir)+1).zfill(3)
            run_command('cp ' + renderfilename + '.wav ' + screen_filename + '.wav')
            #make a new sublink
            run_command('cp '+filmfolder+'.tmp/blend.mp4 '+video_origins+'.mp4')
            os.system('ln -sfr '+video_origins+'.mp4 '+screen_filename+'.mp4')
            run_command('rm '+filmfolder+'.tmp/blend.mp4')
            run_command('rm '+scenedir+'blend/'+blendmodes[blendselect]+'.mp4')
            run_command('ffmpeg -y -sseof -1 -i ' + screen_filename + '.mp4 -update 1 -q:v 1 -vf scale=800:450 ' + screen_filename + '.jpeg')
            #ffmpeg -i blendtest.mp4 -i blendtest3.mp4 -filter_complex "blend=screen" output2.mp4
            newaudiomix = True
            take=counttakes2(scenedir)
            renderfilename = scenedir+'take' + str(counttakes2(scenedir)).zfill(3)
            updatethumb=True
            rendermenu = True
            newaudiomix = True
        ###---------CROSSFADE--------
        if os.path.isfile(scenedir+'.crossfade') == True:
            settings = pickle.load(open(scenedir + ".crossfade", "rb"))
            s, trimfile = settings
            logger.info("settings loaded")
            videolength=0
            foldername = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
            crossfade_folder = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot+1).zfill(3) + '/'
            crossfade_filename = 'take' + str(counttakes2(crossfade_folder)).zfill(3)
            filename = trimfile
            compileshot(crossfade_folder+crossfade_filename,crossfade_folder,filmname)
            pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + foldername+filename + '.mp4', shell=True)
            videolength = pipe.decode().strip()
            videolength=(int(videolength)/1000)-0.2
            pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + crossfade_folder+ crossfade_filename + '.mp4', shell=True)
            videolength2 = pipe.decode().strip()
            videolength2=(int(videolength2)/1000)-0.2
            if videolength > int(s)/2:
                if videolength2 > int(s)/2:           
                    #crossfade(scenedir,trimfile,'end', s)
                    crossfade_start = int(videolength)-crossfade
                    output = scenedir+'take' + str(counttakes2(scenedir)+1).zfill(3)
                    run_command('ffmpeg -y -i '+renderfilename+'.mp4 -i '+crossfade_folder+crossfade_filename+'.mp4 -filter_complex "xfade=offset='+str(crossfade_start)+':duration='+str(crossfade)+'" '+output+'.mp4')
                    run_command('ffmpeg -y -i '+renderfilename+'.wav -i '+crossfade_folder+crossfade_filename+'.wav -filter_complex "acrossfade=d='+str(crossfade)+'" '+output+'.wav')
                    run_command('ffmpeg -y -sseof -1 -i ' + output + '.mp4 -update 1 -q:v 1 -vf scale=800:450 ' + output + '.jpeg')
                    os.remove(scenedir+'.crossfade')
                    #ffmpeg -i blendtest.mp4 -i blendtest.mp4 -filter_complex "xfade=offset=4.5:duration=1" output3.mp4
                    #crossfade()
        try:
            with open(scenedir + '.videohash', 'r') as f:
                oldvideohash = f.readline().strip()
            print('oldvideohash is: ' + oldvideohash)
        except:
            print('no videohash found, making one...')
            with open(scenedir + '.videohash', 'w') as f:
                f.write(videohash)
        #Audio
        lasttake = counttakes(filmname, filmfolder, scene, shot)
        lasttakefilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take' + str(lasttake).zfill(3) 
        audiohash = ''
        oldaudiohash = ''
        newaudiomix = False
        if lasttakefilename == renderfilename:
            audiohash += str(int(countsize(renderfilename + '.wav')))
            dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, shot)
            for p in dubfiles:
                audiohash += str(int(countsize(p)))
            print('Audiohash of shot is: ' + audiohash)
            try:
                with open(scenedir + '.audiohash', 'r') as f:
                    oldaudiohash = f.readline().strip()
                print('oldaudiohash is: ' + oldaudiohash)
            except:
                print('no audiohash found, making one...')
                with open(scenedir + '.audiohash', 'w') as f:
                    f.write(audiohash)
            if audiohash != oldaudiohash or newmix == True or renderfix == True:
                print('rerendering')
                #check if sound file exist
                if os.path.isfile(renderfilename+'.wav') == False:
                    logger.info('no sound, creating empty audio track')
                    audiosilence(renderfilename)
                #time.sleep(3)
                #make scene rerender
                os.system('touch '+filmfolder + filmname + '/scene' + str(scene).zfill(3)+'/.rerender')
                #copy original sound
                if os.path.exists(scenedir+'dub') == True:
                    os.system('cp '+scenedir+'dub/original.wav '+renderfilename+'.wav')
                #os.system('cp '+dubfolder+'original.wav '+renderfilename+'.wav')
                renderaudio(filmfolder, filmname, scene, renderfilename, renderfilename, dubfiles, dubmix)
                print('updating audiohash...')
                with open(scenedir + '.audiohash', 'w') as f:
                    f.write(audiohash)
                for i in range(len(dubfiles)):
                    os.system('cp ' + scenedir + '/dub/.settings' + str(i + 1).zfill(3) + ' ' + scenedir + '/dub/.rendered' + str(i + 1).zfill(3))
                print('Audio rendered!')
                newaudiomix = True
                logger.info('compile done!')
            else:
                print('Already rendered!')
            #muxings=False
            ifaudio = get_audio_length(renderfilename+'.mp4')
            if muxing == True and ifaudio == None:
                #muxing mp3 layer to mp4 file
                #count estimated audio filesize with a bitrate of 320 kb/s
                audiosize = countsize(renderfilename + '.wav') * 0.453
                p = Popen(['ffmpeg', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-ac', '2', '-b:a', '320k', renderfilename + '.mp3'])
                while p.poll() is None:
                    time.sleep(0.2)
                    try:
                        rendersize = countsize(renderfilename + '.mp3')
                    except:
                        continue
                    writemessage('audio rendering ' + str(int(rendersize)) + ' of ' + str(int(audiosize)) + ' kb done')
                ##MERGE AUDIO & VIDEO
                writemessage('Merging audio & video')
                #os.remove(renderfilename + '.mp4') 
                call(['MP4Box', '-rem', '2',  video_origins + '.mp4'], shell=False)
                call(['MP4Box', '-fps', str(film_fps), '-add', video_origins + '.mp4', '-add', renderfilename + '.mp3', '-new', video_origins + '_tmp.mp4'], shell=False)
                os.system('cp -f ' + video_origins + '_tmp.mp4 ' + video_origins + '.mp4')
                try:
                    os.remove(video_origins + '_tmp.mp4')
                    os.remove(renderfilename + '.mp3')
                except:
                    print('nothing to remove')
            #origin=os.path.realpath(renderfilename+'.mp4')
            #os.system('rm ' + filename + '.h264')
            #os.system('rm /dev/shm/temp.wav')
            #os.system('ln -sfr '+video_origins+'.mp4 '+filename+'.mp4')
        status=renderfilename,newaudiomix
        q.put(status)
    q = mp.Queue()
    proc = mp.Process(target=render, args=(q, filmfolder, filmname, renderfilename, scene, shot))
    proc.start()
    procdone = False
    status = ''
    while True:
        if proc.is_alive() == False and procdone == False:
            status = q.get()
            print(status)
            procdone = True
            proc.join()
            renderfilename,newaudiomix = status
            vumetermessage(renderfilename+'.mp4')
            break
        if middlebutton() == True:
            proc.terminate()
            proc.join()
            procdone = True
            q=''
            os.system('pkill MP4Box')
            vumetermessage('canceled for now, maybe u want to render later ;)')
            writemessage('press any button to continue')
            print('canceling videorender')
            renderfilename = ''
            newaudiomix=''
            break
        time.sleep(0.0555)
    return renderfilename, newaudiomix

#-------------Render Scene-------------

def renderscene(filmfolder, filmname, scene):
    global fps, muxing
    #dont start muxing individual shots or scenes lol
    mux = False
    if muxing == True:
        mux = True
        muxing = False
    #This function checks and calls rendervideo & renderaudio if something has changed in the film
    #Video
    videohash = ''
    oldvideohash = ''
    filmfiles = shotfiles(filmfolder, filmname, scene)
    renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene'
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
    # Check if video corrupt
    renderfixscene = False
    renderfix=False
    #try:
    #    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + renderfilename + '.mp4', shell=True)
    #    videolength = pipe.decode().strip()
    #except:
    #    videolength = ''
    #    renderfixscene = True
    #print('Scene length ' + videolength)
    #if videolength == '':
    #    print('Okey, hold your horses, rendering!')
    #    # For backwards compatibility remove old rendered scene files
    #    #run_command('rm ' + renderfilename + '.mp4')
    #    #run_command('rm ' + renderfilename + '.wav')
    #    #vumetermessage('corrupted scene file! removing, please render again')
    #    renderfixscene = True
    #    #return '', ''
    # Video Hash
    for p in filmfiles:
        #compileshot(p,filmfolder,filmname)
        #print(p)
        #time.sleep(5)
        scene = int(p.rsplit('scene',1)[1][:3])
        shot = int(p.rsplit('shot',1)[1][:3])
        #remove audio track
        #call(['MP4Box', '-rem', '2',  p], shell=False)
        rendershotname, renderfix = rendershot(filmfolder, filmname, p, scene, shot)
        if renderfix == True:
            renderfixscene = True
        if rendershotname:
            try: 
                videohash = videohash + str(int(countsize(p + '.mp4')))
            except:
                print('no file? ')
    filmfiles = shotfiles(filmfolder, filmname, scene)
    for p in filmfiles:
        scene = int(p.rsplit('scene',1)[1][:3])
        shot = int(p.rsplit('shot',1)[1][:3])
        #call(['MP4Box', '-rem', '2',  p+'.mp4'], shell=False)
        rendershotname, renderfix = rendershot(filmfolder, filmname, p, scene, shot)
        if renderfix == True:
            renderfixscene = True
        if rendershotname:
            try: 
                videohash = videohash + str(int(countsize(p + '.mp4')))
            except:
                print('no file? ')
    print('Videohash of scene is: ' + videohash)
    try:
        with open(scenedir + '.videohash', 'r') as f:
            oldvideohash = f.readline().strip()
        print('oldvideohash is: ' + oldvideohash)
    except:
        print('no videohash found, making one...')
        with open(scenedir + '.videohash', 'w') as f:
            f.write(videohash)
    print('renderfix is:'+str(renderfixscene))
    # Render if needed
    if videohash != oldvideohash or renderfixscene == True:
        run_command('rm '+renderfilename+'.info')
        #remove audio track
        call(['MP4Box', '-rem', '2', renderfilename+'.mp4'], shell=False)
        rendervideo(filmfolder,filmname,scene,filmfiles, renderfilename, 'scene ' + str(scene))
        #fastedit(filmfolder, filmname, filmfiles, scene)
        #run_command('cp '+renderfilename+ '.mp4 '+renderfilename+'_tmp.mp4')
        #call(['ffmpeg', '-i', renderfilename + '_tmp.mp4', '-r', '25', '-vsync', '1', '-c:v', 'copy', '-fflags', '+genpts+igndts', '-movflags', '+faststart', renderfilename+'.mp4', '-y'], shell=False)
        #call(['ffmpeg', '-i', renderfilename + '_tmp.mp4', '-r', '25', '-c:v', 'copy', '-movflags', '+faststart', renderfilename+'.mp4', '-y'], shell=False)
        try:
            os.remove(renderfilename + '_tmp.mp4')
        except:
            pass
        print('updating videohash...')
        with open(scenedir + '.videohash', 'w') as f:
            f.write(videohash)
    #time.sleep(3)

    #Audio
    audiohash = ''
    oldaudiohash = ''
    newaudiomix = False
    for p in filmfiles:
        try:
            audiohash += str(int(countsize(p + '.wav')))
        except:
            audiohash=0
            renderfix=True
    dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, 0)
    print(dubfiles)
    for p in dubfiles:
        try:
            audiohash += str(int(countsize(p)))
        except:
            audiohash=0
    print('Audiohash of scene is: ' + audiohash)
    try:
        with open(scenedir + '.audiohash', 'r') as f:
            oldaudiohash = f.readline().strip()
        print('oldaudiohash is: ' + oldaudiohash)
    except:
        print('no audiohash found, making one...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash) 
        renderfixscene=True
    if os.path.isfile(scenedir+'/.rerender') == True:
        renderfixscene=True
        os.system('rm '+scenedir+'/.rerender')
    if audiohash != oldaudiohash or newmix == True or renderfix == True or renderfixscene == True:
        renderaudio(filmfolder, filmname, scene, filmfiles, renderfilename, dubfiles, dubmix)
        print('updating audiohash...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
        for i in range(len(dubfiles)):
            os.system('cp ' + scenedir + '/dub/.settings' + str(i + 1).zfill(3) + ' ' + scenedir + '/dub/.rendered' + str(i + 1).zfill(3))
        print('Audio rendered!')
        newaudiomix = True
        #os.system('mv ' + renderfilename + '.mp4 ' + renderfilename + '_tmp.mp4')
    else:
        print('Already rendered!')
    #dont mux scenes for now
    #mux = False
    ifaudio = get_audio_length(renderfilename+'.mp4')
    if mux == True and ifaudio == None:
        muxing = True
        #muxing mp3 layer to mp4 file
        #count estimated audio filesize with a bitrate of 320 kb/s
        try:
            audiosize = countsize(renderfilename + '.wav') * 0.453
        except:
            print('noothing here')
        os.system('mv ' + renderfilename + '.mp4 ' + renderfilename + '_tmp.mp4')
        if debianversion == 'stretch':
            p = Popen(['avconv', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-ac', '2', '-b:a', '320k', renderfilename + '.mp3'])
        else:
            p = Popen(['ffmpeg', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-ac', '2', '-b:a', '320k', renderfilename + '.mp3'])
        while p.poll() is None:
            time.sleep(0.02)
            try:
                rendersize = countsize(renderfilename + '.mp3')
            except:
                continue
            writemessage('audio rendering ' + str(int(rendersize)) + ' of ' + str(int(audiosize)) + ' kb done')
        ##MERGE AUDIO & VIDEO
        writemessage('Merging audio & video')
        #os.remove(renderfilename + '.mp4') 
        call(['MP4Box', '-rem', '2',  renderfilename + '_tmp.mp4'], shell=False)
        #call(['MP4Box', '-inter', '40', '-v', renderfilename + '.mp4'], shell=False)
        call(['MP4Box', '-add', renderfilename + '_tmp.mp4', '-add', renderfilename + '.mp3', '-new', renderfilename + '.mp4'], shell=False)
        #call(['ffmpeg', '-i', renderfilename + '_tmp.mp4', '-r', '25', '-fflags', '+genpts+igndts', '-vsync', '1', '-c:v', 'copy', '-c:a', 'copy', '-movflags', 'faststart', renderfilename+'.mp4', '-y'], shell=False)
        os.remove(renderfilename + '_tmp.mp4')
        os.remove(renderfilename + '.mp3')
    return renderfilename, newaudiomix

#-------------Render film------------

def renderfilm(filmfolder, filmname, comp, scene):
    global fps, muxing
    def render(q, filmfolder, filmname, comp, scene):
        global fps, muxing
        #dont start muxing individual shots or scenes lol
        mux = False
        if muxing == True:
            mux = True
            muxing = False
        newaudiomix = False
        #if comp == 1:
        #    newaudiomix = True
        #This function checks and calls renderscene first then rendervideo & renderaudio if something has changed in the film
        if scene > 0:
            scenefilename, audiomix = renderscene(filmfolder, filmname, scene)
            q.put(scenefilename)
            return
        scenes = countscenes(filmfolder, filmname)
        for i in range(scenes):

            scenefilename, audiomix = renderscene(filmfolder, filmname, i + 1)
            #Check if a scene has a new audiomix
            print('audiomix of scene ' + str(i + 1) + ' is ' + str(audiomix))
            if audiomix == True:
                newaudiomix = True
            scenefilename, audiomix = renderscene(filmfolder, filmname, i + 1)
            #Check if a scene has a new audiomix
            print('audiomix of scene ' + str(i + 1) + ' is ' + str(audiomix))
            if audiomix == True:
                newaudiomix = True
        filmfiles = scenefiles(filmfolder, filmname)
        #Video
        videohash = ''
        oldvideohash = ''
        renderfilename = filmfolder + filmname + '/' + filmname
        filmdir = filmfolder + filmname + '/'
        scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
        for p in filmfiles:
            print(p)
            #compileshot(p,filmfolder,filmname)
            videohash += str(int(countsize(p + '.mp4')))
        print('Videohash of film is: ' + videohash)
        try:
            with open(filmdir + '.videohash', 'r') as f:
                oldvideohash = f.readline().strip()
            print('oldvideohash is: ' + oldvideohash)
        except:
            print('no videohash found, making one...')
            with open(filmdir + '.videohash', 'w') as f:
                f.write(videohash)
        if videohash != oldvideohash:
            rendervideo(filmfolder,filmname,scene,filmfiles, renderfilename, filmname)
            print('updating video hash')
            with open(filmdir + '.videohash', 'w') as f:
                f.write(videohash)
        #Audio
        audiohash = ''
        oldaudiohash = ''
        for p in filmfiles:
            print(p)
            audiohash += str(int(countsize(p + '.wav')))
        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, 0, 0)
        for p in dubfiles:
            audiohash += str(int(countsize(p)))
        print('Audiohash of film is: ' + audiohash)
        try:
            with open(filmdir + '.audiohash', 'r') as f:
                oldaudiohash = f.readline().strip()
            print('oldaudiohash is: ' + oldaudiohash)
        except:
            print('no audiohash found, making one...')
            with open(filmdir+ '.audiohash', 'w') as f:
                f.write(audiohash)
        #This is if the scene has a new audiomix
        if newaudiomix == True:
            newmix = True
        if audiohash != oldaudiohash or newmix == True:
            renderaudio(filmfolder, filmname, scene, filmfiles, renderfilename, dubfiles, dubmix)
            print('updating audiohash...')
            with open(filmdir+ '.audiohash', 'w') as f:
                f.write(audiohash)
            for i in range(len(dubfiles)):
                os.system('cp ' + filmdir + '/dub/.settings' + str(i + 1).zfill(3) + ' ' + filmdir + '/dub/.rendered' + str(i + 1).zfill(3))
            print('Audio rendered!')
            #compressing
            if comp > 0:
                writemessage('compressing audio')
                os.system('mv ' + renderfilename + '.wav ' + renderfilename + '_tmp.wav')
                #run_command('sox ' + renderfilename + '_tmp.wav ' + renderfilename + '.wav compand 0.3,1 6:-70,-60,-20 -5 -90 0.2')
                run_command('sox ' + renderfilename + '_tmp.wav ' + renderfilename + '.wav compand 0.0,1 6:-70,-43,-20 -6 -90 0.1')
                os.remove(renderfilename + '_tmp.wav')
        else:
            print('Already rendered!')
        #muxing = True
        ifaudio = get_audio_length(renderfilename+'.mp4')
        if mux == True and ifaudio == None:
            muxing = True
            #muxing mp3 layer to mp4 file
            #count estimated audio filesize with a bitrate of 320 kb/s
            audiosize = countsize(renderfilename + '.wav') * 0.453
            os.system('mv ' + renderfilename + '.mp4 ' + renderfilename + '_tmp.mp4')
            if debianversion == 'stretch':
                p = Popen(['avconv', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-ac', '2', '-b:a', '320k', renderfilename + '.mp3'])
            else:
                p = Popen(['ffmpeg', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-ac', '2', '-b:a', '320k', renderfilename + '.mp3'])
            while p.poll() is None:
                time.sleep(0.02)
                try:
                    rendersize = countsize(renderfilename + '.mp3')
                except:
                    continue
                writemessage('audio rendering ' + str(int(rendersize)) + ' of ' + str(int(audiosize)) + ' kb done')
            ##MERGE AUDIO & VIDEO
            writemessage('Merging audio & video')
            #os.remove(renderfilename + '.mp4') 
            call(['MP4Box', '-rem', '2',  renderfilename + '_tmp.mp4'], shell=False)
            #call(['MP4Box', '-inter', '40', '-v', renderfilename + '_tmp.mp4'], shell=False)
            #call(['ffmpeg', '-i', renderfilename + '_tmp.mp4', '-c', 'copy', '-movflags', 'faststart', renderfilename+'.mp4', '-y'], shell=False)
            p = Popen(['MP4Box', '-add', renderfilename + '_tmp.mp4', '-add', renderfilename + '.mp3', '-new', renderfilename + '.mp4'], shell=False)
            while p.poll() is None:
                time.sleep(0.02)
                try:
                    rendersize = countsize(renderfilename + '.mp4')
                except:
                    continue
                writemessage('audio & video merging ' + str(int(rendersize)) + ' of ' + str(int(audiosize)) + ' kb done')
            os.remove(renderfilename + '_tmp.mp4')
            os.remove(renderfilename + '.mp3')
        q.put(renderfilename)
    q = mp.Queue()
    proc = mp.Process(target=render, args=(q,filmfolder,filmname,comp,scene))
    proc.start()
    procdone = False
    status = ''
    while True:
        if proc.is_alive() == False and procdone == False:
            status = q.get()
            print(status)
            procdone = True
            proc.join()
            renderfilename = status
            vumetermessage(status+'.mp4')
            break
        if middlebutton() == True:
            proc.terminate()
            proc.join()
            procdone = True
            q=''
            os.system('pkill MP4Box')
            vumetermessage('canceled for now, maybe u want to render later ;)')
            writemessage('press any button to continue')
            print('canceling videorender')
            renderfilename = ''
            break
    return renderfilename

#-------------Get dub files-----------

def getdubs(filmfolder, filmname, scene, shot):
    #search for dub files
    print('getting scene dubs')
    dubfiles = []
    dubmix = []
    rerender = False
    if filmname == None and scene == None and shot == None:
        filefolder = filmfolder
    elif scene > 0 and shot == 0:
        filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/dub/'
    elif scene > 0 and shot > 0:
        filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/dub/'
    else:
        filefolder = filmfolder + filmname + '/dub/'
    try:
        allfiles = os.listdir(filefolder)
    except:
        print('no dubs')
        return dubfiles, dubmix, rerender
    for a in allfiles:
        if 'dub' in a:
            print('Dub audio found! ' + filefolder + a)
            dubfiles.append(filefolder + a)
            dubfiles.sort()
    #check if dub mix has changed
    dubnr = 1
    for i in dubfiles:
        dub = []
        rendered_dub = []
        try:
            with open(filefolder + '.settings' + str(dubnr).zfill(3), 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                dub.append(float(i))
            print('dub ' + str(dubnr).zfill(3) + ' loaded!')
            print(dub)
        except:
            print('cant find settings file')
            dub = [1.0, 1.0, 0.0, 0.0]
            with open(filefolder + ".settings" + str(dubnr).zfill(3), "w") as f:
                for i in dub:
                    f.write(str(i) + '\n')
        try:
            with open(filefolder + '.rendered' + str(dubnr).zfill(3), 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                rendered_dub.append(float(i))
            print('rendered dub loaded')
            print(rendered_dub)
        except:
            print('no rendered dubmix found!')
        if rendered_dub != dub:
            rerender = True
        dubmix.append(dub)
        dubnr += 1
    return dubfiles, dubmix, rerender

#------------Remove Dubs----------------

def removedub(dubfolder, dubnr):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    header = 'Are you sure you want to remove dub ' + str(dubnr) + '?'
    menu = 'NO', 'YES'
    settings = '', ''
    oldmenu=''
    while True:
        writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(menu) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and selected == 0:
            logger.info('dont remove dub')
            time.sleep(0.3)
            break
        elif pressed == 'middle' and selected == 1: 
            os.system('rm ' + dubfolder + 'dub' + str(dubnr).zfill(3) + '.wav')
            os.system('rm ' + dubfolder + '.settings' + str(dubnr).zfill(3))
            os.system('rm ' + dubfolder + '.rendered' + str(dubnr).zfill(3))
            time.sleep(0.5)
            print(dubfolder)
            dubs = next(os.walk(dubfolder))[2]
            print(dubs)
            for i in dubs:
                if 'dub' not in i:
                    dubs.remove(i)
            organized_nr = 1
            for s in sorted(dubs):
                if '.wav' in s and 'dub' in s:
                    print(s)
                    unorganized_nr = int(s[3:-4])
                    if organized_nr == unorganized_nr:
                        print('correct')
                        pass
                    if organized_nr != unorganized_nr:
                        print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                        run_command('mv ' + dubfolder + 'dub' + str(unorganized_nr).zfill(3) + '.wav ' + dubfolder + 'dub' + str(organized_nr).zfill(3) + '.wav')
                        run_command('mv ' + dubfolder + '.settings' + str(unorganized_nr).zfill(3) + ' ' + dubfolder + '.settings' + str(organized_nr).zfill(3))
                        run_command('mv ' + dubfolder + '.rendered' + str(unorganized_nr).zfill(3) + ' ' + dubfolder + '.rendered' + str(organized_nr).zfill(3))
                    organized_nr += 1
            logger.info('removed dub file!')
            vumetermessage('dub removed!')
            break
        time.sleep(0.05)

#-------------Clip settings---------------

def clipsettings(filmfolder, filmname, scene, shot, take, plughw, yanked):
    vumetermessage('press record, view or retake to be dubbing')
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    dubfiles = []
    dubmix = []
    dubmix_old = []
    if scene > 0 and shot == 0:
        header = 'Scene ' + str(scene) + ' dubbing settings'
        filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/dub/'
        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, 0)
    elif scene > 0 and shot > 0:
        header = 'Scene ' + str(scene) + ' shot ' + str(shot) + ' dubbing settings'
        filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/dub/'
        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, shot)
    else:
        header = 'Film ' + filmname + ' dubbing settings'
        filefolder = filmfolder + filmname + '/dub/'
        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, 0, 0)
    newdub = [1.0, 1.0, 0.1, 0.1]
    dubselected = len(dubfiles) - 1
    dubrecord = ''
    oldmenu=''
    while True:
        nmix = round(newdub[0],1)
        ndub = round(newdub[1],1)
        nfadein = round(newdub[2],1)
        nfadeout = round(newdub[3],1)
        if dubfiles:
            mix = round(dubmix[dubselected][0],1)
            dub = round(dubmix[dubselected][1],1)
            fadein = round(dubmix[dubselected][2],1)
            fadeout = round(dubmix[dubselected][3],1)
            menu = 'BACK', 'ADD:', '', '', 'DUB' + str(dubselected + 1) + ':', '', '', ''
            settings = '', 'd:' + str(nmix) + '/o:' + str(ndub), 'in:' + str(nfadein), 'out:' + str(nfadeout), '', 'd:' + str(mix) + '/o' + str(dub), 'in:' + str(fadein), 'out:' + str(fadeout), ''
        else:
            menu = 'BACK', 'ADD:', '', ''
            settings = '', 'd:' + str(nmix) + '/o:' + str(ndub), 'in:' + str(nfadein), 'out:' + str(nfadeout), ''
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)

        #NEW DUB SETTINGS
        if pressed == 'up' and selected == 1:
            if newdub[0] > 0.99 and newdub[1] > 0.01:
                newdub[1] -= 0.1
            if newdub[1] > 0.99 and newdub[0] < 0.99:
                newdub[0] += 0.1
        elif pressed == 'down' and selected == 1:
            if newdub[1] > 0.99 and newdub[0] > 0.01:
                newdub[0] -= 0.1
            if newdub[0] > 0.99 and newdub[1] < 0.99:
                newdub[1] += 0.1
        elif pressed == 'up' and selected == 2:
            newdub[2] += 0.1
        elif pressed == 'down' and selected == 2:
            if newdub[2] > 0.01:
                newdub[2] -= 0.1
        elif pressed == 'up' and selected == 3:
            newdub[3] += 0.1
        elif pressed == 'down' and selected == 3:
            if newdub[3] > 0.01:
                newdub[3] -= 0.1
        elif pressed == 'insert' and yanked != '':
            os.makedirs(filefolder, exist_ok=True)
            dubmix.append(newdub)
            dubrecord = filefolder + 'dub' + str(len(dubfiles)+1).zfill(3) + '.wav'
            os.system('cp '+yanked+'.wav '+dubrecord)
            vumetermessage('dub' + yanked + ' pasted!')
            dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, shot)
            dubselected = len(dubfiles) - 1
            dubrecord=''
            yanked = ''
        elif pressed == 'record' or pressed == 'middle' and selected == 1:
            dubmix.append(newdub)
            dubrecord = filefolder + 'dub' + str(len(dubfiles)+1).zfill(3) + '.wav'
            break
        elif pressed == 'retake' and selected == 4:
            dubrecord = filefolder + 'dub' + str(dubselected + 1).zfill(3) + '.wav'
            break
        #DUB SETTINGS
        elif pressed == 'up' and selected == 4:
            if dubselected + 1 < len(dubfiles):
                dubselected = dubselected + 1
        elif pressed == 'down' and selected == 4:
            if dubselected > 0:
                dubselected = dubselected - 1
        elif pressed == 'move' and selected == 4:
            vumetermessage('press insert button to move dub')
            movedub = filefolder + 'dub' + str(dubselected + 1).zfill(3) + '.wav'
        elif pressed == 'copy':
            vumetermessage('dub' + str(dubselected + 1).zfill(3)+' copied!')
            yanked = filefolder + 'dub' + str(dubselected + 1).zfill(3)
        elif pressed == 'insert' and selected == 4:
            vumetermessage('moving dub please hold on')
            pastedub = filefolder + 'dub' + str(dubselected + 1).zfill(3) + '_insert.wav'
            os.system('mv -n ' + movedub + ' ' + pastedub)
            organizedubs(filefolder)
            pastedub=''
        elif pressed == 'remove' and selected == 4:
            removedub(filefolder, dubselected + 1)
            dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, shot)
            dubselected = len(dubfiles) - 1
            if len(dubfiles) == 0:
                #save original sound
                saveoriginal = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take'+str(take).zfill(3)+'.wav'
                print('no dubs, copying original sound to original')
                os.system('cp '+filefolder+'original.wav '+saveoriginal)
                #removedub folder
                os.system('rm -r ' + filefolder)
                time.sleep(1)
                selected = 0
        elif pressed == 'up' and selected == 5:
            if dubmix[dubselected][0] >= 0.99 and dubmix[dubselected][1] > 0.01:
                dubmix[dubselected][1] -= 0.1
            if dubmix[dubselected][1] >= 0.99 and dubmix[dubselected][0] < 0.99:
                dubmix[dubselected][0] += 0.1
        elif pressed == 'down' and selected == 5:
            if dubmix[dubselected][1] >= 0.99 and dubmix[dubselected][0] > 0.01:
                dubmix[dubselected][0] -= 0.1
            if dubmix[dubselected][0] >= 0.99 and dubmix[dubselected][1] < 0.99:
                dubmix[dubselected][1] += 0.1
        elif pressed == 'up' and selected == 6:
            dubmix[dubselected][2] += 0.1
        elif pressed == 'down' and selected == 6:
            if dubmix[dubselected][2] > 0.01:
                dubmix[dubselected][2] -= 0.1
        elif pressed == 'up' and selected == 7:
            dubmix[dubselected][3] += 0.1
        elif pressed == 'down' and selected == 7:
            if dubmix[dubselected][3] > 0.01:
                dubmix[dubselected][3] -= 0.1
        if pressed == 'right':
            if selected < (len(settings)-2):
                selected = selected + 1
            else:
                selected = 0
            selected == 0
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
            else:
                selected = len(settings) - 2
        elif pressed == 'middle' and menu[selected] == 'BACK':
            os.system('pkill aplay')
            break
        elif pressed == 'views': # mix dub and listen
            run_command('pkill aplay')
            dubfiles, dubmix, rerender = getdubs(filmfolder, filmname, scene, shot)
            if scene:
                filename = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/scene'
                renderfilename = renderfilm(filmfolder, filmname, 0, scene)
                playdub(filmname,renderfilename, 'scene',take)
            elif shot and scene:
                filename = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(scene).zfill(3)+'/shot'
                renderfilename = renderfilm(filmfolder, filmname, 0, scene)
                playdub(filmname,renderfilename, 'shot',take)
            else:
                filename = filmfolder + filmname + '/' + filmname
        time.sleep(0.05)
    #Save dubmix before returning
    if dubmix != dubmix_old:
        if os.path.isdir(filefolder) == False:
            os.makedirs(filefolder)
        c = 1
        for i in dubmix:
            with open(filefolder + ".settings" + str(c).zfill(3), "w") as f:
                for p in i:
                    f.write(str(round(p,1)) + '\n')
                    print(str(round(p,1)))
            c += 1
        dubmix_old = dubmix
    return dubrecord, yanked

#---------------Play & DUB--------------------

def playdub(filmname, filename, player_menu, take):
    global headphoneslevel, miclevel, plughw, channels, filmfolder, scene, soundrate, soundformat, showhelp, camera, overlay, overlay2, gonzopifolder, i2cbuttons, film_fps, film_reso
    #camera.stop_preview()
    #overlay = removeimage(camera, overlay)
    reso_w=film_reso.split('x')[0]
    reso_h=film_reso.split('x')[1]
    if film_reso == '1920x1080':
        screen_reso_w='800'
        screen_reso_h='475'
        topspace='15'
    elif film_reso == '1920x816':
        screen_reso_w='800'
        screen_reso_h='415'
        topspace='75'
    takename = 'take' + str(take).zfill(3)
    if i2cbuttons == False:
        hdmi_mode=True
    else:
        hdmi_mode=False
    if showhelp == True:
        overlay2 = removeimage(camera, overlay2)
        overlay2 = displayimage(camera, gonzopifolder+'/extras/view-buttons.png', overlay, 4)
    #read fastedit file
    if player_menu == 'scene':
        scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
        try:
            with open(scenedir + '.fastedit', 'r') as f:
                fastedit = f.read().splitlines()
                print(fastedit)
        except:
            print('no fastedit file found')
            fastedit = 9999999
    #omxplayer hack
    os.system('rm /tmp/omxplayer*')
    video = True
    if player_menu == 'dub':
        dub = True
    else:
        dub = False
    if not os.path.isfile(filename + '.mp4'):
        #should probably check if its not a corrupted video file
        logger.info("no file to play")
        if dub == True:
            video = False
        else:
            return
    sound = has_audio_track(filename + '.mp4')
    t = 0
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    #playing = False
    pause = False
    trim = False
    videolag = 0
    trimfromstart=0
    trimfromend=0
    remove_shots = []
    split_list=[]
    soundsync=0.0
    oldmenu=''
    if video == True:
        if player_menu == 'dubbb':
            try:
                if hdmi_mode==False:
                    player = OMXPlayer(filename + '.mp4', args=['-n', '-1', '--fps', str(film_fps), '--layer', '3', '--no-osd', '--win', '0,'+topspace+','+screen_reso_w+','+screen_reso_h,' --no-keys',  '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
                else:
                    player = OMXPlayer(filename + '.mp4', args=['-n', '-1', '--fps', str(film_fps), '--layer', '3', '--no-osd','--win', '0,15,'+reso_w+','+reso_h, '--no-keys',  '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
            except:
                writemessage('Something wrong with omxplayer')
                time.sleep(0.1)
                return
        else:
            try:
                if hdmi_mode==False:
                    player = OMXPlayer(filename + '.mp4', args=['--adev', 'alsa:hw:'+str(plughw), '--fps', str(film_fps), '--layer', '3', '--no-osd', '--win', '0,'+topspace+','+screen_reso_w+','+screen_reso_h, '--no-keys', '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
                else:
                    player = OMXPlayer(filename + '.mp4', args=['--adev', 'alsa:hw:'+str(plughw), '--fps', str(film_fps), '--layer', '3', '--no-osd','--no-keys','--win', '0,15,'+reso_w+','+reso_h, '--no-keys', '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
            except:
                writemessage('Something wrong with omxplayer')
                time.sleep(0.1)
                return
            #player = OMXPlayer(filename + '.mp4', args=['--fps', '25', '--layer', '3', '--win', '0,70,800,410', '--no-osd', '--no-keys'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
        writemessage('Loading..')
        clipduration = player.duration()
        #vumetermessage('up [fast-forward], down [rewind], help button for more')
    if sound == False:
        try:
            playerAudio = OMXPlayer(filename + '.wav', args=['--adev','alsa:hw:'+str(plughw), '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer2', pause=True)
        except:
            writemessage('something wrong with audio player')
            time.sleep(0.1)
            return
    #omxplayer hack to play really short videos.
    if clipduration < 4:
        logger.info("clip duration shorter than 4 sec")
        player.previous()
        if sound == False:
            playerAudio.previous()
    if dub == True:
        p = 0
        while p < 3:
            writemessage('Dubbing in ' + str(3 - p) + 's')
            time.sleep(1)
            p+=1
    if video == True:
        player.play()
        #player.pause()
        player.set_position(0)
        if sound == False:
            playerAudio.play()
            #playerAudio.pause()
            playerAudio.set_position(0)
        #run_command('aplay -D plughw:0 ' + filename + '.wav &')
        #run_command('mplayer ' + filename + '.wav &')
    if player_menu == 'dub':
        run_command(gonzopifolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:'+str(plughw)+' -f '+soundformat+' -c '+str(channels)+' -r '+soundrate+' -vv '+filmfolder+'.tmp/dub.wav &')
    time.sleep(0.5)
    #try:
    #    playerAudio.play()
    #except:
    #    logger.info('something wrong with omxplayer audio or playing film mp4 audio')
        #logger.warning(e)
    starttime = time.time()
    selected = 1
    while True:
        if player_menu == 'scene':
            fastedit_shot = 1
            for i in fastedit:
                if int(t) > float(int(i)/1000):
                    fastedit_shot = fastedit_shot + 1
            if not remove_shots:
                vumetermessage('shot ' + str(fastedit_shot))
            else:
                p = ''
                for i in remove_shots:
                    p = p + str(i) + ','
                vumetermessage('shot ' + str(fastedit_shot) + ' remove:' + p)
        if trim == True:
            menu = 'CANCEL', 'FROM BEGINNING', 'FROM END'
            settings = '','',''
        elif pause == True:
            if player_menu == 'shot':
                menu = 'BACK', 'PLAY', 'REPLAY', 'TRIM', 'SPLIT'
                settings = '','','','',''
            else:
                menu = 'BACK', 'PLAY', 'REPLAY'
                settings = '','',''
        elif player_menu == 'dub': 
            menu = 'BACK', 'REDUB', 'PHONES:', 'MIC:'
            settings = '', '', str(headphoneslevel), str(miclevel)
        else:
            #menu = 'BACK', 'PAUSE', 'REPLAY', 'PHONES:', 'SYNC:'
            menu = 'BACK', 'PAUSE', 'REPLAY', 'PHONES:'
            #settings = '', '', '', str(headphoneslevel), str(soundsync)
            settings = '', '', '', str(headphoneslevel)
        if dub == True:
            header = 'Dubbing ' + str(round(t,1))
        else:
            header = 'Playing ' + str(datetime.timedelta(seconds=round(t))) + ' of ' + str(datetime.timedelta(seconds=round(clipduration))) + ' s'
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if buttonpressed == True:
            flushbutton()
        if pressed == 'remove':
            vumetermessage('video cuts removed!')
            trimfromstart=0
            trimfromend=0
            split_list=[]
        #SHOWHELP
        elif pressed == 'showhelp':
            vumetermessage('Button layout')
            if showhelp == False:
                overlay2 = removeimage(camera, overlay2)
                overlay2 = displayimage(camera, gonzopifolder+'/extras/view-buttons.png', overlay, 4)
                showhelp = True
            elif showhelp == True:
                overlay2 = removeimage(camera, overlay2)
                updatethumb =  True
                showhelp = False
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'up':
            if menu[selected] == 'PHONES:':
                if headphoneslevel < 100:
                    headphoneslevel = headphoneslevel + 2
                    run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            elif menu[selected] == 'SYNC:':
                soundsync += 0.01
                soundsync = round(soundsync,2)
            elif menu[selected] == 'MIC:':
                if miclevel < 100:
                    miclevel = miclevel + 2
                    run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            else:
                if pause == False:
                    try:
                        player.set_position(t+2)
                        if sound == False:
                            playerAudio.set_position(t+2)
                        time.sleep(0.2)
                        #playerAudio.set_position(player.position())
                    except:
                        print('couldnt set position of player')
                else:
                    try:
                        player.play()
                        if sound == False:
                            playerAudio.play()
                        time.sleep(0.3)
                        t=t+0.1 
                        player.set_position(t)
                        player.pause()
                        if sound == False:
                            playerAudio.set_position(soundsync+t)
                            playerAudio.pause()
                        #playerAudio.set_position(player.position())
                    except:
                        print('couldnt set position of player')
        elif pressed == 'down':
            if menu[selected] == 'PHONES:':
                if headphoneslevel > 0:
                    headphoneslevel = headphoneslevel - 2
                    run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            elif menu[selected] == 'SYNC:':
                soundsync -= 0.01
                soundsync = round(soundsync,2)
            elif menu[selected] == 'MIC:':
                if miclevel > 0:
                    miclevel = miclevel - 2
                    run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            else:
                if pause == False:
                    if t > 1:
                        try:
                            player.set_position(t-2)
                            if sound == False:
                                playerAudio.set_position(soundsync+t-2)
                            time.sleep(0.25)
                            #playerAudio.set_position(player.position())
                        except:
                            print('couldnt set position of player')
                else:
                    try:
                        player.play()
                        if sound == False:
                            playerAudio.play()
                        time.sleep(0.3)
                        t=t-0.1
                        player.set_position(t)
                        player.pause()
                        if sound == False:
                            playerAudio.set_position(soundsync+t)
                            playerAudio.pause()
                        #playerAudio.set_position(player.position())
                    except:
                        print('couldnt set position of player')
        elif holdbutton == 'copy':
            if t > 1:
                try:
                    player.set_position(t-60)
                    if sound == False:
                        playerAudio.set_position(soundsync+t-60)
                    time.sleep(0.25)
                    #playerAudio.set_position(player.position())
                except:
                    print('couldnt set position of player')
        elif holdbutton == 'insert':
            if t > 1:
                try:
                    player.set_position(t+30)
                    if sound == False:
                        playerAudio.set_position(soundsync+t+30)
                    time.sleep(0.25)
                    #playerAudio.set_position(player.position())
                except:
                    print('couldnt set position of player')
        elif pressed == 'view':
            trimfromstart = player.position()
            vumetermessage('shot start position set to: '+ str(trimfromstart))
            player.pause()
            if sound == False:
                playerAudio.pause()
            time.sleep(0.5)
            player.play()
            if sound == False:
                playerAudio.play()
        elif pressed == 'record':
            if trimfromstart != 0 and trimfromend != 0 and trimfromstart < trimfromend:
                split_list.append([[trimfromstart, trimfromend], takename])
                vumetermessage('split '+str(len(split_list))+' position set to: '+ str(player.position()))
                player.pause()
                if sound == False:
                    playerAudio.pause()
                time.sleep(0.5)
                player.play()
                if sound == False:
                    playerAudio.play()
        elif pressed == 'retake':
            if player.position() < clipduration:
                trimfromend = player.position()
                vumetermessage('shot end position set to: '+ str(trimfromend))
                player.pause()
                if sound == False:
                    playerAudio.pause()
                time.sleep(0.5)
                player.play()
                if sound == False:
                    playerAudio.play()
        elif pressed == 'middle':
            time.sleep(0.2)
            if menu[selected] == 'BACK' or player.playback_status() == "Stopped" or pressed == 'record':
                try:
                    if video == True:
                        #player.stop()
                        #playerAudio.stop()
                        player.quit()
                        if sound == False:
                            playerAudio.quit()
                            if soundsync < 0:
                                fastaudiotrim(filename,'0',str(soundsync))
                                #audiotrim(filename+'.mp4', 'beginning','') 
                            elif soundsync > 0:
                                fastaudiotrim(filename,str(soundsync),'')
                                #audiotrim(filename+'.mp4', 'end','') 
                    #os.system('pkill -9 aplay') 
                except:
                    #kill it if it dont stop
                    print('OMG! kill dbus-daemon')
                if dub == True:
                    os.system('pkill arecord')
                    time.sleep(0.2)
                os.system('pkill -9 omxplayer')
                #os.system('pkill -9 dbus-daemon')
                return [trimfromstart, trimfromend], split_list
            elif menu[selected] == 'SYNC:':
                try:
                    player.set_position(t-2)
                    if sound == False:
                        playerAudio.set_position(soundsync+t-2)
                    time.sleep(0.25)
                    #playerAudio.set_position(player.position())
                except:
                    print('couldnt set position of player')
            elif menu[selected] == 'REPLAY' or menu[selected] == 'REDUB':
                pause = False
                try:
                    os.system('pkill aplay')
                    if dub == True:
                        os.system('pkill arecord')
                    if video == True:
                        player.pause()
                        player.set_position(0)
                        if sound == False:
                            playerAudio.pause()
                            playerAudio.set_position(soundsync+0)
                    if dub == True:
                        p = 0
                        while p < 3:
                            writemessage('Dubbing in ' + str(3 - p) + 's')
                            time.sleep(1)
                            p+=1
                    player.play()
                    if sound == False:
                        playerAudio.play()
                    #if player_menu != 'film':
                    #    playerAudio.play()
                    #run_command('aplay -D plughw:0 ' + filename + '.wav &')
                    if dub == True:
                        run_command(gonzopifolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:'+str(plughw)+' -f '+soundformat+' -c '+str(channels)+' -r '+soundrate+' -vv '+filmfolder+'.tmp/dub.wav &')
                except:
                    pass
                starttime = time.time()
            # check if not to close to end otherwise will throw error
            elif menu[selected] == 'PAUSE':
                try:
                    player.pause()
                    if sound == False:
                        playerAudio.pause()
                    pause = True
                except:
                    pass
                #try:
                #    playerAudio.pause()
                #except:
                #    pass
            elif menu[selected] == 'PLAY':
                try:
                    player.play()
                    if sound == False:
                        playerAudio.play()
                    pause = False
                except:
                    pass
                #try:
                #    playerAudio.play()
                #except:
                #    pass
            elif menu[selected] == 'TRIM':
                selected = 1
                trim = True
            elif menu[selected] == 'CANCEL':
                selected = 1
                trim = False
            elif menu[selected] == 'SPLIT':
                split_list.append([[0, player.position()], takename])
                split_list.append([[player.position(), clipduration], takename])
                vumetermessage('split '+str(len(split_list))+' position set to: '+ str(player.position()))
                player.quit()
                #playerAudio.quit()
                return trim, split_list
            elif menu[selected] == 'FROM BEGINNING':
                trim = ['beginning', player.position()]
                player.quit()
                #playerAudio.quit()
                return trim, split_list
            elif menu[selected] == 'FROM END':
                trim = ['end', player.position()]
                player.quit()
                if sound == False:
                    playerAudio.quit()
                return trim, split_list
        time.sleep(0.02)
        if pause == False:
            try:
                t = player.position()
            except:
                os.system('pkill aplay') 
                if dub == True:
                    os.system('pkill arecord')
                player.quit()
                if sound == False:
                    playerAudio.quit()
                    if soundsync < 0:
                        fastaudiotrim(filename,'0',str(soundsync))
                        #audiotrim(filename+'.mp4', 'beginning','') 
                    elif soundsync > 0:
                        fastaudiotrim(filename,str(soundsync),'')
                        #audiotrim(filename+'.mp4', 'end','') 
                return [trimfromstart, trimfromend], split_list
                #return remove_shots
        if t > (clipduration - 0.3):
            os.system('pkill aplay') 
            if dub == True:
                writemessage('Video ended. Press any key to stop dubbing...')
                waitforanykey()
                os.system('pkill arecord')
            player.quit()
            if sound == False:
                playerAudio.quit()
                if soundsync < 0:
                    fastaudiotrim(filename,'0',str(soundsync))
                    #audiotrim(filename+'.mp4', 'beginning','') 
                elif soundsync > 0:
                    fastaudiotrim(filename,str(soundsync),'')
                    #audiotrim(filename+'.mp4', 'end','') 
            return [trimfromstart, trimfromend], split_list
    try:
        player.quit()
        if sound == False:
            playerAudio.quit()
            if soundsync < 0:
                fastaudiotrim(filename,'0',str(soundsync))
                #audiotrim(filename+'.mp4', 'beginning','') 
            elif soundsync > 0:
                fastaudiotrim(filename,str(soundsync),'')
                #audiotrim(filename+'.mp4', 'end','') 
    except:
        pass
    return [trimfromstart, trimfromend], split_list
    #playerAudio.quit()
    #os.system('pkill dbus-daemon')

#---------------View Film--------------------

def viewfilm(filmfolder, filmname):
    scenes, shots, takes = countlast(filmname, filmfolder)
    scene = 1
    filmfiles = []
    while scene <= scenes:
        shots = countshots(filmname, filmfolder, scene)
        if shots > 0:
            filmfiles.extend(shotfiles(filmfolder, filmname, scene))
        scene = scene + 1
    return filmfiles


#--------------Save video crossfade settings-----------------

def crossfadesave(filmfolder, s, trimfile):
    #db.insert('videos', tid=datetime.datetime.now())
    settings=s,trimfile
    try:
        with open(filmfolder + ".crossfade", "wb") as f:
            pickle.dump(settings, f)
            #logger.info("settings saved")
    except:
        logger.warning("could not save settings")
        #logger.warning(e)
    return

#--------------Save video trim settings-----------------

def videotrimsave(filmfolder, where, s, trimfile):
    #db.insert('videos', tid=datetime.datetime.now())
    settings=s,trimfile
    try:
        with open(filmfolder + "."+where, "wb") as f:
            pickle.dump(settings, f)
            #logger.info("settings saved")
    except:
        logger.warning("could not save settings")
        #logger.warning(e)
    return

#--------------Save split settings-----------------

def split_list_save(foldername, splitlist):
    #db.insert('videos', tid=datetime.datetime.now())
    settings=splitlist
    try:
        with open(foldername + ".split", "wb") as f:
            pickle.dump(settings, f)
            logger.info("split settings saved")
    except:
        logger.warning("could not save settings")
        #logger.warning(e)
    return


#---------------Video Trim--------------------

def videotrim(filmfolder, foldername ,filename, where, s, t, make_new_take_or_shot):
    global film_reso, db
    #theres two different ways of non-rerendering mp4 cut techniques that i know MP4Box and ffmpeg
    if make_new_take_or_shot == 'take':
        trim_filename = foldername+filename[:-3] + str(counttakes2(foldername)+1).zfill(3)
    else:
        trim_filename = make_new_take_or_shot
    filename=foldername+filename
    if where == 'both':
        s=round(s, 3)
        t=round(t, 3)
        video_edit_len=round(float(t)-float(s),3)
        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
        tot = int(videos_totalt.videos)
        video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
        run_command('ffmpeg -i '+filename+'.mp4 -ss '+str(s)+' -t '+str(video_edit_len)+' -c:v copy -c:a copy -y '+video_origins+'.mp4')
        os.system('ln -sfr '+video_origins+'.mp4 '+trim_filename+'.mp4')
        run_command('ffmpeg -i '+filename+'.wav -ss '+str(s)+' -t '+str(video_edit_len)+' -c:a copy -y '+video_origins+'.wav')
        os.system('ln -sfr '+video_origins+'.wav '+trim_filename+'.wav')
        #run_command('ecasound -i:'+filename+'.wav -o:'+trim_filename+'.wav -ss:'+str(s)+' -t:'+str(video_edit_len))
        #if os.path.exists(foldername+'dub') == True:
        #    dubfiles, dubmix, rerender = getdubs(foldername+'dub/', None, None, None)
        #    for d in dubfiles:
        #        writemessage('trimming dubs from beginning and end')
        #        vumetermessage(d)
        #        #audiotrim(trim_filename, 'beginning', d)
        #        run_command('ecasound -i:'+d+' -o:'+d+'_temp -ss '+str(s)+' -t '+str(t))
        #    writemessage('trimming original sound')
    elif where == 'beginning':
        logger.info('trimming clip from beginning')
        #run_command('ffmpeg -ss ' + str(s) + ' -i ' + filename + '.mp4 -c copy ' + trim_filename + '.mp4')
        #ffmpeg -fflags +genpts -r 25 -i take009.mp4 -c:v h264_omx -crf 20 -profile:v high -level:v 4.2 -preset slower -bsf:v h264_metadata=level=4.2 -g 1 -b:v 8888888 take010.mp4
        #run_command('MP4Box ' + filename + '.mp4 -splitx ' + str(s) + ':end -out ' + trim_filename +  '.mp4')
        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
        tot = int(videos_totalt.videos)
        video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
        run_command('ffmpeg -i '+filename+'.mp4 -ss '+str(s)+' -c:v copy -c:a copy -y '+video_origins+'.mp4')
        run_command('cp ' + filename + '.wav ' + video_origins + '.wav')
        audiotrim(video_origins, 'beginning','')
        os.system('ln -sfr '+video_origins+'.mp4 '+trim_filename+'.mp4')
        os.system('ln -sfr '+video_origins+'.wav '+trim_filename+'.wav')
        #if os.path.exists(foldername+'dub') == True:
        #    dubfiles, dubmix, rerender = getdubs(foldername+'dub/', None, None, None)
        #    for d in dubfiles:
        #        writemessage('trimming dubs from beginning')
        #        vumetermessage(d)
        #        audiotrim(trim_filename, 'beginning', d)
        #    writemessage('trimming original sound')
        #    audiotrim(trim_filename, 'beginning', foldername+'dub/original.wav')
    elif where == 'end':
        logger.info('trimming clip from end')
        #run_command('ffmpeg -to ' + str(s) + ' -i ' + filename + '.mp4 -c copy ' + trim_filename + '.mp4')
        #run_command('MP4Box ' + filename + '.mp4 -splitx 0:' + str(s) + ' -out ' + trim_filename + '.mp4')
        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
        tot = int(videos_totalt.videos)
        video_origins=filmfolder+'.videos/'+datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
        run_command('ffmpeg -i '+filename+'.mp4 -t '+str(s)+' -c:v copy -c:a copy -y '+video_origins+'.mp4')
        run_command('cp ' + filename + '.wav ' + video_origins + '.wav')
        audiotrim(video_origins, 'end','')
        os.system('ln -sfr '+video_origins+'.mp4 '+trim_filename+'.mp4')
        os.system('ln -sfr '+video_origins+'.wav '+trim_filename+'.wav')
        #if os.path.exists(foldername+'dub') == True:
        #    dubfiles, dubmix, rerender = getdubs(foldername+'dub/', None, None, None)
        #    for d in dubfiles:
        #        writemessage('trimming dubs from end')
        #        vumetermessage(d)
        #        audiotrim(trim_filename, 'end', d)
        #    writemessage('trimming original sound')
        #    audiotrim(trim_filename, 'end', foldername+'dub/original.wav')
    #take last frame 
    videolength = get_video_length(video_origins+'.mp4')
    #db.insert('videos', tid=datetime.datetime.now(), filename=video_origins+'.mp4', foldername=foldername, audiolength=videolength/1000, videolength=videolength/1000)
    if film_reso == '1920x1080':
        run_command('ffmpeg -y -sseof -1 -i ' + trim_filename + '.mp4 -update 1 -q:v 1 -vf scale=800:450 ' + trim_filename + '.jpeg')
        run_command('ffmpeg -y -sseof -1 -i ' + trim_filename + '.mp4 -update 1 -q:v 1 -vf scale=80:45 ' + trim_filename + '_thumb.jpeg')
    elif film_reso == '1920x816':
        run_command('ffmpeg -y -sseof -1 -i ' + trim_filename + '.mp4 -update 1 -q:v 1 -vf scale=800:340 ' + trim_filename + '.jpeg')
    return

#---------------Video Trim From start and end--------------------

def fastvideotrim(filename, trim_filename, beginning, end):
    #theres two different ways of non-rerendering mp4 cut techniques that i know MP4Box and ffmpeg
    logger.info('trimming clip from beginning and end')
    #run_command('ffmpeg -to ' + str(s) + ' -i ' + filename + '.mp4 -c copy ' + trim_filename + '.mp4')
    run_command('MP4Box ' + filename + '.mp4 -splitx '+ str(beginning)+ ':' + str(end) + ' -out ' + trim_filename + '.mp4')
    run_command('cp ' + filename + '.wav ' + trim_filename + '.wav')
    fastaudiotrim(trim_filename, beginning, end)
    #take last frame 
    run_command('ffmpeg -sseof -1 -i ' + trim_filename + '.mp4 -update 1 -q:v 1 -vf scale=800:450 ' + trim_filename + '.jpeg')
    return

#--------------Get Audio cards--------------
def getaudiocards():
    with open("/proc/asound/cards") as fp:
        cards = fp.readlines()
    audiocards = []
    for i in cards:
        if i[1] in ['0','1','2','3']:
            print('audio card 0: ' + i[22:].rstrip('\n'))
            audiocards.append(i[22:].rstrip('\n'))
    return audiocards

#--------------Fast Audio Trim--------------------
# make audio file same length as video file
def fastaudiotrim(filename, beginning, end):
    global filmfolder
    audio_origins = (os.path.realpath(filename+'.wav'))
    if end != '':
        run_command('sox -V0 ' + filename + '.wav ' + filmfolder+'.tmp/trim.wav trim ' + beginning + ' ' + end + ' pad '+str(float(end)*-1))
    else: 
        run_command('sox -V0 ' + filename + '.wav ' + filmfolder+'.tmp/trim.wav trim ' + beginning)
    run_command('sox -V0 -G ' + filmfolder+'.tmp/trim.wav ' + audio_origins + ' fade 0.01 0 0.01')
    os.system('rm '+filmfolder+'.tmp/trim.wav')

#--------------Audio Trim--------------------
# make audio file same length as video file
def audiotrim(filename, where, dub):
    global channels, fps, db
    videofile=filename
    audiosync=0
    print("chaaaaaaaaaaaaaaaanel8: " +str(channels))
    writemessage('Audio syncing..')
    #pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
    #videolength = pipe.decode().strip()
    videolength = get_video_length(filename+'.mp4')
    print('videolength:'+str(videolength))
    if dub:
        #pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + dub[:-4] + '.wav', shell=True)
        #audiolength = pipe.decode().strip()
        audiolength = get_audio_length(dub[:-4] + '.wav')
    else:
        try:
            #pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + filename + '.wav', shell=True)
            #audiolength = pipe.decode().strip()
            audiolength = get_audio_length(filename+'.wav')
        except:
            audiosilence(filename)
            audiolength=videolength
        #if there is no audio length
    logger.info('audio is:' + str(audiolength))
    #separate seconds and milliseconds
    #videoms = int(videolength) % 1000
    #audioms = int(audiolength) % 1000
    #videos = int(videolength) / 1000
    #audios = int(audiolength) / 1000
    video_origins = (os.path.realpath(filename+'.mp4'))
    audio_origins = (os.path.realpath(filename+'.wav'))
    if int(audiolength) > int(videolength):
        #calculate difference
        audiosync = int(audiolength) - int(videolength)
        newaudiolength = int(audiolength) - audiosync
        logger.info('Audiofile is: ' + str(audiosync) + 'ms longer')
        #trim from end or beginning and put a 0.01 in- and outfade
        if where == 'end':
            if dub:
                run_command('sox -V0 -b 16 ' + dub[:-4] + '.wav -c 2 ' + dub[:-4] + '_temp.wav trim 0 -' + str(int(audiosync)/1000))
            else:
                run_command('sox -V0 -b 16 ' + filename + '.wav -c 2 ' + filename + '_temp.wav trim 0 -' + str(int(audiosync)/1000))
        if where == 'beginning':
            if dub:
                logger.info('trimming from beginning at: '+str(int(audiosync)/1000))
                run_command('sox -V0 -b 16 ' + dub[:-4] + '.wav -c 2 ' + dub[:-4] + '_temp.wav trim ' + str(int(audiosync)/1000))
            else:
                logger.info('trimming from beginning at: '+str(int(audiosync)/1000))
                run_command('sox -V0 -b 16 ' + filename + '.wav -c 2 ' + filename + '_temp.wav trim ' + str(int(audiosync)/1000))
        if dub:
            run_command('sox -V0 -b 16 -G ' + dub[:-4] + '_temp.wav -c 2 ' + dub[:-4] + '.wav fade 0.01 0 0.01')
            os.remove(dub[:-4] + '_temp.wav')
        else:
            run_command('sox -V0 -b 16 -G ' + filename + '_temp.wav -c 2 ' + audio_origins + ' fade 0.01 0 0.01')
            os.remove(filename + '_temp.wav')
        #if int(audiosync) > 400:
        #    writemessage('WARNING!!! VIDEO FRAMES DROPPED!')
        #    vumetermessage('Consider changing to a faster microsd card.')
        #    time.sleep(10)
        delayerr = 'A' + str(audiosync)
        print(delayerr)
    elif int(audiolength) < int(videolength):
        audiosync = int(videolength) - int(audiolength)
        #calculate difference
        #audiosyncs = videos - audios
        #audiosyncms = videoms - audioms
        #if audiosyncms < 0:
        #    if audiosyncs > 0:
        #        audiosyncs = audiosyncs - 1
        #    audiosyncms = 1000 + audiosyncms
        logger.info('Videofile is: ' + str(audiosync) + 'ms longer')
        logger.info('Videofile is: ' + str(int(audiosync)/1000) + 's longer')
        #time.sleep(2)
        #make fade
        #make delay file
        print(str(int(audiosync)/1000))
        if dub:
            run_command('sox -V0 -b 16 -r '+soundrate+' '+dub[:-4]+'.wav -c 2 '+dub[:-4]+'_temp.wav trim 0.0 pad 0 ' + str(int(audiosync)/1000))
            run_command('sox -V0 -b 16 -G ' + dub[:-4] + '_temp.wav -c 2 ' + dub[:-4] + '.wav fade 0.01 0 0.01')
        else:
            run_command('sox -V0 -b 16 -r '+soundrate+' '+filename+'.wav -c 2 '+filename+'_temp.wav trim 0.0 pad 0 ' + str(int(audiosync)/1000))
            run_command('sox -V0 -b 16 -G ' + filename + '_temp.wav -c 2 ' + audio_origins + ' fade 0.01 0 0.01')
        #add silence to end
        #run_command('sox -V0 /dev/shm/silence.wav ' + filename + '_temp.wav')
        #run_command('cp '+filename+'.wav '+filename+'_temp.wav')
        #run_command('sox -V0 -G ' + filename + '_temp.wav /dev/shm/silence.wav ' + filename + '.wav')
        if dub:
            os.remove(dub[:-4] + '_temp.wav')
        else:
            os.remove(filename + '_temp.wav')
        #os.remove('/dev/shm/silence.wav')
        delayerr = 'V' + str(audiosync)
        print(delayerr)
    #print('the results:')
    #if dub:
    #    pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + dub[:-4] + '.wav', shell=True)
    #    audiolength = pipe.decode().strip()
    #else:
    #    pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + filename + '.wav', shell=True)
    #    audiolength = pipe.decode().strip()
    #print('aftersyncvideo: '+str(videolength) + ' audio:'+str(audiolength))
    #if int(audiolength) != int(videolength):
    #    vumetermessage('SYNCING FAILED!')
    #    time.sleep(10)
    #os.remove('/dev/shm/' + filename + '.wav')
    return float(audiosync)/1000, int(videolength), int(audiolength)
    #os.system('mv audiosynced.wav ' + filename + '.wav')
    #os.system('rm silence.wav')

#--------------Audiosilence--------------------
# make an empty audio file as long as a video file

def audiosilence(renderfilename):
    global channels, soundrate,filmfolder
    writemessage('Creating audiosilence..')
    #pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + renderfilename + '.mp4', shell=True)
    #videolength = pipe.decode()
    logger.info('checking video length')
    videolength = get_video_length(renderfilename+'.mp4')
    audio_origins = (os.path.realpath(renderfilename+'.mp4'))[:-4]
    logger.info('Video length is ' + str(videolength))
    #separate seconds and milliseconds
    videoms = int(videolength) % 1000
    videos = int(videolength) / 1000
    logger.info('Videofile is: ' + str(videos) + 's ' + str(videoms))
    run_command('sox -V0 -n -b 16 -r '+soundrate+' -c 2 '+filmfolder+'.tmp/silence.wav trim 0.0 ' + str(videos))
    videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
    tot = int(videos_totalt.videos)
    #audio_origins=datetime.datetime.now().strftime('%Y%d%m')+'_'+os.urandom(8).hex()+'_'+str(tot).zfill(5)
    os.system('cp '+filmfolder+'.tmp/silence.wav '+audio_origins+'.wav')
    os.system('ln -sfr '+audio_origins+'.wav '+renderfilename+'.wav')
    os.system('rm '+filmfolder+'.tmp/silence.wav')

#--------------USB filmfolder-------------------

def usbfilmfolder(dsk):
    if dsk == 1:
        usbmount = 1
    else:
        usbmount = 0
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    writemessage('Searching for usb storage device, middlebutton to cancel')
    time.sleep(2)
    if os.path.exists('/dev/sda1') == True:
        os.system('sudo mount -o  noatime,nodiratime,async /dev/sda1 /media/usb0')
        os.system('sudo chown pi /media/usb0')
        os.system('sudo echo none | sudo tee /sys/block/sda/queue/scheduler')
        #os.system('sudo umount -l /media/usb0')
    if os.path.exists('/dev/sdb1') == True:
        os.system('sudo mount -o  noatime,nodiratime,async /dev/sdb1 /media/usb1')
        os.system('sudo chown pi /media/usb1')
        os.system('sudo echo none | sudo tee /sys/block/sda/queue/scheduler')
        #os.system('sudo umount -l /media/usb0')
    waiting = time.time() 
    while True:
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        usbconnected = os.path.ismount('/media/usb'+str(usbmount))
        if pressed == 'middle' or time.time() - waiting > 8:
            writemessage('canceling..')
            time.sleep(1)
            break
        time.sleep(0.02)
        if usbconnected == True:
            try:
                os.makedirs('/media/usb'+str(usbmount)+'/gonzopifilms/')
            except:
                pass
            try:
                p = subprocess.check_output('stat -f -c %T /media/usb'+str(usbmount), shell=True)
                filesystem = p.decode()
                print('filesystem info: ' + filesystem)
            except:
                writemessage('Oh-no! dont know your filesystem')
                waitforanykey()
            filmfolder = '/media/usb'+str(usbmount)+'/gonzopifilms/'
            os.system('sudo chmod 755 /media/usb'+str(usbmount))
            os.system('sudo chmod 755 '+filmfolder)
            #run_command('pumount /media/usb'+str(usbmount))
            writemessage('Filming to USB'+str(usbmount))
            time.sleep(2)
            return filmfolder
        else:
            writemessage('Filming to SDCARD')
            time.sleep(2)
            return

#--------------Copy to USB-------------------

def copytousb(filmfolder):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    writemessage('Searching for usb storage device, middlebutton to cancel')
    films = getfilms(filmfolder)
    if 'usb0' in filmfolder:
        usbmount = 1
    else:
        usbmount = 0
    while True:
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        usbconnected = os.path.ismount('/media/usb'+str(usbmount))
        if pressed == 'middle':
            writemessage('canceling..')
            time.sleep(2)
            break
        time.sleep(0.02)
        if usbconnected == True:
            #Copy new files to usb device
            try:
                os.makedirs('/media/usb'+str(usbmount)+'/gonzopifilms/')
            except:
                pass
            try:
                p = subprocess.check_output('stat -f -c %T /media/usb'+str(usbmount), shell=True)
                filesystem = p.decode()
                print('filesystem info: ' + filesystem)
            except:
                writemessage('Oh-no! dont know your filesystem')
                waitforanykey()
                return
            for filmname in films:
                #check filmhash
                filmname = filmname[0]
                usbpath = '/media/usb'+str(usbmount)+'/gonzopifilms/'+filmname
                usbvideopath = '/media/usb0/gonzopifilms/.videos/'
                usbfilmhash = ''
                filmhash = ''
                while True:
                    if os.path.exists(usbpath) == False:
                        break
                    try:
                        with open(filmfolder + filmname + '/.filmhash', 'r') as f:
                            filmhash = f.readline().strip()
                        print('filmhash is: ' + filmhash)
                    except:
                        print('no filmhash found!')
                    try:
                        with open(usbpath + '/.filmhash', 'r') as f:
                            usbfilmhash = f.readline().strip()
                        print('usbfilmhash is: ' + usbfilmhash)
                    except:
                        print('no usbfilmhash found!')
                    if usbfilmhash == filmhash:
                        print('same moviefilm found, updating clips...')
                        break
                    else:
                        writemessage('Found a subsequent moviefilm...')
                        print('same film exist with different filmhashes, copying to subsequent film folder')
                        time.sleep(2)
                        usbpath += '_new'
                try:
                    os.makedirs(usbpath)
                    writemessage('Copying film ' + filmname + '...')
                except:
                    writemessage('Found existing ' + filmname + ', copying new files... ')
                try:
                    run_command('rsync -avr -P ' + filmfolder + filmname + '/ ' + usbpath)
                    run_command('rsync -avr -P ' + filmfolder + '.videos/ ' + usbvideopath)
                except:
                    writemessage('couldnt copy film ' + filmname)
                    waitforanykey()
                    return
            run_command('sync')
            writemessage('all files copied successfully!')
            waitforanykey()
            run_command('pumount /media/usb'+str(usbmount))
            writemessage('You can safely unplug the usb device now')
            time.sleep(2)
            return
        else:
            usbmount = usbmount + 1

#-----------Check for the webz---------

def webz_on():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("google.com", 80))
        return True
    except OSError:
        pass
    writemessage('No internet connection!')
    time.sleep(2)
    return False

#-------------Upload film------------

def uploadfilm(filename, filmname):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    mods = ['Back']
    settings = ['']
    writemessage('Searching for upload mods')
    with open(gonzopifolder + '/mods/upload-mods-enabled') as m:
        mods.extend(m.read().splitlines())
    for m in mods:
        settings.append('')
    menu = mods
    selected = 0
    oldmenu=''
    while True:
        header = 'Where do you want to upload?'
        oldmenu=writemenu(menu,settings,selected,header,showmenu,oldmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(menu) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and  menu[selected] == 'Back':
            return None
        elif pressed == 'middle' and  menu[selected] in mods:
            cmd = gonzopifolder + '/mods/' + menu[selected] + '.sh ' + filmname + ' ' + filename + '.mp4'
            return cmd
        time.sleep(0.02)


#-------------Streaming---------------

def startstream(camera, stream, plughw, channels,network, udp_ip, udp_port, bitrate):
    #youtube
    #youtube="rtmp://a.rtmp.youtube.com/live2/"
    #with open("/home/pi/.youtube-live") as fp:
    #    key = fp.readlines()
    #print('using key: ' + key[0])
    #stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar 48000 -vcodec copy -acodec libmp3lame -b:a 128k -ar 48000 -map 0:0 -map 1:0 -strict experimental -f flv ' + youtube + key[0]
    #
    #stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar 44100 -vcodec copy -acodec libmp3lame -b:a 128k -ar 44100 -map 0:0 -map 1:0 -strict experimental -f mpegts tcp://0.0.0.0:3333\?listen'
    #stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar '+soundrate+' -acodec mp2 -b:a 128k -ar '+soundrate+' -vcodec copy -map 0:0 -map 1:0 -g 0 -f mpegts udp://10.42.0.169:5002'
    #numbers_only = ' ','1','2','3','4','5','6','7','8','9','0'
    #newhost, hostport = newudp_ip(numbers_only, network)
    #stream_cmd = 'ffmpeg -f h264 -r 24.989 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar '+soundrate+' -acodec mp2 -b:a 128k -ar '+soundrate+' -vcodec copy -f mpegts udp://'+udp_ip+':'+udp_port
    stream_cmd = 'ffmpeg -f h264 -r 24.989 -i - -vcodec copy -f mpegts udp://'+udp_ip+':'+udp_port
    try:
        stream = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE) 
        if bitrate > 1000:
            camera.start_recording(stream.stdin, splitter_port=2, format='h264', bitrate = bitrate)
        else:
            camera.start_recording(stream.stdin, splitter_port=2, format='h264', quality=quality)
    except:
        stream = ''
    #now = time.strftime("%Y-%m-%d-%H:%M:%S") 
    return stream

def stopstream(camera, stream):
    camera.stop_recording(splitter_port=2) 
    os.system('pkill -9 ffmpeg') 
    print("Camera safely shut down") 
    print("Good bye")
    stream = ''
    return stream

def startrecording(camera, takename,bitrate, quality, profilelevel, reclength):
    global film_fps
    # FFmpeg command to take H.264 input from stdin and output to MP4
    ffmpeg_cmd = ['ffmpeg','-i', 'pipe:0', '-fflags', '+genpts+igndts', '-c:v', 'copy', '-movflags', 'frag_keyframe+empty_moov', '-level:v', '4.2', '-g', '1', '-r', '25', '-f', 'mp4', takename, '-loglevel','debug', '-y']
    rec_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    if reclength > 1 or reclength == 0:
        if camera.recording == True:
            if bitrate > 1000:
                camera.split_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)
            else:
                camera.split_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, quality = quality)
        else:
            if bitrate > 1000:
                camera.start_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)
            else:
                camera.start_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, quality = quality)
    else:
        if camera.recording == True:
            if bitrate > 1000:
                camera.split_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)
            else:
                camera.split_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, quality = quality)
        else:
            if bitrate > 1000:
                camera.start_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)
            else:
                camera.start_recording(rec_process.stdin, format='h264', level=profilelevel, intra_period=5, quality = quality)
    return rec_process, camera

def stoprecording(camera,rec_process,bitrate, quality, profilelevel):
    #camera.stop_recording()
    #camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
    if bitrate > 1000:
        camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
    else:
        camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, quality = quality)   # back to hot standby
    # Close the FFmpeg process
    time.sleep(0.5)
    rec_process.stdin.close()
    #rec_process.wait()
    print("Recording complete!")
    return rec_process, camera

#-------------Beeps-------------------

def beep(bus):
    global gonzopifolder, plughw
    if bus:
        buzzerrepetitions = 100
        buzzerdelay = 0.00001
        for _ in range(buzzerrepetitions):
            for value in [0xC, 0x4]:
                #GPIO.output(1, value)
                bus.write_byte_data(DEVICE,OLATA,value)
                time.sleep(buzzerdelay)
    else:
        run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep.wav')
    return

def longbeep(bus):
    global gonzopifolder, plughw
    if bus:
        buzzerrepetitions = 100
        buzzerdelay = 0.0001
        for _ in range(buzzerrepetitions * 5):
            for value in [0xC, 0x4]:
                #GPIO.output(1, value)
                bus.write_byte_data(DEVICE,OLATA,value)
                buzzerdelay = buzzerdelay - 0.00000004
                time.sleep(buzzerdelay)
        bus.write_byte_data(DEVICE,OLATA,0x4)
    else:
        run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep_long.wav')
    return

def buzz(buzzerlength):
    buzzerdelay = 0.0001
    for _ in range(buzzerlength):
        for value in [0xC, 0x4]:
            #GPIO.output(1, value)
            bus.write_byte_data(DEVICE,OLATA,value)
            time.sleep(buzzerdelay)
    return

#---------reading in a lens shading table----------

def read_table(inFile):
    # q&d-way to read in ls_table.h
    ls_table = []
    channel  = []
    with open(inFile) as file:       
        for line in file:
            # we skip the unimportant stuff
            if not (   line.startswith("uint") \
                    or line.startswith("}")):
                # the comments separate the color planes
                if line.startswith("//"):                
                    channel = []
                    ls_table.append(channel)
                else:
                    # scan in a single line
                    line = line.replace(',','')
                    lineData = [int(x) for x in line.split()]
                    channel.append(lineData)
    return np.array(ls_table,dtype=np.uint8)    

#-------------Check if file empty----------

def empty(filename):
    if os.path.isfile(filename + '.mp4') == False:
        return False
    if os.path.isfile(filename + '.mp4') == True:
        writemessage('Take already exists')
        time.sleep(1)
        return True

#--------------BUTTONS-------------

def waitforanykey():
    vumetermessage("press any key to continue..")
    time.sleep(1)
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    flushbutton()
    while pressed == '':
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
    return

def middlebutton():
    with term.cbreak():
        val = term.inkey(timeout=0)
    if val.is_sequence:
        event = val.name
        #print(event)
    elif val:
        event = val
        #print(event)
    else:
        event = ''
    if i2cbuttons == True:
        readbus = bus.read_byte_data(DEVICE,GPIOB)
        readbus2 = bus.read_byte_data(DEVICE,GPIOA)
        if readbus != 255:
            print('i2cbutton pressed: ' + str(readbus))
        if readbus2 != 247:
            print('i2cbutton pressed: ' + str(readbus2))
    else:
        readbus = 255
        readbus2 = 247
    pressed = ''
    if event == 'KEY_ENTER' or event == 10 or event == 13 or (readbus == 247 and readbus2 == 247):
        pressed = 'middle'
        return True
    return False

def flushbutton():
    with term.cbreak():
        while True:
            inp = term.inkey(timeout=0)
            #print('flushing ' + repr(inp))
            if inp == '':
                break

def getbutton(lastbutton, buttonpressed, buttontime, holdbutton):
    global i2cbuttons, serverstate, nextstatus, process, que, gonzopictrl_ip, recording, onlysound, filmname, filmfolder, scene, shot, take, selected, camera, loadfilmsettings, selected, newfilmname, recordwithports
    #Check controller
    pressed = ''
    nextstatus = ''
    try:
        if process.is_alive() == False and serverstate == 'on':
            nextstatus = que.get()
            if "*" in nextstatus:
                gonzopictrl_ip = nextstatus.split('*')[1]
                nextstatus = nextstatus.split('*')[0]
                print('gonzopictrl ip:' + gonzopictrl_ip)
            process = Process(target=listenforclients, args=("0.0.0.0", port, que))
            process.start()
            if 'SELECTED' in nextstatus:
                try:
                    selected=int(nextstatus.split(':')[1])
                except:
                    print('wtf?')
            if nextstatus=="PICTURE":
                pressed="picture"
            elif nextstatus=="UP":
                pressed="up"
            elif nextstatus=="DOWN":
                pressed="down"
            elif nextstatus=="LEFT":
                pressed="left"
            elif nextstatus=="RIGHT":
                pressed="right"
            elif nextstatus=="VIEW":
                pressed="view"
            elif nextstatus=="MIDDLE":
                pressed="middle"
            elif nextstatus=="DELETE":
                pressed="remove"
            elif nextstatus=="RECORD":
                pressed="record"
            elif nextstatus=="REC":
                pressed="record_now"
            elif nextstatus=="STOP":
                if recording == True:
                    pressed="record"
            elif nextstatus=="STOPRETAKE":
                if recording == True:
                    pressed="retake"
            elif nextstatus=="RECSOUND":
                if recording==False:
                    pressed="record"
                    onlysound=True
            elif nextstatus=="PLACEHOLDER":
                pressed="insert_shot"
            elif nextstatus=="TAKEPLACEHOLDER":
                pressed="insert_take"
            elif nextstatus=="NEWSCENE":
                pressed="new_scene"
            elif "NEWFILM:" in nextstatus:
                newfilmname = nextstatus.split(':')[1]
                pressed="new_film"
            elif "SYNCIP:" in nextstatus:
                pressed=nextstatus
            elif "SYNCDONE" in nextstatus:
                pressed=nextstatus
            elif "RETAKE" in nextstatus:
                if recordwithports == True:
                    pressed="retake_now"
                else:
                    pressed="retake"
            elif "RETAKE:" in nextstatus:
                pressed=nextstatus
            elif "SCENE:" in nextstatus:
                pressed=nextstatus
            elif "SHOT:" in nextstatus:
                pressed=nextstatus
            elif "SHOTSCENES:" in nextstatus:
                pressed=nextstatus
            elif "REMOVE:" in nextstatus:
                pressed=nextstatus
            elif "Q:" in nextstatus:
                pressed=nextstatus
            elif "CAMERA:" in nextstatus:
                pressed=nextstatus
            elif "move" in nextstatus:
                pressed=nextstatus
            elif "copy" in nextstatus:
                pressed=nextstatus
            elif "paste" in nextstatus:
                pressed="insert"
            elif "dub" in nextstatus:
                pressed="dub"
            elif "MAKEPLACEHOLDERS:" in nextstatus:
                pressed=nextstatus
            #print(nextstatus)
    except:
        #print('process not found')
        pass

    with term.cbreak():
        val = term.inkey(timeout=0)
    if val.is_sequence:
        event = val.name
        #print(event)
        flushbutton()
    elif val:
        event = val
        #print(event)
        flushbutton()
    else:
        event = ''
    keydelay = 0.08
    if i2cbuttons == True:
        readbus = bus.read_byte_data(DEVICE,GPIOB)
        readbus2 = bus.read_byte_data(DEVICE,GPIOA)
        if readbus == 0:
            readbus = 255
        if readbus2 == 0:
            readbus2 = 247
        if readbus != 255:
            print('i2cbutton readbus pressed: ' + str(readbus))
        if readbus2 != 247:
            print('i2cbutton readbus2 pressed: ' + str(readbus2))
    else:
        readbus = 255
        readbus2 = 247
    if buttonpressed == False:
        #if event != '':
        #    print(term.clear+term.home)
        if event == 27:
            pressed = 'quit'
        elif event == 'KEY_ENTER' or event == 10 or event == 13 or (readbus == 247 and readbus2 == 247):
            pressed = 'middle'
        elif event == 'KEY_UP' or (readbus == 191 and readbus2 == 247):
            pressed = 'up'
        elif event == 'KEY_DOWN' or (readbus == 254 and readbus2 == 247):
            pressed = 'down'
        elif event == 'KEY_LEFT' or (readbus == 239 and readbus2 == 247):
            pressed = 'left'
        elif event == 'KEY_RIGHT' or (readbus == 251 and readbus2 == 247):
            pressed = 'right'
        elif event == 'KEY_PGUP' or event == ' ' or (readbus == 127 and readbus2 == 247):
            pressed = 'record'
        elif event == 'KEY_PGDOWN' or (readbus == 253 and readbus2 == 247):
            pressed = 'retake'
        elif event == 'KEY_TAB' or (readbus == 223 and readbus2 == 247): 
            pressed = 'view'
        elif event == 'KEY_DELETE' or readbus2 == 246:
            pressed = 'remove'
        elif event == 'KEY_BACKSPACE':
            pressed = 'remove'
        elif event == 'N' or (readbus2 == 245 and readbus == 254):
            pressed = 'peak'
        elif event == 'S' or (readbus2 == 244):
            pressed = 'screen'
        elif event == 'P' or (readbus2 == 245 and readbus == 127):
            pressed = 'insert'
        elif event == 'D' or (readbus2 == 245 and readbus == 251):
            pressed = 'dub'
        elif event == 'O' or (readbus2 == 245 and readbus == 239):
            pressed = 'changemode'
        elif event == 'H' or (readbus2 == 245 and readbus == 191):
            pressed = 'showhelp'
        elif event == 'A' or (readbus2 == 245 and readbus == 253):
            pressed = 'showmenu'
        elif event == 'C' or (readbus2 == 245 and readbus == 223):
            pressed = 'copy'
        elif event == 'M' or (readbus2 == 245 and readbus == 247):
            pressed = 'move'
        elif event == '|' or (readbus2 == 245 and readbus == 251):
            pressed = 'split'
        #elif readbus2 == 247:
        #    pressed = 'shutdown'
        #if pressed != '':
            #print(pressed)
        buttontime = time.time()
        holdbutton = pressed
        buttonpressed = True
    if readbus == 255 and event == '' and nextstatus == '' :
        buttonpressed = False
    if float(time.time() - buttontime) > 0.2 and buttonpressed == True:
        if holdbutton == 'up' or holdbutton == 'down' or holdbutton == 'right' or holdbutton == 'left' or holdbutton == 'shutdown' or holdbutton == 'remove':
            pressed = holdbutton
            keydelay = 0.1
    if time.time() - buttontime > 2 and buttonpressed == True:
        keydelay = 0.08
    if time.time() - buttontime > 6 and buttonpressed == True:
        keydelay = 0.05
    if time.time() - buttontime > 8 and buttonpressed == True:
        keydelay = 0.01
    if time.time() - buttontime > 10 and buttonpressed == True:
        keydelay = 0.01
    return pressed, buttonpressed, buttontime, holdbutton, event, keydelay

def startinterface():
    call([gonzopifolder+'/startinterface.sh &'], shell = True)

def stopinterface(camera):
    try:
        camera.stop_preview()
        camera.close()
    except:
        print('no camera to close')
    os.system('pkill arecord')
    os.system('pkill startinterface')
    os.system('pkill tarinagui')
    os.system('sudo pkill -9 -f gonzopi_menu.py')
    #run_command('sudo systemctl stop apache2')
    return camera

def startcamera(camera):
    global camera_model, fps_selection, fps_selected, cammode, film_fps, film_reso, quality, profilelevel, lens, fps, bitrate
    camera = picamera.PiCamera()
    camera.meter_mode='spot'
    #camera.video_stabilization=True
    if cammode == 'film':
        if film_reso=='1920x1080':
            reso=(1920,1080)
        elif film_reso=='1920x816':
            reso=(1920,816)
        elif film_reso=='1280x720':
            reso=(1280,720)
    elif cammode == 'picture':
        reso=(4056,3040)
    camera.resolution = reso #tested modes 1920x816, 1296x552/578, v2 1640x698, 1640x1232, hqbinned 2028x1080, full 4056x3040
    #Background image
    underlay = None
    bakgimg = gonzopifolder + '/extras/bakg.jpg'
    displaybakg(camera, bakgimg, underlay, 2)
    #lensshade = ''
    #npzfile = np.load('lenses/' + lens)
    #lensshade = npzfile['lens_shading_table']
    #
    #camera frame rate sync to audio clock
    #
    camera_model, camera_revision , filmfolder = getconfig(camera)
    if os.path.isdir(filmfolder) == False:
        os.makedirs(filmfolder)
    # v1 = 'ov5647'
    # v2 = ? 
    logger.info("picamera version is: " + camera_model + ' ' + camera_revision)
    if camera_model == 'imx219':
        #table = read_table('lenses/' + lens)
        #camera.lens_shading_table = table
        camera.framerate = 24.97
    elif camera_model == 'ov5647':
        #table = read_table('lenses/' + lens)
        camera.lens_shading_table = table
        # Different versions of ov5647 with different clock speeds, need to make a config file
        # if there's more frames then the video will be longer when converting it to 25 fps,
        # I try to get it as perfect as possible with trial and error.
        # ov5647 Rev C
        if camera_revision == 'rev.C': 
            #camera.framerate = 26.03
            fps_selection=[5,8,10,11,12,13,14,15,26.03,35,49]
            fps=fps_selection[fps_selected]
            camera.framerate = fps 
        # ov5647 Rev D"
        if camera_revision == 'rev.D':
            #camera.framerate = 23.15
            fps_selection=[5,8,10,11,12,13,14,15,23.15,35,49]
            fps=fps_selection[fps_selected]
            camera.framerate = fps 
    elif camera_model == 'imx477':
        if film_fps == 25:
            #fps_selection=[5,15,24.985,35,49]
            #if sound is gettin before pic add 0.001
            #fps_selection=[5,8,10,11,12,13,14,15,24.989,35,49]-0.67s 1800s
            fps_selection=[5,8,10,11,12,13,14,15,24.989,30,35,40,42,45,49]#-0.4s 600s
            #fps_selection=[5,8,10,11,12,13,14,15,24.9888,35,49]+078 300s
            #fps_selection=[5,8,10,11,12,13,14,15,24.987,35,49]+1s 300s
            fps=fps_selection[fps_selected]
            camera.framerate = fps 
        elif film_fps == 24:
            fps_selection=[5,8,10,11,12,13,14,15,23.9894,35,49]
            fps=fps_selection[fps_selected]
            camera.framerate = fps 
        elif film_fps == 30:
            fps_selection=[5,8,10,11,12,13,14,15,29.9868,35,49]
            fps=fps_selection[fps_selected]
            camera.framerate = fps 
    else:
        camera.framerate = fps
    camera.crop = (0, 0, 1.0, 1.0)
    camera.led = False
    camera.start_preview()
    camera.awb_mode = 'auto'
    #camera.exposure_mode = 'off'            # Locks exposure/gain
    # These are the manual gains that actually fix the color cast on the HQ camera
    # Start with these values under daylight or LED lighting, then fine-tune
    camera.awb_gains = (1.7, 1.4)           # (red_gain, blue_gain)
    # Optional but helps a lot: turn off most of the ISP "beautification"
    camera.image_denoise = False
    camera.image_effect = 'none'
    # There is no direct "lens shading off" in legacy picamera,
    # but this reduces most of the extra colour shift caused by it:
    camera.drc_strength = 'off'             # disables extra tone-mapping that shifts hues
    time.sleep(1)
    if cammode == 'film':
        if bitrate > 1000:
            camera.start_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
        else:
            camera.start_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, quality = quality)   # back to hot standby
    return camera

def startcamera_preview(camera):
    global bitrate, quality, profilelevel
    if camera.recording == True:
        camera.stop_recording()
    try:
        camera.start_preview()
    except:
        print('no preview')
    if bitrate > 1000:
        camera.start_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
    else:
        camera.start_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, quality = quality)   # back to hot standby
    return camera

def stopcamera_preview(camera):
    if camera.recording == True:
        camera.stop_recording()
    try:
        camera.stop_preview()
    except:
        print('no preview')
    #camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
    #camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, quality = quality)   # back to hot standby
    # Close the FFmpeg process
    #time.sleep(0.5)
    #rec_process.wait()
    print("Camera preview stopped")
    return camera

def stopcamera(camera, rec_process):
    global bitrate, quality, profilelevel
    if camera.recording:
        camera.stop_recording()
    try:
        camera.stop_preview()
        camera.close()
    except:
        print('no camera to close')
    #camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, bitrate = bitrate)   # back to hot standby
    #camera.split_recording('/dev/null', format='h264', level=profilelevel, intra_period=5, quality = quality)   # back to hot standby
    # Close the FFmpeg process
    #time.sleep(0.5)
    try: 
        rec_process.stdin.close()
    except:
        rec_process = ''
    #rec_process.wait()
    print("Camera stopped")
    return camera

def gonzopiserver(state):
    #Gonzopi server
    if state == True:
        #Try to run apache
        try:
            run_command('sudo systemctl start apache2')
            os.system("sudo ln -sf -t "+gonzopifolder+"/srv/static/ " + filmfolder)
            os.system("sudo chown -h www-data "+gonzopifolder+"/srv/static/gonzopifilms")
            return 'on'
        except:
            os.system("sudo chown -h pi "+gonzopifolder+"/srv/static/gonzopifilms")
            writemessage("could not run gonzopi server")
            time.sleep(2)
            return 'off'
    if state == False:
        run_command('sudo systemctl stop apache2')
        return 'off'

if __name__ == '__main__':
    import sys
    try:
        main()
    except:
        os.system('pkill arecord')
        os.system('pkill startinterface')
        os.system('pkill tarinagui')
        os.system('sudo pkill -9 -f gonzopi_menu.py')
        print('Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1])
