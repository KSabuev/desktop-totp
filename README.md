# desktop-totp
Google Authenticator desktop. Lightweight PyQt5 desktop widget for TOTP codes with one-click copy and visual countdown timer

ENG/[RU](READMEru.md)

## ✨ Features
- Always-on-top, frameless window
- Drag-and-drop anywhere on screen
- Visual progress bar showing time until code refresh
- One-click copy to clipboard
- Supports standard Base32 TOTP secrets

## Tech Stack
- Python 3.10+
- PyQt5
- dotenv

## Quick Start
```bash
git clone https://github.com/KSabuev/desktop-totp.git
cd desktop-totp
pip install -r requirements.txt
python app.py