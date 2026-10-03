"""
Logistics Domain Validation, Physics Assertion, and Geospatial Gating Module.
Enforces physical plausibility, chronological integrity, geographic bounding boxes,
and non-parametric Tukey's Fences Winsorization.
"""

from typing import Optional
import numpy as np
import pandas as pd


class LogisticsDomainValidator:
    """Enforces logistics domain constraints and spatial/temporal physical laws."""

    def __init__(
        self,
        lat_bounds: tuple[float, float] = (18.40, 18.70),
        lon_bounds: tuple[float, float] = (73.75, 74.00),
        max_transit_hours_floor: float = 0.05,
    ) -> None:
        self.lat_min, self.lat_max = lat_bounds
        self.lon_min, self.lon_max = lon_bounds
        self.min_transit_hours = max_transit_hours_floor

    def validate_geospatial_bounds(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, int]:
        """
        Enforces operational bounding box constraints. Rejects Null Island (0,0),
        swapped coordinates, and out-of-corridor pings.
        """
        valid_lat = (df["dest_latitude"] >= self.lat_min) & (df["dest_latitude"] <= self.lat_max)
        valid_lon = (df["dest_longitude"] >= self.lon_min) & (df["dest_longitude"] <= self.lon_max)
        valid_mask = valid_lat & valid_lon

        violations = int((~valid_mask).sum())
        cleaned_df = df[valid_mask].copy()
        return cleaned_df, violations

    def validate_chronological_sequence(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, int]:
        """
        Detects and filters impossible temporal inversions where delivery precedes dispatch.
        Missing delivery timestamps (MNAR) are preserved as active exceptions/in-transit drops.
        """
        inverted_mask = (
            df["actual_delivery_timestamp"].notna()
            & (df["actual_delivery_timestamp"] < df["dispatch_timestamp"])
        )
        inversions_count = int(inverted_mask.sum())
        valid_df = df[~inverted_mask].copy()
        return valid_df, inversions_count

    def sanitize_physical_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reconciles physical sensor anomalies: sets negative or zero weights to NaN
        to enable downstream robust imputation without corrupting distributions.
        Computes cubic volume (m³) and volumetric density (kg/m³).
        """
        df_out = df.copy()

        # Weight non-positivity check
        df_out.loc[df_out["cargo_weight_kg"] <= 0, "cargo_weight_kg"] = np.nan

        # Package dimensions non-positivity check
        for dim in ["length_cm", "width_cm", "height_cm"]:
            if dim in df_out.columns:
                df_out.loc[df_out[dim] <= 0, dim] = np.nan

        # Calculate volumetric cube in cubic meters (m³)
        df_out["package_volume_m3"] = (
            df_out["length_cm"] * df_out["width_cm"] * df_out["height_cm"]
        ) / 1_000_000.0

        # Density metric (kg / m³)
        df_out["density_kg_m3"] = df_out["cargo_weight_kg"] / (df_out["package_volume_m3"] + 1e-4)

        return df_out

    def assign_operational_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorizes delivery outcomes without target leakage:
        - 'EXCEPTION_OR_IN_TRANSIT': unrecorded POD timestamp (preserves MNAR drops).
        - 'LATE': completed drop breaching committed SLA.
        - 'ON_TIME': completed drop adhering to SLA.
        Computes actual transit duration in hours for completed shipments.
        """
        df_out = df.copy()

        status_conditions = [
            df_out["actual_delivery_timestamp"].isna(),
            df_out["actual_delivery_timestamp"] > df_out["promised_sla_timestamp"],
        ]
        status_choices = ["EXCEPTION_OR_IN_TRANSIT", "LATE"]
        df_out["delivery_status"] = np.select(
            status_conditions, status_choices, default="ON_TIME"
        )

        # Compute transit duration for completed deliveries
        transit_seconds = (
            df_out["actual_delivery_timestamp"] - df_out["dispatch_timestamp"]
        ).dt.total_seconds()
        df_out["actual_transit_hours"] = transit_seconds / 3600.0

        return df_out

    @staticmethod
    def apply_tukey_winsorization(
        series: pd.Series,
        k: float = 1.5,
        lower_floor: Optional[float] = 0.1,
    ) -> pd.Series:
        """
        Applies Tukey's Fences IQR outlier gating. Caps values exceeding upper/lower fences
        (Winsorization) to avoid loss-function collapse while preserving data volume.
        """
        valid_series = series.dropna()
        if len(valid_series) < 10:
            return series

        q25 = valid_series.quantile(0.25)
        q75 = valid_series.quantile(0.75)
        iqr = q75 - q25

        lower_bound = q25 - (k * iqr)
        upper_bound = q75 + (k * iqr)

        if lower_floor is not None:
            lower_bound = max(lower_floor, lower_bound)

        return series.clip(lower=lower_bound, upper=upper_bound)

    def validate_and_filter(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, dict[str, int]]:
        """Executes full domain validation suite and records audit metrics."""
        metrics: dict[str, int] = {"pre_validation_records": len(df)}

        # 1. Geospatial boundary enforcement
        geo_df, geo_violations = self.validate_geospatial_bounds(df)
        metrics["geospatial_violations_dropped"] = geo_violations

        # 2. Chronological sequence check
        chrono_df, inversions = self.validate_chronological_sequence(geo_df)
        metrics["chronological_inversions_dropped"] = inversions

        # 3. Physical metrics validation & volume calculation
        phys_df = self.sanitize_physical_metrics(chrono_df)

        # 4. Operational status assignment
        status_df = self.assign_operational_status(phys_df)

        # 5. Non-parametric outlier winsorization on completed transit durations & distance
        transit_mask = status_df["actual_transit_hours"].notna()
        status_df.loc[transit_mask, "actual_transit_hours"] = self.apply_tukey_winsorization(
            status_df.loc[transit_mask, "actual_transit_hours"], k=1.5, lower_floor=self.min_transit_hours
        )

        status_df["transit_distance_km"] = self.apply_tukey_winsorization(
            status_df["transit_distance_km"], k=1.5, lower_floor=5.0
        )

        metrics["post_validation_records"] = len(status_df)
        return status_df, metrics
