from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Metric(Base):

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True)
    box_id = Column(Integer, index=True)
    payment_type = Column(String, index=True)
    value = Column(Float)
