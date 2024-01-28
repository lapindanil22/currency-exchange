import decimal
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ExchangeRateModel(Base):
    __tablename__ = "exchange_rate"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), nullable=False)
    target_currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), nullable=False)
    rate: Mapped[decimal.Decimal] = mapped_column(nullable=False)


Index("ix_base_currency_id_target_currency_id",
      "exchange_rate.base_currency_id", "exchange_rate.target_currency_id", unique=True)
