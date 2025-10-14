#!/usr/bin/env python3
"""
Test GUI libraries to see what's working
"""

print("Testing available GUI libraries...")

# Test tkinter
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    def test_tkinter():
        root = tk.Tk()
        root.title("tkinter Test")
        root.geometry("300x200")
        
        label = tk.Label(root, text="tkinter is working!", font=("Arial", 14))
        label.pack(pady=20)
        
        button = tk.Button(root, text="Click me!", 
                          command=lambda: messagebox.showinfo("Success", "tkinter works!"))
        button.pack(pady=10)
        
        quit_btn = tk.Button(root, text="Quit", command=root.quit)
        quit_btn.pack(pady=10)
        
        root.mainloop()
    
    print("✓ tkinter: Available")
    
except ImportError as e:
    print(f"✗ tkinter: Failed - {e}")

# Test PyQt6
try:
    from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
    from PyQt6.QtCore import Qt
    import sys
    
    def test_pyqt6():
        app = QApplication(sys.argv)
        
        window = QWidget()
        window.setWindowTitle("PyQt6 Test")
        window.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        
        label = QLabel("PyQt6 is working!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        def show_message():
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("PyQt6 works!")
            msg.exec()
        
        button = QPushButton("Click me!")
        button.clicked.connect(show_message)
        layout.addWidget(button)
        
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(app.quit)
        layout.addWidget(quit_button)
        
        window.setLayout(layout)
        window.show()
        
        app.exec()
    
    print("✓ PyQt6: Available")
    
except ImportError as e:
    print(f"✗ PyQt6: Failed - {e}")

# Summary
print("\n" + "="*50)
print("Available GUI Libraries:")
print("="*50)

working_libs = []

try:
    import tkinter
    working_libs.append("tkinter (built-in Python GUI)")
    print("1. tkinter - Simple, built-in GUI library")
    print("   Example: import tkinter as tk")
except:
    pass

try:
    import PyQt6
    working_libs.append("PyQt6 (Modern Qt bindings)")
    print("2. PyQt6 - Modern, professional GUI framework")
    print("   Example: from PyQt6.QtWidgets import QApplication")
except:
    pass

if not working_libs:
    print("No GUI libraries are working!")
else:
    print(f"\n{len(working_libs)} GUI libraries are ready to use!")

print("\nTo test the GUIs, run:")
print("python3 gui_test.py tkinter   # Test tkinter")
print("python3 gui_test.py pyqt6     # Test PyQt6")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "tkinter":
            test_tkinter()
        elif sys.argv[1].lower() == "pyqt6":
            test_pyqt6()
        else:
            print("Usage: python3 gui_test.py [tkinter|pyqt6]")