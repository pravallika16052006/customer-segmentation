from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd

try:
    import streamlit as st

    cache_resource = getattr(
        st,
        "cache_resource",
        lambda func: func,
    )
except Exception:
    def cache_resource(func):
        return func


from backend.data_loader import engineer_features


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "clustering_model.pkl"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.pkl"
METADATA_PATH = MODELS_DIR / "model_metadata.json"


# ============================================================
# FINAL MODEL FEATURES
# ============================================================

SELECTED_NUMERIC_FEATURES = [
    "Age",
    "Income",
    "TotalChildren",
    "CustomerTenureDays",
    "Recency",
    "TotalSpending",
    "TotalPurchases",
    "DealPurchaseShare",
    "WebPurchaseShare",
    "CatalogPurchaseShare",
    "NumWebVisitsMonth",
    "CampaignAcceptedCount",
]

SELECTED_CATEGORICAL_FEATURES = [
    "Education",
    "Marital_Status",
]

SELECTED_FEATURES = (
    SELECTED_NUMERIC_FEATURES
    + SELECTED_CATEGORICAL_FEATURES
)


# ============================================================
# REQUIRED RAW INPUT COLUMNS
# ============================================================

REQUIRED_INPUT_COLUMNS = {
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
    "AcceptedCmp1",
    "AcceptedCmp2",
    "AcceptedCmp3",
    "AcceptedCmp4",
    "AcceptedCmp5",
}


# ============================================================
# LOAD SAVED ML ARTIFACTS
# ============================================================

@cache_resource
def load_clustering_artifacts() -> Tuple[Any, Any, Dict[str, Any]]:
    """
    Load and cache:
    - preprocessing pipeline
    - trained K-Means model
    - model metadata
    """

    if not PREPROCESSOR_PATH.exists():
        raise FileNotFoundError(
            f"Preprocessor not found at {PREPROCESSOR_PATH}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Clustering model not found at {MODEL_PATH}"
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata not found at {METADATA_PATH}"
        )

    preprocessor = joblib.load(PREPROCESSOR_PATH)
    model = joblib.load(MODEL_PATH)

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        metadata = json.load(file)

    return preprocessor, model, metadata


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_customer_data(
    customers: pd.DataFrame,
    require_id: bool = False,
) -> None:
    """
    Validate raw customer data before ML inference.
    """

    if customers.empty:
        raise ValueError(
            "Customer dataset contains no rows."
        )

    if require_id and "ID" not in customers.columns:
        raise ValueError(
            "The dataset must contain an ID column."
        )

    missing_columns = sorted(
        REQUIRED_INPUT_COLUMNS
        - set(customers.columns)
    )

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{missing_columns}"
        )


# ============================================================
# CLUSTER NAME HELPERS
# ============================================================

def normalize_cluster_names(
    cluster_names: Dict[str, Any],
) -> Dict[int, str]:
    """
    Convert metadata cluster keys from JSON strings
    into integer cluster IDs.
    """

    return {
        int(key): str(value)
        for key, value in cluster_names.items()
    }


def get_dynamic_cluster_names(
    cluster_stats_df: pd.DataFrame,
) -> Dict[int, str]:
    """
    Generate descriptive names from cluster statistics.

    This is intended for analytical/display use.
    Prediction itself always uses the fixed cluster
    mapping stored in model_metadata.json.
    """

    if (
        cluster_stats_df.empty
        or "TotalSpending" not in cluster_stats_df.columns
    ):
        try:
            _, _, metadata = load_clustering_artifacts()

            return normalize_cluster_names(
                metadata.get("cluster_names", {})
            )

        except Exception:
            return {
                0: "Premium Customers",
                1: "Budget / Deal-Oriented Customers",
                2: "Regular Customers",
            }

    stats = cluster_stats_df.copy()

    sorted_stats = stats.sort_values(
        by="TotalSpending",
        ascending=False,
    )

    if "Cluster" in sorted_stats.columns:
        cluster_ids = (
            sorted_stats["Cluster"]
            .tolist()
        )
    else:
        cluster_ids = (
            sorted_stats.index
            .tolist()
        )

    names: Dict[int, str] = {}

    if len(cluster_ids) == 3:
        names[int(cluster_ids[0])] = (
            "Premium Customers"
        )

        names[int(cluster_ids[1])] = (
            "Regular Customers"
        )

        names[int(cluster_ids[2])] = (
            "Budget / Deal-Oriented Customers"
        )

    else:
        for position, cluster_id in enumerate(
            cluster_ids
        ):
            cluster_id = int(cluster_id)

            if position == 0:
                names[cluster_id] = (
                    "High Value Customers"
                )

            elif position == len(cluster_ids) - 1:
                names[cluster_id] = (
                    "Budget / Deal-Oriented Customers"
                )

            else:
                names[cluster_id] = (
                    f"Tier {position + 1} Customers"
                )

    return names


# ============================================================
# FEATURE PREPARATION
# ============================================================

