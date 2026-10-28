
from pathlib import Path

from src.data_generator import generate_sales_data
from src.data_loader import SalesDataLoader
from src.validators import check_dataframe
from src.analytics import SalesAnalytics
from src.visualizer import SalesVisualizer


# Shared application state.
clean_df = None
analytics_engine = None


def load_and_clean_data(generate_new=False):
    """Generate data if requested, then load, validate, and clean it."""
    global clean_df, analytics_engine

    if generate_new:
        print("\n===== GENERATING NEW SALES DATA =====")
        generate_sales_data()

    print("\n===== LOADING AND CLEANING DATA =====")

    loader = SalesDataLoader()
    loader.load_data()
    loader.validate_columns()

    clean_df = loader.clean_data()
    loader.save_clean_data()

    check_dataframe(clean_df)

    # The old analytics object may refer to older data.
    analytics_engine = SalesAnalytics(clean_df)

    print("\nData loaded and cleaned successfully.")
    print(f"Clean dataset shape: {clean_df.shape}")

    return clean_df


def ensure_data_loaded():
    """Load data on demand when the application needs it."""
    if clean_df is None or analytics_engine is None:
        load_and_clean_data()

    return clean_df


def display_analytics_summary():
    """Display the main analytics results."""
    ensure_data_loaded()

    print("\n===== OVERALL SUMMARY =====")
    summary = analytics_engine.overall_summary()

    for metric, value in summary.items():
        print(f"{metric.replace('_', ' ').title()}: {value}")

    print("\n===== REVENUE BY CATEGORY =====")
    print(
        analytics_engine.revenue_by_category()
        .to_string(index=False)
    )

    print("\n===== TOP 5 PRODUCTS =====")
    print(
        analytics_engine.revenue_by_product()
        .head(5)
        .to_string(index=False)
    )

    print("\n===== REVENUE BY REGION =====")
    print(
        analytics_engine.revenue_by_region()
        .to_string(index=False)
    )

    print("\n===== MONTHLY REVENUE =====")
    print(
        analytics_engine.monthly_revenue()
        .to_string(index=False)
    )

    print("\n===== TOP 10 ORDERS =====")
    print(
        analytics_engine.top_orders()
        .to_string(index=False)
    )

    print("\n===== CATEGORY FREQUENCIES =====")
    print(analytics_engine.category_frequencies())

    print("\n===== UNIQUE VALUES =====")
    print(analytics_engine.unique_values())

    print("\n===== HIGHEST-REVENUE PRODUCT =====")
    print(analytics_engine.top_product())

    print("\n===== HIGH-VALUE ELECTRONICS SALES =====")
    filtered = analytics_engine.filter_sales(
        min_revenue=10000,
        category="Electronics",
    )
    print(f"Matching records: {len(filtered)}")
    print(filtered.head(10).to_string(index=False))


def export_reports():
    """Save analytics summaries as CSV reports."""
    ensure_data_loaded()

    print("\n===== EXPORTING CSV REPORTS =====")
    analytics_engine.save_reports()

    report_dir = Path("data/reports")
    report_files = sorted(report_dir.glob("*.csv"))

    if report_files:
        print("\nCSV files in the reports directory:")
        for report in report_files:
            print(f"- {report}")
    else:
        print("No CSV reports were found. Check save_reports().")


def generate_visualizations():
    """Generate all charts using the cleaned dataset."""
    ensure_data_loaded()

    print("\n===== GENERATING VISUALIZATIONS =====")

    visualizer = SalesVisualizer(clean_df)
    visualizer.generate_all()

    chart_dir = Path("data/reports/charts")
    chart_files = sorted(chart_dir.glob("*.png"))

    print(f"\nGenerated {len(chart_files)} PNG chart(s).")
    for chart in chart_files:
        print(f"- {chart}")


def run_complete_analysis():
    """Run the full data-to-report pipeline."""
    load_and_clean_data(generate_new=True)
    display_analytics_summary()
    export_reports()
    generate_visualizations()

    print("\n===== COMPLETE ANALYSIS FINISHED =====")
    print("Data, analytics reports, and visualizations are ready.")


def display_menu():
    """Display the application menu."""
    print("\n" + "=" * 55)
    print("       SALES ANALYTICS & VISUALIZER")
    print("=" * 55)
    print("1. Generate and clean sales data")
    print("2. View analytics summary")
    print("3. Generate visualizations")
    print("4. Export reports")
    print("5. Run complete analysis")
    print("6. Exit")


def main():
    """Run the interactive application."""
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-6): ").strip()

        try:
            if choice == "1":
                load_and_clean_data(generate_new=True)

            elif choice == "2":
                display_analytics_summary()

            elif choice == "3":
                generate_visualizations()

            elif choice == "4":
                export_reports()

            elif choice == "5":
                run_complete_analysis()

            elif choice == "6":
                print("\nThank you for using Sales Analytics & Visualizer!")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 6.")

        except (FileNotFoundError, ValueError, KeyError, OSError) as error:
            print(f"\nCould not complete that operation: {error}")
            print("Check the input data, columns, and file paths.")

        except Exception as error:
            # Keep the menu running if an unexpected operation fails.
            print(f"\nUnexpected error: {type(error).__name__}: {error}")
            print("The application is still running; you can try again.")


if __name__ == "__main__":
    main()
