"""Make the skillgap modules importable from tests/ (adds the repo root to sys.path)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
