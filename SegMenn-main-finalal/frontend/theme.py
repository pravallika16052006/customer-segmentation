"""
SegMen Shared Visual Design System & UI Components.

Owns visual tokens, typography, CSS injection, responsive card builders,
and Plotly chart styling for a consistent Forest Green + Ivory
customer analytics dashboard.
"""

from __future__ import annotations

import html as _html
from typing import Any, Dict, List

import streamlit as st


# ============================================================
# SAFE HTML INJECTION
# ============================================================

def _md(html_str: str) -> None:
    """Safely render HTML without markdown indentation glitches."""
    lines = [
        line.strip()
        for line in html_str.strip().splitlines()
    ]

    st.markdown(
        " ".join(
            line for line in lines if line
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# DESIGN TOKENS
# ============================================================

COLORS = {
    # Main surfaces
    "bg": "#F5F6F1",
    "sidebar": "#183A37",
    "surface": "#FFFDF7",
    "surface_hover": "#EDEFE6",

    # Borders
    "border": "#DDE3DC",
    "border_strong": "#C5CDC2",

    # Primary Forest Green
    "accent": "#285943",
    "accent_soft": "rgba(40, 89, 67, 0.10)",

    # Secondary Sage Green
    "accent_2": "#6B8F71",
    "accent_2_soft": "rgba(107, 143, 113, 0.12)",

    # Typography
    "text": "#26332F",
    "text_secondary": "#71807A",
    "text_muted": "#87966F",

    # Status / semantic colors
    "green": "#285943",
    "green_soft": "rgba(40, 89, 67, 0.10)",

    # Soft Gold
    "amber": "#C7A86B",
    "amber_soft": "rgba(199, 168, 107, 0.15)",

    # Error
    "red": "#B85C5C",
    "red_soft": "rgba(184, 92, 92, 0.10)",
}


# ============================================================
# GLOBAL CLUSTER COLORS
# ============================================================

CLUSTER_COLORS = {
    # Internal K-Means IDs
    0: "#285943",
    1: "#6B8F71",
    2: "#C7A86B",

    # UI display labels
    "Cluster 1": "#285943",
    "Cluster 2": "#6B8F71",
    "Cluster 3": "#C7A86B",

    # Segment names
    "Premium Customers": "#285943",
    "Budget / Deal-Oriented Customers": "#6B8F71",
    "Regular Customers": "#C7A86B",
    "High Value Customers": "#285943",
}


SEGMENT_STYLES = {
    "Premium Customers": {
        "accent": "green",
        "color": "#285943",
        "soft": "rgba(40, 89, 67, 0.12)",
        "icon": "trophy",
    },

    "Budget / Deal-Oriented Customers": {
        "accent": "accent_2",
        "color": "#6B8F71",
        "soft": "rgba(107, 143, 113, 0.14)",
        "icon": "tag",
    },

    "Regular Customers": {
        "accent": "amber",
        "color": "#C7A86B",
        "soft": "rgba(199, 168, 107, 0.16)",
        "icon": "groups",
    },

    "High Value Customers": {
        "accent": "green",
        "color": "#285943",
        "soft": "rgba(40, 89, 67, 0.12)",
        "icon": "trophy",
    },
}


def segment_style(name: Any) -> dict:
    """Return visual styling for a customer segment or cluster ID."""
    sname = str(name).strip()
    lowered = sname.lower()

    # Internal K-Means cluster 0
    if sname in ("0", "Cluster 0"):
        return SEGMENT_STYLES["Premium Customers"]

    # Premium / High Value names
    if "premium" in lowered or "high value" in lowered:
        return SEGMENT_STYLES["Premium Customers"]

    # Internal K-Means cluster 1
    if sname == "1":
        return SEGMENT_STYLES["Budget / Deal-Oriented Customers"]

    # Preserve existing UI convention for Cluster 1 / Cluster 2
    # when the actual segment name contains budget/deal terms.
    if (
        sname in ("Cluster 1", "Cluster 2")
        and ("budget" in lowered or "deal" in lowered)
    ):
        return SEGMENT_STYLES["Budget / Deal-Oriented Customers"]

    # Budget / Deal segment names
    if "budget" in lowered or "deal" in lowered:
        return SEGMENT_STYLES["Budget / Deal-Oriented Customers"]

    # Internal K-Means cluster 2
    if sname == "2":
        return SEGMENT_STYLES["Regular Customers"]

    # Display Cluster 3
    if sname == "Cluster 3":
        return SEGMENT_STYLES["Regular Customers"]

    # Regular segment name
    if "regular" in lowered:
        return SEGMENT_STYLES["Regular Customers"]

    # Generic lookup against defined segment names
    for key, style in SEGMENT_STYLES.items():
        key_lower = key.lower()

        if (
            key_lower in lowered
            or lowered in key_lower
        ):
            return style

    # Safe fallback
    return {
        "accent": "accent",
        "color": "#285943",
        "soft": "rgba(40, 89, 67, 0.12)",
        "icon": "person",
    }


# ============================================================
# INLINE SVG ICONS
# ============================================================

_ICON_PATHS = {
    "dashboard": (
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
    ),

    "groups": (
        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),

    "person": (
        '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/>'
    ),

    "trophy": (
        '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>'
        '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>'
        '<path d="M4 22h16"/>'
        '<path d="M10 14.66V17c0 .55-.45 1-1 1H7v4h10v-4h-2c-.55 0-1-.45-1-1v-2.34"/>'
        '<path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>'
    ),

    "tag": (
        '<path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94 0-2.48 0-3.42L12 2Z"/>'
        '<path d="M7 7h.01"/>'
    ),

    "hub": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M3 12h6m6 0h6M12 3v6m0 6v6"/>'
    ),

    "chart-donut": (
        '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>'
        '<path d="M22 12A10 10 0 0 0 12 2v10z"/>'
    ),

    "chart-bar": (
        '<line x1="12" y1="20" x2="12" y2="10"/>'
        '<line x1="18" y1="20" x2="18" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="16"/>'
    ),

    "query": (
        '<circle cx="11" cy="11" r="8"/>'
        '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
    ),

    "lightbulb": (
        '<path d="M9 18h6"/>'
        '<path d="M10 22h4"/>'
        '<path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>'
    ),

    "arrow-right": (
        '<line x1="5" y1="12" x2="19" y2="12"/>'
        '<polyline points="12 5 19 12 12 19"/>'
    ),

    "check-circle": (
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
        '<polyline points="22 4 12 14.01 9 11.01"/>'
    ),

    "sparkles": (
        '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>'
    ),

    "wallet": (
        '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/>'
        '<path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>'
    ),

    "trending-up": (
        '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>'
        '<polyline points="17 6 23 6 23 12"/>'
    ),
}


def icon_svg(
    name: str,
    size: int = 18,
    stroke: str = "currentColor",
) -> str:
    """Return inline SVG icon string."""

    body = _ICON_PATHS.get(
        name,
        _ICON_PATHS["person"],
    )

    return (
        f'<svg width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" '
        f'stroke="{stroke}" stroke-width="2" '
        f'stroke-linecap="round" '
        f'stroke-linejoin="round" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f"{body}"
        f"</svg>"
    )


# ============================================================
# GLOBAL CSS
# ============================================================

_STATIC_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* ========================================================
   GLOBAL APPLICATION
   ======================================================== */

html,
body,
[class*="css"],
.stApp {
    font-family:
        'Plus Jakarta Sans',
        'Inter',
        -apple-system,
        BlinkMacSystemFont,
        sans-serif;

    color: var(--sm-text);
}

[data-testid="stAppViewContainer"] {
    background-color: var(--sm-bg);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 1.8rem;
    padding-bottom: 3.5rem;
    max-width: 1240px;
}

/* ========================================================
   PAGE HEADER
   ======================================================== */

.sm-page-header {
    margin-bottom: 1.6rem;
}

.sm-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    text-transform: uppercase;
    letter-spacing: 0.08em;

    font-size: 0.72rem;
    font-weight: 700;

    color: var(--sm-accent);
    background: var(--sm-accent-soft);

    padding: 3px 10px;
    border-radius: 999px;

    margin-bottom: 0.5rem;
}

