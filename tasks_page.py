"""
Tasks management page for CABUS application
Enhanced tabs and dialog UI improvements - Card Layout
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import calendar
from base_page import BasePage
from config import TASK_CATEGORIES, TASK_PRIORITIES, TASK_STATUSES, PRIORITY_COLORS


class TasksPage(BasePage):
    """Tasks management with enhanced UI elements"""
    
    def __init__(self, root, main_content, user_name, task_manager):
        super().__init__(root, main_content, user_name)
        self.task_manager = task_manager
    
    def show(self):
        """Display the tasks page"""
        self.clear_content()
        
        # Header
        header_frame = tk.Frame(self.main_content, bg=self.COLORS['DARK_BG'])
        header_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(
            header_frame, text=" Task Manager", 
            font=("Arial", 36, "bold"),
            bg=self.COLORS['DARK_BG'], 
            fg=self.COLORS['ACCENT_LIGHT']
        ).pack(anchor="center")
        
        # Controls frame
        controls_frame = tk.Frame(self.main_content, bg=self.COLORS['CARD'], relief="flat", bd=2)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Search
        search_frame = tk.Frame(controls_frame, bg=self.COLORS['CARD'])
        search_frame.pack(side="left", padx=10, pady=10)
        tk.Label(
            search_frame, text="Search:", 
            bg=self.COLORS['CARD'], 
            fg=self.COLORS['TEXT'], 
            font=("Arial", 11)
        ).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_tasks())
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var, 
            font=("Arial", 11), width=20,
            bg=self.COLORS['BG'], 
            fg=self.COLORS['TEXT'], 
            insertbackground=self.COLORS['ACCENT'], 
            bd=1, relief="flat"
        )
        search_entry.pack(side="left", padx=5)
        
        # Filter
        filter_frame = tk.Frame(controls_frame, bg=self.COLORS['CARD'])
        filter_frame.pack(side="left", padx=10, pady=10)
        tk.Label(
            filter_frame, text="Category:", 
            bg=self.COLORS['CARD'], 
            fg=self.COLORS['TEXT'], 
            font=("Arial", 11)
        ).pack(side="left")
        self.category_var = tk.StringVar(value="All")
        self.category_var.trace('w', lambda *args: self.refresh_tasks())
        category_combo = ttk.Combobox(
            filter_frame, textvariable=self.category_var,
            values=["All"] + TASK_CATEGORIES,
            width=12, state="readonly", 
            font=("Arial", 10)
        )
        category_combo.pack(side="left", padx=5)
        
        # Sort
        sort_frame = tk.Frame(controls_frame, bg=self.COLORS['CARD'])
        sort_frame.pack(side="left", padx=10, pady=10)
        tk.Label(
            sort_frame, text="Sort:", 
            bg=self.COLORS['CARD'], 
            fg=self.COLORS['TEXT'], 
            font=("Arial", 11)
        ).pack(side="left")
        self.sort_var = tk.StringVar(value="None")
        self.sort_var.trace('w', lambda *args: self.refresh_tasks())
        sort_combo = ttk.Combobox(
            sort_frame, textvariable=self.sort_var,
            values=["None", "Deadline", "Priority", "Status"],
            width=12, state="readonly", 
            font=("Arial", 10)
        )
        sort_combo.pack(side="left", padx=5)
        
        # Add Task button
        tk.Button(
            controls_frame, text="➕ Add Task", 
            bg=self.COLORS['ACCENT'], 
            fg=self.COLORS['TEXT'],
            font=("Arial", 12, "bold"), 
            relief="flat", bd=0,
            activebackground=self.COLORS['ACCENT_LIGHT'], 
            padx=20, pady=8,
            command=self.add_task
        ).pack(side="right", padx=10)
        
        # Enhanced Notebook with modern tabs
        notebook_container = tk.Frame(self.main_content, bg=self.COLORS['DARK_BG'])
        notebook_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create custom tab bar
        self.tab_bar = tk.Frame(notebook_container, bg=self.COLORS['CARD'], height=55)
        self.tab_bar.pack(fill="x")
        self.tab_bar.pack_propagate(False)
        
        # Add bottom border to tab bar
        tk.Frame(self.tab_bar, bg=self.COLORS['ACCENT'], height=2).pack(side="bottom", fill="x")
        
        # Tab buttons container
        tabs_inner = tk.Frame(self.tab_bar, bg=self.COLORS['CARD'])
        tabs_inner.pack(fill="both", expand=True, padx=5)
        
        # Content area
        self.content_area = tk.Frame(notebook_container, bg=self.COLORS['DARK_BG'])
        self.content_area.pack(fill="both", expand=True)
        
        # Create tab frames
        self.list_tab = tk.Frame(self.content_area, bg=self.COLORS['DARK_BG'])
        self.calendar_tab = tk.Frame(self.content_area, bg=self.COLORS['DARK_BG'])
        self.chart_tab = tk.Frame(self.content_area, bg=self.COLORS['DARK_BG'])
        
        # Tab configuration
        self.tabs = [
            {
                'name': 'List View',
                'icon': '📋',
                'frame': self.list_tab,
                'button': None
            },
            {
                'name': 'Calendar View',
                'icon': '📅',
                'frame': self.calendar_tab,
                'button': None
            },
            {
                'name': 'Progress Chart',
                'icon': '📊',
                'frame': self.chart_tab,
                'button': None
            }
        ]
        
        # Create tab buttons
        for i, tab in enumerate(self.tabs):
            tab_btn = tk.Frame(tabs_inner, bg=self.COLORS['CARD'], cursor="hand2")
            tab_btn.pack(side="left", fill="both", padx=2)
            
            # Icon and text container
            content = tk.Frame(tab_btn, bg=self.COLORS['CARD'])
            content.pack(padx=20, pady=10)
            
            icon_label = tk.Label(
                content,
                text=tab['icon'],
                font=("Arial", 16),
                bg=self.COLORS['CARD'],
                fg=self.COLORS['SECONDARY_TEXT']
            )
            icon_label.pack(side="left", padx=(0, 8))
            
            text_label = tk.Label(
                content,
                text=tab['name'],
                font=("Arial", 11, "bold"),
                bg=self.COLORS['CARD'],
                fg=self.COLORS['SECONDARY_TEXT']
            )
            text_label.pack(side="left")
            
            # Active indicator (hidden by default)
            indicator = tk.Frame(tab_btn, bg=self.COLORS['ACCENT'], height=3)
            
            # Store references
            tab['button'] = tab_btn
            tab['content'] = content
            tab['icon_label'] = icon_label
            tab['text_label'] = text_label
            tab['indicator'] = indicator
            
            # Bind click event
            for widget in [tab_btn, content, icon_label, text_label]:
                widget.bind("<Button-1>", lambda e, idx=i: self.switch_tab(idx))
                widget.bind("<Enter>", lambda e, idx=i: self.on_tab_hover(idx, True))
                widget.bind("<Leave>", lambda e, idx=i: self.on_tab_hover(idx, False))
        
        # Create grid layout in list tab
        self.create_grid_layout(self.list_tab)
        
        # Show first tab
        self.current_tab = -1
        self.switch_tab(0)
        
        self.refresh_tasks()
    
    def switch_tab(self, index):
        """Switch between tabs with visual feedback"""
        if self.current_tab == index:
            return
        
        # Hide previous tab
        if self.current_tab >= 0:
            prev_tab = self.tabs[self.current_tab]
            prev_tab['frame'].pack_forget()
            prev_tab['indicator'].pack_forget()
            prev_tab['button']['bg'] = self.COLORS['CARD']
            prev_tab['content']['bg'] = self.COLORS['CARD']
            prev_tab['icon_label']['bg'] = self.COLORS['CARD']
            prev_tab['icon_label']['fg'] = self.COLORS['SECONDARY_TEXT']
            prev_tab['text_label']['bg'] = self.COLORS['CARD']
            prev_tab['text_label']['fg'] = self.COLORS['SECONDARY_TEXT']
        
        # Show new tab
        current_tab = self.tabs[index]
        current_tab['frame'].pack(fill="both", expand=True)
        current_tab['indicator'].pack(side="bottom", fill="x")
        current_tab['button']['bg'] = self.COLORS['BG']
        current_tab['content']['bg'] = self.COLORS['BG']
        current_tab['icon_label']['bg'] = self.COLORS['BG']
        current_tab['icon_label']['fg'] = self.COLORS['ACCENT_LIGHT']
        current_tab['text_label']['bg'] = self.COLORS['BG']
        current_tab['text_label']['fg'] = self.COLORS['TEXT']
        
        self.current_tab = index
        
        # Update content based on tab
        if index == 1:
            self.show_calendar()
        elif index == 2:
            self.show_chart()
    
    def on_tab_hover(self, index, entering):
        """Handle tab hover effects"""
        if index == self.current_tab:
            return
        
        tab = self.tabs[index]
        if entering:
            tab['button']['bg'] = self.COLORS['BG']
            tab['content']['bg'] = self.COLORS['BG']
            tab['icon_label']['bg'] = self.COLORS['BG']
            tab['text_label']['bg'] = self.COLORS['BG']
            tab['text_label']['fg'] = self.COLORS['TEXT']
        else:
            tab['button']['bg'] = self.COLORS['CARD']
            tab['content']['bg'] = self.COLORS['CARD']
            tab['icon_label']['bg'] = self.COLORS['CARD']
            tab['text_label']['bg'] = self.COLORS['CARD']
            tab['text_label']['fg'] = self.COLORS['SECONDARY_TEXT']
    
    def create_grid_layout(self, parent):
        """Create the grid layout for tasks"""
        # Create canvas with scrollbar
        canvas = tk.Canvas(parent, bg=self.COLORS['DARK_BG'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        self.tasks_container = tk.Frame(canvas, bg=self.COLORS['DARK_BG'])
        
        self.tasks_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.tasks_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def refresh_tasks(self):
        """Refresh all task displays"""
        # Clear tasks container
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
        
        # Filter tasks
        filtered_tasks = self.task_manager.tasks.copy()
        
        search_text = self.search_var.get().lower()
        if search_text:
            filtered_tasks = [t for t in filtered_tasks if search_text in t["title"].lower()]
        
        if self.category_var.get() != "All":
            filtered_tasks = [t for t in filtered_tasks if t["category"] == self.category_var.get()]
        
        # Sort tasks
        if self.sort_var.get() == "Deadline":
            filtered_tasks.sort(key=lambda x: x["deadline"])
        elif self.sort_var.get() == "Priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            filtered_tasks.sort(key=lambda x: priority_order[x["priority"]])
        elif self.sort_var.get() == "Status":
            filtered_tasks.sort(key=lambda x: x["status"])
        
        # Display tasks in grid (2 columns)
        row = 0
        col = 0
        for task in filtered_tasks:
            self.create_task_card(self.tasks_container, task, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        # Update calendar and chart if they're visible
        if self.current_tab == 1:
            self.show_calendar()
        elif self.current_tab == 2:
            self.show_chart()
    
    def create_task_card(self, parent, task, row, col):
        """Create a new modern task card matching the reference image"""
        # Card container with minimum size
        card_frame = tk.Frame(parent, bg=self.COLORS['DARK_BG'])
        card_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
        
        # Configure grid weights for responsive layout
        parent.grid_columnconfigure(0, weight=1, minsize=700)
        parent.grid_columnconfigure(1, weight=1, minsize=700)
        parent.grid_rowconfigure(row, weight=0, minsize=450)
        
        # Main card with border
        card = tk.Frame(card_frame, bg=self.COLORS['BG'], relief="solid", bd=1, highlightthickness=0)
        card.pack(fill="both", expand=True)
        
        # Yellow priority bar on the left
        priority_bar = tk.Frame(card, bg="#FFC107", width=12)
        priority_bar.pack(side="left", fill="y")
        
        # Content area with increased padding
        content = tk.Frame(card, bg=self.COLORS['BG'])
        content.pack(side="left", fill="both", expand=True, padx=35, pady=35)
        
        # Title
        title_label = tk.Label(
            content,
            text=task["title"],
            font=("Arial", 20, "bold"),
            bg=self.COLORS['BG'],
            fg=self.COLORS['TEXT'],
            anchor="w"
        )
        title_label.pack(fill="x", pady=(0, 15))
        
        # Status badge
        status_colors = {
            "Pending": "#FFA500",
            "In Progress": "#5DADE2",
            "Completed": "#52BE80"
        }
        status_icons = {
            "Pending": "⏳",
            "In Progress": "🔄",
            "Completed": "✓"
        }
        
        status_frame = tk.Frame(content, bg=self.COLORS['BG'])
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_badge = tk.Label(
            status_frame,
            text=f"{status_icons[task['status']]} {task['status']}",
            font=("Arial", 11, "bold"),
            bg=status_colors[task["status"]],
            fg="white",
            padx=12,
            pady=6
        )
        status_badge.pack(side="left")
        
        # Metadata section
        meta_frame = tk.Frame(content, bg=self.COLORS['BG'])
        meta_frame.pack(fill="x", pady=(0, 20))
        
        # Category
        cat_row = tk.Frame(meta_frame, bg=self.COLORS['BG'])
        cat_row.pack(fill="x", pady=3)
        tk.Label(
            cat_row,
            text=f"📁 {task['category']}",
            font=("Arial", 11),
            bg=self.COLORS['BG'],
            fg=self.COLORS['SECONDARY_TEXT'],
            anchor="w"
        ).pack(side="left")
        
        # Deadline
        deadline_row = tk.Frame(meta_frame, bg=self.COLORS['BG'])
        deadline_row.pack(fill="x", pady=3)
        tk.Label(
            deadline_row,
            text=f"📅 {task['deadline']}",
            font=("Arial", 11),
            bg=self.COLORS['BG'],
            fg=self.COLORS['SECONDARY_TEXT'],
            anchor="w"
        ).pack(side="left")
        
        # Priority
        priority_row = tk.Frame(meta_frame, bg=self.COLORS['BG'])
        priority_row.pack(fill="x", pady=3)
        tk.Label(
            priority_row,
            text=f"⚡ Priority: {task['priority']}",
            font=("Arial", 11, "bold"),
            bg=self.COLORS['BG'],
            fg="#FFC107",
            anchor="w"
        ).pack(side="left")
        
        # Action buttons
        btn_frame = tk.Frame(content, bg=self.COLORS['BG'])
        btn_frame.pack(fill="x")
        
        # Edit button
        edit_btn = tk.Button(
            btn_frame,
            text="✏ Edit",
            font=("Arial", 11, "bold"),
            bg="#8B5CF6",
            fg="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda t=task: self.edit_task(t)
        )
        edit_btn.pack(side="left", padx=(0, 8))
        
        # Done button
        done_btn = tk.Button(
            btn_frame,
            text="✓ Done",
            font=("Arial", 11, "bold"),
            bg="#52BE80",
            fg="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda t=task: self.mark_completed(t)
        )
        done_btn.pack(side="left", padx=4)
        
        # Delete button
        delete_btn = tk.Button(
            btn_frame,
            text="🗑 Delete",
            font=("Arial", 11, "bold"),
            bg="#E74C3C",
            fg="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda t=task: self.delete_task(t)
        )
        delete_btn.pack(side="left", padx=4)
        
        # Hover effects
        def create_hover(button, normal_color, hover_color):
            button.bind("<Enter>", lambda e: button.config(bg=hover_color))
            button.bind("<Leave>", lambda e: button.config(bg=normal_color))
        
        create_hover(edit_btn, "#8B5CF6", "#9D6FFF")
        create_hover(done_btn, "#52BE80", "#6DD49E")
        create_hover(delete_btn, "#E74C3C", "#F16B5C")
    
    def add_task(self):
        """Show dialog to add new task"""
        self.show_task_dialog()
    
    def edit_task(self, task):
        """Show dialog to edit task"""
        self.show_task_dialog(task)
    
    def show_task_dialog(self, task=None):
        """Show enhanced task creation/editing dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task" if not task else "Edit Task")
        dialog.geometry("550x620")
        dialog.configure(bg="#1e1e2e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Accent bar at top
        tk.Frame(dialog, bg="#a78bfa", height=4).pack(fill="x")
        
        # Header
        header_frame = tk.Frame(dialog, bg="#1e1e2e")
        header_frame.pack(fill="x", padx=35, pady=25)
        
        tk.Label(
            header_frame,
            text="Add New Task" if not task else "Edit Task",
            font=("Segoe UI", 24, "bold"),
            bg="#1e1e2e",
            fg="#a78bfa"
        ).pack()
        
        # Form container
        form_container = tk.Frame(dialog, bg="#1e1e2e")
        form_container.pack(fill="both", expand=True, padx=35)
        
        # Task Title
        tk.Label(
            form_container,
            text="Task Title:",
            bg="#1e1e2e",
            fg="#e0e0e0",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))
        
        title_frame = tk.Frame(form_container, bg="#2d2d44", highlightbackground="#4a4a6a", highlightthickness=1)
        title_frame.pack(fill="x", pady=(0, 18))
        
        title_entry = tk.Entry(
            title_frame,
            font=("Segoe UI", 11),
            bg="#2d2d44",
            fg="#ffffff",
            insertbackground="#a78bfa",
            relief="flat",
            bd=0
        )
        title_entry.pack(fill="x", padx=12, pady=10)
        if task:
            title_entry.insert(0, task["title"])
        
        # Category
        tk.Label(
            form_container,
            text="Category:",
            bg="#1e1e2e",
            fg="#e0e0e0",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))
        
        category_style = ttk.Style()
        category_style.theme_use('clam')
        category_style.configure(
            'Dark.TCombobox',
            fieldbackground="#2d2d44",
            background="#2d2d44",
            foreground="#ffffff",
            bordercolor="#4a4a6a",
            arrowcolor="#a78bfa",
            borderwidth=1
        )
        category_style.map('Dark.TCombobox',
            fieldbackground=[('readonly', '#2d2d44')],
            selectbackground=[('readonly', '#2d2d44')],
            selectforeground=[('readonly', '#ffffff')]
        )
        
        category_entry = ttk.Combobox(
            form_container,
            values=TASK_CATEGORIES,
            font=("Segoe UI", 11),
            state="readonly",
            style='Dark.TCombobox'
        )
        category_entry.pack(fill="x", pady=(0, 18), ipady=8)
        category_entry.set(task["category"] if task else "Personal")
        
        # Priority
        tk.Label(
            form_container,
            text="Priority:",
            bg="#1e1e2e",
            fg="#e0e0e0",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))
        
        priority_entry = ttk.Combobox(
            form_container,
            values=TASK_PRIORITIES,
            font=("Segoe UI", 11),
            state="readonly",
            style='Dark.TCombobox'
        )
        priority_entry.pack(fill="x", pady=(0, 18), ipady=8)
        priority_entry.set(task["priority"] if task else "Medium")
        
        # Status
        tk.Label(
            form_container,
            text="Status:",
            bg="#1e1e2e",
            fg="#e0e0e0",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))
        
        status_entry = ttk.Combobox(
            form_container,
            values=TASK_STATUSES,
            font=("Segoe UI", 11),
            state="readonly",
            style='Dark.TCombobox'
        )
        status_entry.pack(fill="x", pady=(0, 18), ipady=8)
        status_entry.set(task["status"] if task else "Pending")
        
        # Deadline
        tk.Label(
            form_container,
            text="Deadline (YYYY-MM-DD):",
            bg="#1e1e2e",
            fg="#e0e0e0",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))
        
        deadline_frame = tk.Frame(form_container, bg="#2d2d44", highlightbackground="#4a4a6a", highlightthickness=1)
        deadline_frame.pack(fill="x", pady=(0, 20))
        
        deadline_entry = tk.Entry(
            deadline_frame,
            font=("Segoe UI", 11),
            bg="#2d2d44",
            fg="#ffffff",
            insertbackground="#a78bfa",
            relief="flat",
            bd=0
        )
        deadline_entry.pack(fill="x", padx=12, pady=10)
        if task:
            deadline_entry.insert(0, task["deadline"])
        else:
            deadline_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        
        def save_task():
            title = title_entry.get().strip()
            if not title:
                messagebox.showwarning("Warning", "Please enter a task title")
                return
            
            try:
                datetime.strptime(deadline_entry.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid deadline", "Enter a valid date in YYYY-MM-DD format")
                return

            task_data = {
                "id": task["id"] if task else len(self.task_manager.tasks) + 1,
                "title": title,
                "category": category_entry.get(),
                "priority": priority_entry.get(),
                "status": status_entry.get(),
                "deadline": deadline_entry.get()
            }
            
            if task:
                self.task_manager.update_task(task_data)
            else:
                self.task_manager.add_task(task_data)
            
            self.refresh_tasks()
            dialog.destroy()
            messagebox.showinfo("Success", "Task saved successfully!")
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="#1e1e2e")
        btn_frame.pack(pady=(10, 30))
        
        save_btn = tk.Button(
            btn_frame,
            text="Save Task",
            bg="#7c3aed",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=save_task
        )
        save_btn.pack(side="left", padx=6)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            bg="#ef4444",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2",
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=6)
        
        # Hover effects
        def on_save_enter(e):
            save_btn['bg'] = "#8b5cf6"
        def on_save_leave(e):
            save_btn['bg'] = "#7c3aed"
        def on_cancel_enter(e):
            cancel_btn['bg'] = "#dc2626"
        def on_cancel_leave(e):
            cancel_btn['bg'] = "#ef4444"
        
        save_btn.bind("<Enter>", on_save_enter)
        save_btn.bind("<Leave>", on_save_leave)
        cancel_btn.bind("<Enter>", on_cancel_enter)
        cancel_btn.bind("<Leave>", on_cancel_leave)
    
    def mark_completed(self, task):
        """Mark task as completed"""
        self.task_manager.update_task(dict(task, status="Completed"))
        self.refresh_tasks()
    
    def delete_task(self, task):
        """Delete a task"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.task_manager.delete_task(task["id"])
            self.refresh_tasks()
    
    def show_calendar(self):
        """Show calendar view"""
        for widget in self.calendar_tab.winfo_children():
            widget.destroy()
        
        now = datetime.now()
        cal = calendar.monthcalendar(now.year, now.month)
        
        tk.Label(
            self.calendar_tab, 
            text=f"{calendar.month_name[now.month]} {now.year}",
            font=("Arial", 24, "bold"), 
            bg=self.COLORS['DARK_BG'], 
            fg=self.COLORS['ACCENT_LIGHT']
        ).pack(pady=20)
        
        cal_frame = tk.Frame(self.calendar_tab, bg=self.COLORS['DARK_BG'])
        cal_frame.pack(pady=10)
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(
                cal_frame, text=day, 
                font=("Arial", 12, "bold"),
                bg=self.COLORS['ACCENT'], 
                fg=self.COLORS['TEXT'], 
                width=10
            ).grid(row=0, column=i, padx=2, pady=2)
        
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    tk.Label(
                        cal_frame, text="", 
                        bg=self.COLORS['DARK_BG'], 
                        width=10
                    ).grid(row=week_num, column=day_num, padx=2, pady=2)
                else:
                    day_tasks = [
                        t for t in self.task_manager.tasks 
                        if t["deadline"] == f"{now.year}-{now.month:02d}-{day:02d}"
                    ]
                    bg_color = self.COLORS['ACCENT_LIGHT'] if day_tasks else self.COLORS['CARD']
                    fg_color = self.COLORS['DARK_BG'] if day_tasks else self.COLORS['TEXT']
                    tk.Label(
                        cal_frame, text=str(day), 
                        bg=bg_color, fg=fg_color, 
                        relief="raised",
                        width=10, height=3, 
                        font=("Arial", 10)
                    ).grid(row=week_num, column=day_num, padx=2, pady=2)
    
    def show_chart(self):
        """Show progress chart"""
        for widget in self.chart_tab.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.chart_tab, text="Task Progress Overview", 
            font=("Arial", 24, "bold"),
            bg=self.COLORS['DARK_BG'], 
            fg=self.COLORS['ACCENT_LIGHT']
        ).pack(pady=20)
        
        total = len(self.task_manager.tasks)
        pending = len([t for t in self.task_manager.tasks if t["status"] == "Pending"])
        in_progress = len([t for t in self.task_manager.tasks if t["status"] == "In Progress"])
        completed = len([t for t in self.task_manager.tasks if t["status"] == "Completed"])
        
        stats_frame = tk.Frame(self.chart_tab, bg=self.COLORS['CARD'], relief="groove", bd=2)
        stats_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        tk.Label(
            stats_frame, text=f"Total Tasks: {total}", 
            font=("Arial", 18),
            bg=self.COLORS['CARD'], 
            fg=self.COLORS['TEXT']
        ).pack(pady=10)
        
        tk.Label(
            stats_frame, text=f"Pending: {pending}", 
            font=("Arial", 16),
            bg=self.COLORS['CARD'], 
            fg="#FFA500"
        ).pack(pady=5)
        
        tk.Label(
            stats_frame, text=f"In Progress: {in_progress}", 
            font=("Arial", 16),
            bg=self.COLORS['CARD'], 
            fg="#5DADE2"
        ).pack(pady=5)
        
        tk.Label(
            stats_frame, text=f"Completed: {completed}", 
            font=("Arial", 16),
            bg=self.COLORS['CARD'], 
            fg="#52BE80"
        ).pack(pady=5)
        
        if total > 0:
            completion_rate = (completed / total) * 100
            tk.Label(
                stats_frame, 
                text=f"\nCompletion Rate: {completion_rate:.1f}%",
                font=("Arial", 18, "bold"), 
                bg=self.COLORS['CARD'], 
                fg=self.COLORS['ACCENT_LIGHT']
            ).pack(pady=5)
            
            progress_bar = ttk.Progressbar(
                stats_frame, length=400, 
                mode='determinate', 
                value=completion_rate
            )
            progress_bar.pack(pady=5)
        
        tk.Label(
            stats_frame, text="\nPriority Breakdown:", 
            font=("Arial", 18, "bold"),
            bg=self.COLORS['CARD'], 
            fg=self.COLORS['TEXT']
        ).pack(pady=8)
        
        high = len([t for t in self.task_manager.tasks if t["priority"] == "High"])
        medium = len([t for t in self.task_manager.tasks if t["priority"] == "Medium"])
        low = len([t for t in self.task_manager.tasks if t["priority"] == "Low"])
        
        tk.Label(
            stats_frame, 
            text=f"🔴 High: {high}  🟡 Medium: {medium}  🟢 Low: {low}",
            font=("Arial", 14), 
            bg=self.COLORS['CARD'], 
            fg=self.COLORS['TEXT']
        ).pack(pady=1)
