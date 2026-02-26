import os
import sys
from pathlib import Path


def _ensure_project_root_on_sys_path() -> None:
    # Add workspace root to sys.path so package-style imports work under different runners
    this_file = Path(__file__).resolve()
    project_root = this_file.parents[3] if len(this_file.parents) >= 4 else this_file.parents[-1]
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


_ensure_project_root_on_sys_path()




