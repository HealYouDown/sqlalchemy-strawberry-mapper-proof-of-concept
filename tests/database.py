from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Enum,
                        Float, Integer, LargeBinary, Numeric, SmallInteger,
                        String, Text, Time, Unicode, UnicodeText,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///")
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()


class TestModel(Base):
    __tablename__ = "test"

    index = Column(Integer, primary_key=True)

    # Some types are not supported by strawberry (yet)
    # and cannot be returned natively

    big_integer = Column(BigInteger, nullable=False)
    boolean = Column(Boolean, nullable=False)
    date = Column(Date, nullable=False)
    date_time = Column(DateTime, nullable=False)
    float_ = Column(Float, nullable=False)
    integer = Column(Integer, nullable=False)
    # interval = Column(Interval, nullable=False)
    # large_binary = Column(LargeBinary, nullable=False)
    numeric = Column(Numeric, nullable=False)
    # pickle_type = Column(PickleType, nullable=False)
    # enum = Column(Enum(...), nullable=False)
    small_integer = Column(SmallInteger, nullable=False)
    string = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    time = Column(Time, nullable=False)
    unicode = Column(Unicode, nullable=False)
    unicode_text = Column(UnicodeText, nullable=False)
