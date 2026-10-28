"""Safe JSON persistence for the desktop trackers."""
import copy
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4


class StorageError(OSError):
    pass


def report_storage_error(message):
    # Avoid creating an implicit Tk window in tests or command-line checks.
    import tkinter
    if tkinter._default_root is not None:
        from tkinter import messagebox
        messagebox.showerror('Tracker data could not be saved', message)


def load_json(filename, default):
    path = Path(filename)
    if not path.exists():
        return copy.deepcopy(default)
    try:
        with path.open(encoding='utf-8') as stream:
            data = json.load(stream)
        if not isinstance(data, type(default)):
            raise ValueError('Unexpected document structure')
        return data
    except (OSError, ValueError, TypeError) as error:
        message = f'Could not read {path.name}. The original file has been preserved. Restore a valid backup before continuing.\n\n{error}'
        report_storage_error(message)
        raise StorageError(message) from error


def save_json(filename, data):
    path = Path(filename)
    temporary = None
    try:
        # Serialize before touching either the live file or its backup.
        payload = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)
        if path.exists():
            load_json(path, [] if isinstance(data, list) else {})
        descriptor, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            shutil.copy2(path, str(path) + '.bak')
        os.replace(temporary, path)
    except (OSError, ValueError, TypeError) as error:
        message = f'Could not save {path.name}. Your previous file has been preserved.\n\n{error}'
        report_storage_error(message)
        raise StorageError(message) from error
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def repair_ids(records):
    seen = set()
    for record in records:
        key = record.get('id')
        if key is None or str(key) in seen:
            record['id'] = str(uuid4())
        seen.add(str(record['id']))
    return records


def positive_number(value, label='Amount', zero_allowed=False):
    if isinstance(value, bool):
        raise ValueError(f'{label} must be a number')
    try:
        number = float(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f'{label} must be a number') from error
    if not math.isfinite(number) or number < 0 or (number == 0 and not zero_allowed):
        raise ValueError(f'{label} must be finite and {"zero or greater" if zero_allowed else "greater than zero"}')
    return number
