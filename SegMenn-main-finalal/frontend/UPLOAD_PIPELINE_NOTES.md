# Upload-driven dashboard

The application no longer loads the bundled customer dataset at startup.

1. Open Dashboard.
2. Choose a folder containing CSV customer data.
3. Click **Process Uploaded Data**.
4. The backend validates the required schema, engineers the same model features, applies the saved preprocessor and trained clustering model, and attaches cluster labels.
5. The processed dataset is stored in the current Streamlit session and powers all dashboard pages.
6. Use **Download Processed Segmentation CSV** to export the exact data used by the dashboard.

The trained model artifacts remain in `models/`; the sample customer data files were removed from the delivered project so there is no automatic dataset injection.
