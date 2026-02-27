#!/usr/bin/env python3
"""
Pulsar Mouse Tool - Python System Tray Applet
A PyQt6-based system tray widget for Pulsar X2V2 Mini mouse
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSlider, QPushButton, QLineEdit, QSpinBox, QGroupBox,
    QFrame, QGridLayout, QColorDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QColor
import dbus

from pulsar_lib import Device, PulsarX2V2Mini, LEDEffect


class PulsarTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme("input-mouse"))
        self.tray_icon.setToolTip("Pulsar X2V2 Mini")
        
        # Create menu
        self.menu = QMenu()
        
        # Battery status
        self.battery_action = QAction("🔋 Checking...", self.menu)
        self.battery_action.setEnabled(False)
        self.menu.addAction(self.battery_action)
        
        self.menu.addSeparator()
        
        # Quick actions
        self.refresh_action = QAction("🔄 Refresh", self.menu)
        self.refresh_action.triggered.connect(self.refresh_data)
        self.menu.addAction(self.refresh_action)
        
        self.open_settings_action = QAction("⚙️ Open Settings", self.menu)
        self.open_settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.open_settings_action)
        
        self.menu.addSeparator()
        
        # Quit
        self.quit_action = QAction("❌ Quit", self.menu)
        self.quit_action.triggered.connect(self.quit)
        self.menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Settings window
        self.settings_window = None
        
        # D-Bus connection
        self.dbus_connected = False
        self.setup_dbus()
        
        # Data
        self.battery_percent = 0
        self.is_charging = False
        self.is_connected = False
        self.settings = {}
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # Update every 5 seconds
        
        # Initial refresh
        self.refresh_data()
    
    def setup_dbus(self):
        """Connect to D-Bus service"""
        try:
            self.bus = dbus.SessionBus()
            self.proxy = self.bus.get_object('org.pulsar.Pulsar', '/org/pulsar/Pulsar')
            self.iface = dbus.Interface(self.proxy, 'org.pulsar.Pulsar')
            self.dbus_connected = True
        except Exception as e:
            print(f"D-Bus connection failed: {e}")
            self.dbus_connected = False
    
    def refresh_data(self):
        """Refresh data from mouse"""
        if not self.dbus_connected:
            self.setup_dbus()
        
        try:
            # Check connection
            connected = self.iface.IsConnected()
            self.is_connected = connected
            
            if connected:
                # Get power info
                power = self.iface.GetPower()
                self.battery_percent = int(power['battery_percent'])
                self.is_charging = bool(power['connected'])
                
                # Update tooltip
                self.tray_icon.setToolTip(
                    f"Pulsar X2V2 Mini - {self.battery_percent}%"
                    f"{' (charging)' if self.is_charging else ''}"
                )
                
                # Update menu
                self.battery_action.setText(
                    f"🔋 {self.battery_percent}%"
                    f"{' ⚡' if self.is_charging else ''}"
                )
                
                # Get settings
                self.settings = self.iface.GetAllSettings()
                
                # Update settings window if open
                if self.settings_window and self.settings_window.isVisible():
                    self.settings_window.update_from_data(self.settings)
            else:
                self.battery_action.setText("🔋 Mouse Disconnected")
                self.tray_icon.setToolTip("Pulsar X2V2 Mini - Disconnected")
                
        except Exception as e:
            print(f"Error refreshing data: {e}")
            self.battery_action.setText("🔋 Error")
            self.is_connected = False
            self.dbus_connected = False
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_settings()
    
    def show_settings(self):
        """Show settings window"""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self)
        
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        self.refresh_data()
    
    def quit(self):
        """Quit application"""
        self.timer.stop()
        self.app.quit()
    
    def run(self):
        """Run the application"""
        self.tray_icon.show()
        sys.exit(self.app.exec())


class SettingsWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Pulsar Mouse Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Connection status
        self.status_label = QLabel("Status: Checking...")
        layout.addWidget(self.status_label)
        
        # Profile section
        profile_group = QGroupBox("Profile")
        profile_layout = QHBoxLayout(profile_group)
        
        profile_layout.addWidget(QLabel("Active Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Profile 1", "Profile 2", "Profile 3", "Profile 4"])
        self.profile_combo.currentIndexChanged.connect(self.on_profile_changed)
        profile_layout.addWidget(self.profile_combo)
        
        layout.addWidget(profile_group)
        
        # DPI section
        dpi_group = QGroupBox("DPI Settings")
        dpi_layout = QGridLayout(dpi_group)
        
        self.dpi_spinboxes = []
        for i in range(4):
            dpi_layout.addWidget(QLabel(f"Mode {i+1}:"), i, 0)
            spinbox = QSpinBox()
            spinbox.setRange(50, 26000)
            spinbox.setSingleStep(50)
            spinbox.valueChanged.connect(lambda val, mode=i: self.on_dpi_changed(mode, val))
            self.dpi_spinboxes.append(spinbox)
            dpi_layout.addWidget(spinbox, i, 1)
        
        dpi_layout.addWidget(QLabel("Active Mode:"), 4, 0)
        self.active_mode_combo = QComboBox()
        self.active_mode_combo.addItems(["Mode 1", "Mode 2", "Mode 3", "Mode 4"])
        self.active_mode_combo.currentIndexChanged.connect(self.on_active_mode_changed)
        dpi_layout.addWidget(self.active_mode_combo, 4, 1)
        
        layout.addWidget(dpi_group)
        
        # Polling rate
        polling_group = QGroupBox("Polling Rate")
        polling_layout = QHBoxLayout(polling_group)
        
        polling_layout.addWidget(QLabel("Rate:"))
        self.polling_combo = QComboBox()
        self.polling_combo.addItems(["125 Hz", "250 Hz", "500 Hz", "1000 Hz"])
        self.polling_combo.currentIndexChanged.connect(self.on_polling_changed)
        polling_layout.addWidget(self.polling_combo)
        
        layout.addWidget(polling_group)
        
        # LED section
        led_group = QGroupBox("LED Settings")
        led_layout = QGridLayout(led_group)
        
        led_layout.addWidget(QLabel("Effect:"), 0, 0)
        self.led_effect_combo = QComboBox()
        self.led_effect_combo.addItems(["off", "steady", "breathe"])
        self.led_effect_combo.currentIndexChanged.connect(self.on_led_effect_changed)
        led_layout.addWidget(self.led_effect_combo, 0, 1)
        
        led_layout.addWidget(QLabel("Brightness:"), 1, 0)
        self.led_brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.led_brightness_slider.setRange(0, 255)
        self.led_brightness_slider.valueChanged.connect(self.on_led_brightness_changed)
        led_layout.addWidget(self.led_brightness_slider, 1, 1)
        
        led_layout.addWidget(QLabel("Color:"), 2, 0)
        self.led_color_btn = QPushButton("Choose Color")
        self.led_color_btn.clicked.connect(self.on_led_color_clicked)
        led_layout.addWidget(self.led_color_btn, 2, 1)
        
        layout.addWidget(led_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.app.refresh_data)
        button_layout.addWidget(refresh_btn)
        
        restore_btn = QPushButton("Restore Defaults")
        restore_btn.clicked.connect(self.on_restore_defaults)
        button_layout.addWidget(restore_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def update_from_data(self, settings):
        """Update UI from settings data"""
        # Update connection status
        if self.app.is_connected:
            self.status_label.setText(
                f"Status: Connected - Battery: {self.app.battery_percent}%"
            )
        else:
            self.status_label.setText("Status: Disconnected")
        
        # Block signals while updating
        self.profile_combo.blockSignals(True)
        self.active_mode_combo.blockSignals(True)
        self.polling_combo.blockSignals(True)
        self.led_effect_combo.blockSignals(True)
        self.led_brightness_slider.blockSignals(True)
        for spinbox in self.dpi_spinboxes:
            spinbox.blockSignals(True)
        
        # Update profile
        active_profile = settings.get('active_profile', 0)
        self.profile_combo.setCurrentIndex(active_profile)
        
        # Update DPI modes
        dpi_modes = settings.get('dpi_modes', [])
        for i, mode_data in enumerate(dpi_modes[:4]):
            if isinstance(mode_data, dict):
                self.dpi_spinboxes[i].setValue(mode_data.get('dpi', 1600))
            else:
                self.dpi_spinboxes[i].setValue(1600)
        
        # Update active mode
        active_mode = settings.get('active_dpi_mode', 0)
        self.active_mode_combo.setCurrentIndex(active_mode)
        
        # Update polling rate
        polling = settings.get('polling_rate_hz', 1000)
        polling_idx = {125: 0, 250: 1, 500: 2, 1000: 3}.get(polling, 3)
        self.polling_combo.setCurrentIndex(polling_idx)
        
        # Update LED
        led = settings.get('led', {})
        effect = led.get('effect', 'off')
        effect_idx = {'off': 0, 'steady': 1, 'breathe': 2}.get(effect, 0)
        self.led_effect_combo.setCurrentIndex(effect_idx)
        
        brightness = led.get('brightness', 128)
        self.led_brightness_slider.setValue(brightness)
        
        # Re-enable signals
        self.profile_combo.blockSignals(False)
        self.active_mode_combo.blockSignals(False)
        self.polling_combo.blockSignals(False)
        self.led_effect_combo.blockSignals(False)
        self.led_brightness_slider.blockSignals(False)
        for spinbox in self.dpi_spinboxes:
            spinbox.blockSignals(False)
    
    def on_profile_changed(self, index):
        """Handle profile change"""
        if self.app.is_connected and self.app.dbus_connected:
            try:
                self.app.iface.SetProfile(int(index))
            except Exception as e:
                print(f"Error setting profile: {e}")
    
    def on_dpi_changed(self, mode, value):
        """Handle DPI change"""
        if self.app.is_connected and self.app.dbus_connected:
            try:
                self.app.iface.SetDPI(int(mode), int(value))
            except Exception as e:
                print(f"Error setting DPI: {e}")
    
    def on_active_mode_changed(self, index):
        """Handle active mode change"""
        if self.app.is_connected and self.app.dbus_connected:
            try:
                dpi = self.dpi_spinboxes[index].value()
                self.app.iface.SetDPI(int(index), int(dpi))
            except Exception as e:
                print(f"Error setting active mode: {e}")
    
    def on_polling_changed(self, index):
        """Handle polling rate change"""
        if self.app.is_connected and self.app.dbus_connected:
            try:
                rates = [125, 250, 500, 1000]
                self.app.iface.SetPollingRate(rates[index])
            except Exception as e:
                print(f"Error setting polling rate: {e}")
    
    def on_led_effect_changed(self, index):
        """Handle LED effect change"""
        if self.app.is_connected and self.app.dbus_connected:
            try:
                effects = ["off", "steady", "breathe"]
                self.app.iface.SetLEDEffect(effects[index])
            except Exception as e:
                print(f"Error setting LED effect: {e}")
    
    def on_led_brightness_changed(self, value):
        """Handle LED brightness change"""
        if self.app.is_connected and self.app.dbus_connected:
            try:
                self.app.iface.SetLEDBrightness(int(value))
            except Exception as e:
                print(f"Error setting LED brightness: {e}")
    
    def on_led_color_clicked(self):
        """Handle LED color picker"""
        color = QColorDialog.getColor()
        if color.isValid() and self.app.is_connected and self.app.dbus_connected:
            try:
                color_str = f"#{color.red():02x}{color.green():02x}{color.blue():02x}"
                active_mode = self.active_mode_combo.currentIndex()
                self.app.iface.SetLEDColor(int(active_mode), color_str)
            except Exception as e:
                print(f"Error setting LED color: {e}")
    
    def on_restore_defaults(self):
        """Restore factory defaults"""
        if self.app.is_connected and self.app.dbus_connected:
            try:
                self.app.iface.RestoreDefaults()
                self.app.refresh_data()
            except Exception as e:
                print(f"Error restoring defaults: {e}")


def main():
    app = PulsarTrayApp()
    app.run()


if __name__ == '__main__':
    main()
