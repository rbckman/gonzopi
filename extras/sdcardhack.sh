#!/bin/bash

echo 3 >/proc/sys/vm/dirty_background_ratio
echo 50 >/proc/sys/vm/dirty_ratio
echo 300 >/proc/sys/vm/dirty_writeback_centisecs
echo 300 >/proc/sys/vm/dirty_expire_centisecs
