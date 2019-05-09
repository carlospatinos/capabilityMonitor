#!/bin/bash
image=$1
if [[ ! ("$#" == 1) ]]; then
    image="ha-testing-nodejs-mongo" 
    echo "Using default image: $image. Please provide specific image id as first parameter if you want to use it." 
fi

docker run --net=host -p 80:5000 -p 8080:5001 --name cliScripts -v /home/carlospatinos/Development/docker/haTesting/files:/opt/scripts  \
       -v /tmp/.X11-unix:/tmp/.X11-unix -t -i -e DISPLAY=$DISPLAY $image
