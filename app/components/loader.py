"""Helper for loading example modules whose paths begin with a digit.

Python identifiers can't start with a digit, so the ``examples/01_bond_pricing/``
style paths can't be imported with normal ``import`` statements. This wraps
``importlib`` so pages can stay readable.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_example(example_dir: str, module: str):
    """Load ``examples/<example_dir>/<module>.py`` and return the module object."""
    file_path = ROOT / "examples" / example_dir / f"{module}.py"
    fq_name = f"_ex_{example_dir}__{module}"
    if fq_name in sys.modules:
        return sys.modules[fq_name]
    spec = importlib.util.spec_from_file_location(fq_name, file_path)
    assert spec is not None and spec.loader is not None, f"cannot load {file_path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[fq_name] = mod
    spec.loader.exec_module(mod)
    return mod
