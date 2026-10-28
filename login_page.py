"""
Login page for CABUS application
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Ensure imports work from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from base_page import BasePage
    from ui_components import AnimatedButton, TitleBar
    from dialogs import ForgotPasswordDialog
except ImportError as e:
    print(f"Error importing modules in login_page.py: {e}")
    print("Please ensure base_page.py, ui_components.py, and dialogs.py are in the same directory")
    sys.exit(1)


class LoginPage(BasePage):
    """Login page with authentication"""
    
    def __init__(self, root, db_manager, on_login_success, on_register_click):
        super().__init__(root, root)
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click
        self.show_password = [False]
        self.current_user_email = None
    
    def show(self):
        """Display the login page"""
        self.clear_content()
        self.root.configure(bg=self.COLORS['BG'])
        
        # Title bar
        TitleBar(self.root, self.root)
        
        # Left panel - Login form
        login_frame = tk.Frame(self.root, bg="#0A0A12")
        login_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            login_frame, text="Login Here", 
            font=("Arial", 65, "bold"), 
            bg="#0A0A12", fg="#C084FF"
        ).place(relx=0.2, rely=0.10)
        
        # Email field
        tk.Label(
            login_frame, text="Email", 
            bg="#0A0A12", fg=self.COLORS['TEXT'], 
            font=("Arial", 20)
        ).place(relx=0.1, rely=0.25)
        
        self.login_email = tk.Entry(
            login_frame, width=30, bd=0, 
            font=("Arial", 30),
            fg=self.COLORS['ACCENT'], 
            bg=self.COLORS['BG'],
            insertbackground=self.COLORS['ACCENT'],
            highlightbackground=self.COLORS['ACCENT'],
            highlightthickness=1, relief="flat"
        )
        self.login_email.place(relx=0.1, rely=0.30)
        
        # Password field
        tk.Label(
            login_frame, text="Password", 
            bg="#0A0A12", fg=self.COLORS['TEXT'], 
            font=("Arial", 20)
        ).place(relx=0.1, rely=0.40)
        
        self.login_password = tk.Entry(
            login_frame, width=30, bd=0, show="*", 
            font=("Arial", 30),
            fg=self.COLORS['ACCENT'], 
            bg=self.COLORS['BG'],
            insertbackground=self.COLORS['ACCENT'],
            highlightbackground=self.COLORS['ACCENT'],
            highlightthickness=1, relief="flat"
        )
        self.login_password.place(relx=0.1, rely=0.45)
        
        # Eye button for show/hide password
        eye_btn = tk.Button(
            login_frame, text="👁", font=("Arial", 16),
            bg=self.COLORS['BG'], fg="#888888",
            bd=0, cursor="hand2", relief="flat",
            activebackground=self.COLORS['BG'],
            activeforeground=self.COLORS['ACCENT'],
            highlightthickness=0,
            command=self.toggle_password
        )
        eye_btn.place(relx=0.88, rely=0.46)
        
        # Add hover effects to eye button
        eye_btn.bind("<Enter>", lambda e: eye_btn.config(fg="#C084FF"))
        eye_btn.bind("<Leave>", lambda e: eye_btn.config(fg="#888888"))
        
        # Login button
        login_btn = AnimatedButton(
            login_frame, 
            "Login", 
            self.handle_login,
            bg_color=self.COLORS['ACCENT']
        )
        login_btn.place(relx=0.35, rely=0.57)
        
        # Forgot password link
        forgot_label = tk.Label(
            login_frame, text="Forgot Password?",
            font=("Arial", 12), bg="#0A0A12", 
            fg="#C084FF", cursor="hand2"
        )
        forgot_label.place(relx=0.45, rely=0.67)
        forgot_label.bind("<Button-1>", lambda e: self.show_forgot_password())
        forgot_label.bind("<Enter>", lambda e: forgot_label.config(fg="#DDA0DD"))
        forgot_label.bind("<Leave>", lambda e: forgot_label.config(fg="#C084FF"))
        
        # Right panel
        right_frame = tk.Frame(self.root, bg="#1a1a2e")
        right_frame.pack(side="right", fill="both", expand=True)
        
        tk.Label(
            right_frame, text="Start Your\nJourney Now", 
            font=("Arial", 60, "bold"), 
            bg="#1a1a2e", fg=self.COLORS['TEXT']
        ).place(relx=0.25, rely=0.25)
        
        tk.Label(
            right_frame,
            text="Track your goals, tasks, fitness, and expenses all in one place\nto stay organized and achieve more every day.",
            font=("Arial", 18), bg="#1a1a2e", 
            fg=self.COLORS['TEXT'], justify="center"
        ).place(relx=0.1, rely=0.50)
        
        # Register button
        register_btn = AnimatedButton(
            right_frame, 
            "Register", 
            self.on_register_click,
            bg_color=self.COLORS['ACCENT']
        )
        register_btn.place(relx=0.35, rely=0.6)
    
    def toggle_password(self):
        """Toggle password visibility"""
        self.show_password[0] = not self.show_password[0]
        self.login_password.config(show="" if self.show_password[0] else "*")
    
    def handle_login(self):
        """Handle login button click"""
        email = self.login_email.get().strip().lower()
        password = self.login_password.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter all fields")
            return
        
        # Validate user credentials
        stored_name, status = self.db_manager.validate_user(email, password)
        
        if status == "not_found":
            messagebox.showerror(
                "Login Failed",
                "❌ No account found with this email!\n\nPlease REGISTER first to create an account."
            )
            return
        elif status == "wrong_password":
            messagebox.showerror(
                "Login Failed", 
                "❌ Incorrect password!\n\nPlease try again or reset your password."
            )
            return
        elif status == "success":
            self.current_user_email = email
            messagebox.showinfo("Success", f"✅ Welcome back, {stored_name}!")
            self.on_login_success(stored_name)
    
    def show_forgot_password(self):
        """Show forgot password dialog"""
        ForgotPasswordDialog(self.root, self.db_manager)