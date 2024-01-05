from sqlalchemy import Column, String
from .base import Base

class Lawyer(Base):
    __tablename__ = "lawyers"
    code = Column(String, primary_key=True)
    