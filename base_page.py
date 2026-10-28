# base_page.py
"""
Base page class that all pages inherit from
Provides common functionality and structure
"""

import tkinter as tk
from config import COLORS


class BasePage:
    """Base class for all pages in the application"""
    
    def __init__(self, root, main_content, user_name=None):
        self.root = root
        self.main_content = main_content
        self.user_name = user_name
        self.COLORS = COLORS
    
    def clear_content(self):
        """Clear all widgets from main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show(self):
        """Display the page - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement show() method")
    
    def create_header(self, title, emoji=""):
        """Create a page header with title"""
        header_frame = tk.Frame(self.main_content, bg=self.COLORS['DARK_BG'])
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_frame = tk.Frame(header_frame, bg=self.COLORS['DARK_BG'])
        title_frame.pack(side="left")
        
        if emoji:
            tk.Label(
                title_frame, text=emoji, 
                font=("Arial", 32), 
                bg=self.COLORS['DARK_BG']
            ).pack(side="left", padx=(0, 10))
        
        tk.Label(
            title_frame, text=title, 
            font=("Arial", 32, "bold"),
            bg=self.COLORS['DARK_BG'], 
            fg=self.COLORS['TEXT']
        ).pack(side="left")
        
        return header_frame
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame"""
        canvas = tk.Canvas(parent, bg=self.COLORS['DARK_BG'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['DARK_BG'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return canvas, scrollable_frame