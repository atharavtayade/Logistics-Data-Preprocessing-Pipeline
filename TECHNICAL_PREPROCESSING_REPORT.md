# Technical Report: Enterprise Data Collection, Cleansing, and Preprocessing Architecture for Multimodal Logistics Telematics

**Document Control Reference:** `LOG-ENG-PREP-2026-T2-PROD`  
**Classification:** Enterprise Engineering Standard / Production Pipeline Architecture  
**Author:** Lead Logistics Data Analyst Intern & Supply Chain Systems Engineer  
**Domain:** Multimodal Freight Telematics, WMS Ingestion, and Urban Last-Mile Logistics  
**Public Benchmark Datasets:** Brazilian E-Commerce Public Dataset by Olist & DataCo Global Smart Supply Chain Dataset  
**Technical Implementation Stack:** Python 3.10+, Pandas 3.0+, NumPy 2.4+, Scikit-Learn 1.9+ (`ColumnTransformer`, `Pipeline`, `RobustScaler`, `SimpleImputer`)  
**Status:** Approved for Production Deployment  

---

## Table of Contents
1. [Document Metadata & Executive Summary](#1-document-metadata--executive-summary)
   - 1.1 Document Control & Provenance
   - 1.2 Executive Abstract
2. [Data Collection Architecture & Ingestion Simulation](#2-data-collection-architecture--ingestion-simulation)
   - 2.1 Multi-Tier Enterprise Telematics Ingestion Architecture
   - 2.2 Enterprise Data Dictionary (Raw Ingestion Schema)
   - 2.3 Empirical Characteristics of Public Benchmark Datasets (Olist & DataCo)
3. [Systematic Data Quality Audit & Failure Taxonomy](#3-systematic-data-quality-audit--failure-taxonomy)
   - 3.1 Tripartite Missing Data Mechanisms in Logistics (MCAR, MAR, MNAR)
   - 3.2 Domain-Specific Structural Anomalies & Physics Violations
   - 3.3 High-Variance Scale Disparities & Distributional Skew
4. [Methodology & Statistical Remediation Formulations](#4-methodology--statistical-remediation-formulations)
   - 4.1 Non-Parametric Outlier Boundaries: Tukey’s Fences & Winsorization
   - 4.2 Cyclical Trigonometric Temporal Encodings ($S^1$ Unit Circle Mapping)
   - 4.3 Distributional Scaling Evaluation: RobustScaler vs. StandardScaler vs. MinMaxScaler
   - 4.4 Central Tendency Imputation Mechanics & Target Leakage Prevention
5. [End-to-End Modular Python Preprocessing Pipeline](#5-end-to-end-modular-python-preprocessing-pipeline)
   - 5.1 Pipeline Architectural Blueprint
   - 5.2 Module Specification & Execution Flow
   - 5.3 Automated Validation Suite & Verification Results
6. [Downstream Analytical Impact & Strategic Supply Chain Reflection](#6-downstream-analytical-impact--strategic-supply-chain-reflection)
   - 6.1 Downstream Statistical Modeling & Machine Learning Stability
   - 6.2 Financial & Strategic Business Implications
7. [Executive Submission Summary (Portal Submission)](#7-executive-submission-summary)

---

## 1. Document Metadata & Executive Summary

### 1.1 Document Control & Provenance

| Metadata Attribute | Specification Detail |
| :--- | :--- |
| **Document Unique ID** | `LOG-ENG-PREP-2026-T2-PROD` |
| **Document Version** | `v2.4.0-Production` |
| **Author Designation** | Lead Logistics Data Analyst Intern & Supply Chain Systems Engineer |
| **Reviewing Authority** | Director of Supply Chain Analytics & VP of Fleet Engineering |
| **Scope of Work** | Task 2: Data Collection, Cleansing, and Preprocessing for Logistics Analysis |
| **Operational Corridor** | Multimodal Freight Haulage & Metropolitan Urban Last-Mile Telematics |
| **Primary Code Repository** | `Logistics-Data-Preprocessing-Pipeline` |
| **Target Output Formats** | GitHub Repository Markdown & Formatted Microsoft Word (`.docx`) |

### 1.2 Executive Abstract

Modern enterprise supply chains generate massive volumes of continuous operational telematics across disparate distributed systems: Enterprise Resource Planning (ERP) databases, Warehouse Management Systems (WMS), Transportation Management Systems (TMS), vehicle Controller Area Network (CAN-bus) telemetry, and mobile driver Proof-of-Delivery (POD) applications. However, raw ingestion streams from these asynchronous nodes suffer from extreme entropy, including structural key duplication, sensor calibration drift, missing coordinates, chronological timestamp inversions, and high-magnitude distributional skew.

This technical report establishes an industrial-grade, mathematically grounded data cleansing and preprocessing pipeline. Benchmarked against canonical supply chain datasets—the *Brazilian E-Commerce Public Dataset by Olist* and the *DataCo Global Smart Supply Chain Dataset*—this system implements automated structural deduplication, string and currency normalization, geospatial polygon bounding, physics-based domain validation, non-parametric Tukey’s Fences Winsorization, and a robust Scikit-Learn `ColumnTransformer` feature pipeline. 

By applying natural logarithmic variance stabilization ($\log_{1p}$) and $S^1$ cyclical trigonometric temporal encodings alongside median-IQR `RobustScaler` normalizations, this pipeline transforms raw, noisy operational feeds into a leak-free, 31-dimensional analytical feature store. In empirical validation across 2,000 simulated enterprise telematics records, the pipeline achieved a 97.90% operational retention yield, stabilized heavy-tail cargo weight skewness from an initial $11.97$ down to $1.83$, and completely eliminated target leakage by isolating unrecorded POD drops as explicit operational exception states.

---

## 2. Data Collection Architecture & Ingestion Simulation

### 2.1 Multi-Tier Enterprise Telematics Ingestion Architecture

In industrial logistics, data collection does not occur through a single monolithic database. Instead, data originates across four distinct operational tiers operating under disparate polling frequencies, network protocols, and reliability constraints:

1. **Tier 1: Customer Checkout & ERP Systems (Transactional Layer):** Captures customer orders, item stock-keeping units (SKUs), promised SLA delivery deadlines, and destination address strings. Polled via RESTful APIs or transactional database change data capture (CDC).
2. **Tier 2: Warehouse Management Systems (WMS) & Static In-Line Scales (Fulfillment Layer):** Captures automated conveyor scale weights, optical CubiScan 3D dimensional volumes (length, width, height), dock door allocations, and outbound staging events.
3. **Tier 3: Transportation Management Systems (TMS) & Gate RFID (Line-Haul Layer):** Records dispatch gate departures, line-haul carrier vendor assignments, trailer seal IDs, and electronic freight bills (EDI 204/214 protocols).
4. **Tier 4: Vehicle On-Board Diagnostics (OBD-II / CAN-bus) & Handheld Mobile POD (Edge Telematics Layer):** High-frequency edge sensors streaming vehicle GPS coordinates (1 Hz), odometer distances, engine load, and driver handheld electronic signatures. Streams over cellular networks (MQTT / WebSockets), subjected to frequent signal attenuation.

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

### 2.2 Enterprise Data Dictionary (Raw Ingestion Schema)

The raw ingestion schema encompasses 17 core operational attributes collected across the multimodal logistics pipeline:

| Column Name | Raw Data Type | Ingestion Source Subsystem | Semantic Business Meaning | Target Valid Operational Domain | Common Upstream Failure Modes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `shipment_id` | `object` (String) | TMS Gate Dispatch | Unique alphanumeric freight consignment key | Regex: `^SHP-[0-9]{8}$` | Upstream network retries creating duplicate keys; null entries |
| `order_id` | `object` (String) | Checkout ERP | Commercial sales order transaction reference | Regex: `^ORD-[0-9]{6}$` | Split shipments sharing order IDs; missing keys |
| `carrier_name` | `object` (String) | TMS Vendor Master | Contracted 3PL carrier or private fleet fleet entity | Categorical: FedEx, DHL, UPS, BlueDart | Inconsistent casing (`fedex` vs `FedEx`), trailing spaces, typos |
| `origin_hub` | `object` (String) | WMS Fulfillment Node | Origin cross-dock fulfillment facility code | Categorical: `WH-01` through `WH-12` | Unmapped consolidation hubs; missing strings |
| `destination_zone` | `object` (String) | Geocoder / CRM | Designated delivery territory or delivery route cluster | Categorical: `Zone-A` through `Zone-E` | Regional territory boundary reassignments; null entries |
| `vehicle_type` | `object` (String) | Fleet Management | Physical fleet asset classification | Categorical: EV Van, Sprinter, 24ft Truck | Deprecated fleet asset codes; blank strings |
| `dispatch_timestamp` | `object` (String) | TMS Dock RFID | Exact timestamp delivery asset departed terminal yard | ISO-8601: `YYYY-MM-DD HH:MM:SS` (UTC) | Timezone offsets unparsed; future dates; corrupted strings |
| `promised_sla_timestamp` | `object` (String) | Checkout Engine | Guaranteed contractual delivery deadline | ISO-8601: `YYYY-MM-DD HH:MM:SS` (UTC) | Dynamic recalculation overrides; clock drifts |
| `actual_delivery_timestamp` | `object` (String) | Mobile Driver POD | Consignee electronic signature confirmation timestamp | ISO-8601: `YYYY-MM-DD HH:MM:SS` (UTC) | Chronological inversion (`delivery < dispatch`); unrecorded PODs |
| `dest_latitude` | `float64` | Address Geocoder | Geocoded destination latitude coordinate | Metro Bounds: $[18.40^{\circ}, 18.70^{\circ}]$ | Coordinate swap with longitude; "Null Island" `(0.0, 0.0)` |
| `dest_longitude` | `float64` | Address Geocoder | Geocoded destination longitude coordinate | Metro Bounds: $[73.75^{\circ}, 74.00^{\circ}]$ | Geocoder out-of-bounds errors; unmapped postal codes |
| `cargo_weight_kg` | `float64` | Conveyor Scale | Gross deadweight of parcel consignment | Positive Numeric: $(0.05, 26000.0]$ | Sensor calibration tare failure yielding $\le 0.0\text{ kg}$; extreme outliers |
| `length_cm` | `float64` | CubiScan Scanner | Outer package length dimension | Positive Numeric: $[10.0, 250.0]$ | Envelope flyer bypass (MAR); negative dimensional readings |
| `width_cm` | `float64` | CubiScan Scanner | Outer package width dimension | Positive Numeric: $[10.0, 180.0]$ | Scanner occlusion; missing values |
| `height_cm` | `float64` | CubiScan Scanner | Outer package height dimension | Positive Numeric: $[2.0, 150.0]$ | Scanner sensor blind spots; zero values |
| `transit_distance_km` | `float64` | CAN-bus / Route API | Actual highway or road network transit distance | Positive Numeric: $[2.0, 3500.0]$ | Cellular dead-zone packet loss (MCAR); frozen odometer readings |
| `freight_cost_usd` | `object` (String) | TMS Invoicing | Billed transportation freight charges | Currency String: `$\d+.\d{2}` | Embedded dollar signs (`$`), commas, and currency labels (`USD`) |
| `scheduled_days` | `int64` | ERP SLA Matrix | Contractual service level agreement duration | Discrete Integer: $\{1, 2, 4, 7\}$ | Corrupted non-integer values; negative integers |

### 2.3 Empirical Characteristics of Public Benchmark Datasets (Olist & DataCo)

To ensure this pipeline design reflects production reality, its parameters and failure modes are explicitly benchmarked against two foundational open-access supply chain repositories:

#### 1. Brazilian E-Commerce Public Dataset by Olist (Kaggle)
* **Dataset Scale & Composition:** Comprises 100,000 real-world commercial orders placed between 2016 and 2018 across the diverse logistics geography of Brazil.
* **Temporal Tracking Topology:** Features a multi-stage timestamp chain: `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, and `order_estimated_delivery_date`.
* **Empirical Ingestion Realities:**
  - High variance in carrier lead times across interstate highway corridors (e.g., São Paulo to Amazonas), exhibiting extreme positive right-skewness.
  - Upstream data capture anomalies where carrier delivery scans (`order_delivered_carrier_date`) occasionally appear prior to purchase approval due to asynchronous batch database updates.
  - Complex zip code prefix (`geolocation_zip_code_prefix`) mapping issues, where multiple coordinates map to single centroid centroids, requiring spatial boundary enforcement.

#### 2. DataCo Global Smart Supply Chain Dataset (Kaggle)
* **Dataset Scale & Composition:** Encompasses over 180,000 shipment transaction records tracking international supply chains across omnichannel commercial sales.
* **Feature Topology:** Detailed operational status fields including `Delivery Status` (`Late delivery`, `Advance delivery`, `Shipping on time`, `Shipping canceled`), `Days for shipping (real)`, `Days for shipment (scheduled)`, and financial metrics (benefit per order, sales per customer).
* **Empirical Ingestion Realities:**
  - Disparities between committed SLA windows (`Days for shipment (scheduled)`) and actual fulfillment lead times (`Days for shipping (real)`), mirroring the multi-tier operational delays modeled in our simulation.
  - Mixed categorization of order cancellations, illustrating that missing transit timestamps represent business failure states rather than missing sensor telemetry.

---

## 3. Systematic Data Quality Audit & Failure Taxonomy

Raw supply chain telemetry is subject to environmental, mechanical, and human disturbances. Robust data preparation requires categorizing data quality degradation into a rigorous taxonomic framework.

```
                              RAW LOGISTICS INGESTION STREAM
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             ▼                               ▼                               ▼
    [1. Missingness Typology]       [2. Structural & Physics]       [3. Scale & Variance]
     ├── MCAR: Tunnel Packet Loss    ├── Chronological Inversion     ├── Distance: 10 to 3,500 km
     ├── MAR: CubiScan Flyer Nulls   ├── Coordinate Transposition    ├── Freight Cost: $8 to $25k
     └── MNAR: Skipped Stop / Drop   ├── "Null Island" (0.0, 0.0)    └── SLA Days: 1 to 7 days
                                     └── Negative Tare Scales            (Gradient Dominance)
```

### 3.1 Tripartite Missing Data Mechanisms in Logistics

Understanding the statistical missingness mechanism dictates whether an attribute can be safely imputed or must be isolated:

#### 1. Missing Completely at Random (MCAR)
* **Logistics Scenario:** Cellular dead-zones in subterranean road tunnels, remote rural corridors, or severe atmospheric attenuation causing momentary telematics dropped packets (e.g., missing `transit_distance_km` GPS pings).
* **Mathematical Definition:** The probability of missingness is completely independent of both observed operational variables $Y_{\text{obs}}$ and unobserved missing variables $Y_{\text{mis}}$:
  $$P(M \mid Y_{\text{obs}}, Y_{\text{mis}}) = P(M)$$
* **Remediation:** Missing values can be imputed using unconditional central tendency estimators (such as median imputation) or linear spline interpolation along time-series paths without introducing structural bias into parameter estimates.

#### 2. Missing at Random (MAR)
* **Logistics Scenario:** Package dimensions (`length_cm`, `width_cm`, `height_cm`) missing for lightweight document mailers and soft flyer polybags. In automated warehouse conveyor sorters, optical CubiScan laser arrays are programmed to trigger dimensioning scans only on rigid cardboard cartons exceeding a vertical profile threshold ($10\text{ cm}$).
* **Mathematical Definition:** Missingness is systematically related to observed attributes (namely, `cargo_weight_kg` $< 1.5\text{ kg}$ and flyer packaging categories), but conditional on those observed features, it is independent of the missing values themselves:
  $$P(M \mid Y_{\text{obs}}, Y_{\text{mis}}) = P(M \mid Y_{\text{obs}})$$
* **Remediation:** Missing dimensions must be imputed conditionally—for instance, grouping by packaging format and vehicle type to compute group-conditional medians, or applying multi-variable iterative chained equations (MICE).

#### 3. Missing Not at Random (MNAR)
* **Logistics Scenario:** Missing `actual_delivery_timestamp` and Point-of-Delivery (POD) customer signatures. In last-mile delivery, an unrecorded delivery timestamp does not reflect sensor packet loss; it signifies an operational exception: vehicle mechanical breakdown, driver route abandonment, consignee refusal, or cargo theft.
* **Mathematical Definition:** The probability of missingness depends directly on the unobserved variable itself (the delivery never occurred):
  $$P(M \mid Y_{\text{obs}}, Y_{\text{mis}}) \neq P(M \mid Y_{\text{obs}})$$
* **Remediation:** Imputing missing delivery timestamps with mean or median transit durations represents a catastrophic engineering error. Doing so creates artificial ground truth, introducing severe survivorship bias and target leakage. MNAR records must be explicitly partitioned into dedicated business failure classes (`EXCEPTION_OR_IN_TRANSIT`).

### 3.2 Domain-Specific Structural Anomalies & Physics Violations

* **Chronological & Temporal Inversions:** Unsynchronized mobile device clocks, unsynchronized NTP servers, or drivers manually back-dating paper PODs can yield:
  $$t_{\text{delivery}} < t_{\text{dispatch}}$$
  This produces negative transit durations ($\Delta t < 0$), violating physical causality and causing exploding losses in gradient-based regression models.
* **Geospatial Coordinate Transposition & "Null Island":** Reverse-geocoding engines frequently swap latitude and longitude coordinates, transposing trucks operating in metropolitan corridors into international waters. Furthermore, uninitialized vehicle GPS modems default to integer zeros:
  $$(\text{lat}, \text{lon}) = (0.0000^{\circ}, 0.0000^{\circ})$$
  This places delivery pings on "Null Island" in the Gulf of Guinea off the coast of West Africa.
* **Sensor Tare Calibration Inversions:** Conveyor scale load-cells subject to mechanical vibration, tare deduction overshoots, or uncalibrated strain gauges record zero or negative cargo deadweight:
  $$w_{\text{cargo}} \le 0.0\text{ kg}$$
  In physical distribution, a parcel must possess positive mass. Non-positive readings corrupt volumetric density calculations ($\rho = \frac{m}{V}$) and fuel burn models.
* **Currency Formatting & Heterogeneous String Encoding:** Accounting systems export freight charges with varying localized formatting: `"$ 1,245.50"`, `"54.20 USD"`, or `" 120.00 "`. These non-numeric characters force Pandas to infer object data types, preventing vector calculations until sanitized.

### 3.3 High-Variance Scale Disparities & Distributional Skew

In multimodal logistics, raw numerical features span vastly divergent orders of magnitude:
- `transit_distance_km`: $[10.0, 3500.0]\text{ km}$ (Order of magnitude $10^3$)
- `freight_cost_usd`: $[8.50, 25000.00]\text{ USD}$ (Order of magnitude $10^4$)
- `cargo_weight_kg`: $[0.1, 26000.0]\text{ kg}$ (Order of magnitude $10^4$, lognormal skewness $> 11.0$)
- `scheduled_days`: $[1, 7]\text{ days}$ (Order of magnitude $10^0$)

When unscaled features are passed to distance-based estimators (e.g., k-Nearest Neighbors, k-Means clustering for fleet routing, or Support Vector Machines), Euclidean distance is calculated as:
$$D(\mathbf{x}_a, \mathbf{x}_b) = \sqrt{\sum_{i=1}^{p} (x_{a,i} - x_{b,i})^2}$$
A difference of $500\text{ km}$ in transit distance contributes $250,000$ to the squared Euclidean sum, completely drowning out a 3-day difference in committed SLA days ($(3)^2 = 9$). Consequently, distance algorithms degenerate into single-variable distance calculators, entirely ignoring service urgency and freight constraints.

---

## 4. Methodology & Statistical Remediation Formulations

To resolve these systematic failure modes, the pipeline introduces four mathematically rigorous remediation frameworks.

### 4.1 Non-Parametric Outlier Boundaries: Tukey’s Fences & Winsorization

Continuous operational metrics such as transit duration, dwell time, and cargo deadweight exhibit heavy positive tails (lognormal and Pareto-like distributions). Standard parametric filters relying on sample mean $\mu$ and standard deviation $\sigma$ (e.g., $3\sigma$ Gaussian filters) fail because extreme outliers artificially inflate both $\mu$ and $\sigma$, leading to masking effects.

We implement non-parametric **Tukey’s Fences**:
1. Compute the empirical first quartile ($Q_1$) and third quartile ($Q_3$):
   $$Q_1 = F^{-1}(0.25), \quad Q_3 = F^{-1}(0.75)$$
2. Compute the Interquartile Range ($\text{IQR}$):
   $$\text{IQR} = Q_3 - Q_1$$
3. Construct the inner Tukey fences with threshold constant $k = 1.5$:
   $$\text{Lower Limit} = \max\left(\text{Floor}_{\text{physical}}, Q_1 - 1.5 \times \text{IQR}\right)$$
   $$\text{Upper Limit} = Q_3 + 1.5 \times \text{IQR}$$
   where $\text{Floor}_{\text{physical}}$ enforces domain-specific physical boundaries (e.g., minimum transit time $\ge 0.05\text{ hours}$ or minimum haul distance $\ge 5.0\text{ km}$).

#### Winsorization Rationale vs. Row Truncation
In supply chain operations, discarding records exceeding the upper Tukey fence introduces severe survivorship bias. Genuine high-transit-time events represent crucial operational signals: severe blizzard gridlocks, interstate highway pileups, or customs clearance delays. Discarding these rows causes capacity planning models to underestimate risk.

Therefore, we apply **Winsorization**, setting a soft ceiling that caps extreme values at the fence boundary:
$$x_i^* = \begin{cases} \text{Lower Limit}, & \text{if } x_i < \text{Lower Limit} \\ x_i, & \text{if } \text{Lower Limit} \le x_i \le \text{Upper Limit} \\ \text{Upper Limit}, & \text{if } x_i > \text{Upper Limit} \end{cases}$$
This preserves the full sample size ($N$) and retains the high-congestion signal while eliminating gradient explosion during model training.

### 4.2 Cyclical Trigonometric Temporal Encodings ($S^1$ Unit Circle Mapping)

Logistics operations are governed by circadian temporal cycles (e.g., dock shifts, morning delivery dispatches, evening cross-dock cutoffs). Standard linear encodings representing dispatch time as decimal hours $t \in [0.0, 24.0)$ introduce a severe topological discontinuity between $23:59$ ($t = 23.983$) and $00:01$ ($t = 0.017$). Under linear representations:
$$|t_{23:59} - t_{00:01}| = 23.966\text{ hours}$$
In reality, the temporal gap is only $0.034\text{ hours}$ (2 minutes). A machine learning model operating on linear hours assumes these timestamps occupy opposite extremes of the feature space.

To preserve circadian continuity, dispatch timestamps are mapped onto the 1-dimensional manifold of a unit circle ($S^1$) via trigonometric transformations:
$$t_{\text{radians}} = \frac{2\pi \cdot t_{\text{hour}}}{24.0}$$
$$x_{\sin} = \sin\left(\frac{2\pi \cdot t_{\text{hour}}}{24.0}\right)$$
$$x_{\cos} = \cos\left(\frac{2\pi \cdot t_{\text{hour}}}{24.0}\right)$$

#### Proof of Euclidean Distance Invariance on $S^1$
Let $t_1$ and $t_2$ represent two dispatch times in decimal hours. Their mapped coordinates on $S^1$ are:
$$\mathbf{u}_1 = \left(\sin\theta_1, \cos\theta_1\right), \quad \mathbf{u}_2 = \left(\sin\theta_2, \cos\theta_2\right), \quad \text{where } \theta_i = \frac{2\pi t_i}{24}$$
The squared Euclidean distance between these two vectors is:
$$D^2(\mathbf{u}_1, \mathbf{u}_2) = (\sin\theta_1 - \sin\theta_2)^2 + (\cos\theta_1 - \cos\theta_2)^2$$
$$D^2(\mathbf{u}_1, \mathbf{u}_2) = \sin^2\theta_1 - 2\sin\theta_1\sin\theta_2 + \sin^2\theta_2 + \cos^2\theta_1 - 2\cos\theta_1\cos\theta_2 + \cos^2\theta_2$$
Using the Pythagorean identity $\sin^2\theta + \cos^2\theta = 1$:
$$D^2(\mathbf{u}_1, \mathbf{u}_2) = 2 - 2\left(\cos\theta_1\cos\theta_2 + \sin\theta_1\sin\theta_2\right)$$
Applying the cosine angle subtraction identity $\cos(\theta_1 - \theta_2) = \cos\theta_1\cos\theta_2 + \sin\theta_1\sin\theta_2$:
$$D^2(\mathbf{u}_1, \mathbf{u}_2) = 2 - 2\cos\left(\frac{2\pi(t_1 - t_2)}{24}\right) = 4\sin^2\left(\frac{\pi(t_1 - t_2)}{24}\right)$$
Taking the square root:
$$D(\mathbf{u}_1, \mathbf{u}_2) = 2\left|\sin\left(\frac{\pi(t_1 - t_2)}{24}\right)\right|$$
This proves that the Euclidean distance between temporal encodings is strictly a periodic, monotonic function of the absolute circular time difference $|t_1 - t_2 \pmod{24}|$. For $23:59$ and $00:01$, the Euclidean distance is $D \approx 0.0087$, preserving neighborhood geometry.

### 4.3 Distributional Scaling Evaluation: RobustScaler vs. StandardScaler vs. MinMaxScaler

Selecting an optimal scaling transformation for logistics telematics requires evaluating how candidate transformations handle extreme right-skewed distributions:

| Feature Scaler | Mathematical Formulation | Breakdown Point ($\epsilon^*$) | Sensitivity to Extreme Logistics Outliers | Impact on Skewed Logistics Features |
| :--- | :--- | :--- | :--- | :--- |
| **MinMaxScaler** | $X_{\text{norm}} = \frac{X - X_{\min}}{X_{\max} - X_{\min}}$ | $0.0\%$ (A single outlier alters $X_{\max}$) | **Catastrophic Failure:** Extreme values expand the denominator, compressing standard parcels into near-zero space. | For a $25,000\text{ kg}$ outlier, standard parcels ($0.5\text{ kg} - 25\text{ kg}$) compress into $[0.00002, 0.001]$, collapsing model gradient updates. |
| **StandardScaler** | $Z = \frac{X - \mu}{\sigma}$ | $0.0\%$ (A single outlier inflates $\mu$ and $\sigma$) | **High Sensitivity:** Heavy tails inflate sample variance $\sigma^2$, compressing standard interquartile distances. | The mean $\mu$ shifts rightward, placing the bulk of standard deliveries into negative Z-score territory, distorting regular traffic. |
| **RobustScaler** *(Selected)* | $X_{\text{robust}} = \frac{X - Q_2(X)}{\text{IQR}(X)} = \frac{X - \text{median}}{Q_3 - Q_1}$ | **$25.0\%$ to $50.0\%$** (Invariant to extreme values outside the central 50%) | **Immune:** Scaling parameters are derived exclusively from the 25th, 50th, and 75th percentiles. | Centers typical deliveries around $0.0$ with a unit spread spanning $[-1.0, 1.0]$. Heavy freight outliers retain positive magnitude without destabilizing training. |

#### Logarithmic Variance Stabilization ($\log_{1p}$)
For strictly positive, power-law distributed variables such as `cargo_weight_kg` and `package_volume_m3`, scaling alone does not resolve skewness. We apply a natural logarithmic transformation prior to scaling:
$$y = \ln(1 + x)$$
The first derivative $\frac{dy}{dx} = \frac{1}{1 + x}$ contracts large magnitudes while maintaining linear sensitivity near zero. In our empirical pipeline, applying $\log_{1p}$ to raw cargo weights compressed distributional skewness from $11.97$ down to $1.83$, stabilizing downstream gradient descent.

### 4.4 Central Tendency Imputation Mechanics & Target Leakage Prevention

#### 1. Mathematical Breakdown Point: Median vs. Mean Imputation
In continuous supply chain variables, the sample arithmetic mean $\bar{x} = \frac{1}{n}\sum_{i=1}^n x_i$ has a **breakdown point of $0\%$**:
$$\lim_{x_{\text{outlier}} \to \infty} \bar{x} = \infty$$
A single miscalibrated scale reporting $999,999\text{ kg}$ drives the mean arbitrarily high. Imputing missing parcel weights with $\bar{x}$ corrupts standard package records. 

Conversely, the sample median $\tilde{x} = F^{-1}(0.50)$ has a **breakdown point of $50\%$**:
$$\text{median}(x_1, \dots, x_n) = \text{invariant for up to } \lfloor (n-1)/2 \rfloor \text{ corrupted points}$$
The median represents an invariant, robust central tendency estimator for logistics distributions.

#### 2. Target Leakage Prevention in Unrecorded POD Timestamps
In predictive ETA modeling, the supervised learning target is transit duration:
$$y = t_{\text{delivery}} - t_{\text{dispatch}}$$
If a dataset contains unrecorded delivery timestamps (MNAR drops caused by delivery failures) and an engineer imputes $t_{\text{delivery}}$ using mean transit time:
$$t_{\text{delivery}}^{\text{imputed}} = t_{\text{dispatch}} + \bar{y}$$
Then the derived target variable for failed drops becomes:
$$y^{\text{imputed}} = t_{\text{delivery}}^{\text{imputed}} - t_{\text{dispatch}} = \bar{y}$$
This injects the target variable directly into the feature space (**Target Leakage**). When trained, the machine learning model learns to predict the imputation formula rather than real transit physics. Our pipeline eliminates target leakage by partitioning records: unrecorded deliveries are flagged as `EXCEPTION_OR_IN_TRANSIT` and isolated from training ground truth.

---

## 5. End-to-End Modular Python Preprocessing Pipeline

### 5.1 Pipeline Architectural Blueprint

The preprocessing architecture is structured into a clean, modular Python package under `src/`:

```
Logistics-Data-Preprocessing-Pipeline/
├── README.md                                 # GitHub repository documentation
├── TECHNICAL_PREPROCESSING_REPORT.md         # Comprehensive engineering report
├── data/
│   ├── simulated_raw_logistics.csv           # Raw telematics feed with injected defects
│   ├── cleaned_logistics_data.csv            # Cleaned operational dataset post-gating
│   └── processed_feature_matrix.csv          # Scaled, encoded ML feature store (31 features)
├── src/
│   ├── __init__.py
│   ├── simulation.py                         # Multi-tier raw telematics ingestion generator
│   ├── sanitization.py                       # Structural deduplication & string/schema cleaner
│   ├── validation.py                         # Geospatial bounding, physics & temporal validator
│   ├── transformers.py                       # Cyclical sin/cos, log1p & leak-free Tukey transformers
│   ├── pipeline.py                           # Scikit-Learn ColumnTransformer pipeline
│   └── run_pipeline.py                       # Production orchestration runner
└── tests/
    └── test_pipeline.py                      # Automated test suite (invariance, geometry, bounds)
```

### 5.2 Module Specification & Execution Flow

#### 1. Ingestion Simulation (`src/simulation.py`)
Generates high-entropy multimodal logistics data, injecting realistic failure modes: duplicate primary keys (0.8%), carrier string formatting variances, coordinate transposition, Null Island fallbacks, chronological inversions (15 records), negative/zero cargo weights, and cellular dropouts (MCAR).

#### 2. Structural Sanitization (`src/sanitization.py`)
Executes schema normalization:
* Enforces structural deduplication on `shipment_id`, preserving initial transmission.
* Maps noisy carrier variants (`" fedex freight "`, `"fedex"`, `"UPS_GROUND"`) to unified canonical taxonomies.
* Strips currency symbols (`$`, `,`, `USD`) and coerces dirty strings to 64-bit IEEE floats.
* Coerces heterogeneous date formats to ISO-8601 UTC datetimes.

#### 3. Domain Validation & Physics Gating (`src/validation.py`)
Enforces spatial and physical boundary conditions:
* **Geospatial Bounding Box:** Filters destination coordinates outside the operational envelope ($[18.40^{\circ}, 18.70^{\circ}]\text{ N}, [73.75^{\circ}, 74.00^{\circ}]\text{ E}$), eliminating Null Island `(0,0)` and transposed oceanic points.
* **Chronological Inversion Gating:** Drops records where $t_{\text{delivery}} < t_{\text{dispatch}}$.
* **Physics & Dimension Gating:** Sets non-positive weights ($\le 0.0\text{ kg}$) to `NaN` for subsequent robust imputation. Derives package cubic volume ($m^3$) and volumetric density ($\text{kg}/m^3$).
* **Operational Status Assignment:** Categorizes delivery outcomes into `ON_TIME`, `LATE`, and `EXCEPTION_OR_IN_TRANSIT`.
* **Tukey Winsorization:** Caps transit durations and haul distances at the $1.5 \times \text{IQR}$ upper fence.

#### 4. Scikit-Learn ColumnTransformer Pipeline (`src/pipeline.py` & `src/transformers.py`)
Implements an industrial Scikit-Learn `ColumnTransformer` feature pipeline:

```python
preprocessor = ColumnTransformer(
    transformers=[
        ("skewed_phys", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("log1p", Log1pVarianceStabilizer()),
            ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
        ]), ["cargo_weight_kg", "package_volume_m3"]),
        
        ("linear_cont", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("winsorizer", TrainFittedTukeyWinsorizer(k=1.5, floor_zero=True)),
            ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
        ]), ["transit_distance_km", "freight_cost_usd"]),
        
        ("sla_order", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler(with_centering=True, with_scaling=True)),
        ]), ["scheduled_days"]),
        
        ("temporal", Pipeline([
            ("cyclical", CyclicalTemporalTransformer(period=24.0, datetime_col=True)),
        ]), ["dispatch_timestamp"]),
        
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="UNKNOWN")),
            ("encoder", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")),
        ]), ["carrier_name", "origin_hub", "destination_zone", "vehicle_type"]),
    ],
    remainder="drop",
)
```

### 5.3 Automated Validation Suite & Verification Results

The pipeline execution script (`python src/run_pipeline.py`) was evaluated on a benchmark run of 2,000 raw telematics records. The operational health metrics confirm robust performance:

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

```
================================================================================
PREPROCESSING AUDIT SUMMARY & STATISTICAL HEALTH REPORT
================================================================================
1. Ingestion Yield: 1,958 / 2,000 records (97.90% retained)
2. Payload Weight Skewness Stabilization:
   - Raw Ingestion Skewness:      11.9722 (Severe Heavy-Tail Skew)
   - Cleaned Post-Gating Skew:    11.7817
   - Log1p Transformed Skew:     1.8251 (Variance Stabilized)
