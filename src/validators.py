
def check_dataframe(df):
    """Print a quick health report for a DataFrame."""

    print("\n===== DATA QUALITY REPORT =====")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"Duplicate order IDs: {df['order_id'].duplicated().sum()}")
    print(f"Missing values: {df.isna().sum().sum()}")
    print(f"Invalid quantities: {(df['quantity'] <= 0).sum()}")
    print(f"Invalid prices: {(df['unit_price'] <= 0).sum()}")
    print(f"Revenue total: ₹{df['revenue'].sum():,.2f}")
    print("\nColumn types:")
    print(df.dtypes)
