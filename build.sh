#!/bin/sh

sudo docker build --no-cache -t streaminsight-api -f Dockerfile .
sudo docker run -p 8002:8002 streaminsight-api