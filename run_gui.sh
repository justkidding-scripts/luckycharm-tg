#!/bin/bash
# GUI Application Runner
# Activates virtual environment and runs GUI applications

echo "🚀 GUI Application Runner"
echo "========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create one with: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated"
echo "Python: $(python --version)"
echo ""

# Run based on argument
case "$1" in
    "tkinter")
        echo "🖼️  Launching tkinter demo..."
        python gui_launcher.py tkinter
        ;;
    "pyqt6")
        echo "🖼️  Launching PyQt6 demo..."
        python gui_launcher.py pyqt6
        ;;
    "hello")
        echo "🖼️  Launching PyQt6 Hello World..."
        python pyqt6_hello.py
        ;;
    "status")
        echo "📊 Checking GUI library status..."
        python gui_launcher.py
        ;;
    *)
        echo "Usage: ./run_gui.sh [tkinter|pyqt6|hello|status]"
        echo ""
        echo "Available commands:"
        echo "  tkinter  - Launch tkinter demo"
        echo "  pyqt6    - Launch PyQt6 demo" 
        echo "  hello    - Launch PyQt6 Hello World"
        echo "  status   - Check GUI library status"
        echo ""
        echo "Or run status check:"
        python gui_launcher.py
        ;;
esac