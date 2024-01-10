from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric
from src.currencies.models import Currency

from src.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rate"
    id = Column(Integer, primary_key=True)
    base_currency_id = Column(Integer, ForeignKey(Currency.id), nullable=False)
    target_currency_id = Column(Integer, ForeignKey(Currency.id), nullable=False)
    rate = Column(Numeric, nullable=False)


Index('ix_base_currency_id_target_currency_id',
      ExchangeRate.base_currency_id, ExchangeRate.target_currency_id, unique=True)
