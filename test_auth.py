#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from premium_styling import PremiumStyleManager
from premium_auth_settings import AuthenticationManager

class SimpleAuthTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔐 Authentication Test")
        self.root.geometry("400x300")
        
        self.style_manager = PremiumStyleManager()
        self.auth_manager = AuthenticationManager()
        
        self.setup_ui()
    
    def setup_ui(self):
        self.root.configure(bg='#1a1a1a')
        
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Title
        tk.Label(main_frame,
                text="🔐 LOGIN TEST",
                bg='#1a1a1a',
                fg='#ffffff',
                font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Username
        tk.Label(main_frame,
                text="Username:",
                bg='#1a1a1a',
                fg='#ffffff',
                font=('Arial', 10)).pack(anchor=tk.W)
        
        self.username_entry = tk.Entry(main_frame,
                                     font=('Arial', 10),
                                     bg='#333333',
                                     fg='#ffffff',
                                     insertbackground='#ffffff')
        self.username_entry.pack(fill=tk.X, pady=(5, 10))
        self.username_entry.insert(0, "admin")
        
        # Password
        tk.Label(main_frame,
                text="Password:",
                bg='#1a1a1a',
                fg='#ffffff',
                font=('Arial', 10)).pack(anchor=tk.W)
        
        self.password_entry = tk.Entry(main_frame,
                                     font=('Arial', 10),
                                     bg='#333333',
                                     fg='#ffffff',
                                     insertbackground='#ffffff',
                                     show='*')
        self.password_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Login button
        login_btn = tk.Button(main_frame,
                            text="🔐 LOGIN",
                            command=self.login,
                            bg='#D72631',
                            fg='#ffffff',
                            font=('Arial', 12, 'bold'),
                            relief='flat',
                            padx=20,
                            pady=10,
                            cursor='hand2')
        login_btn.pack(fill=tk.X, pady=10)
        
        # Status
        self.status_label = tk.Label(main_frame,
                                   text="Enter: admin / password123!",
                                   bg='#1a1a1a',
                                   fg='#cccccc',
                                   font=('Arial', 9))
        self.status_label.pack(pady=10)
        
        # Focus on password field
        self.root.after(100, lambda: self.password_entry.focus_set())
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        print(f"Attempting login with username: '{username}' and password: '{password}'")
        
        if self.auth_manager.authenticate(username, password):
            self.status_label.config(text="✅ SUCCESS!", fg='#00ff00')
            messagebox.showinfo("Success", "Authentication successful!")
            self.root.destroy()
        else:
            self.status_label.config(text="❌ FAILED - Try again", fg='#ff0000')
            self.password_entry.delete(0, tk.END)
    
    def run(self):
        self.root.mainloop()
        return self.auth_manager.authenticated

def main():
    print("🔐 Starting Authentication Test")
    print("Expected credentials:")
    print("Username: admin")
    print("Password: password123!")
    print()
    
    test = SimpleAuthTest()
    success = test.run()
    
    print(f"Authentication result: {success}")

if __name__ == "__main__":
    main()