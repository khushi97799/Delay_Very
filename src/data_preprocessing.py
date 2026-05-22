import pandas as pd
import os

# Load dataset
df = pd.read_csv("D:/DELHIVERY_PROJECT/delivery_data.csv")

print(df.head())

print(df.columns)
# Remove duplicates
df.drop_duplicates(inplace=True)

# Remove missing values
df.dropna(inplace=True)

# Convert datetime
df['trip_creation_time'] = pd.to_datetime(
    df['trip_creation_time']
)

df['delay'] = (
    df['actual_time'] - df['osrm_time']
)

df['delay_ratio'] = (
    df['actual_time'] / df['osrm_time']
)

df['sla_breach'] = (
    df['actual_time'] > df['osrm_time']
).astype(int)

df['hour'] = df['trip_creation_time'].dt.hour

df['day'] = df['trip_creation_time'].dt.day_name()

df['month'] = df['trip_creation_time'].dt.month

df['peak_hour'] = (
    df['hour'].between(8, 11)
).astype(int)
os.makedirs("data/processed", exist_ok=True)
df.to_csv(
    "data/processed/cleaned_data.csv",
    index=False
)