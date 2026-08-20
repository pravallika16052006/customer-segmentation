"""
SegMenAI - Recommendations Page
Strategic segment recommendations and individual customer next-best actions.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
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
from backend.recommendations import (
    get_segment_recommendations,
    get_customer_recommendation,
)

from frontend.theme import (
    inject_base_styles,
    page_header,
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
    title="Recommendations",
    subtitle="Simple strategies for each customer group and individual customer.",
)


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = get_active_data()

except Exception as exc:
    st.error(f"Unable to load customer dataset: {exc}")
    st.stop()


if df is None or df.empty:
    st.info("Upload a customer CSV from the Dashboard to begin analysis.")
    st.stop()


# ============================================================
# SECTION 1 — SEGMENT STRATEGIES
# ============================================================

st.subheader("Segment Strategies")

st.write(
    "Simple strategies designed for each customer group."
)


segment_recs = get_segment_recommendations(df)


# ============================================================
# SEGMENT STRATEGY CARDS
# ============================================================

cols = st.columns(len(segment_recs))


for idx, rec in enumerate(segment_recs):

    with cols[idx]:

        style = segment_style(rec["name"])

        color = style.get(
            "color",
            "#285943",
        )

        soft = style.get(
            "soft",
            "#F5F6F1",
        )

        icon_name = style.get(
            "icon",
            "groups",
        )

        characteristics = rec.get(
            "characteristics",
            "",
        )

        strategy = rec.get(
            "strategy",
            "",
        )

        goal = rec.get(
            "goal",
            "",
        )

        action_items = rec.get(
            "action_items",
            [],
        )

        if isinstance(action_items, str):
            action_items = [action_items]


        action_html = "".join(
            f"""
            <div style="
                display:flex;
                align-items:flex-start;
                gap:8px;
                margin-bottom:7px;
                color:#71807A;
                font-size:0.82rem;
                line-height:1.45;
            ">
                <span style="
                    color:{color};
                    font-weight:700;
                ">✓</span>

                <span>{item}</span>
            </div>
            """
            for item in action_items
        )


        _md(
            f"""
            <div style="
                background:#FFFDF7;
                border:1px solid #DDE3DC;
                border-top:4px solid {color};
                border-radius:14px;
                padding:1.25rem;
                min-height:470px;
                box-shadow:0 2px 8px rgba(24,58,55,0.05);
            ">

                <!-- Header -->

                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    margin-bottom:1rem;
                ">

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:9px;
                    ">

                        <div style="
                            color:{color};
                            display:flex;
                        ">
                            {icon_svg(icon_name, size=20)}
                        </div>

                        <div style="
                            font-size:1.05rem;
                            font-weight:800;
                            color:#183A37;
                        ">
                            {rec["name"]}
                        </div>

                    </div>

                    <span style="
                        background:{soft};
                        color:{color};
                        font-size:0.72rem;
                        font-weight:700;
                        padding:4px 9px;
                        border-radius:999px;
                    ">
                        {rec["share"]:.1f}%
                    </span>

                </div>


                <!-- Customer count -->

                <div style="
                    background:#F5F6F1;
                    border:1px solid #E1E6DF;
                    border-radius:10px;
                    padding:0.75rem;
                    margin-bottom:1rem;
                ">

                    <div style="
                        font-size:0.68rem;
                        text-transform:uppercase;
                        letter-spacing:0.04em;
                        color:#87966F;
                        font-weight:700;
                    ">
                        Customers
                    </div>

                    <div style="
                        font-size:1.35rem;
                        font-weight:800;
                        color:#183A37;
                        margin-top:2px;
                    ">
                        {rec["count"]:,}
                    </div>

                </div>


                <!-- Who they are -->

                <div style="
                    font-size:0.68rem;
                    text-transform:uppercase;
                    letter-spacing:0.05em;
                    color:#87966F;
                    font-weight:700;
                    margin-bottom:0.3rem;
                ">
                    Who they are
                </div>

                <div style="
                    color:#71807A;
                    font-size:0.84rem;
                    line-height:1.5;
                    margin-bottom:1rem;
                ">
                    {characteristics}
                </div>


                <!-- What to do -->

                <div style="
                    font-size:0.68rem;
                    text-transform:uppercase;
                    letter-spacing:0.05em;
                    color:#87966F;
                    font-weight:700;
                    margin-bottom:0.3rem;
                ">
                    What to do
                </div>

                <div style="
                    color:#26332F;
                    font-size:0.84rem;
                    line-height:1.5;
                    margin-bottom:1rem;
                ">
                    {strategy}
                </div>


                <!-- Actions -->

                <div style="
                    font-size:0.68rem;
                    text-transform:uppercase;
                    letter-spacing:0.05em;
                    color:#87966F;
                    font-weight:700;
                    margin-bottom:0.45rem;
                ">
                    Recommended Actions
                </div>

                {action_html}


                <!-- Goal -->

                <div style="
                    margin-top:0.9rem;
                    padding-top:0.8rem;
                    border-top:1px solid #E1E6DF;
                ">

                    <span style="
                        font-size:0.68rem;
                        text-transform:uppercase;
                        color:#87966F;
                        font-weight:700;
                    ">
                        Goal
                    </span>

                    <div style="
                        color:#285943;
                        font-size:0.82rem;
                        font-weight:700;
                        line-height:1.4;
                        margin-top:3px;
                    ">
                        {goal}
                    </div>

                </div>

            </div>
            """
        )


# ============================================================
# SECTION DIVIDER
# ============================================================

st.markdown(
    "<div style='height:1rem'></div>",
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# SECTION 2 — FIND A CUSTOMER
# ============================================================

st.subheader("Find a Customer")

st.write(
    "Search for an individual customer to view their segment details and recommendations."
)


# ============================================================
# SEARCH AREA
# ============================================================

search_col, sample_col = st.columns(
    [2.5, 1]
)


with search_col:

    cust_id_input = st.text_input(
        "Enter Customer ID",
        placeholder="Enter Customer ID, e.g. 5524",
        help=(
            "Enter an exact numeric Customer ID "
            "to view their personalized recommendations."
        ),
    )


# ------------------------------------------------------------
# SAMPLE CUSTOMER IDs
# ------------------------------------------------------------

sample_ids = []

if "Cluster" in df.columns and "ID" in df.columns:

    for cluster_id in sorted(
        df["Cluster"].dropna().unique()
    ):

        matching = df[
            df["Cluster"] == cluster_id
        ]

        if not matching.empty:

            sample_ids.append(
                str(
                    int(
                        matching.iloc[0]["ID"]
                    )
                )
            )


with sample_col:

    if sample_ids:

        st.markdown(
            """
            <div style="
                font-size:0.72rem;
                text-transform:uppercase;
                letter-spacing:0.04em;
                color:#87966F;
                font-weight:700;
                margin-bottom:6px;
            ">
                Sample IDs
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="
                color:#71807A;
                font-size:0.82rem;
                line-height:1.5;
            ">
                {", ".join(sample_ids)}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# CUSTOMER RESULT
