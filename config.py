"""
DayBalance Configuration & Global Settings
Centralized management of database paths, analytical constants, and UI color palettes.
"""

from pathlib import Path
import os

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DEFAULT_DB_PATH = DATA_DIR / "daybalance.db"
DB_PATH = Path(os.getenv("DAYBALANCE_DB_PATH", str(DEFAULT_DB_PATH)))

# Analytical Constants
# Minimum number of valid paired observations required for reliable correlation analysis
MIN_CORRELATION_PAIRS = int(os.getenv("DAYBALANCE_MIN_SAMPLE_SIZE", "7"))
RECOMMENDED_CORRELATION_PAIRS = 14

# Habit Categories
HABIT_CATEGORIES = [
    "Health & Fitness",
    "Study & Academic",
    "Productivity & Deep Work",
    "Movement & Active",
    "Mindfulness & Well-being",
    "Creative & Personal",
    "Custom"
]

# Habit Measurement Types
MEASUREMENT_TYPES = {
    "boolean": "Completion (Yes/No)",
    "duration_minutes": "Duration (Minutes)",
    "count": "Repetitions / Count",
    "numeric_target": "Custom Numeric Target"
}

# Habit Frequencies
FREQUENCIES = {
    "daily": "Every Day (Mon-Sun)",
    "weekdays": "Weekdays Only (Mon-Fri)",
    "weekends": "Weekends Only (Sat-Sun)",
    "custom_days": "Custom Selected Days"
}

# Weekday Mapping (0 = Monday, 6 = Sunday)
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Visual Palette Tokens (Modern Delightful Personal Habit Tracker Palette)
THEME_TOKENS = {
    "light": {
        "name": "Fresh Daybreak (Modern Habit Tracker)",
        "bg_primary": "#F8FAFC",       # Clean soft canvas (Slate 50)
        "bg_secondary": "#F1F5F9",     # Slate 100 neutral containers
        "bg_card": "#FFFFFF",          # Crisp white card surface
        "bg_card_hover": "#F8FAFC",    # Card hover
        "border": "#E2E8F0",           # Soft modern border (Slate 200)
        "border_subtle": "#F1F5F9",    # Fine divider
        "text_primary": "#0F172A",     # Deep charcoal typography (Slate 900)
        "text_secondary": "#475569",   # Muted slate secondary (Slate 600)
        "text_muted": "#64748B",       # Slate 500 metadata
        "accent": "#10B981",           # Vibrant Emerald Mint (Habitify/Everyday green)
        "accent_hover": "#059669",     # Deep emerald hover
        "accent_light": "rgba(16, 185, 129, 0.12)",
        "accent_border": "rgba(16, 185, 129, 0.28)",
        "status_success": "#10B981",   # Vibrant Emerald Green
        "status_warning": "#F59E0B",   # Warm Amber / Streak Gold
        "status_danger": "#EF4444",    # Coral Red
        "status_info": "#0284C7",      # Sky Blue (Focus / Study)
        "streak_orange": "#F97316",    # Flame Orange
        "mind_purple": "#8B5CF6",      # Mindfulness Violet
        "plotly_template": "plotly_white",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#F1F5F9"
    },
    "dark": {
        "name": "Midnight Obsidian (Deep OLED Habit Tracker)",
        "bg_primary": "#0B0F17",       # Rich midnight obsidian
        "bg_secondary": "#131B26",     # Dark container surface
        "bg_card": "#1A2332",          # Elevated dark card
        "bg_card_hover": "#222D3E",    # Card hover
        "border": "#26354A",           # Subtle dark border
        "border_subtle": "#1B2636",    # Fine dark divider
        "text_primary": "#F8FAFC",     # Bright white text (Slate 50)
        "text_secondary": "#94A3B8",   # Soft slate secondary (Slate 400)
        "text_muted": "#64748B",       # Slate 500 metadata
        "accent": "#34D399",           # Luminous Emerald Mint
        "accent_hover": "#10B981",     # Mint hover
        "accent_light": "rgba(52, 211, 153, 0.16)",
        "accent_border": "rgba(52, 211, 153, 0.32)",
        "status_success": "#34D399",   # Luminous Green
        "status_warning": "#FBBF24",   # Warm Gold
        "status_danger": "#F87171",    # Soft Coral
        "status_info": "#38BDF8",      # Vibrant Sky Blue
        "streak_orange": "#FB923C",    # Bright Flame
        "mind_purple": "#A78BFA",      # Soft Lavender
        "plotly_template": "plotly_dark",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#1F2B3B"
    }
}