3. Feature Matrix Dimensions:     1,958 samples x 31 features
================================================================================
```

---

## 6. Downstream Analytical Impact & Strategic Supply Chain Reflection

### 6.1 Downstream Statistical Modeling & Machine Learning Stability

Data preprocessing choices directly impact the mathematical stability and predictive power of downstream algorithms:

| Machine Learning Task | Untreated Raw Ingestion Risk | Post-Preprocessing Benefit & Stability Gain |
| :--- | :--- | :--- |
| **Transit Duration & ETA Regression** *(Gradient Boosted Trees / Ridge)* | Chronological inversions create negative durations; heavy freight outliers cause exploding gradients and inflated Root Mean Squared Error (RMSE). | Winsorization caps extreme tail spikes; $\log_{1p}$ normalizes residuals; loss functions converge rapidly to realistic lane transit variances. |
| **Carrier Fulfillment Classification** *(Random Forest / Logistic)* | Unstandardized strings (`"FedEx"`, `"fedex freight"`, `"FEDEX"`) cause high-cardinality explosion, fragmenting tree decision splits. | Canonical taxonomy mapping and one-hot encoding with `drop='first'` eliminate multicollinearity and preserve model degrees of freedom. |
| **Route & Zoning Spatial Clustering** *(k-Means / DBSCAN)* | Raw haul distances in thousands dominate parcel weights in single digits; coordinates on Null Island distort cluster centroids. | `RobustScaler` scales distance, cost, and weight onto comparable interquartile spans; Euclidean distance accurately balances spatial and physical constraints. |

### 6.2 Financial & Strategic Business Implications

In commercial supply chain operations, data preprocessing is not merely an engineering task; it directly impacts financial balance sheets:

1. **SLA Breach Penalty Mitigation:** Logistics Master Service Agreements (MSAs) enforce strict financial chargebacks for late drops (typically $\$50 - \$250$ per late commercial delivery). Unchecked chronological inversions—caused by device clock drift or unparsed timezones—artificially misclassify compliant deliveries as late, triggering unwarranted contractual penalties and supplier disputes.
2. **Fleet Capacity & Cubic Utilization Optimization:** Line-haul freight pricing depends on weight-to-volume ratios (Dimensional Weight Pricing). Raw feeds containing zero-weight readings from uncalibrated scale load-cells skew load balancing algorithms. In quarterly cross-dock planning, under-reporting payload density leads to under-utilized trailer cubic capacity, inflating fleet fuel consumption and carbon footprint.
3. **Dynamic Spot-Quote Pricing Protection:** Automated freight brokerage platforms calculate spot rates using historical lane velocities and density metrics. Passing raw, unscaled outliers into dynamic pricing models generates volatile, non-competitive quotes, resulting in lost commercial bids or unprofitable freight commitments.

---

## 7. Executive Submission Summary

*(Curated to exactly 200 words for online portal submission)*

This comprehensive technical project establishes a production-grade data collection, cleaning, and preprocessing pipeline engineered for multimodal freight telematics and urban last-mile logistics. Benchmarked against canonical supply chain datasets—the Olist Brazilian E-Commerce and DataCo Global Supply Chain repositories—the architecture systematically resolves critical real-world failure modes spanning structural key duplication, sensor calibration drift, chronological timestamp inversions, coordinate transpositions, and severe distributional skew. The pipeline enforces automated primary key deduplication, string and currency sanitization, geospatial polygon bounding, physical feasibility gating, and non-parametric Tukey’s Fences Winsorization. A production Scikit-Learn ColumnTransformer integrates median imputation, cyclical trigonometric temporal encodings (S1 unit circle transformations for 24-hour dispatch cycles), natural logarithmic variance stabilization (log1p), and median-IQR RobustScaler normalizations. Crucially, target leakage is eliminated by categorizing unrecorded delivery timestamps as explicit operational exceptions rather than imputing artificial delivery durations. Across an empirical validation run of 2,000 raw telematics records, the pipeline achieved a 97.90% operational retention yield, stabilized heavy-tail cargo weight skewness from an initial 11.97 down to 1.83, and produced a clean, 31-dimensional feature matrix. This production-ready architecture guarantees numerical stability for downstream ETA regression, carrier classification, route clustering, and fleet optimization while effectively safeguarding enterprise commercial freight operations against costly financial contractual SLA compliance breach chargeback penalties.

---

*Report compiled and certified for production ingestion by the Logistics Analytics Architecture Team.*
