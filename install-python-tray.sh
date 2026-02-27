#!/bin/bash
set -e

echo "Installing Pulsar Mouse Python Tray Applet..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/share/plasma-pulsar"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "Installing Python dependencies..."
pip3 install --user PyQt6

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

echo "Installing Python plasmoid..."
cp "$SCRIPT_DIR/plasma-pulsar-python/pulsar_tray.py" "$INSTALL_DIR/"

echo "Creating autostart entry..."
mkdir -p "$AUTOSTART_DIR"
cp "$SCRIPT_DIR/plasma-pulsar-python/pulsar-mouse-tray.desktop" "$AUTOSTART_DIR/"

# Update the Exec path in the desktop file
sed -i "s|/home/adrianbonpin/.local/share/plasma-pulsar|$INSTALL_DIR|g" "$AUTOSTART_DIR/pulsar-mouse-tray.desktop"

echo ""
echo "Installation complete!"
echo ""
echo "The tray applet will start automatically on next login."
echo ""
echo "To start it now, run:"
echo "  python3 $INSTALL_DIR/pulsar_tray.py"
echo ""
echo "Or use the D-Bus service directly with:"
echo "  systemctl --user start pulsard"
