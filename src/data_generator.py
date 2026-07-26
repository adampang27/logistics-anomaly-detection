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
    # Generate transit times (between 24 and 72 hours) with anomalies
    normal_transit_times = np.random.randint(24, 73, size = 9500)
    anamoly_transit_times = np.random.uniform(6,12, size = 500)
    transit_times = np.append(normal_transit_times, anamoly_transit_times)

    # Shuffle the transit times so that the anomalies are distributed randomly
    random.shuffle(transit_times)

    # Create the core dataframe
    df = pd.DataFrame({
        "package_id": package_ids,
        "timestamp": timestamps,
        "transit_time_hours": transit_times,
    })

    # Create the anomaly column where anything delivered in under 12 hours is an anomaly
    df["is_anomaly"] = (df["transit_time_hours"] < 12).astype(int)

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
