#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄    ▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄ 
# █       █       █  █  █ █       █       █       █   █
# █   ▄▄▄▄█   ▄   █   █▄█ █▄▄▄▄   █   ▄   █    ▄  █   █
# █  █  ▄▄█  █ █  █       █▄▄▄▄█  █  █ █  █   █▄█ █   █
# █  █ █  █  █▄█  █  ▄    █ ▄▄▄▄▄▄█  █▄█  █    ▄▄▄█   █
# █  █▄▄█ █       █ █ █   █ █▄▄▄▄▄█       █   █   █   █
# █▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄█  █▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄█   █▄▄▄█

# https://gonzopi.tarina.org

import picamerax as picamera
import numpy as np
import string
import os
import time
import datetime
import multiprocessing as mp
from subprocess import call
from subprocess import Popen
from omxplayer import OMXPlayer
from multiprocessing import Process, Queue
import subprocess
import sys
import pickle
import RPi.GPIO as GPIO
from PIL import Image
import socket
import configparser
import shortuuid
import smbus
import ifaddr
import web

#import shlex
from blessed import Terminal

# bless the code!
term = Terminal()

#DEBIAN VERSION
pipe = subprocess.check_output('lsb_release -c -s', shell=True)
debianversion = pipe.decode().strip()
print('running debian ' + debianversion)

#I2CBUTTONS
probei2c = 0
while probei2c < 3:
    try:
        if debianversion == "stretch":
            os.system('sudo modprobe i2c-dev')
            bus = smbus.SMBus(3) # Rev 2 Pi uses 1
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

