from PyQt5.QtWidgets import (
    QApplication, QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QCursor
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QSystemTrayIcon
from desktop_totp.totp import TOTP
import json
import os
import time
import sys

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
DIGITS = 6
INTERVAL = 30


def get_remaining() -> int:
    return INTERVAL - (int(time.time()) % INTERVAL)


class AddServiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Service")
        self.setFixedSize(300, 150)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Service:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("TOTP Key:"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Secret key")
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)

        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_data(self):
        return self.name_input.text().strip(), self.key_input.text().strip()


class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.services = []
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.services = json.load(f)
        else:
            self.services = []

    def save(self):
        with open(self.config_path, "w") as f:
            json.dump(self.services, f, indent=2)

    def add_service(self, name, secret):
        self.services.append({"name": name, "secret": secret})
        self.save()

    def remove_service(self, index):
        if 0 <= index < len(self.services):
            self.services.pop(index)
            self.save()

    def get_service(self, index):
        if 0 <= index < len(self.services):
            return self.services[index]
        return None


class TotpTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.icon_size = 22
        self.config = ConfigManager(CONFIG_FILE)
        self.generators = {}
        self._rebuild_generators()

        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("TOTP")

        self.context_menu = QMenu()
        self.tray.setContextMenu(self.context_menu)

        self.services_menu = QMenu()
        self.services_menu.setWindowFlags(self.services_menu.windowFlags() | Qt.FramelessWindowHint)

        self.tray.activated.connect(self.on_tray_activated)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tray_icon)
        self.timer.start(200)

        self.rebuild_context_menu()
        self.rebuild_services_menu()
        self.update_tray_icon()
        self.tray.show()

    def _rebuild_generators(self):
        self.generators = {}
        for i, svc in enumerate(self.config.services):
            try:
                self.generators[i] = TOTP(svc["secret"], DIGITS, INTERVAL)
            except Exception:
                self.generators[i] = None

    def rebuild_context_menu(self):
        self.context_menu.clear()

        add_action = QAction("Add Service...", self.context_menu)
        add_action.triggered.connect(self.add_service)
        self.context_menu.addAction(add_action)

        self.context_menu.addSeparator()

        if not self.config.services:
            empty_action = QAction("No services added", self.context_menu)
            empty_action.setEnabled(False)
            self.context_menu.addAction(empty_action)
        else:
            for i, svc in enumerate(self.config.services):
                remove_action = QAction(f"Remove: {svc['name']}", self.context_menu)
                remove_action.triggered.connect(lambda checked, idx=i: self.remove_service(idx))
                self.context_menu.addAction(remove_action)

        self.context_menu.addSeparator()

        quit_action = QAction("Exit", self.context_menu)
        quit_action.triggered.connect(self.app.quit)
        self.context_menu.addAction(quit_action)

    def rebuild_services_menu(self):
        self.services_menu.clear()

        if not self.config.services:
            empty_action = QAction("No services added", self.services_menu)
            empty_action.setEnabled(False)
            self.services_menu.addAction(empty_action)
        else:
            for i, svc in enumerate(self.config.services):
                action = QAction(svc["name"], self.services_menu)
                action.triggered.connect(lambda checked, idx=i: self.copy_totp(idx))
                self.services_menu.addAction(action)

    def add_service(self):
        dialog = AddServiceDialog()
        if dialog.exec_() == QDialog.Accepted:
            name, secret = dialog.get_data()
            if not name:
                QMessageBox.warning(dialog, "Error", "Service name is required.")
                return
            if not secret:
                QMessageBox.warning(dialog, "Error", "TOTP key is required.")
                return
            try:
                TOTP(secret, DIGITS, INTERVAL)
            except Exception:
                QMessageBox.warning(dialog, "Error", "Invalid TOTP key (must be valid Base32).")
                return
            self.config.add_service(name, secret)
            self._rebuild_generators()
            self.rebuild_context_menu()
            self.rebuild_services_menu()
            self.tray.showMessage("TOTP", f"Service '{name}' added.", QSystemTrayIcon.Information, 500)

    def remove_service(self, index):
        svc = self.config.get_service(index)
        if svc and QMessageBox.question(
            None, "Remove Service",
            f"Remove '{svc['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.config.remove_service(index)
            self._rebuild_generators()
            self.rebuild_context_menu()
            self.rebuild_services_menu()
            self.tray.showMessage("TOTP", f"Service '{svc['name']}' removed.", QSystemTrayIcon.Information, 500)

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
            self.rebuild_services_menu()
            self.services_menu.popup(QCursor.pos())

    def copy_totp(self, index):
        gen = self.generators.get(index)
        svc = self.config.get_service(index)
        if gen and svc:
            otp = gen.get_current()
            self.app.clipboard().setText(otp)
            self.tray.showMessage("TOTP", f"{svc['name']}: {otp}", QSystemTrayIcon.Information, 500)

    def run(self):
        self.app.exec_()


if __name__ == "__main__":
    app = TotpTrayApp()
    app.run()