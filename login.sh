#!/bin/sh

git pull
docker-compose stop clickbotlogin
docker-compose build --pull clickbotlogin
docker-compose up --remove-orphans -d clickbotlogin
docker-compose exec clickbotlogin python3 login.py