.sm-page-header h1 {
    font-family:
        'Plus Jakarta Sans',
        sans-serif;

    font-weight: 800;
    letter-spacing: -0.02em;

    color: var(--sm-text);

    font-size: 1.95rem;
    margin-bottom: 0.3rem;
}

.sm-page-header .sm-subtitle {
    color: var(--sm-text-secondary);

    font-size: 0.96rem;

    max-width: 700px;

    margin: 0;

    line-height: 1.5;
}

/* ========================================================
   KPI CARDS
   ======================================================== */

.sm-kpi-grid {
    display: grid;

    grid-template-columns:
        repeat(auto-fit, minmax(210px, 1fr));

    gap: 1rem;

    margin-bottom: 1.5rem;
}

.sm-kpi-card {
    position: relative;

    background: var(--sm-surface);

    border: 1px solid var(--sm-border);

    border-radius: 14px;

    padding: 1.15rem 1.25rem;

    box-shadow:
        0 1px 3px rgba(32, 48, 42, 0.04),
        0 1px 2px rgba(32, 48, 42, 0.02);

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}

.sm-kpi-card:hover {
    transform: translateY(-2px);

    box-shadow:
        0 8px 20px rgba(40, 89, 67, 0.08);
}

.sm-kpi-icon {
    display: inline-flex;

    align-items: center;
    justify-content: center;

    width: 34px;
    height: 34px;

    border-radius: 10px;

    background:
        var(--sm-kpi-icon-bg,
        var(--sm-accent-soft));

    color:
        var(--sm-kpi-icon-color,
        var(--sm-accent));

    margin-bottom: 0.65rem;
}

