import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from models import ExpenseManager, FitnessManager, Goal, GoalManager, TaskManager


class TrackerRegressionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def file(self, name):
        return Path(self.folder.name) / name

    def expense(self, date=None, amount=10):
        return {'description': 'Food', 'amount': amount, 'category': 'Food',
                'date': date or datetime.now().strftime('%m/%d/%Y')}

    def test_expense_delete_add_ids_do_not_collide(self):
        manager = ExpenseManager(str(self.file('expenses.json')))
        for _ in range(3):
            manager.add_expense(self.expense())
        manager.delete_expense(manager.expenses[1]['id'])
        manager.add_expense(self.expense())
        self.assertEqual(len({e['id'] for e in manager.expenses}), 3)
        manager.delete_expense(manager.expenses[0]['id'])
        self.assertEqual(len(manager.expenses), 2)

    def test_duplicate_task_ids_repaired_in_memory_without_writing(self):
        path = self.file('tasks.json')
        path.write_text(json.dumps([{'id': 2, 'title': 'A'}, {'id': 2, 'title': 'B'}]))
        original = path.read_bytes()
        manager = TaskManager(str(path))
        self.assertEqual(len({t['id'] for t in manager.tasks}), 2)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual([t['title'] for t in manager.tasks], ['A', 'B'])

    def test_new_task_ids_ignore_caller_collisions(self):
        manager = TaskManager(str(self.file('tasks.json')))
        task = {'id': 1, 'title': 'A', 'deadline': '2026-10-28'}
        manager.add_task(task.copy())
        manager.add_task(task.copy())
        self.assertEqual(len({t['id'] for t in manager.tasks}), 2)

    def test_goal_due_today_has_zero_remaining_days(self):
        goal = Goal('Today', '', 'short-term', datetime.now().strftime('%Y-%m-%d'))
        self.assertEqual(goal.get_days_remaining(), 0)

    def test_monthly_expenses_exclude_other_months(self):
        manager = ExpenseManager(str(self.file('expenses.json')))
        manager.add_expense(self.expense('01/04/2026', 10))
        manager.add_expense(self.expense('02/04/2026', 25))
        self.assertEqual(manager.get_total_expenses('2026-01'), 10)
        self.assertEqual(manager.get_category_totals('2026-02'), {'Food': 25})

    def test_corrupt_files_fail_closed_and_are_preserved(self):
        for cls in [GoalManager, TaskManager, ExpenseManager, FitnessManager]:
            with self.subTest(cls=cls):
                path = self.file(cls.__name__ + '.json')
                path.write_text('{unfinished')
                with self.assertRaises(Exception):
                    cls(str(path))
                self.assertEqual(path.read_text(), '{unfinished')

    def test_nonfinite_and_nonpositive_expenses_rejected(self):
        manager = ExpenseManager(str(self.file('expenses.json')))
        for value in [float('nan'), float('inf'), -1, 0]:
            with self.assertRaises(ValueError):
                manager.add_expense(self.expense(amount=value))
        self.assertEqual(manager.expenses, [])

    def test_invalid_task_date_rejected_before_mutation(self):
        manager = TaskManager(str(self.file('tasks.json')))
        with self.assertRaises(ValueError):
            manager.add_task({'title': 'A', 'deadline': '2026-02-30'})
        self.assertEqual(manager.tasks, [])

    def test_failed_atomic_save_preserves_file_and_memory(self):
        manager = ExpenseManager(str(self.file('expenses.json')))
        manager.add_expense(self.expense())
        before = self.file('expenses.json').read_bytes()
        with patch('os.replace', side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError):
                manager.add_expense(self.expense())
        self.assertEqual(self.file('expenses.json').read_bytes(), before)
        self.assertEqual(len(manager.expenses), 1)

    def test_workout_can_only_end_after_start_and_retains_saved_count(self):
        manager = FitnessManager(str(self.file('fitness.json')))
        manager.add_exercise({'exercise': 'Squat', 'sets': 3, 'reps': 10, 'weight': 0})
        self.assertFalse(manager.end_workout())
        manager.start_workout()
        self.assertTrue(manager.end_workout())
        self.assertEqual(len(manager.workout_history[-1]['exercises']), 1)
        self.assertEqual(manager.current_workout, [])
        self.assertFalse(manager.workout_active)

    def test_workout_draft_survives_reload(self):
        path = str(self.file('fitness.json'))
        manager = FitnessManager(path)
        manager.start_workout()
        manager.add_exercise({'exercise': 'Squat', 'sets': 3, 'reps': 10, 'weight': 0})
        restored = FitnessManager(path)
        self.assertTrue(restored.workout_active)
        self.assertEqual(len(restored.current_workout), 1)

    def test_atomic_save_keeps_previous_version_backup(self):
        path = self.file('expenses.json')
        manager = ExpenseManager(str(path))
        manager.add_expense(self.expense(amount=10))
        previous = path.read_bytes()
        manager.add_expense(self.expense(amount=20))
        self.assertEqual(Path(str(path) + '.bak').read_bytes(), previous)

    def test_corruption_after_load_is_not_overwritten(self):
        path = self.file('tasks.json')
        manager = TaskManager(str(path))
        path.write_text('{broken')
        with self.assertRaises(OSError):
            manager.add_task({'title': 'A', 'deadline': '2026-10-28'})
        self.assertEqual(path.read_text(), '{broken')
        self.assertEqual(manager.tasks, [])

    def test_failed_workout_completion_preserves_draft(self):
        path = self.file('fitness.json')
        manager = FitnessManager(str(path))
        manager.start_workout()
        manager.add_exercise({'exercise': 'Squat', 'sets': 3, 'reps': 10, 'weight': 0})
        before = path.read_bytes()
        with patch('os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                manager.end_workout()
        self.assertTrue(manager.workout_active)
        self.assertEqual(len(manager.current_workout), 1)
        self.assertEqual(manager.workout_history, [])
        self.assertEqual(path.read_bytes(), before)

    def test_edit_exercise_preserves_other_exercises(self):
        path = str(self.file('fitness.json'))
        manager = FitnessManager(path)
        for name in ['Squat', 'Rows']:
            manager.add_exercise({'exercise': name, 'sets': 3, 'reps': 10, 'weight': 0})
        manager.update_exercise(0, {'exercise': 'Squat', 'sets': 4, 'reps': 10, 'weight': 10})
        restored = FitnessManager(path)
        self.assertEqual(len(restored.current_workout), 2)
        self.assertEqual(restored.current_workout[0]['sets'], 4)
        self.assertEqual(restored.current_workout[1]['exercise'], 'Rows')

    def test_invalid_exercise_edit_does_not_change_saved_draft(self):
        path = self.file('fitness.json')
        manager = FitnessManager(str(path))
        manager.add_exercise({'exercise': 'Squat', 'sets': 3, 'reps': 10, 'weight': 0})
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            manager.update_exercise(0, {'exercise': 'Squat', 'sets': -1, 'reps': 10, 'weight': 0})
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(manager.current_workout[0]['sets'], 3)

    def test_tiny_expense_cannot_round_to_zero(self):
        manager = ExpenseManager(str(self.file('expenses.json')))
        with self.assertRaises(ValueError):
            manager.add_expense(self.expense(amount=0.001))

    def goal_manager(self):
        manager = GoalManager(str(self.file('goals.json')))
        goal = Goal('Original', 'Description', 'short-term', '2026-12-01')
        goal.add_milestone('Read')
        goal.add_milestone('Read')
        goal.add_milestone('Finish')
        goal.milestones[0].completed = True
        goal.milestones[2].completed = True
        manager.add_goal(goal)
        return manager, goal

    def test_failed_goal_update_restores_committed_memory(self):
        manager, goal = self.goal_manager()
        before = self.file('goals.json').read_bytes()
        goal.title = 'Rejected'
        with patch('os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                manager.update_goal(goal)
        self.assertEqual(manager.get_goal(goal.id).title, 'Original')
        self.assertEqual(self.file('goals.json').read_bytes(), before)
        manager.add_goal(Goal('Other', '', 'long-term', '2027-01-01'))
        self.assertEqual(GoalManager(manager.filename).get_goal(goal.id).title, 'Original')

    def test_failed_direct_goal_save_restores_milestone(self):
        manager, goal = self.goal_manager()
        goal.toggle_milestone(0)
        with patch('os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                manager.save_goals()
        self.assertTrue(manager.get_goal(goal.id).milestones[0].completed)

    def test_goal_edit_preserves_repeated_milestones_by_occurrence(self):
        manager, goal = self.goal_manager()
        edited = goal.edited('New name', 'New detail', 'long-term', '2027-01-01',
                           ['Read', 'Read', 'Finish', 'Read'])
        self.assertEqual([m.completed for m in edited.milestones], [True, False, True, False])
        self.assertEqual(goal.title, 'Original')
        self.assertEqual(len(goal.milestones), 3)
        self.assertEqual(edited.id, goal.id)

    def test_goal_page_edits_a_detached_copy(self):
        from goals_page import GoalsPage
        manager, goal = self.goal_manager()
        page = GoalsPage.__new__(GoalsPage)
        page.show_goal_form = lambda: setattr(page.editing_goal, 'title', 'Draft')
        page.edit_goal(goal)
        self.assertIsNot(page.editing_goal, goal)
        self.assertEqual(manager.get_goal(goal.id).title, 'Original')

    def test_failed_page_milestone_toggle_does_not_mutate_original(self):
        from goals_page import GoalsPage
        manager, goal = self.goal_manager()
        page = GoalsPage.__new__(GoalsPage)
        page.goal_manager = manager
        page.refresh_goals = lambda: None
        with patch('os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                page.toggle_milestone(goal, 0)
        self.assertTrue(goal.milestones[0].completed)
        self.assertTrue(manager.get_goal(goal.id).milestones[0].completed)


if __name__ == '__main__':
    unittest.main()
