#!/bin/bash

# Настройки
IMAGE_NAME="avanti"
IMAGE_TAG="latest"
REMOTE_HOST=""
REMOTE_USER=""
REMOTE_PATH="/tmp/avanti"
REMOTE_BUILD_DIR="${REMOTE_PATH}/avanti-build"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Создание временной директории на сервере ===${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_BUILD_DIR}"

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при создании директории на сервере${NC}"
    exit 1
fi

echo -e "${GREEN}=== Копирование файлов проекта на сервер ===${NC}"
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' --exclude 'venv' --exclude '.idea' \
    ./ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BUILD_DIR}/

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при копировании файлов${NC}"
    exit 1
fi

echo -e "${GREEN}=== Сборка Docker образа на сервере ===${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_BUILD_DIR} && docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка при сборке образа на сервере${NC}"
    exit 1
fi

echo -e "${GREEN}=== Очистка временных файлов на сервере ===${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "rm -rf ${REMOTE_BUILD_DIR}"

echo -e "${GREEN}=== Готово! ===${NC}"
echo -e "Docker образ собран на сервере: ${IMAGE_NAME}:${IMAGE_TAG}"
echo -e ""
echo -e "${YELLOW}Образ готов к использованию на ${REMOTE_HOST}${NC}"
echo -e "Для запуска контейнера используйте:"
echo -e "docker run -d --name avanti ${IMAGE_NAME}:${IMAGE_TAG}"
