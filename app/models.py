from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Wine(Base):
    __tablename__ = "wines"

    id          = Column(Integer, primary_key=True, index=True)
    nom         = Column(String, nullable=False)
    couleur     = Column(String, nullable=False)   # rouge | blanc | rose
    domaine     = Column(String, nullable=True)
    annee       = Column(Integer, nullable=True)
    region      = Column(String, nullable=True)
    appellation = Column(String, nullable=True)
    qty         = Column(Integer, default=1)
    prix        = Column(Float, nullable=True)
    garde       = Column(Integer, nullable=True)
    rating      = Column(Integer, default=0)
    notes       = Column(Text, nullable=True)
    emplacement = Column(String, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())