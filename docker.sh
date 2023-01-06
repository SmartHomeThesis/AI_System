#!/bin/bash
#arecord -f S16_LE -c 2 -d 10 -r 16000 --device="hw:0,7" /tmp/test-mic.wav
# aplay /tmp/test-mic.wav
xhost + local:
docker run  -it  --privileged -e DISPLAY=$DISPLAY \
           -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
           --device /dev/video0:/dev/video0 \
           --device /dev \
           -v /dev/shm:/dev/shm \
            -v /etc/machine-id:/etc/machine-id \
            -v /run/user/$uid/pulse:/run/user/$uid/pulse \
            -v /var/lib/dbus:/var/lib/dbus \
            -v ~/.pulse:/home/$dockerUsername/.pulse \
            -p 4713:4713 -p 5900:5900 \
           --rm \
           -v /home/pop_os_hi/Documents/HK221/Thesis/Latest-Project-Smart-Hone/Smart-Home:/root/face_recognition \
           -v /tmp:/tmp \
           smart-home:0.1 \
           /bin/bash