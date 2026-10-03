"""
Logistics Raw Telematics and Multi-Tier Ingestion Simulator.
Simulates asynchronous feeds from WMS, TMS, CAN-bus, and Driver Handheld POD devices,
systematically injecting domain-specific failure modes (MCAR, MAR, MNAR, inversions,
Null Island coordinates, and physical sensor drift).
"""

from typing import Optional
import numpy as np
import pandas as pd


def generate_raw_multimodal_telematics(
    n_records: int = 1500,
    seed: int = 42,
    city_lat_bounds: tuple[float, float] = (18.40, 18.70),
    city_lon_bounds: tuple[float, float] = (73.75, 74.00),
) -> pd.DataFrame:
    """
    Synthesizes a realistic, high-entropy enterprise logistics telematics stream.

    Injected Data Quality Defects:
    1. Structural Duplicates: Duplicate primary transmission keys.
    2. String & Schema Inconsistencies: Casing variances, untrimmed whitespace,
       and unparsed currency text fields.
    3. Chronological Inversions: Delivery timestamps preceding dock dispatch.
    4. Missing Data Typologies:
       - MCAR: Cellular signal dropouts in odometer telemetry.
       - MAR: Dimension scanner nulls conditioned on lightweight flyers/envelopes.
       - MNAR: Unrecorded POD timestamps resulting from delivery exceptions/failures.
    5. Sensor & Physical Violations:
       - Strain-gauge tare drift yielding zero or negative cargo weights.
       - Extreme industrial freight outliers (Pareto / Log-normal heavy tails).
    6. Geospatial Anomalies:
       - Geocoder coordinate inversions and "Null Island" (0.0, 0.0) fallback records.
    """
    np.random.seed(seed)
    base_timestamp = pd.Timestamp("2026-10-01 06:00:00")

    # 1. Primary Identifier Generation
    shipment_ids = [f"SHP-{10000000 + i}" for i in range(n_records)]
    order_ids = [f"ORD-{500000 + (i % (n_records - 50))}" for i in range(n_records)]

    # Inject duplicate transmissions (0.8% duplicate rate)
    for dup_idx in [12, 45, 120, 310, 550, 890, 1100, 1340]:
        if dup_idx < n_records:
            shipment_ids[dup_idx] = shipment_ids[dup_idx - 1]

    # 2. Master Categorical Attributes with Formatting Noise
    raw_carriers = [
        "FedEx Freight", "DHL Express", "UPS Ground", "BlueDart Logistics",
        " fedex freight ", "dhl express", "UPS_GROUND", "BlueDart", "UNKNOWN"
    ]
    carrier_probs = [0.28, 0.24, 0.22, 0.16, 0.03, 0.03, 0.02, 0.01, 0.01]
    carrier_col = np.random.choice(raw_carriers, size=n_records, p=carrier_probs)

    origin_hubs = [f"WH-{i:02d}" for i in range(1, 13)] + [None, "WH-99_INVALID"]
    hub_probs = [0.08] * 12 + [0.03, 0.01]
    hub_col = np.random.choice(origin_hubs, size=n_records, p=hub_probs)

    destination_zones = ["Zone-Metro-A", "Zone-Suburban-B", "Zone-Industrial-C", "Zone-Rural-D", None]
    zone_probs = [0.35, 0.30, 0.20, 0.12, 0.03]
    zone_col = np.random.choice(destination_zones, size=n_records, p=zone_probs)

    vehicle_classes = ["EV_CARGO_VAN", "SPRINTER_VAN", "RIGID_TRUCK_24FT", "HEAVY_FREIGHT_TRAILER"]
    vehicle_col = np.random.choice(vehicle_classes, size=n_records, p=[0.40, 0.35, 0.15, 0.10])

    # 3. Temporal Dispatch & SLA Windows
    dispatch_offsets_minutes = np.random.uniform(0, 1440 * 3, size=n_records)  # 3-day window
    dispatch_datetimes = [base_timestamp + pd.Timedelta(minutes=float(m)) for m in dispatch_offsets_minutes]

    # SLA commitment tier: 1 day (express), 2 days (priority), 4 days (standard), 7 days (economy)
    scheduled_days_col = np.random.choice([1, 2, 4, 7], size=n_records, p=[0.25, 0.35, 0.30, 0.10])
    sla_deadlines = [
        dt + pd.Timedelta(days=int(sd)) for dt, sd in zip(dispatch_datetimes, scheduled_days_col)
    ]

    # Actual transit duration (Lognormal distribution with operational tail)
    # Median ~ 18 hours, tail extending into multi-day congestion
    transit_hours = np.random.lognormal(mean=2.8, sigma=0.65, size=n_records)

    delivery_datetimes: list[Optional[pd.Timestamp]] = []
    for dt, dur in zip(dispatch_datetimes, transit_hours):
        delivery_datetimes.append(dt + pd.Timedelta(hours=float(dur)))

    # Ingestion Defect: Chronological Inversions (Delivery occurs before Dispatch)
    inversion_indices = np.random.choice(n_records, size=15, replace=False)
    for idx in inversion_indices:
        delivery_datetimes[idx] = dispatch_datetimes[idx] - pd.Timedelta(hours=np.random.uniform(1.5, 12.0))

    # Ingestion Defect: Missing Not At Random (MNAR) - Failed drops, returns, consignee absent
    # Missing delivery timestamps are unrecorded POD events
    mnar_indices = np.random.choice(n_records, size=65, replace=False)
    for idx in mnar_indices:
        delivery_datetimes[idx] = None

    # 4. Geospatial Coordinate Fields (Pune Metropolitan Corridor Benchmark)
    lat_min, lat_max = city_lat_bounds
    lon_min, lon_max = city_lon_bounds
    lats = np.random.uniform(lat_min, lat_max, size=n_records)
    lons = np.random.uniform(lon_min, lon_max, size=n_records)

    # Ingestion Defect: Null Island (0.0, 0.0) fallback on uninitialized GPS
    null_island_indices = np.random.choice(n_records, size=8, replace=False)
    for idx in null_island_indices:
        lats[idx] = 0.0
        lons[idx] = 0.0

    # Ingestion Defect: Geospatial Transposition / Geocoder Coordinate Swaps
    swapped_indices = np.random.choice(n_records, size=6, replace=False)
    for idx in swapped_indices:
        temp = lats[idx]
        lats[idx] = lons[idx]
        lons[idx] = temp

    # Ingestion Defect: Wild Out-of-Bounds Coordinates
    oob_indices = np.random.choice(n_records, size=5, replace=False)
    for idx in oob_indices:
        lats[idx] = 99.9999
        lons[idx] = -195.4321

    # 5. Physical Dimensions & Payload Metrics
    # Mixture of parcel payloads: standard parcels (0.5 to 25 kg) and heavy freight consignments
    base_weights_kg = np.random.lognormal(mean=2.2, sigma=1.2, size=n_records)  # in kg
    # Scale up a few industrial freight outliers (heavy haul)
    heavy_freight_indices = np.random.choice(n_records, size=18, replace=False)
    for idx in heavy_freight_indices:
        base_weights_kg[idx] = np.random.uniform(8000.0, 26000.0)

    # Ingestion Defect: Negative and Zero weights (Sensor tare failure)
    zero_weight_indices = np.random.choice(n_records, size=12, replace=False)
    for idx in zero_weight_indices:
        base_weights_kg[idx] = 0.0
    negative_weight_indices = np.random.choice(n_records, size=8, replace=False)
    for idx in negative_weight_indices:
        base_weights_kg[idx] = -float(np.random.uniform(2.5, 45.0))

    # Package Dimensions (cm)
    lengths_cm = np.random.uniform(15.0, 110.0, size=n_records)
    widths_cm = np.random.uniform(10.0, 85.0, size=n_records)
    heights_cm = np.random.uniform(5.0, 60.0, size=n_records)

    # Ingestion Defect: Missing at Random (MAR) - Envelope flyers not triggering CubiScan
    # Soft flyer envelopes under 1.5 kg frequently bypass 3D dimensioning beams
    for i in range(n_records):
        if base_weights_kg[i] < 1.5 and np.random.rand() < 0.65:
            lengths_cm[i] = np.nan
            widths_cm[i] = np.nan
            heights_cm[i] = np.nan

    # 6. Haul Distance and Telematics Sensor Dropouts (MCAR)
    # Haversine / road distances in km
    transit_distance_km = np.random.uniform(12.0, 1850.0, size=n_records)
    # MCAR: Random telematics antenna packet loss
    mcar_dist_indices = np.random.choice(n_records, size=35, replace=False)
    for idx in mcar_dist_indices:
        transit_distance_km[idx] = np.nan

    # 7. Freight Costs Invoiced as Raw Unsanitized Currency Strings
    base_cost = (base_weights_kg * 0.42) + (transit_distance_km * 0.68) + np.random.normal(20, 5, size=n_records)
    base_cost = np.maximum(base_cost, 8.50)  # Minimum floor charge

    cost_strings: list[Optional[str]] = []
    for c in base_cost:
        if np.isnan(c) or np.random.rand() < 0.03:
            cost_strings.append(None)
        else:
            # Varying currency formatting: "$ 1,245.50", "1245.50 USD", " $54.20 "
            r_fmt = np.random.rand()
            if r_fmt < 0.60:
                cost_strings.append(f"${c:,.2f}")
            elif r_fmt < 0.85:
                cost_strings.append(f" ${c:,.2f} ")
            elif r_fmt < 0.95:
                cost_strings.append(f"{c:.2f} USD")
            else:
                cost_strings.append(f"${c:,.2f}")

    # Build Raw DataFrame with String Representations
    df_raw = pd.DataFrame({
        "shipment_id": shipment_ids,
        "order_id": order_ids,
        "carrier_name": carrier_col,
        "origin_hub": hub_col,
        "destination_zone": zone_col,
        "vehicle_type": vehicle_col,
        "dispatch_timestamp": [str(d) if d is not None else None for d in dispatch_datetimes],
        "promised_sla_timestamp": [str(d) if d is not None else None for d in sla_deadlines],
        "actual_delivery_timestamp": [str(d) if d is not None else None for d in delivery_datetimes],
        "dest_latitude": lats,
        "dest_longitude": lons,
        "cargo_weight_kg": base_weights_kg,
        "length_cm": lengths_cm,
        "width_cm": widths_cm,
        "height_cm": heights_cm,
        "transit_distance_km": transit_distance_km,
        "freight_cost_usd": cost_strings,
        "scheduled_days": scheduled_days_col,
    })

    return df_raw
