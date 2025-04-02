import picamerax as picamera
import subprocess
import time

quality = 20
bitrate = 8888888
profilelevel='4.2'

# FFmpeg command to take H.264 input from stdin and output to MP4
ffmpeg_cmd = [
    'ffmpeg',
    '-i', 'pipe:0',           # Input from stdin (raw H.264 from PiCamera)
    '-c:v', 'copy',      # Use hardware encoder
    '-b:v', str(bitrate),
    '-level:v', '4.2',
    '-g', '1',
    '-f', 'mp4',             # Output format
    'output.mp4',            # Output file
    '-loglevel','debug',
    '-y'                     # Overwrite output file if it exists
]


#'-c:v h264_omx -profile:v high -level:v 4.2 -preset slow -bsf:v h264_metadata=level=4.2 -g 1 -b:v '+str(bitrate)+' -c:a copy '
# Start FFmpeg process
process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

# Initialize PiCamera
with picamera.PiCamera() as camera:
    camera.resolution = (1920, 1080)  # High Quality Camera resolution
    camera.framerate = 24.97
    camera.start_preview()
    # Start recording and pipe to FFmpeg
    print("Starting recording...")
    camera.start_recording(process.stdin, format='h264', bitrate = 8888888, level=profilelevel, quality=quality, intra_period=1)
    camera.wait_recording(10)  # Record for 10 seconds
    camera.stop_recording()

# Close the FFmpeg process
process.stdin.close()
process.wait()
print("Recording complete!")
