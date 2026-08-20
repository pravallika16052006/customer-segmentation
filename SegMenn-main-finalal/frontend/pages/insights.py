"""
SegMenAI - Segment Analysis Page

Deep-dive behavioral profiling, distributions, product/channel
preferences, and multi-dimensional radar comparison.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PROJECT PATH SETUP
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# BACKEND IMPORTS
# ============================================================

from backend.data_loader import get_active_data

from backend.analysis import (
    calculate_cluster_statistics,
    generate_segment_narrative,
    get_category_spending_breakdown,
    get_channel_breakdown,
    get_distribution_data,
)


# ============================================================
# THEME IMPORTS
# ============================================================

from frontend.theme import (
    inject_base_styles,
    page_header,
    kpi_grid,
    apply_plotly_theme,
    segment_style,
    icon_svg,
    COLORS,
    _md,
)


# ============================================================
# GLOBAL STYLES
# ============================================================

inject_base_styles()


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    title="Segment Analysis",
    subtitle=(
        "Detailed analysis of customer spending and channel preferences."
    ),
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = get_active_data()

except Exception as exc:

    st.error(
        f"Unable to load the customer dataset: {exc}"
    )

    st.stop()


# ============================================================
# DATA VALIDATION
# ============================================================

if df is None or df.empty:
    st.info("Upload a customer CSV from the Dashboard to begin analysis.")
    st.stop()


if "Cluster_Name" not in df.columns:

    st.error(
        "The dataset does not contain the required "
        "'Cluster_Name' column."
    )

    st.stop()


# ============================================================
# CLUSTER STATISTICS
# ============================================================

cluster_stats = calculate_cluster_statistics(df)

available_segments = sorted(
    df["Cluster_Name"]
    .dropna()
    .unique()
    .tolist()
)


if not available_segments:

    st.warning(
        "No customer segments are available for analysis."
    )

    st.stop()


# ============================================================
# SEGMENT SELECTOR
# ============================================================

selector_col, _ = st.columns([1.5, 2])

with selector_col:

    selected_segment = st.selectbox(
        "Select Customer Segment",
        options=available_segments,
        index=0,
    )


# ============================================================
# SELECTED SEGMENT DATA
# ============================================================

seg_df = df[
    df["Cluster_Name"] == selected_segment
].copy()


if seg_df.empty:

    st.warning(
        "No customer records are available "
        "for the selected segment."
    )

    st.stop()


# ============================================================
# CLUSTER ID
# ============================================================

if "Cluster" in seg_df.columns:

    cluster_id = int(
        seg_df["Cluster"].iloc[0]
    )

else:

    cluster_id = 0


# ============================================================
# CLUSTER STATISTICS ROW
# ============================================================

try:

    if cluster_id in cluster_stats.index:

        stats_row = cluster_stats.loc[
            cluster_id
        ]

    else:

        stats_row = cluster_stats.iloc[0]

except Exception:

    stats_row = cluster_stats.iloc[0]


# ============================================================
# SEGMENT STYLE
# ============================================================

style = segment_style(
    selected_segment
)

seg_color = style.get(
    "color",
    COLORS["accent"],
)

seg_soft = style.get(
    "soft",
    COLORS["accent_soft"],
)

seg_icon = style.get(
    "icon",
    "groups",
)


# ============================================================
# SEGMENT OVERVIEW METRICS
# ============================================================

count = int(
    stats_row.get(
        "CustomerCount",
        len(seg_df),
    )
)


share = float(
    stats_row.get(
        "SharePercentage",
        (count / len(df)) * 100,
    )
)


avg_income = float(
    stats_row.get(
        "Income",
        (
            seg_df["Income"].mean()
            if "Income" in seg_df.columns
            else 0.0
        ),
    )
)


avg_spend = float(
    stats_row.get(
        "TotalSpending",
        (
            seg_df["TotalSpending"].mean()
            if "TotalSpending" in seg_df.columns
            else 0.0
        ),
    )
)


avg_purchases = float(
    stats_row.get(
        "TotalPurchases",
        (
            seg_df["TotalPurchases"].mean()
            if "TotalPurchases" in seg_df.columns
            else 0.0
        ),
    )
)


avg_recency = float(
    stats_row.get(
        "Recency",
        (
            seg_df["Recency"].mean()
            if "Recency" in seg_df.columns
            else 0.0
        ),
    )
)


# ============================================================
# KPI CARDS
# ============================================================

kpi_grid(
    [
        {
            "label": "Segment Size",
            "value": f"{count:,}",
            "icon": "person",
            "accent": "green",
            "sub": (
                f"{share:.1f}% of total customer base"
            ),
        },
        {
            "label": "Average Income",
            "value": f"${avg_income:,.0f}",
            "icon": "wallet",
            "accent": "accent_2",
            "sub": "Annual household earnings",
        },
        {
            "label": "Average Spending",
            "value": f"${avg_spend:,.0f}",
            "icon": "trophy",
            "accent": "green",
            "sub": "Total product expenditure",
        },
        {
            "label": "Order Frequency",
            "value": f"{avg_purchases:.1f}",
            "icon": "chart-bar",
            "accent": "amber",
            "sub": (
                f"{avg_recency:.0f} days average recency"
            ),
        },
    ]
)


# ============================================================
# SEGMENT PROFILE
# ============================================================

st.markdown(
    "<div style='height: 0.2rem'></div>",
    unsafe_allow_html=True,
)


try:

    narrative = generate_segment_narrative(
        selected_segment,
        cluster_id,
        stats_row,
        df,
    )

except Exception:

    narrative = (
        "This segment represents a distinct group of "
        "customers identified through behavioral clustering."
    )


_md(
    f"""
    <div
        style="
            background: var(--sm-surface);
            border: 1px solid var(--sm-border);
            border-left: 4px solid {seg_color};
            border-radius: 12px;
            padding: 1.15rem 1.3rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 2px rgba(32,48,42,0.03);
        "
    >

        <div
            style="
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {seg_color};
                margin-bottom: 0.45rem;
            "
        >
            {icon_svg(seg_icon, size=15)}

            <span>
                {selected_segment} · Segment Profile
            </span>

        </div>

        <p
            style="
                font-size: 0.92rem;
                color: var(--sm-text-secondary);
                line-height: 1.6;
                margin: 0;
            "
        >
            {narrative}
        </p>

    </div>
    """
)


# ============================================================
# BEHAVIORAL & FINANCIAL DISTRIBUTIONS
# ============================================================

st.subheader(
    "Behavioral & Financial Distributions"
)

st.caption(
    "Distribution patterns within the selected customer segment."
)


dist_col1, dist_col2 = st.columns(2)


# ============================================================
# INCOME DISTRIBUTION
# ============================================================

with dist_col1:

    st.markdown(
        "**Income Distribution ($)**"
    )

    if "Income" in df.columns:

        income_series = get_distribution_data(
            df,
            "Income",
            cluster_id=cluster_id,
        )

        fig_income = px.histogram(
            income_series,
            nbins=35,
            labels={
                "value": "Annual Income ($)"
            },
            color_discrete_sequence=[
                seg_color
            ],
            opacity=0.85,
        )

        fig_income.update_layout(
            showlegend=False,
            xaxis_title="Annual Income ($)",
            yaxis_title="Customer Count",
        )

        apply_plotly_theme(
            fig_income,
            height=300,
            show_legend=False,
        )

        st.plotly_chart(
            fig_income,
            use_container_width=True,
        )

    else:

        st.info(
            "Income data is not available."
        )


# ============================================================
# SPENDING DISTRIBUTION
# ============================================================

with dist_col2:

    st.markdown(
        "**Total Spending Distribution ($)**"
    )

    if "TotalSpending" in df.columns:

        spending_series = get_distribution_data(
            df,
            "TotalSpending",
            cluster_id=cluster_id,
        )

        fig_spending = px.histogram(
            spending_series,
            nbins=35,
            labels={
                "value": "Total Spending ($)"
            },
            color_discrete_sequence=[
                seg_color
            ],
            opacity=0.85,
        )

        fig_spending.update_layout(
            showlegend=False,
            xaxis_title="Total Spending ($)",
            yaxis_title="Customer Count",
        )

        apply_plotly_theme(
            fig_spending,
            height=300,
            show_legend=False,
        )

        st.plotly_chart(
            fig_spending,
            use_container_width=True,
        )

    else:

        st.info(
            "Spending data is not available."
        )


# ============================================================
# PRODUCT & CHANNEL PREFERENCES
# ============================================================

st.markdown(
    "<div style='height: 0.5rem'></div>",
    unsafe_allow_html=True,
)

st.subheader(
    "Product Affinities & Purchasing Channels"
)

st.caption(
    "Understand what the selected segment buys "
    "and how customers prefer to purchase."
)


category_col, channel_col = st.columns(2)


# ============================================================
# PRODUCT CATEGORY
# ============================================================

with category_col:

    st.markdown(
        "**Average Spend by Product Category ($)**"
    )

    try:

        category_df = get_category_spending_breakdown(
            df,
            cluster_id=cluster_id,
        )

    except Exception:

        category_df = pd.DataFrame()


    if not category_df.empty:

        fig_category = px.bar(
            category_df,
            x="Category",
            y="AverageSpend",
            text="AverageSpend",
        )

        fig_category.update_traces(
            marker_color=seg_color,
            texttemplate="$%{text:,.1f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average Spend: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )

        fig_category.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Average Spend ($)",
        )

        apply_plotly_theme(
            fig_category,
            height=320,
            show_legend=False,
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True,
        )

    else:

        st.info(
            "Product category breakdown is not available."
        )


# ============================================================
# PURCHASE CHANNEL
# ============================================================

with channel_col:

    st.markdown(
        "**Purchase Channel Breakdown (Orders)**"
    )

    try:

        channel_df = get_channel_breakdown(
            df,
            cluster_id=cluster_id,
        )

    except Exception:

        channel_df = pd.DataFrame()


    if not channel_df.empty:

        fig_channel = px.bar(
            channel_df,
            x="Channel",
            y="AverageOrders",
            text="AverageOrders",
        )

        fig_channel.update_traces(
            marker_color=seg_color,
            texttemplate="%{text:.1f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average Orders: %{y:.2f}"
                "<extra></extra>"
            ),
        )

        fig_channel.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Average Orders",
        )

        apply_plotly_theme(
            fig_channel,
            height=320,
            show_legend=False,
        )

        st.plotly_chart(
            fig_channel,
            use_container_width=True,
        )

    else:

        st.info(
            "Channel breakdown is not available."
        )



# ============================================================
# SEGMENT SUMMARY
# ============================================================

st.markdown(
    "<div style='height: 0.5rem'></div>",
    unsafe_allow_html=True,
)

st.subheader(
    "Segment Summary"
)


summary_items = [
    (
        "Customers",
        f"{count:,}",
    ),
    (
        "Customer Share",
        f"{share:.1f}%",
    ),
    (
        "Average Income",
        f"${avg_income:,.0f}",
    ),
    (
        "Average Spending",
        f"${avg_spend:,.0f}",
    ),
    (
        "Average Orders",
        f"{avg_purchases:.1f}",
    ),
    (
        "Average Recency",
        f"{avg_recency:.0f} days",
    ),
]


summary_html = ""

for label, value in summary_items:

    summary_html += f"""
        <div
            style="
                background: var(--sm-surface);
                border: 1px solid var(--sm-border);
                border-radius: 10px;
                padding: 0.9rem 1rem;
            "
        >

            <div
                style="
                    font-size: 0.7rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                    color: var(--sm-text-muted);
                    margin-bottom: 0.25rem;
                "
            >
                {label}
            </div>

            <div
                style="
                    font-size: 1.1rem;
                    font-weight: 800;
                    color: var(--sm-text);
                "
            >
                {value}
            </div>

        </div>
    """


_md(
    f"""
    <div
        style="
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
            margin-bottom: 1rem;
        "
     class="insight-summary-grid">
        {summary_html}
    </div>


    """
)