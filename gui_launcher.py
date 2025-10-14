#!/usr/bin/env python3
"""
GUI Status and Launcher
Run this to check GUI library status and launch demos
"""

import sys
import os
import subprocess

def check_gui_status():
    """Check which GUI libraries are working"""
    print("="*50)
    print(" GUI LIBRARY STATUS CHECK")
    print("="*50)
    
    # Check if we're in venv
    venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"Virtual Environment: {'✓ Active' if venv_active else '✗ Not Active'}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Python Path: {sys.executable}")
    
    libraries = [
        ('tkinter', 'Built-in GUI library'),
        ('PyQt6', 'Modern Qt6 framework'),
        ('PyQt5', 'Qt5 framework'),
        ('customtkinter', 'Modern tkinter styling')
    ]
    
    print("\\nLibrary Status:")
    print("-" * 30)
    
    working_libs = []
    for lib, desc in libraries:
        try:
            __import__(lib)
            print(f"✓ {lib:<15} - {desc}")
            working_libs.append(lib)
        except ImportError:
            print(f"✗ {lib:<15} - {desc}")
    
    return working_libs

def launch_tkinter_demo():
    """Launch tkinter demo"""
    print("\\nLaunching tkinter demo...")
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    root = tk.Tk()
    root.title("tkinter Demo")
    root.geometry("400x300")
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Title
    title_label = ttk.Label(main_frame, text="tkinter is Working!", 
                           font=('Arial', 16, 'bold'))
    title_label.grid(row=0, column=0, columnspan=2, pady=20)
    
    # Input section
    ttk.Label(main_frame, text="Enter something:").grid(row=1, column=0, sticky=tk.W, pady=5)
    entry = ttk.Entry(main_frame, width=20)
    entry.grid(row=1, column=1, pady=5, padx=10)
    
    # Buttons
    def show_message():
        text = entry.get() or "Nothing entered"
        messagebox.showinfo("Message", f"You entered: {text}")
    
    ttk.Button(main_frame, text="Show Message", 
              command=show_message).grid(row=2, column=0, pady=10)
    
    ttk.Button(main_frame, text="Close", 
              command=root.destroy).grid(row=2, column=1, pady=10)
    
    # Status
    status_label = ttk.Label(main_frame, text="✓ tkinter GUI library is working perfectly")
    status_label.grid(row=3, column=0, columnspan=2, pady=20)
    
    root.mainloop()

def launch_pyqt6_demo():
    """Launch PyQt6 demo"""
    print("\\nLaunching PyQt6 demo...")
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                                QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QLineEdit, QMessageBox)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    
    app = QApplication(sys.argv)
    
    # Main window
    window = QMainWindow()
    window.setWindowTitle("PyQt6 Demo")
    window.setGeometry(150, 150, 500, 350)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    title = QLabel("PyQt6 is Working!")
    title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Input section
    input_layout = QHBoxLayout()
    input_layout.addWidget(QLabel("Enter something:"))
    line_edit = QLineEdit()
    line_edit.setPlaceholderText("Type here...")
    input_layout.addWidget(line_edit)
    layout.addLayout(input_layout)
    
    # Buttons
    button_layout = QHBoxLayout()
    
    def show_message():
        text = line_edit.text() or "Nothing entered"
        QMessageBox.information(window, "Message", f"You entered: {text}")
    
    show_btn = QPushButton("Show Message")
    show_btn.clicked.connect(show_message)
    button_layout.addWidget(show_btn)
    
    close_btn = QPushButton("Close")
    close_btn.clicked.connect(app.quit)
    button_layout.addWidget(close_btn)
    
    layout.addLayout(button_layout)
    
    # Status
    status = QLabel("✓ PyQt6 GUI library is working perfectly")
    status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(status)
    
    window.show()
    app.exec()

def main():
    """Main menu"""
    working_libs = check_gui_status()
    
    if not working_libs:
        print("\\n❌ No GUI libraries are working!")
        print("Make sure you're in the virtual environment: source venv/bin/activate")
        return
    
    print(f"\\n✅ Found {len(working_libs)} working GUI libraries!")
    print("\\nDemo Options:")
    
    if 'tkinter' in working_libs:
        print("1. Launch tkinter demo")
    
    if 'PyQt6' in working_libs:
        print("2. Launch PyQt6 demo")
    
    print("\\nUsage:")
    print("  python gui_launcher.py tkinter  # Launch tkinter demo")
    print("  python gui_launcher.py pyqt6    # Launch PyQt6 demo")
    print("\\nNote: Make sure to run 'source venv/bin/activate' first!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "tkinter":
            working_libs = check_gui_status()
            if 'tkinter' in working_libs:
                launch_tkinter_demo()
            else:
                print("❌ tkinter is not available")
        elif sys.argv[1].lower() == "pyqt6":
            working_libs = check_gui_status()
            if 'PyQt6' in working_libs:
                launch_pyqt6_demo()
            else:
                print("❌ PyQt6 is not available")
        else:
            print("Usage: python gui_launcher.py [tkinter|pyqt6]")
    else:
        main()