from sqlalchemy import create_engine, MetaData, Column, Integer, String, Date, Table, ForeignKey, ARRAY, LargeBinary, Float
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()

class XY(Base):
    __tablename__ = 'XY'

    xyID = Column(Integer, primary_key=True, autoincrement=True)

def initialize_database(postgres_pw, ip):    
    POSTGRES_URL = f"postgresql://postgres:{postgres_pw}@{ip}:5432/postgres"
    engine = create_engine(POSTGRES_URL)

    Base.metadata.create_all(engine)
    print("Datenbanktabellen wurden erfolgreich initialisiert.")