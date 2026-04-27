# desktop-totp
Google Authenticator для десктопа. Минималистичный виджет для рабочего стола, который генерирует одноразовые пароли (TOTP) и копирует их в буфер обмена по клику.

## Особенности
- Окно поверх всех приложений (always-on-top)
- Перетаскивание мышью в любое место экрана
- Визуальный индикатор времени до обновления кода
- Копирование кода в буфер в один клик
- Поддержка стандартных TOTP-секретов (Base32)

## Библиотеки
- Python 3.10+
- PyQt5
- dotenv

## Быстрый старт
```bash
git clone https://github.com/KSabuev/desktop-totp.git
cd desktop-totp
pip install -r requirements.txt
python app.py