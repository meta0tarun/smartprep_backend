# app/create_tables.py
from .db import engine
from .models import Base

def create():
    Base.metadata.create_all(bind=engine)
    print("Tables created")

if __name__ == "__main__":
    create()
