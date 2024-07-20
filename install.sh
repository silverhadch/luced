#!/bin/bash

# Define variables
REPO_URL="https://github.com/silverhadch/luced"
DIST_DIR="dist"
MAN_DIR="docs/man"
EXE_FILE="luced"
MAN_FILE="luced.1"
BIN_DIR="/bin"
MANPAGES_DIR="/usr/share/man/man1"

# Create directories if they don't exist
sudo mkdir -p "$MANPAGES_DIR"

# Check if files already exist and delete them
if [ -f "$BIN_DIR/$EXE_FILE" ]; then
    echo "Removing existing $EXE_FILE from $BIN_DIR..."
    sudo rm "$BIN_DIR/$EXE_FILE"
fi

if [ -f "$MANPAGES_DIR/$MAN_FILE" ]; then
    echo "Removing existing $MAN_FILE from $MANPAGES_DIR..."
    sudo rm "$MANPAGES_DIR/$MAN_FILE"
fi

# Download the luced executable and man page
echo "Downloading $EXE_FILE from $REPO_URL..."
wget -q --show-progress "$REPO_URL/raw/Beta-v.-2.0/$DIST_DIR/$EXE_FILE" -O "$EXE_FILE"

echo "Downloading $MAN_FILE from $REPO_URL..."
wget -q --show-progress "$REPO_URL/raw/Beta-v.-2.0/$MAN_DIR/$MAN_FILE" -O "$MAN_FILE"

# Move files to appropriate directories
echo "Installing $EXE_FILE to $BIN_DIR..."
sudo mv "$EXE_FILE" "$BIN_DIR/$EXE_FILE"
sudo chmod +x "$BIN_DIR/$EXE_FILE"

echo "Installing $MAN_FILE to $MANPAGES_DIR..."
sudo mv "$MAN_FILE" "$MANPAGES_DIR/$MAN_FILE"

# Update man database
echo "Updating man database..."
sudo mandb

echo "Installation complete."
