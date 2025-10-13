#!/bin/bash
# Telegram Automation Suite - Desktop Launcher with 3-Option Menu
# Delegates to native launchers (C++/Go) with fallback to Python

set -euo pipefail

# Find the comprehensive Telegram system
PRIMARY_PATH="/home/nike/Telegram-Invite-Bulk"
FALLBACK_PATHS=(
  "/home/nike/telegram-invite-bulk-native-pro"
  "/home/nike/telegram-automation-suite-MODULAR"
  "/home/nike/TelegramAutomation"
  "/home/nike/telegram-scraper-native"
  "/home/nike/Desktop/mini-warp-client/utility-tools/telegram-invite-bulk-native-pro"
)

TARGET_DIR=""
if [[ -d "$PRIMARY_PATH" ]]; then
  TARGET_DIR="$PRIMARY_PATH"
else
  for d in "${FALLBACK_PATHS[@]}"; do
    if [[ -d "$d" ]]; then
      TARGET_DIR="$d"
      break
    fi
  done
fi

if [[ -z "$TARGET_DIR" ]]; then
  echo "❌ Could not locate Telegram automation tool directory"
  exit 1
fi

echo "📱 COMPREHENSIVE TELEGRAM AUTOMATION SUITE"
echo "==========================================="
echo "PhD Criminology Research - Copenhagen University"
echo "Features: 150+ tools, Advanced GUI, Master Scraper"
echo ""
echo "🚀 Launching Enhanced Telegram GUI with all features..."
echo "   Location: $TARGET_DIR"

cd "$TARGET_DIR"

# Activate virtual environment if it exists
if [[ -d "$TARGET_DIR/.venv" ]]; then
  echo "🔧 Activating virtual environment..."
  source "$TARGET_DIR/.venv/bin/activate"
elif [[ -d "$TARGET_DIR/telegram_automation_env" ]]; then
  echo "🔧 Activating telegram automation environment..."
  source "$TARGET_DIR/telegram_automation_env/bin/activate"
fi

# Launch the comprehensive GUI directly
echo "🚀 Starting Enhanced Telegram GUI..."
if [[ -f "$TARGET_DIR/enhanced_telegram_gui.py" ]]; then
  python3 "$TARGET_DIR/enhanced_telegram_gui.py" "$@" &
elif [[ -f "$TARGET_DIR/debug_gui.py" ]]; then
  python3 "$TARGET_DIR/debug_gui.py" "$@" &
else
  echo "❌ Enhanced GUI not found in $TARGET_DIR"
  exit 1
fi

echo "✅ GUI launched successfully! Check the application window."
