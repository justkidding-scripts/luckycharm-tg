#!/bin/bash
set -e

echo "🔧 Starting setup for Rust, Python, C++, and Go development environment..."
sudo apt update && sudo apt install -y \
  build-essential \
  cmake \
  curl \
  git \
  pkg-config \
  libssl-dev \
  lldb \
  gdb \
  valgrind \
  python3-pip \
  qtbase5-dev \
  libqt5svg5-dev \
  qttools5-dev-tools \
  libgl1-mesa-dev \
  libxrandr-dev \
  libxinerama-dev \
  libxcursor-dev \
  libxi-dev \
  xclip

# Rust setup
if ! command -v rustup &> /dev/null; then
  echo "🦀 Installing Rust..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  source "$HOME/.cargo/env"
fi

echo "📦 Installing Rust tools..."
cargo install cargo-expand
cargo install cargo-watch
cargo install cargo-edit
cargo install trunk
cargo install --locked pretty_assertions
cargo install --locked tracing-subscriber

# Rust GUI frameworks
cargo install egui_demo_app
cargo install iced

# Python setup
echo "🐍 Installing Python debuggers and GUI libs..."
pip3 install --upgrade pip
pip3 install pudb ipdb debugpy icecream rich textual dearpygui pyqt6

# Go setup
if ! command -v go &> /dev/null; then
  echo "🐹 Installing Go..."
  sudo apt install -y golang-go
fi

echo "📦 Installing Go debugging/profiling tools..."
go install github.com/go-delve/delve/cmd/dlv@latest
go install github.com/rogpeppe/godef@latest
go install github.com/kyoh86/richgo@latest

# Go GUI frameworks
go install fyne.io/fyne/v2/cmd/fyne@latest

# C++ setup
echo "🧠 Installing C++ testing/debugging tools..."
git clone https://github.com/catchorg/Catch2.git
cd Catch2 && cmake -Bbuild -H. && sudo cmake --build build/ --target install && cd ..
rm -rf Catch2

# Install vcpkg (optional C++ package manager)
echo "📦 Installing vcpkg (for C++ dependencies)..."
git clone https://github.com/microsoft/vcpkg.git
./vcpkg/bootstrap-vcpkg.sh

echo "✅ Setup complete. Recommended next steps:"
echo "- Use 'cargo watch -x run' for live Rust dev"
echo "- Use 'dlv debug' for Go live debugging"
echo "- Use 'textual run your_script.py' for Python TUI apps"
echo "- Use 'qtcreator' or 'cursor' for GUI editing in C++"
echo "- Explore GUI demos: 'egui_demo_app', 'dearpygui', 'fyne demo'"

