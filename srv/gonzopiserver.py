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
import json
import datetime
from PIL import Image
from pymediainfo import MediaInfo

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

urls = (
    '/','intro',   
    '/c/?', 'index',
    '/f/(.*)?', 'films',
    '/t/(.*)?', 'tree',
    '/e/(.*)?', 'edit',
    '/save-order/(.*)?', 'logorder',
    '/p/(.*)?', 'player',
    '/api','api'
)

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
menuold = []
vumeterold = ''
#configfile = home + '/.gonzopi/config.ini'
#configdir = os.path.dirname(configfile)
#config = configparser.ConfigParser()
#if config.read(configfile):
#    filmfolder = config['USER']['filmfolder']+'/'
filmfolder = '/home/pi/gonzopifilms/'
real_filmfolder=filmfolder

os.system("unlink static/*")
#CHECK IF FILMING TO USB STORAGE
filmfolderusb=usbfilmfolder()
if filmfolderusb:
    filmfolder=filmfolderusb
    real_filmfolder=filmfolder
    # Link video directory to static dir
    os.system("ln -s -t static/ " + filmfolder)
    filmfolder='static/gonzopifilms/'
    filmdb = filmfolder+'.videos/gonzopi.db'
    db = web.database(dbn='sqlite', db=filmdb)
else:
    os.system("ln -s -t static/ " + filmfolder)
    filmfolder='static/gonzopifilms/'
    #fix filmfolder root to Videos/gonzopifilms
    filmdb = filmfolder+'.videos/gonzopi.db'
    db = web.database(dbn='sqlite', db=filmdb)

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

app = web.application(urls, globals())
render = web.template.render('templates/', base="base")
render2 = web.template.render('templates/', base="base2")
web.config.debug=False
os.system('rm '+basedir+'/sessions/*')
store = web.session.DiskStore(basedir + '/sessions/')
session = web.session.Session(app,store,initializer={'login': 0, 'user': '', 'backurl': '', 'bildsida': 0, 'cameras': [], 'reload': 0, 'randhash':'', 'menu':[]})

port=55555
ip='0.0.0.0'
cameras=[]
recording = False

session.randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()

##---------------Connection----------------------------------------------

def pingtocamera(host, port, data):
    #print("Sending to "+host+" on port "+str(port)+" DATA:"+data)
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
    #print(filmfolder)
    films = next(os.walk(filmfolder))[1]
    for i in films:
        if os.path.isfile(filmfolder + i + '/settings.p') == True:
            lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
            films_sorted.append((i,lastupdate))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[1], reverse=True)
    #print(films_sorted)
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

def if_exist(dir):
    print(basedir+dir)
    if os.path.isfile(basedir+dir) == False:
        print('thumb not exist')
        return False
    else:
        print('thumb is')
        return True

def countsize(filename):
    size = 0
    if type(filename) is str:
        size = os.stat(filename).st_size
    else:
        return 0
    return size/1024

def checkvideo(video,filmfolder,film,scene,shot,take):
    if take==None:
        take=1
    #print(basedir+video)
    p = "/"+filmfolder+film+"/scene"+str(scene).zfill(3)+"/shot"+str(shot).zfill(3)+ "/picture"+str(take).zfill(3)+".jpeg"
    #print(p)
    v = ''
    if video != '':
        try:
            if os.stat(basedir+video).st_size == 0:
                v = ''
            else:
                v='video'
        except:
            v = ''
    if os.path.isfile(basedir+p) == True:
        return p, v
    return '', v

def get_video_length(filepath):
    video_origins = (os.path.realpath(filepath))
    try:
        video_db=db.select('videos', where='filename="'+video_origins+'"')[0]
        return str(datetime.timedelta(seconds=round(video_db.videolength)))
    except:
        pass
    return
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
            db.update('videos', where='filename="'+video_origins+'"', videolength=duration_ms/1000, audiolength=duration_ms/1000)
            return str(datetime.timedelta(seconds=round(duration_ms/1000)))
            #return int(duration_ms)
    return None  # No video track found

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

