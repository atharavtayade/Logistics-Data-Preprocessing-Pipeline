"""
Custom Scikit-Learn Transformers for Logistics Telematics Feature Engineering.
Implements Cyclical Temporal Encodings (sin/cos), Log1p Variance Stabilization,
and Leakage-Free Tukey's Fences Winsorization.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CyclicalTemporalTransformer(BaseEstimator, TransformerMixin):
    """
    Transforms dispatch timestamps or decimal hour values into continuous
    2-dimensional cyclical components on the unit circle:
        x_sin = sin(2 * pi * t / period)
        x_cos = cos(2 * pi * t / period)
    Preserves seamless topological neighborhood between 23:59 and 00:00.
    """

    def __init__(self, period: float = 24.0, datetime_col: bool = True) -> None:
        self.period = period
        self.datetime_col = datetime_col

    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X)
        transformed_cols = []

        for col in X_df.columns:
            series = X_df[col]
            if self.datetime_col:
                dt_series = pd.to_datetime(series, errors="coerce")
                # Decimal hours: hour + minute / 60.0 + second / 3600.0
                t_vals = dt_series.dt.hour + dt_series.dt.minute / 60.0 + dt_series.dt.second / 3600.0
                # Fallback NaN to median time (12:00)
                t_vals = t_vals.fillna(12.0)
            else:
                t_vals = pd.to_numeric(series, errors="coerce").fillna(12.0)

            radians = 2.0 * np.pi * t_vals / self.period
            sin_feat = np.sin(radians)
            cos_feat = np.cos(radians)

            transformed_cols.extend([sin_feat.to_numpy(), cos_feat.to_numpy()])

        return np.column_stack(transformed_cols)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = ["time_col"]
        names = []
        for feat in input_features:
            names.extend([f"{feat}_sin", f"{feat}_cos"])
        return np.array(names)


class Log1pVarianceStabilizer(BaseEstimator, TransformerMixin):
    """
    Applies natural logarithm log(1 + x) to right-skewed positive features
    (e.g., cargo weight, package volume) to compress heavy tails and normalize residuals.
    """

    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self

    def transform(self, X):
        X_arr = np.asarray(X, dtype=np.float64)
        X_clipped = np.maximum(X_arr, 0.0)
        return np.log1p(X_clipped)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.array([f"log1p_feat_{i}" for i in range(1)])
        return np.array([f"log1p_{f}" for f in input_features])


class TrainFittedTukeyWinsorizer(BaseEstimator, TransformerMixin):
    """
    Scikit-Learn compliant Tukey's Fences outlier clipper.
    Computes Q1, Q3, and IQR exclusively during fit() to eliminate test-set target leakage.
    Clips inference/test values to training bounds.
    """

    def __init__(self, k: float = 1.5, floor_zero: bool = True) -> None:
        self.k = k
        self.floor_zero = floor_zero
        self.lower_bounds_: np.ndarray | None = None
        self.upper_bounds_: np.ndarray | None = None

    def fit(self, X, y=None):
        X_arr = np.asarray(X, dtype=np.float64)
        q25 = np.nanpercentile(X_arr, 25, axis=0)
        q75 = np.nanpercentile(X_arr, 75, axis=0)
        iqr = q75 - q25

        lower = q25 - (self.k * iqr)
        upper = q75 + (self.k * iqr)

        if self.floor_zero:
            lower = np.maximum(lower, 0.0)

        self.lower_bounds_ = lower
        self.upper_bounds_ = upper
        return self

    def transform(self, X):
        if self.lower_bounds_ is None or self.upper_bounds_ is None:
            raise RuntimeError("Transformer has not been fitted.")
        X_arr = np.asarray(X, dtype=np.float64)
        return np.clip(X_arr, self.lower_bounds_, self.upper_bounds_)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.array([f"winsor_{i}" for i in range(1)])
        return np.array(input_features)
