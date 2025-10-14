#!/bin/bash
# Premium Telegram Automation Suite Launcher
# Uses system Python3 with tkinter support

cd "$(dirname "$0")"

echo "🚀 Starting Premium Telegram Automation Suite..."
echo ""

# Check if required modules are available
echo "Checking dependencies..."

# Install missing Python packages if needed
/usr/bin/python3 -c "
import sys
missing_modules = []
required_modules = ['tkinter', 'sqlite3', 'json', 'os', 'threading', 'datetime', 'logging', 'hashlib', 'subprocess', 'asyncio', 'configparser', 'pathlib']

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f'❌ Missing modules: {missing_modules}')
    sys.exit(1)
else:
    print('✅ All core modules available')
"

if [ $? -ne 0 ]; then
    echo "Please install missing dependencies and try again."
    exit 1
fi

# Check for pip modules
echo "Checking pip modules..."
/usr/bin/python3 -c "
import sys
try:
    import telethon
    print('✅ telethon available')
except ImportError:
    print('⚠️  telethon not available - some features may be limited')

try:
    import matplotlib
    print('✅ matplotlib available')
except ImportError:
    print('⚠️  matplotlib not available - charts disabled')
"

echo ""
echo "🎯 PREMIUM TELEGRAM AUTOMATION SUITE"
echo "====================================="
echo ""
echo "FEATURES:"
echo "- 🔐 Secure Authentication (admin/password123!)"
echo "- 🌐 Advanced Proxy Chaining with Tor"
echo "- 👻 Invisible Member Detection"
echo "- 🤖 Automated Batch Scraping"
echo "- ⚙️ Comprehensive Settings Management"
echo "- 💊 Health Monitoring & Auto-Recovery"
echo "- 🛡️ Advanced Anti-Detection System"
echo "- 🎨 Premium Styling"
echo "- 📊 Real-time Analytics Dashboard"
echo "- 🛒 Marketplace Integration Ready"
echo ""
echo "LOGIN CREDENTIALS:"
echo "Username: admin"
echo "Password: password123!"
echo ""
echo "Starting application..."
echo ""

# Launch the application with system Python
/usr/bin/python3 premium_master_launcher.py

echo ""
echo "👋 Application closed."