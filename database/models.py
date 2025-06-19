# database/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    image = Column(String, nullable=True)

    # 🔽 New structured fields for easy querying/comparison
    release_date = Column(String)
    display_size = Column(String)
    resolution = Column(String)
    os = Column(String)
    chipset = Column(String)
    ram = Column(String)
    storage = Column(String)
    camera_main = Column(String)
    battery = Column(String)
    network = Column(String)
    dimensions = Column(String)
    weight = Column(String)

    # Relationship
    specifications = relationship(
        "Specification", back_populates="phone", cascade="all, delete"
    )


class Specification(Base):
    __tablename__ = "specifications"

    id = Column(Integer, primary_key=True, index=True)
    phone_id = Column(Integer, ForeignKey("phones.id"))
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)

    phone = relationship("Phone", back_populates="specifications")