.sm-kpi-label {
    font-size: 0.76rem;

    font-weight: 600;

    text-transform: uppercase;

    letter-spacing: 0.04em;

    color: var(--sm-text-muted);

    margin-bottom: 0.2rem;
}

.sm-kpi-value {
    font-family:
        'Plus Jakarta Sans',
        sans-serif;

    font-size: 1.65rem;

    font-weight: 800;

    color: var(--sm-text);

    line-height: 1.2;
}

.sm-kpi-sub {
    font-size: 0.78rem;

    color: var(--sm-text-secondary);

    margin-top: 0.25rem;

    font-weight: 500;
}

/* ========================================================
   INSIGHT CARDS
   ======================================================== */

.sm-insight-card {
    display: flex;

    gap: 1rem;

    background: var(--sm-surface);

    border: 1px solid var(--sm-border);

    border-left:
        4px solid
        var(--sm-ins-accent,
        var(--sm-accent));

    border-radius: 12px;

    padding: 1rem 1.2rem;

    margin-bottom: 0.75rem;

    box-shadow:
        0 1px 2px rgba(32, 48, 42, 0.03);
}

.sm-insight-icon {
    display: inline-flex;

    align-items: center;
    justify-content: center;

    width: 34px;
    height: 34px;

    border-radius: 9px;

    background:
        var(--sm-ins-soft,
        var(--sm-accent-soft));

    color:
        var(--sm-ins-accent,
        var(--sm-accent));

    flex-shrink: 0;

    margin-top: 2px;
}

.sm-insight-title {
    font-size: 0.95rem;

    font-weight: 700;

    color: var(--sm-text);

    margin-bottom: 0.25rem;
}

.sm-insight-desc {
    font-size: 0.88rem;

    color: var(--sm-text-secondary);

    line-height: 1.55;

    margin: 0;
}

/* ========================================================
   STRATEGY CARDS
   ======================================================== */

.sm-strategy-card {
    background: var(--sm-surface);

    border: 1px solid var(--sm-border);

    border-top:
        4px solid
        var(--sm-strat-color,
        var(--sm-accent));

    border-radius: 14px;

    padding: 1.35rem 1.45rem;

    margin-bottom: 1.2rem;

    box-shadow:
        0 1px 3px rgba(32, 48, 42, 0.04);
}

.sm-strategy-head {
    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 1rem;

    margin-bottom: 1rem;

    padding-bottom: 0.8rem;

    border-bottom:
        1px solid
        var(--sm-border);
}

.sm-strategy-title {
    display: flex;

    align-items: center;

    gap: 0.65rem;
}

.sm-strategy-name {
    font-size: 1.15rem;

    font-weight: 800;

    color: var(--sm-text);
}

.sm-badge {
    font-size: 0.76rem;

    font-weight: 700;

    padding: 3px 10px;

    border-radius: 999px;

    background:
        var(--sm-strat-soft,
        var(--sm-accent-soft));

    color:
        var(--sm-strat-color,
        var(--sm-accent));
}