#MAIN
def main():
    global headphoneslevel, miclevel, gonzopifolder, screen, loadfilmsettings, plughw, channels, filmfolder, scene, showmenu, rendermenu, quality, profilelevel, i2cbuttons, menudone, soundrate, soundformat, process, serverstate, que, port, recording, onlysound, camera_model, fps_selection, fps_selected, fps, db, selected, cammode, newfilmname, camera_recording, abc
    # Get path of the current dir, then use it as working directory:
    rundir = os.path.dirname(__file__)
    if rundir != '':
        os.chdir(rundir)
    #filmfolder = "/home/pi/Videos/"
    #picfolder = "/home/pi/Pictures/"
    gonzopifolder = os.getcwd()

    #MENUS
    standardmenu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'FPS:', 'Q:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'MODE:', 'DSK:', 'SHUTDOWN', 'SRV:', 'SEARCH:', 'WIFI:', 'UPDATE', 'UPLOAD', 'BACKUP', 'LOAD', 'NEW', 'TITLE', 'LIVE:'
    gonzopictrlmenu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'FPS:', 'Q:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'MODE:', 'DSK:', 'SHUTDOWN', 'SRV:', 'SEARCH:', 'WIFI:', 'CAMERA:', 'Add CAMERA', 'New FILM', 'New SCENE', 'Sync SCENE'
    #gonzopictrlmenu = "BACK","CAMERA:", "Add CAMERA","New FILM","","New SCENE","Sync SCENE","Snapshot"
    emptymenu='','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''
    menu = standardmenu
    showgonzopictrl = False
    recordwithports = False
    pressagain = ''
    #STANDARD VALUES (some of these may not be needed, should do some clean up)
    abc = '_','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0'
    numbers_only = ' ','1','2','3','4','5','6','7','8','9','0'
    keydelay = 0.0555
    selectedaction = 0
    selected = 0
    awb = 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
    awbx = 0
    awb_lock = 'no'
    cammode = 'film'
    camera_model=''
    fps = 25
    fps_selected=2
    quality = 27
    profilelevel='4.2'
    headphoneslevel = 40
    miclevel = 50
    soundformat = 'S16_LE'
    soundrate = '48000'
    recording = False
    retake = False
    lastmenu = ''
    menudone = ''
    rendermenu = True
    showmenu = 1
    showmenu_settings = True
    showhelp = False
    overlay = None
    overlay2 = None
    underlay = None
    reclenght = 0
    t = 0
    rectime = ''
    scene = 1
    shot = 1
    take = 1
    pic = 1
    onlysound=False
    filmname = 'onthefloor'
    newfilmname = ''
    beeps = 0
    beepcountdown = 0
    beeping = False
    backlight = True
    lastbeep = time.time()
    flip = 'no'
    between = 30
    duration = 0.2
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
    moving = False
    stream = ''
    live = 'no'
    peakshot = ''
    peaktake = ''
    plughw = 0 #default audio device
    channels = 1 #default mono
    #SAVE SETTINGS FREQUENCY IN SECS
    pausetime = time.time()
    savesettingsevery = 5
    #TARINA VERSION
    f = open(gonzopifolder + '/VERSION')
    gonzopiversion = f.readline()
    gonzopivername = f.readline()

    #START INTERFACE
    startinterface()

    db=''
    #FIRE UP CAMERA
    camera = startcamera(lens,fps)
    #GET FILMFOLDER AND CAMERA VERSION
    camera_model, camera_revision , filmfolder = getconfig(camera)
    if os.path.isdir(filmfolder) == False:
        os.makedirs(filmfolder)

    #SYSTEM CONFIGS (turn off hdmi)
    #run_command('tvservice -o')
    #Kernel page cache optimization for sd card
    run_command('sudo ' + gonzopifolder + '/extras/sdcardhack.sh')
    #Make screen shut off work and run full brightness
    run_command('gpio -g mode 19 pwm ')
    run_command('gpio -g pwm 19 1023')
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

    #THUMBNAILCHECKER
    oldscene = scene
    oldshot = shot
    oldtake = take
    #TURN ON WIFI AND TARINA SERVER
    serverstate = 'on'
    wifistate = 'on'
    if os.path.isdir(gonzopifolder+'/srv/sessions') == False:
        os.makedirs(gonzopifolder+'/srv/sessions')
        os.system('chown www-data '+gonzopifolder+'/srv/sessions')
    #serverstate = gonzopiserver(False)
    #TO_BE_OR_NOT_TO_BE 
    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
    filename = 'take' + str(take).zfill(3)
    recordable = not os.path.isfile(foldername + filename + '.mp4') and not os.path.isfile(foldername + filename + '.h264')
    onthefloor_folder=filmfolder+'onthefloor'
    if os.path.isdir(onthefloor_folder) == False:
        os.makedirs(onthefloor_folder)

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
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        print("IPs of network adapter " + adapter.nice_name)
        for ip in adapter.ips:
            if ':' not in ip.ip[0] and '127.0.0.1' != ip.ip:
                print(ip.ip)
                networks=[ip.ip]
    if networks != []:
        network=networks[0]
        if network not in cameras:
            cameras=[]
            cameras.append(network)

    port = 55555
    que = Queue()
    process = Process(target=listenforclients, args=("0.0.0.0", port, que))
    process.start()
    nextstatus = ''

    serverstate_old='off'
    wifistate_old='off'

    camera_model, camera_revision, filmfolder= getconfig(camera)

    #--------------MAIN LOOP---------------#
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
                camera.stop_preview()
                camera.close()
                camera = startcamera(lens,fps)
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
            elif pressed == 'view' and menu[selected] == 'SCENE:':
                writemessage('Loading scene...')
                organize(filmfolder, filmname)
                filmfiles = shotfiles(filmfolder, filmname, scene)
                if len(filmfiles) > 0:
                    #Check if rendered video exist
                    camera.stop_preview()
                    #renderfilename, newaudiomix = renderscene(filmfolder, filmname, scene)
                    renderfilename = renderfilm(filmfolder, filmname, comp, scene, True)
                    if renderfilename != '':
                        remove_shots = playdub(filmname,renderfilename, 'film')
                        if remove_shots != []:
                            for i in remove_shots:
                                remove(filmfolder, filmname, scene, i, take, 'shot')
                            organize(filmfolder, filmname)
                            updatethumb = True
                            #loadfilmsettings = True
                            time.sleep(0.5)
                        else:
                            print('nothing to remove')
                        camera.start_preview()
                else:
                    vumetermessage("There's absolutely nothing in this scene! hit rec!")
                rendermenu = True
            #VIEW FILM
            elif pressed == 'view' and menu[selected] == 'FILM:':
                writemessage('Loading film...')
                organize(filmfolder, filmname)
                filmfiles = viewfilm(filmfolder, filmname)
                if len(filmfiles) > 0:
                    camera.stop_preview()
                    #removeimage(camera, overlay)
                    renderfilename = renderfilm(filmfolder, filmname, comp, 0, True)
                    if renderfilename != '':
                        remove_shots = playdub(filmname,renderfilename, 'film')
                    #overlay = displayimage(camera, imagename, overlay, 3)
                    camera.start_preview()
                else:
                    vumetermessage('wow, shoot first! there is zero, nada, zip footage to watch now... just hit rec!')
                rendermenu = True
            #VIEW SHOT OR TAKE
            elif pressed == 'view':
                writemessage('Loading clip...')
                organize(filmfolder, filmname)
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    removeimage(camera, overlay)
                    camera.stop_preview()
                    foldername = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    #compileshot(foldername + filename,filmfolder,filmname)
                    renderfilename, newaudiomix = rendershot(filmfolder, filmname, foldername+filename, scene, shot)
                    if renderfilename != '':
                        trim = playdub(filmname,foldername + filename, 'shot')
                        if trim:
                            take = counttakes(filmname, filmfolder, scene, shot)+1
                            trim_filename = foldername + 'take' + str(take).zfill(3)
                            videotrim(foldername + filename, trim_filename, trim[0], trim[1])
                            if os.path.exists(foldername+'dub') == True:
                                print('trim dubs here')
                        imagename = foldername + filename + '.jpeg'
                        overlay = displayimage(camera, imagename, overlay, 3)
                        camera.start_preview()
                    else:
                        vumetermessage('nothing here! hit rec!')
                    rendermenu = True
            #DUB SHOT
            elif pressed == 'middle' and menu[selected] == 'SHOT:' and recordable == False:
                newdub = clipsettings(filmfolder, filmname, scene, shot, take, plughw)
                take = counttakes(filmname, filmfolder, scene, shot)
                if newdub:
                    camera.stop_preview()
                    #save original sound
                    dubfolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/dub/'
                    saveoriginal = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take'+str(take).zfill(3)+'.wav'
                    dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene, shot)
                    foldername = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    if dubfiles==[]:
                        print('no dubs, copying original sound to original')
                        os.system('cp '+saveoriginal+' '+dubfolder+'original.wav')
                        time.sleep(2)
                    renderfilename, newaudiomix = rendershot(filmfolder, filmname, foldername+filename, scene, shot)
                    playdub(filmname,renderfilename, 'dub')
                    #run_command('sox -V0 -G /dev/shm/dub.wav -c 2 ' + newdub)
                    #add audio/video start delay sync
                    run_command('sox -V0 -G /dev/shm/dub.wav -c 2 /dev/shm/temp.wav trim 0.013')
                    run_command('mv /dev/shm/temp.wav '+ newdub)
                    audiosync, videolenght, audiolenght = audiotrim(renderfilename, 'end', newdub)
                    vumetermessage('new shot dubbing made!')
                    camera.start_preview()
                    time.sleep(1)
                else:
                    vumetermessage('see ya around!')
                rendermenu = True
            #DUB SCENE
            elif pressed == 'middle' and menu[selected] == 'SCENE:':
                newdub = clipsettings(filmfolder, filmname, scene, 0, take, plughw)
                if newdub:
                    camera.stop_preview()
                    renderfilename, newaudiomix = renderscene(filmfolder, filmname, scene)
                    playdub(filmname,renderfilename, 'dub')
                    #run_command('sox -V0 -G /dev/shm/dub.wav -c 2 ' + newdub)
                    #add audio/video start delay sync
                    run_command('sox -V0 -G /dev/shm/dub.wav -c 2 /dev/shm/temp.wav trim 0.013')
                    run_command('mv /dev/shm/temp.wav '+ newdub)
                    audiosync, videolenght, audiolenght = audiotrim(renderfilename, 'end', newdub)
                    vumetermessage('new scene dubbing made!')
                    camera.start_preview()
                    time.sleep(1)
                else:
                    vumetermessage('see ya around!')
                rendermenu = True
            #DUB FILM
            elif pressed == 'middle' and menu[selected] == 'FILM:':
                newdub = clipsettings(filmfolder, filmname, 0, 0, take, plughw)
                if newdub:
                    camera.stop_preview()
                    renderfilename = renderfilm(filmfolder, filmname, comp, 0, False)
                    playdub(filmname,renderfilename, 'dub')
                    run_command('sox -V0 -G /dev/shm/dub.wav -c 2 ' + newdub)
                    vumetermessage('new film dubbing made!')
                    camera.start_preview()
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
                        renderfilename = renderfilm(filmfolder, filmname, comp, 0, True)
                        cmd = uploadfilm(renderfilename, filmname)
                        if cmd != None:
                            stopinterface(camera)
                            try:
                                run_command(cmd)
                            except:
                                logger.warning('uploadfilm bugging')
                            startinterface()
                            camera = startcamera(lens,fps)
                            loadfilmsettings = True
                        selectedaction = 0
                rendermenu = True
            #LOAD FILM
            elif pressed == 'middle' and menu[selected] == 'LOAD':
                filmname = loadfilm(filmname, filmfolder)
                loadfilmsettings = True
            #UPDATE
            elif pressed == 'middle' and menu[selected] == 'UPDATE':
                if webz_on() == True:
                    stopinterface(camera)
                    gonzopiversion, gonzopivername = update(gonzopiversion, gonzopivername)
                    startinterface()
                    camera = startcamera(lens,fps)
                    loadfilmsettings = True
                    selectedaction = 0
                rendermenu = True
            #WIFI
            elif pressed == 'middle' and menu[selected] == 'WIFI:':
                stopinterface(camera)
                run_command('wicd-curses')
                startinterface()
                camera = startcamera(lens,fps)
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
                else:
                    print(term.clear)
                    filmname = newfilmname
                    newfilmname = ''
                    vumetermessage('film already exist!')
                    logger.info('film already exist!')
                    updatethumb = True
                    loadfilmsettings = True
                    rendermenu = True
            #EDIT FILM NAME
            elif pressed == 'middle' and menu[selected] == 'TITLE' or filmname == '':
                newfilmname = nameyourfilm(filmfolder, filmname, abc, False)
                if filmname != newfilmname:
                    os.system('mv ' + filmfolder + filmname + ' ' + filmfolder + newfilmname)
                    filmname = newfilmname
                    db = get_film_files(filmname,filmfolder,db)
                    vumetermessage('Film title changed to ' + filmname + '!')
                else:
                    vumetermessage('')
                rendermenu = True
            #(YANK) COPY TAKE
            elif pressed == 'copy' and menu[selected] == 'TAKE:' and recordable == False:
                copying = 'take'
                yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)+'/take' + str(take).zfill(3)
                vumetermessage('Take ' + str(take) + ' copied! (I)nsert button to place it...')
                time.sleep(1)
            #(YANK) COPY SHOT
            elif pressed == 'copy' and menu[selected] == 'SHOT:':
                copying = 'shot'
                yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                vumetermessage('Shot ' + str(shot) + ' copied! (I)nsert button to place it...')
                time.sleep(1)
            #(YANK) COPY SCENE
            elif pressed == 'copy' and menu[selected] == 'SCENE:':
                copying = 'scene'
                yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                vumetermessage('Scene ' + str(scene) + ' copied! (I)nsert button to place it...')
                time.sleep(1)
            #(CUT) MOVE TAKE
            elif pressed == 'move' and menu[selected] == 'TAKE:' and recordable == False:
                copying = 'take'
                moving = True
                yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)+'/take' + str(take).zfill(3)
                vumetermessage('Moving shot ' + str(shot) + ' (I)nsert button to place it...')
                time.sleep(1)
            #(CUT) MOVE SHOT
            elif pressed == 'move' and menu[selected] == 'SHOT:':
                copying='shot'
                moving = True
                yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                vumetermessage('Moving shot ' + str(shot) + ' (I)nsert button to place it...')
                time.sleep(1)
            #(CUT) MOVE SCENE
            elif pressed == 'move' and menu[selected] == 'SCENE:':
                copying='scene'
                moving = True
                yanked = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                vumetermessage('Moving scene ' + str(scene) + ' (I)nsert button to place it...')
                time.sleep(1)
            #PASTE SHOT and PASTE SCENE
            elif pressed == 'insert' and yanked:
                if copying == 'take':
                    take = counttakes(filmname, filmfolder, scene, shot)
                    take=take+1
                    vumetermessage('Pasting take, please wait...')
                    paste = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3)
                    #try:
                    #    os.makedirs(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot'+ str(shot).zfill(3))
                    #except:
                    #    pass
                    os.system('cp ' + yanked + '.mp4 ' + paste + '.mp4')
                    os.system('cp ' + yanked + '.jpeg ' + paste + '.jpeg')
                    os.system('cp ' + yanked + '.h264 ' + paste + '.h264')
                    os.system('cp ' + yanked + '.wav ' + paste + '.wav')
                    paste = ''
                    if moving == True:
                        os.system('rm -r ' + yanked + '*')
                elif copying == 'shot':
                    vumetermessage('Pasting shot, please wait...')
                    paste = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_yanked' 
                    try:
                        os.makedirs(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3))
                    except:
                        pass
                    os.system('cp -r ' + yanked + ' ' + paste)
                    if moving == True:
                        os.system('rm -r ' + yanked + '/*')
                        #Remove hidden placeholder
                        os.system('rm ' + yanked + '/.placeholder')
                elif copying == 'scene':
                    vumetermessage('Pasting scene, please wait...')
                    paste = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_yanked'
                    os.system('cp -r ' + yanked + ' ' + paste)
                    if moving == True:
                        os.system('rm -r ' + yanked + '/*')
                        #Remove hidden placeholder
                        #os.system('rm ' + yanked + '/.placeholder')
                add_organize(filmfolder, filmname)
                organize(filmfolder, filmname)
                updatethumb = True
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                yanked = ''
                copying = ''
                moving = False
                vumetermessage('Pasted!')
                time.sleep(2)
            #INSERT SHOT
            elif pressed == 'insert' and menu[selected] != 'SCENE:' and yanked == '':
                insertshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_insert'
                try:
                    os.makedirs(insertshot)
                except:
                    print('is there already prob')
                add_organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                vumetermessage('Shot ' + str(shot) + ' inserted')
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
                except:
                    print('is there already prob')
                add_organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                vumetermessage('Shot ' + str(shot) + ' inserted')
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
                vumetermessage('Take ' + str(shot) + ' inserted')
                updatethumb = True
                #time.sleep(1)
            #INSERT SCENE
            elif pressed == 'insert' and menu[selected] == 'SCENE:' and recordable == False and yanked == '':
                insertscene = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_insert'
                logger.info("inserting scene")
                os.makedirs(insertscene)
                add_organize(filmfolder, filmname)
                take = 1
                shot = 1
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
                    stopinterface(camera)
                    code.interact(local=locals())
                    startinterface()
                    camera = startcamera(lens,fps)
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
                print("clean up film folder here")
                #cleanupdisk(filmname,filmfolder)
            #REMOVE DELETE
            #take
            elif pressed == 'remove' and menu[selected] == 'TAKE:':
                remove(filmfolder, filmname, scene, shot, take, 'take')
                organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                take = counttakes(filmname, filmfolder, scene, shot)
                updatethumb = True
                rendermenu = True
                #loadfilmsettings = True
                time.sleep(0.2)
            #shot
            elif pressed == 'remove' and menu[selected] == 'SHOT:':
                remove(filmfolder, filmname, scene, shot, take, 'shot')
                organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                take = counttakes(filmname, filmfolder, scene, shot)
                updatethumb = True
                rendermenu = True
                #loadfilmsettings = True
                time.sleep(0.2)
            #scene
            elif pressed == 'remove' and menu[selected] == 'SCENE:' or pressed=='remove_now':
                remove(filmfolder, filmname, scene, shot, take, 'scene')
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
                remove(filmfolder, filmname, scene, shot, take, 'film')
                filmname = getfilms(filmfolder)[0][0]
                if filmname == '':
                    filmname = nameyourfilm(filmfolder,filmname,abc, True)
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
                ip = pressed.split(':')[1]
                vumetermessage('SYNCING!')
                stopinterface(camera)
                video_files=shotfiles(filmfolder, filmname, scene)
                for i in video_files:
                    compileshot(i,filmfolder,filmname)
                    logger.info('SYNCING:'+i)
                organize(filmfolder, filmname)
                if not os.path.isfile('/home/pi/.ssh/id_rsa'):
                    run_command('ssh-keygen')
                run_command('ssh-copy-id pi@'+ip)
                try:
                    run_command('rsync -avr --update --progress --files-from='+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/.origin_videos / pi@'+ip+':/')
                except:
                    logger.info('no origin videos')
                #run_command('scp -r '+filmfolder+filmname+'/'+'scene'+str(scene).zfill(3)+' pi@'+ip+':'+filmfolder+filmname+'/')
                sendtocamera(ip,port,'SYNCDONE:'+cameras[0])
                startinterface()
                camera = startcamera(lens,fps)
                loadfilmsettings = True
                rendermenu = True
            elif 'SYNCDONE:' in pressed:
                stopinterface(camera)
                ip = pressed.split(':')[1]
                logger.info('SYNCING from ip:'+ip)
                run_command('ssh-copy-id pi@'+ip)
                try:
                    run_command('rsync -avr --update --progress pi@'+ip+':'+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/ '+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/')
                except:
                    logger.info('no files')
                with open(filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/.origin_videos', 'r') as f:
                    scene_origin_files = [line.rstrip() for line in f]
                #a=0
                #for i in cameras:
                #    if a != 0:
                #        run_command('rsync -avr --update --progress '+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/ pi@'+i+':'+filmfolder+filmname+'/scene'+str(scene).zfill(3)+'/')
                #        time.sleep(3)
                #    a=a+1
                startinterface()
                camera = startcamera(lens,fps)
                loadfilmsettings = True
                rendermenu = True
                vumetermessage('SYNC DONE!')
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
                for i in cameras:
                    if i != cameras[0]:
                        vumetermessage('Hold on syncing!')
                        sendtocamera(i,port,'SYNCIP:'+cameras[0])
                        time.sleep(1)
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
                if len(cameras) > 1:
                    newselected = 1
            elif event == "2":
                if len(cameras) > 2:
                    newselected = 2
            elif event == "3":
                if len(cameras) > 3:
                    newselected = 3
            elif event == "4":
                if len(cameras) > 4:
                    newselected = 4
            elif event == "5":
                if len(cameras) > 5:
                    newselected = 5
            elif event == "6":
                if len(cameras) > 6:
                    newselected = 6
            elif event == "7":
                if len(cameras) > 7:
                    newselected = 7
            elif event == "8":
                if len(cameras) > 8:
                    newselected = 8
            elif event == "9":
                if len(cameras) > 9:
                    newselected = 9
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
                if len(cameras) > 1:
                    vumetermessage('filming with '+camera_model +' ip:'+ cameras[camselected] + ' '+camerasconnected+' camselected:'+str(camselected)+' rec:'+str(camera_recording))
                else:
                    vumetermessage('filming with '+camera_model +' ip:'+ network + ' '+camerasconnected+' camselected:'+str(camselected)+' rec:'+str(camera_recording))


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
                    pressed = 'record'
                print('exhausted from all beepings')
        if pressed == 'record' and recordwithports==False or pressed == 'record_now' or pressed == 'retake_now' or pressed == 'retake' and recordwithports==False or reclenght != 0 and t > reclenght:
            overlay = removeimage(camera, overlay)
            if recording == False and recordable == True or recording == False and pressed == 'record_now' or recording == False and pressed == 'retake_now':
                #camera_recording=0
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take) 
                if pressed == "record":
                    #shot = shots+1
                    take = takes+1
                elif pressed == "retake":
                    take = takes+1
                elif pressed == 'record_now':
                    shot=shots+1
                    take=1
                elif pressed == 'retake_now':
                    takes = counttakes(filmname, filmfolder, scene, shot)
                    take = takes + 1
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
                        videos_totalt = db.query("SELECT COUNT(*) AS videos FROM videos")[0]
                        tot = int(videos_totalt.videos)
                        video_origins=datetime.datetime.now().strftime('%Y%d%m')+str(tot).zfill(5)
                        db.insert('videos', tid=datetime.datetime.now(), filename=filmfolder+'.videos/'+video_origins+'.mp4', foldername=foldername, filmname=filmname, scene=scene, shot=shot, take=take, audiolenght=0, videolenght=0)
                        os.system(gonzopifolder + '/alsa-utils-1.1.3/aplay/arecord -D plughw:' + str(plughw) + ' -f '+soundformat+' -c ' + str(channels) + ' -r '+soundrate+' -vv '+ foldername + filename + '.wav &')
                        sound_start = time.time()
                        if onlysound != True:
                            camera.start_recording(filmfolder+ '.videos/'+video_origins+'.h264', format='h264', quality=quality, level=profilelevel)
                            starttime = time.time()
                        os.system('ln -sfr '+filmfolder+'.videos/'+video_origins+'.h264 '+foldername+filename+'.h264')
                        recording = True
                        showmenu = 0
                    if cammode == 'picture':
                        #picdate=datetime.datetime.now().strftime('%Y%d%m')
                        picture = foldername +'picture' + str(take).zfill(3) + '.jpeg'
                        print('taking picture')
                        camera.capture(picture,format="jpeg",use_video_port=True) 
                        run_command('touch ' + foldername + 'take' + str(take).zfill(3) + '.mp4')
                        basewidth = 800
                        img = Image.open(picture)
                        wpercent = (basewidth/float(img.size[0]))
                        hsize = int((float(img.size[1])*float(wpercent)))
                        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                        img.save(foldername+'take'+str(take).zfill(3) + '.jpeg')
                        vumetermessage('Great Pic taken!!')
                        updatethumb = True
                elif beepcountdown > 0 and beeping == True:
                    beeping = False
                    beepcountdown = 0
                    vumetermessage('Filming was canceled!!')
            elif recording == True and float(time.time() - starttime) > 0.2:
                #print(term.clear+term.home)
                disk = os.statvfs(gonzopifolder + '/')
                diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
                recording = False
                if showmenu_settings == True:
                    showmenu = 1
                if onlysound != True:
                    camera.stop_recording()
                os.system('pkill arecord')
                soundlag=starttime-sound_start
                db.update('videos', where='filename="'+filmfolder+'.videos/'+video_origins+'.mp4"', soundlag=soundlag)
                #time.sleep(0.005) #get audio at least 0.1 longer
                #camera.capture(foldername + filename + '.jpeg', resize=(800,341))
                if onlysound != True:
                    try:
                        #camera.capture(foldername + filename + '.jpeg', resize=(800,340), use_video_port=True)
                        camera.capture(foldername + filename + '.jpeg', resize=(800,450), use_video_port=True)
                    except:
                        logger.warning('something wrong with camera jpeg capture')
                #delayerr = audiotrim(foldername,filename)
                onlysound = False
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                if beeps > 0:
                    if bus:
                        buzz(300)
                    else:
                        run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep.wav')
                if round(fps) != 25:
                    compileshot(foldername + filename,filmfolder,filmname)
                #os.system('cp /dev/shm/' + filename + '.wav ' + foldername + filename + '.wav')
                if beeps > 0:
                    if bus:
                        buzz(150)
                    else:
                        run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep.wav')
                t = 0
                rectime = ''
                vumetermessage('Gonzopi ' + gonzopiversion[:-1] + ' ' + gonzopivername[:-1])
                updatethumb = True
                #camera_recording=0
            #if not in last shot or take then go to it
            if pressed == 'record' and recordable == False:
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                shot=shots+1
                take=1
                #take = takes
                #takes = counttakes(filmname, filmfolder, scene, shot)
            if pressed == 'retake' and recordable == False:
                #scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                takes = counttakes(filmname, filmfolder, scene, shot)
                #take = takes
                #takes = counttakes(filmname, filmfolder, scene, shot)
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
            reclenght = 0
        elif pressed == 'middle' and menu[selected] == 'LIVE:':
            if stream == '':
                stream = startstream(camera, stream, plughw, channels)
                if stream == '':
                    vumetermessage('something wrong with streaming')
                else:
                    live = 'yes'
            else:
                stream = stopstream(camera, stream)
                live = 'no'
        elif pressed == 'middle' and menu[selected] == 'BRIGHT:':
            camera.brightness = 50
        elif pressed == 'middle' and menu[selected] == 'CONT:':
            camera.contrast = 0
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

        #UP
        elif pressed == 'up':
            if menu[selected] == 'FILM:':
                filmname = 'onthefloor'
                filmname_back = filmname
                filmname = loadfilm(filmname, filmfolder)
                loadfilmsettings = True
            if menu[selected] == 'BRIGHT:':
                camera.brightness = min(camera.brightness + 1, 99)
            elif menu[selected] == 'CONT:':
                camera.contrast = min(camera.contrast + 1, 99)
            elif menu[selected] == 'SAT:':
                camera.saturation = min(camera.saturation + 1, 99)
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
            elif menu[selected] == 'LENGTH:':
                reclenght = reclenght + 1
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
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shots, takes = browse2(filmname, filmfolder, scene, shot, take, 0, 1)
                #shot = 1
            elif menu[selected] == 'SHOT:' and recording == False:
                if shot <= shots:
                    shot += 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, 1)
                #takes = take
            elif menu[selected] == 'TAKE:' and recording == False:
                if take <= takes:
                    take += 1
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
                camera.stop_preview()
                camera.close()
                camera = startcamera(lens,fps)
                loadfilmsettings = True
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
                if camera_model == 'imx477':
                    if fps_selected < len(fps_selection)-1:
                        fps_selected+=1
                        fps_selection=[5,8,10,11,12,13,14,15,24.985,35,49]
                        fps=fps_selection[fps_selected]
                        camera.framerate = fps
            elif menu[selected] == 'Q:':
                if quality < 39:
                    quality += 1
            elif menu[selected] == 'CAMERA:':
                if camselected < len(cameras)-1:
                    newselected = camselected+1
                    logger.info('camera selected:'+str(camselected))

        #LEFT
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
            else:
                selected = len(menu) - 1
            if selected == 4:
                selected = 3
        #DOWN
        elif pressed == 'down':
            if menu[selected] == 'FILM:':
                if filmname == 'onthefloor':
                    try:
                        filmname = getfilms(filmfolder)[1][0]
                    except:
                        filmname='onthefloor'
                    filename_back = 'onthefloor'
                    loadfilmsettings = True
                else:
                    filmname = 'onthefloor'
                    loadfilmsettings = True
            elif menu[selected] == 'BRIGHT:':
                camera.brightness = max(camera.brightness - 1, 0)
            elif menu[selected] == 'CONT:':
                camera.contrast = max(camera.contrast - 1, -100)
            elif menu[selected] == 'SAT:':
                camera.saturation = max(camera.saturation - 1, -100)
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
                if reclenght > 0:
                    reclenght = reclenght - 1
                    time.sleep(0.1)
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
                    shot=1
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shots, take = browse2(filmname, filmfolder, scene, shot, take, 0, -1)
                #takes = take
                #shot = 1
            elif menu[selected] == 'SHOT:' and recording == False:
                if shot > 1:
                    shot -= 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, -1)
                #takes = take
            elif menu[selected] == 'TAKE:' and recording == False:
                if take > 1:
                    take -= 1
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
                camera.stop_preview()
                camera.close()
                camera = startcamera(lens,fps)
                loadfilmsettings = True
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
                if camera_model == 'imx477':
                    if fps_selected > 0:
                        fps_selected-=1
                        fps_selection=[5,8,10,11,12,13,14,15,24.985,35,49]
                        fps=fps_selection[fps_selected]
                        camera.framerate = fps
            elif menu[selected] == 'Q:':
                if quality > 10:
                    quality -= 1
            elif menu[selected] == 'CAMERA:':
                if camselected > 0:
                    newselected = camselected-1
                    logger.info('camera selected:'+str(camselected))

        #RIGHT
        elif pressed == 'right':
            if selected < len(menu) - 1:
                selected = selected + 1
            else:
                selected = 0
            if selected == 4: #jump over recording time
                selected = 5
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
                cammode=filmsettings[23]
                scene=filmsettings[24]
                shot=filmsettings[25]
                take=filmsettings[26]
                logger.info('film settings loaded & applied')
                time.sleep(0.2)
            except:
                logger.warning('could not load film settings')
            if flip == "yes":
                camera.vflip = True
                camera.hflip = True
            run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            origin_videos=organize(filmfolder, filmname)
            print('ORIGIN')
            print(origin_videos)
            print('total of videos: '+str(len(origin_videos)))
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
            organize(filmfolder,'onthefloor')
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
                filename = 'take' + str(take).zfill(3)
                recordable = not os.path.isfile(foldername + filename + '.mp4') and not os.path.isfile(foldername + filename + '.h264')
                overlay = removeimage(camera, overlay)
                if menu[selected] == 'SCENE:' and recordable == False: # display first shot of scene if browsing scenes
                    p = counttakes(filmname, filmfolder, scene, 1)
                    imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                #elif menu[selected] == 'FILM:' and recordable == True:
                #    scene, shot, take = countlast(filmname,filmfolder)
                #    shot += 1
                elif menu[selected] == 'FILM:' and recordable == False: # display first shot of film
                    p = counttakes(filmname, filmfolder, 1, 1)
                    imagename = filmfolder + filmname + '/scene' + str(1).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3) + '.jpeg'
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

        #Check if menu is changed and save settings / sec
        if buttonpressed == True or recording == True or rendermenu == True:
            lastmenu = menu[selected]
            if showgonzopictrl == False:
                menu = standardmenu
                settings = filmname, str(scene) + '/' + str(scenes), str(shot) + '/' + str(shots), str(take) + '/' + str(takes), rectime, camerashutter, cameraiso, camerared, camerablue, str(round(camera.framerate)), str(quality), str(camera.brightness), str(camera.contrast), str(camera.saturation), str(flip), str(beeps), str(reclenght), str(plughw), str(channels), str(miclevel), str(headphoneslevel), str(comp), '', cammode, diskleft, '', serverstate, searchforcameras, wifistate, '', '', '', '', '', '', live
            else:
                #gonzopictrlmenu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'FPS:', 'Q:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'MODE:', 'DSK:', 'SHUTDOWN', 'SRV:', 'SEARCH:', 'WIFI:', 'CAMERA:', 'Add CAMERA', 'New FILM', 'Sync FILM', 'Sync SCENE'
                menu = gonzopictrlmenu
                #settings = '',str(camselected),'','',rectime,'','','','','','','','','',''
                settings = filmname, str(scene) + '/' + str(scenes), str(shot) + '/' + str(shots), str(take) + '/' + str(takes), rectime, camerashutter, cameraiso, camerared, camerablue, str(round(camera.framerate)), str(quality), str(camera.brightness), str(camera.contrast), str(camera.saturation), str(flip), str(beeps), str(reclenght), str(plughw), str(channels), str(miclevel), str(headphoneslevel), str(comp), '', cammode, diskleft, '', serverstate, searchforcameras, wifistate, str(camselected), '', '', '', '', '', ''
            #Rerender menu if picamera settings change
            #if settings != oldsettings or selected != oldselected:
            writemenu(menu,settings,selected,'',showmenu)
            rendermenu = False
            #save settings if menu has been updated and x seconds passed
            if recording == False:
                #if time.time() - pausetime > savesettingsevery: 
                if oldsettings != settings:
                    settings_to_save = [filmfolder, filmname, camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, comp, between, duration, showmenu_settings, quality,wifistate,serverstate,plughw,channels,cammode,scene,shot,take]
                    #print('saving settings')
                    savesettings(settings_to_save, filmname, filmfolder)
                if time.time() - pausetime > savesettingsevery: 
                    pausetime = time.time()
                    #NETWORKS
                    networks=[]
                    adapters = ifaddr.get_adapters()
                    for adapter in adapters:
                        print("IPs of network adapter " + adapter.nice_name)
                        for ip in adapter.ips:
                            if ':' not in ip.ip[0] and '127.0.0.1' != ip.ip:
                                print(ip.ip)
                                networks=[ip.ip]
                    if networks != []:
                        network=networks[0]
                        if network not in cameras:
                            cameras=[]
                            cameras.append(network)
                    else:
                        network='not connected'
                    if len(cameras) > 1:
                        camerasconnected='connected '+str(len(cameras)-1)
                        recordwithports=True
                        vumetermessage('filming with '+camera_model +' ip:'+ cameras[camselected] + ' '+camerasconnected+' camselected:'+str(camselected)+' rec:'+str(camera_recording))
                    else:
                        camerasconnected=''
                        recordwithports=False
                        if searchforcameras == 'on':
                            camerasconnected='searching '+str(pingip)
                        vumetermessage('filming with '+camera_model +' ip:'+ network + ' '+camerasconnected)
                    disk = os.statvfs(gonzopifolder + '/')
                    diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
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
    filmdb = filmfolder+'.videos/gonzopi.db'
    db = web.database(dbn='sqlite', db=filmdb)
    try:
        videodb=db.select('videos')
        return db
    except:
        db.query("CREATE TABLE videos (id integer PRIMARY KEY, tid DATETIME, filename TEXT, foldername TEXT, filmname TEXT, scene INT, shot INT, take INT, audiolenght FLOAT, videolenght FLOAT,soundlag FLOAT, audiosync FLOAT);")
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
    except:
        print('did not connect')
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

