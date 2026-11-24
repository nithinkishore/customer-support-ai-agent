
from app.database.connection import SessionLocal
from app.database.models import Order


def check_order_status(order_id: str, customer_id: int):
    """
    Retrieve order details only when the order belongs
    to the authenticated customer.
    """

    if customer_id is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    db = SessionLocal()

    try:
        order = (
            db.query(Order)
            .filter(
                Order.order_id == order_id,
                Order.customer_id == customer_id
            )
            .first()
        )

        if order is None:
            return {
                "success": False,
                "message": "Order not found or you do not have permission to access it."
            }

        return {
            "success": True,
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "product_name": order.product_name,
            "order_status": order.order_status,
            "delivery_date": order.delivery_date
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Database error: {str(e)}"
        }

    finally:
        db.close()
