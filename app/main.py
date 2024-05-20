import time

from app.database import init_db
from fastapi import Request, FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.users.views import user_router
from app.products.views import products_router
from app.orders.views import orders_router
from app.orders.eventSourcing import orders_router as orders_event_router
from app.restaurants.views import restaurant_router

app = FastAPI(
    # redoc_url=None,
    # docs_url=None
)

init_db(app)

origins = ["http://localhost:3000", "https://poskoreev.ru"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(user_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(restaurant_router)
app.include_router(orders_event_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response