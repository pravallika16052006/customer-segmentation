"""
SegMen - Analysis Module
Aggregations, statistical profiling, distribution calculations, and dynamic business insights.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

CATEGORY_COLUMNS = {
    "MntWines": "Wines",
    "MntMeatProducts": "Meat Products",
    "MntGoldProds": "Gold Products",
    "MntFishProducts": "Fish Products",
    "MntFruits": "Fruits",
    "MntSweetProducts": "Sweets",
}

CHANNEL_COLUMNS = {
    "NumStorePurchases": "In-Store",
    "NumWebPurchases": "Web Orders",
    "NumCatalogPurchases": "Catalog",
    "NumDealsPurchases": "Discount Deals",
}


def calculate_cluster_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute aggregated metric averages and summaries for each customer cluster.
    """
    if df.empty or "Cluster" not in df.columns:
        return pd.DataFrame()

    agg_dict = {
        "ID": "count",
        "Income": ["mean", "median"],
        "TotalSpending": ["mean", "median"],
        "TotalPurchases": ["mean", "median"],
        "Recency": ["mean", "median"],
        "Age": "mean",
        "TotalChildren": "mean",
        "CustomerTenureDays": "mean",
        "DealPurchaseShare": "mean",
        "WebPurchaseShare": "mean",
        "CatalogPurchaseShare": "mean",
        "StorePurchaseShare": "mean",
        "NumWebVisitsMonth": "mean",
        "CampaignAcceptedCount": "mean",
    }

    # Filter only available columns
    clean_agg = {k: v for k, v in agg_dict.items() if k in df.columns}
    grouped = df.groupby("Cluster").agg(clean_agg)

    # Flatten multi-level column names
    flat_cols = []
    for col in grouped.columns:
        if isinstance(col, tuple):
            metric, stat = col
            flat_cols.append(f"{metric}_{stat}" if stat != "count" else "CustomerCount")
        else:
            flat_cols.append(str(col))
    grouped.columns = flat_cols

    total_customers = len(df)
    grouped["SharePercentage"] = (grouped["CustomerCount"] / total_customers) * 100

    # Cluster Names map
    cluster_names = df.groupby("Cluster")["Cluster_Name"].first().to_dict()
    grouped["Cluster_Name"] = grouped.index.map(cluster_names)

    # Reorder key columns nicely
    if "TotalSpending_mean" in grouped.columns:
        grouped["TotalSpending"] = grouped["TotalSpending_mean"]
    if "Income_mean" in grouped.columns:
        grouped["Income"] = grouped["Income_mean"]
    if "TotalPurchases_mean" in grouped.columns:
        grouped["TotalPurchases"] = grouped["TotalPurchases_mean"]
    if "Recency_mean" in grouped.columns:
        grouped["Recency"] = grouped["Recency_mean"]

    return grouped


