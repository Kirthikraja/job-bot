from sqlalchemy import create_engine  # open a connection to the database (SQLite, Postgres, etc.)
from sqlalchemy.ext.declarative import declarative_base  # used to create Base so models (Job, etc.) can inherit and become tables
from sqlalchemy.orm import sessionmaker  # factory that creates a "session" (one conversation with the DB for add/query/update)
import os  # used to read env vars e.g. DATABASE_URL via os.getenv
from dotenv import load_dotenv  # load variables from .env file into the environment



load_dotenv()  # load .env so we can use DATABASE_URL and other env vars

# First arg "DATABASE_URL": the name (key) we look up in the process environment. We're asking: what value is stored under the name DATABASE_URL?
# Second arg "sqlite:///./jobbot.db": the default value. Used only when there is no env var named DATABASE_URL (or it's empty). So = what we use when the environment doesn't define DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobbot.db")

# engine = connection to the database. Everything that talks to the DB uses this.
# check_same_thread=False lets FastAPI use the same engine from different request threads.
engine=create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

#session local = factory that creates a new "session" (one conversation with the DB for add/query/update)
SessionLocal=sessionmaker(bind=engine, autocommit=False, autoflush=False)

#base=the class that every model (Job, Application, etc.) inherits from.
#sqlalchemy uses it to create tables in the database

Base=declarative_base() #declarative_base() is a SQLAlchemy function that creates a base class for all your models




def get_db():
    """FastAPI dependency: gives one DB session per request, then closes it when the request ends.""" 
    db=SessionLocal() #create a one new session
    try:
        yield db #hands that session to route(or whoever called get_db)  the code runs with db available
    finally:
        db.close() #after the request finishes (suces or error) lose so the connection isnt left open 