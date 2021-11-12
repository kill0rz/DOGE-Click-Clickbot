#!/bin/sh

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

git pull
# prevent interrupt from running instance
docker-compose stop clickbotbot clickbotlogin
docker-compose up -d db

# load env variables for docker volume
export $(cat .env | xargs)

# run withdrawal script
docker build ./build/ -t clickbotbot:withdraw -f build/Dockerfile-withdraw
docker run --rm --env-file .env -v ${SCRIPTPATH}/${DATA_STORAGE}sessions/:'/usr/src/app/session/' clickbotbot:withdraw
