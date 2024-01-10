from sqlalchemy import Column, Integer, String

from src.database import Base


class Currency(Base):
    __tablename__ = "currency"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    sign = Column(String)
