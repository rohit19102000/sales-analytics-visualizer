
import pandas as pd
import numpy as np
from pathlib import Path


REQUIRED_COLUMNS = [
    "order_id",
    "date",
    "product",
    "category",
    "region",
    "customer_type",
    "quantity",
    "unit_price",
    "discount_pct",
]


class SalesDataLoader:
    """Load, validate and clean sales data."""
    
    def __init__(self, file_path="data/sales.csv"):
        self.file_path = Path(file_path)
        self.df = None

    def load_data(self):
        """Read the CSV into a Pandas DataFrame."""

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Sales file not found: {self.file_path}"
            )

        self.df = pd.read_csv(self.file_path)
        print(f"Loaded {len(self.df)} sales records.")

        return self.df

    def validate_columns(self):
        """Check that all required columns exist."""

        if self.df is None:
            raise ValueError("Load the data before validating it.")

        missing = [
            column
            for column in REQUIRED_COLUMNS
            if column not in self.df.columns
        ]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        return True

    def clean_data(self):
        """Clean dates, invalid values and duplicate orders."""

        if self.df is None:
            raise ValueError("Load the data before cleaning it.")

        self.df = self.df.copy()

        self.df["date"] = pd.to_datetime(
            self.df["date"], errors="coerce"
        )

        numeric_columns = [
            "quantity", "unit_price", "discount_pct"
        ]

        for column in numeric_columns:
            self.df[column] = pd.to_numeric(
                self.df[column], errors="coerce"
            )

        self.df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Remove rows without essential information.
        self.df.dropna(
            subset=[
                "order_id", "date", "product",
                "quantity", "unit_price", "discount_pct",
            ],
            inplace=True,
        )

        # An order ID should be unique in this dataset.
        self.df.drop_duplicates(
            subset="order_id", keep="first", inplace=True
        )

        # Reject impossible values.
        self.df = self.df[
            (self.df["quantity"] > 0)
            & (self.df["unit_price"] > 0)
            & (self.df["discount_pct"].between(0, 100))
        ].copy()

        self.df["quantity"] = self.df["quantity"].astype(int)

        self.df["revenue"] = (
            self.df["quantity"]
            * self.df["unit_price"]
            * (1 - self.df["discount_pct"] / 100)
        )

        self.df["revenue"] = self.df["revenue"].round(2)

        return self.df

    def save_clean_data(self, output_path="data/reports/clean_sales.csv"):
        """Save cleaned data for future phases."""

        if self.df is None:
            raise ValueError("There is no data to save.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.df.to_csv(output_path, index=False)
        print(f"Cleaned data saved to {output_path}")
