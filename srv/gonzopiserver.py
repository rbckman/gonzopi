#!/usr/bin/env python3

import web
import os
import socket
import ifaddr
import sys
import time
import random
import hashlib
import configparser

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

#--------------USB filmfolder-------------------

def usbfilmfolder():
    usbmount = 0
    while True:
        usbconnected = os.path.ismount('/media/usb'+str(usbmount))
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
                print('Oh-no! dont know your filesystem')
            filmfolder = '/media/usb'+str(usbmount)+'/gonzopifilms/'
            return filmfolder
        else:
            usbmount = usbmount + 1
        if usbmount > 20:
            break

home = os.path.expanduser('~')
#configfile = home + '/.gonzopi/config.ini'
#configdir = os.path.dirname(configfile)
#config = configparser.ConfigParser()
#if config.read(configfile):
#    filmfolder = config['USER']['filmfolder']+'/'
filmfolder = '/home/pi/gonzopifilms/'

os.system("unlink static/*")
#CHECK IF FILMING TO USB STORAGE
filmfolderusb=usbfilmfolder()
if filmfolderusb:
    filmfolder=filmfolderusb
    # Link video directory to static dir
    os.system("ln -s -t static/ " + filmfolder)
    filmfolder='static/gonzopifilms/'
else:
    os.system("ln -s -t static/ " + filmfolder)
    filmfolder='static/gonzopifilms/'
    #fix filmfolder root to Videos/gonzopifilms

basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(basedir)

films = []

#NETWORKS

networks=[]
adapters = ifaddr.get_adapters()
for adapter in adapters:
    print("IPs of network adapter " + adapter.nice_name)
    for ip in adapter.ips:
        if '::' not in ip.ip[0] and '127.0.0.1' != ip.ip:
            print(ip.ip)
            networks.append(ip.ip)
network=networks[0]

urls = (
    '/?', 'index',
    '/f/(.*)?', 'films'
)

app = web.application(urls, globals())
render = web.template.render('templates/', base="base")
web.config.debug=False
os.system('rm '+basedir+'/sessions/*')
store = web.session.DiskStore(basedir + '/sessions/')
session = web.session.Session(app,store,initializer={'login': 0, 'user': '', 'backurl': '', 'bildsida': 0, 'cameras': [], 'reload': 0, 'randhash':''})

port=55555
ip='0.0.0.0'
cameras=[]
recording = False

session.randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()

##---------------Connection----------------------------------------------

def pingtocamera(host, port, data):
    print("Sending to "+host+" on port "+str(port)+" DATA:"+data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.01)
    try:
        while True:
            s.connect((host, port))
            s.send(str.encode(data))
            if host not in cameras and host not in networks:
                session.cameras.append(host)
                print("Found camera! "+host)
            print("Sent to server..")
            break
    except:
        ('did not connect')
    s.close()

def sendtocamera(host, port, data):
    print("Sending to "+host+" on port "+str(port)+" DATA:"+data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        while True:
            s.connect((host, port))
            s.send(str.encode(data))
            print("Sent to server..")
            break
    except:
        ('did not connect')
    s.close()


def getfilms(filmfolder):
    #get a list of films, in order of settings.p file last modified
    films_sorted = []
    films = next(os.walk(filmfolder))[1]
    for i in films:
        if os.path.isfile(filmfolder + i + '/settings.p') == True:
            lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
            films_sorted.append((i,lastupdate))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[1], reverse=True)
    print(films_sorted)
    return films_sorted

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
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
    except:
        allfiles = []
        return takes
    for a in allfiles:
        if '.mp4' in a or '.h264' in a:
            takes = takes + 1
    return takes

def checkpicture(thumbdir,scene,shot,take):
    if os.path.isfile(thumbdir) == False:
        return "/"+filmfolder+name+"/scene"+str(scene).zfill(3)+"/shot"+str(shot).zfill(3)+"/picture"+str(take).zfill(3)+".jpeg"
    else:
        return ''

def checkvideo(video,filmfolder,film,scene,shot,take):
    print(basedir+video+'fuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuck')
    if os.path.islink(basedir+video) == False:
        p = "/"+filmfolder+film+"/scene"+str(scene).zfill(3)+"/shot"+str(shot).zfill(3)+"/picture"+str(take).zfill(3)+".jpeg"
        if os.path.isfile(basedir+p) == False:
            return 'render'
        else:
            return p
    else:
        return 'video'

