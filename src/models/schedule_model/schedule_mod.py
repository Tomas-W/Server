from datetime import datetime
from sqlalchemy import Integer, String, Date, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.extensions import server_db_


class Schedule(server_db_.Model):
    """
    Stores the schedule data.
    
    - ID (int): Identifier [Primary Key]
    - DATE (date): Date of the schedule [Unique]
    - WEEK_NUMBER (str): Week number of the schedule
    - DAY (str): Day of the schedule
    - NAMES (list[str]): Names of the schedule
    - HOURS (list[str]): Hours of the schedule
    """
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(Date, unique=True, nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[str] = mapped_column(String(255), nullable=False)
    names: Mapped[str] = mapped_column(Text, nullable=False)
    start_hours: Mapped[str] = mapped_column(Text, nullable=False)
    end_hours: Mapped[str] = mapped_column(Text, nullable=False)
    
    starts: Mapped[str] = mapped_column(Text)
    ends: Mapped[str] = mapped_column(Text)

    def __init__(self, date: datetime, week_number: str, day: str,
                 names: list[str], hours: list[str]):
        self.date = date
        self.week_number = week_number
        self.day = day
        self.names = self._join(self._crop_names(names))
        self.start_hours = self._get_start_hours(hours)
        self.end_hours = self._get_end_hours(hours)
        
        self.starts = self._get_starts(hours)
        self.ends = self._get_ends(hours)
    
    def _crop_names(self, names: list[str]) -> list[str]:
        return [f"{name.split()[0]} {name.split()[1][0]}" for name in names]
    
    def _get_start_hours(self, hours: list[str]) -> str:
        start_hours = [hour.split(" - ")[0] for hour in hours]
        return self._join(start_hours)
    
    def _get_end_hours(self, hours: list[str]) -> str:
        end_hours = [hour.split(" - ")[1] for hour in hours]
        return self._join(end_hours)
    
    def _get_starts(self, hours: list[str]) -> str:
        starts = []
        for hour in hours:
            start_time = hour.split(" - ")[0]
            start_value = self._convert_time_to_value(start_time)
            starts.append(str(start_value))
        return self._join(starts)
        
    def _get_ends(self, hours: list[str]) -> str:
        ends = []
        for hour in hours:
            end_time = hour.split(" - ")[1]
            end_value = self._convert_time_to_value(end_time)
            ends.append(str(end_value))
        return self._join(ends)
    
    def _convert_time_to_value(self, time_str: str) -> int:
        hours, minutes = map(int, time_str.split(":"))
        total_minutes = (hours - 6) * 60 + minutes
        return total_minutes // 15
    
    def date_to_dict(self) -> dict:
        return {
            "date": self.date,
            "week_number": int(self.week_number),
            "day": self.day,
            "names": self._split(self.names),
            "start_hours": self._split(self.start_hours),
            "end_hours": self._split(self.end_hours),
            "starts": self._split(self.starts, make_int=True),
            "ends": self._split(self.ends, make_int=True)
        }
    
    @staticmethod
    def _join(value: list[str]) -> str:
        return "|".join(value)
    
    @staticmethod
    def _split(value: str, make_int: bool = False) -> list[str]:
        return [int(item) if make_int else item for item in value.split("|")] if value else []


