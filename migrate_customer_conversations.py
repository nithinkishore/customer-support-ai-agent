from sqlalchemy import inspect, text

from app.database.connection import Base, engine
from app.database import models  # noqa: F401 - registers all ORM models


def migrate():
    # Creates any missing tables, including customers.
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    conversation_columns = {
        column["name"]
        for column in inspector.get_columns("conversations")
    }

    if "customer_id" not in conversation_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE conversations "
                    "ADD COLUMN customer_id INTEGER "
                    "REFERENCES customers(id)"
                )
            )
        print("Added customer_id to conversations table.")
    else:
        print("customer_id column already exists.")

    print("Database migration completed.")
    print(
        "Note: conversations created before this migration remain unassigned "
        "and are intentionally not shown to customer accounts."
    )


if __name__ == "__main__":
    migrate()
