"""
SegMen Backend Package
Modular data loading, clustering inference, statistical analysis, and recommendation engines.
"""

from backend.data_loader import (
    load_unified_data,
    get_active_data,
    set_active_data,
    clear_active_data,
    load_cluster_profiles,
    get_dataset_summary,
)
from backend.inference import (
    load_clustering_artifacts,
    predict_customer_record,
    predict_batch_records,
    get_dynamic_cluster_names,
)
from backend.analysis import (
    calculate_cluster_statistics,
    generate_business_insights,
    generate_segment_narrative,
    get_distribution_data,
    get_category_spending_breakdown,
    get_channel_breakdown,
    get_radar_chart_data,
)
from backend.recommendations import (
    get_segment_recommendations,
    get_customer_recommendation,
)

__all__ = [
    "load_unified_data",
    "get_active_data",
    "set_active_data",
    "clear_active_data",
    "load_cluster_profiles",
    "get_dataset_summary",
    "load_clustering_artifacts",
    "predict_customer_record",
    "predict_batch_records",
    "get_dynamic_cluster_names",
    "calculate_cluster_statistics",
    "generate_business_insights",
    "generate_segment_narrative",
    "get_distribution_data",
    "get_category_spending_breakdown",
    "get_channel_breakdown",
    "get_radar_chart_data",
    "get_segment_recommendations",
    "get_customer_recommendation",
]
