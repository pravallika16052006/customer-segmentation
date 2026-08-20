"""
SegMen - Streamlit Application
Main frontend entrypoint for the SegMenAI dashboard.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
import streamlit as st


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# FRONTEND THEME
# ============================================================

from frontend.theme import inject_base_styles


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SegMen | Customer Segmentation & Insights",
    page_icon=(
        "assets/logo.png"
        if (ROOT_DIR / "assets" / "logo.png").exists()
        else "◎"
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# FASTAPI BACKEND URL
# ============================================================

API_URL = os.getenv(
    "SEGEMAI_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ============================================================
# BACKEND HEALTH CHECK
# ============================================================

def check_backend_status() -> bool:
    """
    Check whether the FastAPI backend is reachable.
    """

    try:
        response = requests.get(
            f"{API_URL}/api/v1/health",
            timeout=2,
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


backend_online = check_backend_status()


# ============================================================
# MULTIPAGE SETUP
# ============================================================

dashboard_page = st.Page(
    "pages/home.py",
    title="Dashboard",
    icon=":material/space_dashboard:",
    default=True,
)

segments_page = st.Page(
    "pages/customer_segmentation.py",
    title="Customer Segments",
    icon=":material/groups:",
)

analysis_page = st.Page(
    "pages/insights.py",
    title="Segment Analysis",
    icon=":material/query_stats:",
)

recommendations_page = st.Page(
    "pages/recommendations.py",
    title="Recommendations",
    icon=":material/tips_and_updates:",
)


pg = st.navigation(
    [
        dashboard_page,
        segments_page,
        analysis_page,
        recommendations_page,
    ],
    position="hidden",
)


# ============================================================
# GLOBAL STYLES
# ============================================================

inject_base_styles()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            display: flex;
            align-items: center;
            gap: 11px;
            padding: 0.4rem 0.2rem 1rem 0.2rem;
        ">

            <div style="
                width: 42px;
                height: 42px;
                border-radius: 12px;
                background: #285943;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                box-shadow: 0 4px 12px rgba(24, 58, 55, 0.30);
            ">

                <svg
                    width="26"
                    height="26"
                    viewBox="0 0 64 64"
                    xmlns="http://www.w3.org/2000/svg"
                >

                    <line
                        x1="24"
                        y1="27"
                        x2="41"
                        y2="24"
                        stroke="#C7A86B"
                        stroke-width="2.5"
                        opacity="0.9"
                    />

                    <line
                        x1="24"
                        y1="27"
                        x2="31"
                        y2="41"
                        stroke="#C7A86B"
                        stroke-width="2.5"
                        opacity="0.9"
                    />

                    <line
                        x1="41"
                        y1="24"
                        x2="31"
                        y2="41"
                        stroke="#C7A86B"
                        stroke-width="2.5"
                        opacity="0.9"
                    />

                    <circle
                        cx="24"
                        cy="27"
                        r="9"
                        fill="#FFFDF7"
                    />

                    <circle
                        cx="41"
                        cy="24"
                        r="6.5"
                        fill="#6B8F71"
                    />

                    <circle
                        cx="31"
                        cy="41"
                        r="7.5"
                        fill="#C7A86B"
                    />

                </svg>

            </div>

            <div>

                <h2 style="
                    margin: 0;
                    font-size: 1.25rem;
                    font-weight: 800;
                    color: #FFFFFF;
                    letter-spacing: -0.02em;
                    font-family: 'Inter', 'DM Sans', sans-serif;
                ">
                    SegMenAI
                </h2>

                <p style="
                    margin: 0;
                    font-size: 0.72rem;
                    color: #C5CDC2;
                    font-weight: 500;
                ">
                    AI-Powered Customer Segmentation
                </p>

            </div>

        </div>

        <hr style="
            border: none;
            border-top: 1px solid #234E49;
            margin: 0 0 1rem 0;
        " />
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # NAVIGATION TITLE
    # ========================================================

    st.markdown(
        """
        <div style="
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #87966F;
            margin-bottom: 0.5rem;
        ">
            Navigation
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # NAVIGATION LINKS
    # ========================================================

    st.page_link(
        dashboard_page,
        label="Dashboard",
        icon=":material/space_dashboard:",
    )

    st.page_link(
        segments_page,
        label="Customer Segments",
        icon=":material/groups:",
    )

    st.page_link(
        analysis_page,
        label="Segment Analysis",
        icon=":material/query_stats:",
    )

    st.page_link(
        recommendations_page,
        label="Recommendations",
        icon=":material/tips_and_updates:",
    )


    # ========================================================
    # BACKEND STATUS
    # ========================================================

    st.markdown(
        "<div style='height: 1.5rem;'></div>",
        unsafe_allow_html=True,
    )

    if backend_online:

        st.success(
            "Backend connected",
            icon="✅",
        )

    else:

        st.error(
            "Backend unavailable",
            icon="🔴",
        )


# ============================================================
# RUN APPLICATION
# ============================================================

pg.run()