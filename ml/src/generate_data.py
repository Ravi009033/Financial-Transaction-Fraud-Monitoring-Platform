from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_STATE = 42
NUM_TRANSACTIONS = 20_000
NUM_ACCOUNTS = 500


MERCHANTS = [
    "Amazon",
    "Flipkart",
    "Walmart",
    "Uber",
    "Swiggy",
    "Zomato",
    "Netflix",
    "Other",
]

LOCATIONS = [
    "Gurugram",
    "Delhi",
    "Noida",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
]


def generate_raw_transactions(
    num_transactions: int = NUM_TRANSACTIONS,
    num_accounts: int = NUM_ACCOUNTS,
) -> pd.DataFrame:

    rng = np.random.default_rng(RANDOM_STATE)

    account_ids = [
        f"ACC{i:05d}"
        for i in range(1, num_accounts + 1)
    ]

    # ---------------------------------------------------------
    # Account-level behavioral profiles
    # ---------------------------------------------------------

    account_profiles = {}

    for account_id in account_ids:

        average_amount = rng.lognormal(
            mean=np.log(80),
            sigma=0.45,
        )

        transaction_activity = rng.choice(
            ["low", "normal", "high"],
            p=[0.20, 0.65, 0.15],
        )

        online_preference = rng.uniform(
            0.50,
            0.95,
        )

        # Typical number of transactions per day.
        if transaction_activity == "low":
            daily_activity = rng.uniform(0.5, 1.5)

        elif transaction_activity == "normal":
            daily_activity = rng.uniform(1.5, 4.0)

        else:
            daily_activity = rng.uniform(4.0, 8.0)

        # Account's normal transaction-hour preference.
        preferred_hour = int(
            rng.integers(7, 23)
        )

        account_profiles[account_id] = {
            "average_amount": average_amount,
            "transaction_activity": transaction_activity,
            "online_preference": online_preference,
            "daily_activity": daily_activity,
            "preferred_hour": preferred_hour,
        }

    # ---------------------------------------------------------
    # Generate normal transactions
    # ---------------------------------------------------------

    rows = []

    start_date = pd.Timestamp("2026-01-01")

    for _ in range(num_transactions):

        account_id = rng.choice(account_ids)

        profile = account_profiles[account_id]

        # -----------------------------------------------------
        # Timestamp
        # -----------------------------------------------------

        day_offset = int(
            rng.integers(
                0,
                60,
            )
        )

        preferred_hour = profile["preferred_hour"]

        # Most transactions happen near the account's
        # normal operating hours.
        if rng.random() < 0.85:

            hour = int(
                np.clip(
                    rng.normal(
                        preferred_hour,
                        3,
                    ),
                    0,
                    23,
                )
            )

        else:

            hour = int(
                rng.integers(
                    0,
                    24,
                )
            )

        minute = int(
            rng.integers(
                0,
                60,
            )
        )

        second = int(
            rng.integers(
                0,
                60,
            )
        )

        timestamp = (
            start_date
            + pd.Timedelta(
                days=day_offset,
            )
            + pd.Timedelta(
                hours=hour,
            )
            + pd.Timedelta(
                minutes=minute,
            )
            + pd.Timedelta(
                seconds=second,
            )
        )

        # -----------------------------------------------------
        # Normal transaction amount
        # -----------------------------------------------------

        amount = rng.lognormal(
            mean=np.log(
                profile["average_amount"]
            ),
            sigma=0.45,
        )

        # -----------------------------------------------------
        # Occasional unusually large transaction
        # -----------------------------------------------------

        if rng.random() < 0.025:

            amount *= rng.uniform(
                4,
                10,
            )

        amount = round(
            float(amount),
            2,
        )

        # -----------------------------------------------------
        # Transaction type
        # -----------------------------------------------------

        is_online = (
            rng.random()
            < profile["online_preference"]
        )

        transaction_type = (
            "online"
            if is_online
            else "offline"
        )

        # -----------------------------------------------------
        # Merchant / location
        # -----------------------------------------------------

        merchant = rng.choice(
            MERCHANTS
        )

        location = rng.choice(
            LOCATIONS
        )

        rows.append(
            {
                "account_id": account_id,
                "amount": amount,
                "merchant": merchant,
                "location": location,
                "transaction_type": transaction_type,
                "timestamp": timestamp,
            }
        )

    df = pd.DataFrame(rows)

    # ---------------------------------------------------------
    # Create suspicious transaction bursts
    # ---------------------------------------------------------
    #
    # A subset of accounts occasionally generates a burst
    # of transactions within a short time window.
    #
    # Some burst transactions are also unusually large.
    # ---------------------------------------------------------

    burst_accounts = rng.choice(
        account_ids,
        size=max(
            1,
            int(num_accounts * 0.12),
        ),
        replace=False,
    )

    burst_rows = []

    for account_id in burst_accounts:

        profile = account_profiles[
            account_id
        ]

        # Each account gets several burst events.
        for _ in range(8):

            base_timestamp = (
                start_date
                + pd.Timedelta(
                    days=int(
                        rng.integers(
                            0,
                            60,
                        )
                    )
                )
                + pd.Timedelta(
                    hours=int(
                        rng.integers(
                            0,
                            24,
                        )
                    )
                )
                + pd.Timedelta(
                    minutes=int(
                        rng.integers(
                            0,
                            60,
                        )
                    )
                )
            )

            # Larger burst sizes create stronger
            # transaction-velocity patterns.
            burst_size = int(
                rng.integers(
                    5,
                    11,
                )
            )

            for _ in range(burst_size):

                timestamp = (
                    base_timestamp
                    + pd.Timedelta(
                        minutes=int(
                            rng.integers(
                                1,
                                90,
                            )
                        )
                    )
                )

                amount = rng.lognormal(
                    mean=np.log(
                        profile["average_amount"]
                    ),
                    sigma=0.50,
                )

                # Some burst transactions are
                # significantly larger than normal.
                if rng.random() < 0.25:

                    amount *= rng.uniform(
                        3,
                        8,
                    )

                amount = round(
                    float(amount),
                    2,
                )

                # Fraud-like bursts are more likely to
                # occur online.
                burst_online_probability = min(
                    0.98,
                    profile["online_preference"] + 0.10,
                )

                is_online = (
                    rng.random()
                    < burst_online_probability
                )

                burst_rows.append(
                    {
                        "account_id": account_id,
                        "amount": amount,
                        "merchant": rng.choice(
                            MERCHANTS
                        ),
                        "location": rng.choice(
                            LOCATIONS
                        ),
                        "transaction_type": (
                            "online"
                            if is_online
                            else "offline"
                        ),
                        "timestamp": timestamp,
                    }
                )

    if burst_rows:

        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    burst_rows
                ),
            ],
            ignore_index=True,
        )

    # ---------------------------------------------------------
    # Keep exactly requested number of transactions
    # ---------------------------------------------------------

    df = (
        df.sample(
            n=num_transactions,
            random_state=RANDOM_STATE,
        )
        .sort_values(
            "timestamp"
        )
        .reset_index(
            drop=True
        )
    )

    return df


def main():

    output_path = Path(
        "ml/data/production_transactions_raw.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = generate_raw_transactions()

    print(
        f"Generated {len(df)} raw transactions"
    )

    print("\nShape:")
    print(df.shape)

    print("\nDate range:")
    print(
        df["timestamp"].min(),
        "->",
        df["timestamp"].max(),
    )

    print("\nSample:")
    print(df.head())

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved to: {output_path}"
    )


if __name__ == "__main__":
    main()