import datetime

from sqlalchemy import Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

Base = declarative_base()


class SQLModel(Base):
    __abstract__ = True


class WeatherData(SQLModel):
    __tablename__ = 'weather_data'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement='auto')
    user_id: Mapped[int] = mapped_column('user_id', Integer)
    request_date: Mapped[datetime.datetime] = mapped_column('request_date', default=datetime.datetime.utcnow)
    data: Mapped[dict] = mapped_column('data', JSON)