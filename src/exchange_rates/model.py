from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric

from src.currencies.model import CurrencyModel
from src.database import Base


class ExchangeRateModel(Base):
    __tablename__ = "exchange_rate"
    id = Column(Integer, primary_key=True)
    base_currency_id = Column(Integer, ForeignKey(CurrencyModel.id), nullable=False)
    target_currency_id = Column(Integer, ForeignKey(CurrencyModel.id), nullable=False)
    rate = Column(Numeric, nullable=False)


Index('ix_base_currency_id_target_currency_id',
      ExchangeRateModel.base_currency_id, ExchangeRateModel.target_currency_id, unique=True)
