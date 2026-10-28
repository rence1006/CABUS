# models.py
"""
Data models for CABUS application
Contains classes for Goals, Tasks, Expenses, and Fitness data
"""

from datetime import datetime
from typing import List, Optional
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from uuid import uuid4
from desktop_storage import load_json, save_json, repair_ids, positive_number, StorageError

# Ensure imports work from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# No other imports needed - this is a standalone data module


class Milestone:
    """Represents a milestone for a goal"""
    
    def __init__(self, text: str, completed: bool = False):
        self.text = text
        self.completed = completed
    
    def to_dict(self):
        return {"text": self.text, "completed": self.completed}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["text"], data["completed"])


class Goal:
    """Represents a user goal with milestones"""
    
    def __init__(self, title: str, description: str, goal_type: str,
                 target_date: str, goal_id: Optional[str] = None):
        self.id = goal_id or str(uuid4())
        self.title = title
        self.description = description
        self.goal_type = goal_type
        self.target_date = target_date
        self.milestones: List[Milestone] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def add_milestone(self, text: str):
        self.milestones.append(Milestone(text))
        self.updated_at = datetime.now().isoformat()
    
    def toggle_milestone(self, index: int):
        if 0 <= index < len(self.milestones):
            self.milestones[index].completed = not self.milestones[index].completed
            self.updated_at = datetime.now().isoformat()

    def edited(self, title, description, goal_type, target_date, milestone_texts):
        """Build a detached form result, matching repeated milestones by occurrence."""
        check_date(target_date)
        goal = deepcopy(self)
        goal.title = title
        goal.description = description
        goal.goal_type = goal_type
        goal.target_date = target_date
        completion = {}
        for milestone in self.milestones:
            completion.setdefault(milestone.text, []).append(milestone.completed)
        goal.milestones = []
        for text in milestone_texts:
            previous = completion.get(text, [])
            goal.milestones.append(Milestone(text, previous.pop(0) if previous else False))
        goal.updated_at = datetime.now().isoformat()
        return goal
    
    def get_progress(self) -> int:
        if not self.milestones:
            return 0
        completed = sum(1 for m in self.milestones if m.completed)
        return int((completed / len(self.milestones)) * 100)
    
    def get_days_remaining(self) -> int:
        try:
            target = datetime.strptime(self.target_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            delta = target - today
            return delta.days
        except:
            return 0
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "goal_type": self.goal_type,
            "target_date": self.target_date,
            "milestones": [m.to_dict() for m in self.milestones],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        goal = cls(
            data["title"],
            data["description"],
            data["goal_type"],
            data["target_date"],
            data["id"]
        )
        goal.milestones = [Milestone.from_dict(m) for m in data["milestones"]]
        goal.created_at = data.get("created_at", datetime.now().isoformat())
        goal.updated_at = data.get("updated_at", datetime.now().isoformat())
        return goal


def tracker_path(filename, default):
    return str(Path(__file__).resolve().parent / default) if filename is None else filename


def check_date(value, formats=("%Y-%m-%d",)):
    for format_string in formats:
        try:
            return datetime.strptime(value, format_string).date()
        except (ValueError, TypeError):
            pass
    raise ValueError("Please enter a valid date")


class GoalManager:
    """Manage goals without replacing unreadable files."""
    def __init__(self, filename=None):
        self.filename = tracker_path(filename, "goals.json")
        self.goals = []
        self.load_goals()

    def load_goals(self):
        try:
            records = repair_ids(load_json(self.filename, []))
            self.goals = [Goal.from_dict(record) for record in records]
            self._committed_goals = deepcopy(self.goals)
        except (KeyError, TypeError, AttributeError) as error:
            raise StorageError("Goal records are invalid; the original file is unchanged") from error

    def save_goals(self):
        self._commit_goals(self.goals)

    def _commit_goals(self, records):
        try:
            save_json(self.filename, [g.to_dict() for g in records])
        except OSError:
            self.goals = deepcopy(self._committed_goals)
            raise
        self.goals = records
        self._committed_goals = deepcopy(records)

    def add_goal(self, goal):
        check_date(goal.target_date)
        records = self.goals + [goal]
        self._commit_goals(records)

    def get_goal(self, goal_id):
        return next((g for g in self.goals if g.id == goal_id), None)

    def update_goal(self, goal):
        try:
            check_date(goal.target_date)
        except ValueError:
            self.goals = deepcopy(self._committed_goals)
            raise
        if not self.get_goal(goal.id):
            return False
        records = [goal if g.id == goal.id else g for g in self.goals]
        self._commit_goals(records)
        return True

    def delete_goal(self, goal_id):
        records = [g for g in self.goals if g.id != goal_id]
        self._commit_goals(records)

    def get_short_term_goals(self):
        return [g for g in self.goals if g.goal_type == "short-term"]

    def get_long_term_goals(self):
        return [g for g in self.goals if g.goal_type == "long-term"]


class TaskManager:
    def __init__(self, filename=None):
        self.filename = tracker_path(filename, "tasks_data.json")
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        try:
            self.tasks = repair_ids(load_json(self.filename, []))
        except (TypeError, AttributeError) as error:
            raise StorageError("Task records are invalid; the original file is unchanged") from error

    def save_tasks(self):
        save_json(self.filename, self.tasks)

    def add_task(self, task):
        if not task.get('title', '').strip():
            raise ValueError("Please enter a task title")
        check_date(task.get('deadline'))
        task = dict(task, id=str(uuid4()))
        records = self.tasks + [task]
        save_json(self.filename, records)
        self.tasks = records

    def update_task(self, task):
        if not task.get('title', '').strip():
            raise ValueError("Please enter a task title")
        check_date(task.get('deadline'))
        if not any(t.get('id') == task.get('id') for t in self.tasks):
            return False
        records = [dict(task) if t.get('id') == task.get('id') else t for t in self.tasks]
        save_json(self.filename, records)
        self.tasks = records
        return True

    def delete_task(self, task_id):
        records = [t for t in self.tasks if t.get('id') != task_id]
        save_json(self.filename, records)
        self.tasks = records

    def get_tasks_by_status(self, status):
        return [t for t in self.tasks if t.get('status') == status]

    def get_tasks_by_category(self, category):
        return [t for t in self.tasks if t.get('category') == category]


class ExpenseManager:
    def __init__(self, filename=None):
        self.filename = tracker_path(filename, "expenses_data.json")
        self.budget = {"amount": 0}
        self.expenses = []
        self.load_data()

    def load_data(self):
        try:
            data = load_json(self.filename, {})
            budget = data.get('budget', {'amount': 0})
            expenses = data.get('expenses', [])
            if not isinstance(budget, dict) or not isinstance(expenses, list):
                raise ValueError("Invalid expense document")
            positive_number(budget.get('amount', 0), zero_allowed=True)
            self.expenses = repair_ids(expenses)
            for expense in self.expenses:
                positive_number(expense['amount'])
                check_date(expense['date'], ("%m/%d/%Y", "%Y-%m-%d"))
            self.budget = budget
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise StorageError("Expense records are invalid; the original file is unchanged") from error

    def save_data(self):
        save_json(self.filename, {"budget": self.budget, "expenses": self.expenses})

    def set_budget(self, amount):
        amount = positive_number(amount)
        positive_number(round(amount, 2))
        budget = dict(self.budget, amount=round(amount, 2))
        save_json(self.filename, {"budget": budget, "expenses": self.expenses})
        self.budget = budget

    def add_expense(self, expense):
        amount = positive_number(expense.get('amount'))
        positive_number(round(amount, 2))
        check_date(expense.get('date'), ("%m/%d/%Y", "%Y-%m-%d"))
        expense = dict(expense, id=str(uuid4()), amount=round(amount, 2))
        records = [expense] + self.expenses
        save_json(self.filename, {"budget": self.budget, "expenses": records})
        self.expenses = records

    def delete_expense(self, expense_id):
        records = [e for e in self.expenses if e['id'] != expense_id]
        save_json(self.filename, {"budget": self.budget, "expenses": records})
        self.expenses = records

    def get_month_expenses(self, month=None):
        month = month or datetime.now().strftime("%Y-%m")
        check_date(month + '-01')
        return [expense for expense in self.expenses
                if check_date(expense['date'], ("%m/%d/%Y", "%Y-%m-%d")).strftime("%Y-%m") == month]

    def get_total_expenses(self, month=None):
        return round(sum(e['amount'] for e in self.get_month_expenses(month)), 2)

    def get_remaining_budget(self, month=None):
        return round(self.budget["amount"] - self.get_total_expenses(month), 2)

    def get_category_totals(self, month=None):
        category_totals = {}
        for expense in self.get_month_expenses(month):
            category = expense['category']
            category_totals[category] = round(category_totals.get(category, 0) + expense['amount'], 2)
        return category_totals


class FitnessManager:
    def __init__(self, filename=None):
        self.filename = tracker_path(filename, "fitness_tracker_data.json")
        self.workout_history = []
        self.current_workout = []
        self.workout_active = False
        self.workout_start_time = None
        self.load_data()

    def load_data(self):
        try:
            data = load_json(self.filename, {})
            self.workout_history = data.get("workout_history", [])
            self.current_workout = data.get("current_workout", [])
            self.workout_active = data.get("workout_active", False)
            start_time = data.get("workout_start_time")
            self.workout_start_time = datetime.fromisoformat(start_time) if start_time else None
            if not isinstance(self.workout_history, list) or not isinstance(self.current_workout, list):
                raise ValueError("Invalid workout records")
            if self.workout_active and self.workout_start_time is None:
                raise ValueError("Active workout missing start time")
        except (TypeError, ValueError) as error:
            raise StorageError("Fitness records are invalid; the original file is unchanged") from error

    def save_data(self):
        save_json(self.filename, {"workout_history": self.workout_history,
                  "current_workout": self.current_workout,
                  "workout_active": self.workout_active,
                  "workout_start_time": self.workout_start_time.isoformat() if self.workout_start_time else None})

    @staticmethod
    def validate_exercise(exercise_data):
        exercise = dict(exercise_data)
        if not exercise.get('exercise', '').strip():
            raise ValueError("Please enter an exercise name")
        for key in ('sets', 'reps'):
            number = positive_number(exercise.get(key), key.title())
            if not number.is_integer():
                raise ValueError("Sets and reps must be whole numbers")
            exercise[key] = int(number)
        exercise['weight'] = positive_number(exercise.get('weight'), 'Weight', zero_allowed=True)
        return exercise

    def add_exercise(self, exercise_data):
        exercise = self.validate_exercise(exercise_data)
        self.current_workout.append(exercise)
        try:
            self.save_data()
        except OSError:
            self.current_workout.pop()
            raise

    def update_exercise(self, index, exercise_data):
        original = deepcopy(self.current_workout)
        replacement = self.validate_exercise(exercise_data)
        try:
            self.current_workout[index] = replacement
            self.save_data()
        except (OSError, ValueError, IndexError):
            self.current_workout = original
            raise

    def delete_exercise(self, index):
        original = self.current_workout.copy()
        self.current_workout.pop(index)
        try:
            self.save_data()
        except OSError:
            self.current_workout = original
            raise

    def start_workout(self):
        if self.workout_active:
            return
        previous = self.workout_start_time
        self.workout_active = True
        self.workout_start_time = datetime.now()
        try:
            self.save_data()
        except OSError:
            self.workout_active = False
            self.workout_start_time = previous
            raise

    def end_workout(self):
        if not self.workout_active or not self.current_workout or self.workout_start_time is None:
            return False
        workout_session = {"date": datetime.now().strftime("%Y-%m-%d"),
                           "start_time": self.workout_start_time.strftime("%H:%M:%S"),
                           "end_time": datetime.now().strftime("%H:%M:%S"),
                           "exercises": deepcopy(self.current_workout)}
        draft = self.current_workout
        self.workout_history.append(workout_session)
        self.current_workout = []
        self.workout_active = False
        try:
            self.save_data()
        except OSError:
            self.workout_history.pop()
            self.current_workout = draft
            self.workout_active = True
            raise
        return True

    def clear_current_workout(self):
        draft = self.current_workout
        self.current_workout = []
        try:
            self.save_data()
        except OSError:
            self.current_workout = draft
            raise
