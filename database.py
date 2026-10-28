# database.py
"""
Database management module for CABUS application
Handles all database operations including user authentication and CRUD operations
"""

import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from datetime import datetime
import sys
import os

# Ensure imports work from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import DB_CONFIG
except ImportError as e:
    print(f"Error importing modules in database.py: {e}")
    print("Please ensure config.py is in the same directory")
    sys.exit(1)


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self.init_database()
    
    def get_connection(self):
        """Create and return a database connection"""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
            return None
    
    def init_database(self):
        """Initialize database and create tables"""
        try:
            # Connect without database first to create it
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password']
            )
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.close()
            conn.close()
            
            # Connect to the database and create tables
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        registered_date DATETIME NOT NULL
                    )
                ''')
                conn.commit()
                cursor.close()
                conn.close()
                return True
        except Error as e:
            messagebox.showerror("Database Error", f"Error initializing database: {e}")
            return False
    
    def save_user(self, name, email, password):
        """Save a new user to the database"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            registered_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO users (name, email, password, registered_date)
                VALUES (%s, %s, %s, %s)
            ''', (name, email, password, registered_date))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except mysql.connector.IntegrityError:
            return False
        except Error as e:
            messagebox.showerror("Database Error", f"Error saving user: {e}")
            return False
    
    def validate_user(self, email, password):
        """Validate user credentials"""
        try:
            conn = self.get_connection()
            if not conn:
                return None, "connection_error"
            
            cursor = conn.cursor()
            cursor.execute('SELECT name, password FROM users WHERE email = %s', (email,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result is None:
                return None, "not_found"
            
            name, stored_password = result
            if stored_password == password:
                return name, "success"
            else:
                return None, "wrong_password"
        except Error as e:
            messagebox.showerror("Database Error", f"Error validating user: {e}")
            return None, "error"
    
    def email_exists(self, email):
        """Check if email already exists in database"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM users WHERE email = %s', (email,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Error as e:
            messagebox.showerror("Database Error", f"Error checking email: {e}")
            return False
    
    def reset_password(self, email, new_password):
        """Reset password for a user"""
        try:
            conn = self.get_connection()
            if not conn:
                return False, "connection_error"
            
            cursor = conn.cursor()
            # Check if email exists
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            result = cursor.fetchone()
            
            if result is None:
                cursor.close()
                conn.close()
                return False, "not_found"
            
            # Update password
            cursor.execute('UPDATE users SET password = %s WHERE email = %s', 
                         (new_password, email))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "success"
        except Error as e:
            messagebox.showerror("Database Error", f"Error resetting password: {e}")
            return False, "error"