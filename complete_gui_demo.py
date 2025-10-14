#!/usr/bin/env python3
"""
Complete GUI Package Demo and Installation Summary
Demonstrates working GUI libraries available on this system
"""

import os
import sys
import subprocess

def check_package(package_name):
    """Check if a Python package is importable"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def run_tkinter_demo():
    """Modern tkinter demo with multiple widgets"""
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
    
    root = tk.Tk()
    root.title("Advanced tkinter Demo")
    root.geometry("600x500")
    root.configure(bg='#f0f0f0')
    
    # Create notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Tab 1: Basic widgets
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Basic Widgets")
    
    ttk.Label(tab1, text="tkinter GUI Demo", font=('Arial', 16, 'bold')).pack(pady=10)
    
    # Entry and button
    entry_frame = ttk.Frame(tab1)
    entry_frame.pack(pady=10)
    ttk.Label(entry_frame, text="Enter text:").pack(side='left')
    entry = ttk.Entry(entry_frame, width=20)
    entry.pack(side='left', padx=5)
    
    def show_entry():
        messagebox.showinfo("Input", f"You entered: {entry.get()}")
    
    ttk.Button(entry_frame, text="Show", command=show_entry).pack(side='left', padx=5)
    
    # Buttons
    button_frame = ttk.Frame(tab1)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="File Dialog", 
              command=lambda: messagebox.showinfo("File", filedialog.askopenfilename() or "No file selected")).pack(side='left', padx=5)
    ttk.Button(button_frame, text="Color Dialog", 
              command=lambda: messagebox.showinfo("Note", "Color dialog requires tkinter.colorchooser")).pack(side='left', padx=5)
    
    # Tab 2: Advanced widgets
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Advanced")
    
    # Progress bar
    progress_frame = ttk.Frame(tab2)
    progress_frame.pack(pady=20)
    ttk.Label(progress_frame, text="Progress Bar:").pack()
    progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
    progress.pack(pady=5)
    progress['value'] = 70
    
    # Scale
    scale_frame = ttk.Frame(tab2)
    scale_frame.pack(pady=20)
    ttk.Label(scale_frame, text="Scale Widget:").pack()
    scale_var = tk.DoubleVar()
    scale = ttk.Scale(scale_frame, from_=0, to=100, orient='horizontal', variable=scale_var)
    scale.pack()
    scale.set(50)
    
    # Text area
    text_frame = ttk.Frame(tab2)
    text_frame.pack(fill='both', expand=True, padx=10, pady=10)
    ttk.Label(text_frame, text="Text Area:").pack(anchor='w')
    text_area = scrolledtext.ScrolledText(text_frame, height=8)
    text_area.pack(fill='both', expand=True)
    text_area.insert('1.0', "This is a scrollable text area.\\nYou can type here and scroll.\\n\\ntkinter is Python's built-in GUI library.")
    
    # Status bar
    status_bar = ttk.Label(root, text="Ready | tkinter is working perfectly", relief='sunken', anchor='w')
    status_bar.pack(side='bottom', fill='x')
    
    root.mainloop()

def run_pyqt6_demo():
    """Advanced PyQt6 demo"""
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                                QLineEdit, QTextEdit, QProgressBar, QSlider,
                                QMessageBox, QFileDialog, QStatusBar)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Advanced PyQt6 Demo")
    window.setGeometry(100, 100, 700, 500)
    
    # Central widget and main layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    
    # Title
    title = QLabel("PyQt6 GUI Demo")
    title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(title)
    
    # Tab widget
    tab_widget = QTabWidget()
    main_layout.addWidget(tab_widget)
    
    # Tab 1: Basic widgets
    tab1 = QWidget()
    tab_widget.addTab(tab1, "Basic Widgets")
    tab1_layout = QVBoxLayout(tab1)
    
    # Input section
    input_layout = QHBoxLayout()
    input_layout.addWidget(QLabel("Enter text:"))
    line_edit = QLineEdit()
    line_edit.setPlaceholderText("Type something here...")
    input_layout.addWidget(line_edit)
    
    def show_input():
        QMessageBox.information(window, "Input", f"You entered: {line_edit.text()}")
    
    show_btn = QPushButton("Show Input")
    show_btn.clicked.connect(show_input)
    input_layout.addWidget(show_btn)
    tab1_layout.addLayout(input_layout)
    
    # Button section
    button_layout = QHBoxLayout()
    
    def open_file():
        file_path, _ = QFileDialog.getOpenFileName(window, "Open File")
        if file_path:
            QMessageBox.information(window, "File Selected", f"Selected: {file_path}")
        else:
            QMessageBox.information(window, "File Dialog", "No file selected")
    
    file_btn = QPushButton("Open File Dialog")
    file_btn.clicked.connect(open_file)
    button_layout.addWidget(file_btn)
    
    info_btn = QPushButton("About PyQt6")
    info_btn.clicked.connect(lambda: QMessageBox.about(window, "About", 
                           "PyQt6 is a modern, professional GUI framework\\nfor Python applications."))
    button_layout.addWidget(info_btn)
    
    tab1_layout.addLayout(button_layout)
    
    # Tab 2: Advanced widgets
    tab2 = QWidget()
    tab_widget.addTab(tab2, "Advanced")
    tab2_layout = QVBoxLayout(tab2)
    
    # Progress bar
    progress_label = QLabel("Progress Bar:")
    tab2_layout.addWidget(progress_label)
    progress_bar = QProgressBar()
    progress_bar.setValue(75)
    tab2_layout.addWidget(progress_bar)
    
    # Slider
    slider_label = QLabel("Slider:")
    tab2_layout.addWidget(slider_label)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(60)
    tab2_layout.addWidget(slider)
    
    # Text area
    text_label = QLabel("Text Area:")
    tab2_layout.addWidget(text_label)
    text_area = QTextEdit()
    text_area.setPlainText("This is a PyQt6 text area.\\n\\nPyQt6 provides:\\n- Modern GUI components\\n- Professional styling\\n- Advanced widgets\\n- Cross-platform support")
    tab2_layout.addWidget(text_area)
    
    # Status bar
    status_bar = QStatusBar()
    status_bar.showMessage("Ready | PyQt6 is working perfectly")
    window.setStatusBar(status_bar)
    
    window.show()
    app.exec()

def main():
    """Main function to show available GUI options"""
    print("="*60)
    print(" GUI PACKAGE INSTALLATION SUMMARY")
    print("="*60)
    
    # Check available packages
    packages = {
        'tkinter': 'Built-in Python GUI library',
        'PyQt6': 'Modern Qt6 bindings for Python',
        'PyQt5': 'Qt5 bindings for Python', 
        'PySide2': 'Official Qt for Python (Qt5)',
        'PySide6': 'Official Qt for Python (Qt6)',
        'customtkinter': 'Modern styled tkinter',
        'kivy': 'Cross-platform GUI framework',
        'wxPython': 'Native GUI toolkit',
        'dearpygui': 'Fast GUI for Python'
    }
    
    print("\\nPackage Status:")
    print("-" * 30)
    
    working_packages = []
    failed_packages = []
    
    for package, description in packages.items():
        if check_package(package):
            print(f"✓ {package:<15} - {description}")
            working_packages.append(package)
        else:
            print(f"✗ {package:<15} - {description}")
            failed_packages.append(package)
    
    print(f"\\nSUMMARY:")
    print(f"Working: {len(working_packages)} packages")
    print(f"Failed:  {len(failed_packages)} packages")
    
    if working_packages:
        print(f"\\nSuccessfully installed GUI libraries:")
        for pkg in working_packages:
            print(f"  • {pkg}")
    
    # Installation commands for failed packages
    if failed_packages:
        print(f"\\nTo install missing packages, try:")
        for pkg in failed_packages:
            if pkg == 'tkinter':
                print(f"  # {pkg} should be built-in - check Python installation")
            elif pkg == 'wxPython':
                print(f"  sudo apt install libgtk-3-dev && pip install {pkg}")
            else:
                print(f"  pip install {pkg}")
    
    print("\\n" + "="*60)
    print(" DEMO OPTIONS")
    print("="*60)
    
    if 'tkinter' in working_packages:
        print("\\n1. Run tkinter demo:")
        print("   python3 complete_gui_demo.py tkinter")
    
    if 'PyQt6' in working_packages:
        print("\\n2. Run PyQt6 demo:")
        print("   python3 complete_gui_demo.py pyqt6")
    
    print("\\nBoth libraries are excellent choices:")
    print("• tkinter: Simple, lightweight, built-in")
    print("• PyQt6: Professional, feature-rich, modern")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "tkinter":
            run_tkinter_demo()
        elif sys.argv[1].lower() == "pyqt6":
            run_pyqt6_demo()
        else:
            print("Usage: python3 complete_gui_demo.py [tkinter|pyqt6]")
    else:
        main()