def writemenu(menu,settings,selected,header,showmenu):
    global menudone, rendermenu
    oldmenu=menudone
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
    if oldmenu != menudone or rendermenu == True:
        print(term.clear+term.home)
        if showmenu == 0:
            print(term.red+menudoneprint)
        else:
            print(menudoneprint)
        #menudone += 'EOF'
        f = open('/dev/shm/interface', 'w')
        f.write(menudone)
        f.close()
        return menudone

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
        size = os.stat(filename).st_size
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
        if '.mp4' in a or '.h264' in a:
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
        if 'shot' in a:
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
        if '.mp4' in a or '.h264' in a:
            if not doubles.replace('.h264', '.mp4') == a:
                takes = takes + 1
            doubles = a
    return takes

#-----------Count videos on floor-----

def countonfloor(filmname, filmfolder):
    print('dsad')


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
    filmfolder=''
    version = camera.revision
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
    if version == 'imx219':
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
            writemenu(menu,settings,selected,header,showmenu)
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

    if filmfolder != '':
        return version, camera_revision, filmfolder+'/'
    else:
        filmfolder = namesomething('Your film folder: ', home+'/Videos')
        config['USER'] = {}
        config['USER']['filmfolder'] = filmfolder
        with open(configfile, 'w') as f:
            config.write(f)
        return camera_model, camera_revision, filmfolder+'/'

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

