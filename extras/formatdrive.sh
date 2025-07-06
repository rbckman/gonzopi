sudo mkfs.ext4 -O ^has_journal /dev/sda1
echo "sudo mount -o  noatime,nodiratime,async /dev/sda1 /media/usb0"
