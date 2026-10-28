# dialogs.py
"""
Dialog windows for CABUS application
"""

import math
import tkinter as tk
from tkinter import messagebox
from ui_components import FormDialog
from config import COLORS


class ForgotPasswordDialog:
    """Dialog for resetting forgotten password"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.dialog = FormDialog(parent, "Reset Password")
        
        self.dialog.add_title("Reset Password", "🔐")
        self.dialog.add_subtitle("Enter your email and new password")
        
        # Email field
        self.email_entry = self.dialog.add_input_field("Email Address")
        self.email_entry.focus()
        
        # New password field
        self.password_entry = self.dialog.add_input_field("New Password", show="*")
        
        # Confirm password field
        self.confirm_entry = self.dialog.add_input_field("Confirm New Password", show="*")
        
        # Error label
        self.error_label = self.dialog.add_error_label()
        
        # Buttons
        btn_frame = self.dialog.add_button_frame()
        
        tk.Button(
            btn_frame, text="Reset Password", 
            font=("Arial", 12, "bold"),
            bg=COLORS['ACCENT'], fg=COLORS['TEXT'], 
            cursor="hand2", bd=0, relief="flat",
            command=self.reset_password
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(
            btn_frame, text="Cancel", 
            font=("Arial", 12, "bold"),
            bg="#6b7280", fg=COLORS['TEXT'], 
            cursor="hand2", bd=0, relief="flat",
            command=self.dialog.destroy
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Bind Enter keys
        self.password_entry.bind("<Return>", lambda e: self.confirm_entry.focus())
        self.confirm_entry.bind("<Return>", lambda e: self.reset_password())
    
    def reset_password(self):
        """Handle password reset"""
        email = self.email_entry.get().strip().lower()
        new_password = self.password_entry.get().strip()
        confirm_password = self.confirm_entry.get().strip()
        
        # Validation
        if not email or not new_password or not confirm_password:
            self.error_label.config(text="Please fill all fields")
            return
        
        if "@" not in email or "." not in email:
            self.error_label.config(text="Please enter a valid email address")
            return
        
        if len(new_password) < 6:
            self.error_label.config(text="Password must be at least 6 characters")
            return
        
        if new_password != confirm_password:
            self.error_label.config(text="Passwords do not match")
            return
        
        # Reset password
        success, status = self.db_manager.reset_password(email, new_password)
        
        if status == "not_found":
            self.error_label.config(text="No account found with this email")
            return
        elif status == "success":
            messagebox.showinfo(
                "Success",
                "✅ Password reset successful!\n\nYou can now login with your new password."
            )
            self.dialog.destroy()
        else:
            self.error_label.config(text="Failed to reset password. Try again.")


class BudgetSetupDialog:
    """Dialog for setting up initial budget"""
    
    def __init__(self, parent, expense_manager, on_complete):
        self.expense_manager = expense_manager
        self.on_complete = on_complete
        
        self.dialog = FormDialog(parent, "Welcome to Expense Tracker", 550, 350)
        
        # Prevent closing
        self.dialog.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.dialog.add_title("Welcome!", "💰")
        self.dialog.add_subtitle("Let's start by setting your monthly budget")
        
        # Budget input
        self.budget_entry = self.dialog.add_input_field("Enter Your Monthly Budget (₱)")
        self.budget_entry.focus()
        
        self.error_label = self.dialog.add_error_label()
        
        # Save button
        tk.Button(
            self.dialog.dialog, text="Start Tracking", 
            font=("Arial", 12, "bold"),
            bg=COLORS['ACCENT'], fg=COLORS['TEXT'], 
            cursor="hand2", bd=0, relief="flat",
            command=self.save_budget
        ).pack(fill="x", padx=60, pady=10)
        
        self.budget_entry.bind("<Return>", lambda e: self.save_budget())
    
    def save_budget(self):
        """Save the budget and close dialog"""
        try:
            budget = float(self.budget_entry.get())
            if math.isfinite(budget) and round(budget, 2) > 0:
                self.expense_manager.set_budget(budget)
                self.dialog.destroy()
                self.on_complete()
            else:
                self.error_label.config(text="Budget must be greater than 0")
        except ValueError:
            self.error_label.config(text="Please enter a valid number")


class EditBudgetDialog:
    """Dialog for editing existing budget"""
    
    def __init__(self, parent, expense_manager, on_complete):
        self.expense_manager = expense_manager
        self.on_complete = on_complete
        
        self.dialog = FormDialog(parent, "Edit Budget", 550, 350)
        
        self.dialog.add_title("Edit Budget", "📝")
        self.dialog.add_subtitle("Update your monthly budget")
        
        # Budget input with current value
        self.budget_entry = self.dialog.add_input_field("New Monthly Budget (₱)")
        self.budget_entry.insert(0, str(self.expense_manager.budget["amount"]))
        self.budget_entry.focus()
        self.budget_entry.select_range(0, tk.END)
        
        self.error_label = self.dialog.add_error_label()
        
        # Buttons
        btn_frame = self.dialog.add_button_frame()
        
        tk.Button(
            btn_frame, text="Update Budget", 
            font=("Arial", 12, "bold"),
            bg=COLORS['ACCENT'], fg=COLORS['TEXT'], 
            cursor="hand2", bd=0, relief="flat",
            command=self.save_budget
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(
            btn_frame, text="Cancel", 
            font=("Arial", 12, "bold"),
            bg="#6b7280", fg=COLORS['TEXT'], 
            cursor="hand2", bd=0, relief="flat",
            command=self.dialog.destroy
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        self.budget_entry.bind("<Return>", lambda e: self.save_budget())
    
    def save_budget(self):
        """Update the budget"""
        try:
            budget = float(self.budget_entry.get())
            if math.isfinite(budget) and round(budget, 2) > 0:
                self.expense_manager.set_budget(budget)
                self.dialog.destroy()
                self.on_complete()
            else:
                self.error_label.config(text="Budget must be greater than 0")
        except ValueError:
            self.error_label.config(text="Please enter a valid number")