class intro:
    def GET(self):
        return render.intro()

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
            sendtocamera(ip,port,'RECORD')
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
        elif i.func == 'camera0':
            sendtocamera(ip,port,'CAMERA:0')
        elif i.func == 'camera1':
            sendtocamera(ip,port,'CAMERA:1')
        elif i.func == 'camera2':
            sendtocamera(ip,port,'CAMERA:2')
        elif i.func == 'camera3':
            sendtocamera(ip,port,'CAMERA:3')
        elif i.func == 'camera4':
            sendtocamera(ip,port,'CAMERA:4')
        elif i.func == 'camera5':
            sendtocamera(ip,port,'CAMERA:5')
        elif i.func == 'camera6':
            sendtocamera(ip,port,'CAMERA:6')
        elif i.func == 'camera7':
            sendtocamera(ip,port,'CAMERA:7')
        elif i.func == 'camera8':
            sendtocamera(ip,port,'CAMERA:8')
        elif i.func == 'move':
            sendtocamera(ip,port,'move')
        elif i.func == 'copy':
            sendtocamera(ip,port,'copy')
        elif i.func == 'paste':
            sendtocamera(ip,port,'paste')
        interface=open('/dev/shm/interface','r')
        vumeter=open('/dev/shm/vumeter','r')
        menu=interface.readlines()
        vumetermessage=vumeter.readlines()[0].rstrip('\n')
        try:
            selected=int(menu[0])
        except:
            selected=0
        try:
            name=menu[4].split(':')[1]
            name=name.rstrip('\n')
        except:
            name=''
        try:
            scene=menu[5].split(':')[1].split('/')[0]
        except:
            scene=1
        try:
            shot=menu[6].split(':')[1].split('/')[0]
        except:
            shot=1
        try:
            take=menu[7].split(':')[1].split('/')[0]
        except:
            take=1
            session.reload = 0
        if i.func == 'retake': 
            print(i.func)
            if recording == False:
                #sendtocamera(ip,port,'RETAKE:'+shot)
                sendtocamera(ip,port,'RETAKE')
                recording = True
            else:
                sendtocamera(ip,port,'STOPRETAKE')
                recording = False
        if i.func != None:
            time.sleep(1)
            session.reload = 1
            raise web.seeother('/c/')
        thumb="/"+filmfolder+name+"/scene"+str(scene).zfill(3)+"/shot"+str(shot).zfill(3)+"/picture"+str(take).zfill(3)+".jpeg"
        #print(thumb)
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
        i = web.input(page=None, scene=None, shot=None, take=None, film=None, randhash=None)
        if i.scene != None:
            shots = countshots(film, filmfolder, i.scene)
            takes = counttakes(film, filmfolder, i.scene, i.shot)
        if i.scene != None and i.shot != None:
            shots = countshots(film, filmfolder, i.scene)
        if i.randhash == None:
            randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
        scenes = countscenes(filmfolder, film)
        return render.filmpage(allfilms, film, scenes, str, filmfolder, counttakes, countshots, shots, i.scene, takes, i.shot, i.take, checkvideo, randhash)

class tree:
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
        i = web.input(page=None, scene=None, shot=None, take=None, film=None, randhash=None)
        if i.scene != None:
            shots = countshots(film, filmfolder, i.scene)
            takes = counttakes(film, filmfolder, i.scene, i.shot)
        if i.scene != None and i.shot != None:
            shots = countshots(film, filmfolder, i.scene)
        if i.randhash == None:
            randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
        scenes = countscenes(filmfolder, film)
        return render2.tree(allfilms, film, scenes, str, filmfolder, counttakes, countshots, countscenes, shots, i.scene, takes, i.shot, i.take, checkvideo, randhash, if_exist)

def createthumb(picture, thumbnail):
    sendtocamera(ip,port,'THUMB|'+picture+':'+thumbnail)

