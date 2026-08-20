"""
SegMenAI - Dashboard Page
Overview of customer base, KPI metrics, dynamic Plotly charts,
and automated business insights.
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
# BACKEND + UI IMPORTS
# ============================================================

from backend.data_loader import (
    get_active_data,
    set_active_data,
    clear_active_data,
)
from backend.inference import predict_customers
from backend.analysis import (
    calculate_cluster_statistics,
    generate_business_insights,
)

from frontend.theme import (
    inject_base_styles,
    page_header,
    kpi_grid,
    insight_card,
    apply_plotly_theme,
    segment_style,
)


# ============================================================
# GLOBAL STYLES
# ============================================================

inject_base_styles()


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    title="Executive Dashboard",
    subtitle=(
        "A clear overview of customer groups, spending habits, "
        "and key business insights."
    ),
)


# ============================================================
# DATASET UPLOAD + PROCESSING
# ============================================================

source_name = st.session_state.get("active_dataset_source")
active_df = get_active_data()

st.markdown("### Upload customer data")
st.write(
    "Upload one or more customer data files. SegMenAI accepts CSV and Excel "
    "files, validates them, runs the saved ML preprocessing and clustering "
    "model, and uses the result across the dashboard."
)

uploaded_files = st.file_uploader(
    "Choose CSV or Excel file(s)",
    type=["csv"],
    accept_multiple_files=True,
    help="Select one or more .csv, .xlsx, or .xls files. Files must use the same customer schema when multiple files are selected.",
)

process_col, clear_col = st.columns([1, 1])

with process_col:
    process_clicked = st.button(
        "Process Uploaded Data",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_files,
    )

with clear_col:
    clear_clicked = st.button(
        "Clear Dataset",
        use_container_width=True,
    )

if clear_clicked:
    clear_active_data()
    st.rerun()

if process_clicked:
    try:
        frames = []
        names = []
        for uploaded in uploaded_files:
            filename = uploaded.name.lower()
            if filename.endswith(".csv"):
                frame = pd.read_csv(uploaded)
            elif filename.endswith((".xlsx", ".xls")):
                frame = pd.read_excel(uploaded)
            else:
                continue
            if frame.empty:
                continue
            frames.append(frame)
            names.append(uploaded.name)

        if not frames:
            raise ValueError("No non-empty CSV or Excel files were selected.")

        base_columns = list(frames[0].columns)
        incompatible = [
            name for name, frame in zip(names[1:], frames[1:])
            if list(frame.columns) != base_columns
        ]
        if incompatible:
            raise ValueError(
                "Uploaded files do not have the same columns. "
                f"Incompatible file(s): {', '.join(incompatible)}"
            )

        raw_df = pd.concat(frames, ignore_index=True)

        with st.status("Running SegMenAI backend pipeline...", expanded=True) as status:
            st.write(f"✓ Loaded {len(names)} uploaded file(s)")
            st.write("✓ Validating required customer fields")
            predictions = predict_customers(raw_df)
            st.write("✓ Applied feature engineering and saved preprocessor")
            st.write("✓ Assigned customer segments with the trained clustering model")

            from backend.data_loader import engineer_features
            processed_df = engineer_features(raw_df)
            processed_df["Cluster"] = predictions["Cluster"].values
            processed_df["Cluster_Name"] = predictions["Cluster_Name"].values

            set_active_data(processed_df, ", ".join(names))
            status.update(label="Dataset processed successfully", state="complete")

        st.success(
            f"Processed {len(processed_df):,} customers from {len(names)} file(s)."
        )
        st.rerun()

    except Exception as exc:
        st.error(f"Data processing failed: {exc}")
        st.info(
            "Make sure the uploaded CSV/Excel files use the same customer fields as "
            "the model training dataset, including Dt_Customer and the campaign columns."
        )

# Stop here until the user uploads data. This prevents the bundled sample dataset
# from appearing automatically when the application starts.
if active_df is None or active_df.empty:
    st.info("No dataset is loaded yet. Upload one or more CSV/Excel files above to populate the dashboard.")
    st.stop()

df_raw = active_df

st.caption(f"Active dataset: {source_name or 'Uploaded dataset'} · {len(df_raw):,} customers")

# Let the user export the exact processed/segmented data used by the dashboard.
export_df = df_raw.copy()
export_csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Processed Segmentation CSV",
    data=export_csv,
    file_name="segmenai_processed_segments.csv",
    mime="text/csv",
)


# ============================================================
# DATA VALIDATION
# ============================================================

if df_raw.empty:
    st.warning(
        "No customer data is currently available."
    )
    st.stop()


required_columns = [
    "Cluster_Name",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df_raw.columns
]

if missing_columns:
    st.error(
        "The dataset is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ============================================================
# INTERACTIVE FILTERS
# ============================================================

with st.expander(
    "Filter Customer Data",
    expanded=False,
):

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    # --------------------------------------------------------
    # Segment Filter
    # --------------------------------------------------------

    all_segments = sorted(
        df_raw["Cluster_Name"]
        .dropna()
        .unique()
        .tolist()
    )

    with filter_col1:

        selected_segments = st.multiselect(
            "Customer Segment",
            options=all_segments,
            default=all_segments,
        )

    # --------------------------------------------------------
    # Income Filter
    # --------------------------------------------------------

    if "Income" in df_raw.columns:

        min_income = int(
            df_raw["Income"].min()
        )

        max_income = int(
            df_raw["Income"].max()
        )

        if min_income == max_income:
            max_income = min_income + 1

        with filter_col2:

            income_range = st.slider(
                "Income Range",
                min_value=min_income,
                max_value=max_income,
                value=(
                    min_income,
                    max_income,
                ),
                step=max(
                    1,
                    int(
                        (max_income - min_income) / 100
                    ),
                ),
            )

    else:

        income_range = None

    # --------------------------------------------------------
    # Spending Filter
    # --------------------------------------------------------

    if "TotalSpending" in df_raw.columns:

        min_spending = int(
            df_raw["TotalSpending"].min()
        )

        max_spending = int(
            df_raw["TotalSpending"].max()
        )

        if min_spending == max_spending:
            max_spending = min_spending + 1

        with filter_col3:

            spending_range = st.slider(
                "Total Spending",
                min_value=min_spending,
                max_value=max_spending,
                value=(
                    min_spending,
                    max_spending,
                ),
                step=max(
                    1,
                    int(
                        (max_spending - min_spending) / 100
                    ),
                ),
            )

    else:

        spending_range = None

    # --------------------------------------------------------
    # Recency Filter
    # --------------------------------------------------------

    if "Recency" in df_raw.columns:

        min_recency = int(
            df_raw["Recency"].min()
        )

        max_recency = int(
            df_raw["Recency"].max()
        )

        if min_recency == max_recency:
            max_recency = min_recency + 1

        with filter_col4:

            recency_range = st.slider(
                "Recency (Days)",
                min_value=min_recency,
                max_value=max_recency,
                value=(
                    min_recency,
                    max_recency,
                ),
                step=1,
            )

    else:

        recency_range = None


# ============================================================
# APPLY FILTERS
# ============================================================

df = df_raw.copy()


if selected_segments:

    df = df[
        df["Cluster_Name"].isin(
            selected_segments
        )
    ]


if (
    income_range is not None
    and "Income" in df.columns
):

    df = df[
        (df["Income"] >= income_range[0])
        & (df["Income"] <= income_range[1])
    ]


if (
    spending_range is not None
    and "TotalSpending" in df.columns
):

    df = df[
        (df["TotalSpending"] >= spending_range[0])
        & (df["TotalSpending"] <= spending_range[1])
    ]


if (
    recency_range is not None
    and "Recency" in df.columns
):

    df = df[
        (df["Recency"] >= recency_range[0])
        & (df["Recency"] <= recency_range[1])
    ]


# ============================================================
# EMPTY FILTER STATE
# ============================================================

if df.empty:

    st.warning(
        "No customers match the selected filters. "
        "Please broaden your filter criteria."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_customers = len(df)

num_segments = (
    df["Cluster_Name"]
    .nunique()
)


avg_spending = (
    float(df["TotalSpending"].mean())
    if "TotalSpending" in df.columns
    else 0.0
)


avg_purchases = (
    float(df["TotalPurchases"].mean())
    if "TotalPurchases" in df.columns
    else 0.0
)


avg_income = (
    float(df["Income"].mean())
    if "Income" in df.columns
    else 0.0
)


# ============================================================
# HIGHEST VALUE SEGMENT
# ============================================================

if "TotalSpending" in df.columns:

    segment_spending = (
        df.groupby("Cluster_Name")[
            "TotalSpending"
        ]
        .mean()
    )

else:

    segment_spending = pd.Series(
        dtype=float
    )


if not segment_spending.empty:

    highest_value_segment = (
        segment_spending.idxmax()
    )

    highest_value_amount = (
        segment_spending.max()
    )

else:

    highest_value_segment = "N/A"
    highest_value_amount = 0.0


# ============================================================
# KPI CARDS
# ============================================================

kpi_grid(
    [
        {
            "label": "Total Customers",
            "value": f"{total_customers:,}",
            "icon": "person",
            "accent": "green",
            "sub": (
                f"From {len(df_raw):,} customer records"
            ),
        },
        {
            "label": "Customer Segments",
            "value": f"{num_segments}",
            "icon": "hub",
            "accent": "green",
            "sub": "K-Means clustering • k = 3",
        },
        {
            "label": "Highest Value Segment",
            "value": highest_value_segment,
            "icon": "trophy",
            "accent": "amber",
            "sub": (
                f"${highest_value_amount:,.0f} "
                "average spending"
            ),
        },
        {
            "label": "Average Spending",
            "value": f"${avg_spending:,.0f}",
            "icon": "wallet",
            "accent": "green",
            "sub": (
                f"Average income: "
                f"${avg_income:,.0f}"
            ),
        },
    ]
)


# ============================================================
# SECTION SPACING
# ============================================================

st.markdown(
    "<div style='height: 0.6rem'></div>",
    unsafe_allow_html=True,
)


# ============================================================
# CHART ROW
# ============================================================

chart_left, chart_right = st.columns(
    [1, 1.4]
)


# ============================================================
# CHART 1 — CUSTOMER DISTRIBUTION
# ============================================================

with chart_left:

    st.subheader(
        "Customer Distribution"
    )

    segment_counts = (
        df["Cluster_Name"]
        .value_counts()
        .reset_index()
    )

    segment_counts.columns = [
        "Segment",
        "Customers",
    ]

    # Forest Green / Ivory compatible
    # segment colors are provided by theme.py
    color_map = {
        segment: segment_style(
            segment
        )["color"]
        for segment
        in segment_counts["Segment"]
    }

    fig_donut = px.pie(
        segment_counts,
        names="Segment",
        values="Customers",
        hole=0.58,
        color="Segment",
        color_discrete_map=color_map,
    )

    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Customers: %{value:,}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#F7F3E8",
                width=3,
            )
        ),
    )

    apply_plotly_theme(
        fig_donut,
        height=360,
        show_legend=True,
    )

    st.plotly_chart(
        fig_donut,
        use_container_width=True,
    )


# ============================================================
# CHART 2 — SEGMENT METRICS
# ============================================================

with chart_right:

    st.subheader(
        "Segment Metrics Comparison"
    )

    cluster_stats = (
        calculate_cluster_statistics(df)
    )

    available_metrics = [
        metric
        for metric in [
            "Income",
            "TotalSpending",
            "TotalPurchases",
            "Recency",
        ]
        if metric in cluster_stats.columns
    ]

    if available_metrics:

        # ----------------------------------------------------
        # Normalize metrics to allow comparison
        # ----------------------------------------------------

        comparison_data = []

        for _, row in cluster_stats.iterrows():

            segment_name = row[
                "Cluster_Name"
            ]

            comparison_data.append(
                {
                    "Segment": segment_name,
                    "Average Income": (
                        row.get(
                            "Income",
                            0
                        )
                    ),
                    "Average Spending": (
                        row.get(
                            "TotalSpending",
                            0
                        )
                    ),
                    "Average Purchases": (
                        row.get(
                            "TotalPurchases",
                            0
                        )
                    ),
                    "Average Recency": (
                        row.get(
                            "Recency",
                            0
                        )
                    ),
                }
            )

        comparison_df = pd.DataFrame(
            comparison_data
        )

        # ----------------------------------------------------
        # Create grouped bar chart
        # ----------------------------------------------------

        fig_bar = go.Figure()

        for _, row in comparison_df.iterrows():

            segment_name = row[
                "Segment"
            ]

            style = segment_style(
                segment_name
            )

            # Scale income so it doesn't dominate
            income_scaled = (
                row["Average Income"]
                / 1000
            )

            fig_bar.add_trace(
                go.Bar(
                    name=segment_name,
                    x=[
                        "Income ($K)",
                        "Spending ($)",
                        "Purchases",
                        "Recency (Days)",
                    ],
                    y=[
                        income_scaled,
                        row["Average Spending"],
                        row["Average Purchases"],
                        row["Average Recency"],
                    ],
                    marker_color=style[
                        "color"
                    ],
                    hovertemplate=(
                        "<b>"
                        + segment_name
                        + "</b><br>"
                        "%{x}: %{y:,.1f}"
                        "<extra></extra>"
                    ),
                )
            )

        fig_bar.update_layout(
            barmode="group",
            bargap=0.25,
        )

        apply_plotly_theme(
            fig_bar,
            height=360,
            show_legend=True,
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
        )

    else:

        st.info(
            "Segment comparison data is unavailable."
        )


# ============================================================
# 2D CUSTOMER SEGMENTATION MAP
# ============================================================

st.markdown(
    "<div style='height: 0.6rem'></div>",
    unsafe_allow_html=True,
)

st.subheader(
    "Customer Segmentation Map"
)

st.caption(
    "Customer distribution based on income and total spending."
)


if (
    "Income" in df.columns
    and "TotalSpending" in df.columns
):

    # Keep chart responsive for large datasets
    sample_size = min(
        1500,
        len(df)
    )

    if len(df) > sample_size:

        sample_df = df.sample(
            n=sample_size,
            random_state=42,
        )

    else:

        sample_df = df.copy()


    color_map_scatter = {
        segment: segment_style(
            segment
        )["color"]
        for segment
        in sample_df[
            "Cluster_Name"
        ].unique()
    }


    scatter_kwargs = {
        "data_frame": sample_df,
        "x": "Income",
        "y": "TotalSpending",
        "color": "Cluster_Name",
        "color_discrete_map": color_map_scatter,
        "opacity": 0.78,
        "labels": {
            "Income": "Annual Income",
            "TotalSpending": "Total Spending",
            "Cluster_Name": "Customer Segment",
        },
    }


    # Add available hover columns only
    hover_columns = {}

    if "ID" in sample_df.columns:
        hover_columns["ID"] = True

    hover_columns["Income"] = ":$,.0f"
    hover_columns[
        "TotalSpending"
    ] = ":$,.0f"

    if "TotalPurchases" in sample_df.columns:
        hover_columns[
            "TotalPurchases"
        ] = ":.0f"

    if "Recency" in sample_df.columns:
        hover_columns[
            "Recency"
        ] = ":.0f"

    hover_columns[
        "Cluster_Name"
    ] = False

    scatter_kwargs[
        "hover_data"
    ] = hover_columns


    fig_scatter = px.scatter(
        **scatter_kwargs
    )


    fig_scatter.update_traces(
        marker=dict(
            size=7,
            line=dict(
                width=0.7,
                color="#F7F3E8",
            ),
        ),
    )


    apply_plotly_theme(
        fig_scatter,
        height=440,
        show_legend=True,
    )


    st.plotly_chart(
        fig_scatter,
        use_container_width=True,
    )

else:

    st.info(
        "Income and spending data are required "
        "to display the segmentation map."
    )


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.markdown(
    "<div style='height: 0.6rem'></div>",
    unsafe_allow_html=True,
)

st.subheader(
    "Key Business Insights"
)

st.write(
    "Data-driven observations generated from the current customer segmentation."
)


try:

    insights = generate_business_insights(
        df,
        cluster_stats,
    )

except Exception as exc:

    insights = []

    st.warning(
        f"Unable to generate business insights: {exc}"
    )


if insights:

    for insight in insights:

        insight_card(
            title=insight.get(
                "title",
                "Business Insight",
            ),
            description=insight.get(
                "description",
                "",
            ),
            icon=insight.get(
                "icon",
                "lightbulb",
            ),
            accent=insight.get(
                "accent",
                "green",
            ),
        )

else:

    st.info(
        "No additional insights are available "
        "for the current filter selection."
    )