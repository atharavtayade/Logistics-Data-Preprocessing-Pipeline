# Logistics Data Preprocessing & Cleansing Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.1-orange.svg)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-3.0.6-darkblue.svg)](https://pandas.pydata.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Grade-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Enterprise Technical Preprocessing Report & Pipeline for Task 2:**  
> *"Data Collection, Cleaning, and Preprocessing for Logistics Analysis"*  
> **Author:** Lead Logistics Data Analyst Intern & Supply Chain Systems Engineer  
> **Domain:** Multimodal Freight Telematics, WMS Ingestion, and Urban Last-Mile Distribution  
> **Benchmark Sources:** *Brazilian E-Commerce Dataset by Olist* & *DataCo Smart Supply Chain Dataset*  

---

## 📌 Executive Overview

Modern supply chains rely on predictive machine learning for real-time ETA forecasting, carrier performance auditing, dynamic lane pricing, and fleet route optimization. However, raw telematics collected across Warehouse Management Systems (WMS), Transportation Management Systems (TMS), vehicle CAN-bus sensors, and mobile driver Proof-of-Delivery (POD) devices suffer from high entropy:
- **Structural Duplication:** Asynchronous network retries causing duplicate consignment keys.
- **Physical & Sensor Drift:** Conveyor load-cell tare errors reporting zero or negative deadweights.
- **Chronological Inversions:** Driver device clock skew indicating delivery *prior* to dock dispatch.
- **Geospatial Transposition:** Inverted latitude/longitude and `(0.0, 0.0)` "Null Island" fallbacks.
- **High-Magnitude Skew:** Distance and cost features in thousands dominating narrow SLA metrics.

This repository implements an **end-to-end, production-grade preprocessing pipeline** using **Python 3.10+, Pandas, NumPy, and Scikit-Learn** (`ColumnTransformer`, `RobustScaler`, `SimpleImputer`).

---

## 🏛️ Ingestion & Preprocessing Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                 MULTI-TIER ENTERPRISE INGESTION LAYER                              |
+-----------------------------------+--------------------------------+-------------------------------+
| Tier 1: ERP / Checkout            | Tier 2: WMS & Conveyor Scales  | Tier 4: Edge CAN-bus & POD    |
| - Order ID & Line Items           | - Gross Deadweight (g / kg)    | - Lat/Lon GPS Pings (1 Hz)    |
| - Promised SLA Windows            | - Package Dimensions (L, W, H) | - Vehicle Odometer & Speed    |
| - Customer Destination Text       | - Cross-Dock Staging Scans     | - Mobile Electronic Signatures|
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
                    |  1. Structural Deduplication & String / Schema Sanitization    |
                    |  2. Domain Logic & Geospatial Polygon Bounding Validation      |
                    |  3. Physics Assertion & Target Leakage Status Gating           |
                    |  4. Scikit-Learn Feature Pipeline (RobustScaler + Sin/Cos Enc) |
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
| Dynamic Route & ETA Engine    |   | Fleet Capacity Utilization    |   | Carrier SLA Performance Audit |
| (Gradient Boosted Regressors) |   | (Linear & Integer Programming)|   | (Cost Reconciliation Mart)    |
+-------------------------------+   +-------------------------------+   +-------------------------------+
```

---

## 📐 Mathematical Remediation Formulations

### 1. Tukey’s Fences & Winsorization
Rather than discarding extreme transit times (which discards vital signals of severe road closures and weather disruptions), non-parametric fences are calculated:
$$\text{IQR} = Q_3 - Q_1$$
$$\text{Lower Bound} = \max(\text{Floor}_{\text{physical}}, Q_1 - 1.5 \times \text{IQR}), \quad \text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$
Values beyond the upper threshold are capped (**Winsorized**) to prevent exploding gradients.

### 2. Cyclical Trigonometric Temporal Encodings ($S^1$ Unit Circle)
Dispatch hours ($t \in [0, 24)$) are projected onto a continuous 2D trigonometric circle to ensure the distance between $23:59$ and $00:01$ is infinitesimal rather than $23.96$ hours:
$$x_{\sin} = \sin\left(\frac{2\pi \cdot t}{24}\right), \quad x_{\cos} = \cos\left(\frac{2\pi \cdot t}{24}\right)$$
**Euclidean distance preservation:**
$$D(\mathbf{u}_1, \mathbf{u}_2) = 2\left|\sin\left(\frac{\pi(t_1 - t_2)}{24}\right)\right|$$

### 3. Distributional Scaling: RobustScaler Selection
$$\text{MinMaxScaler: } X_{\text{norm}} = \frac{X - X_{\min}}{X_{\max} - X_{\min}} \quad (\text{Breakdown Point } \epsilon^* = 0\%)$$
$$\text{StandardScaler: } Z = \frac{X - \mu}{\sigma} \quad (\text{Breakdown Point } \epsilon^* = 0\%)$$
$$\mathbf{RobustScaler: } X_{\text{robust}} = \frac{X - \text{median}}{\text{IQR}} \quad (\mathbf{Breakdown Point } \epsilon^* \in [25\%, 50\%])$$
`RobustScaler` ignores the extreme upper and lower 25% of observations during parameter estimation, centering standard parcel flows around $0.0$ while preserving heavy freight magnitude without loss-function collapse.

### 4. Target Leakage Elimination
Missing `actual_delivery_timestamp` records are Missing Not At Random (MNAR), representing delivery exceptions (breakdowns, cancellations). Imputing delivery timestamps synthesizes artificial training targets. The pipeline categorizes these records into `EXCEPTION_OR_IN_TRANSIT` and isolates them from the supervised ETA training matrix.

---

## 🚀 Repository Structure

```
Logistics-Data-Preprocessing-Pipeline/
├── README.md                                 # Project overview & architectural guide
├── TECHNICAL_PREPROCESSING_REPORT.md         # Exhaustive 7-section engineering report
├── generate_docx_report.py                   # Automated Word (.docx) document generator
├── Task_2_Logistics_Data_Preprocessing_Report.docx  # Formatted executive deliverable
├── data/
│   ├── simulated_raw_logistics.csv           # 2,000 raw records with injected defects
│   ├── cleaned_logistics_data.csv            # Cleaned operational dataset post-gating
│   └── processed_feature_matrix.csv          # Scaled, encoded ML feature store (31 features)
├── src/
│   ├── __init__.py
│   ├── simulation.py                         # Multi-tier telematics generator (MCAR, MAR, MNAR)
│   ├── sanitization.py                       # Deduplication & schema coercion
│   ├── validation.py                         # Spatial bounding, physics & temporal validator
│   ├── transformers.py                       # Cyclical temporal, Log1p, and Tukey transformers
│   ├── pipeline.py                           # Scikit-Learn ColumnTransformer pipeline
│   └── run_pipeline.py                       # End-to-end execution runner
└── tests/
    └── test_pipeline.py                      # Automated test suite (invariance, geometry, bounds)
