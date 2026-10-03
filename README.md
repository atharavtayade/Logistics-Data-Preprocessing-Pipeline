# Logistics Data Ingestion, Cleaning & Preprocessing Pipeline
> **Enterprise Telematics Sanitization, Robust Outlier Remediation, and Scaled Feature Engineering for Supply Chain Analytics**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-3.0.6-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.1-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.26%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

## Executive Summary

Modern supply chains depend heavily on predictive machine learning for estimated time of arrival (ETA) forecasting, fleet capacity optimization, dynamic pricing, and carrier service-level agreement (SLA) verification. However, multi-source telematics ingested across Warehouse Management Systems (WMS), Transportation Management Systems (TMS), vehicle CAN-bus diagnostics, and mobile Proof-of-Delivery (POD) handoffs suffer from acute data quality challenges:

* **Structural Redundancy:** Network retries generate duplicate consignment events.
* **Sensor Drift & Calibration Errors:** Load-cell scales output zero or negative tare deadweights.
* **Temporal Inversions:** Device clock drifts record package drop-offs prior to hub dock departure.
* **Geospatial Drift:** Coordinate transpositions and uncalibrated GPS units resolve to `(0.0, 0.0)` ("Null Island").
* **Extreme Distributional Skew:** High-magnitude distance and freight expenses dominate narrow operational integer metrics.

This repository implements a production-grade, leak-free preprocessing pipeline designed around **Python 3.10+, Pandas, and Scikit-Learn** (`ColumnTransformer`, `RobustScaler`, `SimpleImputer`). The architecture is empirically benchmarked against the **Olist Brazilian E-Commerce Dataset** and the **DataCo Global Smart Supply Chain Dataset**.

---

## System Architecture

+----------------------------------------------------------------------------------------------------+
|                                 MULTI-TIER ENTERPRISE INGESTION LAYER                              |
+-----------------------------------+--------------------------------+-------------------------------+
| Tier 1: ERP / Checkout            | Tier 2: WMS & Conveyor Scales  | Tier 3: Edge CAN-bus & POD    |
| - Order ID & Consignment Items    | - Gross Deadweight (g / kg)    | - Geodetic Lat/Lon Pings      |
| - Committed Delivery SLAs         | - Packaging Dimensions (L,W,H) | - Instantaneous Velocity      |
| - Destination Geocodes            | - Yard Cross-Dock Scans        | - Mobile Electronic POD Stamp |
+-----------------+-----------------+----------------+---------------+---------------+---------------+
|                                  |                               |
+----------------------------------+-------------------------------+
|
v
+------------------------------------+
|    Streaming Ingestion Broker      |
| (Apache Kafka / AWS Kinesis / MQTT)|
+------------------+-----------------+
|
v
+------------------------------------+
|      Raw Telematics Lakehouse      |
|   (Bronze Delta Lake / MinIO S3)   |
+------------------+-----------------+
|
v
+----------------------------------------------------------------+
|           ENTERPRISE DATA PREPROCESSING PIPELINE ENGINE        |
+----------------------------------------------------------------+
|  1. Structural Deduplication & Schema Sanitization             |
|  2. Bounding Polygon & Coordinate Transposition Filtering      |
|  3. Physical Boundary Assertion & Status Partitioning Gating  |
|  4. Scikit-Learn ColumnTransformer Pipeline Execution          |
+--------------------------------+-------------------------------+
|
v
+------------------------------------+
|      Clean Analytics Feature Store |
|       (Silver / Gold Layer)        |
+------------------+-----------------+
|
+-------------------------------------------+-----------------------------------------+
|                                           |                                         |
v                                           v                                         v
+-------------------------------+   +-------------------------------+   +-------------------------------+
| ETA Prediction Engine         |   | Dynamic Fleet Routing         |   | Carrier SLA Performance Audit |
| (Gradient Boosted Regressors) |   | (Linear & Integer Programming)|   | (Contract Cost Reconciliation)|
+-------------------------------+   +-------------------------------+   +-------------------------------+

## Mathematical Formulations & Remediation Logic

### 1. Tukey’s Fences & Winsorization
Rather than purging transit durations—which discards critical operational evidence of transit gridlock or severe weather—non-parametric quantile boundaries are applied:

