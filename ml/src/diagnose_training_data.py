import pandas as pd


DATA_PATH = "ml/data/production_training_data.csv"

df = pd.read_csv(DATA_PATH)


print("Dataset shape:")
print(df.shape)


print("\nClass distribution:")
print(df["Class"].value_counts())


# ---------------------------------------------------------
# Define the same conditions used during labeling
# ---------------------------------------------------------

high_amount_ratio = df["amount_vs_avg_ratio"] >= 8.0

high_velocity = df["transactions_last_24h"] >= 5

late_night = (
    (df["transaction_hour"] >= 0)
    & (df["transaction_hour"] < 5)
)

online = df["is_online"] == 1

combined = high_amount_ratio & high_velocity


# ---------------------------------------------------------
# Rule activation
# ---------------------------------------------------------

print("\nRule activation:")

print(
    "High amount ratio:",
    high_amount_ratio.sum(),
)

print(
    "High velocity:",
    high_velocity.sum(),
)

print(
    "Late night:",
    late_night.sum(),
)

print(
    "Online:",
    online.sum(),
)

print(
    "High amount + high velocity:",
    combined.sum(),
)


# ---------------------------------------------------------
# Fraud rate by rule
# ---------------------------------------------------------

print("\nFraud rate by rule:")

for name, condition in [
    ("High amount ratio", high_amount_ratio),
    ("High velocity", high_velocity),
    ("Late night", late_night),
    ("Online", online),
    ("High amount + high velocity", combined),
]:

    if condition.sum() > 0:
        print(
            f"{name}:",
            f"{condition.sum()} rows,",
            f"fraud rate = {df.loc[condition, 'Class'].mean():.4f}",
        )


# ---------------------------------------------------------
# Fraud rate by amount-ratio bucket
# ---------------------------------------------------------

df["ratio_bucket"] = pd.cut(
    df["amount_vs_avg_ratio"],
    bins=[
        -float("inf"),
        1,
        2,
        4,
        8,
        15,
        float("inf"),
    ],
)

print("\nFraud rate by amount ratio:")

print(
    df.groupby(
        "ratio_bucket",
        observed=True,
    )["Class"]
    .agg(["count", "mean"])
)


# ---------------------------------------------------------
# Fraud rate by velocity
# ---------------------------------------------------------

print("\nFraud rate by transactions_last_24h:")

print(
    df.groupby("transactions_last_24h")["Class"]
    .agg(["count", "mean"])
    .head(20)
)