class edit:
    def GET(self, film):
        shots = 0
        takes = 0
        gonzopifilms = getfilms(filmfolder)
        renderedfilms = []
        unrenderedfilms = []
        allfilms = []
        filmdb = filmfolder+'.videos/gonzopi.db'
        db = web.database(dbn='sqlite', db=filmdb)
        for f in gonzopifilms:
            if os.path.isfile(filmfolder + f[0] + '/' + f[0] + '.mp4') == True:
                renderedfilms.append(f[0])
                allfilms.append(f[0])
            else:
                unrenderedfilms.append(f[0])
                allfilms.append(f[0])
        i = web.input(page=None, scene=None, shot=None, take=None, film=None, randhash=None)
        if i.scene != None:
            shots = countshots(film, filmfolder, i.scene)
            takes = counttakes(film, filmfolder, i.scene, i.shot)
        if i.scene != None and i.shot != None:
            shots = countshots(film, filmfolder, i.scene)
        if i.randhash == None:
            randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
        scenes = countscenes(filmfolder, film)
        return render2.edit(allfilms, film, scenes, str, filmfolder, counttakes, countshots, countscenes, shots, i.scene, takes, i.shot, i.take, checkvideo, randhash, if_exist, createthumb,basedir,time,get_video_length, db, real_filmfolder)

class logorder:
    def POST(self, film):
        try:
            data = web.data()
            order = json.loads(data)

            if not order:
                web.header('Content-Type', 'application/json')
                return json.dumps({"error": "No data provided"})

            # Write alt values to file without index
            with open(basedir+'/static/order.edit', 'w') as f:
                for alt in order:
                    f.write(f"{alt}\n")
                    print(alt)

            web.header('Content-Type', 'application/json')
            return json.dumps({"message": "Order saved successfully"})
        except json.JSONDecodeError:
            web.header('Content-Type', 'application/json')
            return json.dumps({"error": "Invalid JSON data"})
        except Exception as e:
            web.header('Content-Type', 'application/json')
            return json.dumps({"error": f"Server error: {str(e)}"})


class player:
    def GET(self, film):
        i=web.input(scene=None,shot=None,take=None)
        randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
        return render.player(real_filmfolder,filmfolder,film,i.scene,i.shot,i.take,str,randhash,has_audio_track)