def generate_business_insights(df: pd.DataFrame, cluster_stats: Optional[pd.DataFrame] = None) -> List[Dict[str, str]]:
    """
    Generate dynamic, data-driven business insights using simple, clear titles and descriptions.
    """
    if cluster_stats is None or cluster_stats.empty:
        cluster_stats = calculate_cluster_statistics(df)

    if cluster_stats.empty:
        return []

    insights = []

    # 1. Largest Segment
    largest_cluster_idx = cluster_stats["CustomerCount"].idxmax()
    largest_name = cluster_stats.loc[largest_cluster_idx, "Cluster_Name"]
    largest_count = int(cluster_stats.loc[largest_cluster_idx, "CustomerCount"])
    largest_share = float(cluster_stats.loc[largest_cluster_idx, "SharePercentage"])
    insights.append({
        "title": "Largest Customer Group",
        "icon": "groups",
        "accent": "accent",
        "description": (
            f"**{largest_name}** are the largest group, with "
            f"**{largest_count:,} customers ({largest_share:.1f}% of all customers)**. "
            "They buy often, so keeping them interested can help maintain sales."
        ),
    })

    # 2. Highest Spending / Customer Lifetime Value
    highest_spend_idx = cluster_stats["TotalSpending"].idxmax()
    highest_spend_name = cluster_stats.loc[highest_spend_idx, "Cluster_Name"]
    highest_spend_val = float(cluster_stats.loc[highest_spend_idx, "TotalSpending"])
    overall_spend = float(df["TotalSpending"].mean()) if "TotalSpending" in df.columns else 1.0
    spend_multiplier = highest_spend_val / max(overall_spend, 1.0)
    insights.append({
        "title": "Customers Who Spend the Most",
        "icon": "trophy",
        "accent": "green",
        "description": (
            f"**{highest_spend_name}** spend the most, with an average spending of "
            f"**${highest_spend_val:,.2f}** ({spend_multiplier:.1f}x the overall average). "
            "Give them special rewards and premium products to encourage them to keep buying."
        ),
    })

    # 3. Deal Sensitivity / Lowest Engagement
    if "DealPurchaseShare_mean" in cluster_stats.columns:
        deal_idx = cluster_stats["DealPurchaseShare_mean"].idxmax()
        deal_name = cluster_stats.loc[deal_idx, "Cluster_Name"]
        deal_share = float(cluster_stats.loc[deal_idx, "DealPurchaseShare_mean"]) * 100
        avg_visits = float(cluster_stats.loc[deal_idx, "NumWebVisitsMonth_mean"]) if "NumWebVisitsMonth_mean" in cluster_stats.columns else 0.0
        insights.append({
            "title": "Customers Who Like Discounts",
            "icon": "tag",
            "accent": "accent_2",
            "description": (
                f"**{deal_name}** often use discounts (**{deal_share:.1f}% of purchases**), "
                f"and they visit the website frequently ({avg_visits:.1f} visits/mo) looking for offers. "
                "Give them discounts, bundle deals, and special sales."
            ),
        })

    # 4. Campaign Responsiveness & Engagement
    if "CampaignAcceptedCount_mean" in cluster_stats.columns:
        camp_idx = cluster_stats["CampaignAcceptedCount_mean"].idxmax()
        camp_name = cluster_stats.loc[camp_idx, "Cluster_Name"]
        camp_acc = float(cluster_stats.loc[camp_idx, "CampaignAcceptedCount_mean"])
        insights.append({
            "title": "Customers Who Respond to Offers",
            "icon": "lightbulb",
            "accent": "green",
            "description": (
                f"**{camp_name}** respond well to offers, with an average of "
                f"**{camp_acc:.2f} accepted campaigns per customer**. "
                "Send them new product offers early and give them offers based on what they buy."
            ),
        })

    return insights


def generate_segment_narrative(
    segment_name: str,
    cluster_id: int,
    stats: pd.Series,
    overall_df: pd.DataFrame,
) -> str:
    """
    Generate a dynamic, statistical narrative paragraph for a given segment.
    """
    avg_income = stats.get("Income", stats.get("Income_mean", 0.0))
    avg_spending = stats.get("TotalSpending", stats.get("TotalSpending_mean", 0.0))
    avg_purchases = stats.get("TotalPurchases", stats.get("TotalPurchases_mean", 0.0))
    avg_recency = stats.get("Recency", stats.get("Recency_mean", 0.0))
    avg_age = stats.get("Age_mean", 45.0)
    deal_share = stats.get("DealPurchaseShare_mean", 0.0) * 100

    overall_income = overall_df["Income"].mean() if "Income" in overall_df.columns else avg_income
    overall_spend = overall_df["TotalSpending"].mean() if "TotalSpending" in overall_df.columns else avg_spending

    income_rel = "above average" if avg_income >= overall_income else "budget-conscious"
    spend_rel = "high spending" if avg_spending >= overall_spend else "modest spending"

    narrative = (
        f"This segment represents **{segment_name}** (Cluster {cluster_id}). "
        f"Customers in this group have an average annual income of **${avg_income:,.2f}** ({income_rel}) "
        f"and an average total spend of **${avg_spending:,.2f}** ({spend_rel}) across an average of "
        f"**{avg_purchases:.1f} recorded purchases**. Their average recency stands at **{avg_recency:.1f} days**, "
        f"with an average age of **{avg_age:.0f} years**. Approximately **{deal_share:.1f}%** of their transactions "
        "involve promotional discount deals."
    )
    return narrative


