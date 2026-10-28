
from src.data_loader import SalesDataLoader
from src.validators import check_dataframe
from src.analytics import SalesAnalytics
from src.visualizer import SalesVisualizer


def main():
    print("=" * 55)
    print("       SALES ANALYTICS & VISUALIZER")
    print("=" * 55)

    # 1. Load and clean the existing dataset.
    loader = SalesDataLoader()
    loader.load_data()
    loader.validate_columns()

    clean_df = loader.clean_data()
    loader.save_clean_data()

    check_dataframe(clean_df)

    # 2. Create the analytics engine.
    analytics = SalesAnalytics(clean_df)

    # 3. Overall numerical summary.
    print("\n===== OVERALL SUMMARY =====")
    summary = analytics.overall_summary()

    for metric, value in summary.items():
        print(f"{metric.replace('_', ' ').title()}: {value}")

    # 4. Category analysis.
    print("\n===== REVENUE BY CATEGORY =====")
    print(analytics.revenue_by_category().to_string(index=False))

    # 5. Product ranking.
    print("\n===== TOP PRODUCTS =====")
    print(analytics.revenue_by_product().head(5).to_string(index=False))

    # 6. Regional performance.
    print("\n===== REVENUE BY REGION =====")
    print(analytics.revenue_by_region().to_string(index=False))

    # 7. Monthly performance.
    print("\n===== MONTHLY REVENUE =====")
    print(analytics.monthly_revenue().to_string(index=False))

    # 8. Highest-revenue orders.
    print("\n===== TOP 10 ORDERS =====")
    print(analytics.top_orders().to_string(index=False))

    # 9. DSA practice.
    print("\n===== CATEGORY FREQUENCIES =====")
    print(analytics.category_frequencies())

    print("\n===== UNIQUE VALUES =====")
    print(analytics.unique_values())

    print("\n===== HIGHEST-REVENUE PRODUCT =====")
    print(analytics.top_product())

    # 10. Demonstrate filtering.
    print("\n===== HIGH-VALUE ELECTRONICS SALES =====")
    filtered = analytics.filter_sales(
        min_revenue=10000,
        category="Electronics",
    )
    print(f"Matching records: {len(filtered)}")
    print(filtered.head(10).to_string(index=False))

    # 11. Save reusable summary reports.
    print("\n===== SAVING REPORTS =====")
    analytics.save_reports()

    print("\nPhase 2 analytics completed successfully!")

    
    print("\n===== GENERATING VISUALIZATIONS =====")
    visualizer =  SalesVisualizer(clean_df)
    visualizer.generate_all()
    
    print("\nPhase 3 visualization completed successfully")


if __name__ == "__main__":
    main()