def loadfilm(filmname, filmfolder):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    films = getfilms(filmfolder)
    filmsize=[]
    for f in films:
        filmsize.append(du(filmfolder+f[0]))
    filmstotal = len(films[1:])
    selectedfilm = 0
    selected = 0
    header = 'Up and down to select and load film'
    menu = 'FILM:', 'BACK'
    while True:
        settings = films[selectedfilm][0], ''
        writemenu(menu,settings,selected,header,showmenu)
        vumetermessage('filmsize: '+filmsize[selectedfilm]+' date: '+time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(films[selectedfilm][1])))
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'down':
            if selectedfilm < filmstotal:
                selectedfilm = selectedfilm + 1
        elif pressed == 'up':
            if selectedfilm > 0:
                selectedfilm = selectedfilm - 1
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and menu[selected] == 'FILM:':
            filmname = films[selectedfilm][0]
            return filmname
        elif pressed == 'middle' and menu[selected] == 'BACK':
            writemessage('Returning')
            return filmname
        time.sleep(0.02)


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
    oldfilmname = filmname
    if newfilm == True:
        filmname = ''
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
                    elif filmname not in getfilms(filmfolder)[0]:
                        logger.info("New film " + filmname)
                        return(filmname)
                except:
                    logger.info("New film " + filmname)
                    return(filmname)
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
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    sound = False
    selected = 0
    header = 'Adjust delay in seconds between videos'
    menu = 'DELAY:', 'DURATION:', 'SOUND:', 'START', 'BACK'
    while True:
        settings = str(round(between,2)), str(round(duration,2)), str(sound), '', ''
        writemenu(menu,settings,selected,header,showmenu)
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
                    vumetermessage('Timelapse lenght is now ' + str(round(n * duration,2)) + ' second clip   ')
                    if recording == False and t > between:
                        if beeps > 0:
                            if bus:
                                buzz(150)
                            else:
                                run_command('aplay -D plughw:' + str(plughw) + ' '+ gonzopifolder + '/extras/beep.wav')
                        #camera.start_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', quality=26, bitrate=5000000)
                        camera.start_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', quality=quality, level=profilelevel)
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
                        camera.stop_recording()
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
                            camera.stop_recording()
                        #create thumbnail
                        try:
                            camera.capture(foldername + filename + '.jpeg', resize=(800,450), use_video_port=True)
                        except:
                            logger.warning('something wrong with camera jpeg capture')
                        writemessage('Compiling timelapse')
                        logger.info('Hold on, rendering ' + str(len(files)) + ' scenes')
                        #RENDER VIDEO
                        renderfilename = foldername + filename
                        n = 1
                        videomerge = ['MP4Box']
                        videomerge.append('-force-cat')
                        for f in files:
                            if sound == True:
                                compileshot(f,filmfolder,filmname)
                                audiotrim(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3), 'end', '')
                                videomerge.append('-cat')
                                videomerge.append(f + '.mp4')
                            else:
                                videomerge.append('-cat')
                                videomerge.append(f + '.h264')
                            n = n + 1                            
                        videomerge.append('-new')
                        videomerge.append(renderfilename + '.mp4')
                        call(videomerge, shell=False) #how to insert somekind of estimated time while it does this?
                        ##RENDER AUDIO
                        if sound == True:
                            writemessage('Rendering sound')
                            audiomerge = ['sox']
                            #if render > 2:
                            #    audiomerge.append(filename + '.wav')
                            for f in files:
                                audiomerge.append(f + '.wav')
                            audiomerge.append(renderfilename + '.wav')
                            call(audiomerge, shell=False)
                        ##MAKE AUDIO SILENCE
                        if sound == False:
                            audiosilence(foldername,filename)
                        #cleanup
                        #os.system('rm -r ' + foldername + 'timelapse')
                        vumetermessage('timelapse done! ;)')
                        return renderfilename, between, duration
                    time.sleep(keydelay)
            if menu[selected] == 'BACK':
                vumetermessage('ok!')
                return '', between, duration
        time.sleep(keydelay)