def create_features(
    customer: pd.DataFrame,
    reference_year: int,
    reference_date: str,
) -> pd.DataFrame:
    """
    Create the same engineered features used by the
    trained clustering model.
    """

    engineered = engineer_features(
        customer,
        reference_year=reference_year,
        reference_date=reference_date,
    )

    customer_dates = pd.to_datetime(
        engineered["Dt_Customer"],
        errors="coerce",
    )

    if customer_dates.isna().any():
        raise ValueError(
            "Dt_Customer contains invalid or missing dates."
        )

    missing_features = [
        feature
        for feature in SELECTED_FEATURES
        if feature not in engineered.columns
    ]

    if missing_features:
        raise ValueError(
            "Engineered customer data is missing model "
            f"features: {missing_features}"
        )

    return engineered


# ============================================================
# INTERNAL PREPARATION FOR PREDICTION
# ============================================================

def _prepare_features(
    customers: pd.DataFrame,
) -> Tuple[pd.DataFrame, Any, Any, Dict[str, Any]]:
    """
    Validate input, load artifacts, engineer features,
    and create the model input matrix.
    """

    validate_customer_data(
        customers,
        require_id=False,
    )

    preprocessor, model, metadata = (
        load_clustering_artifacts()
    )

    reference_year = int(
        metadata["reference_year"]
    )

    reference_date = str(
        metadata["reference_date"]
    )

    engineered = create_features(
        customer=customers,
        reference_year=reference_year,
        reference_date=reference_date,
    )

    X = engineered[
        SELECTED_FEATURES
    ].copy()

    X_processed = preprocessor.transform(X)

    return (
        X_processed,
        model,
        preprocessor,
        metadata,
    )


# ============================================================
# SINGLE CUSTOMER PREDICTION
# ============================================================

def predict_customer(
    customer: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Assign one customer to a learned segment.

    Returns:
        customer_id
        cluster
        cluster_name
        recommendation
    """

    if len(customer) != 1:
        raise ValueError(
            "predict_customer expects exactly one customer row."
        )

    (
        X_processed,
        model,
        _preprocessor,
        metadata,
    ) = _prepare_features(customer)

    predicted_cluster = int(
        model.predict(X_processed)[0]
    )

    cluster_names = normalize_cluster_names(
        metadata.get("cluster_names", {})
    )

    cluster_name = cluster_names.get(
        predicted_cluster,
        f"Cluster {predicted_cluster}",
    )

    recommendations = metadata.get(
        "recommendations",
        {},
    )

    recommendation = recommendations.get(
        cluster_name,
        "No recommendation available.",
    )

    customer_id = None

    if "ID" in customer.columns:
        value = customer.iloc[0]["ID"]

        if pd.notna(value):
            customer_id = int(value)

    elif "Customer_ID" in customer.columns:
        value = customer.iloc[0]["Customer_ID"]

        if pd.notna(value):
            customer_id = int(value)

    return {
        "customer_id": customer_id,
        "cluster": predicted_cluster,
        "cluster_name": cluster_name,
        "recommendation": str(
            recommendation
        ),
    }


# ============================================================
# BATCH CUSTOMER PREDICTION
# ============================================================

def predict_customers(
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign segments to multiple customers.

    Returns:
        ID | Cluster | Cluster_Name
    """

    validate_customer_data(
        customers,
        require_id=True,
    )

    (
        X_processed,
        model,
        _preprocessor,
        metadata,
    ) = _prepare_features(customers)

    predictions = model.predict(
        X_processed
    )

    clusters = [
        int(cluster)
        for cluster in predictions
    ]

    cluster_names = normalize_cluster_names(
        metadata.get("cluster_names", {})
    )

    cluster_name_results = [
        cluster_names.get(
            cluster,
            f"Cluster {cluster}",
        )
        for cluster in clusters
    ]

    return pd.DataFrame(
        {
            "ID": customers["ID"].astype(int),
            "Cluster": clusters,
            "Cluster_Name": cluster_name_results,
        }
    )


# ============================================================
# COMPATIBILITY WRAPPERS
# ============================================================

def predict_customer_record(
    customer_data: Dict[str, Any] | pd.DataFrame,
) -> Dict[str, Any]:
    """
    Compatibility wrapper for the previous backend interface.
    """

    if isinstance(customer_data, dict):
        customer_df = pd.DataFrame(
            [customer_data]
        )
    else:
        customer_df = customer_data.copy()

    return predict_customer(
        customer_df
    )


def predict_batch_records(
    customers_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compatibility wrapper for the previous backend interface.
    """

    results = predict_customers(
        customers_df
    )

    enriched = customers_df.copy()

    enriched["Cluster"] = results[
        "Cluster"
    ].values

    enriched["Cluster_Name"] = results[
        "Cluster_Name"
    ].values

    return enriched


# ============================================================
# SAVE SEGMENTATION RESULTS
# ============================================================

def save_segmentation_results(
    results: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Save segmentation results to CSV.
    """

    output = Path(
        output_path
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results.to_csv(
        output,
        index=False,
    )

    return output


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    test_path = (
        BASE_DIR
        / "data"
        / "processed"
        / "test_customer_input.csv"
    )

    if test_path.exists():
        test_customer = pd.read_csv(
            test_path
        )

        print(
            predict_customer(
                test_customer
            )
        )

    full_dataset_path = (
        BASE_DIR
        / "data"
        / "processed"
        / "customer_cleaned.csv"
    )

    if full_dataset_path.exists():
        sample = pd.read_csv(
            full_dataset_path
        ).head(10)

        print(
            predict_customers(
                sample
            ).to_string(
                index=False
            )
        )
