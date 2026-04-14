#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

REQUIRED_LIBS=(
    libxcb-cursor0
    libxcb-xinerama0
    libxcb-xinput0
    libxcb-render-util0
    libxcb-icccm4
    libxcb-image0
    libxcb-keysyms1
    libxcb-randr0
    libxcb-shape0
    libxcb-xfixes0
    libxkbcommon-x11-0
    libglu1-mesa
)

echo "Checking system dependencies..."
MISSING=()
for LIB in "${REQUIRED_LIBS[@]}"; do
    dpkg -s "$LIB" &> /dev/null || MISSING+=("$LIB")
done

if [ ${#MISSING[@]} -ne 0 ]; then
    echo "Missing system packages:"
    for LIB in "${MISSING[@]}"; do
        echo "  - $LIB"
    done
    echo ""
    echo "Install them with:"
    echo "sudo apt install ${MISSING[*]}"
    exit 1
fi

echo "All system dependencies are installed."

if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python 3.10+"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "Starting Voices of KRL..."
python3 -m src.main
