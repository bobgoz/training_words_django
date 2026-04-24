#!/bin/bash

# Конфигурация
BACKUP_DIR="/root/opt/training/backups/volumes"
DATE=$(date +%Y%m%d_%H%M%S)

# Создаём папку для бэкапов
mkdir -p $BACKUP_DIR

echo "📦 Начинаем бэкап Docker volumes..."

# Список volumes для бэкапа
VOLUMES=(
    "training_postgres_data"
    "training_static"
    "training_media"
)

# Бэкап каждого volume
for VOLUME in "${VOLUMES[@]}"; do
    echo "  → Бэкап $VOLUME..."
    docker run --rm \
        -v ${VOLUME}:/source:ro \
        -v ${BACKUP_DIR}:/backup \
        alpine \
        tar czf /backup/${VOLUME}_${DATE}.tar.gz -C /source .
done

# Бэкап PostgreSQL через pg_dump (рекомендуется для данных)
echo "  → Бэкап PostgreSQL..."
docker exec training_db pg_dump -U bobrov -d training | gzip > ${BACKUP_DIR}/database_${DATE}.sql.gz

echo "✅ Бэкап завершён в $BACKUP_DIR"
