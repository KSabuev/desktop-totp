from PyQt5.QtWidgets import QApplication, QPushButton, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from dotenv import dotenv_values
import time
import sys

from totp import TOTP

TOTP_SECRET = dotenv_values().get('TOTP_SECRET')
DIGITS = 6
INTERVAL = 30


def get_remaining() -> int:
    return INTERVAL - (int(time.time()) % INTERVAL)


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.generator = TOTP(TOTP_SECRET, DIGITS, INTERVAL)
        self.old_pos = None
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(100, 40)

        btn = QPushButton('TOTP', self)
        btn.move(5, 5)
        btn.clicked.connect(self.copy_totp)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def copy_totp(self):
        otp = self.generator.get_current()
        QApplication.clipboard().setText(otp)

    def update_time(self):
        self.update()

    def paintEvent(self, _):
        t = get_remaining()
        painter = QPainter(self)
        painter.fillRect(0, 35, (t * 100 // INTERVAL), 5, QColor('green' if t > 5 else 'red'))

    def mousePressEvent(self, e):
        self.old_pos = e.globalPos() if e.button() == Qt.LeftButton else None

    def mouseMoveEvent(self, e):
        if self.old_pos:
            delta = e.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = e.globalPos()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
