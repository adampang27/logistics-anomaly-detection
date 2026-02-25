"""
Automated Data Generation 

Our data source
"""

import pandas as pd
import numpy as np
import random
import os

# Range of dates
START_DATE = np.datetime64('2024-01-01')
END_DATE = np.datetime64('2025-12-31')
# Generate 100 timestamps between start and end dates
timestamps = pd.date_range(start=START_DATE, end=END_DATE, periods = 10000).tolist()
# Generate package IDs (6 digits)
package_ids = np.random.choice(np.arange(100_000,1_000_000), size=10000, replace = False)
# Generate transit times (between 24 and 72 hours) with anamolies
normal_transit_times = np.random.randint(24, 73, size = 9500)
anamoly_transit_times = np.random.uniform(6,12, size = 500)
transit_times = np.append(normal_transit_times, anamoly_transit_times)

random.shuffle(transit_times)
df.sort_values(by="timestamp")

df = pd.DataFrame({
    "package_id": package_ids,
    "timestamp": timestamps,
    "transit_time_hours": transit_times
})

# Get the directory where this script is (src) and then go up one level to the root
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Output the csv file into the data folder
output_path = os.path.join(base_dir, "data", "dummy_logistics_data.csv")

df.to_csv(output_path, index=False)

