
# Sample customer order database

orders = {
    "ORD1001": {
        "customer": "John",
        "product": "Laptop",
        "status": "Shipped"
    },

    "ORD1002": {
        "customer": "Sarah",
        "product": "Mobile",
        "status": "Delivered"
    },

    "ORD1003": {
        "customer": "David",
        "product": "Headphones",
        "status": "Processing"
    }
}


# First AI Agent business tool

def check_order_status(order_id):

    order = orders.get(order_id)

    if order is None:

        return {
            "success": False,
            "message": "Order not found."
        }

    return {
        "success": True,
        "order_id": order_id,
        "customer": order["customer"],
        "product": order["product"],
        "status": order["status"]
    }


# Test the tool

result = check_order_status("ORD9999")

print("\nORDER TRACKING RESULT:\n")

print(result)
