# Інсталяція вебсервісу вручну

Також існує можливість встановлення вебсервісу вручну, без застосування скрипта.

Для початку роботи потрібно мати чисту систему Ubuntu, всі необхідні пакети та репозиторії будуть підключені в ході виконання встановлення.

**Для того, щоб встановити даний вебсервіс вручну необхідно:**

### 1. Додати репозиторій з Python3.10:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

### 2. Встановити необхідні пакети:

```bash
sudo apt-get update
sudo apt upgrade -y
sudo apt install -y curl libmariadb-dev gcc python3.10 python3.10-venv python3.10-dev git pkg-config
```
**Важливо!** Якщо версія Python нижче 3.10, сервіс працювати не буде.

### 3. Додати репозиторій MariaDB

```bash
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | sudo bash
```

### 4. Встановити СУБД MariaDB:

```bash
sudo apt install -y mariadb-server
sudo apt install -y libmysqlclient-dev
sudo apt install -y libmariadb-dev
```
### 5. Запустити MariaDB та налаштувати автозапуск:

```bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

### 6. Перевірити чи працює MariaDB:

```bash
sudo systemctl status mariadb
```

**Примітка**. Якщо базу даних запущено, можна переходити до виконання наступних кроків. Інакше – потрібно перевірити чи не було допущено помилку при виконанні одного з попередніх кроків.

### 7. Створити базу даних та користувача. Для цього необхідно:

7.1. Увійти в консоль MariaDB:

```bash
sudo mysql
```

7.2. Створити базу даних:

```bash
CREATE DATABASE IF NOT EXISTS your_db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

де: `your_db_name` – бажана назва БД.

7.3. Створити користувача:

```bash
CREATE USER IF NOT EXISTS 'your_db_user'@'%' IDENTIFIED BY 'your_db_password';
```

де:

- `your_db_user` – логін користувача БД;

- `your_db_password` – пароль для даного користувача.

7.4. Надати користувачеві повні права на базу даних, замінивши `your_db_user` на логін створеного на попередньому кроці користувача:

```bash
GRANT ALL PRIVILEGES ON your_db_name.* TO 'your_db_user'@'%';
```

7.5. Примусово оновити привілеї:

```bash
FLUSH PRIVILEGES;
```
Базу даних та користувача успішно створено.

7.6. Вийти з консолі MariaDB:

```bash
exit
```

### 8. Клонувати репозиторій:

```bash
git clone https://github.com/kshypachov/soap_sync_service.git
```

### 9. Перейти до директорії з вебсервісом:

```bash
cd soap_sync_service
```

### 10. Виконати конфігурацію вебсервісу згідно [настанов з конфігурації](./configuration.md).

### 11. Створити віртуальне середовище:

```bash
python3.10 -m venv soap_sync_service
```

### 12. Активувати віртуальне середовище:

```bash
source soap_sync_service/bin/activate
```

### 13. Встановити залежності:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 14. Створити структуру БД, для чого необхідно:

14.1. Створити початкову міграцію:
```bash
alembic revision --autogenerate -m "Init migration"
```

14.2. Налаштувати міграції для створення структури бази даних:
```head
alembic upgrade head
```

### 15. Створити systemd unit-файл для запуску вебсервісу:

```bash
sudo bash -c "cat > /etc/systemd/system/soap_sync_service.service" << EOL
[Unit]
Description=SOAP Service by Guvicorn
After=network.target

[Service]
User=$USER
WorkingDirectory=$PWD
ExecStart=$PWD/venu/bin/gunicorn -c  gunicorn_config.py main:wsgi_application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL
```

### 16. Перезавантажити конфігурацію systemd:

```bash
sudo systemctl daemon-reload
```

### 17. Додати вебсервіс до автозапуску:

```bash
sudo systemctl enable soap_sync_service
```

##
Матеріали створено за підтримки проєкту міжнародної технічної допомоги «Підтримка ЄС цифрової трансформації України (DT4UA)».
