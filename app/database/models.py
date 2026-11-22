
from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, nullable=False, index=True)
    customer_name = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    order_status = Column(String, nullable=False)
    delivery_date = Column(String, nullable=True)
