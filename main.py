# main.py
"""
Main application file for CABUS
Personal Management System - Goals, Tasks, Fitness, and Expenses Tracker
"""

import tkinter as tk
from config import COLORS, WINDOW_CONFIG
from database import DatabaseManager
from models import GoalManager, TaskManager, ExpenseManager, FitnessManager
from login_page import LoginPage
from register_page import RegisterPage
from dashboard_page import DashboardPage
from ui_components import TitleBar


class CabusApp:
    """Main application class"""
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title(WINDOW_CONFIG['title'])
        self.root.attributes('-fullscreen', WINDOW_CONFIG['fullscreen'])
        self.root.configure(bg=COLORS['DARK_BG'])
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.goal_manager = GoalManager()
        self.task_manager = TaskManager()
        self.expense_manager = ExpenseManager()
        self.fitness_manager = FitnessManager()
        
        # Current user
        self.current_user = None
        
        # Dashboard reference
        self.dashboard = None
    
    def run(self):
        """Start the application"""
        self.show_login()
        self.root.mainloop()
    
    def show_login(self):
        """Display login page"""
        login_page = LoginPage(
            self.root,
            self.db_manager,
            self.on_login_success,
            self.show_register
        )
        login_page.show()
    
    def show_register(self):
        """Display registration page"""
        register_page = RegisterPage(
            self.root,
            self.db_manager,
            self.show_login
        )
        register_page.show()
    
    def on_login_success(self, user_name):
        """Handle successful login"""
        self.current_user = user_name
        self.show_dashboard()
    
    def show_dashboard(self):
        """Display main dashboard"""
        self.dashboard = DashboardPage(
            self.root,
            self.current_user,
            self.goal_manager,
            self.task_manager,
            self.expense_manager,
            self.fitness_manager,
            self.show_login
        )
        self.dashboard.show()


if __name__ == "__main__":
    app = CabusApp()
    app.run()