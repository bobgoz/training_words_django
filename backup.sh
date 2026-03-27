#!/bin/bash

# Конфигурация
SERVER_USER="root"
SERVER_IP="2.59.161.253"
SERVER_PATH="/var/lib/docker/rootfs/overlayfs/98e186f0ccc2827ef1f547fdba71425cf8eb3933549b44f86f991567cfa6e568/app/"        # ← нужно узнать
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).json"
LOCAL_BACKUP_DIR="./backups"
# Команда для бекапа данных
DUMPDATA_COMMAND="python manage.py dumpdata \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions \
  --exclude admin.logentry \
  --indent 2"
CONTAINER_NAME="training_beta"

# Создаём папку для бэкапов
mkdir -p $LOCAL_BACKUP_DIR

echo "📦 Создаём дамп базы данных на сервере..."

# Выполняем dumpdata через контейнер (контейнер называется training_web)
ssh $SERVER_USER@$SERVER_IP "docker exec $CONTAINER_NAME $DUMPDATA_COMMAND > /tmp/$BACKUP_NAME"

echo "📥 Копируем файл с сервера..."

# Копируем файл
scp $SERVER_USER@$SERVER_IP:/tmp/$BACKUP_NAME $LOCAL_BACKUP_DIR/$BACKUP_NAME

# Удаляем временный файл
ssh $SERVER_USER@$SERVER_IP "rm /tmp/$BACKUP_NAME"

echo "✅ Бэкап сохранён: $LOCAL_BACKUP_DIR/$BACKUP_NAME"