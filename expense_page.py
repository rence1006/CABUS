"""
Expense tracking page for CABUS application
Budget management and expense categorization
"""

import math
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from base_page import BasePage
from dialogs import BudgetSetupDialog, EditBudgetDialog
from config import EXPENSE_CATEGORIES, CATEGORY_COLORS, CATEGORY_EMOJIS


class ExpensePage(BasePage):
    """Expense tracking and budget management page"""
    
    def __init__(self, root, main_content, user_name, expense_manager):
        super().__init__(root, main_content, user_name)
        self.expense_manager = expense_manager
        
        # Initialize reminders if not exists
        if not hasattr(root, "reminders"):
            root.reminders = []
    
    def show(self):
        """Display the expense page"""
        self.clear_content()
        
        # Check if budget is set
        if self.expense_manager.budget["amount"] == 0:
            BudgetSetupDialog(self.root, self.expense_manager, self.show)
            return
        
        # Main container
        expense_container = tk.Frame(self.main_content, bg=self.COLORS['DARK_BG'])
        expense_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title
        title_frame = tk.Frame(expense_container, bg=self.COLORS['DARK_BG'])
        title_frame.pack(pady=20)
        
        tk.Label(
            title_frame, text=" Expense Tracker", 
            font=("Arial", 36, "bold"),
            bg=self.COLORS['DARK_BG'], 
            fg=self.COLORS['ACCENT_LIGHT']
        ).pack()
        
        # Overview cards
        overview_frame = tk.Frame(expense_container, bg=self.COLORS['DARK_BG'])
        overview_frame.pack(fill="x", pady=10)
        
        total_expenses = self.expense_manager.get_total_expenses()
        remaining = self.expense_manager.get_remaining_budget()
        percent_used = (total_expenses / self.expense_manager.budget["amount"] * 100) if self.expense_manager.budget["amount"] > 0 else 0
        
        cards_frame = tk.Frame(overview_frame, bg=self.COLORS['DARK_BG'])
        cards_frame.pack(fill="x")
        
        self.create_budget_card(
            cards_frame, "Total Budget", 
            f"₱{self.expense_manager.budget['amount']:.2f}", 
            self.COLORS['ACCENT_LIGHT'], has_edit=True
        )
        self.create_budget_card(
            cards_frame, "Expenses This Month", 
            f"₱{total_expenses:.2f}", "#ef4444"
        )
        self.create_budget_card(
            cards_frame, "Remaining", 
            f"₱{remaining:.2f}",
            "#22c55e" if remaining >= 0 else "#ef4444"
        )
        
        # Progress bar
        progress_frame = tk.Frame(expense_container, bg="#2d3748", relief="groove", bd=2)
        progress_frame.pack(fill="x", pady=10)
        
        progress_inner = tk.Frame(progress_frame, bg="#2d3748")
        progress_inner.pack(fill="both", padx=15, pady=15)
        
        tk.Label(
            progress_inner, 
            text=f"Budget Usage: {percent_used:.1f}%",
            font=("Arial", 11), 
            bg="#2d3748", 
            fg=self.COLORS['SECONDARY_TEXT']
        ).pack(anchor="w", pady=(0, 5))
        
        progress_canvas = tk.Canvas(progress_inner, height=16, bg="#4a5568", highlightthickness=0)
        progress_canvas.pack(fill="x", pady=5)
        
        def draw_progress():
            progress_canvas.delete("all")
            w = progress_canvas.winfo_width()
            if w > 1:
                fill = min(w * percent_used / 100, w)
                color = "#ef4444" if percent_used > 90 else "#eab308" if percent_used > 70 else self.COLORS['ACCENT_LIGHT']
                progress_canvas.create_rectangle(0, 0, fill, 16, fill=color, outline="")
        
        progress_canvas.after(100, draw_progress)
        
        # Content grid
        content_grid = tk.Frame(expense_container, bg=self.COLORS['DARK_BG'])
        content_grid.pack(fill="both", expand=True, pady=10)
        
        # Configure columns to have equal weight
        content_grid.grid_columnconfigure(0, weight=1, uniform="col")
        content_grid.grid_columnconfigure(1, weight=1, uniform="col")
        content_grid.grid_columnconfigure(2, weight=1, uniform="col")
        content_grid.grid_rowconfigure(0, weight=1)
        
        # Left panel - Add expense form
        left_panel = tk.Frame(content_grid, bg=self.COLORS['DARK_BG'])
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.create_expense_form(left_panel)
        
        # Middle panel - Expense list
        middle_panel = tk.Frame(content_grid, bg=self.COLORS['DARK_BG'])
        middle_panel.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.create_expense_list(middle_panel)
        
        # Right panel - Reminders
        right_panel = tk.Frame(content_grid, bg=self.COLORS['DARK_BG'])
        right_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.create_reminders_panel(right_panel)
    
    def create_budget_card(self, parent, title, value, color, has_edit=False):
        """Create a budget card"""
        card = tk.Frame(parent, bg="#2d3748", relief="groove", bd=2)
        card.pack(side="left", fill="both", expand=True, padx=5)
        
        card_inner = tk.Frame(card, bg="#2d3748")
        card_inner.pack(fill="both", padx=15, pady=15)
        
        header = tk.Frame(card_inner, bg="#2d3748")
        header.pack(fill="x")
        
        tk.Label(
            header, text=title, 
            font=("Arial", 10), 
            bg="#2d3748",
            fg=self.COLORS['SECONDARY_TEXT']
        ).pack(side="left")
        
        if has_edit:
            edit_btn = tk.Label(
                header, text="Edit", 
                font=("Arial", 9), 
                bg="#2d3748",
                fg=self.COLORS['ACCENT_LIGHT'], 
                cursor="hand2"
            )
            edit_btn.pack(side="right")
            edit_btn.bind("<Button-1>", lambda e: self.show_edit_budget())
        
        tk.Label(
            card_inner, text=value, 
            font=("Arial", 24, "bold"),
            bg="#2d3748", fg=color, 
            anchor="w"
        ).pack(fill="x", pady=(5, 0))
    
    def create_expense_form(self, parent):
        """Create expense input form"""
        form_frame = tk.Frame(parent, bg="#2d3748", relief="groove", bd=2)
        form_frame.pack(fill="both", expand=True)
        
        form_inner = tk.Frame(form_frame, bg="#2d3748")
        form_inner.pack(fill="both", padx=15, pady=15)
        
        # Description
        tk.Label(
            form_inner, text="Description", 
            font=("Arial", 10),
            bg="#2d3748", 
            fg=self.COLORS['SECONDARY_TEXT']
        ).pack(anchor="w")
        
        self.desc_entry = tk.Entry(
            form_inner, font=("Arial", 11), 
            bg="#4a5568",
            fg=self.COLORS['TEXT'], 
            insertbackground=self.COLORS['ACCENT'], 
            bd=0
        )
        self.desc_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Amount
        tk.Label(
            form_inner, text="Amount (₱)", 
            font=("Arial", 10),
            bg="#2d3748", 
            fg=self.COLORS['SECONDARY_TEXT']
        ).pack(anchor="w")
        
        self.amount_entry = tk.Entry(
            form_inner, font=("Arial", 11), 
            bg="#4a5568",
            fg=self.COLORS['TEXT'], 
            insertbackground=self.COLORS['ACCENT'], 
            bd=0
        )
        self.amount_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Category
        tk.Label(
            form_inner, text="Category", 
            font=("Arial", 10),
            bg="#2d3748", 
            fg=self.COLORS['SECONDARY_TEXT']
        ).pack(anchor="w")
        
        self.category_var = tk.StringVar(value="Food")
        category_combo = ttk.Combobox(
            form_inner, textvariable=self.category_var,
            values=EXPENSE_CATEGORIES, 
            state="readonly", 
            font=("Arial", 11)
        )
        category_combo.pack(fill="x", ipady=5, pady=(0, 15))
        
        # Add button
        tk.Button(
            form_inner, text="➕ Add Expense", 
            font=("Arial", 12, "bold"),
            bg=self.COLORS['ACCENT'], 
            fg=self.COLORS['TEXT'], 
            cursor="hand2", bd=0, relief="flat",
            command=self.add_expense
        ).pack(fill="x", ipady=8)
        
        # Spacer to push content up
        tk.Frame(form_inner, bg="#2d3748").pack(fill="both", expand=True)
    
    def create_expense_list(self, parent):
        """Create expense list display"""
        list_frame = tk.Frame(parent, bg="#2d3748", relief="groove", bd=2)
        list_frame.pack(fill="both", expand=True)
        
        list_inner = tk.Frame(list_frame, bg="#2d3748")
        list_inner.pack(fill="both", padx=15, pady=15)
        
        tk.Label(
            list_inner, text="🔍 Recent Expenses", 
            font=("Arial", 16, "bold"),
            bg="#2d3748", fg=self.COLORS['TEXT']
        ).pack(anchor="w", pady=(0, 10))
        
        # Search bar
        search_frame = tk.Frame(list_inner, bg="#2d3748")
        search_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            search_frame, text="Search:", 
            font=("Arial", 10),
            bg="#2d3748", 
            fg=self.COLORS['SECONDARY_TEXT']
        ).pack(side="left", padx=(0, 8))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.update_expense_list())
        
        search_entry = tk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("Arial", 11), 
            bg="#4a5568",
            fg=self.COLORS['TEXT'], 
            insertbackground=self.COLORS['ACCENT'], 
            bd=0
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=6)
        
        # Scrollable expenses
        canvas_frame = tk.Frame(list_inner, bg="#2d3748")
        canvas_frame.pack(fill="both", expand=True)
        
        expense_canvas = tk.Canvas(canvas_frame, bg="#2d3748", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=expense_canvas.yview)
        
        self.expense_list = tk.Frame(expense_canvas, bg="#2d3748")
        expense_canvas.create_window((0, 0), window=self.expense_list, anchor="nw")
        expense_canvas.configure(yscrollcommand=scrollbar.set)
        
        expense_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.expense_list.bind(
            "<Configure>",
            lambda e: expense_canvas.configure(scrollregion=expense_canvas.bbox("all"))
        )
        
        self.update_expense_list()
    
    def create_reminders_panel(self, parent):
        """Create reminders panel"""
        rem_frame = tk.Frame(parent, bg="#2d3748", relief="groove", bd=2)
        rem_frame.pack(fill="both", expand=True)
        
        # Use grid layout for better control
        rem_frame.grid_rowconfigure(0, weight=1)
        rem_frame.grid_rowconfigure(1, weight=0)
        rem_frame.grid_columnconfigure(0, weight=1)
        
        # Top section: Title and scrollable list
        top_section = tk.Frame(rem_frame, bg="#2d3748")
        top_section.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 10))
        
        tk.Label(
            top_section, text="📌 Reminders", 
            font=("Arial", 16, "bold"),
            bg="#2d3748", fg=self.COLORS['TEXT']
        ).pack(anchor="w", pady=(0, 15))
        
        # Scrollable reminders list
        rem_canvas_frame = tk.Frame(top_section, bg="#2d3748")
        rem_canvas_frame.pack(fill="both", expand=True)
        
        rem_canvas = tk.Canvas(rem_canvas_frame, bg="#2d3748", highlightthickness=0)
        rem_scrollbar = ttk.Scrollbar(rem_canvas_frame, orient="vertical", command=rem_canvas.yview)
        
        self.rem_list_frame = tk.Frame(rem_canvas, bg="#2d3748")
        rem_canvas.create_window((0, 0), window=self.rem_list_frame, anchor="nw")
        rem_canvas.configure(yscrollcommand=rem_scrollbar.set)
        
        rem_canvas.pack(side="left", fill="both", expand=True)
        rem_scrollbar.pack(side="right", fill="y")
        
        self.rem_list_frame.bind(
            "<Configure>",
            lambda e: rem_canvas.configure(scrollregion=rem_canvas.bbox("all"))
        )
        
        self.update_reminders()
        
        # Bottom section: Add Reminder button
        button_section = tk.Frame(rem_frame, bg="#2d3748")
        button_section.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        tk.Button(
            button_section, text="➕ Add Reminder", 
            font=("Arial", 12, "bold"),
            bg=self.COLORS['ACCENT'], 
            fg=self.COLORS['TEXT'], 
            cursor="hand2", bd=0, relief="flat",
            command=self.add_reminder_popup
        ).pack(fill="x", ipady=8)
    
    def add_expense(self):
        """Add a new expense"""
        desc = self.desc_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        
        if not desc:
            messagebox.showwarning("Warning", "Please enter a description")
            return
        
        try:
            amount = float(amount_str)
            if not math.isfinite(amount) or round(amount, 2) <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid amount")
            return
        
        expense = {
            'description': desc,
            'amount': amount,
            'category': self.category_var.get(),
            'date': datetime.now().strftime("%m/%d/%Y")
        }
        
        self.expense_manager.add_expense(expense)
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        
        self.show()
    
    def update_expense_list(self):
        """Update the expense list display with search filter"""
        for widget in self.expense_list.winfo_children():
            widget.destroy()
        
        # Get search query
        search_query = self.search_var.get().lower().strip()
        
        # Filter expenses based on search
        filtered_expenses = self.expense_manager.expenses
        if search_query:
            filtered_expenses = [
                exp for exp in self.expense_manager.expenses
                if search_query in exp['description'].lower() or 
                   search_query in exp['category'].lower()
            ]
        
        if not filtered_expenses:
            if search_query:
                tk.Label(
                    self.expense_list, text=f"No expenses matching '{search_query}'",
                    bg="#2d3748", fg="#6b7280", 
                    font=("Arial", 11)
                ).pack(pady=20)
            else:
                tk.Label(
                    self.expense_list, text="No expenses yet.",
                    bg="#2d3748", fg="#6b7280", 
                    font=("Arial", 11)
                ).pack(pady=20)
        else:
            for expense in filtered_expenses:
                self.create_expense_card(expense)
    
    def create_expense_card(self, expense):
        """Create an expense card"""
        card = tk.Frame(self.expense_list, bg="#374151", bd=1, relief="raised")
        card.pack(fill="x", pady=3)
        
        inner = tk.Frame(card, bg="#374151")
        inner.pack(fill="both", padx=10, pady=10)
        
        tk.Label(
            inner, text=CATEGORY_EMOJIS[expense['category']],
            bg=CATEGORY_COLORS[expense['category']],
            font=("Arial", 16), width=2
        ).pack(side="left", padx=(0, 10))
        
        info = tk.Frame(inner, bg="#374151")
        info.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            info, text=expense['description'], 
            font=("Arial", 12, "bold"),
            bg="#374151", fg=self.COLORS['TEXT']
        ).pack(anchor="w")
        
        tk.Label(
            info, text=f"{expense['category']} • {expense['date']}",
            bg="#374151", 
            fg=self.COLORS['SECONDARY_TEXT']
        ).pack(anchor="w")
        
        tk.Label(
            inner, text=f"₱{expense['amount']:.2f}", 
            font=("Arial", 16, "bold"),
            bg="#374151", fg="#ef4444"
        ).pack(side="left", padx=10)
        
        delete_btn = tk.Label(
            inner, text="🗑️", 
            font=("Arial", 16),
            bg="#374151", fg="#ef4444", 
            cursor="hand2"
        )
        delete_btn.pack(side="left")
        delete_btn.bind("<Button-1>", lambda e, eid=expense['id']: self.delete_expense(eid))
    
    def delete_expense(self, expense_id):
        """Delete an expense"""
        self.expense_manager.delete_expense(expense_id)
        self.show()
    
    def update_reminders(self):
        """Update reminders display"""
        for widget in self.rem_list_frame.winfo_children():
            widget.destroy()
        
        if not self.root.reminders:
            tk.Label(
                self.rem_list_frame, 
                text="No reminders yet.",
                bg="#2d3748", fg="#6b7280",
                font=("Arial", 11)
            ).pack(pady=20)
        else:
            for r in self.root.reminders:
                c = tk.Frame(self.rem_list_frame, bg="#374151", bd=1, relief="raised")
                c.pack(fill="x", pady=3)
                tk.Label(
                    c, text=r, 
                    bg="#374151", 
                    fg=self.COLORS['TEXT'],
                    font=("Arial", 12), 
                    padx=10, pady=8
                ).pack(anchor="w")
    
    def add_reminder_popup(self):
        """Show add reminder popup"""
        if len(self.root.reminders) >= 5:
            messagebox.showwarning(
                "Limit Reached",
                "You can only have 5 reminders at a time.\nPlease delete an existing reminder first."
            )
            return
        
        pop = tk.Toplevel(self.root)
        pop.title("Add Reminder")
        pop.geometry("350x200")
        pop.configure(bg="#2d3748")
        pop.transient(self.root)
        pop.grab_set()
        
        pop.update_idletasks()
        x = (pop.winfo_screenwidth() // 2) - (pop.winfo_width() // 2)
        y = (pop.winfo_screenheight() // 2) - (pop.winfo_height() // 2)
        pop.geometry(f"+{x}+{y}")
        
        tk.Label(
            pop, text="Reminder:", 
            font=("Arial", 12),
            bg="#2d3748", fg=self.COLORS['TEXT']
        ).pack(pady=10)
        
        entry = tk.Entry(
            pop, font=("Arial", 12), 
            bg="#4a5568",
            fg=self.COLORS['TEXT'], 
            insertbackground=self.COLORS['ACCENT']
        )
        entry.pack(fill="x", padx=20, ipady=8)
        
        def save():
            t = entry.get().strip()
            if t:
                self.root.reminders.insert(0, t)
                pop.destroy()
                self.show()
        
        tk.Button(
            pop, text="Save Reminder", 
            bg=self.COLORS['ACCENT'], 
            fg=self.COLORS['TEXT'],
            font=("Arial", 12, "bold"), 
            command=save
        ).pack(fill="x", padx=10, pady=10)
    
    def show_edit_budget(self):
        """Show edit budget dialog"""
        EditBudgetDialog(self.root, self.expense_manager, self.show)
