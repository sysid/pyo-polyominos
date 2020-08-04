import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Float, Boolean, Column, Integer, String, DateTime

_log = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = "sqlite:///./logdata.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Logdata(Base):
    __tablename__ = 'logdata'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    name = Column(String)
    objective = Column(Float)
    constraints = Column(Integer)
    variables = Column(Integer)
    duration = Column(Float)
    solved = Column(Boolean())


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
_ = None
