
from app.database.connection import SessionLocal
from app.database.models import Order


def seed_orders():
    db = SessionLocal()

    try:
        sample_orders = [
            Order(
                order_id="ORD1001",
                customer_name="John",
                product_name="Laptop",
                order_status="Shipped",
                delivery_date="2026-11-22"
            ),
            Order(
                order_id="ORD1002",
                customer_name="David",
                product_name="Mobile",
                order_status="Processing",
                delivery_date="2026-11-25"
            ),
            Order(
                order_id="ORD1003",
                customer_name="Sarah",
                product_name="Headphones",
                order_status="Delivered",
                delivery_date="2026-11-18"
            )
        ]

        db.add_all(sample_orders)
        db.commit()

        print("Sample orders inserted successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error inserting orders: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_orders()