def get_category_spending_breakdown(df: pd.DataFrame, cluster_id: Optional[int] = None) -> pd.DataFrame:
    """
    Calculate average expenditure across product categories.
    """
    target = df if cluster_id is None else df[df["Cluster"] == cluster_id]
    if target.empty:
        return pd.DataFrame()

    categories = []
    amounts = []
    shares = []
    total_cat_spend = 0.0

    for col, label in CATEGORY_COLUMNS.items():
        if col in target.columns:
            avg_amt = float(target[col].mean())
            categories.append(label)
            amounts.append(avg_amt)
            total_cat_spend += avg_amt

    if total_cat_spend > 0:
        shares = [(a / total_cat_spend) * 100 for a in amounts]
    else:
        shares = [0.0] * len(amounts)

    res_df = pd.DataFrame({
        "Category": categories,
        "AverageSpend": amounts,
        "SpendShare": shares,
    }).sort_values(by="AverageSpend", ascending=False)

    return res_df


def get_channel_breakdown(df: pd.DataFrame, cluster_id: Optional[int] = None) -> pd.DataFrame:
    """
    Calculate distribution across purchase channels.
    """
    target = df if cluster_id is None else df[df["Cluster"] == cluster_id]
    if target.empty:
        return pd.DataFrame()

    channels = []
    counts = []
    for col, label in CHANNEL_COLUMNS.items():
        if col in target.columns:
            channels.append(label)
            counts.append(float(target[col].mean()))

    total_c = sum(counts) if sum(counts) > 0 else 1.0
    shares = [(c / total_c) * 100 for c in counts]

    return pd.DataFrame({
        "Channel": channels,
        "AverageOrders": counts,
        "SharePercentage": shares,
    }).sort_values(by="AverageOrders", ascending=False)


def get_radar_chart_data(df: pd.DataFrame) -> Tuple[List[str], Dict[str, List[float]]]:
    """
    Generate normalized radar chart metrics (0 to 100 scale) for all clusters.
    """
    dimensions = [
        "Income Level",
        "Total Spending",
        "Purchase Volume",
        "Customer Recency",
        "Digital Activity",
        "Promo Sensitivity",
    ]

    cluster_stats = calculate_cluster_statistics(df)
    if cluster_stats.empty:
        return dimensions, {}

    # Extract raw metrics
    raw_data: Dict[str, Dict[str, float]] = {}
    for cl_idx, row in cluster_stats.iterrows():
        cname = str(row["Cluster_Name"])
        raw_data[cname] = {
            "Income Level": float(row.get("Income", 0.0)),
            "Total Spending": float(row.get("TotalSpending", 0.0)),
            "Purchase Volume": float(row.get("TotalPurchases", 0.0)),
            "Customer Recency": float(row.get("Recency", 0.0)),
            "Digital Activity": float(row.get("NumWebVisitsMonth_mean", 0.0)),
            "Promo Sensitivity": float(row.get("DealPurchaseShare_mean", 0.0)) * 100,
        }

    # Normalize each dimension to 10-100 scale
    normalized: Dict[str, List[float]] = {cname: [] for cname in raw_data}

    for dim in dimensions:
        vals = [raw_data[cname][dim] for cname in raw_data]
        min_v = min(vals)
        max_v = max(vals)
        spread = max_v - min_v if max_v != min_v else 1.0

        for cname in raw_data:
            scaled = 15.0 + ((raw_data[cname][dim] - min_v) / spread) * 80.0
            normalized[cname].append(round(scaled, 1))

    return dimensions, normalized


def get_distribution_data(df: pd.DataFrame, column: str, cluster_id: Optional[int] = None) -> pd.Series:
    """
    Extract clean series for distribution histograms.
    """
    target = df if cluster_id is None else df[df["Cluster"] == cluster_id]
    if column not in target.columns:
        return pd.Series(dtype=float)
    return target[column].dropna()
