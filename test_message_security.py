
from app.database.connection import SessionLocal
from app.database.models import Customer
from app.database.chat_repository import save_message

EMAIL_A = "nithinkishore.36@gmail.com"
EMAIL_B = "nithinkishorers@gmail.com"

CONVERSATION_A = 4
CONVERSATION_B = 5

print("\n===== MESSAGE SECURITY TEST =====")

# Retrieve customer IDs
db = SessionLocal()

try:
    customer_a = (
        db.query(Customer)
        .filter(Customer.email == EMAIL_A)
        .first()
    )

    customer_b = (
        db.query(Customer)
        .filter(Customer.email == EMAIL_B)
        .first()
    )
finally:
    db.close()

if customer_a is None or customer_b is None:
    raise Exception("Customer account not found.")

# TEST 1: Account A saves a message in its own conversation
save_message(
    CONVERSATION_A,
    "user",
    "Security test: Account A authorized message.",
    customer_a.id
)
print("TEST 1 PASSED: Account A saved its own message.")

# TEST 2: Account B saves a message in its own conversation
save_message(
    CONVERSATION_B,
    "user",
    "Security test: Account B authorized message.",
    customer_b.id
)
print("TEST 2 PASSED: Account B saved its own message.")

# TEST 3: Account B tries to write to Account A's conversation
try:
    save_message(
        CONVERSATION_A,
        "user",
        "Unauthorized test message from Account B.",
        customer_b.id
    )
    print("TEST 3 FAILED: Unauthorized message was saved.")
except PermissionError:
    print("TEST 3 PASSED: Account B was denied access.")

# TEST 4: Account A tries to write to Account B's conversation
try:
    save_message(
        CONVERSATION_B,
        "user",
        "Unauthorized test message from Account A.",
        customer_a.id
    )
    print("TEST 4 FAILED: Unauthorized message was saved.")
except PermissionError:
    print("TEST 4 PASSED: Account A was denied access.")

print("\n===== MESSAGE SECURITY TEST COMPLETED =====")
