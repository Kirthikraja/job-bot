from .database import Base, engine
from .job import Job
from .application import Application
from .credential import Credential

def init_db():
    Base.metadata.create_all(bind=engine)