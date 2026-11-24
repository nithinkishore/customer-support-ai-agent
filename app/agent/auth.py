
from passlib.context import CryptContext

from app.database.connection import SessionLocal
from app.database.models import Customer


# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Convert a plain password into a secure hash."""
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify a password against its stored hash."""
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def register_customer(
    full_name: str,
    email: str,
    password: str
):
    """Register a new customer in SQLite."""

    db = SessionLocal()

    try:
        email = email.strip().lower()

        existing_customer = (
            db.query(Customer)
            .filter(Customer.email == email)
            .first()
        )

        if existing_customer:
            return {
                "success": False,
                "message": "Email is already registered."
            }

        customer = Customer(
            full_name=full_name.strip(),
            email=email,
            password_hash=hash_password(password)
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return {
            "success": True,
            "customer_id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
            "message": "Registration successful."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def login_customer(email: str, password: str):
    """Authenticate an existing customer."""

    db = SessionLocal()

    try:
        email = email.strip().lower()

        customer = (
            db.query(Customer)
            .filter(Customer.email == email)
            .first()
        )

        if customer is None:
            return {
                "success": False,
                "message": "Invalid email or password."
            }

        if not verify_password(
            password,
            customer.password_hash
        ):
            return {
                "success": False,
                "message": "Invalid email or password."
            }

        return {
            "success": True,
            "customer_id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
            "message": "Login successful."
        }

    finally:
        db.close()
