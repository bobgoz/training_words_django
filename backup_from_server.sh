#!/bin/bash

SERVER="root@2.59.161.253"
SERVER_BACKUP_DIR="/root/opt/training/backups/volumes/"
PATH_TO_SCRIPT="/root/opt/training/backup_volumes.sh"

DATE=$(date +%d_%m_%Y_%H_%M_%S)

LOCAL_BACKUP_DIR="./backups/training/$DATE/"

mkdir -p $LOCAL_BACKUP_DIR

echo "📦 Забираем бэкап с сервера..."

# Выполняем бэкап на сервере
ssh $SERVER $PATH_TO_SCRIPT

# Скачиваем бэкапы
scp -r $SERVER:$SERVER_BACKUP_DIR/ $LOCAL_BACKUP_DIR/

echo "Очищаем папку volumes на сервере..."

ssh $SERVER "rm -r $SERVER_BACKUP_DIR/*"

echo "✅ Бэкап сохранён в $LOCAL_BACKUP_DIR"