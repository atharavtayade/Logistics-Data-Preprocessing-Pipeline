"""
Production Scikit-Learn ColumnTransformer Preprocessing Pipeline.
Integrates median continuous imputation, categorical encoding, cyclical temporal transformations,
log-variance stabilization, and RobustScaler for heavy-tailed logistics distributions.
"""

from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

from .transformers import (
    CyclicalTemporalTransformer,
    Log1pVarianceStabilizer,
    TrainFittedTukeyWinsorizer,
)


def build_logistics_feature_pipeline() -> ColumnTransformer:
    """
    Constructs an industrial Scikit-Learn ColumnTransformer pipeline.

    Architectural Pipelines:
    1. Skewed Physicals (cargo_weight_kg, package_volume_m3):
       Median Imputer -> Log1p Transform -> RobustScaler
    2. Linear Spatial/Financial (transit_distance_km, freight_cost_usd):
       Median Imputer -> Tukey's Winsorizer -> RobustScaler
    3. Operational SLA (scheduled_days):
       Median Imputer -> RobustScaler
    4. Temporal Dispatch Cycle (dispatch_timestamp):
       Cyclical Trigonometric (sin/cos) 24h Transformation
    5. Categorical Master Attributes (carrier_name, origin_hub, destination_zone, vehicle_type):
       Constant 'UNKNOWN' Imputer -> One-Hot Encoding (drop='first', handle_unknown='ignore')
    """
    # 1. Skewed physical features
    skewed_features = ["cargo_weight_kg", "package_volume_m3"]
    skewed_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("log1p", Log1pVarianceStabilizer()),
            ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
        ]
    )

    # 2. Linear continuous features
    linear_features = ["transit_distance_km", "freight_cost_usd"]
    linear_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("winsorizer", TrainFittedTukeyWinsorizer(k=1.5, floor_zero=True)),
            ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
        ]
    )

    # 3. Integer operational SLA
    sla_features = ["scheduled_days"]
    sla_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
        ]
    )

    # 4. Temporal cycle feature
    temporal_features = ["dispatch_timestamp"]
    temporal_pipeline = Pipeline(
        steps=[
            ("cyclical", CyclicalTemporalTransformer(period=24.0, datetime_col=True)),
        ]
    )

    # 5. Categorical features
    categorical_features = ["carrier_name", "origin_hub", "destination_zone", "vehicle_type"]
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="UNKNOWN")),
            ("encoder", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")),
        ]
    )

    # Assemble ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("skewed_phys", skewed_pipeline, skewed_features),
            ("linear_cont", linear_pipeline, linear_features),
            ("sla_order", sla_pipeline, sla_features),
            ("temporal", temporal_pipeline, temporal_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    return preprocessor


class ProductionLogisticsPipeline:
    """End-to-end wrapper providing DataFrame preservation and audit reporting."""

    def __init__(self) -> None:
        self.column_transformer = build_logistics_feature_pipeline()
        self.is_fitted = False
        self.feature_names_: list[str] = []

    def fit(self, df: pd.DataFrame) -> "ProductionLogisticsPipeline":
        self.column_transformer.fit(df)
        self.is_fitted = True
        self.feature_names_ = self._extract_feature_names()
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted prior to transform.")
        transformed_matrix = self.column_transformer.transform(df)
        transformed_df = pd.DataFrame(
            transformed_matrix,
            columns=self.feature_names_,
            index=df.index,
        )
        return transformed_df

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)

    def _extract_feature_names(self) -> list[str]:
        """Extracts readable feature names from the underlying ColumnTransformer."""
        names: list[str] = []
        for name, trans, cols in self.column_transformer.transformers_:
            if name == "remainder" or trans == "drop":
                continue
            if name == "skewed_phys":
                names.extend([f"log_robust_{c}" for c in cols])
            elif name == "linear_cont":
                names.extend([f"winsor_robust_{c}" for c in cols])
            elif name == "sla_order":
                names.extend([f"robust_{c}" for c in cols])
            elif name == "temporal":
                names.extend(["dispatch_hour_sin", "dispatch_hour_cos"])
            elif name == "categorical":
                ohe_encoder = trans.named_steps["encoder"]
                cat_names = ohe_encoder.get_feature_names_out(cols).tolist()
                names.extend(cat_names)
            else:
                names.extend(cols)
        return names
