from typing import List

from fastapi import HTTPException, APIRouter, Response, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, insert

from app.database_new.database import get_async_session
from app.database_new.models import ProductsCategories
from app.products.schemas import CreateProduct, CreateProductCagegory, CreateMenuItem, MenuModel
from app.products.models import Products, Menu


products_router = APIRouter(
    prefix="/api/v1/products"
)


@products_router.get('/', tags=['Products'])
async def get_product(session: Session = Depends(get_async_session)):
    query = select(Menu.id, Menu.size, Menu.price, Menu.quantity, Menu.bonuses, Menu.is_have, Menu.is_view, Products.title, Products.description).join(Products).where(Products.id == Menu.product)
    menu = await session.execute(query)
    # print(menu.scalars().all())
    return menu.scalars()

@products_router.get('/getproducts', tags=['Products'])
async def get_product(session: Session = Depends(get_async_session)):
    query = select(Products)
    menu = await session.execute(query)
    return menu.scalars().all()

@products_router.post('/addProduct', tags=['Products'])
async def add_product(new_product: CreateProduct, session: Session = Depends(get_async_session)):
    query = insert(Products).values(**new_product.model_dump())
    await session.execute(query)
    await session.commit()
    return 'ok'


@products_router.post('/addProductCategory', tags=['Products'])
async def add_product_category(new_category: CreateProductCagegory, session: Session = Depends(get_async_session)):
    query = insert(ProductsCategories).values(**new_category.model_dump())
    await session.execute(query)
    await session.commit()
    return 'ok'


@products_router.post('/addMenuItem', tags=['Products'])
async def add_menu_item(new_menu_item: CreateMenuItem, session: Session = Depends(get_async_session)):
    query = insert(Menu).values(**new_menu_item.model_dump())
    await session.execute(query)
    await session.commit()
    return 'ok'
