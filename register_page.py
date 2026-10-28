"""
Registration page for CABUS application
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
except ImportError as e:
    print(f"Error importing modules in register_page.py: {e}")
    print("Please ensure base_page.py and ui_components.py are in the same directory")
    sys.exit(1)


class RegisterPage(BasePage):
    """Registration page for new users"""
    
    def __init__(self, root, db_manager, on_back_to_login):
        super().__init__(root, root)
        self.db_manager = db_manager
        self.on_back_to_login = on_back_to_login
        self.show_password = [False]
        self.show_confirm_password = [False]
    
    def show(self):
        """Display the registration page"""
        self.clear_content()
        self.root.configure(bg=self.COLORS['BG'])
        
        # Title bar
        TitleBar(self.root, self.root)
        
        # Left panel - Registration form
        left_frame = tk.Frame(self.root, bg="#0A0A12")
        left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            left_frame, text="Register Here", 
            font=("Arial", 65, "bold"),
            bg="#0A0A12", fg="#C084FF"
        ).place(relx=0.2, rely=0.1)
        
        # Email field
        tk.Label(
            left_frame, text="Email", 
            bg="#0A0A12", fg=self.COLORS['TEXT'], 
            font=("Arial", 20)
        ).place(relx=0.1, rely=0.3)
        
        self.register_email = tk.Entry(
            left_frame, width=30, bd=0, 
            font=("Arial", 30),
            fg=self.COLORS['ACCENT'], 
            bg=self.COLORS['BG'],
            insertbackground=self.COLORS['ACCENT'],
            highlightbackground=self.COLORS['ACCENT'],
            highlightthickness=1, relief="flat"
        )
        self.register_email.place(relx=0.1, rely=0.35)
        
        # Password field
        tk.Label(
            left_frame, text="Password", 
            bg="#0A0A12", fg=self.COLORS['TEXT'], 
            font=("Arial", 20)
        ).place(relx=0.1, rely=0.45)
        
        self.register_password = tk.Entry(
            left_frame, width=30, bd=0, show="*", 
            font=("Arial", 30),
            fg=self.COLORS['ACCENT'], 
            bg=self.COLORS['BG'],
            insertbackground=self.COLORS['ACCENT'],
            highlightbackground=self.COLORS['ACCENT'],
            highlightthickness=1, relief="flat"
        )
        self.register_password.place(relx=0.1, rely=0.50)
        
        # Eye button for password
        eye_btn = tk.Button(
            left_frame, text="👁", font=("Arial", 16),
            bg=self.COLORS['BG'], fg="#888888",
            bd=0, cursor="hand2", relief="flat",
            activebackground=self.COLORS['BG'],
            activeforeground=self.COLORS['ACCENT'],
            highlightthickness=0,
            command=self.toggle_password
        )
        eye_btn.place(relx=0.88, rely=0.51)
        
        # Add hover effects to eye button
        eye_btn.bind("<Enter>", lambda e: eye_btn.config(fg="#C084FF"))
        eye_btn.bind("<Leave>", lambda e: eye_btn.config(fg="#888888"))
        
        # Confirm Password field
        tk.Label(
            left_frame, text="Confirm Password", 
            bg="#0A0A12", fg=self.COLORS['TEXT'], 
            font=("Arial", 20)
        ).place(relx=0.1, rely=0.60)
        
        self.register_confirm_password = tk.Entry(
            left_frame, width=30, bd=0, show="*", 
            font=("Arial", 30),
            fg=self.COLORS['ACCENT'], 
            bg=self.COLORS['BG'],
            insertbackground=self.COLORS['ACCENT'],
            highlightbackground=self.COLORS['ACCENT'],
            highlightthickness=1, relief="flat"
        )
        self.register_confirm_password.place(relx=0.1, rely=0.65)
        
        # Eye button for confirm password
        eye_btn_confirm = tk.Button(
            left_frame, text="👁", font=("Arial", 16),
            bg=self.COLORS['BG'], fg="#888888",
            bd=0, cursor="hand2", relief="flat",
            activebackground=self.COLORS['BG'],
            activeforeground=self.COLORS['ACCENT'],
            highlightthickness=0,
            command=self.toggle_confirm_password
        )
        eye_btn_confirm.place(relx=0.88, rely=0.66)
        
        # Add hover effects to confirm eye button
        eye_btn_confirm.bind("<Enter>", lambda e: eye_btn_confirm.config(fg="#C084FF"))
        eye_btn_confirm.bind("<Leave>", lambda e: eye_btn_confirm.config(fg="#888888"))
        
        # Register button
        register_btn = AnimatedButton(
            left_frame, 
            "Register", 
            self.handle_register,
            bg_color=self.COLORS['ACCENT']
        )
        register_btn.place(relx=0.35, rely=0.78)
        
        # Right panel
        right_frame = tk.Frame(self.root, bg="#1a1a2e")
        right_frame.pack(side="right", fill="both", expand=True)
        
        tk.Label(
            right_frame, text="Don't have an\n account?\n Register now!", 
            font=("Arial", 50, "bold"),
            bg="#1a1a2e", fg=self.COLORS['TEXT']
        ).place(relx=0.25, rely=0.25)
        
        tk.Label(
            right_frame,
            text="Join now and take control of your goals, tasks, fitness, and \nexpenses all in one place!",
            font=("Arial", 18), bg="#1a1a2e", 
            fg=self.COLORS['TEXT'], justify="center"
        ).place(relx=0.1, rely=0.55)
        
        # Back to Login button
        back_btn = AnimatedButton(
            right_frame, 
            "Back to Login", 
            self.on_back_to_login,
            bg_color=self.COLORS['ACCENT']
        )
        back_btn.place(relx=0.35, rely=0.63)
    
    def toggle_password(self):
        """Toggle password visibility"""
        self.show_password[0] = not self.show_password[0]
        self.register_password.config(show="" if self.show_password[0] else "*")
    
    def toggle_confirm_password(self):
        """Toggle confirm password visibility"""
        self.show_confirm_password[0] = not self.show_confirm_password[0]
        self.register_confirm_password.config(show="" if self.show_confirm_password[0] else "*")
    
    def handle_register(self):
        """Handle registration button click"""
        email = self.register_email.get().strip().lower()
        password = self.register_password.get().strip()
        confirm_password = self.register_confirm_password.get().strip()
        
        if not email or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        
        if self.db_manager.email_exists(email):
            messagebox.showerror(
                "Error", 
                "This email is already registered!\nPlease use a different email or login."
            )
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        # Extract name from email (before @)
        name = email.split('@')[0].capitalize()
        
        # Save user to database
        if self.db_manager.save_user(name, email, password):
            messagebox.showinfo(
                "Success",
                f"Registration Successful!\nWelcome, {name}!\n\nYou can now login with your credentials."
            )
            self.on_back_to_login()
        else:
            messagebox.showerror("Error", "Registration failed. Please try again.")