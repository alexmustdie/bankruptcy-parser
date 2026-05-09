from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FedresursData(Base):

    __tablename__ = "fedresurs_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inn = Column(String(20), nullable=False, unique=True, index=True)
    case_number = Column(String(50), nullable=True, index=True)
    last_date = Column(DateTime, nullable=True)

    arbitr_cases = relationship(
        "ArbitrData", back_populates="fedresurs_case", uselist=False
    )

    def __repr__(self):
        return f"<FedresursData(inn='{self.inn}', case_number='{self.case_number}')>"


class ArbitrData(Base):

    __tablename__ = "arbitr_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String(50), nullable=False, unique=True, index=True)
    last_date = Column(DateTime, nullable=True)
    document_name = Column(Text, nullable=True)

    fedresurs_id = Column(
        Integer, ForeignKey("fedresurs_data.id"), nullable=True, unique=True
    )
    fedresurs_case = relationship("FedresursData", back_populates="arbitr_cases")

    def __repr__(self):
        return f"<ArbitrData(case_number='{self.case_number}')>"
