from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint

class Base(DeclarativeBase):
    pass

class CustomerDB(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    name: Mapped[str] = mapped_column(String, nullable = False)
    email: Mapped[str] = mapped_column(String, unique = True, index = True, nullable = False)
    customer_since: Mapped[int]  = mapped_column(Integer, index = True, nullable = True)
    orders: Mapped[list["OrderDB"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class OrderDB(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    order_number: Mapped[int] = mapped_column(Integer, unique = True, nullable = False)
    total_cents: Mapped[int] = mapped_column(Integer)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete = "CASCADE"), nullable = False)
    user: Mapped["CustomerDB"] = relationship(back_populates="orders")




