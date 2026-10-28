"""
Fitness tracking page for CABUS application
Workout logging and exercise tracking
"""

import math
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import sys
import os

# Ensure imports work from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from base_page import BasePage
except ImportError as e:
    print(f"Error importing modules in fitness_page.py: {e}")
    print("Please ensure base_page.py is in the same directory")
    sys.exit(1)


class FitnessPage(BasePage):
    """Fitness and workout tracking page"""
    
    # Color scheme matching the navigation
    COLORS = {
        'BG': '#1a1a2e',           # Dark background
        'CARD': '#16213e',         # Card/panel background
        'ACCENT': '#0f3460',       # Accent color
        'ACCENT_LIGHT': '#e94560', # Light accent (red/pink)
        'TEXT': '#eaeaea'          # Text color
    }
    
    def __init__(self, root, main_content, user_name, fitness_manager):
        super().__init__(root, main_content, user_name)
        self.fitness_manager = fitness_manager
    
    def show(self):
        """Display the fitness page"""
        self.clear_content()
        self.main_content.configure(bg=self.COLORS['BG'])
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=self.COLORS['CARD'])
        style.configure("TLabel", background=self.COLORS['CARD'], foreground=self.COLORS['TEXT'], font=("Helvetica", 12))
        
        # Configure custom button style
        style.configure("Custom.TButton", 
                       font=("Verdana", 12, "bold"), 
                       padding=10,
                       background=self.COLORS['CARD'],
                       foreground=self.COLORS['ACCENT_LIGHT'],
                       borderwidth=0,
                       relief="flat")
        style.map("Custom.TButton", 
                 background=[("active", self.COLORS['ACCENT'])],
                 foreground=[("active", self.COLORS['TEXT'])])
        
        style.configure("Custom.Treeview",
                       background='#374151',
                       foreground=self.COLORS['TEXT'],
                       fieldbackground='#374151',
                       rowheight=40,
                       font=("Helvetica", 11),
                       borderwidth=0,
                       relief="flat")
        
        style.configure("Custom.Treeview.Heading",
                       background=self.COLORS['ACCENT'],
                       foreground=self.COLORS['TEXT'],
                       relief="raised",
                       font=("Helvetica", 12, "bold"),
                       borderwidth=2)
        
        style.map("Custom.Treeview",
                 background=[("selected", self.COLORS['ACCENT_LIGHT'])],
                 foreground=[("selected", "white")])
        
        style.map("Custom.Treeview.Heading",
                 background=[("active", self.COLORS['ACCENT_LIGHT'])],
                 foreground=[("active", "#ffffff")])
        
        # Configure Entry style
        style.configure("Custom.TEntry",
                       fieldbackground=self.COLORS['ACCENT'],
                       foreground=self.COLORS['TEXT'],
                       insertcolor=self.COLORS['ACCENT_LIGHT'])
        
        # Title
        title_frame = ttk.Frame(self.main_content)
        title_frame.pack(fill="x", pady=20)
        title_label = ttk.Label(
            title_frame, text="Fitness Gym Tracker", 
            font=("Verdana", 24, "bold"), 
            foreground=self.COLORS['ACCENT_LIGHT']
        )
        title_label.pack()
        
        # Main content frame
        main_frame = ttk.Frame(self.main_content)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel for inputs
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="y", padx=10)
        
        input_title = ttk.Label(
            left_panel, text="Add New Exercise", 
            font=("Verdana", 16, "bold"),
            foreground=self.COLORS['ACCENT_LIGHT']
        )
        input_title.pack(pady=10)
        
        exercise_label = ttk.Label(left_panel, text="Exercise Name:")
        exercise_label.pack(anchor="w", pady=5)
        self.exercise_entry = tk.Entry(left_panel, font=("Helvetica", 12), width=25,
                                       bg=self.COLORS['ACCENT'], fg=self.COLORS['TEXT'],
                                       insertbackground=self.COLORS['ACCENT_LIGHT'],
                                       relief="flat", bd=5)
        self.exercise_entry.pack(pady=5)
        
        sets_label = ttk.Label(left_panel, text="Sets:")
        sets_label.pack(anchor="w", pady=5)
        self.sets_entry = tk.Entry(left_panel, font=("Helvetica", 12), width=25,
                                   bg=self.COLORS['ACCENT'], fg=self.COLORS['TEXT'],
                                   insertbackground=self.COLORS['ACCENT_LIGHT'],
                                   relief="flat", bd=5)
        self.sets_entry.pack(pady=5)
        
        reps_label = ttk.Label(left_panel, text="Reps:")
        reps_label.pack(anchor="w", pady=5)
        self.reps_entry = tk.Entry(left_panel, font=("Helvetica", 12), width=25,
                                   bg=self.COLORS['ACCENT'], fg=self.COLORS['TEXT'],
                                   insertbackground=self.COLORS['ACCENT_LIGHT'],
                                   relief="flat", bd=5)
        self.reps_entry.pack(pady=5)
        
        weight_label = ttk.Label(left_panel, text="Weight:")
        weight_label.pack(anchor="w", pady=5)
        self.weight_entry = tk.Entry(left_panel, font=("Helvetica", 12), width=25,
                                     bg=self.COLORS['ACCENT'], fg=self.COLORS['TEXT'],
                                     insertbackground=self.COLORS['ACCENT_LIGHT'],
                                     relief="flat", bd=5)
        self.weight_entry.pack(pady=5)
        
        # Status label
        self.status_label = ttk.Label(
            left_panel, 
            text="Workout: Not Started", 
            font=("Verdana", 10, "bold"), 
            foreground=self.COLORS['ACCENT_LIGHT']
        )
        self.status_label.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(pady=20)
        
        # Right panel for display
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=10)
        
        display_title = ttk.Label(
            right_panel, text="Current Workout", 
            font=("Verdana", 16, "bold"),
            foreground=self.COLORS['ACCENT_LIGHT']
        )
        display_title.pack(pady=10)
        
        # Frame for treeview and scrollbar
        tree_frame = ttk.Frame(right_panel)
        tree_frame.pack(fill="both", expand=True, pady=10)
        
        columns = ("Exercise", "Sets", "Reps", "Weight")
        
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings",
            height=15, 
            style="Custom.Treeview"
        )
        
        self.tree.heading("Exercise", text="EXERCISE", anchor="center")
        self.tree.heading("Sets", text="SETS", anchor="center")
        self.tree.heading("Reps", text="REPS", anchor="center")
        self.tree.heading("Weight", text="WEIGHT", anchor="center")
        
        self.tree.column("Exercise", width=250, anchor="center")
        self.tree.column("Sets", width=90, anchor="center")
        self.tree.column("Reps", width=90, anchor="center")
        self.tree.column("Weight", width=130, anchor="center")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.tag_configure('oddrow', background="#c0c0c0", foreground=self.COLORS['BG'], font=("Helvetica", 11))
        self.tree.tag_configure('evenrow', background=self.COLORS['TEXT'], foreground=self.COLORS['BG'], font=("Helvetica", 11))
        self.tree.tag_configure('highlight', background=self.COLORS['ACCENT_LIGHT'], foreground="white", font=("Helvetica", 11, "bold"))
        
        # Summary section
        summary_frame = ttk.Frame(right_panel)
        summary_frame.pack(fill="x", pady=10)
        
        self.summary_label = ttk.Label(
            summary_frame, 
            text="📊 Total Exercises: 0 | Total Sets: 0 | Total Reps: 0",
            font=("Verdana", 12, "bold"),
            foreground=self.COLORS['ACCENT_LIGHT']
        )
        self.summary_label.pack()
        
        # Footer
        footer_frame = ttk.Frame(self.main_content)
        footer_frame.pack(fill="x", pady=10)
        footer_label = ttk.Label(
            footer_frame, text="Stay Fit, Stay Strong! 💪", 
            font=("Verdana", 10), 
            foreground=self.COLORS['TEXT']
        )
        footer_label.pack()
        
        # Add buttons with custom styling - DARK PURPLE COLOR #374151
        # All buttons now have the same height (height=2) for consistency
        self.add_button = tk.Button(
            button_frame, text="➕ Add Exercise", 
            command=self.add_exercise, 
            bg='#374151',  # Dark purple
            fg=self.COLORS['TEXT'],
            font=("Verdana", 12, "bold"), 
            bd=0, relief="flat",
            activebackground=self.COLORS['ACCENT'], 
            activeforeground=self.COLORS['TEXT'],
            padx=20, pady=10, width=18
        )
        self.add_button.pack(side="top", pady=5)
        
        self.start_button = tk.Button(
            button_frame, text="▶️ Start Workout", 
            command=self.start_workout,
            bg='#374151',  # Dark purple
            fg=self.COLORS['TEXT'],
            font=("Verdana", 12, "bold"), 
            bd=0, relief="flat",
            activebackground=self.COLORS['ACCENT'], 
            activeforeground=self.COLORS['TEXT'],
            padx=20, pady=10, width=18
        )
        self.start_button.pack(side="top", pady=5)
        
        self.end_button = tk.Button(
            button_frame, text="⏹️ End Workout", 
            command=self.end_workout, 
            state="disabled",
            bg='#374151',  # Dark purple
            fg=self.COLORS['TEXT'],
            font=("Verdana", 12, "bold"), 
            bd=0, relief="flat",
            activebackground=self.COLORS['ACCENT'], 
            activeforeground=self.COLORS['TEXT'],
            disabledforeground="#666666",
            padx=20, pady=10, width=18
        )
        self.end_button.pack(side="top", pady=5)
        
        view_button = tk.Button(
            button_frame, text="📊 View Progress", 
            command=self.view_progress,
            bg='#374151',  # Dark purple
            fg=self.COLORS['TEXT'],
            font=("Verdana", 12, "bold"), 
            bd=0, relief="flat",
            activebackground=self.COLORS['ACCENT'], 
            activeforeground=self.COLORS['TEXT'],
            padx=20, pady=10, width=18, height=2
        )
        view_button.pack(side="top", pady=5)
        
        # Bind events
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.edit_exercise)
        
        # Update display
        self.update_summary()
        self.refresh_display()
        if self.fitness_manager.workout_active:
            self.start_button.config(state="disabled")
            self.end_button.config(state="normal")
            self.status_label.config(text="Workout: ACTIVE", foreground="#2ecc71")
    
    def add_exercise(self):
        """Add exercise to current workout"""
        exercise = self.exercise_entry.get().strip()
        sets = self.sets_entry.get().strip()
        reps = self.reps_entry.get().strip()
        weight = self.weight_entry.get().strip()
        
        if not exercise or not sets or not reps or not weight:
            messagebox.showwarning("Missing Information", "Please fill in all fields!")
            return
        
        try:
            sets = int(sets)
            reps = int(reps)
            weight = float(weight)
            if sets <= 0 or reps <= 0 or not math.isfinite(weight) or weight < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Input", "Sets and reps must be positive integers; weight must be a finite number, zero or greater.")
            return
        
        exercise_data = {
            "exercise": exercise,
            "sets": sets,
            "reps": reps,
            "weight": weight,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if getattr(self, 'editing_exercise_index', None) is not None:
            self.fitness_manager.update_exercise(self.editing_exercise_index, exercise_data)
            self.editing_exercise_index = None
        else:
            self.fitness_manager.add_exercise(exercise_data)
        self.refresh_display()
        self.update_summary()
        
        self.exercise_entry.delete(0, tk.END)
        self.sets_entry.delete(0, tk.END)
        self.reps_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Added {exercise} to workout!")
    
    def start_workout(self):
        """Start workout session"""
        self.fitness_manager.start_workout()
        self.start_button.config(state="disabled")
        self.end_button.config(state="normal")
        self.status_label.config(text="Workout: ACTIVE", foreground="#2ecc71")
        messagebox.showinfo("Workout Started", "Your workout session has begun! 💪")
    
    def end_workout(self):
        """End workout session"""
        if not self.fitness_manager.current_workout:
            messagebox.showwarning("No Exercises", "Add some exercises before ending the workout!")
            return
        
        exercise_count = len(self.fitness_manager.current_workout)
        if self.fitness_manager.end_workout():
            self.editing_exercise_index = None
            self.start_button.config(state="normal")
            self.end_button.config(state="disabled")
            self.status_label.config(text="Workout: Completed", foreground=self.COLORS['ACCENT_LIGHT'])
            
            messagebox.showinfo(
                "Workout Complete", 
                f"Great job! Completed {exercise_count} exercises.\n"
                f"Workout saved to history!"
            )
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.update_summary()
    
    def update_summary(self):
        """Update workout summary"""
        total_exercises = len(self.fitness_manager.current_workout)
        total_sets = sum(ex["sets"] for ex in self.fitness_manager.current_workout)
        total_reps = sum(ex["sets"] * ex["reps"] for ex in self.fitness_manager.current_workout)
        
        self.summary_label.config(
            text=f"📊 Total Exercises: {total_exercises} | Total Sets: {total_sets} | Total Reps: {total_reps}"
        )
    
    def refresh_display(self):
        """Refresh the exercise display"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for ex in self.fitness_manager.current_workout:
            self.tree.insert("", "end", values=(ex["exercise"], ex["sets"], ex["reps"], ex["weight"]))
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.main_content, tearoff=0,
                          bg=self.COLORS['CARD'], 
                          fg=self.COLORS['TEXT'],
                          activebackground=self.COLORS['ACCENT'],
                          activeforeground=self.COLORS['TEXT'])
            menu.add_command(label="Delete Exercise", command=self.delete_selected)
            menu.post(event.x_root, event.y_root)
    
    def delete_selected(self):
        """Delete selected exercise"""
        selected = self.tree.selection()
        if not selected:
            return
        
        if messagebox.askyesno("Delete Exercise", "Delete this exercise from current workout?"):
            item = selected[0]
            index = self.tree.index(item)
            if index < len(self.fitness_manager.current_workout):
                self.fitness_manager.delete_exercise(index)
                self.editing_exercise_index = None
            self.tree.delete(item)
            self.update_summary()
    
    def edit_exercise(self, event):
        """Edit exercise on double-click"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        index = self.tree.index(item)
        if index >= len(self.fitness_manager.current_workout):
            return
        
        exercise_data = self.fitness_manager.current_workout[index]
        self.exercise_entry.delete(0, tk.END)
        self.exercise_entry.insert(0, exercise_data["exercise"])
        self.sets_entry.delete(0, tk.END)
        self.sets_entry.insert(0, str(exercise_data["sets"]))
        self.reps_entry.delete(0, tk.END)
        self.reps_entry.insert(0, str(exercise_data["reps"]))
        self.weight_entry.delete(0, tk.END)
        self.weight_entry.insert(0, str(exercise_data["weight"]))
        
        self.editing_exercise_index = index
    
    def view_progress(self):
        """Show workout history"""
        if not self.fitness_manager.workout_history:
            messagebox.showinfo("No History", "No workout history yet. Complete a workout to see progress!")
            return
        
        progress_window = tk.Toplevel(self.main_content)
        progress_window.title("Workout History")
        progress_window.geometry("700x500")
        progress_window.configure(bg=self.COLORS['BG'])
        
        title = tk.Label(
            progress_window, text="📊 Workout History", 
            font=("Verdana", 20, "bold"), 
            foreground=self.COLORS['ACCENT_LIGHT'],
            bg=self.COLORS['BG']
        )
        title.pack(pady=20)
        
        # Create styled frame for treeview
        tree_frame = tk.Frame(progress_window, bg=self.COLORS['BG'])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("Date", "Time", "Exercises", "Total Sets")
        history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                    height=20, style="Custom.Treeview")
        
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=150)
        
        for session in self.fitness_manager.workout_history:
            total_sets = sum(ex["sets"] for ex in session["exercises"])
            history_tree.insert("", "end", values=(
                session["date"],
                session["start_time"],
                len(session["exercises"]),
                total_sets
            ))
        
        history_tree.pack(fill="both", expand=True)
        
        total_workouts = len(self.fitness_manager.workout_history)
        total_exercises = sum(len(s["exercises"]) for s in self.fitness_manager.workout_history)
        
        summary = tk.Label(
            progress_window, 
            text=f"Total Workouts: {total_workouts} | Total Exercises: {total_exercises}",
            font=("Verdana", 12, "bold"),
            bg=self.COLORS['BG'],
            fg=self.COLORS['ACCENT_LIGHT']
        )
        summary.pack(pady=10)
