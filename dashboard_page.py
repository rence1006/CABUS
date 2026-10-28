# dashboard_page.py
"""
Main dashboard page that contains navigation to all features
"""

import tkinter as tk
from tkinter import font as tkfont
import math
from base_page import BasePage
from ui_components import TitleBar
from goals_page import GoalsPage
from tasks_page import TasksPage
from expense_page import ExpensePage
from fitness_page import FitnessPage


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Create a rounded rectangle on a canvas"""
    points = [x1 + radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def create_pill_button_with_glow(parent, text, command):
    """Create pill-shaped button with glow effect - consistent sizing"""
    # Fixed dimensions for all buttons
    width = 140
    height = 50
    radius = height // 2

    container = tk.Frame(parent, bg=parent.cget('bg'))

    canvas = tk.Canvas(container, width=width + 16, height=height + 16,
                       bg=parent.cget('bg'), highlightthickness=0)
    canvas.pack()

    # Glow layers (hidden initially)
    glow_outer = create_rounded_rect(canvas, 4, 4, width + 12, height + 12,
                                     radius=radius + 6, fill="", outline="", width=0)
    glow_mid = create_rounded_rect(canvas, 6, 6, width + 10, height + 10,
                                   radius=radius + 4, fill="", outline="", width=0)

    # Main button
    bg = create_rounded_rect(canvas, 8, 8, width + 8, height + 8,
                             radius=radius, fill="#1a1a3e",
                             outline="#6C63FF", width=1)

    txt = canvas.create_text(width // 2 + 8, height // 2 + 8, text=text,
                             font=("Verdana", 14, "bold"),
                             fill="#a99cde")

    def on_enter(e):
        canvas.itemconfig(glow_outer, outline="#6C63FF", width=3)
        canvas.itemconfig(glow_mid, outline="#9370DB", width=2)
        canvas.itemconfig(bg, fill="#2a2a4e", outline="#C084FF", width=2)
        canvas.itemconfig(txt, fill="#FFFFFF")
        canvas.config(cursor="hand2")

    def on_leave(e):
        canvas.itemconfig(glow_outer, outline="", width=0)
        canvas.itemconfig(glow_mid, outline="", width=0)
        canvas.itemconfig(bg, fill="#1a1a3e", outline="#6C63FF", width=1)
        canvas.itemconfig(txt, fill="#a99cde")

    def on_click(e):
        canvas.itemconfig(bg, fill="#3a3a5e")
        canvas.after(100, lambda: canvas.itemconfig(bg, fill="#2a2a4e"))
        command()

    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Button-1>", on_click)

    return container


class DashboardPage(BasePage):
    """Main dashboard with navigation sidebar and animated home page"""
    
    def __init__(self, root, user_name, goal_manager, task_manager, 
                 expense_manager, fitness_manager, on_logout):
        super().__init__(root, None, user_name)
        self.goal_manager = goal_manager
        self.task_manager = task_manager
        self.expense_manager = expense_manager
        self.fitness_manager = fitness_manager
        self.on_logout = on_logout
        
        # Current page
        self.current_page = None
        
        # Animation variables
        self.glow_alpha = 0.5
        self.glow_direction = 1
        self.beam_y = 0
        self.orb1_offset = 0
        self.orb2_offset = 0
        self.animation_id = None
        self.canvas = None
    
    def show(self):
        """Display the dashboard"""
        # Clear everything
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg=self.COLORS['DARK_BG'])
        
        # Title bar
        TitleBar(self.root, self.root)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content area
        self.main_content = tk.Frame(self.root, bg=self.COLORS['DARK_BG'])
        self.main_content.pack(side="bottom", fill="both", expand=True)
        
        # Show default page
        self.show_home()
    
    def create_sidebar(self):
        """Create navigation sidebar with rounded design and pill buttons"""
        # Container for sidebar with padding - positioned directly below title bar
        sidebar_outer = tk.Frame(self.root, bg=self.COLORS['DARK_BG'], height=80)
        sidebar_outer.pack(side="top", fill="x", padx=40, pady=(0, 10))
        sidebar_outer.pack_propagate(False)

        # Create rounded sidebar using canvas
        sidebar_canvas = tk.Canvas(sidebar_outer, bg=self.COLORS['DARK_BG'], highlightthickness=0)
        sidebar_canvas.pack(fill="both", expand=True)

        # Inner frame for content
        sidebar = tk.Frame(sidebar_canvas, bg="#0f0f23")

        # Draw rounded rectangle background
        def draw_rounded_sidebar():
            sidebar_canvas.delete("bg")
            width = sidebar_canvas.winfo_width()
            height = sidebar_canvas.winfo_height()
            if width > 1 and height > 1:
                create_rounded_rect(sidebar_canvas, 0, 0, width, height,
                                    radius=40, fill="#0f0f23", 
                                    outline=self.COLORS['ACCENT'], width=2, tags="bg")
                sidebar_canvas.tag_lower("bg")

        # Create window and update function
        sidebar_window = sidebar_canvas.create_window(0, 0, window=sidebar, anchor="nw", tags="content")

        def update_sidebar_size(event=None):
            width = sidebar_canvas.winfo_width()
            height = sidebar_canvas.winfo_height()
            sidebar_canvas.itemconfig(sidebar_window, width=width, height=height)
            sidebar.config(width=width, height=height)
            draw_rounded_sidebar()

        sidebar_canvas.bind("<Configure>", update_sidebar_size)
        sidebar_canvas.after(100, update_sidebar_size)

        # Left: CABUS logo
        menu_frame = tk.Frame(sidebar, bg="#0f0f23")
        menu_frame.pack(side="left", padx=20, pady=15)
        tk.Label(menu_frame, text="CABUS", font=("Verdana", 18, "italic"),
                 bg="#0f0f23", fg=self.COLORS['ACCENT_LIGHT']).pack()

        # Center: Navigation buttons container with improved layout
        button_container = tk.Frame(sidebar, bg="#0f0f23")
        button_container.pack(side="left", fill="both", expand=True)
        
        # Create inner frame to center buttons vertically
        inner_button_frame = tk.Frame(button_container, bg="#0f0f23")
        inner_button_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Menu items with pill buttons
        menu_items = [
            ("Dashboard", self.show_home),
            ("Goals", self.show_goals),
            ("Tasks", self.show_tasks),
            ("Fitness", self.show_fitness),
            ("Expense", self.show_expense),
        ]
        
        # Create buttons with consistent spacing
        for text, cmd in menu_items:
            pill_btn = create_pill_button_with_glow(inner_button_frame, text, cmd)
            pill_btn.pack(side="left", padx=10, pady=0)

        # Right: Logout button
        logout_frame = tk.Frame(sidebar, bg="#0f0f23")
        logout_frame.pack(side="right", padx=20, pady=15)

        # Create rounded logout button with custom styling
        logout_canvas = tk.Canvas(logout_frame, width=180, height=50,
                                  bg="#0f0f23", highlightthickness=0)
        logout_canvas.pack()

        # Glow layers
        logout_glow1 = create_rounded_rect(logout_canvas, 2, 2, 178, 48,
                                           radius=24, fill="", outline="", width=0)
        logout_glow2 = create_rounded_rect(logout_canvas, 4, 4, 176, 46,
                                           radius=22, fill="", outline="", width=0)

        # Main logout button
        logout_bg = create_rounded_rect(logout_canvas, 6, 6, 174, 44,
                                        radius=20, fill="#f5f5f5", outline="#e0e0e0", width=1)
        logout_txt = logout_canvas.create_text(90, 25, text="🚪 Logout",
                                               font=("Arial", 14, "bold"),
                                               fill="#333333")

        def logout_hover_enter(e):
            logout_canvas.itemconfig(logout_glow1, outline="#d0d0d0", width=2)
            logout_canvas.itemconfig(logout_glow2, outline="#e5e5e5", width=1)
            logout_canvas.itemconfig(logout_bg, fill="#ffffff")
            logout_canvas.config(cursor="hand2")

        def logout_hover_leave(e):
            logout_canvas.itemconfig(logout_glow1, outline="", width=0)
            logout_canvas.itemconfig(logout_glow2, outline="", width=0)
            logout_canvas.itemconfig(logout_bg, fill="#f5f5f5")

        def logout_click(e):
            logout_canvas.itemconfig(logout_bg, fill="#e5e5e5")
            logout_canvas.after(100, lambda: logout_canvas.itemconfig(logout_bg, fill="#ffffff"))
            self.on_logout()

        logout_canvas.bind("<Enter>", logout_hover_enter)
        logout_canvas.bind("<Leave>", logout_hover_leave)
        logout_canvas.bind("<Button-1>", logout_click)
    
    def blend_color(self, hex_color, alpha):
        """Convert hex to RGB and blend with background"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        bg_r, bg_g, bg_b = 10, 10, 18
        factor = alpha / 255
        
        final_r = int(bg_r + (r - bg_r) * factor)
        final_g = int(bg_g + (g - bg_g) * factor)
        final_b = int(bg_b + (b - bg_b) * factor)
        
        return f"#{final_r:02x}{final_g:02x}{final_b:02x}"
    
    def draw_dashboard(self):
        """Draw the animated dashboard content"""
        if not self.canvas or not self.canvas.winfo_exists():
            return
            
        self.canvas.delete("all")
        width = self.canvas.winfo_width() or 1400
        height = self.canvas.winfo_height() or 820
        center_x = width // 2
        center_y = height // 2 - 50
        
        # Draw glowing orbs
        x_offset1 = math.sin(self.orb1_offset) * 20
        y_offset1 = math.cos(self.orb1_offset) * 20
        orb1_x = center_x - 300
        orb1_y = center_y - 150
        
        for i in range(5, 0, -1):
            alpha = int(100 / i)
            color = self.blend_color("#9370DB", alpha)
            radius = 200 * i / 5
            self.canvas.create_oval(
                orb1_x + x_offset1 - radius, orb1_y + y_offset1 - radius,
                orb1_x + x_offset1 + radius, orb1_y + y_offset1 + radius,
                fill=color, outline=""
            )
        
        x_offset2 = math.sin(self.orb2_offset) * 20
        y_offset2 = math.cos(self.orb2_offset) * 20
        orb2_x = center_x + 300
        orb2_y = center_y + 100
        
        for i in range(5, 0, -1):
            alpha = int(100 / i)
            color = self.blend_color("#BA55D3", alpha)
            radius = 150 * i / 5
            self.canvas.create_oval(
                orb2_x + x_offset2 - radius, orb2_y + y_offset2 - radius,
                orb2_x + x_offset2 + radius, orb2_y + y_offset2 + radius,
                fill=color, outline=""
            )
        
        # Draw CABUS logo with glow effect
        logo_font = tkfont.Font(family="Arial", size=100, weight="bold")
        
        for offset in range(3, 0, -1):
            glow_alpha_val = int(100 * self.glow_alpha / offset)
            glow_color = self.blend_color("#9370DB", glow_alpha_val)
            
            for dx, dy in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
                self.canvas.create_text(
                    center_x + dx, center_y + dy,
                    text="CABUS", font=logo_font,
                    fill=glow_color
                )
        
        self.canvas.create_text(center_x, center_y, text="CABUS", font=logo_font, fill="white")
        
        # Welcome text
        welcome_font = tkfont.Font(family="Arial", size=28)
        self.canvas.create_text(
            center_x, center_y + 180,
            text=f"Welcome to CABUS, {self.user_name}!",
            font=welcome_font, fill="white"
        )
        
        # Subtitle
        subtitle_font = tkfont.Font(family="Arial", size=16)
        self.canvas.create_text(
            center_x, center_y + 220,
            text="Your goals, tasks, fitness, and expenses all in one place",
            font=subtitle_font, fill="#9370DB"
        )
    
    def animate(self):
        """Animation loop for dashboard effects"""
        if not self.canvas or not self.canvas.winfo_exists():
            return
            
        self.glow_alpha += 0.02 * self.glow_direction
        if self.glow_alpha >= 1 or self.glow_alpha <= 0.3:
            self.glow_direction *= -1
        
        self.beam_y += 2
        self.orb1_offset += 0.02
        self.orb2_offset += 0.03
        
        self.draw_dashboard()
        self.animation_id = self.canvas.after(30, self.animate)
    
    def stop_animation(self):
        """Stop the animation loop"""
        if self.animation_id:
            try:
                self.canvas.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None
    
    def show_home(self):
        """Show animated home/welcome page"""
        self.stop_animation()
        
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        self.main_content.configure(bg=self.COLORS['DARK_BG'])
        
        # Create canvas for animations
        self.canvas = tk.Canvas(self.main_content, bg=self.COLORS['DARK_BG'], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Start animation after a short delay
        self.canvas.after(100, self.animate)
    
    def show_goals(self):
        """Show goals page"""
        self.stop_animation()
        page = GoalsPage(self.root, self.main_content, self.user_name, self.goal_manager)
        page.show()
    
    def show_tasks(self):
        """Show tasks page"""
        self.stop_animation()
        page = TasksPage(self.root, self.main_content, self.user_name, self.task_manager)
        page.show()
    
    def show_expense(self):
        """Show expense page"""
        self.stop_animation()
        page = ExpensePage(self.root, self.main_content, self.user_name, self.expense_manager)
        page.show()
    
    def show_fitness(self):
        """Show fitness page"""
        self.stop_animation()
        page = FitnessPage(self.root, self.main_content, self.user_name, self.fitness_manager)
        page.show()