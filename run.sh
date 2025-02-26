#!/bin/bash

docker run -d -it --env-file .env -v ./db:/app/db -v ./media:/app/media -v ./reports:/app/reports -p8000:8000 --name mojo-$(date -u +"%Y-%m-%d") mojo bash
docker ps -a