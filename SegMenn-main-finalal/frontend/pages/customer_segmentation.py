"""
SegMenAI - Customer Segments Page

Detailed cluster profiling and interactive customer database explorer.
Uses the shared Forest Green + Ivory visual design system.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# PATH SETUP
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# BACKEND + THEME IMPORTS
# ============================================================

from backend.data_loader import get_active_data
from backend.analysis import calculate_cluster_statistics
from backend.recommendations import get_segment_recommendations

from frontend.theme import (
    inject_base_styles,
    page_header,
    segment_style,
    icon_svg,
    COLORS,
    _md,
)


# ============================================================
# INITIALIZE THEME
# ============================================================

inject_base_styles()


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    title="Customer Segments",
    subtitle=(
        "Explore customer groups, understand their behavior, "
        "and identify the right strategy for each segment."
    ),
)


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = get_active_data()

except Exception as exc:
    st.error(f"Error loading customer dataset: {exc}")
    st.stop()

if df is None or df.empty:
    st.info("Upload a customer CSV from the Dashboard to begin analysis.")
    st.stop()


# ============================================================
# CALCULATE SEGMENT DATA
# ============================================================

cluster_stats = calculate_cluster_statistics(df)
segment_recs = get_segment_recommendations(df)


# ============================================================
# CUSTOM PAGE-SPECIFIC CSS
# ============================================================

st.html(
    """
    <style>

    /* ======================================================
       SECTION HEADERS
       ====================================================== */

    .seg-section-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--sm-text);
        margin-top: 0.4rem;
        margin-bottom: 0.25rem;
    }

    .seg-section-desc {
        font-size: 0.88rem;
        color: var(--sm-text-secondary);
        margin-bottom: 1.2rem;
    }


    /* ======================================================
       SEGMENT CARD
       ====================================================== */

    .seg-card {
        background: var(--sm-surface);
        border: 1px solid var(--sm-border);
        border-radius: 14px;

        padding: 1.2rem;

        height: 100%;

        box-shadow:
            0 1px 3px rgba(32, 48, 42, 0.04);

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .seg-card:hover {
        transform: translateY(-2px);

        box-shadow:
            0 8px 20px rgba(40, 89, 67, 0.08);
    }


    /* ======================================================
       SEGMENT HEADER
       ====================================================== */

    .seg-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;

        gap: 0.6rem;

        padding-bottom: 0.85rem;

        border-bottom:
            1px solid var(--sm-border);

        margin-bottom: 0.9rem;
    }


    .seg-card-title {
        display: flex;
        align-items: center;

        gap: 0.55rem;

        min-width: 0;
    }


    .seg-card-name {
        font-size: 0.98rem;
        font-weight: 800;

        color: var(--sm-text);

        line-height: 1.25;
    }


    .seg-cluster-badge {
        font-size: 0.68rem;
        font-weight: 700;

        padding: 3px 8px;

        border-radius: 999px;

        white-space: nowrap;
    }


    /* ======================================================
       SEGMENT METRICS
       ====================================================== */

    .seg-metrics {
        display: grid;

        grid-template-columns:
            repeat(2, minmax(0, 1fr));

        gap: 0.65rem;

        margin-bottom: 0.95rem;
    }


    .seg-metric {
        background: var(--sm-bg);

        border: 1px solid var(--sm-border);

        border-radius: 10px;

        padding: 0.65rem 0.7rem;
    }


    .seg-metric-label {
        font-size: 0.65rem;

        text-transform: uppercase;

        letter-spacing: 0.04em;

        font-weight: 700;

        color: var(--sm-text-muted);

        margin-bottom: 0.2rem;
    }


    .seg-metric-value {
        font-size: 1rem;

        font-weight: 800;

        color: var(--sm-text);

        line-height: 1.2;
    }


    .seg-metric-sub {
        font-size: 0.67rem;

        color: var(--sm-text-secondary);

        margin-top: 0.15rem;
    }


    /* ======================================================
       STRATEGY
       ====================================================== */

    .seg-strategy-label {
        font-size: 0.67rem;

        text-transform: uppercase;

        letter-spacing: 0.05em;

        font-weight: 700;

        color: var(--sm-text-muted);

        margin-bottom: 0.25rem;
    }


    .seg-strategy {
        font-size: 0.8rem;

        color: var(--sm-text-secondary);

        line-height: 1.5;
    }


    /* ======================================================
       DATABASE SECTION
       ====================================================== */

    .database-header {
        display: flex;

        align-items: center;

        gap: 0.65rem;

        margin-bottom: 0.25rem;
    }


    .database-icon {
        display: inline-flex;

        align-items: center;
        justify-content: center;

        width: 34px;
        height: 34px;

        border-radius: 9px;

        background: var(--sm-accent-soft);

        color: var(--sm-accent);
    }


    .database-title {
        font-size: 1.15rem;

        font-weight: 800;

        color: var(--sm-text);
    }


    .database-subtitle {
        font-size: 0.86rem;

        color: var(--sm-text-secondary);

        margin-bottom: 1rem;
    }


    /* ======================================================
       RESULTS INFO
       ====================================================== */

    .results-info {
        font-size: 0.8rem;

        color: var(--sm-text-secondary);

        margin-top: 0.55rem;

        margin-bottom: 0.8rem;
    }


    .results-number {
        color: var(--sm-accent);

        font-weight: 700;
    }


    /* ======================================================
       DOWNLOAD AREA
       ====================================================== */

    .download-label {
        font-size: 0.78rem;

        font-weight: 600;

        color: var(--sm-text-secondary);

        margin-bottom: 0.35rem;
    }


    /* ======================================================
       RESPONSIVE
       ====================================================== */

    @media (max-width: 768px) {

        .seg-metrics {
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
        }

    }

    </style>
    """
)


# ============================================================
# CUSTOMER SEGMENT PROFILES
# ============================================================

_md(
    """
    <div class="seg-section-title">
        Customer Segment Profiles
    </div>

    <div class="seg-section-desc">
        Key attributes, spending patterns, and core strategies for each segment.
    </div>
    """
)


# ============================================================
# SEGMENT CARDS
# ============================================================

cols = st.columns(
    len(segment_recs),
    gap="medium",
)


for idx, rec in enumerate(segment_recs):

    with cols[idx]:

        style = segment_style(rec["name"])

        color = style.get(
            "color",
            COLORS["accent"],
        )

        soft = style.get(
            "soft",
            COLORS["accent_soft"],
        )

        icon_name = style.get(
            "icon",
            "groups",
        )

        _md(
            f"""
            <div class="seg-card">

                <!-- HEADER -->
                <div class="seg-card-header">

                    <div class="seg-card-title">

                        <div
                            style="
                                color: {color};
                                display: flex;
                                flex-shrink: 0;
                            "
                        >
                            {icon_svg(icon_name, size=20)}
                        </div>

                        <div class="seg-card-name">
                            {rec["name"]}
                        </div>

                    </div>


                    <span
                        class="seg-cluster-badge"
                        style="
                            background: {soft};
                            color: {color};
                        "
                    >
                        Cluster {rec["cluster_id"]}
                    </span>

                </div>


                <!-- METRICS -->
                <div class="seg-metrics">

                    <!-- CUSTOMERS -->
                    <div class="seg-metric">

                        <div class="seg-metric-label">
                            Customers
                        </div>

                        <div class="seg-metric-value">
                            {rec["count"]:,}
                        </div>

                        <div class="seg-metric-sub">
                            {rec["share"]:.1f}% of base
                        </div>

                    </div>


                    <!-- SPENDING -->
                    <div class="seg-metric">

                        <div class="seg-metric-label">
                            Avg Spending
                        </div>

                        <div
                            class="seg-metric-value"
                            style="color: {color};"
                        >
                            ${rec["avg_spend"]:,.2f}
                        </div>

                        <div class="seg-metric-sub">
                            Per customer
                        </div>

                    </div>


                    <!-- INCOME -->
                    <div class="seg-metric">

                        <div class="seg-metric-label">
                            Avg Income
                        </div>

                        <div class="seg-metric-value">
                            ${rec["avg_income"]:,.0f}
                        </div>

                        <div class="seg-metric-sub">
                            Annual
                        </div>

                    </div>


                    <!-- PURCHASE FREQUENCY -->
                    <div class="seg-metric">

                        <div class="seg-metric-label">
                            Purchases
                        </div>

                        <div class="seg-metric-value">
                            {rec["avg_purchases"]:.1f}
                        </div>

                        <div class="seg-metric-sub">
                            Orders per customer
                        </div>

                    </div>

                </div>


                <!-- RECENCY -->
                <div
                    style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        background: {soft};
                        border-radius: 9px;
                        padding: 0.55rem 0.7rem;
                        margin-bottom: 0.9rem;
                    "
                >

                    <span
                        style="
                            font-size: 0.7rem;
                            font-weight: 700;
                            color: {color};
                        "
                    >
                        RECENCY
                    </span>

                    <span
                        style="
                            font-size: 0.78rem;
                            font-weight: 700;
                            color: var(--sm-text);
                        "
                    >
                        {rec["recency"]:.0f} days
                    </span>

                </div>


                <!-- STRATEGY -->
                <div class="seg-strategy-label">
                    Key Strategy
                </div>

                <div class="seg-strategy">
                    {rec["strategy"]}
                </div>

            </div>
            """
        )


# ============================================================
# DATABASE DIVIDER
# ============================================================

st.markdown(
    "<div style='height: 1rem'></div>",
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# CUSTOMER DATABASE HEADER
# ============================================================

_md(
    f"""
    <div class="database-header">

        <div class="database-icon">
            {icon_svg("query", size=18)}
        </div>

        <div class="database-title">
            Customer Database Explorer
        </div>

    </div>

    <div class="database-subtitle">
        Search and filter individual customer records by segment,
        customer ID, and display preferences.
    </div>
    """
)


# ============================================================
# FILTER BAR
# ============================================================

f1, f2, f3 = st.columns(
    [1.5, 2.2, 1],
    gap="medium",
)


# ------------------------------------------------------------
# SEGMENT FILTER
# ------------------------------------------------------------

all_segment_names = sorted(
    df["Cluster_Name"].unique().tolist()
)

with f1:

    selected_seg_filter = st.selectbox(
        "Customer Segment",
        options=[
            "All Segments",
            *all_segment_names,
        ],
        index=0,
    )


# ------------------------------------------------------------
# CUSTOMER SEARCH
# ------------------------------------------------------------

with f2:

    search_id = st.text_input(
        "Search Customer ID",
        placeholder="Enter Customer ID...",
    )


# ------------------------------------------------------------
# ROW LIMIT
# ------------------------------------------------------------

with f3:

    max_rows = st.selectbox(
        "Rows Displayed",
        options=[
            25,
            50,
            100,
            500,
            1000,
        ],
        index=1,
    )


# ============================================================
# FILTER DATA
# ============================================================

filtered_table = df.copy()


# Segment filter
if selected_seg_filter != "All Segments":

    filtered_table = filtered_table[
        filtered_table["Cluster_Name"]
        == selected_seg_filter
    ]


# Customer ID search
if search_id.strip():

    try:

        search_int = int(
            search_id.strip()
        )

        filtered_table = filtered_table[
            filtered_table["ID"]
            == search_int
        ]

    except ValueError:

        st.warning(
            "Please enter a valid numeric Customer ID."
        )


# ============================================================
# DISPLAY COLUMNS
# ============================================================

display_cols = [
    "ID",
    "Cluster",
    "Cluster_Name",
    "Income",
    "TotalSpending",
    "TotalPurchases",
    "Recency",
    "Age",
    "TotalChildren",
    "DealPurchaseShare",
    "CampaignAcceptedCount",
]


available_display = [
    column
    for column in display_cols
    if column in filtered_table.columns
]


display_df = (
    filtered_table[
        available_display
    ]
    .head(max_rows)
    .copy()
)


# ============================================================
# RENAME COLUMNS
# ============================================================

rename_map = {

    "ID":
        "Customer ID",

    "Cluster_Name":
        "Segment Name",

    "TotalSpending":
        "Spending ($)",

    "Income":
        "Income ($)",

    "TotalPurchases":
        "Total Orders",

    "Recency":
        "Recency (Days)",

    "TotalChildren":
        "Children",

    "DealPurchaseShare":
        "Deal Share",

    "CampaignAcceptedCount":
        "Campaigns",
}


display_df = display_df.rename(
    columns=rename_map
)


# ============================================================
# FORMAT VALUES
# ============================================================

if "Spending ($)" in display_df.columns:

    display_df["Spending ($)"] = (
        display_df["Spending ($)"]
        .map(
            lambda x:
                f"${x:,.2f}"
                if pd.notna(x)
                else "$0.00"
        )
    )


if "Income ($)" in display_df.columns:

    display_df["Income ($)"] = (
        display_df["Income ($)"]
        .map(
            lambda x:
                f"${x:,.0f}"
                if pd.notna(x)
                else "$0"
        )
    )


if "Deal Share" in display_df.columns:

    display_df["Deal Share"] = (
        display_df["Deal Share"]
        .map(
            lambda x:
                f"{x * 100:.1f}%"
                if pd.notna(x)
                else "0.0%"
        )
    )


# ============================================================
# RESULTS SUMMARY
# ============================================================

st.markdown(
    f"""
    <div class="results-info">
        Showing
        <span class="results-number">
            {len(display_df):,}
        </span>
        of
        <span class="results-number">
            {len(filtered_table):,}
        </span>
        matching customers
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CUSTOMER TABLE
# ============================================================

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# CSV DOWNLOAD
# ============================================================

st.markdown(
    "<div style='height: 0.35rem'></div>",
    unsafe_allow_html=True,
)

csv_data = (
    filtered_table
    .to_csv(index=False)
    .encode("utf-8")
)


st.download_button(
    label="Download Filtered Customer Records",
    data=csv_data,
    file_name="segmenai_filtered_customers.csv",
    mime="text/csv",
)