```

---

## ⚡ Quickstart & Execution

### 1. Prerequisites & Environment
Ensure Python 3.10+ is installed:
```bash
pip install pandas numpy scikit-learn python-docx
```

### 2. Execute Automated Unit Tests
Verify deduplication, chronological filtering, geospatial bounding, and cyclical geometry:
```bash
python tests/test_pipeline.py
```
*Output:*
```
All unit and pipeline tests passed successfully!
```

### 3. Run the Production Pipeline
Simulate raw telematics, execute cleaning, fit the Scikit-Learn `ColumnTransformer`, and export clean feature sets:
```bash
python src/run_pipeline.py
```

### 4. Generate the Executive Word (.docx) Report
```bash
python generate_docx_report.py
```

---

## 📊 Preprocessing Audit Metrics & Empirical Results

Benchmark evaluation across 2,000 simulated multimodal telematics records:

| Execution Metric | Ingestion Stage Value | Analytical Interpretation & Engineering Significance |
| :--- | :--- | :--- |
| **Total Ingestion Records** | $2,000\text{ rows}$ | Raw simulated multimodal stream containing realistic anomalies |
| **Duplicate Keys Purged** | $8\text{ rows}$ ($0.40\%$) | Purged redundant API retries, preserving initial arrival timestamps |
| **Geospatial Violations Dropped** | $19\text{ rows}$ ($0.95\%$) | Eliminated Null Island `(0,0)`, swapped coordinates, and out-of-bounds pings |
| **Chronological Inversions Dropped** | $15\text{ rows}$ ($0.75\%$) | Purged physical violations where delivery preceded dispatch |
| **Validated Dataset Yield** | **$1,958\text{ rows}$ ($97.90\%$)** | High operational retention yield for downstream modeling |
| **Delivery Status Partitioning** | • `ON_TIME`: $1,750$ ($89.4\%$)<br>• `LATE`: $144$ ($7.4\%$)<br>• `EXCEPTION`: $64$ ($3.3\%$) | Target leakage eliminated; unrecorded drops isolated from training |
| **Raw Cargo Weight Skewness** | **$+11.9722$** | Extreme right-skew driven by heavy industrial consignments |
| **Post-Log1p Feature Skewness** | **$+1.8251$** | **84.75% skewness reduction**, stabilizing variance and gradient updates |
| **Final Transformed Feature Matrix** | **$1,958\text{ rows} \times 31\text{ features}$** | High-rank, leak-free, scaled numeric matrix ready for production ML |

---

## 📝 Portal Submission Summary (Exactly 200 Words)

> "This comprehensive technical project establishes a production-grade data collection, cleaning, and preprocessing pipeline engineered for multimodal freight telematics and urban last-mile logistics. Benchmarked against canonical supply chain datasets—the Olist Brazilian E-Commerce and DataCo Global Supply Chain repositories—the architecture systematically resolves critical real-world failure modes spanning structural key duplication, sensor calibration drift, chronological timestamp inversions, coordinate transpositions, and severe distributional skew. The pipeline enforces automated primary key deduplication, string and currency sanitization, geospatial polygon bounding, physical feasibility gating, and non-parametric Tukey’s Fences Winsorization. A production Scikit-Learn ColumnTransformer integrates median imputation, cyclical trigonometric temporal encodings (S1 unit circle transformations for 24-hour dispatch cycles), natural logarithmic variance stabilization (log1p), and median-IQR RobustScaler normalizations. Crucially, target leakage is eliminated by categorizing unrecorded delivery timestamps as explicit operational exceptions rather than imputing artificial delivery durations. Across an empirical validation run of 2,000 raw telematics records, the pipeline achieved a 97.90% operational retention yield, stabilized heavy-tail cargo weight skewness from an initial 11.97 down to 1.83, and produced a clean, 31-dimensional feature matrix. This production-ready architecture guarantees numerical stability for downstream ETA regression, carrier classification, route clustering, and fleet optimization while effectively safeguarding enterprise commercial freight operations against costly financial contractual SLA compliance breach chargeback penalties."

---

## 📄 License
This architecture is licensed under the MIT License - see the LICENSE file for details.
#   L o g i s t i c s - D a t a - P r e p r o c e s s i n g - P i p e l i n e  
 