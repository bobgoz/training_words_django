#!/bin/bash

#Деплой проекта 
#Раскомментить нужные образы, если они обновлялись

PATH_TO_TRAINING='/root/opt/training'

IMAGE_TAG_WEB=bobgoze/training_word

IMAGE_TAG_GATEWAY=bobgoze/gateway

docker build -t $IMAGE_TAG_WEB .
docker push $IMAGE_TAG_WEB

# docker build -t $IMAGE_TAG_GATEWAY ./nginx
# docker push $IMAGE_TAG_GATEWAY

ssh root@2.59.161.253 "cd $PATH_TO_TRAINING && \
    docker-compose -f docker-compose.prod.yml down && \
    docker rmi bobgoze/training_word:latest | true && \
    docker-compose -f docker-compose.prod.yml up -d
    "
