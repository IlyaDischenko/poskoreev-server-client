from sqlalchemy import MetaData, Column, Integer, String, Boolean, Table, ForeignKey

from app.database_new.database import Base

metadata = MetaData()




ProductsCategories = Table(
    "products_categories", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("type", String, nullable=False),
)

Menu = Table(
    "menu", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column('product', ForeignKey("products.id")),
    # Column('restaurant', ForeignKey("products.id"), primary_key=True),
    Column('category', ForeignKey("products_categories.id")),
    Column("price", Integer, nullable=False, default=0),
    Column("quantity", Integer, nullable=False, default=0),
    Column("size", Integer, nullable=False, default=0),
    Column("bonuses", Integer, nullable=False, default=0),
    Column("is_view", Boolean, default=True),
    Column("is_have", Boolean, default=True),

)
