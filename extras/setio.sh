sudo echo none | sudo tee /sys/block/sda/queue/scheduler
sudo echo 20 | sudo tee /proc/sys/vm/dirty_background_ratio
sudo echo 40 | sudo tee /proc/sys/vm/dirty_ratio
