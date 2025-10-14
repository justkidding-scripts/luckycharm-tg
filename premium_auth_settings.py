#!/usr/bin/env python3
"""
Premium Authentication & Settings System
=======================================
Enterprise-grade authentication and comprehensive settings management.
Includes proxy chaining, health checks, session rotation, and anti-detection.

Features:
- Login authentication (admin / password123!)
- Proxy chaining with Tor integration  
- Advanced settings management
- Health checks and session rotation
- Debugging and anti-detection controls

Author: Premium Security Suite
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib
import json
import os
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import configparser
from premium_styling import apply_premium_styling, PremiumStyleManager

class AuthenticationManager:
    """Secure authentication system for premium access"""
    
    def __init__(self):
        self.authenticated = False
        self.username = None
        self.login_attempts = 0
        self.max_attempts = 5
        self.lockout_time = 300  # 5 minutes
        self.last_failed_attempt = None
        
        # Default credentials (in production, use encrypted storage)
        self.valid_credentials = {
            'admin': self._hash_password('password123!')
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        # Check lockout
        if self.is_locked_out():
            return False
        
        hashed_password = self._hash_password(password)
        
        if username in self.valid_credentials and self.valid_credentials[username] == hashed_password:
            self.authenticated = True
            self.username = username
            self.login_attempts = 0
            return True
        else:
            self.login_attempts += 1
            self.last_failed_attempt = datetime.now()
            return False
    
    def is_locked_out(self) -> bool:
        """Check if account is locked out due to failed attempts"""
        if self.login_attempts >= self.max_attempts and self.last_failed_attempt:
            time_diff = (datetime.now() - self.last_failed_attempt).seconds
            return time_diff < self.lockout_time
        return False
    
    def get_lockout_remaining(self) -> int:
        """Get remaining lockout time in seconds"""
        if self.is_locked_out():
            time_diff = (datetime.now() - self.last_failed_attempt).seconds
            return max(0, self.lockout_time - time_diff)
        return 0

class ProxyChainManager:
    """Advanced proxy chaining system with Tor integration"""
    
    def __init__(self):
        self.proxy_chains = []
        self.active_chain = None
        self.tor_enabled = False
        self.proxychains_config_path = "/etc/proxychains4.conf"
        self.custom_config_path = os.path.expanduser("~/.proxychains/proxychains.conf")
        
        # Ensure custom config directory exists
        os.makedirs(os.path.dirname(self.custom_config_path), exist_ok=True)
        
        self.proxy_types = ['http', 'socks4', 'socks5']
        self.setup_default_chains()
    
    def setup_default_chains(self):
        """Setup default proxy chains"""
        self.proxy_chains = [
            {
                'name': 'Tor Only',
                'proxies': [{'type': 'socks5', 'host': '127.0.0.1', 'port': 9050}],
                'enabled': True
            },
            {
                'name': 'Double Hop',
                'proxies': [
                    {'type': 'socks5', 'host': '127.0.0.1', 'port': 9050},
                    {'type': 'http', 'host': '127.0.0.1', 'port': 8080}
                ],
                'enabled': False
            },
            {
                'name': 'Triple Chain',
                'proxies': [
                    {'type': 'socks5', 'host': '127.0.0.1', 'port': 9050},
                    {'type': 'socks4', 'host': '127.0.0.1', 'port': 1080},
                    {'type': 'http', 'host': '127.0.0.1', 'port': 3128}
                ],
                'enabled': False
            }
        ]
    
    def start_tor(self) -> bool:
        """Start Tor service"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'start', 'tor'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.tor_enabled = True
                time.sleep(5)  # Wait for Tor to establish circuits
                return True
            return False
        except Exception as e:
            print(f"Error starting Tor: {e}")
            return False
    
    def stop_tor(self) -> bool:
        """Stop Tor service"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'stop', 'tor'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.tor_enabled = False
                return True
            return False
        except Exception as e:
            print(f"Error stopping Tor: {e}")
            return False
    
    def test_proxy_chain(self, chain_name: str) -> bool:
        """Test if a proxy chain is working"""
        chain = next((c for c in self.proxy_chains if c['name'] == chain_name), None)
        if not chain:
            return False
        
        # Generate temporary proxychains config
        config_content = self.generate_proxychains_config(chain)
        temp_config = "/tmp/test_proxychains.conf"
        
        with open(temp_config, 'w') as f:
            f.write(config_content)
        
        try:
            # Test with curl through proxychains
            result = subprocess.run([
                'proxychains4', '-f', temp_config, '-q',
                'curl', '--connect-timeout', '10', '-s', 'https://httpbin.org/ip'
            ], capture_output=True, text=True, timeout=15)
            
            return result.returncode == 0 and 'origin' in result.stdout
        except Exception as e:
            print(f"Proxy chain test failed: {e}")
            return False
        finally:
            if os.path.exists(temp_config):
                os.remove(temp_config)
    
    def generate_proxychains_config(self, chain: Dict) -> str:
        """Generate proxychains configuration content"""
        config = """