.sm-flow-box {
    background: var(--sm-bg);

    border: 1px solid var(--sm-border);

    border-radius: 10px;

    padding: 0.85rem 1rem;

    margin-bottom: 1rem;

    font-size: 0.88rem;
}

.sm-flow-step {
    margin-bottom: 0.45rem;

    line-height: 1.5;
}

.sm-flow-step:last-child {
    margin-bottom: 0;
}

.sm-flow-label {
    font-weight: 700;

    text-transform: uppercase;

    font-size: 0.72rem;

    letter-spacing: 0.04em;

    color: var(--sm-text-muted);

    margin-right: 6px;
}

/* ========================================================
   ACTION ITEMS
   ======================================================== */

.sm-action-list {
    list-style: none;

    margin: 0.5rem 0 0 0;

    padding: 0;
}

.sm-action-list li {
    display: flex;

    align-items: flex-start;

    gap: 0.6rem;

    font-size: 0.88rem;

    color: var(--sm-text-secondary);

    padding: 0.45rem 0;

    line-height: 1.5;
}

.sm-action-arrow {
    color:
        var(--sm-strat-color,
        var(--sm-accent));

    flex-shrink: 0;

    margin-top: 2px;
}

/* ========================================================
   CUSTOMER SEARCH CARD
   ======================================================== */

.sm-cust-card {
    background: var(--sm-surface);

    border: 1px solid var(--sm-border);

    border-radius: 14px;

    padding: 1.4rem;

    margin-top: 1rem;

    box-shadow:
        0 2px 6px rgba(32, 48, 42, 0.04);
}

.sm-cust-header {
    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 1rem;

    padding-bottom: 0.9rem;

    border-bottom:
        1px solid
        var(--sm-border);

    margin-bottom: 1rem;
}

.sm-cust-id-badge {
    font-size: 1.25rem;

    font-weight: 800;

    color: var(--sm-text);
}

/* ========================================================
   BUTTONS
   ======================================================== */

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;

    font-weight: 600;

    font-size: 0.9rem;

    padding: 0.55rem 1.1rem;

    border:
        1px solid
        var(--sm-border-strong);

    background:
        var(--sm-surface);

    color:
        var(--sm-text);

    transition:
        all 0.15s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color:
        var(--sm-accent);

    color:
        var(--sm-accent);

    background:
        var(--sm-accent-soft);
}

.stButton > button[kind="primary"] {
    background:
        var(--sm-accent);

    border:
        1px solid
        var(--sm-accent);

    color: #FFFFFF;

    box-shadow:
        0 4px 12px
        rgba(40, 89, 67, 0.25);
}

.stButton > button[kind="primary"]:hover {
    background:
        #183A37;

    border-color:
        #183A37;

    box-shadow:
        0 6px 16px
        rgba(40, 89, 67, 0.30);

    transform:
        translateY(-1px);

    color:
        #FFFFFF;
}

/* ========================================================
   SIDEBAR
   ======================================================== */

section[data-testid="stSidebar"] {
    background-color: #183A37 !important;
    border-right: 1px solid #234E49 !important;
}

section[data-testid="stSidebar"] * {
    color: #F5F6F1;
}

/* ========================================================
   SIDEBAR NAVIGATION
   ======================================================== */

section[data-testid="stSidebar"] div[data-testid="stPageLink"] {
    border-radius: 8px !important;
    margin-bottom: 4px !important;
    border-left: 3px solid transparent !important;
    background-color: transparent !important;
    transition: all 0.15s ease !important;
}

section[data-testid="stSidebar"] div[data-testid="stPageLink"] a {
    color: #F5F6F1 !important;
    background-color: transparent !important;
    padding: 0.55rem 0.75rem !important;
    border-radius: 8px !important;
    text-decoration: none !important;
}

section[data-testid="stSidebar"] div[data-testid="stPageLink"] a p,
section[data-testid="stSidebar"] div[data-testid="stPageLink"] a span,
section[data-testid="stSidebar"] div[data-testid="stPageLink"] [data-testid="stPageLink-NavLink"] {
    color: #F5F6F1 !important;
    font-weight: 500 !important;
    font-size: 0.92rem !important;
    opacity: 0.95 !important;
    visibility: visible !important;
}

