
from app.agent.auth import (
    register_customer,
    login_customer
)


print("\n===== CUSTOMER AUTHENTICATION TEST =====")

# 1. Register a customer
registration = register_customer(
    full_name="Test Customer",
    email="nithin.test@example.com",
    password="Test@12345"
)

print("\nTEST 1 - Customer Registration")
print(registration)


# 2. Test duplicate email
duplicate = register_customer(
    full_name="Test Customer",
    email="nithin.test@example.com",
    password="Test@12345"
)

print("\nTEST 2 - Duplicate Email")
print(duplicate)


# 3. Login with correct password
login = login_customer(
    email="nithin.test@example.com",
    password="Test@12345"
)

print("\nTEST 3 - Correct Password")
print(login)


# 4. Login with incorrect password
wrong_login = login_customer(
    email="nithin.test@example.com",
    password="WrongPassword123"
)

print("\nTEST 4 - Incorrect Password")
print(wrong_login)
