#!/bin/bash
rm mojo.sqlite3
rm media/findings/*.png
rm media/improvements/*.png
rm media/strengths/*.png
rm -rf env
rm -rf static/*
rm db/*.sqlite3
docker ps -a | grep mojo|awk '{print $1}' | xargs docker stop $i
docker ps -a | grep mojo|awk '{print $1}' | xargs docker rm $i