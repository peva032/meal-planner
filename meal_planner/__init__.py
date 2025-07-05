"""
Meal Planner - A simple meal planning and shopping list generation application.

This package provides:
- Database client for storing meals and ingredients
- Standardized units for consistent measurements
- Streamlit web application for user interaction
"""

from .db import DbClient
from .units import Unit
from . import streamlit_app
from . import cli

__version__ = "1.0.0"
__author__ = "Meal Planner Team"

# Public API
__all__ = [
    "DbClient",
    "Unit",
    "streamlit_app",
    "cli",
]
