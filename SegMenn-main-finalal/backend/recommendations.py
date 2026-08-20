"""
SegMen - Recommendations Module
Data-driven & Business-Rule based strategy engines for segments and individual customer profiles.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from backend.analysis import calculate_cluster_statistics


def get_segment_recommendations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate rich strategy recommendations for each customer segment based on actual data.
    """
    cluster_stats = calculate_cluster_statistics(df)
    if cluster_stats.empty:
        return []

    recommendations = []

    for cluster_id, row in cluster_stats.iterrows():
        cname = str(row["Cluster_Name"])
        count = int(row["CustomerCount"])
        share = float(row["SharePercentage"])
        avg_spend = float(row.get("TotalSpending", 0.0))
        avg_income = float(row.get("Income", 0.0))
        avg_purchases = float(row.get("TotalPurchases", 0.0))
        recency = float(row.get("Recency", 0.0))
        deal_share = float(row.get("DealPurchaseShare_mean", 0.0)) * 100
        camp_resp = float(row.get("CampaignAcceptedCount_mean", 0.0))

        # Dynamic strategy assignment based on spending & income
        if avg_spend >= 1200 or "Premium" in cname or "High Value" in cname:
            characteristics = (
                f"High income (${avg_income:,.0f}/yr) and high spending (${avg_spend:,.0f} avg). "
                f"They buy frequently in store and from catalogs."
            )
            strategy = "Reward loyalty and offer early access to new products."
            goal = "Keep them loyal and increase repeat orders."
            action_items = [
                "Reward top spenders with exclusive perks and dedicated support.",
                "Offer early access to new product releases and reserve collections.",
                "Provide special luxury product bundles.",
            ]
            accent = "green"
            icon = "trophy"

        elif avg_spend >= 500 or "Regular" in cname or "Growth" in cname:
            characteristics = (
                f"Middle to high income (${avg_income:,.0f}/yr) with steady purchases (${avg_spend:,.0f} spend, {avg_purchases:.1f} orders)."
            )
            strategy = "Encourage higher order sizes and offer complementary items."
            goal = "Increase average purchases and turn them into premium spenders."
            action_items = [
                "Recommend related products when they shop.",
                "Offer free fast delivery on orders above a target total.",
                "Send helpful reminders for repeat purchases.",
            ]
            accent = "accent"
            icon = "groups"

        else:
            characteristics = (
                f"Price-sensitive customers (${avg_income:,.0f}/yr income) who look for deals ({deal_share:.1f}% deal purchases)."
            )
            strategy = "Offer targeted discounts and value packs to encourage orders."
            goal = "Re-engage inactive buyers and keep purchases consistent."
            action_items = [
                "Promote flash sales and discount coupons.",
                "Offer affordable product bundles and starter packs.",
                "Send automated reminders if they have not ordered in over 45 days.",
            ]
            accent = "accent_2"
            icon = "tag"

        recommendations.append({
            "cluster_id": int(cluster_id),
            "name": cname,
            "count": count,
            "share": share,
            "avg_spend": avg_spend,
            "avg_income": avg_income,
            "avg_purchases": avg_purchases,
            "recency": recency,
            "characteristics": characteristics,
            "strategy": strategy,
            "goal": goal,
            "action_items": action_items,
            "accent": accent,
            "icon": icon,
        })

    return recommendations


