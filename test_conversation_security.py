
from app.database.connection import SessionLocal
from app.database.models import Customer
from app.database.chat_repository import get_conversation_messages

EMAIL_A = "nithinkishore.36@gmail.com"
EMAIL_B = "nithinkishorers@gmail.com"

CONVERSATION_A = 4
CONVERSATION_B = 5

print("\n===== CONVERSATION SECURITY TEST =====")

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
    raise Exception("One or both customer accounts were not found.")

print("Account A ID:", customer_a.id)
print("Account B ID:", customer_b.id)

# TEST 1: Account A accesses its own conversation
messages = get_conversation_messages(
    CONVERSATION_A, customer_a.id
)
print("\nTEST 1 PASSED: Account A accessed its own conversation.")

# TEST 2: Account B accesses its own conversation
messages = get_conversation_messages(
    CONVERSATION_B, customer_b.id
)
print("TEST 2 PASSED: Account B accessed its own conversation.")

# TEST 3: Account B tries to access Account A's conversation
try:
    get_conversation_messages(
        CONVERSATION_A, customer_b.id
    )
    print("TEST 3 FAILED: Unauthorized access was allowed.")
except PermissionError:
    print("TEST 3 PASSED: Account B was denied access to Account A's conversation.")

# TEST 4: Account A tries to access Account B's conversation
try:
    get_conversation_messages(
        CONVERSATION_B, customer_a.id
    )
    print("TEST 4 FAILED: Unauthorized access was allowed.")
except PermissionError:
    print("TEST 4 PASSED: Account A was denied access to Account B's conversation.")

print("\n===== SECURITY TEST COMPLETED =====")
