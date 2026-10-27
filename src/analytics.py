
import numpy as np
import pandas as pd

from pathlib import Path
from src.decorators import log_operation


class SalesAnalytics:
    """Analyse cleaned sales records."""

    def __init__(self, df):
        if df is None or df.empty:
            raise ValueError("Sales data cannot be empty.")

        required = {
            "order_id", "date", "product", "category",
            "region", "customer_type", "quantity",
            "unit_price", "discount_pct", "revenue",
        }

        missing = required.difference(df.columns)

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

        self.df = df.copy()

        self.df["date"] = pd.to_datetime(
            self.df["date"], errors="coerce"
        )

        self.df["revenue"] = pd.to_numeric(
            self.df["revenue"], errors="coerce"
        )

        self.df.dropna(
            subset=["date", "revenue"], inplace=True
        )

        if self.df.empty:
            raise ValueError("No valid sales records remain.")

    @log_operation
    def overall_summary(self):
        """Calculate overall numerical statistics."""

        revenue = self.df["revenue"].to_numpy(dtype=float)
        quantity = self.df["quantity"].to_numpy(dtype=float)

        return {
            "total_orders": int(self.df["order_id"].nunique()),
            "total_units": int(np.sum(quantity)),
            "total_revenue": round(float(np.sum(revenue)), 2),
            "average_order_value": round(
                float(np.mean(revenue)), 2
            ),
            "median_revenue": round(
                float(np.median(revenue)), 2
            ),
            "minimum_revenue": round(
                float(np.min(revenue)), 2
            ),
            "maximum_revenue": round(
                float(np.max(revenue)), 2
            ),
            "revenue_std_dev": round(
                float(np.std(revenue)), 2
            ),
            "revenue_25th_percentile": round(
                float(np.percentile(revenue, 25)), 2
            ),
            "revenue_75th_percentile": round(
                float(np.percentile(revenue, 75)), 2
            ),
        }

    @log_operation
    def revenue_by_category(self):
        """Calculate revenue and order counts by category."""

        result = (
            self.df.groupby("category")
            .agg(
                total_revenue=("revenue", "sum"),
                average_revenue=("revenue", "mean"),
                total_units=("quantity", "sum"),
                order_count=("order_id", "nunique"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )

        result["total_revenue"] = result[
            "total_revenue"
        ].round(2)

        result["average_revenue"] = result[
            "average_revenue"
        ].round(2)

        return result

    @log_operation
    def revenue_by_product(self):
        """Rank products by revenue."""

        result = (
            self.df.groupby("product")
            .agg(
                total_revenue=("revenue", "sum"),
                units_sold=("quantity", "sum"),
                order_count=("order_id", "nunique"),
                average_unit_price=("unit_price", "mean"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )

        return result.round(2)

    @log_operation
    def revenue_by_region(self):
        """Compare sales performance across regions."""

        result = (
            self.df.groupby("region")
            .agg(
                total_revenue=("revenue", "sum"),
                total_units=("quantity", "sum"),
                order_count=("order_id", "nunique"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )

        result["total_revenue"] = result[
            "total_revenue"
        ].round(2)

        return result

    @log_operation
    def monthly_revenue(self):
        """Summarize revenue month by month."""

        monthly = self.df.copy()

        monthly["month"] = (
            monthly["date"].dt.to_period("M").astype(str)
        )

        result = (
            monthly.groupby("month")
            .agg(
                total_revenue=("revenue", "sum"),
                order_count=("order_id", "nunique"),
                units_sold=("quantity", "sum"),
            )
            .reset_index()
            .sort_values("month")
        )

        result["total_revenue"] = result[
            "total_revenue"
        ].round(2)

        return result

    @log_operation
    def top_orders(self, limit=10):
        """Return the highest-revenue individual records."""

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        return (
            self.df.nlargest(limit, "revenue")[
                [
                    "order_id", "date", "product",
                    "region", "quantity", "revenue",
                ]
            ]
            .reset_index(drop=True)
        )

    @log_operation
    def filter_sales(
        self,
        min_revenue=0,
        category=None,
        region=None,
    ):
        """Filter sales using multiple optional conditions."""

        if min_revenue < 0:
            raise ValueError("Minimum revenue cannot be negative.")

        filtered = self.df[
            self.df["revenue"] >= min_revenue
        ]

        if category is not None:
            filtered = filtered[
                filtered["category"].str.casefold()
                == category.casefold()
            ]

        if region is not None:
            filtered = filtered[
                filtered["region"].str.casefold()
                == region.casefold()
            ]

        return filtered.copy().reset_index(drop=True)

    @log_operation
    def category_frequencies(self):
        """Count categories using a Python dictionary."""

        frequencies = {}

        for category in self.df["category"]:
            frequencies[category] = (
                frequencies.get(category, 0) + 1
            )

        return dict(
            sorted(
                frequencies.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    @log_operation
    def unique_values(self):
        """Find unique products, regions and customer types."""

        return {
            "products": sorted(
                set(self.df["product"].dropna())
            ),
            "regions": sorted(
                set(self.df["region"].dropna())
            ),
            "customer_types": sorted(
                set(self.df["customer_type"].dropna())
            ),
        }

    @log_operation
    def top_product(self):
        """Find the product with the highest total revenue."""

        result = self.revenue_by_product()

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    @log_operation
    def save_reports(self, output_dir="data/reports"):
        """Save analysis tables as CSV files."""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        reports = {
            "category_summary.csv": self.revenue_by_category(),
            "product_summary.csv": self.revenue_by_product(),
            "region_summary.csv": self.revenue_by_region(),
            "monthly_summary.csv": self.monthly_revenue(),
            "top_orders.csv": self.top_orders(),
        }

        for filename, report in reports.items():
            report.to_csv(
                output_dir / filename,
                index=False,
            )
            print(f"Saved: {output_dir / filename}")

        return list(reports)
