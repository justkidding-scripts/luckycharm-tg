#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox
import hashlib
import time

class SimpleAuth:
    def __init__(self):
        self.username = "admin"
        self.password = "password123!"
        self.authenticated = False
        self.login_attempts = 0
        self.max_attempts = 3
        
    def authenticate(self, username, password):
        """Simple authentication check"""
        if self.login_attempts >= self.max_attempts:
            return False
            
        if username == self.username and password == self.password:
            self.authenticated = True
            self.login_attempts = 0
            return True
        else:
            self.login_attempts += 1
            return False
    
    def show_login_window(self):
        """Show login window and return success/failure"""
        root = tk.Tk()
        root.title("🔐 Premium Login")
        root.geometry("400x300")
        root.configure(bg='#1a1a1a')
        root.resizable(False, False)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (400 // 2)
        y = (root.winfo_screenheight() // 2) - (300 // 2)
        root.geometry(f"400x300+{x}+{y}")
        
        # Make window stay on top initially
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        
        # Main frame
        main_frame = tk.Frame(root, bg='#1a1a1a')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Title
        title_label = tk.Label(main_frame,
                              text="🔐 PREMIUM LOGIN",
                              bg='#1a1a1a',
                              fg='#ffffff',
                              font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # Username field
        tk.Label(main_frame,
                text="Username:",
                bg='#1a1a1a',
                fg='#cccccc',
                font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
        
        username_entry = tk.Entry(main_frame,
                                 font=('Arial', 12),
                                 bg='#333333',
                                 fg='#ffffff',
                                 insertbackground='#ffffff',
                                 relief='flat',
                                 bd=0)
        username_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        username_entry.insert(0, "admin")
        
        # Password field
        tk.Label(main_frame,
                text="Password:",
                bg='#1a1a1a',
                fg='#cccccc',
                font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
        
        password_entry = tk.Entry(main_frame,
                                 font=('Arial', 12),
                                 bg='#333333',
                                 fg='#ffffff',
                                 insertbackground='#ffffff',
                                 relief='flat',
                                 bd=0,
                                 show='*')
        password_entry.pack(fill=tk.X, pady=(0, 20), ipady=8)
        
        # Status label
        status_label = tk.Label(main_frame,
                               text="Enter credentials: admin / password123!",
                               bg='#1a1a1a',
                               fg='#888888',
                               font=('Arial', 9))
        status_label.pack(pady=(0, 20))
        
        # Login button
        def do_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                status_label.config(text="Please enter both username and password!", fg='#ff6666')
                return
            
            if self.authenticate(username, password):
                status_label.config(text="✅ Login successful!", fg='#66ff66')
                root.after(1000, root.destroy)
            else:
                remaining = self.max_attempts - self.login_attempts
                if remaining > 0:
                    status_label.config(text=f"❌ Invalid credentials! {remaining} attempts left", fg='#ff6666')
                    password_entry.delete(0, tk.END)
                else:
                    status_label.config(text="❌ Too many failed attempts!", fg='#ff6666')
                    root.after(2000, root.destroy)
        
        login_btn = tk.Button(main_frame,
                             text="🔐 LOGIN",
                             command=do_login,
                             bg='#8B7355',  # Elegant beige
                             fg='#ffffff',
                             font=('Arial', 12, 'bold'),
                             relief='flat',
                             bd=0,
                             cursor='hand2')
        login_btn.pack(fill=tk.X, pady=10, ipady=10)
        
        # Bind Enter key
        def on_enter(event):
            do_login()
        
        root.bind('<Return>', on_enter)
        password_entry.bind('<Return>', on_enter)
        username_entry.bind('<Return>', on_enter)
        
        # Focus on password field after a short delay
        def focus_password():
            password_entry.focus_set()
            password_entry.icursor(tk.END)
        
        root.after(200, focus_password)
        
        # Run the window
        try:
            root.mainloop()
        except:
            pass
            
        return self.authenticated

def test_auth():
    """Test the authentication system"""
    print("🔐 Testing Simple Authentication")
    print("Expected: username=admin, password=password123!")
    
    auth = SimpleAuth()
    success = auth.show_login_window()
    
    print(f"Authentication result: {success}")
    return success

if __name__ == "__main__":
    test_auth()