# ============================================================

if cust_id_input.strip():

    try:

        target_id = int(
            cust_id_input.strip()
        )

        result = get_customer_recommendation(
            target_id,
            df,
        )


        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        if "error" in result:

            st.error(
                result["error"]
            )

        else:

            cname = result["cluster_name"]
            cid = result["cluster"]

            style = segment_style(cname)

            color = style.get(
                "color",
                "#285943",
            )

            soft = style.get(
                "soft",
                "#F5F6F1",
            )

            icon_name = style.get(
                "icon",
                "person",
            )

            metrics = result["metrics"]
            demog = result["demographics"]
            bench = result["benchmarks"]
            tailored = result["tailored_actions"]
            # CUSTOMER PROFILE HEADER
            # ====================================================

            _md(
                f"""
                <div style="
                    background:#FFFDF7;
                    border:1px solid #DDE3DC;
                    border-left:5px solid {color};
                    border-radius:14px;
                    padding:1.25rem;
                    margin-top:1rem;
                    box-shadow:0 2px 8px rgba(24,58,55,0.05);
                ">

                    <div style="
                        display:flex;
                        align-items:center;
                        justify-content:space-between;
                    ">

                        <div>

                            <div style="
                                font-size:0.68rem;
                                text-transform:uppercase;
                                letter-spacing:0.05em;
                                color:#87966F;
                                font-weight:700;
                            ">
                                Customer Profile
                            </div>

                            <div style="
                                font-size:1.35rem;
                                font-weight:800;
                                color:#183A37;
                                margin-top:3px;
                            ">
                                Customer #{target_id}
                            </div>

                        </div>


                        <div style="
                            display:flex;
                            align-items:center;
                            gap:7px;
                            background:{soft};
                            color:{color};
                            padding:6px 11px;
                            border-radius:999px;
                            font-size:0.8rem;
                            font-weight:700;
                        ">

                            {icon_svg(icon_name, size=15)}

                            {cname}

                        </div>

                    </div>

                </div>
                """
            )


            # ====================================================
            # CUSTOMER KPIs
            # ====================================================

            st.markdown(
                "<div style='height:0.7rem'></div>",
                unsafe_allow_html=True,
            )

            m1, m2, m3, m4 = st.columns(4)


            with m1:

                st.metric(
                    "Total Spending",
                    f"${metrics['TotalSpending']:,.2f}",
                    delta=(
                        f"${metrics['TotalSpending'] - bench['cluster_avg_spend']:+,.0f} "
                        "vs Segment Avg"
                    ),
                )


            with m2:

                st.metric(
                    "Annual Income",
                    f"${metrics['Income']:,.0f}",
                    delta=(
                        f"${metrics['Income'] - bench['cluster_avg_income']:+,.0f} "
                        "vs Segment Avg"
                    ),
                )


            with m3:

                st.metric(
                    "Total Orders",
                    f"{metrics['TotalPurchases']:.0f}",
                    delta=(
                        f"{metrics['TotalPurchases'] - bench['cluster_avg_purchases']:+.1f} "
                        "vs Segment Avg"
                    ),
                )


            with m4:

                st.metric(
                    "Recency",
                    f"{metrics['Recency']:.0f} days",
                    help="Days since the customer's last transaction.",
                )


            # ====================================================
            # PROFILE DETAILS
            # ====================================================

            st.markdown(
                "<div style='height:0.6rem'></div>",
                unsafe_allow_html=True,
            )

            detail_left, detail_right = st.columns(2)


            # ----------------------------------------------------
            # DEMOGRAPHICS
            # ----------------------------------------------------

            with detail_left:

                _md(
                    f"""
                    <div style="
                        background:#F5F6F1;
                        border:1px solid #E1E6DF;
                        border-radius:12px;
                        padding:1rem;
                    ">

                        <div style="
                            font-size:0.72rem;
                            text-transform:uppercase;
                            letter-spacing:0.04em;
                            color:#87966F;
                            font-weight:700;
                            margin-bottom:0.6rem;
                        ">
                            Customer Details
                        </div>

                        <div style="
                            color:#71807A;
                            font-size:0.86rem;
                            line-height:1.8;
                        ">

                            <b style="color:#26332F;">
                                Age
                            </b>
                            &nbsp; {demog['Age']} years
                            <br>

                            <b style="color:#26332F;">
                                Education
                            </b>
                            &nbsp; {demog['Education']}
                            <br>

                            <b style="color:#26332F;">
                                Marital Status
                            </b>
                            &nbsp; {demog['Marital_Status']}
                            <br>

                            <b style="color:#26332F;">
                                Children
                            </b>
                            &nbsp; {demog['TotalChildren']}

                        </div>

                    </div>
                    """
                )


            # ----------------------------------------------------
            # BEHAVIORAL SIGNALS
            # ----------------------------------------------------

            with detail_right:

                deal_share = metrics.get(
                    "DealPurchaseShare",
                    0,
                )

                # Handle both fraction and percentage formats
                if deal_share <= 1:
                    deal_share_display = (
                        deal_share * 100
                    )
                else:
                    deal_share_display = deal_share


                web_visits = metrics.get(
                    "NumWebVisitsMonth",
                    0,
                )

                campaign_count = metrics.get(
                    "CampaignAcceptedCount",
                    0,
                )

                customer_status = (
                    "Active Shopper"
                    if metrics["Recency"] < 50
                    else "Reactivation Candidate"
                )


                _md(
                    f"""
                    <div style="
                        background:#F5F6F1;
                        border:1px solid #E1E6DF;
                        border-radius:12px;
                        padding:1rem;
                    ">

                        <div style="
                            font-size:0.72rem;
                            text-transform:uppercase;
                            letter-spacing:0.04em;
                            color:#87966F;
                            font-weight:700;
                            margin-bottom:0.6rem;
                        ">
                            Behavioral Signals
                        </div>

                        <div style="
                            color:#71807A;
                            font-size:0.86rem;
                            line-height:1.8;
                        ">

                            <b style="color:#26332F;">
                                Deal Purchase Share
                            </b>
                            &nbsp; {deal_share_display:.1f}%
                            <br>

                            <b style="color:#26332F;">
                                Web Visits / Month
                            </b>
                            &nbsp; {web_visits:.0f}
                            <br>

                            <b style="color:#26332F;">
                                Campaign Responses
                            </b>
                            &nbsp; {campaign_count}
                            <br>

                            <b style="color:#26332F;">
                                Status
                            </b>
                            &nbsp;
                            <span style="
                                color:{color};
                                font-weight:700;
                            ">
                                {customer_status}
                            </span>

                        </div>

                    </div>
                    """
                )


            # ====================================================
            # PERSONALIZED ACTIONS
            # ====================================================

            st.markdown(
                "<div style='height:0.8rem'></div>",
                unsafe_allow_html=True,
            )

            _md(
                """
                <div style="
                    font-size:0.72rem;
                    text-transform:uppercase;
                    letter-spacing:0.05em;
                    color:#87966F;
                    font-weight:700;
                    margin-bottom:0.5rem;
                ">
                    Recommended Actions
                </div>
                """
            )


            if tailored:

                action_html = ""

                for action in tailored:

                    action_html += f"""
                    <div style="
                        display:flex;
                        align-items:flex-start;
                        gap:10px;
                        background:#FFFDF7;
                        border:1px solid #E1E6DF;
                        border-left:3px solid {color};
                        border-radius:9px;
                        padding:0.75rem 0.9rem;
                        margin-bottom:0.55rem;
                    ">

                        <div style="
                            color:{color};
                            display:flex;
                            flex-shrink:0;
                            margin-top:2px;
                        ">
                            {icon_svg("check-circle", size=16)}
                        </div>

                        <div style="
                            color:#26332F;
                            font-size:0.86rem;
                            line-height:1.5;
                        ">
                            {action}
                        </div>

                    </div>
                    """


                _md(action_html)

            else:

                st.info(
                    "No personalized actions are available "
                    "for this customer."
                )


    except ValueError:

        st.warning(
            "Please enter a valid numeric Customer ID."
        )