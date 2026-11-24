
from app.agent.tools import check_order_status

# Test 1: Existing order
print("\n--- TEST 1: Valid Order ---")
result = check_order_status("ORD1001")
print(result)

# Test 2: Another existing order
print("\n--- TEST 2: Another Valid Order ---")
result = check_order_status("ORD1002")
print(result)

# Test 3: Invalid order
print("\n--- TEST 3: Invalid Order ---")
result = check_order_status("ORD9999")
print(result)
