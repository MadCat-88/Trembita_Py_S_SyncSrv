#!/bin/bash

set -e

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
echo "Встановлення системних залежностей..."
sudo apt update
sudo apt upgrade -y

# Масив з назвами пакетів
packages=(curl libmariadb-dev gcc ${PYTHON_VERSION} ${PYTHON_VERSION}-venv ${PYTHON_VERSION}-dev git pkg-config)

# Перевірка кожного пакету
for pkg in "${packages[@]}"; do
    if ! apt-cache show "$pkg" > /dev/null 2>&1; then
        echo "Пакет $pkg не знайдено в репозиторії. Завершення скрипта."
        exit 1
    fi
done

echo "Усі пакети доступні в репозиторії."

# Якщо всі пакети доступні, виконуємо встановлення пакетів за допомогою apt
sudo apt install -y "${packages[@]}"

# Налаштування репозиторію MariaDB
echo "Налаштування репозиторію MariaDB..."
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash

# Встановлення MariaDB сервера
echo "Встановлення MariaDB сервера..."
sudo apt install -y mariadb-server
sudo apt install -y libmysqlclient-dev
sudo apt install -y libmariadb-dev

# Запуск та налаштування MariaDB
echo "Запуск та налаштування MariaDB..."
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Створення бази даних та користувача
echo "Створення бази даних та користувача..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';"
sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Клонування репозиторію
echo "Клонування репозиторію..."
git clone $REPO_URL
cd $PROJECT_DIR || exit

# Створення та активація віртуального середовища
echo "Створення та активація віртуального середовища..."
${PYTHON_VERSION} -m venv $VENV_DIR
source $VENV_DIR/bin/activate   # Для Windows: venv\Scripts\activate

# Встановлення залежностей Python
echo "Встановлення залежностей Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Налаштування конфігурації бази даних
echo "Налаштування конфігурації бази даних..."
sed -i "s/^sqlalchemy.url = .*/sqlalchemy.url = mariadb+mariadbconnector:\/\/$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT\/$DB_NAME/" alembic.ini
sed -i "s/^host = .*/host = $DB_HOST/" config.ini
sed -i "s/^port = .*/port = $DB_PORT/" config.ini
sed -i "s/^name = .*/name = $DB_NAME/" config.ini
sed -i "s/^username = .*/username = $DB_USER/" config.ini
sed -i "s/^password = .*/password = $DB_PASSWORD/" config.ini

# Створення структури бази даних
echo "Створення структури бази даних..."
alembic revision --autogenerate -m "Init migration"
alembic upgrade head

# Створення unit файлу для systemd
echo "Створення unit файлу для systemd..."
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service" << EOL
[Unit]
Description=SOAP Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$PWD
ExecStart=$PWD/$VENV_DIR/bin/python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Перезапуск systemd та запуск сервісу
echo "Перезапуск systemd та запуск сервісу..."
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

echo "Встановлення завершено! Сервіс запущено та додано в автозапуск."
