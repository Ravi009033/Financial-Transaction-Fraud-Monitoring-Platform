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

        # Most accounts have normal activity.
        # A smaller group is more transaction-active.
        transaction_activity = rng.choice(
            ["normal", "high"],
            p=[0.85, 0.15],
        )

        online_preference = rng.uniform(
            0.5,
            0.95,
        )

        account_profiles[account_id] = {
            "average_amount": average_amount,
            "transaction_activity": transaction_activity,
            "online_preference": online_preference,
        }

    # ---------------------------------------------------------
    # Generate transactions
    # ---------------------------------------------------------

    rows = []

    start_date = pd.Timestamp("2026-01-01")

    for _ in range(num_transactions):

        account_id = rng.choice(account_ids)

        profile = account_profiles[account_id]

        # -----------------------------------------------------
        # Timestamp
        # -----------------------------------------------------

        timestamp = (
            start_date
            + pd.Timedelta(
                seconds=int(
                    rng.integers(
                        0,
                        60 * 24 * 60 * 60,
                    )
                )
            )
        )

        # -----------------------------------------------------
        # Normal transaction amount
        # -----------------------------------------------------

        amount = rng.lognormal(
            mean=np.log(profile["average_amount"]),
            sigma=0.65,
        )

        # -----------------------------------------------------
        # Occasional unusually large transaction
        # -----------------------------------------------------

        if rng.random() < 0.025:
            amount *= rng.uniform(
                5,
                12,
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
    # Create account-level transaction bursts
    # ---------------------------------------------------------
    #
    # Select a small number of accounts that occasionally
    # generate several transactions close together.
    #
    # This creates realistic variation in transaction velocity.
    # ---------------------------------------------------------

    burst_accounts = rng.choice(
        account_ids,
        size=max(1, int(num_accounts * 0.10)),
        replace=False,
    )

    burst_account_set = set(
        burst_accounts
    )

    burst_rows = []

    for account_id in burst_accounts:

        # Around 10 burst events across the dataset.
        for _ in range(10):

            base_timestamp = (
                start_date
                + pd.Timedelta(
                    seconds=int(
                        rng.integers(
                            0,
                            60 * 24 * 60 * 60,
                        )
                    )
                )
            )

            profile = account_profiles[
                account_id
            ]

            # Generate 3–7 transactions within
            # a short period.
            burst_size = int(
                rng.integers(
                    3,
                    8,
                )
            )

            for _ in range(burst_size):

                timestamp = (
                    base_timestamp
                    + pd.Timedelta(
                        minutes=int(
                            rng.integers(
                                1,
                                180,
                            )
                        )
                    )
                )

                amount = rng.lognormal(
                    mean=np.log(
                        profile["average_amount"]
                    ),
                    sigma=0.65,
                )

                # A few burst transactions are unusually large.
                if rng.random() < 0.15:
                    amount *= rng.uniform(
                        3,
                        8,
                    )

                amount = round(
                    float(amount),
                    2,
                )

                is_online = (
                    rng.random()
                    < profile["online_preference"]
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
                pd.DataFrame(burst_rows),
            ],
            ignore_index=True,
        )

    # Keep exactly the requested number of transactions.
    df = (
        df.sample(
            n=num_transactions,
            random_state=RANDOM_STATE,
        )
        .sort_values("timestamp")
        .reset_index(drop=True)
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