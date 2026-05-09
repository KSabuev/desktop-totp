# desktop-totp
Google Authenticator для десктопа. Минималистичный виджет для рабочего стола, который генерирует одноразовые пароли (TOTP) и копирует их в буфер обмена по клику.


## Особенности
- Иконка в системном трее с визуальным таймером
- Поддержка нескольких сервисов TOTP (добавление/удаление)
- Клик по иконке показывает список сервисов для копирования
- Конфигурация хранится в JSON-файле
- Уведомления в трее при копировании
- Работает из системного трея без окон

## Библиотеки
- Python 3.10+
- PyQt5

## Быстрый старт
```bash
git clone https://github.com/KSabuev/desktop-totp.git
cd desktop-totp
pip install -r requirements.txt
python app.py
```

## Сборка DEB-пакета
Запускать из терминала Linux (не из IDE):
```bash
sudo apt install dpkg-dev
pip install build
./build.sh
```

Установка: `sudo dpkg -i desktop-totp_X.X.X_all.deb`