section[data-testid="stSidebar"] div[data-testid="stPageLink"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] div[data-testid="stPageLink"] a svg,
section[data-testid="stSidebar"] div[data-testid="stPageLink"] a i {
    color: #C7A86B !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* ========================================================
   SIDEBAR HOVER
   ======================================================== */

section[data-testid="stSidebar"] div[data-testid="stPageLink"]:hover {
    background-color: rgba(255, 255, 255, 0.08) !important;
    border-left: 3px solid #6B8F71 !important;
}

section[data-testid="stSidebar"] div[data-testid="stPageLink"]:hover a p,
section[data-testid="stSidebar"] div[data-testid="stPageLink"]:hover a span,
section[data-testid="stSidebar"] div[data-testid="stPageLink"]:hover [data-testid="stPageLink-NavLink"] {
    color: #FFFFFF !important;
}

/* ========================================================
   ACTIVE SIDEBAR PAGE
   ======================================================== */

section[data-testid="stSidebar"] div[data-testid="stPageLink"][data-active="true"],
section[data-testid="stSidebar"] div[data-testid="stPageLink"][aria-current="page"] {
    background-color: #285943 !important;
    border-left: 3px solid #C7A86B !important;
}

section[data-testid="stSidebar"] div[data-testid="stPageLink"][data-active="true"] a p,
section[data-testid="stSidebar"] div[data-testid="stPageLink"][data-active="true"] a span,
section[data-testid="stSidebar"] div[data-testid="stPageLink"][data-active="true"] [data-testid="stPageLink-NavLink"] {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] div[data-testid="stPageLink"][data-active="true"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] div[data-testid="stPageLink"][data-active="true"] a svg {
    color: #C7A86B !important;
}

/* ========================================================
   INPUTS
   ======================================================== */

.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    border-radius:
        9px !important;

    border-color:
        #D5DBD1 !important;

    background:
        #FFFFFF !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color:
        #285943 !important;

    box-shadow:
        0 0 0 1px
        rgba(40, 89, 67, 0.15) !important;
}

/* ========================================================
   DATAFRAME
   ======================================================== */

[data-testid="stDataFrame"] {
    border:
        1px solid
        var(--sm-border);

    border-radius:
        10px;

    overflow:
        hidden;
}

/* ========================================================
   DIVIDERS
   ======================================================== */

hr {
    border-color:
        var(--sm-border) !important;
}

/* ========================================================
   SCROLLBAR
   ======================================================== */

::-webkit-scrollbar {
    width: 7px;
    height: 7px;
}

::-webkit-scrollbar-track {
    background:
        #F1F0E8;
}

::-webkit-scrollbar-thumb {
    background:
        #B8C2B8;

    border-radius:
        10px;
}

::-webkit-scrollbar-thumb:hover {
    background:
        #6B8F71;
}

.insight-summary-grid {
    width: 100%;
}

@media (max-width: 768px) {
    .insight-summary-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}

