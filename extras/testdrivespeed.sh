
#test latency!
sudo dd if=/dev/zero of=/media/usb0/test bs=1M count=100 oflag=dsync

echo "good speed should be at < 0.5 s for 100 MB"

#test write speed
sudo dd if=/dev/zero of=/media/usb0/test bs=4M count=100 status=progress

echo "better speed better quality"
