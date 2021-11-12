#!/bin/sh

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

git pull
docker-compose stop clickbotbot clickbotlogin
docker-compose build --pull clickbotbot
docker-compose up -d db
sleep 5
docker-compose up --remove-orphans -d clickbotbot
