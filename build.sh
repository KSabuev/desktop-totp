#!/bin/bash
set -e

cd "$(dirname "$0")"

VERSION=$(grep -m1 '^version = "' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')
echo "Building version $VERSION..."

mkdir -p dist

if [ ! -f "dist/desktop_totp-${VERSION}-py3-none-any.whl" ]; then
    echo "Building wheel..."
    pip install build -q
    python3 -m build --wheel --no-isolation -q
fi

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

pip install --target="$TEMP_DIR/install" "PyQt5>=5.15" "python-dotenv>=0.19" -q

pip install "dist/desktop_totp-${VERSION}-py3-none-any.whl" --target="$TEMP_DIR/install" -q

PKG_DIR="$TEMP_DIR/pkg"
mkdir -p "$PKG_DIR/usr/lib/python3/dist-packages"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/DEBIAN"

cp -r "$TEMP_DIR/install/desktop_totp" "$PKG_DIR/usr/lib/python3/dist-packages/"
cp -r "$TEMP_DIR/install/desktop_totp-"* "$PKG_DIR/usr/lib/python3/dist-packages/"

cat > "$PKG_DIR/usr/bin/desktop-totp" << 'EOF'
#!/bin/sh
exec python3 -c "from desktop_totp import main; main()" "$@"
EOF
chmod +x "$PKG_DIR/usr/bin/desktop-totp"

cp debian/desktop-totp.desktop "$PKG_DIR/usr/share/applications/"

cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: desktop-totp
Version: $VERSION
Architecture: all
Maintainer: Your Name <you@name.com>
Description: TOTP generator in system tray
 Desktop TOTP is a simple application that generates TOTP codes
 and displays them in the system tray.
Depends: python3 (>=3.8), python3-pyqt5, python3-dotenv
EOF

dpkg-deb --build "$PKG_DIR" "desktop-totp_${VERSION}_all.deb"

echo "Done: desktop-totp_${VERSION}_all.deb"