def get_customer_recommendation(customer_id: int, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Lookup a specific customer and generate personalized benchmark analysis and tailored actions.
    """
    if "ID" not in df.columns:
        return {"error": "Customer ID column not found in dataset."}

    matched = df[df["ID"] == customer_id]
    if matched.empty:
        return {"error": f"Customer ID {customer_id} was not found in the customer database."}

    cust = matched.iloc[0]
    cluster_id = int(cust.get("Cluster", 0))
    cluster_name = str(cust.get("Cluster_Name", f"Cluster {cluster_id}"))

    # Overall and cluster-specific benchmarks
    cluster_subset = df[df["Cluster"] == cluster_id]

    cust_spend = float(cust.get("TotalSpending", 0.0))
    cluster_avg_spend = float(cluster_subset["TotalSpending"].mean()) if "TotalSpending" in cluster_subset.columns else cust_spend
    overall_avg_spend = float(df["TotalSpending"].mean()) if "TotalSpending" in df.columns else cust_spend

    cust_income = float(cust.get("Income", 0.0))
    cluster_avg_income = float(cluster_subset["Income"].mean()) if "Income" in cluster_subset.columns else cust_income
    overall_avg_income = float(df["Income"].mean()) if "Income" in df.columns else cust_income

    cust_purchases = float(cust.get("TotalPurchases", 0.0))
    cluster_avg_purchases = float(cluster_subset["TotalPurchases"].mean()) if "TotalPurchases" in cluster_subset.columns else cust_purchases

    cust_recency = float(cust.get("Recency", 0.0))
    deal_share = float(cust.get("DealPurchaseShare", 0.0)) * 100
    web_visits = float(cust.get("NumWebVisitsMonth", 0.0))
    camp_accepted = int(cust.get("CampaignAcceptedCount", 0))
    age = int(cust.get("Age", 45))
    education = str(cust.get("Education", "Graduation"))
    marital_status = str(cust.get("Marital_Status", "Single"))
    children = int(cust.get("TotalChildren", 0))

    # Tailored recommendations
    personalized_actions: List[str] = []

    # Recency-based trigger
    if cust_recency > 70:
        personalized_actions.append(
            f"Has not ordered recently ({cust_recency:.0f} days inactive): Send a reminder email with a small discount."
        )
    elif cust_recency < 20:
        personalized_actions.append(
            f"Active shopper ({cust_recency:.0f} days since last purchase): Ask for feedback and recommend complementary items."
        )

    # Spending & Value trigger
    if cust_spend > cluster_avg_spend * 1.2:
        personalized_actions.append(
            f"High spender (${cust_spend:,.2f}): Offer exclusive rewards and early product access."
        )
    elif cust_spend < cluster_avg_spend * 0.7:
        personalized_actions.append(
            f"Below-average spending (${cust_spend:,.2f}): Offer a discount bundle to encourage a larger order."
        )

    # Channel & Deal trigger
    if deal_share > 40:
        personalized_actions.append(
            f"Responds well to deals ({deal_share:.0f}% deal purchases): Send promotional codes and clearance alerts."
        )
    if web_visits >= 6:
        personalized_actions.append(
            f"Frequent web visitor ({web_visits:.0f} visits/mo): Show personalized website offers."
        )

    # Campaign responsiveness
    if camp_accepted > 0:
        personalized_actions.append(
            "Responds to marketing campaigns: Include in direct promotion lists."
        )
    else:
        personalized_actions.append(
            "Has not responded to prior email campaigns: Try special offer notifications."
        )

    return {
        "customer_id": customer_id,
        "cluster": cluster_id,
        "cluster_name": cluster_name,
        "demographics": {
            "Age": age,
            "Education": education,
            "Marital_Status": marital_status,
            "TotalChildren": children,
        },
        "metrics": {
            "Income": cust_income,
            "TotalSpending": cust_spend,
            "TotalPurchases": cust_purchases,
            "Recency": cust_recency,
            "DealPurchaseShare": deal_share,
            "NumWebVisitsMonth": web_visits,
            "CampaignAcceptedCount": camp_accepted,
        },
        "benchmarks": {
            "cluster_avg_spend": cluster_avg_spend,
            "overall_avg_spend": overall_avg_spend,
            "cluster_avg_income": cluster_avg_income,
            "overall_avg_income": overall_avg_income,
            "cluster_avg_purchases": cluster_avg_purchases,
        },
        "tailored_actions": personalized_actions,
    }
