
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class SalesVisualizer:
    """Create and save visualizations for sales data."""

    
    def __init__(self, df, output_dir="data/reports/charts"):
        if df is None or df.empty:
            raise ValueError("Sales data cannot be empty.")

        required = {
            "date", "product", "category", "region",
            "quantity", "unit_price", "discount_pct", "revenue",
        }

        missing = required.difference(df.columns)
        if missing:
            raise ValueError(
                f"Missing columns for visualization: {sorted(missing)}"
            )

        # Store a copy of the DataFrame in this object.
        self.df = df.copy()

        self.df["date"] = pd.to_datetime(
            self.df["date"], errors="coerce"
        )

        self.df = self.df.dropna(
            subset=["date", "quantity", "unit_price", "revenue"]
        ).copy()

        numeric_columns = [
            "quantity", "unit_price", "discount_pct", "revenue"
        ]

        # Keep rows where every selected numeric value is finite.
        finite_rows = np.isfinite(
            self.df[numeric_columns]
        ).all(axis=1)

        self.df = self.df.loc[finite_rows].copy()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        sns.set_theme(style="whitegrid", context="notebook")


    def _save_chart(self, filename):
        """Save the current Matplotlib figure."""

        path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Chart saved: {path}")
        plt.close()

    def monthly_revenue_chart(self):
        """Plot total revenue over time."""

        monthly = (
            self.df.assign(month=self.df["date"].dt.to_period("M"))
            .groupby("month", as_index=False)["revenue"]
            .sum()
        )

        monthly["month"] = monthly["month"].astype(str)

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(
            monthly["month"],
            monthly["revenue"],
            marker="o",
            linewidth=2,
            label="Monthly revenue",
        )

        ax.set_title("Monthly Sales Revenue")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue (₹)")
        ax.tick_params(axis="x", rotation=60)
        ax.legend()
        ax.grid(True, alpha=0.3)

        self._save_chart("monthly_revenue.png")

    def category_revenue_chart(self):
        """Compare total revenue by category."""

        category = (
            self.df.groupby("category", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
        )

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.barplot(
            data=category,
            x="revenue",
            y="category",
            hue="category",
            legend=False,
            ax=ax,
        )

        ax.set_title("Revenue by Product Category")
        ax.set_xlabel("Total Revenue (₹)")
        ax.set_ylabel("Category")

        self._save_chart("category_revenue.png")

    def region_count_chart(self):
        """Count sales records in each region."""

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(
            data=self.df,
            x="region",
            order=self.df["region"].value_counts().index,
            hue="region",
            legend=False,
            ax=ax,
        )

        ax.set_title("Number of Sales Records by Region")
        ax.set_xlabel("Region")
        ax.set_ylabel("Number of Records")

        self._save_chart("region_counts.png")

    def revenue_distribution_chart(self):
        """Display revenue distribution with a KDE estimate."""

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(
            data=self.df,
            x="revenue",
            bins=25,
            kde=True,
            ax=ax,
        )

        ax.set_title("Distribution of Sales Revenue")
        ax.set_xlabel("Revenue per Record (₹)")
        ax.set_ylabel("Frequency")

        self._save_chart("revenue_distribution.png")

    def revenue_boxplot(self):
        """Show revenue spread and potential outliers."""

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.boxplot(
            data=self.df,
            x="category",
            y="revenue",
            ax=ax,
        )

        ax.set_title("Revenue Spread by Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Revenue (₹)")
        ax.tick_params(axis="x", rotation=20)

        self._save_chart("revenue_boxplot.png")

    def quantity_revenue_scatter(self):
        """Explore the relationship between quantity and revenue."""

        sample_size = min(300, len(self.df))
        sample = self.df.sample(
            n=sample_size,
            random_state=42,
        )

        fig, ax = plt.subplots(figsize=(9, 6))
        sns.scatterplot(
            data=sample,
            x="quantity",
            y="revenue",
            hue="category",
            alpha=0.7,
            ax=ax,
        )

        ax.set_title("Quantity vs Revenue by Category")
        ax.set_xlabel("Quantity")
        ax.set_ylabel("Revenue (₹)")
        ax.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left")

        self._save_chart("quantity_vs_revenue.png")

    def pairplot_chart(self):
        """Compare several numerical variables."""

        numeric_columns = [
            "quantity", "unit_price", "discount_pct", "revenue"
        ]

        pair_df = self.df[numeric_columns + ["category"]].copy()

        grid = sns.pairplot(
            data=pair_df,
            vars=numeric_columns,
            hue="category",
            diag_kind="hist",
            plot_kws={"alpha": 0.6, "s": 25},
        )

        grid.figure.suptitle(
            "Pairwise Relationships in Sales Data",
            y=1.02,
        )

        path = self.output_dir / "sales_pairplot.png"
        grid.figure.savefig(
            path, dpi=120, bbox_inches="tight"
        )
        print(f"Chart saved: {path}")
        plt.close(grid.figure)

    def correlation_heatmap(self):
        """Visualize correlations among numerical columns."""

        numeric = self.df[
            ["quantity", "unit_price", "discount_pct", "revenue"]
        ]

        correlation = numeric.corr()

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            correlation,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            center=0,
            ax=ax,
        )

        ax.set_title("Sales Variables Correlation Heatmap")

        self._save_chart("correlation_heatmap.png")

    def overview_dashboard(self):
        """Display four useful charts in one figure."""

        fig, axes = plt.subplots(
            nrows=2,
            ncols=2,
            figsize=(14, 10),
        )

        monthly = (
            self.df.assign(month=self.df["date"].dt.to_period("M"))
            .groupby("month")["revenue"]
            .sum()
        )
        monthly.index = monthly.index.astype(str)

        monthly.plot(
            kind="line", marker="o", ax=axes[0, 0]
        )
        axes[0, 0].set_title("Monthly Revenue")
        axes[0, 0].tick_params(axis="x", rotation=60)

        category = (
            self.df.groupby("category")["revenue"]
            .sum()
            .sort_values()
        )
        category.plot(kind="barh", ax=axes[0, 1])
        axes[0, 1].set_title("Revenue by Category")
        axes[0, 1].set_xlabel("Revenue (₹)")

        sns.histplot(
            data=self.df, x="revenue", bins=20,
            kde=True, ax=axes[1, 0]
        )
        axes[1, 0].set_title("Revenue Distribution")

        sns.scatterplot(
            data=self.df,
            x="quantity",
            y="revenue",
            hue="category",
            alpha=0.6,
            ax=axes[1, 1],
        )
        axes[1, 1].set_title("Quantity vs Revenue")
        axes[1, 1].legend(fontsize="small")

        fig.suptitle("Sales Analytics Overview", fontsize=16)
        fig.tight_layout()

        path = self.output_dir / "overview_dashboard.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Chart saved: {path}")
        plt.close(fig)

    def generate_all(self):
        """Generate the complete chart collection."""

        chart_methods = [
            self.monthly_revenue_chart,
            self.category_revenue_chart,
            self.region_count_chart,
            self.revenue_distribution_chart,
            self.revenue_boxplot,
            self.quantity_revenue_scatter,
            self.pairplot_chart,
            self.correlation_heatmap,
            self.overview_dashboard,
        ]

        for method in chart_methods:
            method()

        print(f"\nAll charts saved in: {self.output_dir}")
