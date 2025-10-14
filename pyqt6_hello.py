#!/usr/bin/env python3
# Activate virtual environment first: source venv/bin/activate
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt
import sys

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("My App")
window.setGeometry(100, 100, 300, 200)  # x, y, width, height

# Create label with better positioning
label = QLabel("Hello World!", window)
label.setAlignment(Qt.AlignmentFlag.AlignCenter)
label.setGeometry(50, 80, 200, 40)  # Center the label

window.show()
app.exec()
