# ui_components.py
"""
Reusable UI components for CABUS application
Contains common widgets and dialogs used across different pages
"""

import tkinter as tk
from tkinter import messagebox
from config import COLORS


class AnimatedButton:
    """Creates an animated button with hover effects"""
    
    def __init__(self, parent, text, command, width=300, height=50, 
                 bg_color=COLORS['ACCENT'], text_color=COLORS['TEXT']):
        self.canvas = tk.Canvas(parent, width=width, height=height, 
                               bg=bg_color, highlightthickness=0)
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.command = command
        
        self.text_id = self.canvas.create_text(
            width/2, height/2, text=text, 
            font=("Arial", 20, "bold"), fill=text_color
        )
        
        self.fill_rect = None
        self.glow_id = None
        self.animating = False
        
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)
    
    def animate_fill(self, current_width):
        if self.animating and current_width <= self.width:
            self.canvas.coords(self.fill_rect, 0, 0, current_width, self.height)
            self.canvas.after(10, self.animate_fill, current_width + 15)
        elif current_width > self.width:
            self.animating = False
    
    def on_enter(self, event):
        if not self.fill_rect:
            self.fill_rect = self.canvas.create_rectangle(
                0, 0, 0, self.height, fill="#2A264D", outline=""
            )
            self.glow_id = self.canvas.create_rectangle(
                0, 0, self.width, self.height, outline="#DDA0DD", width=3
            )
            self.canvas.tag_lower(self.glow_id, self.text_id)
            self.canvas.tag_lower(self.fill_rect, self.text_id)
            self.animating = True
            self.animate_fill(0)
    
    def on_leave(self, event):
        self.animating = False
        if self.fill_rect:
            self.canvas.delete(self.fill_rect)
            self.canvas.delete(self.glow_id)
            self.fill_rect = None
            self.glow_id = None
    
    def on_click(self, event):
        if self.command:
            self.command()
    
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
    
    def place(self, **kwargs):
        self.canvas.place(**kwargs)
    
    def grid(self, **kwargs):
        self.canvas.grid(**kwargs)


class TitleBar:
    """Creates a custom title bar with close and minimize buttons"""
    
    def __init__(self, parent, root, bg_color=COLORS['DARK_BG']):
        self.frame = tk.Frame(parent, bg=bg_color, height=40)
        self.frame.pack(fill=tk.X, side=tk.TOP)
        
        tk.Button(
            self.frame, text='✕', bg=bg_color, fg=COLORS['ACCENT_LIGHT'], 
            bd=0, activebackground=COLORS['ACCENT'], 
            font=("Arial", 12, "bold"), command=root.destroy
        ).pack(side=tk.RIGHT, padx=10, pady=5)
        
        tk.Button(
            self.frame, text='—', bg=bg_color, fg=COLORS['ACCENT_LIGHT'], 
            bd=0, activebackground=COLORS['ACCENT'], 
            font=("Arial", 12, "bold"), command=lambda: root.iconify()
        ).pack(side=tk.RIGHT, padx=10, pady=5)


class FormDialog:
    """Base class for creating form dialogs"""
    
    def __init__(self, parent, title, width=550, height=400):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.configure(bg=COLORS['CARD'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def add_title(self, text, emoji=""):
        title_text = f"{emoji} {text}" if emoji else text
        tk.Label(
            self.dialog, text=title_text, 
            font=("Arial", 24, "bold"),
            bg=COLORS['CARD'], fg=COLORS['ACCENT_LIGHT']
        ).pack(pady=(30, 10))
    
    def add_subtitle(self, text):
        tk.Label(
            self.dialog, text=text,
            font=("Arial", 12), 
            bg=COLORS['CARD'], fg=COLORS['SECONDARY_TEXT']
        ).pack(pady=(0, 30))
    
    def add_input_field(self, label_text, show=None):
        tk.Label(
            self.dialog, text=label_text, 
            font=("Arial", 11),
            bg=COLORS['CARD'], fg=COLORS['TEXT']
        ).pack(pady=(0, 10))
        
        entry = tk.Entry(
            self.dialog, font=("Arial", 14), 
            bg="#4a5568", fg=COLORS['TEXT'], 
            insertbackground=COLORS['ACCENT'], 
            bd=0, justify="center", show=show
        )
        entry.pack(fill="x", padx=60, ipady=12, pady=(0, 20))
        return entry
    
    def add_error_label(self):
        error_label = tk.Label(
            self.dialog, text="", 
            font=("Arial", 9),
            bg=COLORS['CARD'], fg="#ef4444"
        )
        error_label.pack(pady=5)
        return error_label
    
    def add_button_frame(self):
        btn_frame = tk.Frame(self.dialog, bg=COLORS['CARD'])
        btn_frame.pack(fill="x", padx=60, pady=20)
        return btn_frame
    
    def destroy(self):
        self.dialog.destroy()


class Card:
    """Creates a card component for displaying information"""
    
    def __init__(self, parent, title, value, color, has_edit=False, edit_command=None):
        self.frame = tk.Frame(parent, bg="#2d3748", relief="groove", bd=2)
        self.frame.pack(side="left", fill="both", expand=True, padx=5)
        
        inner = tk.Frame(self.frame, bg="#2d3748")
        inner.pack(fill="both", padx=15, pady=15)
        
        header = tk.Frame(inner, bg="#2d3748")
        header.pack(fill="x")
        
        tk.Label(
            header, text=title, 
            font=("Arial", 10), 
            bg="#2d3748", fg=COLORS['SECONDARY_TEXT']
        ).pack(side="left")
        
        if has_edit and edit_command:
            edit_btn = tk.Label(
                header, text="Edit", 
                font=("Arial", 9), 
                bg="#2d3748", fg=COLORS['ACCENT_LIGHT'], 
                cursor="hand2"
            )
            edit_btn.pack(side="right")
            edit_btn.bind("<Button-1>", lambda e: edit_command())
        
        tk.Label(
            inner, text=value, 
            font=("Arial", 24, "bold"),
            bg="#2d3748", fg=color, anchor="w"
        ).pack(fill="x", pady=(5, 0))


class ProgressBar:
    """Creates a progress bar component"""
    
    def __init__(self, parent, label, percentage, color):
        frame = tk.Frame(parent, bg="#2d3748")
        frame.pack(fill="x", pady=(0, 12))
        
        tk.Label(
            frame, text=f"{label}: {percentage:.1f}%",
            font=("Arial", 11, "bold"), 
            bg="#2d3748", fg="#374151"
        ).pack(anchor="w", pady=(0, 5))
        
        self.canvas = tk.Canvas(frame, height=16, bg="#4a5568", highlightthickness=0)
        self.canvas.pack(fill="x")
        
        self.percentage = percentage
        self.color = color
        
        self.canvas.after(100, self.draw)
    
    def draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        if w > 1:
            fill = min(w * self.percentage / 100, w)
            self.canvas.create_rectangle(0, 0, fill, 16, fill=self.color, outline="")