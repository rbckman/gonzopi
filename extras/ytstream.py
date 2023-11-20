#!/usr/bin/env python3 
import subprocess 
import picamerax
import time 
YOUTUBE="rtmp://a.rtmp.youtube.com/live2/" 
KEY='j1cs-7hac-ygrj-5gaq-3m5b' 
stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac 1 -i hw:0 -vcodec copy -acodec libmp3lame -ar 44100 -map 0:0 -map 1:0 -strict experimental -f flv ' + YOUTUBE + KEY 
stream = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE) 
camera = picamerax.PiCamera(resolution=(640, 480), framerate=25) 
try: 
  now = time.strftime("%Y-%m-%d-%H:%M:%S") 
  camera.framerate = 25 
  camera.vflip = True 
  camera.hflip = True 
  camera.start_recording(stream.stdin, format='h264', bitrate = 2000000) 
  while True: 
     camera.wait_recording(1) 
except KeyboardInterrupt: 
     camera.stop_recording() 
finally: 
  camera.close() 
  stream.stdin.close() 
  stream.wait() 
  print("Camera safely shut down") 
  print("Good bye") 