class index:
    def GET(self):
        global recording
        films = getfilms(filmfolder)
        renderedfilms = []
        unrenderedfilms = []
        allfilms = []
        for f in films:
            if os.path.isfile(filmfolder + f[0] + '/' + f[0] + '.mp4') == True:
                renderedfilms.append(f[0])
                allfilms.append(f[0])
            else:
                unrenderedfilms.append(f[0])
                allfilms.append(f[0])
        i=web.input(func=None,selected=None)
        if i.selected != None:
            sendtocamera(ip,port,'SELECTED:'+i.selected)
        if i.func == 'search':
            session.cameras=[]
            # ping ip every 10 sec while not recording to connect cameras
            pingip=0
            while pingip < 255 :
                pingip+=1
                pingtocamera(network[:-3]+str(pingip),port,'PING')
        elif i.func == 'record':
            sendtocamera(ip,port,'REC')
        elif i.func == 'retake':
            print('retake')
        elif i.func == 'up':
            sendtocamera(ip,port,'UP')
        elif i.func == 'down':
            sendtocamera(ip,port,'DOWN')
        elif i.func == 'left':
            sendtocamera(ip,port,'LEFT')
        elif i.func == 'right':
            sendtocamera(ip,port,'RIGHT')
        elif i.func == 'view':
            sendtocamera(ip,port,'VIEW')
        elif i.func == 'middle':
            sendtocamera(ip,port,'MIDDLE')
        elif i.func == 'delete':
            sendtocamera(ip,port,'DELETE')
        elif i.func == 'picture':
            sendtocamera(ip,port,'PICTURE')
            session.randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            session.reload = 1
        interface=open('/dev/shm/interface','r')
        vumeter=open('/dev/shm/vumeter','r')
        menu=interface.readlines()
        vumetermessage=vumeter.readlines()[0].rstrip('\n')
        try:
            selected=int(menu[0])
        except:
            selected=0
        try:
            name=menu[3].split(':')[1]
            name=name.rstrip('\n')
        except:
            name=''
        try:
            scene=menu[4].split(':')[1].split('/')[0]
        except:
            scene=1
        try:
            shot=menu[5].split(':')[1].split('/')[0]
        except:
            shot=1
        try:
            take=menu[6].split(':')[1].split('/')[0]
        except:
            take=1
            session.reload = 0
        if i.func == 'retake': 
            print(i.func)
            if recording == False:
                sendtocamera(ip,port,'RETAKE:'+shot)
                recording = True
            else:
                sendtocamera(ip,port,'STOPRETAKE')
                recording = False
        if i.func != None:
            time.sleep(1)
            session.reload = 1
            raise web.seeother('/')
        thumb="/"+filmfolder+name+"/scene"+str(scene).zfill(3)+"/shot"+str(shot).zfill(3)+"/picture"+str(take).zfill(3)+".jpeg"
        print(thumb)
        if os.path.isfile(basedir+thumb) == False:
            print(basedir+thumb)
            thumb=''
        return render.index(allfilms, session.cameras, menu, selected,name,scene,shot,take,str,session.randhash,thumb,vumetermessage,i.func,filmfolder)

class films:
    def GET(self, film):
        shots = 0
        takes = 0
        gonzopifilms = getfilms(filmfolder)
        renderedfilms = []
        unrenderedfilms = []
        allfilms = []
        for f in gonzopifilms:
            if os.path.isfile(filmfolder + f[0] + '/' + f[0] + '.mp4') == True:
                renderedfilms.append(f[0])
                allfilms.append(f[0])
            else:
                unrenderedfilms.append(f[0])
                allfilms.append(f[0])
        i = web.input(page=None, scene=None, shot=None, take=None, film=None)
        if i.scene != None:
            shots = countshots(film, filmfolder, i.scene)
            takes = counttakes(film, filmfolder, i.scene, i.shot)
        if i.scene != None and i.shot != None:
            shots = countshots(film, filmfolder, i.scene)
        scenes = countscenes(filmfolder, film)
        return render.filmpage(allfilms, film, scenes, str, filmfolder, counttakes, countshots, shots, i.scene, takes, i.shot, i.take, checkvideo)

application = app.wsgifunc()

