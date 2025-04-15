echo none | sudo tee /sys/block/sda/queue/scheduler
echo 20 | sudo tee /proc/sys/vm/dirty_background_ratio
echo 40 | sudo tee /proc/sys/vm/dirty_ratio
