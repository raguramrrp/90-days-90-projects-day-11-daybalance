"""
DayBalance UI Theme System & Visual Token Injector
Implements the Sage Green, Warm Ivory & Editorial Wellness design system
with dynamic Light/Dark mode support, top navigation harmony, and Plotly styling.
"""

from typing import Any, Dict, Optional
import streamlit as st
from config import THEME_TOKENS


def get_current_theme() -> str:
    """Returns the active theme ('light' or 'dark') from session state or profile preference."""
    try:
        if "active_theme" not in st.session_state:
            st.session_state["active_theme"] = "light"
        return st.session_state["active_theme"]
    except Exception:
        return "light"


def set_current_theme(theme_mode: str) -> None:
    """Sets and persists the active theme mode."""
    if theme_mode in ("light", "dark"):
        st.session_state["active_theme"] = theme_mode


def get_theme_tokens(theme_mode: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves color and styling tokens for the active theme."""
    mode = theme_mode or get_current_theme()
    return THEME_TOKENS.get(mode, THEME_TOKENS["light"])


def apply_custom_css(theme_mode: Optional[str] = None) -> None:
    """
    Injects custom CSS adhering strictly to the Sage Green & Warm Ivory editorial design system.
    Provides calm wellness aesthetics, clean typographic hierarchy, and responsive styling.
    """
    tokens = get_theme_tokens(theme_mode)

    css = f"""
    <style>
        /* DayBalance Root CSS Variables */
        :root {{
            --db-bg: {tokens['bg_primary']};
            --db-secondary: {tokens['bg_secondary']};
            --db-surface: {tokens['bg_card']};
            --db-surface-hover: {tokens['bg_card_hover']};
            --db-border: {tokens['border']};
            --db-border-subtle: {tokens.get('border_subtle', tokens['border'])};
            --db-text: {tokens['text_primary']};
            --db-text-muted: {tokens['text_muted']};
            --db-text-secondary: {tokens['text_secondary']};
            --db-accent: {tokens['accent']};
            --db-accent-hover: {tokens['accent_hover']};
            --db-accent-light: {tokens['accent_light']};
            --db-accent-border: {tokens.get('accent_border', tokens['border'])};
            --db-success: {tokens['status_success']};
            --db-warning: {tokens['status_warning']};
            --db-danger: {tokens['status_danger']};
            --db-info: {tokens['status_info']};
        }}

        /* Global App Canvas & Background */
        .stApp {{
            background-color: var(--db-bg) !important;
            color: var(--db-text) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }}

        /* Native Local Desktop App Mode: Clean chrome without web clutter */
        #MainMenu {{ visibility: hidden !important; display: none !important; }}
        header[data-testid="stHeader"] .stDeployButton {{ display: none !important; }}
        footer {{ visibility: hidden !important; display: none !important; }}
        div[data-testid="stDecoration"] {{ display: none !important; }}
        div[data-testid="stToolbar"] {{ display: none !important; }}
        div[data-testid="stStatusWidget"] {{ display: none !important; }}
        .viewerBadge_container__1QSob {{ display: none !important; }}

        /* Streamlit Top Header & Navigation Refinement */
        header[data-testid="stHeader"] {{
            background-color: var(--db-bg) !important;
            border-bottom: 1px solid var(--db-border-subtle) !important;
        }}
        [data-testid="stTopLevelNav"] {{
            background-color: var(--db-surface) !important;
            padding: 0.35rem 1rem !important;
            border-bottom: 1px solid var(--db-border) !important;
        }}
        [data-testid="stTopLevelNav"] *,
        [data-testid="stTopLevelNav"] a,
        [data-testid="stTopLevelNav"] button,
        [data-testid="stTopLevelNav"] span,
        [data-testid="stTopLevelNav"] p,
        [data-testid="stTopLevelNav"] div {{
            color: var(--db-text-secondary) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.86rem !important;
            text-decoration: none !important;
        }}
        [data-testid="stTopLevelNav"] svg {{
            fill: var(--db-text-secondary) !important;
            stroke: var(--db-text-secondary) !important;
        }}
        [data-testid="stTopLevelNav"] button,
        [data-testid="stTopLevelNav"] a {{
            color: var(--db-text-secondary) !important;
            font-weight: 500 !important;
            font-size: 0.86rem !important;
            border-radius: 8px !important;
            padding: 0.35rem 0.75rem !important;
            transition: all 0.15s ease-in-out !important;
            border: 1px solid transparent !important;
        }}
        [data-testid="stTopLevelNav"] button:hover,
        [data-testid="stTopLevelNav"] a:hover,
        [data-testid="stTopLevelNav"] button:hover *,
        [data-testid="stTopLevelNav"] a:hover * {{
            color: var(--db-accent) !important;
            background-color: var(--db-secondary) !important;
        }}
        [data-testid="stTopLevelNav"] [aria-current="page"],
        [data-testid="stTopLevelNav"] [aria-selected="true"],
        [data-testid="stTopLevelNav"] [data-active="true"] {{
            color: #059669 !important;
            background-color: rgba(16, 185, 129, 0.12) !important;
            border: 1px solid #10B981 !important;
            font-weight: 700 !important;
        }}
        [data-testid="stTopLevelNav"] [aria-current="page"] *,
        [data-testid="stTopLevelNav"] [aria-selected="true"] *,
        [data-testid="stTopLevelNav"] [data-active="true"] * {{
            color: #059669 !important;
            font-weight: 700 !important;
        }}
        [data-testid="stTopLevelNav"] [aria-current="page"] svg,
        [data-testid="stTopLevelNav"] [aria-selected="true"] svg,
        [data-testid="stTopLevelNav"] [data-active="true"] svg {{
            fill: #059669 !important;
            stroke: #059669 !important;
        }}

        /* Compact Top Brand & Utility Header */
        .db-top-nav-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.6rem 0.5rem 0.8rem 0.5rem;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--db-border-subtle);
        }}
        .db-brand-badge {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}
        .db-brand-logo {{
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--db-accent);
            letter-spacing: -0.02em;
        }}
        .db-brand-tagline {{
            font-size: 0.78rem;
            color: var(--db-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding-left: 0.6rem;
            border-left: 1px solid var(--db-border);
        }}

        /* Page Headings - Compact & Context-Rich */
        .db-header-container {{
            margin-bottom: 1.25rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--db-border-subtle);
        }}
        .db-header-title {{
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--db-text);
            margin: 0;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }}
        .db-header-subtitle {{
            font-size: 0.9rem;
            color: var(--db-text-secondary);
            margin-top: 0.25rem;
            margin-bottom: 0;
            line-height: 1.4;
        }}

        /* Minimal Typography-Led Metric Strip */
        .db-metric-strip {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            padding: 1.1rem 1.4rem;
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 8px;
            margin-bottom: 1.25rem;
        }}
        .db-editorial-metric {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-right: 1px solid var(--db-border-subtle);
            padding-right: 1rem;
        }}
        .db-editorial-metric:last-child {{
            border-right: none;
            padding-right: 0;
        }}
        .db-metric-label {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--db-text-muted);
            margin-bottom: 0.25rem;
        }}
        .db-metric-val {{
            font-size: 1.85rem;
            font-weight: 700;
            color: var(--db-text);
            line-height: 1.15;
            letter-spacing: -0.02em;
        }}
        .db-metric-sub {{
            font-size: 0.8rem;
            color: var(--db-text-secondary);
            margin-top: 0.35rem;
            line-height: 1.3;
        }}

        /* Calm Editorial & Modern Bento Cards */
        .db-card {{
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 12px;
            padding: 1.1rem 1.35rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .db-card:hover {{
            border-color: var(--db-accent-border);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        }}

        /* Modern Bento Stat Hero Cards */
        .db-bento-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-bottom: 1.25rem;
        }}
        .db-bento-card {{
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 12px;
            padding: 1.1rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 1.1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            transition: all 0.15s ease-in-out;
        }}
        .db-bento-card:hover {{
            border-color: var(--db-accent);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        }}
        .db-bento-icon {{
            width: 46px;
            height: 46px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            flex-shrink: 0;
        }}
        .db-bento-content {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .db-bento-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--db-text-muted);
            margin-bottom: 0.2rem;
        }}
        .db-bento-value {{
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--db-text);
            line-height: 1.15;
            letter-spacing: -0.02em;
        }}
        .db-bento-sub {{
            font-size: 0.78rem;
            color: var(--db-text-secondary);
            margin-top: 0.2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .db-stat-badge {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--db-accent);
            background: var(--db-accent-light);
            border: 1px solid var(--db-accent-border);
            padding: 0.12rem 0.45rem;
            border-radius: 4px;
        }}

        /* Category Pastel Tags */
        .db-cat-tag {{
            display: inline-block;
            font-size: 0.74rem;
            font-weight: 600;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            letter-spacing: 0.01em;
        }}
        .db-cat-study {{ background: #E6F7F0; color: #065F46; }}
        .db-cat-active {{ background: #DEF7EC; color: #047857; }}
        .db-cat-mind {{ background: #F3E8FF; color: #6B21A8; }}
        .db-cat-work {{ background: #FEF3C7; color: #92400E; }}
        .db-cat-health {{ background: #FEE2E2; color: #991B1B; }}
        .db-cat-creative {{ background: #FCE7F3; color: #9D174D; }}
        .db-cat-custom {{ background: #F1F5F9; color: #334155; }}

        /* Schedule Table & Badges */
        .db-pill-done-status {{
            display: inline-block;
            background: #DEF7EC;
            color: #03543F;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 6px 18px;
            border-radius: 6px;
            text-align: center;
        }}
        .db-check-circle {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #059669;
            color: #FFFFFF;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 800;
            flex-shrink: 0;
        }}
        .db-uncheck-circle {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 2px solid #CBD5E1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        /* 7-Day Consistency Weekday History Cards */
        .db-history-card {{
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 12px;
            padding: 1.1rem 1.35rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            margin-top: 1.25rem;
        }}
        .db-day-box {{
            flex: 1;
            padding: 0.75rem 0.5rem;
            border-radius: 8px;
            border: 1px solid var(--db-border-subtle);
            background: var(--db-surface);
            text-align: center;
        }}
        .db-day-box-today {{
            flex: 1;
            padding: 0.75rem 0.5rem;
            border-radius: 8px;
            border: 1.5px solid #10B981;
            background: rgba(16, 185, 129, 0.08);
            text-align: center;
        }}
        .db-dot-done {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #059669;
            margin: 0 2px;
        }}
        .db-dot-pending {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #CBD5E1;
            margin: 0 2px;
        }}

        /* Approved Bento Grid & Hero Header System */
        .db-hero-header-box {{
            text-align: center;
            padding: 1rem 0 1.25rem 0;
            margin-bottom: 0.25rem;
        }}
        .db-hero-date {{
            font-size: 2.1rem;
            font-weight: 800;
            color: var(--db-text);
            margin: 0;
            line-height: 1.15;
            letter-spacing: -0.025em;
        }}
        .db-hero-sub {{
            font-size: 0.95rem;
            color: var(--db-text-secondary);
            margin-top: 0.35rem;
            font-weight: 500;
        }}

        /* Bento 6-Card Modules */
        .db-bento-module {{
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 14px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .db-bento-module:hover {{
            border-color: var(--db-accent);
        }}
        .db-bento-module-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--db-text);
            margin: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .db-bento-module-sub {{
            font-size: 0.78rem;
            color: var(--db-text-secondary);
            margin-top: 0.2rem;
            margin-bottom: 0.85rem;
        }}

        /* Bento Checklist items */
        .db-chk-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.55rem 0.65rem;
            border-radius: 8px;
            background: var(--db-secondary);
            border: 1px solid var(--db-border-subtle);
            margin-bottom: 0.45rem;
        }}
        .db-chk-left {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            overflow: hidden;
        }}
        .db-chk-box-done {{
            width: 22px;
            height: 22px;
            border-radius: 6px;
            background: #10B981;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 800;
            flex-shrink: 0;
        }}
        .db-chk-box-pending {{
            width: 22px;
            height: 22px;
            border-radius: 6px;
            border: 1.5px solid var(--db-border);
            background: var(--db-surface);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .db-chk-name-done {{
            font-size: 0.88rem;
            font-weight: 500;
            color: var(--db-text-muted);
            text-decoration: line-through;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .db-chk-name-pending {{
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--db-text);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* Wearable Top Banner */
        .db-wearable-top-banner {{
            background: var(--db-accent-light);
            border: 1px solid var(--db-accent-border);
            color: var(--db-accent);
            padding: 0.45rem 0.85rem;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }}

        /* Streak Giant Card */
        .db-streak-hero-val {{
            font-size: 3rem;
            font-weight: 900;
            color: var(--db-text);
            line-height: 1;
            letter-spacing: -0.03em;
        }}

        /* Consistency Giant Card */
        .db-consistency-hero-val {{
            font-size: 2.8rem;
            font-weight: 800;
            color: var(--db-accent);
            line-height: 1.1;
            letter-spacing: -0.02em;
        }}

        /* Interactive Habit Card for 1-Click Dashboard Completion */
        .db-habit-row {{
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 12px;
            padding: 0.85rem 1.15rem;
            margin-bottom: 0.65rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            transition: all 0.15s ease-in-out;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        }}
        .db-habit-row:hover {{
            border-color: var(--db-accent);
            background: var(--db-surface-hover);
        }}
        .db-habit-completed {{
            border-color: rgba(16, 185, 129, 0.35);
            background: rgba(16, 185, 129, 0.03);
        }}

        /* Everyday.app 7-Day Consistency Squircle Chain */
        .db-chain-container {{
            display: flex;
            gap: 5px;
            align-items: center;
        }}
        .db-day-pill {{
            width: 24px;
            height: 24px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.68rem;
            font-weight: 700;
            transition: transform 0.15s ease;
        }}
        .db-day-pill:hover {{
            transform: scale(1.15);
        }}
        .db-pill-done {{
            background-color: var(--db-accent);
            color: #ffffff;
        }}
        .db-pill-rest {{
            background-color: rgba(245, 158, 11, 0.18);
            color: var(--db-warning);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        .db-pill-missed {{
            background-color: rgba(239, 68, 68, 0.12);
            color: var(--db-danger);
            border: 1px solid rgba(239, 68, 68, 0.25);
        }}
        .db-pill-pending {{
            background-color: var(--db-secondary);
            color: var(--db-text-muted);
            border: 1px dashed var(--db-border);
        }}


        /* Streak Flame Badge */
        .db-streak-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.82rem;
            font-weight: 700;
            color: #D97706;
            background: #FEF3C7;
            border: 1px solid rgba(217, 119, 6, 0.28);
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
        }}

        /* Daily Check-in Quick Hero Banner */
        .db-quick-checkin-banner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-left: 4px solid var(--db-accent);
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-bottom: 1.25rem;
        }}

        /* Status Badges - Restrained Botanical Tones */
        .db-badge {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            text-align: center;
            letter-spacing: 0.02em;
        }}
        .status-success {{
            background-color: var(--db-accent-light);
            color: var(--db-accent);
            border: 1px solid var(--db-accent-border);
        }}
        .status-warning {{
            background-color: rgba(184, 123, 46, 0.12);
            color: var(--db-warning);
            border: 1px solid rgba(184, 123, 46, 0.28);
        }}
        .status-danger {{
            background-color: rgba(184, 74, 57, 0.12);
            color: var(--db-danger);
            border: 1px solid rgba(184, 74, 57, 0.28);
        }}
        .status-info {{
            background-color: rgba(74, 109, 124, 0.12);
            color: var(--db-info);
            border: 1px solid rgba(74, 109, 124, 0.28);
        }}
        .status-rest {{
            background-color: rgba(124, 141, 131, 0.12);
            color: var(--db-text-secondary);
            border: 1px solid rgba(124, 141, 131, 0.25);
        }}
        .status-skipped {{
            background-color: rgba(124, 141, 131, 0.1);
            color: var(--db-text-muted);
            border: 1px solid rgba(124, 141, 131, 0.2);
        }}
        .status-pending {{
            background-color: var(--db-accent-light);
            color: var(--db-accent);
            border: 1px solid var(--db-accent-border);
        }}

        /* Streamlit Button Restyling */
        .stButton button,
        .stButton button[kind="secondary"] {{
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            padding: 0.45rem 1rem !important;
            transition: all 0.15s ease-in-out !important;
            border: 1px solid var(--db-border) !important;
            background-color: var(--db-surface) !important;
            color: var(--db-text) !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
        }}
        .stButton button:hover,
        .stButton button[kind="secondary"]:hover {{
            border-color: #10B981 !important;
            color: #059669 !important;
            background-color: var(--db-secondary) !important;
        }}
        .stButton button[kind="primary"],
        .stButton button[data-testid="baseButton-primary"] {{
            background-color: #059669 !important;
            color: #ffffff !important;
            border: 1px solid #047857 !important;
            box-shadow: 0 1px 3px rgba(5, 150, 105, 0.2) !important;
        }}
        .stButton button[kind="primary"]:hover,
        .stButton button[data-testid="baseButton-primary"]:hover {{
            background-color: #047857 !important;
            color: #ffffff !important;
            border-color: #047857 !important;
        }}
        .stButton button:focus-visible {{
            outline: 2px solid #059669 !important;
            outline-offset: 2px !important;
        }}

        /* Focus & Form Elements */
        button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {{
            outline: 2px solid var(--db-accent) !important;
            outline-offset: 2px !important;
        }}
        .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {{
            background-color: var(--db-surface) !important;
            border: 1px solid var(--db-border) !important;
            border-radius: 6px !important;
            color: var(--db-text) !important;
        }}

        /* Streamlit Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 1.5rem !important;
            border-bottom: 1px solid var(--db-border-subtle) !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            padding: 0.5rem 0.25rem !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            color: var(--db-text-secondary) !important;
            border: none !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--db-accent) !important;
            font-weight: 700 !important;
            border-bottom: 2px solid var(--db-accent) !important;
        }}

        /* Streamlit Progress Bar */
        .stProgress > div > div > div > div {{
            background-color: var(--db-accent) !important;
        }}

        /* Futuristic Focus Timer HUD Box */
        .db-timer-hero {{
            text-align: center;
            padding: 2.2rem 1.6rem;
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 16px;
            margin: 0.5rem 0 1rem 0;
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.08), 0 4px 20px rgba(0, 0, 0, 0.03);
            position: relative;
            overflow: hidden;
            transition: all 0.25s ease-in-out;
        }}
        .db-timer-hero:hover {{
            border-color: var(--db-accent);
            box-shadow: 0 0 40px rgba(16, 185, 129, 0.14), 0 6px 24px rgba(0, 0, 0, 0.05);
        }}
        .db-timer-clock {{
            font-size: 4.4rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', 'SF Mono', 'Roboto Mono', 'Fira Code', monospace;
            color: var(--db-accent);
            letter-spacing: 0.08em;
            text-shadow: 0 0 25px rgba(16, 185, 129, 0.4);
            line-height: 1.1;
            margin: 0.6rem 0;
        }}
        .db-hud-status {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            margin-bottom: 0.75rem;
        }}
        .db-hud-status.status-running {{
            background: var(--db-accent-light);
            color: var(--db-accent);
            border: 1px solid var(--db-accent-border);
        }}
        .db-hud-status.status-paused {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--db-warning);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        .db-hud-status.status-ready {{
            background: var(--db-border-subtle);
            color: var(--db-text-muted);
            border: 1px solid var(--db-border);
        }}
        .db-pulse-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--db-accent);
            box-shadow: 0 0 8px var(--db-accent);
            display: inline-block;
        }}

        /* Accessible Calendar Status Legend */
        .db-legend-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            padding: 0.6rem 0.9rem;
            background: var(--db-secondary);
            border: 1px solid var(--db-border-subtle);
            border-radius: 6px;
            margin-top: 0.5rem;
            font-size: 0.8rem;
        }}
        .db-legend-item {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
            color: var(--db-text-secondary);
        }}

        /* Spacious Daily Check-in Habit Cards & Wellness Tiles */
        .db-checkin-habit-card {{
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 12px;
            padding: 1.15rem 1.35rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.18s ease-in-out;
        }}
        .db-checkin-habit-card:hover {{
            border-color: #10B981;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.06);
        }}
        .db-checkin-habit-completed {{
            border-left: 4px solid #059669 !important;
            background: rgba(16, 185, 129, 0.02);
        }}
        .db-target-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.76rem;
            font-weight: 600;
            padding: 0.2rem 0.65rem;
            border-radius: 9999px;
            background: var(--db-secondary);
            color: var(--db-text-secondary);
            border: 1px solid var(--db-border);
        }}
        .db-routine-pill {{
            display: inline-flex;
            align-items: center;
            font-size: 0.74rem;
            font-weight: 600;
            padding: 0.2rem 0.55rem;
            border-radius: 9999px;
            background: rgba(2, 132, 199, 0.08);
            color: #0284C7;
            border: 1px solid rgba(2, 132, 199, 0.2);
        }}
        .db-wellness-tile {{
            background: var(--db-surface);
            border: 1px solid var(--db-border);
            border-radius: 12px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_plotly_layout(theme_mode: Optional[str] = None) -> Dict[str, Any]:
    """Generates standard Plotly layout parameters for visual harmony with Sage & Ivory theme."""
    tokens = get_theme_tokens(theme_mode)
    return {
        "template": tokens["plotly_template"],
        "paper_bgcolor": tokens["chart_bg"],
        "plot_bgcolor": tokens["chart_bg"],
        "font": {
            "family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            "color": tokens["text_primary"],
            "size": 11
        },
        "margin": {"l": 45, "r": 20, "t": 45, "b": 35},
        "xaxis": {
            "gridcolor": tokens["chart_grid"],
            "linecolor": tokens["border"],
            "tickfont": {"color": tokens["text_secondary"], "size": 10}
        },
        "yaxis": {
            "gridcolor": tokens["chart_grid"],
            "linecolor": tokens["border"],
            "tickfont": {"color": tokens["text_secondary"], "size": 10}
        }
    }
