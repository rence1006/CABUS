"""
Goals management page for CABUS application
Allows users to create, track, and manage short-term and long-term goals
"""

import tkinter as tk
from copy import deepcopy
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from base_page import BasePage
from models import Goal


class GoalsPage(BasePage):
    """Goals tracking and management page"""
    
    def __init__(self, root, main_content, user_name, goal_manager):
        super().__init__(root, main_content, user_name)
        self.goal_manager = goal_manager
        self.editing_goal = None
    
    def show(self):
        """Display the goals page"""
        self.clear_content()
        self.main_content.configure(bg=self.COLORS['DARK_BG'])
        
        # Header
        header_frame = tk.Frame(self.main_content, bg=self.COLORS['DARK_BG'])
        header_frame.pack(fill="x", padx=30, pady=20)
        
        title_frame = tk.Frame(header_frame, bg=self.COLORS['DARK_BG'])
        title_frame.pack(side="left")
        
        tk.Label(
            title_frame, text="Goal Tracker", 
            font=("Arial", 32, "bold"),
            bg=self.COLORS['DARK_BG'], 
            fg=self.COLORS['TEXT']
        ).pack(side="left")
        
        # Add Goal button
        add_btn = tk.Button(
            header_frame, text="+ Add Goal",
            bg=self.COLORS['ACCENT'], 
            fg="white", 
            font=("Arial", 12, "bold"),
            relief="flat", padx=25, pady=12, 
            cursor="hand2",
            activebackground=self.COLORS['ACCENT_LIGHT'],
            command=self.show_goal_form
        )
        add_btn.pack(side="right")
        
        # Main container with two columns
        columns_container = tk.Frame(self.main_content, bg=self.COLORS['DARK_BG'])
        columns_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Left column - Short-term goals
        left_column = tk.Frame(columns_container, bg=self.COLORS['DARK_BG'])
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        short_header = tk.Frame(left_column, bg="#4169E1", height=50)
        short_header.pack(fill="x")
        short_header.pack_propagate(False)
        tk.Label(
            short_header, text="🎯  Short-term Goals", 
            font=("Arial", 16, "bold"),
            bg="#4169E1", fg="white"
        ).pack(side="left", padx=20, pady=12)
        
        self.short_canvas = tk.Canvas(left_column, bg=self.COLORS['DARK_BG'], highlightthickness=0)
        short_scroll = tk.Scrollbar(left_column, orient="vertical", command=self.short_canvas.yview)
        self.short_frame = tk.Frame(self.short_canvas, bg=self.COLORS['DARK_BG'])
        
        self.short_frame.bind(
            "<Configure>",
            lambda e: self.short_canvas.configure(scrollregion=self.short_canvas.bbox("all"))
        )
        self.short_canvas.create_window((0, 0), window=self.short_frame, anchor="nw")
        self.short_canvas.configure(yscrollcommand=short_scroll.set)
        
        self.short_canvas.pack(side="left", fill="both", expand=True)
        short_scroll.pack(side="right", fill="y")
        
        # Right column - Long-term goals
        right_column = tk.Frame(columns_container, bg=self.COLORS['DARK_BG'])
        right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        long_header = tk.Frame(right_column, bg="#4169E1", height=50)
        long_header.pack(fill="x")
        long_header.pack_propagate(False)
        tk.Label(
            long_header, text="📈  Long-term Goals", 
            font=("Arial", 16, "bold"),
            bg="#4169E1", fg="white"
        ).pack(side="left", padx=20, pady=12)
        
        self.long_canvas = tk.Canvas(right_column, bg=self.COLORS['DARK_BG'], highlightthickness=0)
        long_scroll = tk.Scrollbar(right_column, orient="vertical", command=self.long_canvas.yview)
        self.long_frame = tk.Frame(self.long_canvas, bg=self.COLORS['DARK_BG'])
        
        self.long_frame.bind(
            "<Configure>",
            lambda e: self.long_canvas.configure(scrollregion=self.long_canvas.bbox("all"))
        )
        self.long_canvas.create_window((0, 0), window=self.long_frame, anchor="nw")
        self.long_canvas.configure(yscrollcommand=long_scroll.set)
        
        self.long_canvas.pack(side="left", fill="both", expand=True)
        long_scroll.pack(side="right", fill="y")
        
        self.refresh_goals()
    
    def create_goal_card(self, parent, goal):
        """Create a goal card widget"""
        card = tk.Frame(parent, bg="#1e293b", relief="solid", bd=1, width=650, height=450)
        card.pack(fill="x", pady=20, padx=15)
        card.pack_propagate(False)
        
        content_frame = tk.Frame(card, bg="#1e293b", padx=35, pady=30)
        content_frame.pack(fill="both", expand=True)
        
        # Header with title and buttons
        header_frame = tk.Frame(content_frame, bg="#1e293b")
        header_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            header_frame, text=goal.title,
            font=("Arial", 20, "bold"),
            bg="#1e293b", fg="white"
        ).pack(side="left")
        
        btn_frame = tk.Frame(header_frame, bg="#1e293b")
        btn_frame.pack(side="right")
        
        # Edit button
        edit_btn = tk.Button(
            btn_frame, text="✏️", 
            font=("Arial", 14),
            command=lambda: self.edit_goal(goal),
            bg="#3b82f6", fg="white", bd=0,
            padx=15, pady=8, relief="flat", 
            cursor="hand2"
        )
        edit_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = tk.Button(
            btn_frame, text="🗑", 
            font=("Arial", 14),
            command=lambda: self.delete_goal(goal),
            bg="#ef4444", fg="white", bd=0,
            padx=15, pady=8, relief="flat", 
            cursor="hand2"
        )
        delete_btn.pack(side="left", padx=5)
        
        # Description
        if goal.description:
            tk.Label(
                content_frame, text=goal.description,
                font=("Arial", 13), bg="#1e293b", 
                fg="#94a3b8",
                wraplength=550, justify="left"
            ).pack(anchor="w", pady=(0, 18))
        
        # Progress bar
        progress = goal.get_progress()
        progress_frame = tk.Frame(content_frame, bg="#1e293b")
        progress_frame.pack(fill="x", pady=(0, 18))
        
        tk.Label(
            progress_frame, 
            text=f"Progress: {progress}%",
            font=("Arial", 13, "bold"), 
            bg="#1e293b", fg="#e2e8f0"
        ).pack(anchor="w", pady=(0, 8))
        
        progress_bar_bg = tk.Frame(progress_frame, bg="#334155", height=12)
        progress_bar_bg.pack(fill="x")
        
        if progress > 0:
            progress_bar = tk.Frame(progress_bar_bg, bg=self.COLORS['ACCENT'], height=12)
            progress_bar.place(relwidth=progress/100, relheight=1)
        
        # Days remaining
        days = goal.get_days_remaining()
        if days < 0:
            days_text = f"⚠️ Overdue by {abs(days)} days"
            days_color = "#ef4444"
        elif days == 0:
            days_text = "⏰ Due today!"
            days_color = "#f59e0b"
        else:
            days_text = f"⏳ {days} days remaining"
            days_color = "#10b981"
        
        tk.Label(
            content_frame, text=days_text,
            font=("Arial", 13, "bold"), 
            bg="#1e293b", fg=days_color
        ).pack(anchor="w", pady=(0, 8))
        
        # Target date
        try:
            date_str = datetime.strptime(goal.target_date, '%Y-%m-%d').strftime('%B %d, %Y')
            tk.Label(
                content_frame,
                text=f"Target: {date_str}",
                font=("Arial", 12), bg="#1e293b", fg="#94a3b8"
            ).pack(anchor="w")
        except:
            pass
        
        # Milestones
        if goal.milestones:
            tk.Label(
                content_frame, text="📋 Milestones",
                font=("Arial", 14, "bold"), 
                bg="#1e293b", fg="#e2e8f0"
            ).pack(anchor="w", pady=(22, 12))
            
            for i, milestone in enumerate(goal.milestones):
                milestone_frame = tk.Frame(content_frame, bg="#1e293b")
                milestone_frame.pack(fill="x", pady=6)
                
                check_btn = tk.Button(
                    milestone_frame,
                    text="✓" if milestone.completed else "○",
                    font=("Arial", 13, "bold"),
                    command=lambda g=goal, idx=i: self.toggle_milestone(g, idx),
                    bg="#10b981" if milestone.completed else "#475569",
                    fg="white", bd=0, padx=12, pady=6,
                    relief="flat", cursor="hand2"
                )
                check_btn.pack(side="left", padx=(0, 15))
                
                milestone_text = tk.Label(
                    milestone_frame, text=milestone.text,
                    font=("Arial", 13, "overstrike" if milestone.completed else ""),
                    bg="#1e293b",
                    fg="#64748b" if milestone.completed else "#cbd5e1",
                    anchor="w"
                )
                milestone_text.pack(side="left", anchor="w", fill="x", expand=True)
    
    def show_goal_form(self):
        """Show goal creation/editing form"""
        form_window = tk.Toplevel(self.root)
        form_window.title("Add New Goal" if not self.editing_goal else "Edit Goal")
        form_window.geometry("750x800")
        form_window.configure(bg="#0f172a")
        form_window.transient(self.root)
        form_window.grab_set()
        
        form_frame = tk.Frame(form_window, bg="#1e293b", padx=40, pady=40)
        form_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Goal Title
        tk.Label(
            form_frame, text="Goal Title", 
            font=("Arial", 11, "bold"),
            bg="#1e293b", fg="#e2e8f0"
        ).pack(anchor="w", pady=(0, 8))
        
        title_entry = tk.Entry(
            form_frame, font=("Arial", 12),
            bg="#334155", fg="white",
            relief="solid", bd=1, insertbackground="white"
        )
        title_entry.pack(fill="x", pady=(0, 20), ipady=8)
        
        # Description
        tk.Label(
            form_frame, text="Description", 
            font=("Arial", 11, "bold"),
            bg="#1e293b", fg="#e2e8f0"
        ).pack(anchor="w", pady=(0, 8))
        
        desc_text = tk.Text(
            form_frame, font=("Arial", 11), 
            height=4,
            bg="#334155", fg="white",
            relief="solid", bd=1, wrap="word", insertbackground="white"
        )
        desc_text.pack(fill="x", pady=(0, 20))
        
        # Goal Type
        tk.Label(
            form_frame, text="Goal Type", 
            font=("Arial", 11, "bold"),
            bg="#1e293b", fg="#e2e8f0"
        ).pack(anchor="w", pady=(0, 8))
        
        type_var = tk.StringVar(value="short-term")
        type_frame = tk.Frame(form_frame, bg="#1e293b")
        type_frame.pack(fill="x", pady=(0, 20))
        
        tk.Radiobutton(
            type_frame, text="⏱️ Short-term", 
            variable=type_var,
            value="short-term", bg="#1e293b", 
            fg="#e2e8f0",
            font=("Arial", 11), 
            selectcolor="#334155",
            activebackground="#1e293b"
        ).pack(side="left", padx=(0, 20))
        
        tk.Radiobutton(
            type_frame, text="📈 Long-term", 
            variable=type_var,
            value="long-term", bg="#1e293b", 
            fg="#e2e8f0",
            font=("Arial", 11), 
            selectcolor="#334155",
            activebackground="#1e293b"
        ).pack(side="left")
        
        # Target Date
        tk.Label(
            form_frame, text="Target Date (YYYY-MM-DD)", 
            font=("Arial", 11, "bold"),
            bg="#1e293b", fg="#e2e8f0"
        ).pack(anchor="w", pady=(0, 8))
        
        date_entry = tk.Entry(
            form_frame, font=("Arial", 12),
            bg="#334155", fg="white",
            relief="solid", bd=1, insertbackground="white"
        )
        date_entry.pack(fill="x", pady=(0, 20), ipady=8)
        date_entry.insert(0, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
        
        # Milestones
        tk.Label(
            form_frame, text="Milestones", 
            font=("Arial", 11, "bold"),
            bg="#1e293b", fg="#e2e8f0"
        ).pack(anchor="w", pady=(0, 8))
        
        milestone_container = tk.Frame(form_frame, bg="#334155", relief="solid", bd=1)
        milestone_container.pack(fill="both", expand=True, pady=(0, 10))
        
        milestone_list = tk.Listbox(
            milestone_container, height=6, 
            font=("Arial", 11),
            bg="#334155", fg="white",
            selectbackground=self.COLORS['ACCENT'], 
            selectforeground="white",
            relief="flat", bd=0
        )
        milestone_list.pack(fill="both", expand=True, padx=2, pady=2)
        
        milestone_input_frame = tk.Frame(form_frame, bg="#1e293b")
        milestone_input_frame.pack(fill="x", pady=(0, 25))
        
        milestone_entry = tk.Entry(
            milestone_input_frame, font=("Arial", 11),
            bg="#334155", fg="white",
            relief="solid", bd=1, insertbackground="white"
        )
        milestone_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=6)
        
        def add_milestone():
            text = milestone_entry.get().strip()
            if text:
                milestone_list.insert(tk.END, text)
                milestone_entry.delete(0, tk.END)
        
        def remove_milestone():
            selection = milestone_list.curselection()
            if selection:
                milestone_list.delete(selection[0])
        
        tk.Button(
            milestone_input_frame, text="Add", 
            command=add_milestone,
            bg="#475569", fg="white", 
            font=("Arial", 10, "bold"),
            relief="flat", padx=20, pady=6, 
            cursor="hand2",
            activebackground="#64748b"
        ).pack(side="left", padx=(0, 5))
        
        tk.Button(
            milestone_input_frame, text="Remove", 
            command=remove_milestone,
            bg="#475569", fg="white", 
            font=("Arial", 10, "bold"),
            relief="flat", padx=20, pady=6, 
            cursor="hand2",
            activebackground="#64748b"
        ).pack(side="left")
        
        # Pre-fill if editing
        if self.editing_goal:
            title_entry.insert(0, self.editing_goal.title)
            desc_text.insert("1.0", self.editing_goal.description)
            type_var.set(self.editing_goal.goal_type)
            date_entry.delete(0, tk.END)
            date_entry.insert(0, self.editing_goal.target_date)
            for milestone in self.editing_goal.milestones:
                milestone_list.insert(tk.END, milestone.text)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="#1e293b")
        button_frame.pack(fill="x", pady=(10, 0))
        
        def save_goal():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            goal_type = type_var.get()
            target_date = date_entry.get().strip()
            
            if not title or not target_date:
                messagebox.showerror("Error", "Please fill in title and target date!")
                return
            
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
            
            if self.editing_goal:
                goal = self.editing_goal.edited(
                    title, description, goal_type, target_date,
                    milestone_list.get(0, tk.END))
            else:
                goal = Goal(title, description, goal_type, target_date)
                for i in range(milestone_list.size()):
                    goal.add_milestone(milestone_list.get(i))
            
            if self.editing_goal:
                self.goal_manager.update_goal(goal)
            else:
                self.goal_manager.add_goal(goal)
            
            self.editing_goal = None
            self.refresh_goals()
            form_window.destroy()
            messagebox.showinfo("Success", "Goal saved successfully!")
        
        tk.Button(
            button_frame, text="Save Goal", 
            command=save_goal,
            bg="#10b981", fg="white", 
            font=("Arial", 11, "bold"),
            relief="flat", padx=25, pady=10, 
            cursor="hand2",
            activebackground="#059669"
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            button_frame, text="Cancel",
            command=lambda: [setattr(self, 'editing_goal', None), form_window.destroy()],
            bg="#475569", fg="white", 
            font=("Arial", 11, "bold"),
            relief="flat", padx=25, pady=10, 
            cursor="hand2",
            activebackground="#64748b"
        ).pack(side="left")
    
    def edit_goal(self, goal):
        """Edit an existing goal"""
        self.editing_goal = deepcopy(goal)
        self.show_goal_form()
    
    def delete_goal(self, goal):
        """Delete a goal"""
        if messagebox.askyesno("Confirm Delete", f"Delete '{goal.title}'?"):
            self.goal_manager.delete_goal(goal.id)
            self.refresh_goals()
    
    def toggle_milestone(self, goal, index):
        """Toggle milestone completion status"""
        updated = deepcopy(goal)
        updated.toggle_milestone(index)
        self.goal_manager.update_goal(updated)
        self.refresh_goals()
    
    def refresh_goals(self):
        """Refresh the goals display"""
        for widget in self.short_frame.winfo_children():
            widget.destroy()
        for widget in self.long_frame.winfo_children():
            widget.destroy()
        
        self.goal_manager.load_goals()
        
        short_term = self.goal_manager.get_short_term_goals()
        if short_term:
            for goal in short_term:
                self.create_goal_card(self.short_frame, goal)
        else:
            tk.Label(
                self.short_frame, 
                text="No short-term goals yet\n\nClick '+ Add Goal' to create one!",
                font=("Arial", 12), 
                bg=self.COLORS['DARK_BG'], 
                fg="#9ca3af",
                justify="center"
            ).pack(pady=80)
        
        long_term = self.goal_manager.get_long_term_goals()
        if long_term:
            for goal in long_term:
                self.create_goal_card(self.long_frame, goal)
        else:
            tk.Label(
                self.long_frame, 
                text="No long-term goals yet\n\nClick '+ Add Goal' to create one!",
                font=("Arial", 12), 
                bg=self.COLORS['DARK_BG'], 
                fg="#9ca3af",
                justify="center"
            ).pack(pady=80)