#------------Remove-----------------------

def remove(filmfolder, filmname, scene, shot, take, sceneshotortake):
    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
    filename = 'take' + str(take).zfill(3)
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    time.sleep(0.1)
    header = 'Are you sure you want to remove ' + sceneshotortake + '?'
    menu = '', ''
    settings = 'NO', 'YES'
    selected = 0
    otf_scene = countscenes(filmfolder, 'onthefloor')
    otf_scene += 1
    otf_shot = countshots('onthefloor', filmfolder, otf_scene)
    otf_shot += 1
    otf_take = counttakes('onthefloor', filmfolder, otf_scene, otf_shot)
    otf_take += 1
    while True:
        writemenu(menu,settings,selected,header,showmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle':
            if selected == 1:
                if filmname == 'onthefloor':
                    if sceneshotortake == 'take':
                        os.system('rm ' + foldername + filename + '.h264')
                        os.system('rm ' + foldername + filename + '.mp4')
                        os.system('rm ' + foldername + filename + '.wav')
                        os.system('rm ' + foldername + filename + '.jpeg')
                    elif sceneshotortake == 'shot' and shot > 0:
                        os.system('rm -r ' + foldername)
                    elif sceneshotortake == 'scene':
                        foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                        os.system('rm -r ' + foldername)
                        scene = countscenes(filmfolder, filmname)
                        shot=1
                        take=1
                    elif sceneshotortake == 'film':
                        foldername = filmfolder + filmname
                        os.system('rm -r ' + foldername)
                        os.makedirs(filmfolder+'onthefloor')
                    return
                else:
                    if sceneshotortake == 'take':
                        writemessage('Throwing take on the floor' + str(take))
                        onthefloor = filmfolder + 'onthefloor/' + 'scene' + str(otf_scene).zfill(3) + '/shot' + str(otf_shot).zfill(3) + '/take' + str(otf_take).zfill(3) 
                        onthefloor_folder = filmfolder + 'onthefloor/' + 'scene' + str(otf_scene).zfill(3) + '/shot' + str(otf_shot).zfill(3) + '/'
                        if os.path.isdir(onthefloor_folder) == False:
                            os.makedirs(onthefloor)
                        os.system('mv ' + foldername + filename + '.h264 ' + onthefloor + '.h264')
                        os.system('mv ' + foldername + filename + '.mp4 ' + onthefloor + '.mp4')
                        os.system('mv ' + foldername + filename + '.wav ' + onthefloor + '.wav')
                        os.system('mv ' + foldername + filename + '.jpeg ' + onthefloor + '.jpeg')
                        take = take - 1
                        if take == 0:
                            take = 1
                    elif sceneshotortake == 'shot' and shot > 0:
                        writemessage('Throwing shot on the floor' + str(shot))
                        onthefloor = filmfolder + 'onthefloor/' + 'scene' + str(otf_scene).zfill(3) + '/shot' + str(otf_shot).zfill(3)+'/'
                        os.makedirs(onthefloor)
                        os.system('cp -r '+foldername+'* '+onthefloor)
                        os.system('rm -r '+foldername)
                        take = counttakes(filmname, filmfolder, scene, shot)
                    elif sceneshotortake == 'scene':
                        onthefloor = filmfolder + 'onthefloor/' + 'scene' + str(otf_scene).zfill(3)
                        os.makedirs(onthefloor)
                        writemessage('Throwing clips on the floor ' + str(scene))
                        foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                        os.system('mv ' + foldername + '/* ' + onthefloor+'/' )
                        scene = countscenes(filmfolder, filmname)
                        shot = 1
                        take = 1
                    elif sceneshotortake == 'film':
                        foldername = filmfolder + filmname
                        os.system('rm -r ' + foldername)
                    organize(filmfolder, 'onthefloor')
                return
            elif selected == 0:
                return
        time.sleep(0.02)

#------------Remove and Organize----------------

def organize(filmfolder, filmname):
    global fps, db
    origin_files=[]
    scenes = next(os.walk(filmfolder + filmname))[1]
    for i in scenes:
        if 'scene' not in i:
            scenes.remove(i)
    # Takes
    for i in sorted(scenes):
        origin_scene_files=[]
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        for p in sorted(shots):
            takes = next(os.walk(filmfolder + filmname + '/' + i + '/' + p))[2]
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
                        run_command(mv + '.h264 ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.h264')
                        run_command(mv + '.wav ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.wav')
                        run_command(mv + '.jpeg ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.jpeg')
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
            if 'yanked' in p:
                #print(p)
                os.system('mv -n ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr - 1).zfill(3) + '_yanked ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
            elif 'insert' in p:
                os.system('mv -n ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr - 1).zfill(3) + '_insert ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
                run_command('touch ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3) + '/.placeholder')
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
        if 'yanked' in i:
            os.system('mv -n ' + filmfolder + filmname + '/scene' + str(organized_nr - 1).zfill(3) + '_yanked ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
        elif 'insert' in i:
            #print(p)
            os.system('mv -n ' + filmfolder + filmname + '/scene' + str(organized_nr - 1).zfill(3) + '_insert ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
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


#-------------Stretch Audio--------------

def stretchaudio(filename,fps):
    fps_rounded=round(fps)
    if int(fps_rounded) != 25:
        pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
        videolenght = pipe.decode().strip()
        try:
            pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + filename + '.wav', shell=True)
            audiolenght = pipe.decode().strip()
        except:
            audiosilence('',filename)
            audiolenght=videolenght
        #if there is no audio lenght
        logger.info('audio is:' + audiolenght)
        if not audiolenght.strip():
            audiolenght = 0
        ratio = int(audiolenght)/int(videolenght)
        print(str(ratio))
        run_command('cp '+filename+'.wav '+filename+'_temp.wav')
        run_command('ffmpeg -y -i ' + filename + '_temp.wav -filter:a atempo="'+str(ratio) + '" ' + filename + '.wav')
        os.remove(filename + '_temp.wav')
    #time.sleep(5)
    return

#-------------Compile Shot--------------

def compileshot(filename,filmfolder,filmname):
    global fps, soundrate, channels
    videolenght=0
    audiolenght=0
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
        run_command('MP4Box -fps 25 -add ' + video_origins + '.h264 ' + video_origins + '.mp4')
        os.system('ln -sfr '+video_origins+'.mp4 '+filename+'.mp4')
        if not os.path.isfile(filename + '.wav'):
            audiosilence('',filename)
        #add audio/video start delay sync
        run_command('sox -V0 '+filename+'.wav -c 2 /dev/shm/temp.wav trim 0.013')
        run_command('mv /dev/shm/temp.wav '+ filename + '.wav')
        stretchaudio(filename,fps)
        audiosync, videolenght, audiolenght = audiotrim(filename, 'end','')
        muxing = False
        if muxing == True:
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
            call(['MP4Box', '-fps', '25', '-add', video_origins + '.mp4', '-add', filename + '.mp3', '-new', video_origins + '_tmp.mp4'], shell=False)
            os.system('cp -f ' + video_origins + '_tmp.mp4 ' + video_origins + '.mp4')
            os.remove(video_origins + '_tmp.mp4')
            os.remove(filename + '.mp3')
        origin=os.path.realpath(filename+'.mp4')
        db.update('videos', where='filename="'+origin+'"', videolenght=videolenght/1000, audiolenght=audiolenght/1000, audiosync=audiosync)
        os.system('rm ' + video_origins + '.h264')
        os.system('rm ' + filename + '.h264')
        os.system('rm /dev/shm/temp.wav')
        os.system('ln -sfr '+video_origins+'.mp4 '+filename+'.mp4')
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

def rendervideo(filmfiles, filename, renderinfo):
    if len(filmfiles) < 1:
        writemessage('Nothing here!')
        time.sleep(2)
        return None
    print('Rendering videofiles')
    writemessage('Hold on, rendering ' + renderinfo + ' with ' + str(len(filmfiles)) + ' files')
    videosize = 0
    rendersize = 0
    videomerge = ['MP4Box']
    videomerge.append('-force-cat')
    for f in filmfiles[:]:
        videosize = videosize + countsize(f + '.mp4')
        videomerge.append('-cat')
        videomerge.append(f + '.mp4#video')
    videomerge.append('-new')
    videomerge.append(filename + '.mp4')
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
    print('Video rendered!')
    return

#---------------Render Audio----------------

def renderaudio(audiofiles, filename, dubfiles, dubmix):
    #if len(audiofiles) < 1:
    #    writemessage('Nothing here!')
    #    time.sleep(2)
    #    return None
    print('Rendering audiofiles')
    ##PASTE AUDIO TOGETHER
    writemessage('Hold on, rendering audio...')
    audiomerge = ['sox']
    #if render > 2:
    #    audiomerge.append(filename + '.wav')
    if isinstance(audiofiles, list):
        for f in audiofiles:
            audiomerge.append(f + '.wav')
        audiomerge.append(filename + '.wav')
        call(audiomerge, shell=False)
    else:
        #if rendering scene with one shot
        if audiofiles[0] != filename:
            os.system('cp '+audiofiles[0]+'.wav '+filename+'.wav')
    #DUBBING
    p = 1
    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
    videolenght = pipe.decode().strip()
    audiolenght=videolenght
    for i, d in zip(dubmix, dubfiles):
        writemessage('Dub ' + str(p) + ' audio found lets mix...')
        #first trimit!
        audiotrim(filename, 'end', d)
        try:
            pipe = subprocess.check_output('soxi -D ' + d, shell=True)
            dubaudiolenght = pipe.decode()
            if dubaudiolengt != videolenght:
                print('dub wrong lenght!')
                time.sleep(5)
        except:
            pass
        os.system('cp ' + filename + '.wav ' + filename + '_tmp.wav')
        #Fade and make stereo
        run_command('sox -V0 -G ' + d + ' /dev/shm/fade.wav fade ' + str(round(i[2],1)) + ' 0 ' + str(round(i[3],1)))
        run_command('sox -V0 -G -m -v ' + str(round(i[0],1)) + ' /dev/shm/fade.wav -v ' + str(round(i[1],1)) + ' ' + filename + '_tmp.wav ' + filename + '.wav trim 0 ' + audiolenght)
        os.remove(filename + '_tmp.wav')
        os.remove('/dev/shm/fade.wav')
        print('Dub mix ' + str(p) + ' done!')
        p += 1
    return

#-------------Fast Edit-----------------
def fastedit(filmfolder, filmname, filmfiles, scene):
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
    totlenght = 0
    try:
        os.remove(scenedir + '.fastedit')
    except:
        print('no fastedit file')
    for f in filmfiles:
        pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + f + '.mp4', shell=True)
        videolenght = pipe.decode().strip()
        totlenght = int(videolenght) + totlenght
        print('writing shot lenghts for fastedit mode')
        with open(scenedir + '.fastedit', 'a') as f:
            f.write(str(totlenght)+'\n')
    

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
    global fps
    #This function checks and calls rendervideo & renderaudio if something has changed in the film
    #Video
    videohash = ''
    oldvideohash = ''
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
    #take = counttakes(filmname, filmfolder, scene, shot)
    #renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3) 
    #return if no file
    # Video Hash
    if os.path.isfile(renderfilename + '.h264') == True:
        compileshot(renderfilename,filmfolder,filmname)
        audiohash = str(int(countsize(renderfilename + '.wav')))
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
    #if something shutdown in middle of process
    elif os.path.isfile(renderfilename + '_tmp.mp4') == True:
        os.system('cp ' + renderfilename + '_tmp.mp4 ' + renderfilename + '.mp4')
    elif os.path.isfile(renderfilename + '.mp4') == True:
        videohash = videohash + str(int(countsize(renderfilename + '.mp4')))
        video_origins = (os.path.realpath(renderfilename+'.mp4'))[:-4]
        print('Videohash of shot is: ' + videohash)
        #time.sleep(3)
    else:
        vumetermessage('Nothing here to play hit record')
        return '', ''
    #if os.path.isfile(renderfilename + '.h264') and os.path.isfile(renderfilename + '.mp4'):
    #    os.system('rm ' + renderfilename + '.h264 ')
    # Check if video corrupt
    renderfix = False
    if os.path.isfile(renderfilename + '.jpeg') == False: 
        run_command('ffmpeg -sseof -1 -i ' + renderfilename + '.mp4 -update 1 -q:v 1 -vf scale=800:450 ' + renderfilename + '.jpeg')
    try:
        pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + renderfilename + '.mp4', shell=True)
        videolenght = pipe.decode().strip()
    except:
        videolenght = ''
    print('Shot lenght ' + videolenght)
    if videolenght == '':
        print('Okey, shot file not found or is corrupted')
        # For backwards compatibility remove old rendered scene files
        # run_command('rm ' + renderfilename + '*')
        return '', ''
        #renderfix = True
    try:
        with open(scenedir + '.videohash', 'r') as f:
            oldvideohash = f.readline().strip()
        print('oldvideohash is: ' + oldvideohash)
    except:
        print('no videohash found, making one...')
        with open(scenedir + '.videohash', 'w') as f:
            f.write(videohash)
    #Audio
    audiohash = ''
    oldaudiohash = ''
    newaudiomix = False
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
        #time.sleep(3)
        #make scene rerender
        os.system('touch '+filmfolder + filmname + '/scene' + str(scene).zfill(3)+'/.rerender')
        #copy original sound
        if os.path.exists(scenedir+'dub') == True:
            os.system('cp '+scenedir+'dub/original.wav '+renderfilename+'.wav')
        #os.system('cp '+dubfolder+'original.wav '+renderfilename+'.wav')
        renderaudio(renderfilename, renderfilename, dubfiles, dubmix)
        print('updating audiohash...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
        for i in range(len(dubfiles)):
            os.system('cp ' + scenedir + '/dub/.settings' + str(i + 1).zfill(3) + ' ' + scenedir + '/dub/.rendered' + str(i + 1).zfill(3))
        print('Audio rendered!')
        newaudiomix = True
        muxing = True
        if muxing == True:
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
            call(['MP4Box', '-fps', '25', '-add', video_origins + '.mp4', '-add', renderfilename + '.mp3', '-new', video_origins + '_tmp.mp4'], shell=False)
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
        logger.info('compile done!')
    else:
        print('Already rendered!')
    return renderfilename, newaudiomix


#-------------Render Scene-------------

def renderscene(filmfolder, filmname, scene):
    global fps
    #This function checks and calls rendervideo & renderaudio if something has changed in the film
    #Video
    videohash = ''
    oldvideohash = ''
    filmfiles = shotfiles(filmfolder, filmname, scene)
    renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene'
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
    # Check if video corrupt
    renderfixscene = False
    try:
        pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + renderfilename + '.mp4', shell=True)
        videolenght = pipe.decode().strip()
    except:
        videolenght = ''
        renderfixscene = True
    print('Scene lenght ' + videolenght)
    if videolenght == '':
        print('Okey, hold your horses, rendering!')
        # For backwards compatibility remove old rendered scene files
        #run_command('rm ' + renderfilename + '.mp4')
        #run_command('rm ' + renderfilename + '.wav')
        #vumetermessage('corrupted scene file! removing, please render again')
        renderfixscene = True
        #return '', ''
    # Video Hash
    for p in filmfiles:
        #compileshot(p,filmfolder,filmname)
        #print(p)
        #time.sleep(5)
        scene = int(p.rsplit('scene',1)[1][:3])
        shot = int(p.rsplit('shot',1)[1][:3])
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
    if videohash != oldvideohash or renderfixscene == True or renderfix == True:
        rendervideo(filmfiles, renderfilename, 'scene ' + str(scene))
        fastedit(filmfolder, filmname, filmfiles, scene)
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
        renderaudio(filmfiles, renderfilename, dubfiles, dubmix)
        print('updating audiohash...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
        for i in range(len(dubfiles)):
            os.system('cp ' + scenedir + '/dub/.settings' + str(i + 1).zfill(3) + ' ' + scenedir + '/dub/.rendered' + str(i + 1).zfill(3))
        print('Audio rendered!')
        newaudiomix = True
        muxing = True
        if muxing == True:
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
            call(['MP4Box', '-add', renderfilename + '_tmp.mp4', '-add', renderfilename + '.mp3', '-new', renderfilename + '.mp4'], shell=False)
            os.remove(renderfilename + '_tmp.mp4')
            os.remove(renderfilename + '.mp3')
    else:
        print('Already rendered!')
    return renderfilename, newaudiomix

#-------------Render film------------

def renderfilm(filmfolder, filmname, comp, scene, muxing):
    global fps
    def render(q, filmfolder, filmname, comp, scene):
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
            rendervideo(filmfiles, renderfilename, filmname)
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
            renderaudio(filmfiles, renderfilename, dubfiles, dubmix)
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
            if muxing == True:
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
                call(['MP4Box', '-add', renderfilename + '_tmp.mp4', '-add', renderfilename + '.mp3', '-new', renderfilename + '.mp4'], shell=False)
                os.remove(renderfilename + '_tmp.mp4')
                os.remove(renderfilename + '.mp3')
        else:
            print('Already rendered!')
        q.put(renderfilename)
    q = mp.Queue()
    proc = mp.Process(target=render, args=(q,filmfolder,filmname,comp,scene))
    proc.start()
    procdone = False
    status = ''
    vumetermessage('press middlebutton to cancel')
    while True:
        if proc.is_alive() == False and procdone == False:
            status = q.get()
            print(status)
            procdone = True
            proc.join()
            renderfilename = status
            vumetermessage('')
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
    if scene > 0 and shot == 0:
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
    while True:
        writemenu(menu,settings,selected,header,showmenu)
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

def clipsettings(filmfolder, filmname, scene, shot, take, plughw):
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
            settings = '', 'd:' + str(nmix) + '/o:' + str(ndub), 'in:' + str(nfadein), 'out:' + str(nfadeout), '', 'd:' + str(mix) + '/o' + str(dub), 'in:' + str(fadein), 'out:' + str(fadeout)
        else:
            menu = 'BACK', 'ADD:', '', ''
            settings = '', 'd:' + str(nmix) + '/o:' + str(ndub), 'in:' + str(nfadein), 'out:' + str(nfadeout)
        writemenu(menu,settings,selected,header,showmenu)
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
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and menu[selected] == 'BACK':
            os.system('pkill aplay')
            break
        elif pressed == 'view': # mix dub and listen
            run_command('pkill aplay')
            dubfiles, dubmix, rerender = getdubs(filmfolder, filmname, scene, shot)
            if scene:
                filename = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/scene'
            else:
                filename = filmfolder + filmname + '/' + filmname
            renderfilename = renderfilm(filmfolder, filmname, 0, scene, False)
            playdub(filmname,renderfilename, 'scene')
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
    return dubrecord

#---------------Play & DUB--------------------

def playdub(filmname, filename, player_menu):
    global headphoneslevel, miclevel, plughw, channels, filmfolder, scene, soundrate, soundformat
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
    t = 0
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    playing = False
    pause = False
    trim = False
    videolag = 0
    remove_shots = []
    if video == True:
        if player_menu == 'dubbb':
            try:
                player = OMXPlayer(filename + '.mp4', args=['-n', '-1', '--fps', '25', '--layer', '3', '--no-osd', '--win', '0,15,800,475','--no-keys'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
            except:
                writemessage('Something wrong with omxplayer')
                time.sleep(0.5)
                return
        else:
            try:
                player = OMXPlayer(filename + '.mp4', args=['--adev', 'alsa:hw:'+str(plughw), '--fps', '25', '--layer', '3', '--no-osd', '--win', '0,15,800,475','--no-keys'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
            except:
                writemessage('Something wrong with omxplayer')
                time.sleep(0.5)
                return
            #player = OMXPlayer(filename + '.mp4', args=['--fps', '25', '--layer', '3', '--win', '0,70,800,410', '--no-osd', '--no-keys'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
        writemessage('Loading...')
        clipduration = player.duration()
    #sound
    #if player_menu != 'film':
    #    try:
    #        playerAudio = OMXPlayer(filename + '.wav', args=['--adev','alsa:hw:'+str(plughw)], dbus_name='org.mpris.MediaPlayer2.omxplayer2', pause=True)
    #        time.sleep(0.2)
    #    except:
    #        writemessage('something wrong with audio player')
    #        time.sleep(2)
    #        return
        #omxplayer hack to play really short videos.
    if clipduration < 4:
        logger.info("clip duration shorter than 4 sec")
        player.previous()
    if dub == True:
        p = 0
        while p < 3:
            writemessage('Dubbing in ' + str(3 - p) + 's')
            time.sleep(1)
            p+=1
    if video == True:
        player.play()
        #run_command('aplay -D plughw:0 ' + filename + '.wav &')
        #run_command('mplayer ' + filename + '.wav &')
    if player_menu == 'dub':
        run_command(gonzopifolder + '/alsa-utils-1.1.3/aplay/arecord -D plughw:'+str(plughw)+' -f '+soundformat+' -c '+str(channels)+' -r '+soundrate+' -vv /dev/shm/dub.wav &')
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
                menu = 'BACK', 'PLAY', 'REPLAY', 'TRIM'
                settings = '','','',''
            else:
                menu = 'BACK', 'PLAY', 'REPLAY'
                settings = '','',''
        elif player_menu == 'dub': 
            menu = 'BACK', 'REDUB', 'PHONES:', 'MIC:'
            settings = '', '', str(headphoneslevel), str(miclevel)
        else:
            menu = 'BACK', 'PAUSE', 'REPLAY', 'PHONES:'
            settings = '', '', '', str(headphoneslevel)
        if dub == True:
            header = 'Dubbing ' + str(round(t,1))
        else:
            header = 'Playing ' + str(round(t,1)) + ' of ' + str(clipduration) + ' s'
        writemenu(menu,settings,selected,header,showmenu)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if buttonpressed == True:
            flushbutton()
        if pressed == 'remove':
            if fastedit_shot in remove_shots:
                remove_shots.remove(fastedit_shot)
            else:
                remove_shots.append(fastedit_shot)
            time.sleep(0.2)
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
            elif menu[selected] == 'MIC:':
                if miclevel < 100:
                    miclevel = miclevel + 2
                    run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            else:
                try:
                    player.set_position(t+2)
                    #playerAudio.set_position(player.position())
                except:
                    print('couldnt set position of player')
        elif pressed == 'down':
            if menu[selected] == 'PHONES:':
                if headphoneslevel > 0:
                    headphoneslevel = headphoneslevel - 2
                    run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            elif menu[selected] == 'MIC:':
                if miclevel > 0:
                    miclevel = miclevel - 2
                    run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            else:
                if t > 1:
                    try:
                        player.set_position(t-2)
                        #playerAudio.set_position(player.position())
                    except:
                        print('couldnt set position of player')
        elif pressed == 'middle' or pressed == 'record':
            time.sleep(0.2)
            if menu[selected] == 'BACK' or player.playback_status() == "Stopped" or pressed == 'record':
                try:
                    if video == True:
                        #player.stop()
                        #playerAudio.stop()
                        player.quit()
                        #playerAudio.quit()
                    #os.system('pkill -9 aplay') 
                except:
                    #kill it if it dont stop
                    print('OMG! kill dbus-daemon')
                if dub == True:
                    os.system('pkill arecord')
                    time.sleep(0.2)
                os.system('pkill -9 omxplayer')
                #os.system('pkill -9 dbus-daemon')
                return remove_shots
            elif menu[selected] == 'REPLAY' or menu[selected] == 'REDUB':
                pause = False
                try:
                    os.system('pkill aplay')
                    if dub == True:
                        os.system('pkill arecord')
                    if video == True:
                        player.pause()
                        player.set_position(0)
                        #if player_menu != 'film':
                            #playerAudio.pause()
                            #playerAudio.set_position(0)
                    if dub == True:
                        p = 0
                        while p < 3:
                            writemessage('Dubbing in ' + str(3 - p) + 's')
                            time.sleep(1)
                            p+=1
                    player.play()
                    #if player_menu != 'film':
                    #    playerAudio.play()
                    #run_command('aplay -D plughw:0 ' + filename + '.wav &')
                    if dub == True:
                        run_command(gonzopifolder + '/alsa-utils-1.1.3/aplay/arecord -D plughw:'+str(plughw)+' -f '+soundformat+' -c '+str(channels)+' -r '+soundrate+' -vv /dev/shm/dub.wav &')
                except:
                    pass
                starttime = time.time()
            elif menu[selected] == 'PAUSE':
                player.pause()
                #try:
                #    playerAudio.pause()
                #except:
                #    pass
                pause = True
            elif menu[selected] == 'PLAY':
                player.play()
                #try:
                #    playerAudio.play()
                #except:
                #    pass
                pause = False
            elif menu[selected] == 'TRIM':
                selected = 1
                trim = True
            elif menu[selected] == 'CANCEL':
                selected = 1
                trim = False
            elif menu[selected] == 'FROM BEGINNING':
                trim = ['beginning', player.position()]
                player.quit()
                #playerAudio.quit()
                return trim
            elif menu[selected] == 'FROM END':
                trim = ['end', player.position()]
                player.quit()
                #playerAudio.quit()
                return trim
        time.sleep(0.02)
        if pause == False:
            try:
                t = player.position()
            except:
                os.system('pkill aplay') 
                if dub == True:
                    os.system('pkill arecord')
                return remove_shots
    player.quit()
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

#---------------Video Trim--------------------

def videotrim(filename, trim_filename, where, s):
    #theres two different ways of non-rerendering mp4 cut techniques that i know MP4Box and ffmpeg
    if where == 'beginning':
        logger.info('trimming clip from beginning')
        #run_command('ffmpeg -ss ' + str(s) + ' -i ' + filename + '.mp4 -c copy ' + trim_filename + '.mp4')
        run_command('MP4Box ' + filename + '.mp4 -splitx ' + str(s) + ':end -out ' + trim_filename + '.mp4')
        run_command('cp ' + filename + '.wav ' + trim_filename + '.wav')
        audiotrim(trim_filename, 'beginning','')
    if where == 'end':
        logger.info('trimming clip from end')
        #run_command('ffmpeg -to ' + str(s) + ' -i ' + filename + '.mp4 -c copy ' + trim_filename + '.mp4')
        run_command('MP4Box ' + filename + '.mp4 -splitx 0:' + str(s) + ' -out ' + trim_filename + '.mp4')
        run_command('cp ' + filename + '.wav ' + trim_filename + '.wav')
        audiotrim(trim_filename, 'end','')
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

#--------------Audio Trim--------------------
# make audio file same lenght as video file
def audiotrim(filename, where, dub):
    global channels, fps
    videofile=filename
    audiosync=0
    print("chaaaaaaaaaaaaaaaanel8: " +str(channels))
    writemessage('Audio syncing..')
    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
    videolenght = pipe.decode().strip()
    print('videolenght:'+str(videolenght))
    if dub:
        filename=dub[:-4]
    try:
        pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + filename + '.wav', shell=True)
        audiolenght = pipe.decode().strip()
    except:
        audiosilence('',filename)
        audiolenght=videolenght
    #if there is no audio lenght
    logger.info('audio is:' + audiolenght)
    if not audiolenght.strip():
        audiolenght = 0
    #separate seconds and milliseconds
    #videoms = int(videolenght) % 1000
    #audioms = int(audiolenght) % 1000
    #videos = int(videolenght) / 1000
    #audios = int(audiolenght) / 1000
    elif int(audiolenght) > int(videolenght):
        #calculate difference
        audiosync = int(audiolenght) - int(videolenght)
        newaudiolenght = int(audiolenght) - audiosync
        logger.info('Audiofile is: ' + str(audiosync) + 'ms longer')
        #trim from end or beginning and put a 0.01 in- and outfade
        if where == 'end':
            run_command('sox -V0 ' + filename + '.wav ' + filename + '_temp.wav trim 0 -' + str(int(audiosync)/1000))
        if where == 'beginning':
            logger.info('trimming from beginning at: '+str(int(audiosync)/1000))
            run_command('sox -V0 ' + filename + '.wav ' + filename + '_temp.wav trim ' + str(int(audiosync)/1000))
        run_command('sox -V0 -G ' + filename + '_temp.wav ' + filename + '.wav fade 0.01 0 0.01')
        os.remove(filename + '_temp.wav')
        #if int(audiosync) > 400:
        #    writemessage('WARNING!!! VIDEO FRAMES DROPPED!')
        #    vumetermessage('Consider changing to a faster microsd card.')
        #    time.sleep(10)
        delayerr = 'A' + str(audiosync)
        print(delayerr)
    elif int(audiolenght) < int(videolenght):
        audiosync = int(videolenght) - int(audiolenght)
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
        run_command('sox -V0 -r '+soundrate+' -c 2 '+filename+'.wav '+filename+'_temp.wav trim 0.0 pad 0 ' + str(int(audiosync)/1000))
        run_command('sox -V0 -G ' + filename + '_temp.wav ' + filename + '.wav fade 0.01 0 0.01')
        #add silence to end
        #run_command('sox -V0 /dev/shm/silence.wav ' + filename + '_temp.wav')
        #run_command('cp '+filename+'.wav '+filename+'_temp.wav')
        #run_command('sox -V0 -G ' + filename + '_temp.wav /dev/shm/silence.wav ' + filename + '.wav')
        os.remove(filename + '_temp.wav')
        #os.remove('/dev/shm/silence.wav')
        delayerr = 'V' + str(audiosync)
        print(delayerr)
    print('the results:')
    pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + filename + '.wav', shell=True)
    audiolenght = pipe.decode().strip()
    print('aftersyncvideo: '+str(videolenght) + ' audio:'+str(audiolenght))
    if int(audiolenght) != int(videolenght):
        vumetermessage('SYNCING FAILED!')
        time.sleep(10)
    #os.remove('/dev/shm/' + filename + '.wav')
    return float(audiosync)/1000, int(videolenght), int(audiolenght)
    #os.system('mv audiosynced.wav ' + filename + '.wav')
    #os.system('rm silence.wav')

#--------------Audiosilence--------------------
# make an empty audio file as long as a video file

def audiosilence(foldername,filename):
    global channels
    writemessage('Creating audiosilence..')
    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + foldername + filename + '.mp4', shell=True)
    videolenght = pipe.decode()
    logger.info('Video lenght is ' + videolenght)
    #separate seconds and milliseconds
    videoms = int(videolenght) % 1000
    videos = int(videolenght) / 1000
    logger.info('Videofile is: ' + str(videos) + 's ' + str(videoms))
    run_command('sox -V0 -n -r '+soundrate+' -c 2 /dev/shm/silence.wav trim 0.0 ' + str(videos))
    os.system('cp /dev/shm/silence.wav ' + foldername + filename + '.wav')
    os.system('rm /dev/shm/silence.wav')

#--------------Copy to USB-------------------

def copytousb(filmfolder):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    writemessage('Searching for usb storage device, middlebutton to cancel')
    films = getfilms(filmfolder)
    while True:
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        usbconnected = os.path.ismount('/media/usb0')
        if pressed == 'middle':
            writemessage('canceling..')
            time.sleep(2)
            break
        time.sleep(0.02)
        if usbconnected == True:
            #Copy new files to usb device
            try:
                os.makedirs('/media/usb0/gonzopifilms/')
            except:
                pass
            try:
                p = subprocess.check_output('stat -f -c %T /media/usb0', shell=True)
                filesystem = p.decode()
                print('filesystem info: ' + filesystem)
            except:
                writemessage('Oh-no! dont know your filesystem')
                waitforanykey()
                return
            for filmname in films:
                #check filmhash
                filmname = filmname[0]
                usbpath = '/media/usb0/gonzopifilms/'+filmname
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
                    run_command('rsync -avr -P ' + filmfolder + filmname + ' ' + usbpath)
                except:
                    writemessage('couldnt copy film ' + filmname)
                    waitforanykey()
                    return
            run_command('sync')
            run_command('pumount /media/usb0')
            writemessage('all files copied successfully!')
            waitforanykey()
            writemessage('You can safely unplug the usb device now')
            time.sleep(2)
            return

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
    while True:
        header = 'Where do you want to upload?'
        writemenu(menu,settings,selected,header,showmenu)
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

def startstream(camera, stream, plughw, channels):
    #youtube
    #youtube="rtmp://a.rtmp.youtube.com/live2/"
    #with open("/home/pi/.youtube-live") as fp:
    #    key = fp.readlines()
    #print('using key: ' + key[0])
    #stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar 44100 -vcodec copy -acodec libmp3lame -b:a 128k -ar 44100 -map 0:0 -map 1:0 -strict experimental -f flv ' + youtube + key[0]
    #
    #stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar 44100 -vcodec copy -acodec libmp3lame -b:a 128k -ar 44100 -map 0:0 -map 1:0 -strict experimental -f mpegts tcp://0.0.0.0:3333\?listen'
    #stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar '+soundrate+' -acodec mp2 -b:a 128k -ar '+soundrate+' -vcodec copy -map 0:0 -map 1:0 -g 0 -f mpegts udp://10.42.0.169:5002'
    stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar '+soundrate+' -acodec mp2 -b:a 128k -ar '+soundrate+' -vcodec copy -f mpegts udp://10.42.0.169:5002'
    try:
        stream = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE) 
        camera.start_recording(stream.stdin, splitter_port=2, format='h264', bitrate = 55555)
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

def buzz(buzzerlenght):
    buzzerdelay = 0.0001
    for _ in range(buzzerlenght):
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
    while True:
        with term.cbreak():
            val = term.inkey(timeout=0)
        if not val:
            event = ''
        elif val.is_sequence:
            event = val.name
        elif val:
            event = val
        if i2cbuttons == True:
            readbus = bus.read_byte_data(DEVICE,GPIOB)
            readbus2 = bus.read_byte_data(DEVICE,GPIOA)
        else:
            readbus = 255
            readbus2 = 247
        if readbus != 255 or readbus2 != 247 or event != '':
            time.sleep(0.05)
            vumetermessage(' ')
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
    global i2cbuttons, serverstate, nextstatus, process, que, gonzopictrl_ip, recording, onlysound, filmname, filmfolder, scene, shot, take, selected, camera, loadfilmsettings, selected, newfilmname
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
            elif "RETAKE:" in nextstatus:
                pressed=nextstatus
            elif "SCENE:" in nextstatus:
                pressed=nextstatus
            elif "SHOT:" in nextstatus:
                pressed=nextstatus
            elif "REMOVE:" in nextstatus:
                pressed=nextstatus
            elif "Q:" in nextstatus:
                pressed=nextstatus
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
        elif event == 'KEY_TAB' or readbus2 == 246:
            pressed = 'view'
        elif event == 'KEY_DELETE' or (readbus == 223 and readbus2 == 247):
            pressed = 'remove'
        elif event == 'KEY_BACKSPACE':
            pressed = 'remove'
        elif event == 'P' or (readbus2 == 245 and readbus == 191):
            pressed = 'peak'
        elif event == 'S' or (readbus2 == 245 and readbus == 223):
            pressed = 'screen'
        elif event == 'A' or (readbus2 == 245 and readbus == 127):
            pressed = 'showmenu'
        elif event == (readbus2 == 245 and readbus == 239):
            pressed = 'changemode'
        elif event == 'H' or (readbus2 == 245 and readbus == 247):
            pressed = 'showhelp'
        elif event == 'I' or (readbus2 == 245 and readbus == 253):
            pressed = 'insert'
        elif event == 'C' or (readbus2 == 244):
            pressed = 'copy'
        elif event == 'M' or (readbus2 == 245 and readbus == 254):
            pressed = 'move'
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
            keydelay = 0.02
    if time.time() - buttontime > 2 and buttonpressed == True:
        keydelay = 0.02
    if time.time() - buttontime > 4 and buttonpressed == True:
        keydelay = 0.01
    return pressed, buttonpressed, buttontime, holdbutton, event, keydelay

def startinterface():
    call(['./startinterface.sh &'], shell = True)

def stopinterface(camera):
    try:
        camera.stop_preview()
        camera.close()
    except:
        print('no camera to close')
    os.system('pkill arecord')
    os.system('pkill startinterface')
    os.system('pkill tarinagui')
    #run_command('sudo systemctl stop apache2')
    return camera

def startcamera(lens, fps):
    global camera_model, fps_selection, fps_selected, cammode
    camera = picamera.PiCamera()
    if cammode == 'film':
        reso=(1920,1080)
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
        table = read_table('lenses/' + lens)
        camera.lens_shading_table = table
        camera.framerate = 24.999
    elif camera_model == 'ov5647':
        table = read_table('lenses/' + lens)
        camera.lens_shading_table = table
        # Different versions of ov5647 with different clock speeds, need to make a config file
        # if there's more frames then the video will be longer when converting it to 25 fps,
        # I try to get it as perfect as possible with trial and error.
        # ov5647 Rev C
        if camera_revision == 'rev.C':
            camera.framerate = 26.03
        # ov5647 Rev D"
        if camera_revision == 'rev.D':
            camera.framerate = 23.15
    elif camera_model == 'imx477':
        fps_selection=[5,15,24.985,35,49]
        fps=fps_selection[fps_selected]
        camera.framerate = fps 
    else:
        camera.framerate = fps
    camera.crop = (0, 0, 1.0, 1.0)
    #stabilization does not work in firmware
    #camera.video_stabilization = True
    camera.led = False
    #lens_shading_table = np.zeros(camera._lens_shading_table_shape(), dtype=np.uint8) + 32
    #camera.lens_shading_table = lens_shading_table
    camera.start_preview()
    camera.awb_mode = 'auto'
    time.sleep(1)
    return camera

def gonzopiserver(state):
    #Gonzopi server
    if state == True:
        #Try to run apache
        try:
            run_command('sudo systemctl start apache2')
            return 'on'
        except:
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
        os.system('pkill gonzopigui')
        print('Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1])
