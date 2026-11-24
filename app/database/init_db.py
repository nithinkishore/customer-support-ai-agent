
from app.database.connection import Base, engine
from app.database.models import (
    Order,
    Conversation,
    ChatMessage,
    Customer
)

def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
    print("All database tables created successfully!")

if __name__ == "__main__":
    initialize_database()
