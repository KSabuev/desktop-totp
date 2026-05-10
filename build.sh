#!/bin/bash
set -e

cd "$(dirname "$0")"

VERSION=$(grep -m1 '^version = "' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')
echo "Building version $VERSION..."

echo "Building AppImage..."
APPDIR=$(mktemp -d)
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib/desktop-totp/desktop_totp" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/64x64/apps"

cp -r desktop_totp/* "$APPDIR/usr/lib/desktop-totp/desktop_totp/"

pip install --target="$APPDIR/usr/lib/desktop-totp/vendor" PyQt5 -q

cat > "$APPDIR/usr/bin/desktop-totp" << 'EOF'
#!/bin/sh
SELF=$(readlink -f "$0")
APP_DIR=$(dirname "$SELF")
export PYTHONPATH="$APP_DIR/../lib/desktop-totp/vendor:$APP_DIR/../lib/desktop-totp"
exec python3 "$APP_DIR/../lib/desktop-totp/desktop_totp/app.py"
EOF
chmod +x "$APPDIR/usr/bin/desktop-totp"

cat > "$APPDIR/usr/share/applications/desktop-totp.desktop" << 'EOF'
[Desktop Entry]
Name=Desktop TOTP
Comment=TOTP code generator
Exec=desktop-totp
Icon=desktop-totp
Terminal=false
Type=Application
Categories=Utility;
EOF

python3 -c "
from PIL import Image, ImageDraw
size = 64
img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)
draw.ellipse([1, 1, size-1, size-1], outline='green', width=2, fill='white')
img.save('$APPDIR/desktop-totp.png')
"
cp "$APPDIR/desktop-totp.png" "$APPDIR/.DirIcon"
cp "$APPDIR/desktop-totp.png" "$APPDIR/usr/share/icons/hicolor/64x64/apps/desktop-totp.png"
cp "$APPDIR/usr/share/applications/desktop-totp.desktop" "$APPDIR/"

ln -sf usr/bin/desktop-totp "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"

APPIMAGETOOL="${APPIMAGETOOL:-$(which appimagetool 2>/dev/null || echo /tmp/appimagetool)}"
if [ ! -f "$APPIMAGETOOL" ]; then
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -O "$APPIMAGETOOL" && chmod +x "$APPIMAGETOOL"
fi
ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "desktop-totp-${VERSION}-x86_64.AppImage"
rm -rf "$APPDIR"
echo "Done: desktop-totp-${VERSION}-x86_64.AppImage"