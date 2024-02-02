from pydantic import BaseModel

class CreateProduct(BaseModel):
    id: int
    title: str
    description: str
    img: str

class CreateProductCagegory(BaseModel):
    id: int
    type: str

class CreateMenuItem(BaseModel):
    id: int
    product: int
    category: int
    price: int
    size: int
    quantity: int
    bonuses: int
    is_view: bool
    is_have: bool

class MenuModel(BaseModel):
    id: int
    category: int

    # class Config:
    #     orm_mode = True