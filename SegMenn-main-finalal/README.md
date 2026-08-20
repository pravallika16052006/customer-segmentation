# SegMen: Customer Segmentation & Insights Dashboard

SegMen is a machine learning driven customer segmentation and actionable recommendation web application. Built for marketing strategists and product teams, SegMen turns complex behavioural, demographic, and transactional customer data into distinct clusters and automated growth playbooks.

---

## Key Features

- **Executive Dashboard**:
  - Live KPI cards tracking customer volume, active clusters, highest-value segment, average customer spending, and purchase frequency.
  - Interactive distribution donut chart and grouped cluster benchmark comparisons.
  - 2D customer segmentation scatter plot (Income vs. Total Spending).
  - Automated business takeaways generated directly from actual dataset percentiles.
  - Interactive multi-dimensional filters (Segments, Income range, Spending range, Recency).

- **Customer Segments**:
  - Deep statistical breakdown for each learned cluster (**Premium Customers**, **Regular Customers**, **Budget / Deal-Oriented Customers**).
  - Dynamic KPI cards detailing count, share, average spending, annual income, order frequency, and recency.
  - Interactive customer database explorer with filtering, ID search, and CSV export.

- **Segment Analysis**:
  - Segment-by-segment deep dive with an interactive dropdown selector.
  - Dynamic narrative segment profile describing each group's behavioral identity.
  - Behavioral histograms for Income and Spending distributions.
  - Product category expenditure breakdown (Wines, Meat, Gold, Fish, Fruits, Sweets).
  - Purchase channel breakdown (In-Store, Web Orders, Catalog, Deals).
  - Multi-dimensional 360° Radar Chart benchmark comparing clusters across standardized dimensions.

- **Strategic Recommendations & Customer-Level Search**:
  - **Segment → Characteristics → Strategy → Expected Goal** frameworks with concrete action items.
  - **Customer Intelligence Lookup**: Instant search by Customer ID returning cluster badge, demographic attributes, benchmark comparison vs. segment mean, and personalized next-best actions.

---

## Tech Stack & Architecture

- **Frontend**: Streamlit, Plotly, Custom Vanilla CSS & Responsive SVGs.
- **Backend & ML**: Python, Pandas, NumPy, Scikit-learn, Joblib.
- **API Layer**: FastAPI (with Uvicorn).

```text
SegemAI/
│
├── app.py                      # Root Streamlit app entrypoint
│
├── backend/                    # Core Backend Logic Layer
│   ├── __init__.py
│   ├── data_loader.py          # Cached data loading, merging, validation, error handling
│   ├── segmentation.py         # Model loading, single & batch inference, dynamic cluster naming
│   ├── analysis.py             # Metrics calculation, distributions, radar charts, dynamic insights
│   └── recommendations.py      # Segment & customer-level business recommendations engine
│
├── frontend/                   # UI & Visualization Layer
│   ├── streamlit_app.py        # Multipage navigation shell
│   ├── theme.py                # Visual design system (tokens, custom styles, Plotly theme)
│   ├── assets/
│   │   └── logo.png            # SegMen branding logo
│   └── pages/
│       ├── home.py             # Page 1: ⌂ Dashboard
│       ├── customer_segmentation.py # Page 2: ◉ Customer Segments
│       ├── insights.py         # Page 3: ◫ Segment Analysis
│       └── recommendations.py  # Page 4: ✦ Recommendations & Customer Lookup
│
├── app/
│   └── app.py                  # FastAPI REST API
│
├── models/
│   ├── clustering_model.pkl    # Trained KMeans model (k=3)
│   ├── preprocessor.pkl        # Scaler & transformer pipeline
│   └── model_metadata.json     # Reference dates, cluster mappings, base strategies
│
├── data/
│   └── processed/
│       ├── customer_cleaned.csv    # 49,997 processed customer records
│       ├── customer_segments.csv   # Customer ID to Cluster assignments
│       └── cluster_profiles.csv    # Cluster benchmark summary
│
├── requirements.txt            # Project dependencies
└── README.md                   # Documentation
```

---

## Quick Start & Running Locally

### 1. Activate Environment & Install Dependencies

```powershell
# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Launch the SegMen Dashboard

Run the Streamlit application directly from the root directory:

```powershell
python -m streamlit run app.py
```

*Or via the frontend folder:*

```powershell
streamlit run frontend/streamlit_app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

### 3. Optional: Run the FastAPI Backend Server

If you wish to run the separate REST API for external client integration:

```powershell
uvicorn app.app:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API documentation will be accessible at `http://127.0.0.1:8000/docs`.

---

## Cluster Overview

| Cluster ID | Segment Name | Customer Count | Share (%) | Avg Spending | Avg Income | Primary Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | **Premium Customers** | 5,537 | 11.1% | $1,578.39 | $79,735 | VIP Concierge, Luxury Bundles, Loyalty Perks |
| **1** | **Budget / Deal-Oriented** | 26,683 | 53.4% | $152.61 | $36,628 | Flash Sales, Essential Bundles, Win-Back Deals |
| **2** | **Regular Customers** | 17,777 | 35.6% | $993.70 | $66,400 | Cross-Selling, Basket Expansion, Double Points |

---

## License

MIT License. SegMen &copy; 2026.

## Application entry points

- `app.py` — Streamlit frontend/dashboard. Run with `python -m streamlit run app.py`.
- `app/api.py` — FastAPI backend. Run with `python -m uvicorn app.api:app --reload --port 8000`. The old duplicate `app/app.py` entry point has been renamed to `app/api.py` to remove ambiguity.
- Dashboard uploads accept one or more CSV, XLSX, or XLS files. Folder upload is not used.