# Proxychains configuration generated by Premium Telegram Tool
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000
localnet 127.0.0.0/255.0.0.0
quiet_mode

[ProxyList]
"""
        for proxy in chain['proxies']:
            config += f"{proxy['type']} {proxy['host']} {proxy['port']}\n"
        
        return config
    
    def apply_proxy_chain(self, chain_name: str) -> bool:
        """Apply a proxy chain as active configuration"""
        chain = next((c for c in self.proxy_chains if c['name'] == chain_name), None)
        if not chain:
            return False
        
        config_content = self.generate_proxychains_config(chain)
        
        try:
            with open(self.custom_config_path, 'w') as f:
                f.write(config_content)
            
            self.active_chain = chain_name
            return True
        except Exception as e:
            print(f"Error applying proxy chain: {e}")
            return False
    
    def get_proxy_status(self) -> Dict:
        """Get current proxy system status"""
        return {
            'tor_enabled': self.tor_enabled,
            'active_chain': self.active_chain,
            'total_chains': len(self.proxy_chains),
            'enabled_chains': len([c for c in self.proxy_chains if c['enabled']])
        }

class AdvancedSettingsManager:
    """Comprehensive settings management system"""
    
    def __init__(self):
        self.settings_file = "premium_settings.json"
        self.load_settings()
    
    def get_default_settings(self) -> Dict:
        """Get default settings configuration"""
        return {
            # Proxy Settings
            'proxy': {
                'enabled': False,
                'type': 'socks5',
                'host': '127.0.0.1',
                'port': 9050,
                'username': '',
                'password': '',
                'chain_enabled': False,
                'active_chain': 'Tor Only',
                'rotation_interval': 300,  # 5 minutes
            },
            
            # Anti-Detection Settings
            'anti_detection': {
                'enabled': True,
                'user_agent_rotation': True,
                'random_delays': True,
                'delay_min': 1.0,
                'delay_max': 3.0,
                'request_spacing': 0.5,
                'session_rotation': True,
                'rotation_after_requests': 100,
                'stealth_mode': True,
                'simulate_human_behavior': True,
            },
            
            # Health Check Settings
            'health_check': {
                'enabled': True,
                'interval': 60,  # seconds
                'check_connectivity': True,
                'check_proxy_health': True,
                'check_session_validity': True,
                'auto_recover': True,
                'max_retry_attempts': 3,
                'health_threshold': 0.8,
            },
            
            # Session Management
            'session_management': {
                'auto_rotate': True,
                'rotation_strategy': 'round_robin',  # round_robin, random, least_used
                'max_concurrent_sessions': 5,
                'session_timeout': 1800,  # 30 minutes
                'preserve_sessions': True,
                'session_backup_enabled': True,
            },
            
            # Debugging Settings
            'debugging': {
                'enabled': False,
                'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
                'log_to_file': True,
                'log_file': 'telegram_debug.log',
                'max_log_size': 10,  # MB
                'log_rotation': True,
                'capture_network_traffic': False,
                'verbose_errors': True,
            },
            
            # Performance Settings
            'performance': {
                'max_threads': 10,
                'batch_size': 50,
                'queue_size': 1000,
                'memory_limit': 512,  # MB
                'cpu_limit': 80,  # percentage
                'io_timeout': 30,
                'connection_pooling': True,
            },
            
            # Security Settings
            'security': {
                'encryption_enabled': True,
                'secure_storage': True,
                'auto_logout_time': 3600,  # 1 hour
                'require_password_on_start': True,
                'audit_logging': True,
                'data_anonymization': True,
            },
            
            # UI Settings
            'ui': {
                'theme': 'dark',
                'notification_style': 'premium',
                'auto_refresh_interval': 5,
                'show_tooltips': True,
                'advanced_mode': False,
                'remember_window_position': True,
            }
        }
    
    def load_settings(self):
        """Load settings from file or create defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.get_default_settings()
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.get_default_settings()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, category: str, key: str = None):
        """Get setting value"""
        if key is None:
            return self.settings.get(category, {})
        return self.settings.get(category, {}).get(key)
    
    def set(self, category: str, key: str, value):
        """Set setting value"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()
    
    def reset_category(self, category: str):
        """Reset a category to defaults"""
        defaults = self.get_default_settings()
        if category in defaults:
            self.settings[category] = defaults[category]
            self.save_settings()

class LoginWindow:
    """Premium login window with authentication"""
    
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.root = tk.Tk()
        self.style_manager = apply_premium_styling(self.root, 'telegram')
        self.setup_login_window()
    
    def setup_login_window(self):
        """Setup the login window interface"""
        self.root.title("💎 Premium Telegram Tool - Authentication")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center window and make sure it's on top
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"450x400+{x}+{y}")
        
        # Ensure window is always on top and focused
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.style_manager.colors['bg_dark'])
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Logo/Title
        title_label = tk.Label(main_frame,
                              text="💎 PREMIUM ACCESS",
                              bg=self.style_manager.colors['bg_dark'],
                              fg=self.style_manager.colors['primary_accent'],
                              font=self.style_manager.fonts['title'])
        title_label.pack(pady=(0, 30))
        
        # Subtitle
        subtitle_label = tk.Label(main_frame,
                                 text="Enterprise Telegram Automation Suite",
                                 bg=self.style_manager.colors['bg_dark'],
                                 fg=self.style_manager.colors['text_secondary'],
                                 font=self.style_manager.fonts['body'])
        subtitle_label.pack(pady=(0, 20))
        
        # Username field
        tk.Label(main_frame,
                text="Username:",
                bg=self.style_manager.colors['bg_dark'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=(10, 5))
        
        self.username_entry = self.style_manager.create_premium_entry(
            main_frame, "admin", width=25
        )
        self.username_entry.pack(pady=(0, 10), fill=tk.X)
        
        # Password field
        tk.Label(main_frame,
                text="Password:",
                bg=self.style_manager.colors['bg_dark'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=(10, 5))
        
        self.password_entry = tk.Entry(main_frame,
                                      bg=self.style_manager.colors['bg_input'],
                                      fg=self.style_manager.colors['text_primary'],
                                      insertbackground=self.style_manager.colors['text_primary'],
                                      font=self.style_manager.fonts['body'],
                                      relief='flat',
                                      bd=1,
                                      show='*')
        self.password_entry.pack(pady=(0, 20), fill=tk.X)
        self.password_entry.focus_set()  # Set focus to password field
        
        # Login button
        login_btn = self.style_manager.create_premium_button(
            main_frame, "🔐 LOGIN", self.attempt_login, 'Premium'
        )
        login_btn.pack(pady=10, fill=tk.X)
        
        # Status label
        self.status_label = tk.Label(main_frame,
                                    text="",
                                    bg=self.style_manager.colors['bg_dark'],
                                    fg=self.style_manager.colors['text_danger'],
                                    font=self.style_manager.fonts['small'])
        self.status_label.pack(pady=(10, 0))
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.attempt_login())
        
        # Focus on password if username is default
        self.root.after(100, self.set_initial_focus)
    
    def set_initial_focus(self):
        """Set initial focus based on username field"""
        # Make sure window is visible and ready
        self.root.update()
        self.root.lift()
        self.root.focus_force()
        
        if self.username_entry.get() == "admin":
            # Clear the placeholder and focus on password
            self.username_entry.configure(fg=self.style_manager.colors['text_primary'])
            self.password_entry.focus_force()
            self.password_entry.icursor(tk.END)
        else:
            self.username_entry.focus_force()
            self.username_entry.select_range(0, tk.END)
    
    def attempt_login(self):
        """Attempt to authenticate user"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Clear status
        self.status_label.config(text="")
        
        # Check lockout
        if self.auth_manager.is_locked_out():
            remaining = self.auth_manager.get_lockout_remaining()
            self.status_label.config(
                text=f"Account locked. Try again in {remaining} seconds.",
                fg=self.style_manager.colors['text_danger']
            )
            return
        
        # Validate input
        if not username or not password:
            self.status_label.config(
                text="Please enter both username and password.",
                fg=self.style_manager.colors['text_warning']
            )
            return
        
        # Attempt authentication
        if self.auth_manager.authenticate(username, password):
            self.status_label.config(
                text="✅ Authentication successful!",
                fg=self.style_manager.colors['text_success']
            )
            self.root.after(1000, self.root.destroy)
        else:
            remaining_attempts = self.auth_manager.max_attempts - self.auth_manager.login_attempts
            self.status_label.config(
                text=f"❌ Invalid credentials. {remaining_attempts} attempts remaining.",
                fg=self.style_manager.colors['text_danger']
            )
            self.password_entry.delete(0, tk.END)
    
    def show(self) -> bool:
        """Show login window and return authentication result"""
        self.root.mainloop()
        return self.auth_manager.authenticated

