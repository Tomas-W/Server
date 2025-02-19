import random
from typing import Any

from flask_login import current_user
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Date,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from src.extensions import (
    server_db_,
    logger,
)

from src.utils.schedule import (
    add_employee_json,
    update_employee_json,
)
from src.utils.misc_utils import crop_name

from config.settings import SERVER


class Employees(server_db_.Model):
    """
    Stores the employee data.
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    code: Mapped[int] = mapped_column(Integer, nullable=True)
    is_activated: Mapped[bool] = mapped_column(Boolean, default=False)

    def set_email(self, email: str) -> bool:
        if self.email == email:
            return False
        
        self.email = email
        update_employee_json(self.name, email=email)
        server_db_.session.commit()
        return True
    
    def set_is_activated(self, is_activated: bool) -> None:
        if not self.is_activated == is_activated:
            self.is_activated = is_activated
            update_employee_json(self.name, is_verified=is_activated)
            server_db_.session.commit()
            if is_activated:
                logger.info(f"[AUTH] EMPLOYEE {self.name} ACTIVATED")
            else:
                logger.info(f"[AUTH] EMPLOYEE {self.name} DEACTIVATED")
    
    def activate(self, email: str) -> bool:
        if self.set_email(email):
            self.set_is_activated(True)
            return True
        return False
    
    def deactivate(self):
        if self.is_activated:
            self.email = ""
            self.set_is_activated(False)
            update_employee_json(self.name, is_verified=False, email="")
            server_db_.session.commit()
            return True
        return False

    @staticmethod
    def add_employee(name: str):
        # cropped_name = crop_name(name)
        employee = Employees.query.filter_by(name=name).first()
        if not employee:
            # Generate random 5 digit code
            code = random.randint(10000, 99999)
            employee = Employees(name=name, code=code)
            server_db_.session.add(employee)
            server_db_.session.commit()
            add_employee_json(name)
            logger.info(f"[ADD] EMPLOYEE {name} ADDED")
        else:
            logger.warning(f"[AUTH] EMPLOYEE NAME {name} ALREADY IN DATABASE")

    def cli_repr(self) -> str:
        return (f"{'ID':<18}{self.id}\n"
                f"{'NAME':<18}{self.name}\n"
                f"{'EMAIL':<18}{self.email}\n"
                f"{'IS ACTIVATED':<18}{self.is_activated}")


class Schedule(server_db_.Model):
    """
    Stores the schedule data.
    
    - ID (int): Identifier [Primary Key]
    - DATE (date): Date of the schedule [Unique]
    - WEEK_NUMBER (str): Week number of the schedule
    - DAY (str): Day of the schedule
    - NAMES (list[str]): Names of the schedule
    
    - START_HOURS (str): Start hours of the schedule
    - END_HOURS (str): End hours of the schedule
    - STARTS (str): Starts of the schedule
    - ENDS (str): Ends of the schedule
    
    - BREAK_TIME (str): Break time of the schedule
    - WORK_TIME (str): Work time of the schedule
    
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
    
    break_times: Mapped[str] = mapped_column(Text, nullable=False)
    work_times: Mapped[str] = mapped_column(Text, nullable=False)

    def __init__(self, date: datetime, week_number: int, day: str,
                 names: list[str], hours: list[str],
                 break_times: list[str], work_times: list[str]):
        self.date = date
        self.week_number = week_number
        self.day = day
        self.names = self._join(names)
        
        self.start_hours = self._get_start_hours(hours)
        self.end_hours = self._get_end_hours(hours)
        self.starts = self._get_starts(hours)
        self.ends = self._get_ends(hours)
        
        self.break_times = self._join(break_times)
        self.work_times = self._join(work_times)
    
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
            "date": self.date.strftime("%d-%m-%Y"),
            "week_number": int(self.week_number),
            "day": self.day,
            "names": self._split(self.names),
            
            "start_hours": self._split(self.start_hours),
            "end_hours": self._split(self.end_hours),
            "starts": self._split(self.starts, make_int=True),
            "ends": self._split(self.ends, make_int=True),
            
            "break_times": self._split(self.break_times),
            "work_times": self._split(self.work_times)
        }
    
    def to_personal_dict(self, name: str) -> dict:
        name = name if name in self.names else ""
        names = self._split(self.names)
        
        start_hours = self._split(self.start_hours)
        start_hour = start_hours[names.index(name)] if name in names else None
        end_hours = self._split(self.end_hours)
        end_hour = end_hours[names.index(name)] if name in names else None
        
        starts = self._split(self.starts, make_int=True)
        start = int(starts[names.index(name)]) if name in names else None
        ends = self._split(self.ends, make_int=True)
        end = int(ends[names.index(name)]) if name in names else None
        
        break_times = self._split(self.break_times)
        break_time = break_times[names.index(name)] if name in names else None
        work_times = self._split(self.work_times)
        work_time = work_times[names.index(name)] if name in names else None
        
        return {
            "date": self.date.strftime("%d-%m-%Y"),
            "week_number": int(self.week_number),
            "day": self.day,
            "name": name,
            
            "start_hour": start_hour,
            "end_hour": end_hour,
            "start": start,
            "end": end,
            
            "break_time": break_time,
            "work_time": work_time
        }
    
    @staticmethod
    def _join(value: list[str]) -> str:
        return "|".join(value)
    
    @staticmethod
    def _split(value: str, make_int: bool = False) -> list[str]:
        return [int(item) if make_int else item for item in value.split("|")] if value else []

    def cli_repr(self) -> str:
        return (f"{'ID':<18}{self.id}\n"
                f"{'DATE':<18}{self.date}\n"
                f"{'WEEK NUMBER':<18}{self.week_number}\n"
                f"{'DAY':<18}{self.day}\n"
                f"{'NAMES':<18}{self.names}")

