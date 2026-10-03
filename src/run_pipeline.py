"""
End-to-End Orchestrator for Logistics Data Preprocessing Pipeline.
Executes raw simulation, structural sanitization, domain validation,
and Scikit-Learn feature engineering pipeline. Exports artifacts and prints audit metrics.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add parent directory to path to allow relative imports if run as script
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from src.simulation import generate_raw_multimodal_telematics
from src.sanitization import LogisticsSanitizer
from src.validation import LogisticsDomainValidator
from src.pipeline import ProductionLogisticsPipeline


def execute_full_pipeline(
    n_samples: int = 2000,
    seed: int = 42,
    output_dir: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """
    Executes the comprehensive production preprocessing pipeline.
    """
    if output_dir is None:
        output_dir = parent_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("LOGISTICS DATA PREPROCESSING PIPELINE: PRODUCTION INGESTION RUN")
    print(f"Author: Logistics Data Analyst Intern & Supply Chain Systems Engineer")
    print(f"Target Scope: Multimodal Freight & Urban Last-Mile Telematics")
    print("=" * 80)

    # ---------------------------------------------------------
    # STAGE 1: RAW INGESTION SIMULATION
    # ---------------------------------------------------------
    print("\n[STAGE 1/4] Simulating multi-tier enterprise telematics stream...")
    raw_df = generate_raw_multimodal_telematics(n_records=n_samples, seed=seed)
    raw_csv_path = output_dir / "simulated_raw_logistics.csv"
    raw_df.to_csv(raw_csv_path, index=False)
    print(f" -> Generated {len(raw_df):,} raw records with injected domain defects.")
    print(f" -> Raw dataset archived to: {raw_csv_path.name}")

    # ---------------------------------------------------------
    # STAGE 2: STRUCTURAL SANITIZATION & SCHEMA COERCION
    # ---------------------------------------------------------
    print("\n[STAGE 2/4] Executing structural deduplication and schema normalization...")
    sanitizer = LogisticsSanitizer()
    sanitized_df, sanitization_metrics = sanitizer.sanitize_dataframe(raw_df)
    print(f" -> Duplicates dropped: {sanitization_metrics['duplicate_keys_dropped']}")
    print(f" -> Invalid dispatch timestamps dropped: {sanitization_metrics['missing_dispatch_dropped']}")
    print(f" -> Sanitized records retained: {sanitization_metrics['sanitized_records']:,}")

    # ---------------------------------------------------------
    # STAGE 3: DOMAIN VALIDATION & PHYSICAL GATING
    # ---------------------------------------------------------
    print("\n[STAGE 3/4] Enforcing geospatial bounding, physics laws, and chronological validity...")
    validator = LogisticsDomainValidator()
    validated_df, validation_metrics = validator.validate_and_filter(sanitized_df)
    print(f" -> Geospatial violations (Null Island / Swapped / OOB) dropped: {validation_metrics['geospatial_violations_dropped']}")
    print(f" -> Chronological inversions (Delivery < Dispatch) dropped: {validation_metrics['chronological_inversions_dropped']}")
    print(f" -> Validated records retained: {validation_metrics['post_validation_records']:,}")

    # Save cleaned operational dataset
    cleaned_csv_path = output_dir / "cleaned_logistics_data.csv"
    validated_df.to_csv(cleaned_csv_path, index=False)
    print(f" -> Cleaned operational dataset exported to: {cleaned_csv_path.name}")

    # Operational status breakdown
    status_counts = validated_df["delivery_status"].value_counts().to_dict()
    print(f" -> Delivery Status Distribution (Target Leakage Prevented):")
    for status, count in status_counts.items():
        pct = (count / len(validated_df)) * 100
        print(f"     * {status}: {count:,} ({pct:.1f}%)")

    # ---------------------------------------------------------
    # STAGE 4: SCIKIT-LEARN COLUMNTRANSFORMER PIPELINE
    # ---------------------------------------------------------
    print("\n[STAGE 4/4] Fitting Scikit-Learn ColumnTransformer feature pipeline...")
    ml_pipeline = ProductionLogisticsPipeline()
    feature_matrix = ml_pipeline.fit_transform(validated_df)
    
    matrix_csv_path = output_dir / "processed_feature_matrix.csv"
    feature_matrix.to_csv(matrix_csv_path, index=False)
    print(f" -> Feature Matrix created with shape: {feature_matrix.shape}")
    print(f" -> Cleaned ML feature store exported to: {matrix_csv_path.name}")

    # Calculate audit metrics
    raw_weight_skew = raw_df["cargo_weight_kg"].dropna().skew()
    clean_weight_skew = validated_df["cargo_weight_kg"].dropna().skew()
    processed_weight_skew = feature_matrix["log_robust_cargo_weight_kg"].skew()

    audit_summary = {
        "raw_records": len(raw_df),
        "duplicates_removed": sanitization_metrics["duplicate_keys_dropped"],
        "geo_violations_removed": validation_metrics["geospatial_violations_dropped"],
        "temporal_inversions_removed": validation_metrics["chronological_inversions_dropped"],
        "validated_records": len(validated_df),
        "ml_feature_count": feature_matrix.shape[1],
        "raw_weight_skewness": raw_weight_skew,
        "clean_weight_skewness": clean_weight_skew,
        "log_transformed_weight_skewness": processed_weight_skew,
        "status_distribution": status_counts,
    }

    print("\n" + "=" * 80)
    print("PREPROCESSING AUDIT SUMMARY & STATISTICAL HEALTH REPORT")
    print("=" * 80)
    print(f"1. Ingestion Yield: {audit_summary['validated_records']:,} / {audit_summary['raw_records']:,} records ({audit_summary['validated_records']/audit_summary['raw_records']*100:.2f}% retained)")
    print(f"2. Payload Weight Skewness Stabilization:")
    print(f"   - Raw Ingestion Skewness:      {raw_weight_skew:.4f} (Severe Heavy-Tail Skew)")
    print(f"   - Cleaned Post-Gating Skew:    {clean_weight_skew:.4f}")
    print(f"   - Log1p Transformed Skew:     {processed_weight_skew:.4f} (Variance Stabilized)")
    print(f"3. Feature Matrix Dimensions:     {feature_matrix.shape[0]:,} samples x {feature_matrix.shape[1]} features")
    print("=" * 80)

    return raw_df, validated_df, feature_matrix, audit_summary


if __name__ == "__main__":
    execute_full_pipeline()