/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 768px) {

    [data-testid="stMainBlockContainer"] {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .sm-page-header h1 {
        font-size: 1.65rem;
    }

    .sm-kpi-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 480px) {

    .sm-kpi-grid {
        grid-template-columns:
            1fr;
    }
}
"""


def inject_base_styles() -> None:
    """Inject root CSS design tokens and layout stylesheets."""

    root_vars = (
        ":root {"
        f"--sm-bg: {COLORS['bg']};"
        f"--sm-sidebar: {COLORS['sidebar']};"
        f"--sm-surface: {COLORS['surface']};"
        f"--sm-surface-hover: {COLORS['surface_hover']};"
        f"--sm-border: {COLORS['border']};"
        f"--sm-border-strong: {COLORS['border_strong']};"
        f"--sm-accent: {COLORS['accent']};"
        f"--sm-accent-soft: {COLORS['accent_soft']};"
        f"--sm-accent-2: {COLORS['accent_2']};"
        f"--sm-accent-2-soft: {COLORS['accent_2_soft']};"
        f"--sm-text: {COLORS['text']};"
        f"--sm-text-secondary: {COLORS['text_secondary']};"
        f"--sm-text-muted: {COLORS['text_muted']};"
        f"--sm-green: {COLORS['green']};"
        f"--sm-green-soft: {COLORS['green_soft']};"
        f"--sm-amber: {COLORS['amber']};"
        f"--sm-amber-soft: {COLORS['amber_soft']};"
        f"--sm-red: {COLORS['red']};"
        f"--sm-red-soft: {COLORS['red_soft']};"
        "}"
    )

    # Use st.html for CSS injection instead of st.markdown.
    # This prevents Streamlit's Markdown renderer from displaying
    # raw CSS when HTML sanitization/parser behavior changes.
    st.html(
        f"<style>{root_vars}{_STATIC_CSS}</style>"
    )


# ============================================================
# COMPONENT BUILDERS
# ============================================================

def page_header(
    title: str,
    subtitle: str = "",
    eyebrow: str = "",
) -> None:
    """Standardized page header."""

    eyebrow_html = (
        f'<div class="sm-eyebrow">{_html.escape(eyebrow)}</div>'
        if eyebrow
        else ""
    )

    subtitle_html = (
        f'<p class="sm-subtitle">'
        f"{_html.escape(subtitle)}"
        f"</p>"
        if subtitle
        else ""
    )

    _md(
        f"""
        <div class="sm-page-header">
            {eyebrow_html}
            <h1>{_html.escape(title)}</h1>
            {subtitle_html}
        </div>
        """
    )


def kpi_grid(
    cards: List[Dict[str, Any]],
) -> None:
    """Render a row of responsive KPI cards."""

    accent_map = {
        "accent": (
            COLORS["accent"],
            COLORS["accent_soft"],
        ),
        "accent_2": (
            COLORS["accent_2"],
            COLORS["accent_2_soft"],
        ),
        "green": (
            COLORS["green"],
            COLORS["green_soft"],
        ),
        "amber": (
            COLORS["amber"],
            COLORS["amber_soft"],
        ),
        "red": (
            COLORS["red"],
            COLORS["red_soft"],
        ),
    }

    cards_html = ""

    for card in cards:
        color, soft = accent_map.get(
            card.get("accent", "accent"),
            accent_map["accent"],
        )

        sub_html = (
            f'<div class="sm-kpi-sub">'
            f'{_html.escape(str(card["sub"]))}'
            f"</div>"
            if card.get("sub")
            else ""
        )

        cards_html += (
            '<div class="sm-kpi-card">'

            f'<div class="sm-kpi-icon" '
            f'style="'
            f'--sm-kpi-icon-bg: {soft}; '
            f'--sm-kpi-icon-color: {color};'
            f'">'
            f'{icon_svg(card.get("icon", "hub"), size=17)}'
            "</div>"

            f'<div class="sm-kpi-label">'
            f'{_html.escape(str(card.get("label", "")))}'
            "</div>"

            f'<div class="sm-kpi-value">'
            f'{_html.escape(str(card.get("value", "")))}'
            "</div>"

            f"{sub_html}"

            "</div>"
        )

    _md(
        f'<div class="sm-kpi-grid">{cards_html}</div>'
    )


def insight_card(
    title: str,
    description: str,
    icon: str = "lightbulb",
    accent: str = "accent",
) -> None:
    """Render a highlighted business insight card."""

    accent_map = {
        "accent": (
            COLORS["accent"],
            COLORS["accent_soft"],
        ),
        "accent_2": (
            COLORS["accent_2"],
            COLORS["accent_2_soft"],
        ),
        "green": (
            COLORS["green"],
            COLORS["green_soft"],
        ),
        "amber": (
            COLORS["amber"],
            COLORS["amber_soft"],
        ),
    }

    color, soft = accent_map.get(
        accent,
        accent_map["accent"],
    )

    _md(
        f"""
        <div
            class="sm-insight-card"
            style="
                --sm-ins-accent: {color};
                --sm-ins-soft: {soft};
            "
        >
            <div class="sm-insight-icon">
                {icon_svg(icon, size=18)}
            </div>

            <div>
                <div class="sm-insight-title">
                    {_html.escape(title)}
                </div>

                <div class="sm-insight-desc">
                    {description}
                </div>
            </div>
        </div>
        """
    )


def strategy_card(
    name: str,
    share: float,
    count: int,
    characteristics: str,
    strategy: str,
    goal: str,
    action_items: List[str],
    accent: str = "accent",
    icon: str = "groups",
) -> None:
    """Render an end-to-end strategic recommendation card."""

    style = segment_style(name)

    color = style.get(
        "color",
        COLORS["accent"],
    )

    soft = style.get(
        "soft",
        COLORS["accent_soft"],
    )

    icon_name = (
        icon
        or style.get("icon", "groups")
    )

    items_html = "".join(
        (
            "<li>"
            '<span class="sm-action-arrow">'
            f'{icon_svg("check-circle", size=14)}'
            "</span>"
            f"<span>{_html.escape(str(item))}</span>"
            "</li>"
        )
        for item in action_items
    )

    _md(
        f"""
        <div
            class="sm-strategy-card"
            style="
                --sm-strat-color: {color};
                --sm-strat-soft: {soft};
            "
        >
            <div class="sm-strategy-head">

                <div class="sm-strategy-title">

                    <div
                        style="
                            color: {color};
                            display: flex;
                        "
                    >
                        {icon_svg(icon_name, size=22)}
                    </div>

                    <div class="sm-strategy-name">
                        {_html.escape(name)}
                    </div>

                </div>

                <div class="sm-badge">
                    {share:.1f}% &bull; {count:,} customers
                </div>

            </div>

            <div class="sm-flow-box">

                <div class="sm-flow-step">

                    <span class="sm-flow-label">
                        Characteristics:
                    </span>

                    <span>
                        {_html.escape(characteristics)}
                    </span>

                </div>

                <div class="sm-flow-step">

                    <span class="sm-flow-label">
                        Strategy:
                    </span>

                    <strong>
                        {_html.escape(strategy)}
                    </strong>

                </div>

                <div class="sm-flow-step">

                    <span class="sm-flow-label">
                        Expected Goal:
                    </span>

                    <span>
                        {_html.escape(goal)}
                    </span>

                </div>

            </div>

            <div
                style="
                    font-size: 0.78rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                    color: var(--sm-text-muted);
                    margin-bottom: 0.35rem;
                "
            >
                Recommended Action Items
            </div>

            <ul class="sm-action-list">
                {items_html}
            </ul>

        </div>
        """
    )


def empty_state(
    icon: str,
    title: str,
    body: str,
) -> None:
    """Render a clean empty-state placeholder."""

    _md(
        f"""
        <div
            style="
                text-align: center;
                background: #FFFFFF;
                border: 1px dashed #C9D0C4;
                border-radius: 16px;
                padding: 2.5rem 1.5rem;
                margin: 1rem 0;
            "
        >

            <div
                style="
                    color: var(--sm-accent);
                    margin-bottom: 0.75rem;
                    display: inline-flex;
                "
            >
                {icon_svg(icon, size=28)}
            </div>

            <div
                style="
                    font-weight: 700;
                    font-size: 1.05rem;
                    color: var(--sm-text);
                    margin-bottom: 0.3rem;
                "
            >
                {_html.escape(title)}
            </div>

            <p
                style="
                    color: var(--sm-text-secondary);
                    font-size: 0.9rem;
                    max-width: 420px;
                    margin: 0 auto;
                "
            >
                {_html.escape(body)}
            </p>

        </div>
        """
    )


# ============================================================
# PLOTLY THEME CONFIGURATOR
# ============================================================

def apply_plotly_theme(
    fig: Any,
    height: int = 380,
    show_legend: bool = True,
) -> Any:
    """
    Apply consistent Forest Green + Ivory styling
    to Plotly charts.
    """

    fig.update_layout(
        height=height,
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20,
        ),
        font=dict(
            family="Plus Jakarta Sans, Inter, sans-serif",
            size=12,
            color=COLORS["text_secondary"],
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                size=11,
                color=COLORS["text_secondary"],
            ),
        ),
        hoverlabel=dict(
            bgcolor=COLORS["text"],
            font_size=12,
            font_family=(
                "Plus Jakarta Sans, "
                "Inter, sans-serif"
            ),
            font_color="#FFFFFF",
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#E9E9E0",
        linecolor="#D5DBD1",
        tickfont=dict(
            size=11,
            color=COLORS["text_secondary"],
        ),
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#E9E9E0",
        linecolor="#D5DBD1",
        tickfont=dict(
            size=11,
            color=COLORS["text_secondary"],
        ),
    )

    return fig