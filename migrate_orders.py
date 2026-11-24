
from sqlalchemy import inspect, text
from app.database.connection import engine, SessionLocal
from app.database.models import Customer, Order

ACCOUNT_A_EMAIL = "nithinkishore.36@gmail.com"

SAMPLE_ORDER_IDS = [
    "ORD1001",
    "ORD1002",
    "ORD1003"
]

print("Starting order migration...")

# 1. Add customer_id column if it does not exist
inspector = inspect(engine)
columns = [column["name"] for column in inspector.get_columns("orders")]

if "customer_id" not in columns:
    with engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE orders ADD COLUMN customer_id "
            "INTEGER REFERENCES customers(id)"
        ))
    print("customer_id column added.")
else:
    print("customer_id column already exists.")

# 2. Assign all three orders to Account A
db = SessionLocal()

try:
    customer = db.query(Customer).filter(
        Customer.email == ACCOUNT_A_EMAIL
    ).first()

    if customer is None:
        raise ValueError("Account A was not found.")

    orders = db.query(Order).filter(
        Order.order_id.in_(SAMPLE_ORDER_IDS)
    ).all()

    found_ids = {order.order_id for order in orders}
    missing_ids = set(SAMPLE_ORDER_IDS) - found_ids

    if missing_ids:
        raise ValueError(f"Orders not found: {missing_ids}")

    for order in orders:
        order.customer_id = customer.id

    db.commit()

    print(f"Account A customer ID: {customer.id}")
    print("Order assignments completed:")

    for order in orders:
        print(order.order_id, "->", order.customer_id)

except Exception:
    db.rollback()
    raise

finally:
    db.close()

print("Migration completed successfully!")
