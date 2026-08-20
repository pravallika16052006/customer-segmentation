from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.inference import (
    predict_customer,
    predict_customers,
)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="SegmenAI API",
    description="AI-powered customer segmentation API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Customer Input Schema
# ============================================================

class CustomerInput(BaseModel):
    ID: int | None = None

    Year_Birth: int = Field(
        ...,
        ge=1900,
        le=2020,
    )

    Education: str

    Marital_Status: str

    Income: float = Field(
        ...,
        ge=0,
    )

    Kidhome: int = Field(
        ...,
        ge=0,
    )

    Teenhome: int = Field(
        ...,
        ge=0,
    )

    Dt_Customer: str

    Recency: int = Field(
        ...,
        ge=0,
    )

    MntWines: float = Field(
        ...,
        ge=0,
    )

    MntFruits: float = Field(
        ...,
        ge=0,
    )

    MntMeatProducts: float = Field(
        ...,
        ge=0,
    )

    MntFishProducts: float = Field(
        ...,
        ge=0,
    )

    MntSweetProducts: float = Field(
        ...,
        ge=0,
    )

    MntGoldProds: float = Field(
        ...,
        ge=0,
    )

    NumDealsPurchases: int = Field(
        ...,
        ge=0,
    )

    NumWebPurchases: int = Field(
        ...,
        ge=0,
    )

    NumCatalogPurchases: int = Field(
        ...,
        ge=0,
    )

    NumStorePurchases: int = Field(
        ...,
        ge=0,
    )

    NumWebVisitsMonth: int = Field(
        ...,
        ge=0,
    )

    AcceptedCmp3: int = Field(
        ...,
        ge=0,
        le=1,
    )

    AcceptedCmp4: int = Field(
        ...,
        ge=0,
        le=1,
    )

    AcceptedCmp5: int = Field(
        ...,
        ge=0,
        le=1,
    )

    AcceptedCmp1: int = Field(
        ...,
        ge=0,
        le=1,
    )

    AcceptedCmp2: int = Field(
        ...,
        ge=0,
        le=1,
    )




def _read_uploaded_dataframe(raw_data: bytes, filename: str) -> pd.DataFrame:
    """Read CSV or Excel upload based on its file extension."""
    name = (filename or "").lower()
    if name.endswith(".csv"):
        return pd.read_csv(BytesIO(raw_data))
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(raw_data))
    raise ValueError("Only CSV, XLSX, and XLS files are supported.")

# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "SegmenAI API",
        "status": "running",
    }


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "segmenai-api",
    }


# ============================================================
# Dataset Preview Endpoint
# ============================================================

@app.post("/api/v1/dataset/preview")
async def preview_dataset(
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """
    Inspect an uploaded CSV before ML processing.
    This endpoint does not train a model.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV, XLSX, and XLS files are supported.",
        )

    raw_data = await file.read()

    if not raw_data:
        raise HTTPException(
            status_code=400,
            detail="The uploaded CSV is empty.",
        )

    max_size = 20 * 1024 * 1024

    if len(raw_data) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum size is 20 MB.",
        )

    try:
        df = _read_uploaded_dataframe(raw_data, file.filename)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read CSV: {str(exc)}",
        ) from exc

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="The CSV contains no data rows.",
        )

    column_profiles = []

    for column in df.columns:
        column_profiles.append(
            {
                "name": str(column),
                "dtype": str(df[column].dtype),
                "missing": int(
                    df[column].isna().sum()
                ),
                "unique": int(
                    df[column].nunique(
                        dropna=True
                    )
                ),
            }
        )

    numerical_columns = [
        str(column)
        for column in df.select_dtypes(
            include="number"
        ).columns
    ]

    categorical_columns = [
        str(column)
        for column in df.select_dtypes(
            include=[
                "object",
                "category",
                "bool",
            ]
        ).columns
    ]

    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "missing_cells": int(
            df.isna().sum().sum()
        ),
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns,
        "columns": column_profiles,
    }


# ============================================================
# Single Customer Segmentation
# ============================================================

@app.post("/api/v1/segment")
def segment_customer(
    customer: CustomerInput,
) -> dict[str, Any]:
    """
    Assign one customer to a learned customer segment.
    """

    try:
        customer_dict = customer.model_dump()

        customer_df = pd.DataFrame(
            [customer_dict]
        )

        result = predict_customer(
            customer_df
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Segmentation failed: {str(exc)}",
        ) from exc


# ============================================================
# Batch CSV Segmentation
# ============================================================

@app.post("/api/v1/segment/file")
async def segment_file(
    file: UploadFile = File(...),
) -> StreamingResponse:
    """
    Segment all customers in an uploaded CSV.

    Returns a CSV containing:
    ID, Cluster, Cluster_Name
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV, XLSX, and XLS files are supported.",
        )

    raw_data = await file.read()

    if not raw_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV is empty.",
        )

    max_size = 20 * 1024 * 1024

    if len(raw_data) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum size is 20 MB.",
        )

    try:
        customers = _read_uploaded_dataframe(raw_data, file.filename)

        results = predict_customers(
            customers
        )

        output = BytesIO()

        results.to_csv(
            output,
            index=False,
        )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    'attachment; filename="customer_segments.csv"'
                )
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Batch segmentation failed: {str(exc)}",
        ) from exc