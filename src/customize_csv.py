import os
import pandas as pd


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "output",
    "decoded_radar.csv"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "output",
    "radar_dataset.csv"
)


# ---------------------------------------------------------
# FILTER SETTINGS
# ---------------------------------------------------------

MIN_SNR = 10.0

MIN_RANGE = 0.20

MAX_RANGE = 10.0

MIN_VELOCITY = -5.0

MAX_VELOCITY = 5.0


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

if not os.path.exists(INPUT_FILE):

    print("ERROR: decoded_radar.csv not found.")

    print(
        "Run parse_recording.py first."
    )

    raise SystemExit


df = pd.read_csv(INPUT_FILE)


print("--------------------------------------------")
print("RADAR DATA CUSTOMIZATION")
print("--------------------------------------------")

print("Original rows:", len(df))


# ---------------------------------------------------------
# REMOVE INVALID VALUES
# ---------------------------------------------------------

df = df.dropna(
    subset=[
        "x_m",
        "y_m",
        "z_m",
        "range_m",
        "velocity_mps",
        "snr_db"
    ]
)


# ---------------------------------------------------------
# FILTER BY SNR
# ---------------------------------------------------------

df = df[
    df["snr_db"] >= MIN_SNR
]


# ---------------------------------------------------------
# FILTER BY RANGE
# ---------------------------------------------------------

df = df[
    (df["range_m"] >= MIN_RANGE) &
    (df["range_m"] <= MAX_RANGE)
]


# ---------------------------------------------------------
# FILTER BY VELOCITY
# ---------------------------------------------------------

df = df[
    (df["velocity_mps"] >= MIN_VELOCITY) &
    (df["velocity_mps"] <= MAX_VELOCITY)
]


# ---------------------------------------------------------
# CREATE ADDITIONAL FEATURES
# ---------------------------------------------------------

# Speed in km/h

df["speed_kmph"] = (
    df["velocity_mps"].abs() * 3.6
)


# Direction of movement

def get_direction(velocity):

    if velocity > 0.1:
        return "AWAY"

    elif velocity < -0.1:
        return "TOWARD"

    else:
        return "STATIONARY"


df["movement"] = df[
    "velocity_mps"
].apply(get_direction)


# ---------------------------------------------------------
# CREATE RADAR ZONE
# ---------------------------------------------------------

def get_zone(distance):

    if distance <= 2:
        return "NEAR"

    elif distance <= 5:
        return "MEDIUM"

    else:
        return "FAR"


df["zone"] = df[
    "range_m"
].apply(get_zone)


# ---------------------------------------------------------
# SAVE FINAL DATASET
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("Final rows:", len(df))

print(
    "Saved to:",
    OUTPUT_FILE
)

print("--------------------------------------------")
print("CUSTOMIZATION COMPLETE")
print("--------------------------------------------")