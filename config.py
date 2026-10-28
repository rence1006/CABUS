# config.py
"""
Configuration module for CABUS application
Contains all constants, color schemes, and database configuration
"""

import os

# Color scheme
COLORS = {
    'DARK_BG': '#0A0A12',
    'CARD': '#1a1a2e',
    'TEXT': '#ffffff',
    'ACCENT': '#6C63FF',
    'ACCENT_LIGHT': '#C084FF',
    'BG': '#16213e',
    'SECONDARY_TEXT': '#a0a0a0'
}

# Database configuration
DB_CONFIG = {
    'host': os.getenv('CABUS_DB_HOST', 'localhost'),
    'user': os.getenv('CABUS_DB_USER', 'root'),
    'password': os.getenv('CABUS_DB_PASSWORD', ''),
    'database': os.getenv('CABUS_DB_NAME', 'user_management')
}

# File paths
DATA_FILES = {
    'goals': 'goals.json',
    'fitness': 'fitness_tracker_data.json',
    'expenses': 'expenses_data.json'
}

# Category configurations
EXPENSE_CATEGORIES = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Health', 'Other']
TASK_CATEGORIES = ['Work', 'Personal', 'Shopping', 'Health', 'Study']
TASK_PRIORITIES = ['Low', 'Medium', 'High']
TASK_STATUSES = ['Pending', 'In Progress', 'Completed']

# Category colors and emojis
CATEGORY_COLORS = {
    'Food': '#a855f7',
    'Transport': '#3b82f6',
    'Shopping': '#ec4899',
    'Entertainment': '#6366f1',
    'Bills': '#ef4444',
    'Health': '#22c55e',
    'Other': '#6b7280'
}

CATEGORY_EMOJIS = {
    'Food': '🍔',
    'Transport': '🚗',
    'Shopping': '🛍️',
    'Entertainment': '🎬',
    'Bills': '📄',
    'Health': '💊',
    'Other': '❓'
}

# Priority colors
PRIORITY_COLORS = {
    "High": "#ff4444",
    "Medium": "#ffcc00",
    "Low": "#52BE80"
}

# Window configuration
WINDOW_CONFIG = {
    'title': 'CABUS - Personal Management System',
    'fullscreen': True
}