class api:
    def GET(self):
        i=web.input(func=None,selected=None, scene=None, shot=None, film=None)
        interface=open('/dev/shm/interface','r')
        menu=interface.readlines()
        vumeter=open('/dev/shm/vumeter','r')
        vumetermessage=vumeter.readlines()[0].rstrip('\n')
        #print(menu)
        menudone=''
        p=0
        film=None
        selectfilm=False
        if menu != '':
            scene=1
            shot=1
            take=1
            for i in menu:
                if p == 0:
                    selected=int(i)+3
                if p > 1:
                    if selected == p:
                        #menudone=menudone+'<b> '+i.rstrip('\n')+' </b> | '
                        menudone=menudone+'<ka style="text-decoration:none; font-size:20px;" color:fff;" href="">'+i+'</ka>'
                    else:
                        #menudone=menudone+i.rstrip('\n')+' | '
                        menudone=menudone+'<a style="text-decoration:none; font-size:20px;" href="?selected='+str(p-3)+'"> '+i+' </a>'
                    #if p == 7:
                    #    menudone=menudone+'<br>'
                    #if p == 13:
                    #    menudone=menudone+'<br>'
                    #if p == 21:
                    #    menudone=menudone+'<br>'
                    #if p == 30:
                    #    menudone=menudone+'<br>'
                if p == 2 and i.rstrip('\n') == 'Up and down to select and load film':
                    selectfilm=True
                if p == 3 and selectfilm==True:
                    try:
                        film=i.split(':')[1].rstrip('\n')
                    except:
                        film=None
                if p == 4 and selectfilm == False:
                    try:
                        film=i.split(':')[1].rstrip('\n')
                    except:
                        film=None
                if p == 5 and film != None:
                    try:
                        scene=int(i.split(':')[1].split('/')[0])
                    except:
                        scene=1
                if p == 6 and film != None:
                    try:
                        shot=int(i.split(':')[1].split('/')[0].rstrip('*'))
                    except:
                        shot=1
                if p == 7 and film != None:
                    try:
                        take=int(i.split(':')[1].split('/')[0])
                    except:
                        take=1
                if p > 0 and selected == 423:
                    menudone=menudone+'<ka style="text-decoration:none; font-size:20px;" color:fff;" href="">'+i+'</ka>'
                #if p > 2 and film == None:
                    #menudone=menudone+'<ka style="text-decoration:none; font-size:20px;" color:fff;" href="">'+i+'</ka>'
                p = p + 1
        thumb = ''
        video = ''
        if film != None:
            if selected == 0:
                video = '/p/'+film
                menudone+=menudone+'video'
            if selected == 4:
                video = '/p/'+film
            elif selected == 5:
                video = '/p/'+film+'?scene=' + str(scene)
            elif selected == 6:
                video = '/p/'+film+'?scene='+str(scene)+'&shot='+str(shot)+'&take='+str(take)
            elif selected == 7:
                video = '/p/'+film+'?scene='+str(scene)+'&shot='+str(shot)+'&take='+str(take)
            else:
                video = '/p/'+film+'?scene='+str(scene)+'&shot='+str(shot)+'&take='+str(take)
            thumb = '/'+filmfolder + film + "/scene" + str(scene).zfill(3) + "/shot" + str(shot).zfill(3) + "/take" + str(take).zfill(3) + ".jpeg" 
        if os.path.isfile(basedir+thumb) == True:
            randhashimg = '?'+hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            writemenu=menudone+'<br><br>'+vumetermessage+'<br><a href="'+video+'"><img src="'+thumb+randhashimg+'"></a>'
            #writemenu=menudone+render.player(filmfolder,film,scene,shot,take,str)
        else:
            writemenu=menudone+'<br><br>'+vumetermessage+'<br>'
        isActive=True
        try:
            with open('/dev/shm/videos_selected','r') as f:
                selected_videos=[line.rstrip('\n') for line in f.readlines()]
        except:
            selected_videos=[]
        return json.dumps({"film": film, "scene":scene,"shot":shot,"isActive":isActive, "selected":selected_videos})

    def POST(self):
        global menuold, vumeterold
        i=web.input(func=None,selected=None, scene=None, shot=None, film=None)
        if i.func == 'record':
            sendtocamera(ip,port,'RECORD')
        elif i.func == 'retake':
            sendtocamera(ip,port,'RETAKE')
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
        elif i.func == 'camera0':
            sendtocamera(ip,port,'CAMERA:0')
        elif i.func == 'camera1':
            sendtocamera(ip,port,'CAMERA:1')
        elif i.func == 'camera2':
            sendtocamera(ip,port,'CAMERA:2')
        elif i.func == 'camera3':
            sendtocamera(ip,port,'CAMERA:3')
        elif i.func == 'camera4':
            sendtocamera(ip,port,'CAMERA:4')
        elif i.func == 'camera5':
            sendtocamera(ip,port,'CAMERA:5')
        elif i.func == 'camera6':
            sendtocamera(ip,port,'CAMERA:6')
        elif i.func == 'camera7':
            sendtocamera(ip,port,'CAMERA:7')
        elif i.func == 'camera8':
            sendtocamera(ip,port,'CAMERA:8')
        elif i.func == 'move':
            sendtocamera(ip,port,'move')
        elif i.func == 'copy':
            sendtocamera(ip,port,'copy')
        elif i.func == 'paste':
            sendtocamera(ip,port,'paste')
        elif i.scene!=None and i.shot!=None and i.film != None:
            sendtocamera(ip,port,'SHOTSCENES:'+str(i.scene)+'|'+str(i.shot))
            time.sleep(0.2)
            sendtocamera(ip,port,'SELECTED:3')
        interface=open('/dev/shm/interface','r')
        menu=interface.readlines()
        vumeter=open('/dev/shm/vumeter','r')
        vumetermessage=vumeter.readlines()[0].rstrip('\n')
        if menu != menuold or vumetermessage != vumeterold:
            menuold=menu
            vumeterold=vumetermessage
            #print(menu)
            menudone=''
            p=0
            film=None
            selectfilm=False
            if menu != '':
                scene=1
                shot=1
                take=1
                for i in menu:
                    if p == 0:
                        selected=int(i)+3
                    if p > 1:
                        if selected == p:
                            #menudone=menudone+'<b> '+i.rstrip('\n')+' </b> | '
                            menudone=menudone+'<ka style="text-decoration:none; font-size:20px;" color:fff;" href="">'+i+'</ka>'
                        else:
                            #menudone=menudone+i.rstrip('\n')+' | '
                            menudone=menudone+'<a style="text-decoration:none; font-size:20px;" href="?selected='+str(p-3)+'"> '+i+' </a>'
                        #if p == 7:
                        #    menudone=menudone+'<br>'
                        #if p == 13:
                        #    menudone=menudone+'<br>'
                        #if p == 21:
                        #    menudone=menudone+'<br>'
                        #if p == 30:
                        #    menudone=menudone+'<br>'
                    if p == 2 and i.rstrip('\n') == 'Up and down to select and load film':
                        selectfilm=True
                    if p == 3 and selectfilm==True:
                        try:
                            film=i.split(':')[1].rstrip('\n')
                        except:
                            film=None
                    if p == 4 and selectfilm == False:
                        try:
                            film=i.split(':')[1].rstrip('\n')
                        except:
                            film=None
                    if p == 5 and film != None:
                        try:
                            scene=int(i.split(':')[1].split('/')[0])
                        except:
                            scene=1
                    if p == 6 and film != None:
                        try:
                            shot=int(i.split(':')[1].split('/')[0])
                        except:
                            shot=1
                    if p == 7 and film != None:
                        try:
                            take=int(i.split(':')[1].split('/')[0])
                        except:
                            take=1
                    if p > 0 and selected == 423:
                        menudone=menudone+'<ka style="text-decoration:none; font-size:20px;" color:fff;" href="">'+i+'</ka>'
                    #if p > 2 and film == None:
                        #menudone=menudone+'<ka style="text-decoration:none; font-size:20px;" color:fff;" href="">'+i+'</ka>'
                    p = p + 1
            thumb = ''
            video = ''
            if film != None:
                if selected == 0:
                    video = '/p/'+film
                    menudone+=menudone+'video'
                if selected == 4:
                    video = '/p/'+film
                elif selected == 5:
                    video = '/p/'+film+'?scene=' + str(scene)
                elif selected == 6:
                    video = '/p/'+film+'?scene='+str(scene)+'&shot='+str(shot)+'&take='+str(take)
                elif selected == 7:
                    video = '/p/'+film+'?scene='+str(scene)+'&shot='+str(shot)+'&take='+str(take)
                else:
                    video = '/p/'+film+'?scene='+str(scene)+'&shot='+str(shot)+'&take='+str(take)
                thumb = '/'+filmfolder + film + "/scene" + str(scene).zfill(3) + "/shot" + str(shot).zfill(3) + "/take" + str(take).zfill(3) + ".jpeg" 
            if os.path.isfile(basedir+thumb) == True:
                randhashimg = '?'+hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                writemenu=menudone+'<br><br>'+vumetermessage+'<br><a href="'+video+'"><img src="'+thumb+randhashimg+'"></a>'
                #writemenu=menudone+render.player(filmfolder,film,scene,shot,take,str)
            else:
                writemenu=menudone+'<br><br>'+vumetermessage+'<br>'
            f = open(basedir+'/static/menu.html', 'w')
            f.write(writemenu)
            f.close()

application = app.wsgifunc()

