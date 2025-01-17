#!/bin/bash

set -e

# Колір тексту
GREEN="\033[32m"
RESET="\033[0m"

# Змінні для конфігурації
REPO_URL="https://github.com/MadCat-88/Trembita_Py_S_SyncSrv.git"
PROJECT_DIR="Trembita_Py_S_SyncSrv"
VENV_DIR="venv"
DB_USER="your_db_user"
DB_PASSWORD="your_db_password"
DB_NAME="soap_service_db"
DB_HOST="127.0.0.1"
DB_PORT="3306"
SERVICE_NAME="soap_sync_service"
#APP_MODULE="main:app"  # Вкажіть правильний модуль додатку

# Використовуємо Python 3.10 тільки !!!
PYTHON_VERSION=python3.10

# Встановлення системних залежностей
echo -e "${GREEN}Встановлення системних залежностей...${RESET}"
sudo apt update
sudo apt upgrade -y

# Масив з назвами пакетів
packages=(curl libmariadb-dev gcc ${PYTHON_VERSION} ${PYTHON_VERSION}-venv ${PYTHON_VERSION}-dev git pkg-config)

# Перевірка кожного пакету
for pkg in "${packages[@]}"; do
    if ! apt-cache show "$pkg" > /dev/null 2>&1; then
        echo -e "${GREEN}Пакет $pkg не знайдено в репозиторії. Завершення скрипта.${RESET}"
        exit 1
    fi
done

echo -e "${GREEN}Усі пакети доступні в репозиторії.${RESET}"

# Якщо всі пакети доступні, виконуємо встановлення пакетів за допомогою apt
sudo apt install -y "${packages[@]}"

# Налаштування репозиторію MariaDB
echo -e "${GREEN}Налаштування репозиторію MariaDB...${RESET}"
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | sudo bash

# Встановлення MariaDB сервера
echo -e "${GREEN}Встановлення MariaDB сервера...${RESET}"
sudo apt install -y mariadb-server
sudo apt install -y libmysqlclient-dev
sudo apt install -y libmariadb-dev

# Запуск та налаштування MariaDB
echo -e "${GREEN}Запуск та налаштування MariaDB...${RESET}"
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Створення бази даних та користувача
echo -e "${GREEN}Створення бази даних та користувача...${RESET}"
sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';"
sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Клонування репозиторію
echo -e "${GREEN}Клонування репозиторію...${RESET}"
git clone $REPO_URL
cd $PROJECT_DIR || exit

# Створення та активація віртуального середовища
echo -e "${GREEN}Створення та активація віртуального середовища...${RESET}"
${PYTHON_VERSION} -m venv $VENV_DIR
source $VENV_DIR/bin/activate   # Для Windows: venv\Scripts\activate

# Встановлення залежностей Python
echo -e "${GREEN}Встановлення залежностей Python...${RESET}"
pip install --upgrade pip
pip install -r requirements.txt

# Налаштування конфігурації бази даних
echo -e "${GREEN}Налаштування конфігурації бази даних...${RESET}"
sed -i "s/^sqlalchemy.url = .*/sqlalchemy.url = mariadb+mariadbconnector:\/\/$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT\/$DB_NAME/" alembic.ini
sed -i "s/^host = .*/host = $DB_HOST/" config.ini
sed -i "s/^port = .*/port = $DB_PORT/" config.ini
sed -i "s/^name = .*/name = $DB_NAME/" config.ini
sed -i "s/^username = .*/username = $DB_USER/" config.ini
sed -i "s/^password = .*/password = $DB_PASSWORD/" config.ini

# Створення структури бази даних
echo -e "${GREEN}Створення структури бази даних...${RESET}"
alembic revision --autogenerate -m "Init migration"
alembic upgrade head

# Створення unit файлу для systemd
echo -e "${GREEN}Створення unit файлу для systemd...${RESET}"
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service" << EOL
[Unit]
Description=SOAP Service by Guvicorn
After=network.target

[Service]
User=$USER
WorkingDirectory=$PWD
ExecStart=$PWD/$VENV_DIR/bin/gunicorn -c  gunicorn_config.py main:wsgi_application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Перезапуск systemd та запуск сервісу
echo -e "${GREEN}Перезапуск systemd та запуск сервісу...${RESET}"
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

echo -e "${GREEN}Встановлення завершено! Сервіс запущено та додано в автозапуск.${RESET}"
