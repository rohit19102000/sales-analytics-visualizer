
import csv
import random
from datetime import date, timedelta
from pathlib import Path


PRODUCTS = {
    "Laptop": ("Electronics", 55000, 85000),
    "Headphones": ("Electronics", 1000, 5000),
    "Keyboard": ("Accessories", 500, 2500),
    "Mouse": ("Accessories", 300, 1500),
    "Chair": ("Furniture", 4000, 12000),
    "Desk": ("Furniture", 5000, 18000),
    "Notebook": ("Stationery", 40, 150),
    "Pen Set": ("Stationery", 80, 300),
}

REGIONS = ["North", "South", "East", "West"]
CUSTOMER_TYPES = ["New", "Returning", "VIP"]

COLUMNS = [
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


def generate_sales_data(
    output_path="data/sales.csv",
    records=500,
    seed=42,
):
    """Generate reproducible synthetic sales records."""

    random.seed(seed)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    start_date = date(2025, 1, 1)
    end_date = date(2026, 12, 31)
    total_days = (end_date - start_date).days

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()

        for number in range(1, records + 1):
            product = random.choice(list(PRODUCTS))
            category, min_price, max_price = PRODUCTS[product]

            order_date = start_date + timedelta(
                days=random.randint(0, total_days)
            )

            writer.writerow({
                "order_id": f"ORD{number:04d}",
                "date": order_date.isoformat(),
                "product": product,
                "category": category,
                "region": random.choice(REGIONS),
                "customer_type": random.choice(CUSTOMER_TYPES),
                "quantity": random.randint(1, 12),
                "unit_price": random.randint(min_price, max_price),
                "discount_pct": random.choice([0, 0, 5, 10, 15, 20]),
            })

    print(f"Generated {records} records: {output_path}")
