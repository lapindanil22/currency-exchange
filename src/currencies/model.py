from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class CurrencyModel(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    name: Mapped[str]
    sign: Mapped[str]
