# desktop-totp
Google Authenticator desktop. Lightweight PyQt5 desktop widget for TOTP codes with one-click copy and visual countdown timer

ENG/[RU](READMEru.md)


## ✨ Features
- System tray icon with visual countdown timer
- Multiple TOTP services support (add/remove)
- Click tray icon to show services and copy codes
- Config stored in JSON file
- System tray notifications on copy
- No window, runs from system tray

## Tech Stack
- Python 3.10+
- PyQt5

## Quick Start
```bash
git clone https://github.com/KSabuev/desktop-totp.git
cd desktop-totp
pip install -r requirements.txt
python app.py
```

## Build DEB Package
Run from Linux terminal (not IDE):
```bash
sudo apt install dpkg-dev
pip install build
./build.sh
```

Install with: `sudo dpkg -i desktop-totp_X.X.X_all.deb`