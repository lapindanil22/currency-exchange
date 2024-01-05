from sqlalchemy import ForeignKey, Index, create_engine, Column, Integer, String, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./exchange.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
Base = declarative_base()


class Currency(Base):
    __tablename__ = "currency"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    sign = Column(String)


class ExchangeRate(Base):
    __tablename__ = "exchange_rate"
    id = Column(Integer, primary_key=True)
    base_currency_id = Column(Integer, ForeignKey(Currency.id), nullable=False)
    target_currency_id = Column(Integer, ForeignKey(Currency.id), nullable=False)
    rate = Column(Numeric, nullable=False)


Index('ix_base_currency_id_target_currency_id',
      ExchangeRate.base_currency_id, ExchangeRate.target_currency_id, unique=True)


Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()
