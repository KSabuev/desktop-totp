from PyQt5.QtWidgets import QApplication, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtCore import Qt
from dotenv import dotenv_values
from totp import TOTP
import time
import sys

TOTP_SECRET = dotenv_values().get('TOTP_SECRET')
DIGITS = 6
INTERVAL = 30

def get_remaining() -> int:
    return INTERVAL - (int(time.time()) % INTERVAL)


class TotpTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.icon_size = 22

        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("TOTP")

        self.menu = QMenu()
        self.quit_action = QAction("Exit")
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)
        self.tray.setContextMenu(self.menu)

        self.tray.activated.connect(self.on_tray_activated)

        self.generator = TOTP(TOTP_SECRET, DIGITS, INTERVAL)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tray_icon)
        self.timer.start(200)

        self.update_tray_icon()
        self.tray.show()

    def create_icon(self, remaining: int):
        px = QPixmap(self.icon_size, self.icon_size)
        px.fill(Qt.transparent)

        qp = QPainter(px)
        qp.setRenderHint(QPainter.Antialiasing)

        qp.setPen(QPen(QColor("green"), 2))
        qp.setBrush(QColor("white"))
        qp.drawEllipse(1, 1, self.icon_size - 2, self.icon_size - 2)

        if remaining < INTERVAL:
            total_angle = 360 * 16
            angle_span = int(total_angle * remaining / INTERVAL)
            qp.setPen(QColor("green"))
            qp.setBrush(QColor("green"))
            qp.drawPie(1, 1, self.icon_size - 2, self.icon_size - 2, 0, angle_span)

        qp.end()
        return QIcon(px)

    def update_tray_icon(self):
        t = get_remaining()
        self.tray.setToolTip(f"TOTP: {t} s")
        self.tray.setIcon(self.create_icon(t))

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.copy_totp()

    def copy_totp(self):
        otp = self.generator.get_current()
        self.app.clipboard().setText(otp)

    def run(self):
        self.app.exec_()


if __name__ == "__main__":
    app = TotpTrayApp()
    app.run()