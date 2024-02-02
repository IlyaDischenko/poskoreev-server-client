from app.database_new.database import engine


# from app.database_new.sqlalchemy_database import engine

def create_tables():
    metadata = metadata.create_all(engine)