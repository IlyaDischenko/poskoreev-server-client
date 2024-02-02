from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.database_new.database import Base



class Menu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product = Column(ForeignKey("products.id"))
    category = Column(ForeignKey("products_categories.id"))
    price = Column(Integer, nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=0)
    size = Column(Integer, nullable=False, default=0)
    bonuses = Column(Integer, nullable=False, default=0)
    is_view = Column(Boolean, default=True)
    is_have = Column(Boolean, default=True)

    def as_dict(self):
        return {c.name: getattr(c.name) for c in self.__table__.columns}


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    img = Column(String, nullable=True)

    def as_dict(self):
        return {c.name: getattr(c.name) for c in self.__table__.columns}
