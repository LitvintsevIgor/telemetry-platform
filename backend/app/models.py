from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Metric(Base):

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    name = Column(String, index=True)
    code = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, index=True)