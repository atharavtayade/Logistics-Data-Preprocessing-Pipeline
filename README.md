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
