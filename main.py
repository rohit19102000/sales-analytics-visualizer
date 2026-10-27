
from src.data_generator import generate_sales_data
from src.data_loader import SalesDataLoader
from src.validators import check_dataframe


def main():
    print("===== SALES ANALYTICS & VISUALIZER =====")

    generate_sales_data(records=500)

    loader = SalesDataLoader()
    loader.load_data()
    loader.validate_columns()

    clean_df = loader.clean_data()
    loader.save_clean_data()

    check_dataframe(clean_df)

    print("\nFirst five cleaned records:")
    print(clean_df.head())

    print("\nPhase 1 completed successfully!")


if __name__ == "__main__":
    main()
