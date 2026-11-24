
from app.database.connection import SessionLocal
from app.database.models import Customer
from app.agent.tools import check_order_status

EMAIL_A = "nithinkishore.36@gmail.com"
EMAIL_B = "nithinkishorers@gmail.com"

ORDER_IDS = ["ORD1001", "ORD1002", "ORD1003"]

db = SessionLocal()

try:
    account_a = db.query(Customer).filter(
        Customer.email == EMAIL_A
    ).first()

    account_b = db.query(Customer).filter(
        Customer.email == EMAIL_B
    ).first()

    if not account_a or not account_b:
        raise Exception("One or both test accounts were not found.")

    print("Account A ID:", account_a.id)
    print("Account B ID:", account_b.id)

    print("\n===== ACCOUNT A TESTS =====")

    for order_id in ORDER_IDS:
        result = check_order_status(order_id, account_a.id)
        print(order_id, result)

        assert result["success"], (
            f"Account A could not access {order_id}"
        )

    print("\n===== ACCOUNT B SECURITY TESTS =====")

    for order_id in ORDER_IDS:
        result = check_order_status(order_id, account_b.id)
        print(order_id, result)

        assert not result["success"], (
            f"SECURITY FAILURE: Account B accessed {order_id}"
        )

    print("\nALL SIX TESTS PASSED!")

finally:
    db.close()