class SettingsWindow:
    """Comprehensive settings management interface"""
    
    def __init__(self, parent, settings_manager: AdvancedSettingsManager, 
                 proxy_manager: ProxyChainManager):
        self.parent = parent
        self.settings = settings_manager
        self.proxy_manager = proxy_manager
        self.window = None
        self.style_manager = PremiumStyleManager()
    
    def show(self):
        """Show the settings window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("⚙️ Premium Settings")
        self.window.geometry("1000x600")  # Wider but shorter
        self.window.configure(bg=self.style_manager.colors['bg_dark'])
        
        # Apply premium styling
        self.style_manager.apply_premium_theme(self.window, 'telegram')
        
        self.setup_settings_interface()
    
    def setup_settings_interface(self):
        """Setup the settings interface"""
        # Main container
        main_frame = tk.Frame(self.window, bg=self.style_manager.colors['bg_dark'])
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame,
                              text="⚙️ Premium Settings Configuration",
                              bg=self.style_manager.colors['bg_dark'],
                              fg=self.style_manager.colors['text_primary'],
                              font=self.style_manager.fonts['heading'])
        title_label.pack(pady=(0, 20))
        
        # Create notebook for settings categories
        notebook = ttk.Notebook(main_frame, style='Premium.TNotebook')
        notebook.pack(expand=True, fill=tk.BOTH)
        
        # Settings tabs
        self.create_proxy_tab(notebook)
        self.create_anti_detection_tab(notebook)
        self.create_health_check_tab(notebook)
        self.create_session_management_tab(notebook)
        self.create_debugging_tab(notebook)
        self.create_performance_tab(notebook)
        
        # Bottom buttons
        button_frame = tk.Frame(main_frame, bg=self.style_manager.colors['bg_dark'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.style_manager.create_premium_button(
            button_frame, "💾 Save All", self.save_all_settings, 'Success'
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        self.style_manager.create_premium_button(
            button_frame, "🔄 Reset to Defaults", self.reset_all_settings, 'Warning'
        ).pack(side=tk.RIGHT)
        
        self.style_manager.create_premium_button(
            button_frame, "❌ Cancel", self.window.destroy
        ).pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_proxy_tab(self, notebook):
        """Create proxy settings tab"""
        frame = ttk.Frame(notebook, style='Premium.TFrame')
        notebook.add(frame, text="🌐 Proxy & Chains")
        
        # Scrollable frame
        canvas = tk.Canvas(frame, bg=self.style_manager.colors['bg_dark'])
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style_manager.colors['bg_dark'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Proxy Chaining Section
        chain_card, chain_content = self.style_manager.create_premium_card(
            scrollable_frame, "🔗 Proxy Chaining", 800, 300
        )
        chain_card.pack(fill=tk.X, pady=10)
        
        # Tor control
        tor_frame = tk.Frame(chain_content, bg=self.style_manager.colors['bg_card'])
        tor_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(tor_frame,
                text="🧅 Tor Service:",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.style_manager.create_premium_button(
            tor_frame, "▶️ Start Tor", lambda: self.proxy_manager.start_tor(), 'Success'
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        self.style_manager.create_premium_button(
            tor_frame, "⏹️ Stop Tor", lambda: self.proxy_manager.stop_tor(), 'Warning'
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Chain selection
        chain_select_frame = tk.Frame(chain_content, bg=self.style_manager.colors['bg_card'])
        chain_select_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(chain_select_frame,
                text="Active Chain:",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.chain_var = tk.StringVar(value=self.settings.get('proxy', 'active_chain'))
        chain_combo = ttk.Combobox(chain_select_frame,
                                  textvariable=self.chain_var,
                                  values=[chain['name'] for chain in self.proxy_manager.proxy_chains],
                                  state='readonly')
        chain_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        self.style_manager.create_premium_button(
            chain_select_frame, "🔧 Apply Chain", 
            lambda: self.proxy_manager.apply_proxy_chain(self.chain_var.get()), 'Premium'
        ).pack(side=tk.RIGHT)
        
        self.style_manager.create_premium_button(
            chain_select_frame, "🧪 Test Chain", 
            lambda: self.test_selected_chain(), 'Gold'
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_anti_detection_tab(self, notebook):
        """Create anti-detection settings tab"""
        frame = ttk.Frame(notebook, style='Premium.TFrame')
        notebook.add(frame, text="🛡️ Anti-Detection")
        
        main_content = tk.Frame(frame, bg=self.style_manager.colors['bg_dark'])
        main_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Create scrollable frame for anti-detection settings
        canvas = tk.Canvas(main_content, bg=self.style_manager.colors['bg_dark'])
        scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style_manager.colors['bg_dark'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Anti-Detection Settings
        detection_card, detection_content = self.style_manager.create_premium_card(
            scrollable_frame, "🛡️ Anti-Detection Configuration", 800, 350
        )
        detection_card.pack(fill=tk.X, pady=10)
        
        # Enable/Disable anti-detection
        self.anti_detection_var = tk.BooleanVar(value=self.settings.get('anti_detection', 'enabled'))
        tk.Checkbutton(detection_content,
                      text="Enable Anti-Detection System",
                      variable=self.anti_detection_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # User Agent Rotation
        self.ua_rotation_var = tk.BooleanVar(value=self.settings.get('anti_detection', 'user_agent_rotation'))
        tk.Checkbutton(detection_content,
                      text="Rotate User Agents",
                      variable=self.ua_rotation_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Random Delays
        self.random_delays_var = tk.BooleanVar(value=self.settings.get('anti_detection', 'random_delays'))
        tk.Checkbutton(detection_content,
                      text="Random Request Delays",
                      variable=self.random_delays_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Delay configuration
        delay_frame = tk.Frame(detection_content, bg=self.style_manager.colors['bg_card'])
        delay_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(delay_frame,
                text="Delay Range (seconds):",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.delay_min_var = tk.DoubleVar(value=self.settings.get('anti_detection', 'delay_min'))
        delay_min_spin = tk.Spinbox(delay_frame,
                                   from_=0.1, to=10.0, increment=0.1,
                                   textvariable=self.delay_min_var,
                                   width=8,
                                   bg=self.style_manager.colors['bg_input'],
                                   fg=self.style_manager.colors['text_primary'])
        delay_min_spin.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Label(delay_frame,
                text="to",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.delay_max_var = tk.DoubleVar(value=self.settings.get('anti_detection', 'delay_max'))
        delay_max_spin = tk.Spinbox(delay_frame,
                                   from_=0.1, to=10.0, increment=0.1,
                                   textvariable=self.delay_max_var,
                                   width=8,
                                   bg=self.style_manager.colors['bg_input'],
                                   fg=self.style_manager.colors['text_primary'])
        delay_max_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Session rotation settings
        self.session_rotation_var = tk.BooleanVar(value=self.settings.get('anti_detection', 'session_rotation'))
        tk.Checkbutton(detection_content,
                      text="Enable Session Rotation",
                      variable=self.session_rotation_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Stealth mode
        self.stealth_mode_var = tk.BooleanVar(value=self.settings.get('anti_detection', 'stealth_mode'))
        tk.Checkbutton(detection_content,
                      text="Enable Stealth Mode",
                      variable=self.stealth_mode_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Human behavior simulation
        self.human_behavior_var = tk.BooleanVar(value=self.settings.get('anti_detection', 'simulate_human_behavior'))
        tk.Checkbutton(detection_content,
                      text="Simulate Human Behavior",
                      variable=self.human_behavior_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_health_check_tab(self, notebook):
        """Create health check settings tab"""
        frame = ttk.Frame(notebook, style='Premium.TFrame')
        notebook.add(frame, text="💊 Health Checks")
        
        main_content = tk.Frame(frame, bg=self.style_manager.colors['bg_dark'])
        main_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Health Check Settings
        health_card, health_content = self.style_manager.create_premium_card(
            main_content, "💊 System Health Monitoring", 800, 350
        )
        health_card.pack(fill=tk.X, pady=10)
        
        # Enable health checks
        self.health_enabled_var = tk.BooleanVar(value=self.settings.get('health_check', 'enabled'))
        tk.Checkbutton(health_content,
                      text="Enable Health Monitoring",
                      variable=self.health_enabled_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Health check interval
        interval_frame = tk.Frame(health_content, bg=self.style_manager.colors['bg_card'])
        interval_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(interval_frame,
                text="Check Interval (seconds):",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.health_interval_var = tk.IntVar(value=self.settings.get('health_check', 'interval'))
        interval_spin = tk.Spinbox(interval_frame,
                                  from_=30, to=3600, increment=30,
                                  textvariable=self.health_interval_var,
                                  width=10,
                                  bg=self.style_manager.colors['bg_input'],
                                  fg=self.style_manager.colors['text_primary'])
        interval_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto recovery
        self.auto_recover_var = tk.BooleanVar(value=self.settings.get('health_check', 'auto_recover'))
        tk.Checkbutton(health_content,
                      text="Enable Automatic Recovery",
                      variable=self.auto_recover_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
    
    def create_session_management_tab(self, notebook):
        """Create session management settings tab"""
        frame = ttk.Frame(notebook, style='Premium.TFrame')
        notebook.add(frame, text="🔄 Session Rotation")
        
        main_content = tk.Frame(frame, bg=self.style_manager.colors['bg_dark'])
        main_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Session Management Settings
        session_card, session_content = self.style_manager.create_premium_card(
            main_content, "🔄 Session Management & Rotation", 800, 350
        )
        session_card.pack(fill=tk.X, pady=10)
        
        # Auto rotation
        self.session_rotation_var = tk.BooleanVar(value=self.settings.get('session_management', 'auto_rotate'))
        tk.Checkbutton(session_content,
                      text="Enable Automatic Session Rotation",
                      variable=self.session_rotation_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Rotation strategy
        strategy_frame = tk.Frame(session_content, bg=self.style_manager.colors['bg_card'])
        strategy_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(strategy_frame,
                text="Rotation Strategy:",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.rotation_strategy_var = tk.StringVar(value=self.settings.get('session_management', 'rotation_strategy'))
        strategy_combo = ttk.Combobox(strategy_frame,
                                     textvariable=self.rotation_strategy_var,
                                     values=['round_robin', 'random', 'least_used'],
                                     state='readonly',
                                     width=15)
        strategy_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Max concurrent sessions
        concurrent_frame = tk.Frame(session_content, bg=self.style_manager.colors['bg_card'])
        concurrent_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(concurrent_frame,
                text="Max Concurrent Sessions:",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.max_sessions_var = tk.IntVar(value=self.settings.get('session_management', 'max_concurrent_sessions'))
        sessions_spin = tk.Spinbox(concurrent_frame,
                                  from_=1, to=20, increment=1,
                                  textvariable=self.max_sessions_var,
                                  width=5,
                                  bg=self.style_manager.colors['bg_input'],
                                  fg=self.style_manager.colors['text_primary'])
        sessions_spin.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_debugging_tab(self, notebook):
        """Create debugging settings tab"""
        frame = ttk.Frame(notebook, style='Premium.TFrame')
        notebook.add(frame, text="🐛 Debugging")
        
        main_content = tk.Frame(frame, bg=self.style_manager.colors['bg_dark'])
        main_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Debugging Settings
        debug_card, debug_content = self.style_manager.create_premium_card(
            main_content, "🐛 Debug Configuration", 800, 350
        )
        debug_card.pack(fill=tk.X, pady=10)
        
        # Enable debugging
        self.debug_enabled_var = tk.BooleanVar(value=self.settings.get('debugging', 'enabled'))
        tk.Checkbutton(debug_content,
                      text="Enable Debug Mode",
                      variable=self.debug_enabled_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
        
        # Log level
        log_level_frame = tk.Frame(debug_content, bg=self.style_manager.colors['bg_card'])
        log_level_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(log_level_frame,
                text="Log Level:",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.log_level_var = tk.StringVar(value=self.settings.get('debugging', 'log_level'))
        log_level_combo = ttk.Combobox(log_level_frame,
                                      textvariable=self.log_level_var,
                                      values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                                      state='readonly',
                                      width=10)
        log_level_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Verbose errors
        self.verbose_errors_var = tk.BooleanVar(value=self.settings.get('debugging', 'verbose_errors'))
        tk.Checkbutton(debug_content,
                      text="Verbose Error Messages",
                      variable=self.verbose_errors_var,
                      bg=self.style_manager.colors['bg_card'],
                      fg=self.style_manager.colors['text_primary'],
                      selectcolor=self.style_manager.colors['bg_input'],
                      font=self.style_manager.fonts['body']).pack(anchor=tk.W, pady=5)
    
    def create_performance_tab(self, notebook):
        """Create performance settings tab"""
        frame = ttk.Frame(notebook, style='Premium.TFrame')
        notebook.add(frame, text="⚡ Performance")
        
        main_content = tk.Frame(frame, bg=self.style_manager.colors['bg_dark'])
        main_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Performance Settings
        perf_card, perf_content = self.style_manager.create_premium_card(
            main_content, "⚡ Performance Optimization", 800, 350
        )
        perf_card.pack(fill=tk.X, pady=10)
        
        # Max threads
        threads_frame = tk.Frame(perf_content, bg=self.style_manager.colors['bg_card'])
        threads_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(threads_frame,
                text="Max Threads:",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.max_threads_var = tk.IntVar(value=self.settings.get('performance', 'max_threads'))
        threads_spin = tk.Spinbox(threads_frame,
                                 from_=1, to=50, increment=1,
                                 textvariable=self.max_threads_var,
                                 width=5,
                                 bg=self.style_manager.colors['bg_input'],
                                 fg=self.style_manager.colors['text_primary'])
        threads_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # Batch size
        batch_frame = tk.Frame(perf_content, bg=self.style_manager.colors['bg_card'])
        batch_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(batch_frame,
                text="Batch Size:",
                bg=self.style_manager.colors['bg_card'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(side=tk.LEFT)
        
        self.batch_size_var = tk.IntVar(value=self.settings.get('performance', 'batch_size'))
        batch_spin = tk.Spinbox(batch_frame,
                               from_=10, to=500, increment=10,
                               textvariable=self.batch_size_var,
                               width=5,
                               bg=self.style_manager.colors['bg_input'],
                               fg=self.style_manager.colors['text_primary'])
        batch_spin.pack(side=tk.LEFT, padx=(10, 0))
    
    def test_selected_chain(self):
        """Test the selected proxy chain"""
        chain_name = self.chain_var.get()
        if not chain_name:
            messagebox.showwarning("Warning", "Please select a proxy chain to test.")
            return
        
        # Show testing dialog
        test_window = tk.Toplevel(self.window)
        test_window.title("Testing Proxy Chain")
        test_window.geometry("300x150")
        test_window.configure(bg=self.style_manager.colors['bg_dark'])
        
        tk.Label(test_window,
                text=f"Testing {chain_name}...",
                bg=self.style_manager.colors['bg_dark'],
                fg=self.style_manager.colors['text_primary'],
                font=self.style_manager.fonts['body']).pack(expand=True)
        
        # Test in background thread
        def test_chain():
            result = self.proxy_manager.test_proxy_chain(chain_name)
            test_window.after(0, lambda: self.show_test_result(test_window, chain_name, result))
        
        threading.Thread(target=test_chain, daemon=True).start()
    
    def show_test_result(self, test_window, chain_name, result):
        """Show proxy chain test result"""
        test_window.destroy()
        
        if result:
            messagebox.showinfo("Test Result", f"✅ {chain_name} is working correctly!")
        else:
            messagebox.showerror("Test Result", f"❌ {chain_name} failed connectivity test.")
    
    def save_all_settings(self):
        """Save all settings from the UI"""
        # Proxy settings
        self.settings.set('proxy', 'active_chain', self.chain_var.get())
        
        # Anti-detection settings
        self.settings.set('anti_detection', 'enabled', self.anti_detection_var.get())
        self.settings.set('anti_detection', 'user_agent_rotation', self.ua_rotation_var.get())
        self.settings.set('anti_detection', 'random_delays', self.random_delays_var.get())
        self.settings.set('anti_detection', 'delay_min', self.delay_min_var.get())
        self.settings.set('anti_detection', 'delay_max', self.delay_max_var.get())
        self.settings.set('anti_detection', 'session_rotation', self.session_rotation_var.get())
        self.settings.set('anti_detection', 'stealth_mode', self.stealth_mode_var.get())
        self.settings.set('anti_detection', 'simulate_human_behavior', self.human_behavior_var.get())
        
        # Health check settings
        self.settings.set('health_check', 'enabled', self.health_enabled_var.get())
        self.settings.set('health_check', 'interval', self.health_interval_var.get())
        self.settings.set('health_check', 'auto_recover', self.auto_recover_var.get())
        
        # Session management settings
        self.settings.set('session_management', 'auto_rotate', self.session_rotation_var.get())
        self.settings.set('session_management', 'rotation_strategy', self.rotation_strategy_var.get())
        self.settings.set('session_management', 'max_concurrent_sessions', self.max_sessions_var.get())
        
        # Debugging settings
        self.settings.set('debugging', 'enabled', self.debug_enabled_var.get())
        self.settings.set('debugging', 'log_level', self.log_level_var.get())
        self.settings.set('debugging', 'verbose_errors', self.verbose_errors_var.get())
        
        # Performance settings
        self.settings.set('performance', 'max_threads', self.max_threads_var.get())
        self.settings.set('performance', 'batch_size', self.batch_size_var.get())
        
        messagebox.showinfo("Settings", "✅ All settings saved successfully!")
        self.window.destroy()
    
    def reset_all_settings(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Reset each category
            for category in ['proxy', 'anti_detection', 'health_check', 'session_management', 
                           'debugging', 'performance']:
                self.settings.reset_category(category)
            
            messagebox.showinfo("Settings", "✅ All settings reset to defaults!")
            self.window.destroy()

# Demo and testing functions
def demo_authentication():
    """Demo the authentication system"""
    auth_manager = AuthenticationManager()
    login_window = LoginWindow(auth_manager)
    
    success = login_window.show()
    
    if success:
        print("✅ Authentication successful!")
        print(f"Welcome, {auth_manager.username}!")
        return True
    else:
        print("❌ Authentication failed!")
        return False

def demo_settings():
    """Demo the settings system"""
    settings_manager = AdvancedSettingsManager()
    proxy_manager = ProxyChainManager()
    
    # Create demo root window
    root = tk.Tk()
    root.withdraw()  # Hide root window
    
    settings_window = SettingsWindow(root, settings_manager, proxy_manager)
    settings_window.show()
    
    root.mainloop()

if __name__ == "__main__":
    # Demo authentication first
    if demo_authentication():
        # If authenticated, show settings
        demo_settings()