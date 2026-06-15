import pandas as pd
from collections import Counter
import re

# Read log file
log_file = "system_logs.txt"

log_entries = []

with open(log_file, "r", encoding="utf-8") as file:
    for line in file:
        match = re.match(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.+)",
            line.strip()
        )

        if match:
            timestamp, level, message = match.groups()
            log_entries.append([timestamp, level, message])

# Convert to DataFrame
df = pd.DataFrame(
    log_entries,
    columns=["timestamp", "level", "message"]
)

# Convert timestamp column to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Remove invalid timestamps (if any)
df = df.dropna(subset=["timestamp"])

# Filter ERROR logs
error_df = df[df["level"] == "ERROR"].copy()

# Group timestamps into 30-second buckets manually
error_df["time_bucket"] = error_df["timestamp"].apply(
    lambda x: x.replace(
        second=(x.second // 30) * 30,
        microsecond=0
    )
)

# Count errors per bucket
error_counts = Counter(error_df["time_bucket"])

# Threshold for anomaly detection
threshold = 3

print("=== Anomaly Detection Results ===\n")

anomaly_found = False

for time_bucket, count in sorted(error_counts.items()):
    if count > threshold:
        anomaly_found = True
        print(
            f"🚨 Anomaly detected! "
            f"{count} ERROR logs within 30 seconds at {time_bucket}"
        )

if not anomaly_found:
    print("✅ No anomalies detected.")

# Summary
print("\n=== Log Summary ===")
print(f"Total Logs  : {len(df)}")
print(f"ERROR Logs  : {len(df[df['level'] == 'ERROR'])}")
print(f"INFO Logs   : {len(df[df['level'] == 'INFO'])}")
print(f"WARN Logs   : {len(df[df['level'] == 'WARN'])}")

# Display full log data
print("\n=== Full Log Analysis ===")
print(df.to_string(index=False))
