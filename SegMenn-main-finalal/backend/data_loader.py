"""
SegMen - Data Loader Module
Handles loading, caching, feature validation, and preprocessing for customer data.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

# Safe Streamlit caching wrapper
try:
    import streamlit as st
    cache_data = getattr(st, "cache_data", lambda func: func)
except Exception:
    def cache_data(func):
        return func


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
CUSTOMER_CLEANED_PATH = PROCESSED_DATA_DIR / "customer_cleaned.csv"
CUSTOMER_SEGMENTS_PATH = PROCESSED_DATA_DIR / "customer_segments.csv"
CLUSTER_PROFILES_PATH = PROCESSED_DATA_DIR / "cluster_profiles.csv"

# Required raw input features
REQUIRED_COLUMNS = [
    "ID",
    "Year_Birth",
    "Education",
    "Marital_Status",
    "Income",
    "Kidhome",
    "Teenhome",
    "Dt_Customer",
    "Recency",
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds",
    "NumDealsPurchases",
    "NumWebPurchases",
    "NumCatalogPurchases",
    "NumStorePurchases",
    "NumWebVisitsMonth",
]

SPENDING_COLUMNS = [
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds",
]

PURCHASE_COLUMNS = [
    "NumWebPurchases",
    "NumCatalogPurchases",
    "NumStorePurchases",
]

CAMPAIGN_COLUMNS = [
    "AcceptedCmp1",
    "AcceptedCmp2",
    "AcceptedCmp3",
    "AcceptedCmp4",
    "AcceptedCmp5",
]


def engineer_features(df: pd.DataFrame, reference_year: int = 2014, reference_date: str = "2014-06-29") -> pd.DataFrame:
    """
    Enrich customer DataFrame with derived business metrics.
    Ensures feature parity across both trained models and dashboard analytics.
    """
    data = df.copy()

    # Customer registration & tenure
    if "Dt_Customer" in data.columns:
        customer_dates = pd.to_datetime(data["Dt_Customer"], errors="coerce")
        ref_ts = pd.Timestamp(reference_date)
        data["CustomerTenureDays"] = (ref_ts - customer_dates).dt.days.fillna(365).astype(int)

    # Age
    if "Year_Birth" in data.columns and "Age" not in data.columns:
        data["Age"] = int(reference_year) - data["Year_Birth"]

    # Total Children
    if "Kidhome" in data.columns and "Teenhome" in data.columns:
        data["TotalChildren"] = data["Kidhome"] + data["Teenhome"]

    # Total Spending
    available_spending = [c for c in SPENDING_COLUMNS if c in data.columns]
    if available_spending:
        data["TotalSpending"] = data[available_spending].sum(axis=1)

    # Total Purchases
    available_purchases = [c for c in PURCHASE_COLUMNS if c in data.columns]
    if available_purchases:
        data["TotalPurchases"] = data[available_purchases].sum(axis=1)

    # Purchase Shares
    if "TotalPurchases" in data.columns:
        total_p = data["TotalPurchases"].replace(0, np.nan)
        if "NumDealsPurchases" in data.columns:
            data["DealPurchaseShare"] = (data["NumDealsPurchases"] / total_p).fillna(0.0).clip(0.0, 1.0)
        if "NumWebPurchases" in data.columns:
            data["WebPurchaseShare"] = (data["NumWebPurchases"] / total_p).fillna(0.0).clip(0.0, 1.0)
        if "NumCatalogPurchases" in data.columns:
            data["CatalogPurchaseShare"] = (data["NumCatalogPurchases"] / total_p).fillna(0.0).clip(0.0, 1.0)
        if "NumStorePurchases" in data.columns:
            data["StorePurchaseShare"] = (data["NumStorePurchases"] / total_p).fillna(0.0).clip(0.0, 1.0)

    # Campaign Engagement
    available_campaigns = [c for c in CAMPAIGN_COLUMNS if c in data.columns]
    if available_campaigns:
        data["CampaignAcceptedCount"] = data[available_campaigns].sum(axis=1)

    return data


def get_active_data() -> Optional[pd.DataFrame]:
    """Return the dataset uploaded in the current Streamlit session.

    The dashboard intentionally has no bundled-data fallback. A user must
    upload a CSV/folder before the analytics pages can display data.
    """
    try:
        import streamlit as st
        df = st.session_state.get("active_dataset")
        return df.copy() if isinstance(df, pd.DataFrame) else None
    except Exception:
        return None


def set_active_data(df: pd.DataFrame, source_name: str = "Uploaded dataset") -> None:
    """Store the processed dataset for all pages in the current session."""
    if df is None or df.empty:
        raise ValueError("Cannot activate an empty dataset.")
    import streamlit as st
    st.session_state["active_dataset"] = df.copy()
    st.session_state["active_dataset_source"] = source_name
    st.session_state["active_dataset_rows"] = int(len(df))
    st.session_state["active_dataset_columns"] = int(len(df.columns))


def clear_active_data() -> None:
    """Clear the currently uploaded dataset from the session."""
    try:
        import streamlit as st
        for key in ("active_dataset", "active_dataset_source", "active_dataset_rows", "active_dataset_columns"):
            st.session_state.pop(key, None)
    except Exception:
        pass


@cache_data
def load_unified_data() -> pd.DataFrame:
    """
    Load the processed customer dataset and merge with cluster segment assignments.
    Cached for high performance.
    """
    if not CUSTOMER_CLEANED_PATH.exists():
        raise FileNotFoundError(
            f"Processed customer dataset not found at {CUSTOMER_CLEANED_PATH}. "
            "Please ensure customer_cleaned.csv is present in data/processed/."
        )

    try:
        df_cleaned = pd.read_csv(CUSTOMER_CLEANED_PATH)
    except Exception as exc:
        raise RuntimeError(f"Failed to read customer_cleaned.csv: {exc}") from exc

    # Validate essential columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df_cleaned.columns]
    if missing:
        raise ValueError(f"Customer dataset is missing required columns: {missing}")

    # Engineer missing columns
    df = engineer_features(df_cleaned)

    # Merge segment labels if available
    if CUSTOMER_SEGMENTS_PATH.exists():
        try:
            df_segments = pd.read_csv(CUSTOMER_SEGMENTS_PATH)
            if "ID" in df_segments.columns and "Cluster" in df_segments.columns:
                df = df.merge(
                    df_segments[["ID", "Cluster", "Cluster_Name"]],
                    on="ID",
                    how="left",
                )
        except Exception as exc:
            pass  # Fall back to model assignment if segments file has issues

    # If Cluster column is missing or has nulls, assign default cluster 0
    if "Cluster" not in df.columns:
        df["Cluster"] = 0
    df["Cluster"] = df["Cluster"].fillna(0).astype(int)

    # Default Cluster Names fallback
    default_names = {
        0: "Premium Customers",
        1: "Budget / Deal-Oriented Customers",
        2: "Regular Customers",
    }
    if "Cluster_Name" not in df.columns or df["Cluster_Name"].isna().any():
        df["Cluster_Name"] = df["Cluster"].map(default_names).fillna("Cluster " + df["Cluster"].astype(str))

    return df


@cache_data
def load_cluster_profiles() -> pd.DataFrame:
    """
    Load the pre-computed cluster profiles CSV if present.
    """
    if CLUSTER_PROFILES_PATH.exists():
        try:
            return pd.read_csv(CLUSTER_PROFILES_PATH)
        except Exception:
            pass
    return pd.DataFrame()


def get_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute key dataset summary metrics dynamically.
    """
    total_customers = len(df)
    unique_clusters = sorted(df["Cluster"].unique().tolist())
    num_clusters = len(unique_clusters)

    avg_spending = float(df["TotalSpending"].mean()) if "TotalSpending" in df.columns else 0.0
    avg_income = float(df["Income"].mean()) if "Income" in df.columns else 0.0
    avg_purchases = float(df["TotalPurchases"].mean()) if "TotalPurchases" in df.columns else 0.0
    avg_recency = float(df["Recency"].mean()) if "Recency" in df.columns else 0.0

    return {
        "total_customers": total_customers,
        "num_clusters": num_clusters,
        "unique_clusters": unique_clusters,
        "avg_spending": avg_spending,
        "avg_income": avg_income,
        "avg_purchases": avg_purchases,
        "avg_recency": avg_recency,
    }
