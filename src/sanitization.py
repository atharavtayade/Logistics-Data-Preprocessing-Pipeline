"""
Logistics Data Sanitization and Structural Cleaning Module.
Standardizes noisy raw schemas, dedupes transmission keys, normalizes string categories,
strips currency formatting, and coerces heterogeneous datetimes to UTC.
"""

import re
from typing import Any
import numpy as np
import pandas as pd


class LogisticsSanitizer:
    """Production-grade structural sanitization engine for supply chain data."""

    def __init__(self) -> None:
        self.carrier_mapping: dict[str, str] = {
            "fedex freight": "FedEx Freight",
            "fedex": "FedEx Freight",
            "dhl express": "DHL Express",
            "dhl": "DHL Express",
            "ups ground": "UPS Ground",
            "ups_ground": "UPS Ground",
            "ups": "UPS Ground",
            "bluedart logistics": "BlueDart Logistics",
            "bluedart": "BlueDart Logistics",
        }

    def deduplicate_records(
        self, df: pd.DataFrame, primary_key: str = "shipment_id"
    ) -> tuple[pd.DataFrame, int]:
        """
        Removes redundant transmissions preserving the initial arrival instance.
        """
        initial_len = len(df)
        deduped_df = df.drop_duplicates(subset=[primary_key], keep="first").copy()
        dropped_count = initial_len - len(deduped_df)
        return deduped_df, dropped_count

    def clean_carrier_names(self, series: pd.Series) -> pd.Series:
        """
        Standardizes carrier strings, stripping whitespaces, lowercasing for lookup,
        and mapping known carrier synonyms to clean taxonomy.
        """
        def _standardize_name(val: Any) -> Any:
            if pd.isna(val):
                return "Unknown Carrier"
            s = str(val).strip()
            if s.upper() in ["NONE", "NAN", "NULL", "UNKNOWN", ""]:
                return "Unknown Carrier"
            norm_key = re.sub(r"[\s_]+", " ", s).lower()
            return self.carrier_mapping.get(norm_key, s.title())

        return series.apply(_standardize_name)

    def parse_currency_to_float(self, series: pd.Series) -> pd.Series:
        """
        Coerces formatted currency strings (e.g., '$1,245.50', '54.20 USD')
        into clean 64-bit IEEE floating point representations.
        """
        def _clean_currency(val: Any) -> float:
            if pd.isna(val):
                return np.nan
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip()
            # Remove currency symbols, commas, and trailing currency ISO codes
            s_clean = re.sub(r"[^\d.-]", "", s)
            try:
                val_float = float(s_clean)
                return val_float if val_float >= 0 else np.nan
            except ValueError:
                return np.nan

        return series.apply(_clean_currency)

    def parse_datetimes(
        self, df: pd.DataFrame, datetime_columns: list[str]
    ) -> pd.DataFrame:
        """
        Coerces multi-format date strings into ISO-8601 compliant pd.Timestamp objects.
        Unparseable strings are coerced to pd.NaT.
        """
        df_out = df.copy()
        for col in datetime_columns:
            if col in df_out.columns:
                df_out[col] = pd.to_datetime(df_out[col], errors="coerce")
        return df_out

    def sanitize_dataframe(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, dict[str, int]]:
        """
        Executes end-to-end structural sanitization on raw logistics dataframe.
        """
        metrics: dict[str, int] = {"raw_records": len(df)}

        # 1. Deduplication
        cleaned_df, dup_dropped = self.deduplicate_records(df, "shipment_id")
        metrics["duplicate_keys_dropped"] = dup_dropped

        # 2. String standardization
        cleaned_df["carrier_name"] = self.clean_carrier_names(cleaned_df["carrier_name"])
        for cat_col in ["origin_hub", "destination_zone", "vehicle_type"]:
            if cat_col in cleaned_df.columns:
                cleaned_df[cat_col] = (
                    cleaned_df[cat_col]
                    .astype(str)
                    .str.strip()
                    .replace({"None": np.nan, "nan": np.nan, "NaN": np.nan, "": np.nan})
                )

        # 3. Currency parsing
        cleaned_df["freight_cost_usd"] = self.parse_currency_to_float(cleaned_df["freight_cost_usd"])

        # 4. Datetime parsing
        time_cols = ["dispatch_timestamp", "promised_sla_timestamp", "actual_delivery_timestamp"]
        cleaned_df = self.parse_datetimes(cleaned_df, time_cols)

        # Drop records lacking primary dispatch timestamp (cannot calculate baseline transit)
        valid_dispatch = cleaned_df["dispatch_timestamp"].notna()
        metrics["missing_dispatch_dropped"] = int((~valid_dispatch).sum())
        cleaned_df = cleaned_df[valid_dispatch].copy()

        metrics["sanitized_records"] = len(cleaned_df)
        return cleaned_df, metrics
