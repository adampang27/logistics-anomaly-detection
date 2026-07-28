"""
Automated Data Generation

Generates one batch of historical logistics data.
Called directly for local runs, and importable
so Airflow's Python Operator can call it.
"""

import pandas as pd
import numpy as np
import random
import os

def generate_batch():
    # Range of dates
    START_DATE = np.datetime64('2024-01-01')
    END_DATE = np.datetime64('2025-12-31')
    # Generate 10,000 timestamps between start and end dates
    timestamps = pd.date_range(start=START_DATE, end=END_DATE, periods = 10000).tolist()
    # Generate package IDs (6 digits)
    package_ids = np.random.choice(np.arange(100_000,1_000_000), size=10000, replace = False)
    # Generate transit times as a bell curve centered at 48h (realistic: most cluster near average)
    normal_transit_times = np.clip(np.random.normal(48, 8, size=9500), 24, 72)
    # Fast anomalies: impossibly quick for coast-to-coast (scan errors / fraud)
    fast_anomalies = np.random.uniform(6, 12, size=250)
    # Late anomalies: suspiciously slow (lost / stuck packages)
    late_anomalies = np.random.uniform(80, 120, size=250)
    transit_times = np.concatenate([normal_transit_times, fast_anomalies, late_anomalies])

    # Shuffle the transit times so that the anomalies are distributed randomly
    random.shuffle(transit_times)

    # Create the core dataframe
    df = pd.DataFrame({
        "package_id": package_ids,
        "timestamp": timestamps,
        "transit_time_hours": transit_times,
    })

    # Two-tailed: flag impossibly fast (<12h) and suspiciously late (>72h) shipments
    df["is_anomaly"] = ((df["transit_time_hours"] < 12) | (df["transit_time_hours"] > 72)).astype(int)

    # Sort the dataframe by timestamp
    df.sort_values(by="timestamp", inplace=True)

    # Get the directory where this script is (src) and then go up one level to the root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Output the csv file into the data folder
    output_path = os.path.join(base_dir, "data", "dummy_logistics_data.csv")

    df.to_csv(output_path, index=False)

    return df

if __name__ == "__main__":
    generate_batch()
