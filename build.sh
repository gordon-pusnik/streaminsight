#!/bin/sh

sudo docker build --no-cache -t streaminsight-api -f Dockerfile .
sudo docker run -p 9000:9000 streaminsight-api