$$\text{IQR} = Q_3 - Q_1$$

$$\text{Lower Limit} = \max(\text{Floor}_{\text{physical}}, Q_1 - 1.5 \times \text{IQR})$$

$$\text{Upper Limit} = Q_3 + 1.5 \times \text{IQR}$$

Values exceeding the upper threshold are capped (Winsorized) to eliminate gradient explosion in downstream models while preserving sample volume.

### 2. Cyclical Trigonometric Temporal Encodings ($S^1$ Unit Circle)
Dispatch hours ($t \in [0, 24)$) are projected onto a continuous 2D trigonometric circle. This guarantees that the temporal distance between $23:59$ and $00:01$ is infinitesimal rather than an artificial 23.96-hour jump:

$$x_{\sin} = \sin\left(\frac{2\pi \cdot t}{24}\right), \quad x_{\cos} = \cos\left(\frac{2\pi \cdot t}{24}\right)$$

$$D(\mathbf{u}_1, \mathbf{u}_2) = 2\left\vert{}\sin\left(\frac{\pi(t_1 - t_2)}{24}\right)\right\vert{}$$

### 3. Distributional Scaling: RobustScaler Justification
Standard scaling mechanisms exhibit critical structural vulnerabilities when applied to freight distributions:

* **MinMaxScaler:** Sensitive to extreme outliers ($\text{Breakdown Point } \epsilon^* = 0\%$). An extreme 25,000 kg shipment compresses normal parcel volumes ($0.5 - 15\text{ kg}$) into a near-zero decimal range ($0.0001 - 0.0006$).
* **StandardScaler:** Relies on the sample mean and variance ($\text{Breakdown Point } \epsilon^* = 0\%$). High positive freight skew inflates variance, compressing standard distribution spreads.
* **RobustScaler:**
  
  $$X_{\text{robust}} = \frac{X - \text{median}}{\text{IQR}}$$

  With a breakdown point $\epsilon^* \in [25\%, 50\%]$, `RobustScaler` scales based on the middle 50% of the distribution. It standardizes normal parcel volumes without loss-function collapse from heavy industrial consignments.

### 4. Target Leakage Prevention
Unrecorded `actual_delivery_timestamp` fields are categorized as Missing Not At Random (MNAR). Imputing artificial arrival times synthesizes false ground-truth labels[cite: 2]. The pipeline tags these records as `EXCEPTION_OR_IN_TRANSIT`, isolating them from the supervised training dataset[cite: 2].

---

## Repository Structure

Logistics-Data-Preprocessing-Pipeline/
├── README.md                                       # Architectural documentation & quickstart
├── TECHNICAL_PREPROCESSING_REPORT.md               # Full 7-section engineering report
├── generate_docx_report.py                         # Automated Word (.docx) document generator
├── Task_2_Logistics_Data_Preprocessing_Report.docx # Formatted executive deliverable
├── data/
│   ├── simulated_raw_logistics.csv                 # 2,000 raw records with injected defects
│   ├── cleaned_logistics_data.csv                  # Validated operational data post-gating
│   └── processed_feature_matrix.csv                # Scaled, encoded ML feature matrix (31 features)
├── src/
│   ├── init.py                                 # Package initializers
│   ├── simulation.py                               # Multi-tier data generator (MCAR, MAR, MNAR)
│   ├── sanitization.py                             # Deduplication & schema coercion
│   ├── validation.py                               # Spatial bounding, physics & temporal validator
│   ├── transformers.py                             # Cyclical temporal, Log1p, and Tukey transformers
│   ├── pipeline.py                                 # Scikit-Learn ColumnTransformer pipeline
│   └── run_pipeline.py                             # End-to-end execution script
└── tests/
└── test_pipeline.py                            # Test suite (invariance, geometry, bounds)

---

## Quickstart & Installation

### 1. Clone the Repository & Configure Dependencies
```bash
git clone [https://github.com/atharavtayade/Logistics-Data-Preprocessing-Pipeline.git](https://github.com/atharavtayade/Logistics-Data-Preprocessing-Pipeline.git)
cd Logistics-Data-Preprocessing-Pipeline
pip install pandas numpy scikit-learn python-docx
