"""
Comprehensive Test Suite for Logistics Data Preprocessing Pipeline.
Validates structural deduplication, chronological inversion gating, geospatial filtering,
cyclical temporal encoding geometry, and ColumnTransformer pipeline invariance.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.sanitization import LogisticsSanitizer
from src.validation import LogisticsDomainValidator
from src.transformers import CyclicalTemporalTransformer
from src.pipeline import ProductionLogisticsPipeline


def test_structural_deduplication():
    df = pd.DataFrame({
        "shipment_id": ["SHP-001", "SHP-002", "SHP-001"],
        "carrier_name": ["FedEx", "DHL", "FedEx"],
        "dispatch_timestamp": ["2026-10-01 08:00:00", "2026-10-01 09:00:00", "2026-10-01 08:00:00"],
    })
    sanitizer = LogisticsSanitizer()
    clean_df, dropped = sanitizer.deduplicate_records(df, "shipment_id")
    assert len(clean_df) == 2
    assert dropped == 1
    assert list(clean_df["shipment_id"]) == ["SHP-001", "SHP-002"]


def test_chronological_inversion_filtering():
    df = pd.DataFrame({
        "shipment_id": ["SHP-001", "SHP-002", "SHP-003"],
        "dispatch_timestamp": pd.to_datetime(["2026-10-01 10:00:00", "2026-10-01 10:00:00", "2026-10-01 10:00:00"]),
        "actual_delivery_timestamp": pd.to_datetime(["2026-10-01 12:00:00", "2026-10-01 09:00:00", None]),
    })
    validator = LogisticsDomainValidator()
    valid_df, inversions = validator.validate_chronological_sequence(df)
    assert inversions == 1
    assert len(valid_df) == 2
    # SHP-002 is dropped (delivery before dispatch)
    assert set(valid_df["shipment_id"]) == {"SHP-001", "SHP-003"}


def test_geospatial_bounds_and_null_island():
    df = pd.DataFrame({
        "shipment_id": ["SHP-01", "SHP-02", "SHP-03", "SHP-04"],
        "dest_latitude": [18.52, 0.0, 18.55, 99.9],
        "dest_longitude": [73.85, 0.0, -190.0, 73.88],
    })
    validator = LogisticsDomainValidator(lat_bounds=(18.40, 18.70), lon_bounds=(73.75, 74.00))
    valid_df, violations = validator.validate_geospatial_bounds(df)
    assert violations == 3
    assert len(valid_df) == 1
    assert valid_df.iloc[0]["shipment_id"] == "SHP-01"


def test_cyclical_temporal_geometry():
    # Test circular continuity between 23:55 and 00:05
    df_times = pd.DataFrame({
        "dispatch_timestamp": [
            pd.Timestamp("2026-10-01 23:55:00"),
            pd.Timestamp("2026-10-02 00:05:00"),
            pd.Timestamp("2026-10-01 12:00:00"),
        ]
    })
    transformer = CyclicalTemporalTransformer(period=24.0, datetime_col=True)
    coords = transformer.fit_transform(df_times)
    
    # coords has shape (3, 2): [sin, cos]
    assert coords.shape == (3, 2)
    # Euclidean distance between 23:55 and 00:05 should be very small
    d_circ = np.linalg.norm(coords[0] - coords[1])
    # Euclidean distance between 00:05 and 12:00 should be ~2.0 (opposite sides of unit circle)
    d_far = np.linalg.norm(coords[1] - coords[2])

    assert d_circ < 0.15
    assert d_far > 1.90


def test_full_pipeline_end_to_end():
    from src.simulation import generate_raw_multimodal_telematics
    raw_df = generate_raw_multimodal_telematics(n_records=100, seed=123)
    
    sanitizer = LogisticsSanitizer()
    sanitized_df, _ = sanitizer.sanitize_dataframe(raw_df)
    
    validator = LogisticsDomainValidator()
    validated_df, _ = validator.validate_and_filter(sanitized_df)
    
    pipeline = ProductionLogisticsPipeline()
    feature_df = pipeline.fit_transform(validated_df)
    
    assert not feature_df.isna().any().any()
    assert feature_df.shape[0] == len(validated_df)
    assert feature_df.shape[1] > 10
    print("All unit and pipeline tests passed successfully!")


if __name__ == "__main__":
    test_structural_deduplication()
    test_chronological_inversion_filtering()
    test_geospatial_bounds_and_null_island()
    test_cyclical_temporal_geometry()
    test_full_pipeline_end_to_end()
